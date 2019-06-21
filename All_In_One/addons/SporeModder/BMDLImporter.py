__author__ = 'Eric'

from collections import namedtuple
import math
import struct
#import bpy

class FileReader:
    def __init__(self, fileBuffer):
        self.fileBuffer = fileBuffer
        
    def tell(self):
        return self.fileBuffer.tell()
        
    def read(self, fmt):
        return struct.unpack(fmt, self.fileBuffer.read(struct.calcsize(fmt)))

    def readByte(self, endian='<'):
        return struct.unpack(endian + 'b', self.fileBuffer.read(1))[0]

    def readUByte(self, endian='<'):
        return struct.unpack(endian + 'B', self.fileBuffer.read(1))[0]

    def readShort(self, endian='<'):
        return struct.unpack(endian + 'h', self.fileBuffer.read(2))[0]

    def readUShort(self, endian='<'):
        return struct.unpack(endian + 'H', self.fileBuffer.read(2))[0]

    def readInt(self, endian='<'):
        return struct.unpack(endian + 'i', self.fileBuffer.read(4))[0]

    def readUInt(self, endian='<'):
        return struct.unpack(endian + 'I', self.fileBuffer.read(4))[0]

    def readFloat(self, endian='<'):
        return struct.unpack(endian + 'f', self.fileBuffer.read(4))[0]

    def readBoolean(self, endian='<'):
        return struct.unpack(endian + '?', self.fileBuffer.read(1))[0]
    
    def seek(self, offset):
        self.fileBuffer.seek(offset)
        
    def readString(self):
        stringBytes = bytearray()
        byte = self.readUByte()
        while byte != 0:
            stringBytes.append(byte)
            byte = self.readUByte()
        return stringBytes.decode('utf-8')
    
    
class BMDLVertex:
    def __init__(self):
        # size: 28 bytes
        self.pos = None
        # what about this?
        self.normal = None
        self.tangent = None
        self.uv = None
        self.color = None

    def read(self, file, elements):
        for fmt in elements:
            fmt.method(self, file)

    def readPosition(self, file):
        self.pos = file.read("3f")

    def readNormal(self, file):
        self.normal = file.readInt()

    def readTangent(self, file):
        self.tangent = file.readInt()

    def readUV(self, file):
        self.uv = [file.readFloat(), file.readFloat()]

    def readColor(self, file):
        self.color = file.readInt()

    @staticmethod
    def decodeColor(color):
        return [
            ((color & 0xFF0000) >> 16) / 255,
            ((color & 0xFF00) >> 8) / 255,
            (color & 0xFF) / 255
        ]

        
class BMDLBuffers:
    methods = {
        0: BMDLVertex.readPosition,
        1: BMDLVertex.readNormal,
        2: BMDLVertex.readTangent,
        4: BMDLVertex.readUV,
        5: BMDLVertex.readColor
        # 6 index
        # 7 weight
    }
    
    BMDLMesh = namedtuple("BMDLMesh", ['material', 'firstTriangle', 'triangleCount'])
    VertexElement = namedtuple("VertexElement", ['stream', 'offset', 'type', 'method'])
    
    def __init__(self, importer):
        self.importer = importer
        self.polyName = None
        self.elements = []
        self.vertices = []
        self.triangles = []
        self.meshes = []
        self.faceStart = 0
        
    def seekToSection(self, fileReader, offset):
        fileReader.seek(self.importer.header.dataStart + offset)
        
    def readFVF(self, fileReader, offsets):
        self.seekToSection(fileReader, offsets[0])
        polyNameOff, hash, null, fvfUnkCount = fileReader.read("4i")

        self.seekToSection(fileReader, polyNameOff)
        self.polyName = fileReader.readString()
        
        self.seekToSection(fileReader, offsets[1])
        vertStructOffset = fileReader.readInt()
        
        self.seekToSection(fileReader, offsets[2])
        vertStart = fileReader.readInt()
        
        self.seekToSection(fileReader, offsets[3])
        faceStart, vertCount, faceCount = fileReader.read("3i")
        vertSize = (faceStart - vertStart) // vertCount
        
        
        # Read vertex elements
        
        self.seekToSection(fileReader, vertStructOffset)
        vertStream = fileReader.readByte()
        fileReader.readByte()
        while vertStream != -1:
            vertOffset = fileReader.readShort()
            vertType = fileReader.readShort()
            vertMethod = BMDLBuffers.methods[fileReader.readShort()]
            self.elements.append(BMDLBuffers.VertexElement(vertStream, vertOffset, vertType, vertMethod))
            
            vertStream = fileReader.readByte()
            fileReader.readByte()
            
            
        # Read vertices
        self.seekToSection(fileReader, vertStart)
        for i in range(vertCount):
            self.seekToSection(fileReader, vertStart + (i*vertSize))
            
            vertex = BMDLVertex()
            vertex.read(fileReader, self.elements)
            self.vertices.append(vertex)
            
        
        # Read triangles
        self.seekToSection(fileReader, faceStart)
        for _ in range(faceCount // 3):
            self.triangles.append(fileReader.read("3H"))
            
        print()
        print(self.polyName)
        print("Vertex count: %d" % vertCount)
        print("Face count: %d" % faceCount)
        for element in self.elements:
            print("\t" + str(element))
            
    def readBuffer(self, fileReader, bufferInfo):
        self.seekToSection(fileReader, bufferInfo[2])
        
        for i in range(bufferInfo[1]):
            self.seekToSection(fileReader, bufferInfo[2] + (i * 44))
            fileReader.read("8f")  # probably bounding box
            materialIndex, firstIndex, faceCount = fileReader.read("3i")
            
            mesh = BMDLBuffers.BMDLMesh(self.importer.materials[materialIndex], firstIndex // 3, faceCount // 3)
            self.meshes.append(mesh)
        
        
class BMDLMaterial:
    MaterialProperty = namedtuple("MaterialProperty", ['name', 'hash', 'value'])
    MaterialFVF = namedtuple("MaterialFVF", ['typeName', 'name', 'typeHash', 'hash'])
    MaterialTexture = namedtuple("MaterialTexture", ['typeName', 'name', 'typeHash', 'hash'])
    
    def __init__(self, importer):
        self.importer = importer
        self.name = None
        self.hash = 0
        self.properties = [] 
        self.fvf = []
        self.textures = []
        
    def getTexture(self, name):
        for texture in self.textures:
            if texture.name == name:
                return texture
        return None
        
    def getProperty(self, name):
        for prop in self.properties:
            if prop.name == name:
                return prop
        return None    
        
    def seekToSection(self, fileReader, offset):
        fileReader.seek(self.importer.header.dataStart + offset)
        
    def read(self, fileReader, matOffsets):
        print(self.importer.header.dataStart)
        print(matOffsets)
        
        self.seekToSection(fileReader, matOffsets[0])
        nameOffset = fileReader.readInt()
        self.hash = fileReader.readUInt()
        unk = fileReader.readInt()
        propCount = fileReader.readInt()
        
        print([nameOffset, self.hash, unk, propCount])
    
        # Read the name
        self.seekToSection(fileReader, nameOffset)
        self.name = fileReader.readString()
        
        self.seekToSection(fileReader, matOffsets[1])
        propOffset, floatCount = fileReader.read("2i")
        
        self.seekToSection(fileReader, matOffsets[2])
        floatStart, texCount = fileReader.read("2i")
        
        self.seekToSection(fileReader, matOffsets[3])
        texStart, fvfCount = fileReader.read("2i")
        
        self.seekToSection(fileReader, matOffsets[4])
        fvfStart = fileReader.readInt()
        
        for i in range(propCount):
            self.seekToSection(fileReader, propOffset + (i*16))
            
            nameOffset = fileReader.readInt()
            hash = fileReader.readUInt()
            start = fileReader.readInt()
            usedFloat = fileReader.readInt()
            
            self.seekToSection(fileReader, floatStart + (start * 4))
            propValue = fileReader.read(usedFloat * "f")
            
            # Read the name
            self.seekToSection(fileReader, nameOffset)
            name = fileReader.readString()
            
            self.properties.append(BMDLMaterial.MaterialProperty(name, hash, propValue))
            
        for i in range(texCount):
            self.seekToSection(fileReader, texStart + (i*16))
            fvfTypeNameOffset, fvfTypeHash, fvfNameOffset, fvfHash = fileReader.read("4I")
            
            self.seekToSection(fileReader, fvfTypeNameOffset)
            fvfTypeName = fileReader.readString()
            
            self.seekToSection(fileReader, fvfNameOffset)
            fvfName = fileReader.readString()
            
            self.textures.append(BMDLMaterial.MaterialTexture(fvfTypeName, fvfName, fvfTypeHash, fvfHash))
            
        for i in range(fvfCount):
            self.seekToSection(fileReader, fvfStart + (i*16))
            fvfTypeNameOffset, fvfTypeHash, fvfNameOffset, fvfHash = fileReader.read("4I")
            
            self.seekToSection(fileReader, fvfTypeNameOffset)
            fvfTypeName = fileReader.readString()
            
            self.seekToSection(fileReader, fvfNameOffset)
            fvfName = fileReader.readString()
            
            self.fvf.append(BMDLMaterial.MaterialFVF(fvfTypeName, fvfName, fvfTypeHash, fvfHash))
        
        print()
        print("MATERIAL: %s     0x%x" % (self.name, self.hash))
        for prop in self.properties:
            print("\t" + str(prop))
        for fvf in self.fvf:
            print("\t" + str(fvf))
        for tex in self.textures:
            print("\t" + str(tex))
        
        
class BMDLHeader:
    def __init__(self):
        self.modelVersion = 0
        self.modelMagic = 0
        self.modelSubVersion = 0
        self.dataStart = 0
        self.dataSize = 0
        self.modelType = 0
        self.modelNull = 0
        self.headerCount = 0
        
    def read(self, fileReader):
        self.modelVersion = fileReader.readUInt()
        self.modelMagic = fileReader.readUInt()
        self.modelSubVersion = fileReader.readUInt()
        self.dataStart = fileReader.readUInt()
        self.dataSize = fileReader.readUInt()
        self.modelType = fileReader.readUInt()
        self.modelNull = fileReader.readUInt()
        self.headerCount = fileReader.readUInt()
        

class BMDLImporter:
    def __init__(self):
        self.header = BMDLHeader()
        self.sceneHash = 0
        self.sceneName = None
        self.materials = []
        self.buffers = []

    def read(self, fileReader):
        self.header.read(fileReader)
        
        if self.header.modelType == 4:
            matGroupStart, matCount, bufferCount, fvfCount = self.readStart04(fileReader)
            offset = 0x34
        elif self.header.modelType == 16:
            matGroupStart, matCount, bufferCount, fvfCount = self.readStart16(fileReader)
            offset = 0x3C
            
        for i in range(matCount):
            fileReader.seek(offset)
            matOffsets = fileReader.read("5i")
            # Remember this position so we can keep reading information
            offset = fileReader.tell()
            
            material = BMDLMaterial(self)
            material.read(fileReader, matOffsets)
            self.materials.append(material)
        
        fileReader.seek(offset)
        fvfOffsets = []
        for i in range(fvfCount):
            fvfOffsets.append(fileReader.read("4i"))
            
        # Remember this position so we can keep reading information
        offset = fileReader.tell()
        
        for i in range(bufferCount):
            fileReader.seek(offset)
            bufferInfoOffset = fileReader.readInt()
            # Remember this position so we can keep reading information
            offset = fileReader.tell()
            
            self.seekToSection(fileReader, matGroupStart + (0x2C * i))
            # Probably bounding box?
            unkFloats = fileReader.read("8f")
            vertBuffIndex, matGroupCount, bufferInfo = fileReader.read("3i")
            
            buffer = BMDLBuffers(self)
            buffer.readFVF(fileReader, fvfOffsets[i])
            buffer.readBuffer(fileReader, [vertBuffIndex, matGroupCount, bufferInfo])
            
            self.buffers.append(buffer)
        
    def seekToSection(self, fileReader, offset):
        fileReader.seek(self.header.dataStart + offset)
            
    def readStart04(self, fileReader):
        offsets = fileReader.read("5i")
        
        self.seekToSection(fileReader, offsets[0])
        
        self.seekToSection(fileReader, offsets[1])
        scenenameOffset = fileReader.readInt()
        sceneHash = fileReader.readUInt()
        matCount = fileReader.readInt()
        
        print("scenenameOffset: 0x%x" % scenenameOffset)
        print("sceneHash: 0x%x" % sceneHash)
        print("matCount: 0x%x" % matCount)
        
        self.seekToSection(fileReader, offsets[2])
        matStart = fileReader.readInt()
        fvfCount = fileReader.readInt()
        
        print("matStart: 0x%x" % matStart)
        print("fvfCount: 0x%x" % fvfCount)
        
        self.seekToSection(fileReader, offsets[3])
        floatStart = fileReader.readInt()
        bufferCount = fileReader.readInt()
        
        print("floatStart: 0x%x" % floatStart)
        print("bufferCount: 0x%x" % bufferCount)
        
        self.seekToSection(fileReader, offsets[4])
        matGroupStart = fileReader.readInt()
        Null = fileReader.readInt()
        
        print("matGroupStart: 0x%x" % matGroupStart)
        print("Null: 0x%x" % Null)
        
        
        fileReader.seek(self.header.dataStart + scenenameOffset)
        self.sceneName = fileReader.readString()
        print(self.sceneName)
        
        return matGroupStart, matCount, bufferCount, fvfCount
    
    def readStart16(self, fileReader):
        offsets = fileReader.read("7i")
        
        self.seekToSection(fileReader, offsets[0])
        self.seekToSection(fileReader, offsets[1])  # boneInfoStart, boneFlag
        self.seekToSection(fileReader, offsets[2])
        
        self.seekToSection(fileReader, offsets[3])
        scenenameOffset = fileReader.readInt()
        sceneHash = fileReader.readUInt()
        matCount = fileReader.readInt()
        
        print("scenenameOffset: 0x%x" % scenenameOffset)
        print("sceneHash: 0x%x" % sceneHash)
        print("matCount: 0x%x" % matCount)
        
        self.seekToSection(fileReader, offsets[4])
        matStart = fileReader.readInt()
        fvfCount = fileReader.readInt()
        
        print("matStart: 0x%x" % matStart)
        print("fvfCount: 0x%x" % fvfCount)
        
        self.seekToSection(fileReader, offsets[5])
        floatStart = fileReader.readInt()
        bufferCount = fileReader.readInt()
        
        print("floatStart: 0x%x" % floatStart)
        print("bufferCount: 0x%x" % bufferCount)
        
        self.seekToSection(fileReader, offsets[6])
        matGroupStart = fileReader.readInt()
        Null = fileReader.readInt()
        
        print("matGroupStart: 0x%x" % matGroupStart)
        print("Null: 0x%x" % Null)
        
        
        fileReader.seek(self.header.dataStart + scenenameOffset)
        self.sceneName = fileReader.readString()
        print(self.sceneName)
        
        return matGroupStart, matCount, bufferCount, fvfCount
    
    def addTexture(self, bMaterial, texture, material):
        if texture is not None:
            slot = bMaterial.texture_slots.add()
            offset = material.getProperty("OffsetUV")
            if offset is not None:
                slot.offset.x = offset.value[0]
                slot.offset.y = offset.value[1]
            scale = material.getProperty("TileUV")
            if offset is not None:
                slot.scale.x = scale.value[0]
                slot.scale.y = scale.value[1]
                
            tex = bpy.data.textures.new(texture.name, type='IMAGE')
            slot.texture = tex
            slot.texture_coords = 'UV'
    
    def addMeshes(self):
        for buffer in self.buffers:
            bMesh = bpy.data.meshes.new(buffer.polyName)
            bObj = bpy.data.objects.new(buffer.polyName, bMesh)
            
            bpy.context.scene.objects.link(bObj)
            bpy.context.scene.objects.active = bObj
            
            # Add all vertices and triangles of the buffer
            
            bMesh.vertices.add(len(buffer.vertices))
            for i in range(len(buffer.vertices)):
                bMesh.vertices[i].co = buffer.vertices[i].pos
            
            print(len(buffer.triangles))
            bMesh.tessfaces.add(len(buffer.triangles))
            for i in range(len(buffer.triangles)):
                for j in range(3):
                    bMesh.tessfaces[i].vertices_raw[j] = buffer.triangles[i][j]
                    
            if buffer.vertices[0].uv is not None:
                uvtex = bMesh.tessface_uv_textures.new()
                uvtex.name = 'DefaultUV'
                for i, face in enumerate(bMesh.tessfaces):
                    uvtex.data[i].uv1 = buffer.vertices[face.vertices_raw[0]].uv
                    uvtex.data[i].uv2 = buffer.vertices[face.vertices_raw[1]].uv
                    uvtex.data[i].uv3 = buffer.vertices[face.vertices_raw[2]].uv
                    uvtex.data[i].uv4 = [0, 0]
                    
            # Set materials for the meshes
            
            for mesh in buffer.meshes:
                bMat = bpy.data.materials.new(mesh.material.name)
                bMesh.materials.append(bMat)
                
                material_index = len(bMesh.materials) - 1
                
                print(len(bMesh.tessfaces))
                print(mesh.triangleCount)
                print(mesh.firstTriangle)
                for i in range(mesh.triangleCount):
                    bMesh.tessfaces[i + mesh.firstTriangle].material_index = material_index
                    
                for texture in mesh.material.textures:
                    self.addTexture(bMat, texture, mesh.material)
                    
            # Vertex colors go the lats because they must be done after updating the mesh
                    
            bMesh.update()
            
            if buffer.vertices[0].color is not None:
                colorLayer = bMesh.vertex_colors.new("Col")

                for t in range(len(buffer.triangles)):
                    for i in range(3):
                        colorLayer.data[t*3 + i].color = BMDLVertex.decodeColor(buffer.vertices[buffer.triangles[t][i]].color)
            
            
            # Finish

            bMesh.update()

def importBMDL(file):
    fileReader = FileReader(file)
    
    importer = BMDLImporter()
    importer.read(fileReader)
    
    #importer.addMeshes()

    return {'FINISHED'}


if __name__ == "__main__":
#     debugFile = open("E:\\Eric\\SporeModder\\Projects\\BMDL_environments\\creatureEditor\\creatureeditor_background.bmdl", "br")
    debugFile = open("E:\\Eric\\SporeModder\\Projects\\BMDL_environments\\#3406158D\\citadel_lvl1_terrainb.bmdl", "br")

    try:
        importBMDL(debugFile)
    finally:
        debugFile.close()
        