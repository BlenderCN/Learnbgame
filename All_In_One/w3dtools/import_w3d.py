#Written by Stephan Vedder and Michael Schnabel
#Last Modification 06.06.2016
#Loads the W3D Format used in games by Westwood & EA
import bpy
import operator
import struct
import os
import math
import sys
import bmesh
from bpy.props import *
from mathutils import Vector, Quaternion
from . import struct_w3d 

# -> some code for texture animation 
#bpy.data.window_managers["WinMan"].key_uvs
#bpy.ops.anim.insert_keyframe_animall()
#bpy.ops.wm.addon_enable(module = "animation_animall")

#TODO 

# find a solution for the mesh property 393216 - camera oriented (points _towards_ camera) -> obj property view_align == camera oriented??

# support animated textures

# read compressed animation data and create it

# apply per vertex color from material pass

# support for multiple textures for one mesh (also multiple uv maps)

# support for 2 bone vertex influences (are they even used?) (mucavtroll)

# unknown chunks:
#	64 size of 4 bytes


def InsensitiveOpen(path):
    #find the file on unix
    dir = os.path.dirname(path)
    name = os.path.basename(path)
    
    for filename in os.listdir(dir):
        if filename.lower()==name.lower():
            path = os.path.join(dir,filename)
            return open(path,"rb")
        
def InsensitivePath(path):
     #find the file on unix
    dir = os.path.dirname(path)
    name = os.path.basename(path)
    
    for filename in os.listdir(dir):
        if filename.lower()==name.lower():
            path = os.path.join(dir,filename)

    return path

#######################################################################################
# Basic Methods
#######################################################################################

def ReadString(file):
    bytes = []
    b = file.read(1)
    while ord(b)!=0:
        bytes.append(b)
        b = file.read(1)
    return (b"".join(bytes)).decode("utf-8")

def ReadFixedString(file):
    SplitString = ((str(file.read(16)))[2:18]).split("\\")
    return SplitString[0]

def ReadLongFixedString(file):
    SplitString = ((str(file.read(32)))[2:34]).split("\\")
    return SplitString[0]

def ReadRGBA(file):
    return struct_w3d.RGBA(r=ord(file.read(1)), g=ord(file.read(1)), b=ord(file.read(1)), a=ord(file.read(1)))

def GetChunkSize(data):
    return (data & 0x7FFFFFFF)

def ReadLong(file):
    #binary_format = "<l" long
    return (struct.unpack("<L", file.read(4))[0])

def ReadShort(file):
    #binary_format = "<h" short
    return (struct.unpack("<H", file.read(2))[0])

def ReadUnsignedShort(file):
    return (struct.unpack("<h", file.read(2))[0])

def ReadLongArray(file,chunkEnd):
    LongArray = []
    while file.tell() < chunkEnd:
        LongArray.append(ReadLong(file))
    return LongArray

def ReadFloat(file):
    #binary_format = "<f" float
    return (struct.unpack("<f", file.read(4))[0])
    
def PrintByte(file):
    val = ord(file.read(1))
    str = ""
    if (val & 128) > 0: 
        str += "1" 
    else: 
        str += "0"
    if (val & 64)  > 0: 
        str += "1" 
    else: 
        str += "0"
    if (val & 32)  > 0: 
        str += "1" 
    else: 
        str += "0"
    if (val & 16)  > 0:
        str += "1" 
    else: 
        str += "0"
    if (val & 8)  > 0: 
        str += "1" 
    else:
        str += "0"
    if (val & 4)  > 0:
        str += "1" 
    else: 
        str += "0"
    if (val & 2)  > 0: 
        str += "1" 
    else: 
        str += "0"
    if (val & 1)  > 0: 
        str += "1" 
    else: 
        str += "0"
    print(str, val)
    
    
#this returns the better values
def ReadFloat8(file): #3 bit exp 4 bit mantissa
    val = ord(file.read(1))
    sign = -1 if (val >> 7) > 0 else 1
    exp = ((val >> 4) & 7) - 3
    mant = val & 15
    mant = (16 ^ mant) / 16
    
    return sign * pow(2.0, exp) * mant
    
def ReadFloat8_(file): #4 bit exp 3 bit mantissa
    val = ord(file.read(1))
    sign = -1 if (val >> 7) > 0 else 1
    exp = ((val >> 3) & 15) - 7
    mant = val & 7
    mant = (8 ^ mant) / 8

    return sign * pow(2.0, exp) * mant
    
    
def ReadMiniFloat16(file):
    return (struct.unpack("<f", file.read(2))[0])

def ReadSignedByte(file):
    return (struct.unpack("<b", file.read(1))[0])

def ReadUnsignedByte(file):
    return (struct.unpack("<B", file.read(1))[0])

def ReadVector(file):
    return Vector((ReadFloat(file), ReadFloat(file), ReadFloat(file)))

def ReadQuaternion(file):
    quat = (ReadFloat(file), ReadFloat(file), ReadFloat(file), ReadFloat(file))
    #change order from xyzw to wxyz
    return Quaternion((quat[3], quat[0], quat[1], quat[2]))

def ReadCompressedQuaternion8(file):
    quat = (ReadFloat8(file), ReadFloat8(file), ReadFloat8(file), ReadFloat8(file))
    #change order from xyzw to wxyz
    return Quaternion((quat[3], quat[0], quat[1], quat[2]))	

def GetVersion(data):
    return struct_w3d.Version(major = (data)>>16, minor = (data) & 0xFFFF)

#######################################################################################
# Hierarchy
#######################################################################################

def ReadHierarchyHeader(file):
    HierarchyHeader = struct_w3d.HierarchyHeader()
    HierarchyHeader.version = GetVersion(ReadLong(file))
    HierarchyHeader.name = ReadFixedString(file)
    HierarchyHeader.pivotCount = ReadLong(file)
    HierarchyHeader.centerPos = ReadVector(file)
    return HierarchyHeader

def ReadPivots(file, chunkEnd):
    pivots = []
    while file.tell() < chunkEnd:
        pivot = struct_w3d.HierarchyPivot()
        pivot.name = ReadFixedString(file)
        pivot.parentID = ReadLong(file)
        pivot.position = ReadVector(file)
        pivot.eulerAngles = ReadVector(file)
        pivot.rotation = ReadQuaternion(file)
        pivots.append(pivot)
    return pivots

# if the exported pivots are corrupted these fixups are used
def ReadPivotFixups(file, chunkEnd):
    pivot_fixups = []
    while file.tell() < chunkEnd:
        pivot_fixup = ReadVector(file)
        pivot_fixups.append(pivot_fixup)
    return pivot_fixups

def ReadHierarchy(file, self, chunkEnd):
    #print("\n### NEW HIERARCHY: ###")
    HierarchyHeader = struct_w3d.HierarchyHeader()
    Pivots = []
    Pivot_fixups = []
    while file.tell() < chunkEnd:
        chunkType = ReadLong(file)
        chunkSize = GetChunkSize(ReadLong(file))
        subChunkEnd = file.tell() + chunkSize
        if chunkType == 257:
            HierarchyHeader = ReadHierarchyHeader(file)
            #print("Header")
        elif chunkType == 258:
            Pivots = ReadPivots(file, subChunkEnd)
            #print("Pivots")
        elif chunkType == 259:
            Pivot_fixups = ReadPivotFixups(file, subChunkEnd)
            #print("PivotFixups")
        else:
            self.report({'ERROR'}, "unknown chunktype in Hierarchy: %s" % chunkType)
            print("!!!unknown chunktype in Hierarchy: %s" % chunkType)
            file.seek(chunkSize, 1)
    return struct_w3d.Hierarchy(header = HierarchyHeader, pivots = Pivots, pivot_fixups = Pivot_fixups)

#######################################################################################
# Animation
#######################################################################################

def ReadAnimationHeader(file):
    return struct_w3d.AnimationHeader(version = GetVersion(ReadLong(file)), name = ReadFixedString(file), 
        hieraName = ReadFixedString(file), numFrames = ReadLong(file), frameRate = ReadLong(file))

def ReadAnimationChannel(file, self, chunkEnd):
    #print("Channel")
    FirstFrame = ReadShort(file)
    LastFrame = ReadShort(file)
    VectorLen = ReadShort(file)
    Type = ReadShort(file)
    Pivot = ReadShort(file)
    Pad = ReadShort(file) 
    Data = []
    if VectorLen == 1:
        while file.tell() < chunkEnd:
            Data.append(ReadFloat(file))
    elif VectorLen == 4:
        while file.tell() < chunkEnd:
            Data.append(ReadQuaternion(file))
    else:
        self.report({'ERROR'}, "!!!unsupported vector len %s" % VectorLen)
        print("!!!unsupported vector len %s" % VectorLen)
        while file.tell() < chunkEnd:
            file.read(1)
    return struct_w3d.AnimationChannel(firstFrame = FirstFrame, lastFrame = LastFrame, vectorLen = VectorLen, 
        type = Type, pivot = Pivot, pad = Pad, data = Data)

def ReadAnimation(file, self, chunkEnd):
    print("\n### NEW ANIMATION: ###")
    Header = struct_w3d.AnimationHeader()
    Channels = []
    while file.tell() < chunkEnd:
        chunkType = ReadLong(file)
        chunkSize = GetChunkSize(ReadLong(file))
        subChunkEnd = file.tell() + chunkSize
        if chunkType == 513:
            Header = ReadAnimationHeader(file)
        elif chunkType == 514:
            Channels.append(ReadAnimationChannel(file, self, subChunkEnd))
        else:
            self.report({'ERROR'}, "unknown chunktype in Animation: %s" % chunkType)
            print("!!!unknown chunktype in Animation: %s" % chunkType)
            file.seek(chunkSize, 1)
    return struct_w3d.Animation(header = Header, channels = Channels)


def ReadCompressedAnimationHeader(file):
    return struct_w3d.CompressedAnimationHeader(version = GetVersion(ReadLong(file)), name = ReadFixedString(file), 
        hieraName = ReadFixedString(file), numFrames = ReadLong(file), frameRate = ReadShort(file), flavor = ReadShort(file))

def ReadTimeCodedAnimationChannel(file, self, chunkEnd): # bfme I animation struct
    TimeCodesCount = ReadLong(file)
    Pivot = ReadShort(file)
    VectorLen = ReadUnsignedByte(file)
    Type = ReadUnsignedByte(file)
    TimeCodedKeys = []

    while file.tell() < chunkEnd: 
        Key = struct_w3d.TimeCodedAnimationKey()
        Key.frame = ReadLong(file)
        if Type == 6:
            Key.value = ReadQuaternion(file)
        else:
            Key.value = ReadFloat(file)
        TimeCodedKeys.append(Key)
    return struct_w3d.TimeCodedAnimationChannel(timeCodesCount = TimeCodesCount, pivot = Pivot, vectorLen = VectorLen, type = Type,
        timeCodedKeys = TimeCodedKeys)
        
def ReadTimeCodedBitChannel(file, self, chunkEnd): #-- channel of boolean values (e.g. visibility) - always size 16
    TimeCodesCount = ReadLong(file)
    Pivot = ReadShort(file)
    Type = ReadUnsignedByte(file) #0 = vis, 1 = timecoded vis
    DefaultValue = ReadUnsignedByte(file)
    print(TimeCodesCount, Pivot, Type, DefaultValue)
    values = []

    #8 bytes left
    while file.tell() < chunkEnd:
        # dont yet know how to interpret this data
        print(ReadUnsignedByte(file))
        
##test function s= short
def FromSageFloat16(s):
    return ((s >> 8) * 10.0 + (s & 255) * 9.96000003814697 / 256.0);
#return (float) ((double) (byte) ((uint) v >> 8) * 10.0 + (double) (byte) ((uint) v & (uint) byte.MaxValue) * 9.96000003814697 / 256.0);
        
def ReadTimeCodedAnimationVector(file, self, chunkEnd):
    print("##############") 
    zero = ReadUnsignedByte(file)
    delta = ReadUnsignedByte(file)
    vecLen = ReadUnsignedByte(file)
    flag = ReadUnsignedByte(file)
    count = ReadShort(file)
    pivot = ReadShort(file)
    print(zero, delta, vecLen, flag, count, pivot)
    
    if delta == 0:	
        for x in range(0, count):
            print(ReadUnsignedShort(file))
        
        print("### data")
        #skip 2 bytes if uneven
        if (count % 2) > 0: 
            file.read(2)
            
        print ("remaining bytes: ", chunkEnd - file.tell())
            
        for x in range(0, count * vecLen):
            print(ReadFloat(file))
    elif delta== 1:
        print(ReadFloat(file))
        for x in range(0, vecLen):
            print(ReadFloat(file))
        while file.tell() < chunkEnd:
            print(ReadUnsignedByte(file))
    else:
        while file.tell() < chunkEnd:
            file.read(1)

def ReadCompressedAnimation(file, self, chunkEnd):
    print("\n### NEW COMPRESSED ANIMATION: ###")
    Header = struct_w3d.CompressedAnimationHeader()
    Channels = []
    Vectors = []
    while file.tell() < chunkEnd:
        chunkType = ReadLong(file)
        chunkSize = GetChunkSize(ReadLong(file))
        subChunkEnd = file.tell() + chunkSize
        if chunkType == 641:
            Header = ReadCompressedAnimationHeader(file)
            print("#### numFrames %s" % Header.numFrames)
            print("##Flavor %s" % Header.flavor)
        elif chunkType == 642:
            Channels.append(ReadTimeCodedAnimationChannel(file, self, subChunkEnd))
        elif chunkType == 643:
            #print("### size: %s" % chunkSize)
            #ReadTimeCodedBitChannel(file, self, subChunkEnd)
            print("chunk 643 not implemented yet")
            file.seek(chunkSize, 1)
        elif chunkType == 644:
            #print("####size %s" % (chunkSize - 8))
            Vectors.append(ReadTimeCodedAnimationVector(file, self, subChunkEnd))
            #print("chunk 644 not implemented yet")
            #file.seek(chunkSize, 1)
        else:
            self.report({'ERROR'}, "unknown chunktype in CompressedAnimation: %s" % chunkType)
            print("!!!unknown chunktype in CompressedAnimation: %s" % chunkType)
            file.seek(chunkSize, 1)	
    return struct_w3d.CompressedAnimation(header = Header, channels = Channels, vectors = Vectors)

#######################################################################################
# HLod
#######################################################################################

def ReadHLodHeader(file):
    HLodHeader = struct_w3d.HLodHeader()
    HLodHeader.version = GetVersion(ReadLong(file))
    HLodHeader.lodCount = ReadLong(file)
    HLodHeader.modelName = ReadFixedString(file)
    HLodHeader.HTreeName = ReadFixedString(file)
    return HLodHeader

def ReadHLodArrayHeader(file):
    HLodArrayHeader = struct_w3d.HLodArrayHeader()
    HLodArrayHeader.modelCount = ReadLong(file)
    HLodArrayHeader.maxScreenSize = ReadFloat(file)
    return HLodArrayHeader

def ReadHLodSubObject(file):
    HLodSubObject = struct_w3d.HLodSubObject()
    HLodSubObject.boneIndex = ReadLong(file)
    HLodSubObject.name = ReadLongFixedString(file)
    return HLodSubObject

def ReadHLodArray(file, self, chunkEnd):
    HLodArrayHeader = struct_w3d.HLodArrayHeader()
    HLodSubObjects = []
    while file.tell() < chunkEnd:
        chunkType = ReadLong(file)
        chunkSize = GetChunkSize(ReadLong(file))
        subChunkEnd = file.tell() + chunkSize
        if chunkType == 1795:
            HLodArrayHeader = ReadHLodArrayHeader(file)
        elif chunkType == 1796:
            HLodSubObjects.append(ReadHLodSubObject(file))
        else:
            self.report({'ERROR'}, "unknown chunktype in HLodArray: %s" % chunkType)
            print("!!!unknown chunktype in HLodArray: %s" % chunkType)
            file.seek(chunkSize, 1)
    return struct_w3d.HLodArray(header = HLodArrayHeader, subObjects = HLodSubObjects)

def ReadHLod(file, self, chunkEnd):
    #print("\n### NEW HLOD: ###")
    HLodHeader = struct_w3d.HLodHeader()
    HLodArray = struct_w3d.HLodArray()
    while file.tell() < chunkEnd:
        chunkType = ReadLong(file)
        chunkSize = GetChunkSize(ReadLong(file))
        subChunkEnd = file.tell() + chunkSize
        if chunkType == 1793:
            HLodHeader = ReadHLodHeader(file)
            #print("Header")
        elif chunkType == 1794:
            HLodArray = ReadHLodArray(file, self, subChunkEnd)
            #print("HLodArray")
        else:
            self.report({'ERROR'}, "unknown chunktype in HLod: %s" % chunkType)
            print("!!!unknown chunktype in HLod: %s" % chunkType)
            file.seek(chunkSize, 1)
    return struct_w3d.HLod(header = HLodHeader, lodArray = HLodArray)

#######################################################################################
# Box
#######################################################################################	

def ReadBox(file):
    #print("\n### NEW BOX: ###")
    version = GetVersion(ReadLong(file))
    attributes = ReadLong(file)
    name = ReadLongFixedString(file)
    color = ReadRGBA(file)
    center = ReadVector(file)
    extend = ReadVector(file)
    return struct_w3d.Box(version = version, attributes = attributes, name = name, color = color, center = center, extend = extend)

#######################################################################################
# Texture
#######################################################################################	

def ReadTexture(file, self, chunkEnd):
    tex = struct_w3d.Texture()
    while file.tell() < chunkEnd:
        Chunktype = ReadLong(file)
        Chunksize = GetChunkSize(ReadLong(file))
        subChunkEnd = file.tell() + Chunksize
        if Chunktype == 50:
            tex.name = ReadString(file)
        elif Chunktype == 51:
            tex.textureInfo = struct_w3d.TextureInfo(attributes = ReadShort(file),
                animType = ReadShort(file), frameCount = ReadLong(file), frameRate = ReadFloat(file))
        else:
            self.report({'ERROR'}, "unknown chunktype in Texture: %s" % chunkType)
            print("!!!unknown chunktype in Texture: %s" % chunkType)
            file.seek(Chunksize,1)
    return tex

def ReadTextureArray(file, self, chunkEnd):
    textures = []
    while file.tell() < chunkEnd:
        Chunktype = ReadLong(file)
        Chunksize = GetChunkSize(ReadLong(file))
        subChunkEnd = file.tell() + Chunksize
        if Chunktype == 49:
            textures.append(ReadTexture(file, self, subChunkEnd))
        else:
            self.report({'ERROR'}, "unknown chunktype in TextureArray: %s" % chunkType)
            print("!!!unknown chunktype in TextureArray: %s" % chunkType)
            file.seek(Chunksize, 1)
    return textures

#######################################################################################
# Material
#######################################################################################	

def ReadMeshTextureCoordArray(file, chunkEnd):
    txCoords = []
    while file.tell() < chunkEnd:
        txCoords.append((ReadFloat(file), ReadFloat(file)))
    return txCoords

def ReadMeshTextureStage(file, self, chunkEnd):
    TextureIds = []
    TextureCoords = []
    while file.tell() < chunkEnd:
        chunkType = ReadLong(file)
        chunkSize = GetChunkSize(ReadLong(file))
        subChunkEnd = file.tell() + chunkSize
        if chunkType == 73:
            TextureIds = ReadLongArray(file, subChunkEnd)
        elif chunkType == 74:
            TextureCoords = ReadMeshTextureCoordArray(file, subChunkEnd)
        else:
            self.report({'ERROR'}, "unknown chunktype in MeshTextureStage: %s" % chunkType)
            print("!!!unknown chunktype in MeshTextureStage: %s" % chunkType)
            file.seek(chunkSize,1)
    return struct_w3d.MeshTextureStage(txIds = TextureIds, txCoords = TextureCoords)	

def ReadMeshMaterialPass(file, self, chunkEnd):
    # got two different types of material passes depending on if the mesh has bump maps of not
    VertexMaterialIds = []
    ShaderIds = []
    DCG =  []
    TextureStage = struct_w3d.MeshTextureStage()
    while file.tell() < chunkEnd:
        chunkType = ReadLong(file)
        chunkSize = GetChunkSize(ReadLong(file))
        subChunkEnd = file.tell() + chunkSize
        if chunkType == 57: #Vertex Material Ids
            VertexMaterialIds = ReadLongArray(file, subChunkEnd)
        elif chunkType == 58:#Shader Ids
            ShaderIds = ReadLongArray(file, subChunkEnd)
        elif chunkType == 59:#vertex colors
            while file.tell() < subChunkEnd:
                DCG.append(ReadRGBA(file))
        elif chunkType == 63:# dont know what this is -> size is always 4 and value 0
            #print("<<< unknown Chunk 63 >>>")
            file.seek(chunkSize, 1)
        elif chunkType == 72: #Texture Stage
            TextureStage = ReadMeshTextureStage(file, self, subChunkEnd)
        elif chunkType == 74: #Texture Coords  
            TextureStage.txCoords = ReadMeshTextureCoordArray(file, subChunkEnd)  
        else:
            self.report({'ERROR'}, "unknown chunktype in MeshMaterialPass: %s" % chunkType)
            print("!!!unknown chunktype in MeshMaterialPass: %s" % chunkType)
            file.seek(chunkSize, 1)
    return struct_w3d.MeshMaterialPass(vmIds = VertexMaterialIds, shaderIds = ShaderIds, dcg = DCG, txStage = TextureStage)

def ReadMaterial(file, self, chunkEnd):
    mat = struct_w3d.MeshMaterial()
    while file.tell() < chunkEnd:
        chunkType = ReadLong(file)
        chunkSize = GetChunkSize(ReadLong(file))
        subChunkEnd = file.tell() + chunkSize
        if chunkType == 44:
            mat.vmName = ReadString(file)
        elif chunkType == 45:
            vmInf = struct_w3d.VertexMaterial()
            vmInf.attributes = ReadLong(file)
            vmInf.ambient = ReadRGBA(file)
            vmInf.diffuse = ReadRGBA(file)
            vmInf.specular = ReadRGBA(file)
            vmInf.emissive = ReadRGBA(file)
            vmInf.shininess = ReadFloat(file)
            vmInf.opacity = ReadFloat(file)
            vmInf.translucency = ReadFloat(file)
            mat.vmInfo = vmInf
        elif chunkType == 46:
            mat.vmArgs0 = ReadString(file)
        elif chunkType == 47:
            mat.vmArgs1 = ReadString(file)
        else:
            self.report({'ERROR'}, "unknown chunktype in Material: %s" % chunkType)
            print("!!!unknown chunktype in Material: %s" % chunkType)
            file.seek(chunkSize,1)
    return mat

def ReadMeshMaterialArray(file, self, chunkEnd):
    Mats = []
    while file.tell() < chunkEnd:
        chunkType = ReadLong(file)
        chunkSize = GetChunkSize(ReadLong(file))
        subChunkEnd = file.tell()+chunkSize
        if chunkType == 43:
            Mats.append(ReadMaterial(file, self, subChunkEnd))
        else:
            self.report({'ERROR'}, "unknown chunktype in MeshMaterialArray: %s" % chunkType)
            print("!!!unknown chunktype in MeshMaterialArray: %s" % chunkType)
            file.seek(chunkSize,1)
    return Mats

def ReadMeshMaterialSetInfo (file):
    result = struct_w3d.MeshMaterialSetInfo(passCount = ReadLong(file), vertMatlCount = ReadLong(file), 
        shaderCount = ReadLong(file), textureCount = ReadLong(file))
    return result

#######################################################################################
# Vertices
#######################################################################################

def ReadMeshVerticesArray(file, chunkEnd):
    verts = []
    while file.tell() < chunkEnd:
        verts.append(ReadVector(file))
    return verts

def ReadMeshVertexInfluences(file, chunkEnd):
    vertInfs = []
    while file.tell()  < chunkEnd:
        vertInf = struct_w3d.MeshVertexInfluences()
        vertInf.boneIdx = ReadShort(file)
        vertInf.xtraIdx = ReadShort(file)
        vertInf.boneInf = ReadShort(file)/100
        vertInf.xtraInf = ReadShort(file)/100
        vertInfs.append(vertInf)
    return vertInfs

#######################################################################################
# Faces
#######################################################################################	

def ReadMeshFace(file):
    result = struct_w3d.MeshFace(vertIds = (ReadLong(file), ReadLong(file), ReadLong(file)),
    attrs = ReadLong(file),
    normal = ReadVector(file),
    distance = ReadFloat(file))
    return result

def ReadMeshFaceArray(file, chunkEnd):
    faces = []
    while file.tell() < chunkEnd:
        faces.append(ReadMeshFace(file))
    return faces

#######################################################################################
# Shader
#######################################################################################

def ReadMeshShaderArray(file, chunkEnd):
    shaders = []
    while file.tell() < chunkEnd:
        shader = struct_w3d.MeshShader()
        shader.depthCompare = ReadUnsignedByte(file)
        shader.depthMask = ReadUnsignedByte(file)
        shader.colorMask = ReadUnsignedByte(file)
        shader.destBlend = ReadUnsignedByte(file)
        shader.fogFunc = ReadUnsignedByte(file)
        shader.priGradient = ReadUnsignedByte(file) 
        shader.secGradient = ReadUnsignedByte(file)
        shader.srcBlend = ReadUnsignedByte(file)
        shader.texturing = ReadUnsignedByte(file)
        shader.detailColorFunc = ReadUnsignedByte(file)
        shader.detailAlphaFunc = ReadUnsignedByte(file)
        shader.shaderPreset = ReadUnsignedByte(file)
        shader.alphaTest = ReadUnsignedByte(file)
        shader.postDetailColorFunc = ReadUnsignedByte(file)
        shader.postDetailAlphaFunc = ReadUnsignedByte(file) 
        shader.pad = ReadUnsignedByte(file)
        shaders.append(shader)
    return shaders

#######################################################################################
# Bump Maps
#######################################################################################

def ReadNormalMapHeader(file, chunkEnd): 
    number = ReadSignedByte(file)
    typeName = ReadLongFixedString(file)
    reserved = ReadLong(file)
    return struct_w3d.MeshNormalMapHeader(number = number, typeName = typeName, reserved = reserved)

def ReadNormalMapEntryStruct(file, self, chunkEnd, entryStruct):
    type = ReadLong(file) #1 texture, 2 bumpScale/ specularExponent, 5 color, 7 alphaTest
    size = ReadLong(file)
    name = ReadString(file)

    if name == "DiffuseTexture":
        entryStruct.unknown = ReadLong(file)
        entryStruct.diffuseTexName = ReadString(file)
    elif name == "NormalMap":
        entryStruct.unknown_nrm = ReadLong(file)
        entryStruct.normalMap = ReadString(file)
    elif name == "BumpScale":
        entryStruct.bumpScale = ReadFloat(file)
    elif name == "AmbientColor":
        entryStruct.ambientColor = (ReadFloat(file), ReadFloat(file), ReadFloat(file), ReadFloat(file))
    elif name == "DiffuseColor":
        entryStruct.diffuseColor = (ReadFloat(file), ReadFloat(file), ReadFloat(file), ReadFloat(file))
    elif name == "SpecularColor":
        entryStruct.specularColor = (ReadFloat(file), ReadFloat(file), ReadFloat(file), ReadFloat(file))
    elif name == "SpecularExponent":
        entryStruct.specularExponent = ReadFloat(file)
    elif name == "AlphaTestEnable":
        entryStruct.alphaTestEnable = ReadUnsignedByte(file)
    else:
        self.report({'ERROR'}, "unknown NormalMapEntryStruct: %s" % name)
        print("!!!unknown NormalMapEntryStruct: %s" % name)
        while file.tell() < chunkEnd:
            file.read(1)
    return entryStruct

def ReadNormalMap(file, self, chunkEnd):
    Header = struct_w3d.MeshNormalMapHeader()
    EntryStruct = struct_w3d.MeshNormalMapEntryStruct()
    while file.tell() < chunkEnd:
        Chunktype = ReadLong(file)
        Chunksize = GetChunkSize(ReadLong(file))
        subChunkEnd = file.tell() + Chunksize
        if Chunktype == 82:
            Header = ReadNormalMapHeader(file, subChunkEnd)
        elif Chunktype == 83:
            EntryStruct = ReadNormalMapEntryStruct(file, self, subChunkEnd, EntryStruct)
        else:
            self.report({'ERROR'}, "unknown chunktype in NormalMap: %s" % chunkType)
            print("!!!unknown chunktype in NormalMap: %s" % chunkType)
            file.seek(Chunksize, 1)
    return struct_w3d.MeshNormalMap(header = Header, entryStruct = EntryStruct)

def ReadBumpMapArray(file, self, chunkEnd):
    NormalMap = struct_w3d.MeshNormalMap()
    while file.tell() < chunkEnd:
        Chunktype = ReadLong(file)
        Chunksize = GetChunkSize(ReadLong(file))
        subChunkEnd = file.tell() + Chunksize
        if Chunktype == 81:
            NormalMap = ReadNormalMap(file, self, subChunkEnd)
        else:
            self.report({'ERROR'}, "unknown chunktype in BumpMapArray: %s" % chunkType)
            print("!!!unknown chunktype in BumpMapArray: %s" % chunkType)
            file.seek(Chunksize, 1)
    return struct_w3d.MeshBumpMapArray(normalMap = NormalMap)

#######################################################################################
# AABTree (Axis-aligned-bounding-box)
#######################################################################################	

def ReadAABTreeHeader(file, chunkEnd):
    nodeCount = ReadLong(file)
    polyCount = ReadLong(file)
    #padding of the header
    while file.tell() < chunkEnd:
        file.read(4)
    return struct_w3d.AABTreeHeader(nodeCount = nodeCount, polyCount = polyCount)

def ReadAABTreePolyIndices(file, chunkEnd):
    polyIndices = []
    while file.tell() < chunkEnd:
        polyIndices.append(ReadLong(file))
    return polyIndices

def ReadAABTreeNodes(file, chunkEnd):
    nodes = []
    while file.tell() < chunkEnd:
        Min = ReadVector(file) # <-
        Max = ReadVector(file) # <- is mouse within these values
        FrontOrPoly0 = ReadLong(file)	  # <- if true check these two
        BackOrPolyCount = ReadLong(file)   # <-
        # if within these, check their children
        #etc bis du irgendwann angekommen bist wos nur noch poly eintraege gibt dann hast du nen index und nen count parameter der dir sagt wo die polys die von dieser bounding box umschlossen sind liegen und wie viele es sind
        # die gehst du dann alle durch wo du halt einfach nen test machst ob deine position xyz in dem poly liegt oder ausserhalb		 
        nodes.append(struct_w3d.AABTreeNode(min = Min, max = Max, frontOrPoly0 = FrontOrPoly0, backOrPolyCount = BackOrPolyCount))
    return nodes

#Axis-Aligned-Bounding-Box tree
def ReadAABTree(file, self, chunkEnd):
    aabtree = struct_w3d.MeshAABTree()
    while file.tell() < chunkEnd:
        Chunktype = ReadLong(file)
        Chunksize = GetChunkSize(ReadLong(file))
        subChunkEnd = file.tell() + Chunksize
        if Chunktype == 145:
            aabtree.header = ReadAABTreeHeader(file, subChunkEnd)
        elif Chunktype == 146:
            aabtree.polyIndices = ReadAABTreePolyIndices(file, subChunkEnd)
        elif Chunktype == 147:
            aabtree.nodes = ReadAABTreeNodes(file, subChunkEnd)
        else:
            self.report({'ERROR'}, "unknown chunktype in AABTree: %s" % chunkType)
            print("!!!unknown chunktype in AABTree: %s" % chunkType)
            file.seek(Chunksize, 1)
    return aabtree

#######################################################################################
# Mesh
#######################################################################################	

def ReadMeshHeader(file):
    result = struct_w3d.MeshHeader(version = GetVersion(ReadLong(file)), attrs =  ReadLong(file), meshName = ReadFixedString(file),
        containerName = ReadFixedString(file),faceCount = ReadLong(file),
        vertCount = ReadLong(file), matlCount = ReadLong(file), damageStageCount = ReadLong(file), sortLevel = ReadLong(file),
        prelitVersion = ReadLong(file), futureCount = ReadLong(file),
        vertChannelCount = ReadLong(file), faceChannelCount = ReadLong(file),
        #bounding volumes
        minCorner = ReadVector(file),
        maxCorner = ReadVector(file),
        sphCenter = ReadVector(file),
        sphRadius =	 ReadFloat(file))
    return result

def ReadMesh(self, file, chunkEnd):
    MeshVerticesInfs = []
    MeshVertices = []
    MeshVerticesCopy = []
    MeshNormals = []
    MeshNormalsCopy = []
    MeshVerticeMats = []
    MeshHeader = struct_w3d.MeshHeader()
    MeshMaterialInfo = struct_w3d.MeshMaterialSetInfo()
    MeshFaces = []
    MeshMaterialPass = struct_w3d.MeshMaterialPass()
    MeshShadeIds = []
    MeshShaders = []
    MeshTextures = []
    MeshUsertext = ""
    MeshBumpMaps = struct_w3d.MeshBumpMapArray()
    MeshAABTree = struct_w3d.MeshAABTree()

    #print("\n### NEW MESH: ###")
    while file.tell() < chunkEnd:
        Chunktype = ReadLong(file)
        Chunksize = GetChunkSize(ReadLong(file))
        subChunkEnd = file.tell() + Chunksize

        if Chunktype == 2:
            try:
                MeshVertices = ReadMeshVerticesArray(file, subChunkEnd)
                #print("Vertices")
            except:
                self.report({'ERROR'}, "Mistake while reading Vertices (Mesh) Byte:%s" % file.tell())
                print("Mistake while reading Vertices (Mesh) Byte:%s" % file.tell())
                e = sys.exc_info()[1]
                print(e)
            temp = 0 
        elif Chunktype == 3072:
            try:
                MeshVerticesCopy = ReadMeshVerticesArray(file, subChunkEnd)
                #print("Vertices-Copy")
            except:
                self.report({'ERROR'}, "Mistake while reading Vertices-Copy (Mesh) Byte:%s" % file.tell())
                print("Mistake while reading Vertices-Copy (Mesh) Byte:%s" % file.tell())
                e = sys.exc_info()[1]
                print(e)
        elif Chunktype == 3:
            try:
                MeshNormals = ReadMeshVerticesArray(file, subChunkEnd)
                #print("Normals")
            except:
                self.report({'ERROR'}, "Mistake while reading Normals (Mesh) Byte:%s" % file.tell())
                print("Mistake while reading Normals (Mesh) Byte:%s" % file.tell())
                e = sys.exc_info()[1]
                print(e)
        elif Chunktype == 3073:
            try:
                MeshNormalsCopy = ReadMeshVerticesArray(file, subChunkEnd)
                #print("Normals-Copy")
            except:
                self.report({'ERROR'}, "Mistake while reading Normals-Copy (Mesh) Byte:%s" % file.tell())
                print("Mistake while reading Normals-Copy (Mesh) Byte:%s" % file.tell())
                e = sys.exc_info()[1]
                print(e)
        elif Chunktype == 12:
            try:
                MeshUsertext = ReadString(file)
                #print("Usertext")
                #print(MeshUsertext)
            except:
                self.report({'ERROR'}, "Mistake while reading Usertext (Mesh) Byte:%s" % file.tell())
                print("Mistake while reading Usertext (Mesh) Byte:%s" % file.tell())
                e = sys.exc_info()[1]
                print(e)
        elif Chunktype == 14:
            try:
                MeshVerticesInfs = ReadMeshVertexInfluences(file, subChunkEnd)
                #print("VertInfs")
            except:
                self.report({'ERROR'}, "Mistake while reading Usertext (Mesh) Byte:%s" % file.tell())
                print("Mistake while reading Usertext (Mesh) Byte:%s" % file.tell())
                e = sys.exc_info()[1]
                print(e)
        elif Chunktype == 31:
            try:
                MeshHeader = ReadMeshHeader(file)
                #print("## Name: " + MeshHeader.meshName)
                #print("Header")
            except:
                self.report({'ERROR'}, "Mistake while reading Mesh Header (Mesh) Byte:%s" % file.tell())
                print("Mistake while reading Mesh Header (Mesh) Byte:%s" % file.tell())
                e = sys.exc_info()[1]
                print(e)
        elif Chunktype == 32:
            try:
                MeshFaces = ReadMeshFaceArray(file, subChunkEnd)
                #print("Faces")
            except:
                self.report({'ERROR'}, "Mistake while reading Mesh Faces (Mesh) Byte:%s" % file.tell())
                print("Mistake while reading Mesh Faces (Mesh) Byte:%s" % file.tell())
                e = sys.exc_info()[1]
                print(e)
        elif Chunktype == 34:
            try:
                MeshShadeIds = ReadLongArray(file, subChunkEnd)
                #print("Shade IDs")
            except:
                self.report({'ERROR'}, "Mistake while reading MeshShadeIds (Mesh) Byte:%s" % file.tell())
                print("Mistake while reading MeshShadeIds (Mesh) Byte:%s" % file.tell())
                e = sys.exc_info()[1]
                print(e)
        elif Chunktype == 40:
            try:
                MeshMaterialInfo = ReadMeshMaterialSetInfo(file)
                #print("MaterialInfo")
            except:
                self.report({'ERROR'}, "Mistake while reading MeshMaterialInfo (Mesh) Byte:%s" % file.tell())
                print("Mistake while reading MeshMaterialInfo (Mesh) Byte:%s" % file.tell())
                e = sys.exc_info()[1]
                print(e)
        elif Chunktype == 41:
            try:
                MeshShaders = ReadMeshShaderArray(file, subChunkEnd)
                #print("MeshShader")
            except:
                self.report({'ERROR'}, "Mistake while reading MeshShaders (Mesh) Byte:%s" % file.tell())
                print("Mistake while reading MeshShaders (Mesh) Byte:%s" % file.tell())
                e = sys.exc_info()[1]
                print(e)
        elif Chunktype == 42:
            try:
                MeshVerticeMats = ReadMeshMaterialArray(file, self, subChunkEnd)
                #print("VertMats")
            except:
                self.report({'ERROR'}, "Mistake while reading VerticeMaterials (Mesh) Byte:%s" % file.tell())
                print("Mistake while reading VerticeMaterials (Mesh) Byte:%s" % file.tell())
                e = sys.exc_info()[1]
                print(e)
        elif Chunktype == 48:
            try:
                MeshTextures = ReadTextureArray(file, self, subChunkEnd)
                #print("Textures")
            except:
                self.report({'ERROR'}, "Mistake while reading MeshTextures (Mesh) Byte:%s" % file.tell())
                print("Mistake while reading MeshTextures (Mesh) Byte:%s" % file.tell())
                e = sys.exc_info()[1]
                print(e)
        elif Chunktype == 56:
            try:
                MeshMaterialPass = ReadMeshMaterialPass(file, self, subChunkEnd)
                #print("MatPass")
            except:
                self.report({'ERROR'}, "Mistake while reading MeshMaterialPass (Mesh) Byte:%s" % file.tell())
                print("Mistake while reading MeshMaterialPass (Mesh) Byte:%s" % file.tell())
                e = sys.exc_info()[1]
                print(e)
        elif Chunktype == 80:
            try:
                MeshBumpMaps = ReadBumpMapArray(file, self, subChunkEnd)
                #print("BumpMapArray")
            except:
                self.report({'ERROR'}, "Mistake while reading BumpMapArray (Mesh) Byte:%s" % file.tell())
                print("Mistake while reading BumpMapArray (Mesh) Byte:%s" % file.tell())
                e = sys.exc_info()[1]
                print(e)
        elif Chunktype == 96:
            try:
                ReadMeshVerticesArray(file, subChunkEnd)
                #print("Tangents") #for normal mapping
            except:
                self.report({'ERROR'}, "Mistake while reading Tangents (Mesh) Byte:%s" % file.tell())
                print("Mistake while reading Tangents (Mesh) Byte:%s" % file.tell())
                e = sys.exc_info()[1]
                print(e)
        elif Chunktype == 97:
            try:
                ReadMeshVerticesArray(file, subChunkEnd)
                #print("Binormals") #for normal mapping
            except:
                self.report({'ERROR'}, "Mistake while reading Binormals (Mesh) Byte:%s" % file.tell())
                print("Mistake while reading Binormals (Mesh) Byte:%s" % file.tell())
                e = sys.exc_info()[1]
                print(e)
        elif Chunktype == 144:
            try:
                MeshAABTree = ReadAABTree(file, self, subChunkEnd)
                #print("AABTree")
            except:
                self.report({'ERROR'}, "Mistake while reading AABTree (Mesh) Byte:%s" % file.tell())
                print("Mistake while reading AABTree (Mesh) Byte:%s" % file.tell())
                e = sys.exc_info()[1]
                print(e)
        else:
            self.report({'ERROR'}, "unknown chunktype in Mesh: %s" % Chunktype)
            print("!!!unknown chunktype in Mesh: %s" % Chunktype)
            file.seek(Chunksize,1)
    return struct_w3d.Mesh(header = MeshHeader, verts = MeshVertices, verts_copy = MeshVerticesCopy, normals = MeshNormals, 
                normals_copy = MeshNormalsCopy, vertInfs = MeshVerticesInfs, faces = MeshFaces, userText = MeshUsertext, 
                shadeIds = MeshShadeIds, matInfo = MeshMaterialInfo, shaders = MeshShaders, vertMatls = MeshVerticeMats,
                textures = MeshTextures, matlPass = MeshMaterialPass, bumpMaps = MeshBumpMaps, aabtree = MeshAABTree)

#######################################################################################
# loadTexture
#######################################################################################

def LoadTexture(self, givenfilepath, mesh, texName, tex_type, destBlend):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    default_tex = script_directory + "/default_tex.dds"

    found_img = False

    basename = os.path.splitext(texName)[0]

    #test if image file has already been loaded
    for image in bpy.data.images:
        if basename == os.path.splitext(image.name)[0]:
            img = image
            found_img = True

    # Create texture slot in material
    mTex = mesh.materials[0].texture_slots.add()
    mTex.use_map_alpha = True

    if found_img == False:
        tgapath = os.path.dirname(givenfilepath) + "/" + basename + ".tga"
        ddspath = os.path.dirname(givenfilepath) + "/" + basename + ".dds"
        tgapath = InsensitivePath(tgapath)
        ddspath = InsensitivePath(ddspath)
        img = None
        try:
            img = bpy.data.images.load(tgapath)
        except:
            try:
                img = bpy.data.images.load(ddspath)
            except:
                self.report({'ERROR'}, "Cannot load texture " + basename)
                print("!!! texture file not found " + basename)
                img = bpy.data.images.load(default_tex)

        cTex = bpy.data.textures.new(texName, type = 'IMAGE')
        cTex.image = img

        if destBlend == 0:
            cTex.use_alpha = True
        else:
            cTex.use_alpha = False

        if tex_type == "normal":
            cTex.use_normal_map = True
            cTex.filter_size = 0.1
            cTex.use_filter_size_min = True
        mTex.texture = cTex	
    else:
        mTex.texture = bpy.data.textures[texName]

    mTex.texture_coords = 'UV'
    mTex.mapping = 'FLAT'
    if tex_type == "normal":
       mTex.normal_map_space = 'TANGENT'
       mTex.use_map_color_diffuse = False
       mTex.use_map_normal = True
       mTex.normal_factor = 1.0
       mTex.diffuse_color_factor = 0.0

#######################################################################################
# loadSkeleton 
#######################################################################################

def LoadSKL(self, sklpath):
    #print("\n### SKELETON: ###")
    Hierarchy = struct_w3d.Hierarchy()
    file = InsensitiveOpen(sklpath)
    file.seek(0,2)
    filesize = file.tell()
    file.seek(0,0)

    while file.tell() < filesize:
        chunkType = ReadLong(file)
        Chunksize =	 GetChunkSize(ReadLong(file))
        chunkEnd = file.tell() + Chunksize
        if chunkType == 256:
            Hierarchy = ReadHierarchy(file, self, chunkEnd)
            file.seek(chunkEnd, 0)
        else:
            file.seek(Chunksize, 1)
    file.close()
    return Hierarchy
    
#######################################################################################
# load bone mesh file
#######################################################################################

def loadBoneMesh(self, filepath):
    file = open(filepath,"rb")
    file.seek(0,2)
    filesize = file.tell()
    file.seek(0,0)
    Mesh = struct_w3d.Mesh()
    
    while file.tell() < filesize:
        Chunktype = ReadLong(file)
        Chunksize =	 GetChunkSize(ReadLong(file))
        chunkEnd = file.tell() + Chunksize
        if Chunktype == 0:
            Mesh = ReadMesh(self, file, chunkEnd)
        else:
            file.seek(Chunksize,1)
    file.close()
    
    Vertices = Mesh.verts
    Faces = []
    for f in Mesh.faces:
        Faces.append(f.vertIds)

    #create the mesh
    mesh = bpy.data.meshes.new("skl_bone")
    mesh.from_pydata(Vertices,[],Faces)
    mesh_ob = bpy.data.objects.new("skl_bone", mesh)
    return mesh 
    
#######################################################################################
# createArmature
#######################################################################################
    
def createArmature(self, Hierarchy, amtName, subObjects):
    amt = bpy.data.armatures.new(Hierarchy.header.name)
    amt.show_names = True
    rig = bpy.data.objects.new(amtName, amt)
    rig.location = Hierarchy.header.centerPos
    rig.rotation_mode = 'QUATERNION'
    rig.show_x_ray = True
    rig.track_axis = "POS_X"
    bpy.context.scene.objects.link(rig) # Link the object to the active scene
    bpy.context.scene.objects.active = rig
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.context.scene.update()

    non_bone_pivots = []
    for obj in subObjects: 
        non_bone_pivots.append(Hierarchy.pivots[obj.boneIndex])

    #create the bones from the pivots
    for pivot in Hierarchy.pivots:
        #test for non_bone_pivots
        if non_bone_pivots.count(pivot) > 0:
                continue #do not create a bone
        bone = amt.edit_bones.new(pivot.name)
        if pivot.parentID > 0:
            parent_pivot =	Hierarchy.pivots[pivot.parentID]
            parent = amt.edit_bones[parent_pivot.name]
            bone.parent = parent
            size = pivot.position.x
        bone.head = Vector((0.0, 0.0, 0.0))
        #has to point in y direction that the rotation is applied correctly
        bone.tail = Vector((0.0, 0.1, 0.0))

    #pose the bones
    bpy.ops.object.mode_set(mode = 'POSE')
    
    script_directory = os.path.dirname(os.path.abspath(__file__))
    bone_file = script_directory + "/bone.W3D"
    
    bone_shape = loadBoneMesh(self, bone_file)

    for pivot in Hierarchy.pivots:
        #test for non_bone_pivots
        if non_bone_pivots.count(pivot) > 0:
            continue #do not create a bone
        bone = rig.pose.bones[pivot.name]
        bone.location = pivot.position
        bone.rotation_mode = 'QUATERNION'
        bone.rotation_euler = pivot.eulerAngles
        bone.rotation_quaternion = pivot.rotation
        #bpy.data.objects["Bone"].scale = (4, 4, 4)
        bone.custom_shape = bpy.data.objects["skl_bone"]

    bpy.ops.object.mode_set(mode = 'OBJECT')
    
    #delete the mesh afterwards
    for ob in bpy.context.scene.objects:
        if ob.type == 'MESH' and ob.name.startswith("skl_bone"):
            ob.delete()
    return rig
    
#######################################################################################
# createAnimation
#######################################################################################

def createAnimation(self, Animation, Hierarchy, rig, compressed):
    bpy.data.scenes["Scene"].render.fps = Animation.header.frameRate
    bpy.data.scenes["Scene"].frame_start = 0
    bpy.data.scenes["Scene"].frame_end = Animation.header.numFrames - 1

    #create the data
    translation_data = []
    for pivot in range (0, len(Hierarchy.pivots)):
        pivot = []
        for frame in range (0, Animation.header.numFrames - 1):
            frame = []
            frame.append(None)
            frame.append(None)
            frame.append(None)
            pivot.append(frame)
        translation_data.append(pivot)
    
    for channel in Animation.channels:
        if (channel.pivot == 0):
            continue   #skip roottransform
        rest_rotation = Hierarchy.pivots[channel.pivot].rotation
        pivot = Hierarchy.pivots[channel.pivot] 
        try:
            obj = rig.pose.bones[pivot.name]
        except:
            obj = bpy.data.objects[pivot.name]
            
        # ANIM_CHANNEL_X
        if channel.type == 0:	
            if compressed:
                for key in channel.timeCodedKeys:
                    translation_data[channel.pivot][key.frame][0] = key.value
            else:
                for frame in range(channel.firstFrame, channel.lastFrame):
                    translation_data[channel.pivot][frame][0] = channel.data[frame - channel.firstFrame]
        # ANIM_CHANNEL_Y
        elif channel.type == 1:	  
            if compressed:
                for key in channel.timeCodedKeys:
                    translation_data[channel.pivot][key.frame][1] = key.value
            else:
                for frame in range(channel.firstFrame, channel.lastFrame):
                    translation_data[channel.pivot][frame][1] = channel.data[frame - channel.firstFrame]
        # ANIM_CHANNEL_Z
        elif channel.type == 2:	 
            if compressed:
                for key in channel.timeCodedKeys:
                    translation_data[channel.pivot][key.frame][2] = key.value
            else:
                for frame in range(channel.firstFrame, channel.lastFrame):
                    translation_data[channel.pivot][frame][2] = channel.data[frame - channel.firstFrame]
        
        # ANIM_CHANNEL_Q
        elif channel.type == 6:	 
            obj.rotation_mode = 'QUATERNION'
            if compressed:
                for key in channel.timeCodedKeys:
                    obj.rotation_quaternion = rest_rotation * key.value
                    obj.keyframe_insert(data_path='rotation_quaternion', frame = key.frame) 
            else:
                for frame in range(channel.firstFrame, channel.lastFrame):
                    obj.rotation_quaternion = rest_rotation * channel.data[frame - channel.firstFrame]
                    obj.keyframe_insert(data_path='rotation_quaternion', frame = frame)	 
        else:
            self.report({'ERROR'}, "unsupported channel type: %s" %channel.type)
            print("unsupported channel type: %s" %channel.type)

    for pivot in range(1, len(Hierarchy.pivots)):
        rest_location = Hierarchy.pivots[pivot].position
        rest_rotation = Hierarchy.pivots[pivot].rotation 
        try:
            obj = rig.pose.bones[Hierarchy.pivots[pivot].name]
        except:
            obj = bpy.data.objects[Hierarchy.pivots[pivot].name]
            
        for frame in range (0, Animation.header.numFrames):
            bpy.context.scene.frame_set(frame)
            pos = Vector((0.0, 0.0, 0.0))

            if not translation_data[pivot][frame][0] == None:
                pos[0] = translation_data[pivot][frame][0]
                if not translation_data[pivot][frame][1] == None:
                    pos[1] = translation_data[pivot][frame][1]
                if not translation_data[pivot][frame][2] == None:
                    pos[2] = translation_data[pivot][frame][2]
                obj.location = rest_location + (rest_rotation * pos)
                obj.keyframe_insert(data_path='location', frame = frame) 
                    
            elif not translation_data[pivot][frame][1] == None:
                pos[1] = translation_data[pivot][frame][1]
                if not translation_data[pivot][frame][2] == None:
                    pos[2] = translation_data[pivot][frame][2]
                obj.location = rest_location + (rest_rotation * pos)
                obj.keyframe_insert(data_path='location', frame = frame) 
                
            elif not translation_data[pivot][frame][2] == None:
                pos[2] = translation_data[pivot][frame][2]
                obj.location = rest_location + (rest_rotation * pos)
                obj.keyframe_insert(data_path='location', frame = frame)

#######################################################################################
# create Box
#######################################################################################
        
def createBox(Box):	
    name = "BOUNDINGBOX" #to keep name always equal (sometimes it is "BOUNDING BOX")
    x = Box.extend[0]/2.0
    y = Box.extend[1]/2.0
    z = Box.extend[2]

    verts = [(x, y, z), (-x, y, z), (-x, -y, z), (x, -y, z), (x, y, 0), (-x, y, 0), (-x, -y, 0), (x, -y, 0)]
    faces = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]

    cube = bpy.data.meshes.new(name)
    box = bpy.data.objects.new(name, cube)
    mat = bpy.data.materials.new("BOUNDINGBOX.Material")
    mat.use_shadeless = True
    mat.diffuse_color = (Box.color.r, Box.color.g, Box.color.b)
    cube.materials.append(mat)
    box.location = Box.center
    bpy.context.scene.objects.link(box)
    cube.from_pydata(verts, [], faces)
    cube.update(calc_edges = True)
    #set render mode to wireframe
    box.draw_type = 'WIRE'
    
#######################################################################################
# Main Import
#######################################################################################

def MainImport(givenfilepath, context, self):
    file = open(givenfilepath,"rb")
    file.seek(0,2)
    filesize = file.tell()
    file.seek(0,0)
    Meshes = []
    Box = struct_w3d.Box()
    Textures = []
    Hierarchy = struct_w3d.Hierarchy()
    Animation = struct_w3d.Animation()
    CompressedAnimation = struct_w3d.CompressedAnimation()
    HLod = struct_w3d.HLod()
    amtName = ""

    while file.tell() < filesize:
        Chunktype = ReadLong(file)
        Chunksize =	 GetChunkSize(ReadLong(file))
        #print(Chunksize)
        chunkEnd = file.tell() + Chunksize
        if Chunktype == 0:
            m = ReadMesh(self, file, chunkEnd)
            Meshes.append(m)
            file.seek(chunkEnd,0)

        elif Chunktype == 256:
            Hierarchy = ReadHierarchy(file, self, chunkEnd)
            file.seek(chunkEnd,0)

        elif Chunktype == 512:
            Animation = ReadAnimation(file, self, chunkEnd)
            file.seek(chunkEnd,0)

        elif Chunktype == 640:
            CompressedAnimation = ReadCompressedAnimation(file, self, chunkEnd)
            file.seek(chunkEnd,0)

        elif Chunktype == 1792:
            HLod = ReadHLod(file, self, chunkEnd)
            file.seek(chunkEnd,0)

        elif Chunktype == 1856:
            Box = ReadBox(file)
            file.seek(chunkEnd,0)

        else:
            self.report({'ERROR'}, "unknown chunktype in File: %s" % Chunktype)
            print("!!!unknown chunktype in File: %s" % Chunktype)
            file.seek(Chunksize,1)

    file.close()

    if not Box.name == "":
        createBox(Box)
    
    #load skeleton (_skl.w3d) file if needed 
    sklpath = ""
    if HLod.header.modelName != HLod.header.HTreeName:
        sklpath = os.path.dirname(givenfilepath) + "/" + HLod.header.HTreeName.lower() + ".w3d"
        try:
            Hierarchy = LoadSKL(self, sklpath)
        except:
            self.report({'ERROR'}, "skeleton file not found: " + HLod.header.HTreeName) 
            print("!!! skeleton file not found: " + HLod.header.HTreeName)
            
    elif (not Animation.header.name == "") and (Hierarchy.header.name == ""):
        sklpath = os.path.dirname(givenfilepath) + "/" + Animation.header.hieraName.lower() + ".w3d"
        try:
            Hierarchy = LoadSKL(self, sklpath)
        except:
            self.report({'ERROR'}, "skeleton file not found: " + Animation.header.hieraName) 
            print("!!! skeleton file not found: " + Animation.header.hieraName)
            
    elif (not CompressedAnimation.header.name == "") and (Hierarchy.header.name == ""):
        sklpath = os.path.dirname(givenfilepath) + "/" + CompressedAnimation.header.hieraName.lower() + ".w3d"
        try:
            Hierarchy = LoadSKL(self, sklpath)
        except:
            self.report({'ERROR'}, "skeleton file not found: " + CompressedAnimation.header.hieraName) 
            print("!!! skeleton file not found: " + CompressedAnimation.header.hieraName)

    #create skeleton if needed
    if not HLod.header.modelName == HLod.header.HTreeName:
        amtName = Hierarchy.header.name
        found = False
        for obj in bpy.data.objects:
            if obj.name == amtName:
                rig = obj
                found = True
        if not found:
            rig = createArmature(self, Hierarchy, amtName, HLod.lodArray.subObjects)
        if len(Meshes) > 0:
            #if a mesh is loaded set the armature invisible
            rig.hide = True

    for m in Meshes:	
        Vertices = m.verts
        Faces = []

        for f in m.faces:
            Faces.append(f.vertIds)

        #create the mesh
        mesh = bpy.data.meshes.new(m.header.meshName)
        mesh.from_pydata(Vertices,[],Faces)
        mesh.uv_textures.new("UVW")

        bm = bmesh.new()
        bm.from_mesh(mesh)

        #create the uv map
        uv_layer = bm.loops.layers.uv.verify()
        bm.faces.layers.tex.verify()

        index = 0
        if len(m.matlPass.txStage.txCoords)>0:
            for f in bm.faces:
                f.loops[0][uv_layer].uv = m.matlPass.txStage.txCoords[Faces[index][0]]
                f.loops[1][uv_layer].uv = m.matlPass.txStage.txCoords[Faces[index][1]]
                f.loops[2][uv_layer].uv = m.matlPass.txStage.txCoords[Faces[index][2]]
                index+=1
                
        bm.to_mesh(mesh)

        mesh_ob = bpy.data.objects.new(m.header.meshName, mesh)
        mesh_ob['userText'] = m.userText

        #show the bounding boxes
        #mesh_ob.show_bounds = True
        #mesh_ob.draw_bounds_type = "BOX"
        
        #create the material for each mesh because the same material could be used with multiple textures
        destBlend = 0
        for vm in m.vertMatls:
            mat = bpy.data.materials.new(m.header.meshName + "." + vm.vmName)
            mat.use_shadeless = True
            if len(m.shaders) > 0:
                if m.shaders[0].alphaTest == 1:
                    mat.use_transparency = True
                    mat.transparency_method = "Z_TRANSPARENCY"
                if m.shaders[0].destBlend == 1:
                    mat.use_transparency = True
                    mat.transparency_method = "Z_TRANSPARENCY"
                    destBlend = 1
            mat.alpha = vm.vmInfo.translucency
            mat.specular_color = (vm.vmInfo.specular.r, vm.vmInfo.specular.g, vm.vmInfo.specular.b)
            mat.diffuse_color = (vm.vmInfo.diffuse.r, vm.vmInfo.diffuse.g, vm.vmInfo.diffuse.b)
            #mat.specular_intensity = vm.vmInfo.shininess
            #mat.diffuse_intensity = vm.vmInfo.opacity
            mesh.materials.append(mat)
            
        for tex in m.textures:
            LoadTexture(self, givenfilepath, mesh, tex.name, "diffuse", destBlend)
            
        #test if mesh has a normal map (if it has the diffuse texture is also stored there and it has no standard material)
        if not m.bumpMaps.normalMap.entryStruct.normalMap == "":
            mat = bpy.data.materials.new(m.header.meshName + ".BumpMaterial")
            mat.use_shadeless = False
            if len(m.shaders) > 0:
                if m.shaders[0].alphaTest == 1:
                    mat.use_transparency = True
                    mat.transparency_method = "Z_TRANSPARENCY"
            mat.alpha = 0.0
            mesh.materials.append(mat)
            #to show textures properly first apply the normal texture
            if not m.bumpMaps.normalMap.entryStruct.normalMap == "":
                LoadTexture(self, givenfilepath, mesh, m.bumpMaps.normalMap.entryStruct.normalMap, "normal", destBlend)
                # set the lamp to sun mode to make bump maps visible
                try: 
                    bpy.data.objects["Lamp"].location = (5.0, 5.0, 5.0)
                    bpy.data.lamps["Lamp"].type = "SUN"
                except:
                    lamp_data = bpy.data.lamps.new(name="Lamp", type='SUN')
                    lamp_object = bpy.data.objects.new(name="Lamp", object_data=lamp_data)
                    bpy.context.scene.objects.link(lamp_object)
                    lamp_object.location = (5.0, 5.0, 5.0)
            if not m.bumpMaps.normalMap.entryStruct.diffuseTexName == "":
                LoadTexture(self, givenfilepath, mesh, m.bumpMaps.normalMap.entryStruct.diffuseTexName, "diffuse", destBlend)
                
                
    for m in Meshes: #need an extra loop because the order of the meshes is random
        mesh_ob = bpy.data.objects[m.header.meshName]
        #hierarchy stuff
        if Hierarchy.header.pivotCount > 0:
            # mesh header attributes
            #		 0		-> normal mesh
            #		 8192	-> normal mesh - two sided
            #		 32768	-> normal mesh - cast shadow
            #		 40960	-> normal mesh - two sided - cast shadow
            #		 131072 -> skin
            #		 139264 -> skin - two sided
            #		 143360 -> skin - two sided - hidden
            #		 163840 -> skin - cast shadow
            #		 172032 -> skin - two sided - cast shadow
            #		 393216 -> normal mesh - camera oriented (points _towards_ camera)
            type = m.header.attrs
            if type == 8192 or type == 40960 or type == 139264 or type == 143360 or type == 172032:
                mesh.show_double_sided = True
                
            if type == 0 or type == 8192 or type == 32768 or type == 40960 or type == 393216:
                for pivot in Hierarchy.pivots:
                    if pivot.name == m.header.meshName:
                        mesh_ob.rotation_mode = 'QUATERNION'
                        mesh_ob.location =	pivot.position
                        mesh_ob.rotation_euler = pivot.eulerAngles
                        mesh_ob.rotation_quaternion = pivot.rotation
                        
                        #test if the pivot has a parent pivot and parent the corresponding bone to the mesh if it has
                        if pivot.parentID > 0:
                            parent_pivot = Hierarchy.pivots[pivot.parentID]
                            try:
                                mesh_ob.parent = bpy.data.objects[parent_pivot.name]
                            except:
                                mesh_ob.parent = bpy.data.objects[amtName]
                                mesh_ob.parent_bone = parent_pivot.name
                                mesh_ob.parent_type = 'BONE'

            elif type == 131072 or type == 139264 or type == 143360 or type == 163840 or type == 172032:
                for pivot in Hierarchy.pivots:
                    mesh_ob.vertex_groups.new(pivot.name)
                        
                for i in range(len(m.vertInfs)):
                    weight = m.vertInfs[i].boneInf
                    if weight == 0.0:
                        weight = 1.0
                    mesh_ob.vertex_groups[m.vertInfs[i].boneIdx].add([i], weight, 'REPLACE')
                    
                    #two bones are not working yet
                    #mesh_ob.vertex_groups[m.vertInfs[i].xtraIdx].add([i], m.vertInfs[i].xtraInf, 'REPLACE')

                mod = mesh_ob.modifiers.new(amtName, 'ARMATURE')
                mod.object = rig
                mod.use_bone_envelopes = False
                mod.use_vertex_groups = True
                
                #to keep the transformations while mesh is in edit mode!!!
                mod.show_in_editmode = True
                mod.show_on_cage = True
            else:
                print("unsupported meshtype attribute: %i" %type)
                self.report({'ERROR'}, "unsupported meshtype attribute: %i" %type)
        bpy.context.scene.objects.link(mesh_ob) # Link the object to the active scene

    #animation stuff
    if not Animation.header.name == "":	
        try:
            rig = bpy.data.objects[Animation.header.hieraName]
            createAnimation(self, Animation, Hierarchy, rig, False)
        except:
            #the animation could be completely without a rig and bones
            createAnimation(self, Animation, Hierarchy, None, False)
            
    elif not CompressedAnimation.header.name == "":	
        rig = bpy.data.objects[CompressedAnimation.header.hieraName]
        createAnimation(self, CompressedAnimation, Hierarchy, rig, True)
        #try:
        #	 createAnimation(self, CompressedAnimation, Hierarchy, rig, True)
        #except:
        #	 #the animation could be completely without a rig and bones
        #	 createAnimation(self, CompressedAnimation, Hierarchy, None, True)
    
    #to render the loaded textures				
    bpy.context.scene.game_settings.material_mode = 'GLSL'
    #set render mode to textured or solid
    for scrn in bpy.data.screens:
        if scrn.name == 'Default':
            for area in scrn.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            if len(bpy.data.textures) > 1:
                                space.viewport_shade = 'TEXTURED'
                            else:
                                space.viewport_shade = 'SOLID'