bl_info = {
    "name": "RenderWare importer/exporter for GTA III/VC/SA (.dff)",
    "author": "Ago Allikmaa (maxorator), Pedro Luis Valadés Viera (PerikiyoXD)",
    "version": (0, 10, 0),
    "blender": (2, 6, 3),
    "location": "File > Import-Export > Renderware (.dff) ",
    "description": "RenderWare importer/exporter for GTA III/VC/SA",
    "category": "Learnbgame",
    }

import struct
import os
import time
import zlib
import base64
import bpy
import math
import mathutils
from collections import deque
from bpy.props import *

class RwTypes():
    ANY = -1
    
    STRUCT = 0x0001
    STRING = 0x0002
    EXTENSION = 0x0003
    TEXTURE = 0x0006
    MATERIAL = 0x0007
    MATERIALLIST = 0x0008
    FRAMELIST = 0x000E
    GEOMETRY = 0x000F
    CLUMP = 0x0010
    ATOMIC = 0x0014
    GEOMETRYLIST = 0x001A
    RENDERRIGHTS = 0x001F
    
    MORPHPLG = 0x0105
    SKINPLG = 0x116
    HANIMPLG = 0x11E
    MATEFFECTS = 0x0120
    BINMESHPLG = 0x050E
    FRAMENAME = 0x253F2FE
    COLLISION = 0x253F2FA
    MATSPECULAR = 0x253F2F6
    NIGHTCOLS = 0x253F2F9
    MATREFLECTION = 0x253F2FC
    MESHEXTENSION = 0x253F2FD
    
    def decodeVersion(version):
        if (version & 0xFFFF0000) == 0:
            print("Version: "+str(hex(version << 8)))
            return version << 8
        else:
            p1 = ((version >> 14) & 0x3FF00) + 0x30000
            p2 = (version >> 16) & 0x3F
            
            print("Version: "+str(hex(p1 | p2)))
            return p1 | p2

class RpGeomFlag:
    TRISTRIP = 0x0001
    POSITIONS = 0x0002
    TEXTURED = 0x0004
    PRELIT = 0x0008
    NORMALS = 0x0010
    LIGHT = 0x0020
    MODULATEMATERIALCOLOR = 0x0040
    TEXTURED2 = 0x0080

class ImportRenderware:
    class RwTriangle:
        def __init__(self, verts, mat):
            self.verts = verts
            self.mat = mat
            
        def desc(self):
            return (self.verts[0], self.verts[1], self.verts[2])
            
    class RwVertex:
        def __init__(self, coords, normal):
            self.coords = coords
            self.normal = normal
            self.uv = None
            self.uv_env = None
            
        def desc(self):
            return (self.coords[0], self.coords[1], self.coords[2])
    
    class RwFrame:
        def __init__(self, loader, index, rot, pos, parent):
            self.loader = loader
            self.index = index
            
            self.geometry = None
            self.atomic = None
            
            self.blobj = None
            self.bldata = None
            
            self.hanimdata = None
            
            self.name = None
            
            rmatrix = mathutils.Matrix.Identity(3)
            rmatrix[0] = rot[0], rot[1], rot[2]
            rmatrix[1] = rot[3], rot[4], rot[5]
            rmatrix[2] = rot[6], rot[7], rot[8]
            rmatrix.resize_4x4()
            rmatrix.translation = pos[0], pos[1], pos[2]
            
            self.matrix = rmatrix
            
            self.parent = parent
            
            self.loader.childrenOf[parent+1].append(self.index)
            
        def setAtomic(self, atomic):
            self.atomic = atomic
            self.geometry = atomic.geometry
            
        def build(self):
            if self.name is None:
                self.name = "noname_" + str(self.index);
                
            if self.geometry:
                self.bldata = self.geometry.build(self.name)
            
            self.blobj = bpy.data.objects.new(self.name, self.bldata)
            
            if self.parent >= 0:
                self.blobj.parent = self.loader.frames[self.parent].blobj
                self.blobj.matrix_local = self.matrix
            
            bpy.context.scene.objects.link(self.blobj)
            
            for frame in self.loader.childrenOf[self.index+1]:
                self.loader.frames[frame].build()
            
            if "_vlo" in self.name or "_dam" in self.name:
                self.blobj.hide = True
                self.blobj.hide_render = True
                
            if self.loader.colhex and self.index == self.loader.childrenOf[0][0]:
                textobj = bpy.data.texts.new(name = ("zrwcoll_" + self.name))
                textobj.from_string(self.loader.colhex)
                
                self.blobj.collhex = textobj.name
                
            if self.hanimdata:
                textobj = bpy.data.texts.new(name = ("zrwhanim" + str(self.index) + "_" + self.name))
                textobj.from_string(self.hanimdata)
                
                self.blobj.rw_hanimdata = textobj.name
                
            if self.geometry and self.geometry.skindata:
                textobj = bpy.data.texts.new(name = ("zrwskin_" + self.name))
                textobj.from_string(self.geometry.skindata)
                
                self.blobj.rw_skindata = textobj.name
            
            if self.atomic and self.atomic.renderPlugin != None and self.atomic.renderExtra != None:
                self.blobj.renderright = self.atomic.renderPlugin
                self.blobj.renderextra = self.atomic.renderExtra
                
            if self.atomic and self.atomic.matfxpipe:
                self.blobj.matfxpipe = True
                
    class RpGeometry:
        def __init__(self, loader, index):
            self.loader = loader
            self.index = index  
            self.vertices = []
            self.triangles = []
            self.materials = []
            self.mesh = None
            self.atomic = None
            self.skindata = None
            self.hasEnvUV = False
            self.vertCol = None
            self.nightVertCol = None
            self.hasNormals = False
            
        def setAtomic(self, atomic):
            self.atomic = atomic
            
        def addMaterial(self, material):
            material.setIndex(len(self.materials))
            self.materials.append(material)
            
        def addVertex(self, vertex):
            self.vertices.append(vertex)
            
        def addTriangle(self, triangle):
            self.triangles.append(triangle)
            
        def build(self, name):
            self.mesh = bpy.data.meshes.new(name)
            
            pyverts = []
            pypolys = []
            
            for vertex in self.vertices:
                pyverts.append(vertex.desc())
                
            for triangle in self.triangles:
                pypolys.append(triangle.desc())
            
            self.mesh.from_pydata(pyverts, [], pypolys)
            self.mesh.update()
            
            if self.vertCol:
                vcol = self.mesh.vertex_colors.new("Normal")
                self.mesh.vertex_colors.active = vcol
                
                for i in range(len(self.vertices)):
                    vcol.data[i].color = (self.vertCol[i][0], self.vertCol[i][1], self.vertCol[i][2])
                    
            if self.nightVertCol:
                nvcol = self.mesh.vertex_colors.new("Night")
                self.mesh.vertex_colors.active = nvcol
                
                for i in range(len(self.vertices)):
                    nvcol.data[i].color = (self.nightVertCol[i][0], self.nightVertCol[i][1], self.nightVertCol[i][2])
            
            uvtexture = self.mesh.uv_textures.new()
            uvtexture.name = "MainUV"
            
            uvlayer = self.mesh.uv_layers[-1]
            
            for i in range(len(self.triangles)):
                for j in range(3):
                    uvlayer.data[3*i + j].uv = self.vertices[self.triangles[i].verts[j]].uv
            
            if self.hasEnvUV:
                euvtexture = self.mesh.uv_textures.new()
                euvtexture.name = "EnvUV"
                
                euvlayer = self.mesh.uv_layers[-1]
                
                for i in range(len(self.triangles)):
                    for j in range(3):
                        euvlayer.data[3*i + j].uv = self.vertices[self.triangles[i].verts[j]].uv_env
                    
            for material in self.materials:
                material.build()
                
            for i in range(len(self.triangles)):
                self.mesh.polygons[i].material_index = self.triangles[i].mat
            
            return self.mesh
        
    class RpMaterial:
        def __init__(self, geometry, flags=None, col=None, textured=None, ambient=None, specular=None, diffuse=None):
            self.index = None
            self.name = "g" + str(geometry.index) + "m"
            self.geometry = geometry
            self.flags = flags
            self.col = col
            self.ambient = ambient
            self.specular = specular
            self.diffuse = diffuse
            self.textured = textured
            self.texture = None
            self.blmat = None
            
            self.envtex = None
            self.readenvmap = False
            self.envIntensity = 1
            
            self.reflectColour = None
            self.reflectIntensity = None
            
            self.spectex = None
            
        def setIndex(self, index):
            self.index = index
            self.name = "g" + str(self.geometry.index) + "m" + str(index)
            
        def setTexture(self, texture):
            self.texture = texture
            
        def setEnvTexture(self, texture):
            self.envtex = texture
            
        def setSpecTexture(self, texture):
            self.spectex = texture
            
        def setReflection(self, colour, intensity):
            self.reflectColour = colour
            self.reflectIntensity = intensity
            
        def build(self):
        
            #Be careful, sometimes materials dont have textures!
            #On this cases, we'll let the material generate it's name.
        
            if (self.texture is None):
                self.name = "notextured_" + str(self.col[0]) + "." + str(self.col[1]) + "." + str(self.col[2]) + "." + str(self.col[3])
            else:
                #We set material's name to the texture name.
                self.name = self.texture.name
                
            #First, we search for the material, to see if we already have this material imported.
            
            lookupMaterial = bpy.data.materials.find(self.name)
            if lookupMaterial != -1:
                self.blmat = bpy.data.materials[lookupMaterial]
                print("Material: Skipping material \""+self.name+"\"")
            else:
                print("Material: Building material \""+self.name+"\"")
                self.blmat = bpy.data.materials.new(self.name)
                self.blmat.diffuse_color = (self.col[0]/255, self.col[1]/255, self.col[2]/255)
                self.blmat.diffuse_intensity = self.diffuse
                self.blmat.ambient = self.ambient
                self.blmat.specular_intensity = self.specular
                
                if self.geometry.vertCol:
                    self.blmat.use_vertex_color_light = True
                
                if self.col[3] < 255:
                    self.blmat.use_transparency = True
                    self.blmat.alpha = self.col[3]/255
                
                if self.envtex:
                    self.envtex.build()
                
                if self.spectex:
                    self.spectex.build()
                
                if self.texture:
                    self.texture.build()
                    self.blmat.active_texture_index = 0
                    
                if self.reflectColour and self.reflectIntensity:
                    self.blmat.mirror_color = self.reflectColour
                    self.blmat.raytrace_mirror.use = True
                    self.blmat.raytrace_mirror.reflect_factor = self.reflectIntensity
            
            self.geometry.mesh.materials.append(self.blmat)
            
    class RwTexture:
        def __init__(self, loader, material, name, texType, intensity=1):
            self.material = material
            self.bltex = None
            self.bltexslot = None
            self.name = name
            self.loader = loader
            self.texType = texType
            self.intensity = intensity
        
        def build(self):
            if self.texType == 1 and self.name in self.loader.envtexpool:
                self.bltex = self.loader.envtexpool[self.name]
            elif self.texType != 1 and self.name in self.loader.texpool:
                self.bltex = self.loader.texpool[self.name]
            else:
                if self.texType == 1:
                    self.bltex = bpy.data.textures.new(self.name, "ENVIRONMENT_MAP")
                    self.bltex.__class__ = bpy.types.EnvironmentMapTexture
                    self.bltex.environment_map.source = "IMAGE_FILE"
                    self.loader.envtexpool[self.name] = self.bltex
                else:
                    self.bltex = bpy.data.textures.new(self.name, "IMAGE")
                    self.bltex.__class__ = bpy.types.ImageTexture
                    self.loader.texpool[self.name] = self.bltex
                    

                print("Texture: Searching texture for material "+self.material.name+" (\"" + os.path.normcase(os.path.dirname(self.loader.filename) + "/" + self.name + ".png") + "\")")                   
                    
                #print(self.loader.filename)    
                    
                imgfile = os.path.normcase(os.path.dirname(self.loader.filename) + "/" + self.name + ".png")
                
                if os.path.isfile(imgfile):
                    self.bltex.image = bpy.data.images.load(imgfile)
            
            self.bltexslot = self.material.blmat.texture_slots.create(self.texType)
            self.bltexslot.texture_coords = "UV"
            self.bltexslot.texture = self.bltex
            
            if (self.texType == 1 or self.texType == 2) and self.material.geometry.hasEnvUV:
                self.bltexslot.uv_layer = "EnvUV"
            else:
                self.bltexslot.uv_layer = "MainUV"
            
            if self.texType == 1:
                self.bltexslot.diffuse_factor = self.intensity
            elif self.texType == 2:
                self.bltexslot.use_map_diffuse = False
                self.bltexslot.use_map_color_diffuse = False
                self.bltexslot.use_map_color_spec = True
                self.bltexslot.specular_color_factor = self.intensity
                
    class RpAtomic:
        def __init__(self, loader, frame, geometry, flags):
            self.loader = loader
            self.frame = frame
            self.geometry = geometry
            self.flags = flags
            
            self.renderPlugin = None
            self.renderExtra = None
            
            self.matfxpipe = False
            
            frame.setAtomic(self)
            geometry.setAtomic(self)
            
        def setRenderRights(self, plugin, extra):
            self.renderPlugin = plugin
            self.renderExtra = extra
    
    def __init__(self, filename):
        print("========== ImportRenderware: importing ==========")
        self.filename = filename
        self.texpool = {}
        self.envtexpool = {}
        
        print("Loading filename " + self.filename)
        
        
        self.colhex = None
        
        self.childrenOf = None
        self.frames = []
        self.geoms = []
        
        self.f = open(filename, "rb")
        self.readSection(RwTypes.CLUMP)
        self.f.close()
        
        for frame in self.childrenOf[0]:
            self.frames[frame].build()
            
    def writeDebug(self, text):
        g = open(self.filename + ".txt", "a")
        g.write(text + "\n")
        g.close()
        
    def readFormat(self, format):
        return struct.unpack(format, self.f.read(struct.calcsize(format)))
    
    def readSlice(self, format, slice):
        size = struct.calcsize(format)
        
        if(len(slice) < size):
            raise Exception("Failed to read slice, buffer is too small.")
        
        return struct.unpack(format, slice[:size]), slice[size:]
        
    def readSection(self, type, extra = None):
        header = self.readFormat("III")
        header = (header[0], header[1], RwTypes.decodeVersion(header[2]))
                
        if type >= 0 and header[0] != type:
            raise Exception("Expected type " + str(type) + ", found " + str(header[0]))
            
        curPos = self.f.tell()
        
        res = None
            
        if header[0] == RwTypes.STRUCT: res = self.readSectionStruct(header)
        elif header[0] == RwTypes.STRING: res = self.readSectionString(header)
        elif header[0] == RwTypes.EXTENSION: res = self.readSectionExtension(header, extra)
        elif header[0] == RwTypes.TEXTURE: res = self.readSectionTexture(header, extra)
        elif header[0] == RwTypes.MATERIAL: res = self.readSectionMaterial(header, extra)
        elif header[0] == RwTypes.MATERIALLIST: res = self.readSectionMaterialList(header, extra)
        elif header[0] == RwTypes.FRAMELIST: res = self.readSectionFrameList(header)
        elif header[0] == RwTypes.GEOMETRY: res = self.readSectionGeometry(header, extra)
        elif header[0] == RwTypes.CLUMP: res = self.readSectionClump(header)
        elif header[0] == RwTypes.ATOMIC: res = self.readSectionAtomic(header)
        elif header[0] == RwTypes.GEOMETRYLIST: res = self.readSectionGeometryList(header)
        elif header[0] == RwTypes.MORPHPLG: res = self.readSectionMorphPLG(header, extra)
        elif header[0] == RwTypes.BINMESHPLG: res = self.readSectionBinMeshPLG(header, extra)
        elif header[0] == RwTypes.FRAMENAME: res = self.readSectionFrameName(header, extra)
        elif header[0] == RwTypes.COLLISION: res = self.readSectionCollision(header, extra)
        elif header[0] == RwTypes.MATEFFECTS: res = self.readSectionMatEffects(header, extra)
        elif header[0] == RwTypes.MATSPECULAR: res = self.readSectionMatSpecular(header, extra)
        elif header[0] == RwTypes.MATREFLECTION: res = self.readSectionMatReflection(header, extra)
        elif header[0] == RwTypes.MESHEXTENSION: res = self.readSectionMeshExtension(header, extra)
        elif header[0] == RwTypes.RENDERRIGHTS: res = self.readSectionRenderRights(header, extra)
        elif header[0] == RwTypes.HANIMPLG: res = self.readSectionHAnimPLG(header, extra)
        elif header[0] == RwTypes.SKINPLG: res = self.readSectionSkinPLG(header, extra)
        elif header[0] == RwTypes.NIGHTCOLS: res = self.readSectionNightCols(header, extra)
        elif type >= 0: raise Exception("Missing read function for section type " + str(type))
        else: print("Ignoring extension data of type " + hex(header[0]))
        
        self.f.seek(curPos + header[1])
        
        return res
        
    def readSectionStruct(self, header):
        return header, self.f.read(header[1])
        
    def readSectionString(self, header):
        byteList = b""
        
        for i in range(header[1]):
            newByte = self.f.read(1)
            if newByte[0] == 0:
                break
            
            byteList += newByte
            
        return header, byteList.decode("ascii")
    
    def readSectionExtension(self, header, extra):
        endPos = self.f.tell() + header[1]
        
        while self.f.tell() < endPos:
            self.readSection(RwTypes.ANY, extra)
            
        return header, None
    
    def readSectionTexture(self, header, material):
        metaHeader, slice = self.readSection(RwTypes.STRUCT)
        (flags, x), slice = self.readSlice("HH", slice)
        
        x, texName = self.readSection(RwTypes.STRING)
        x, alphaName = self.readSection(RwTypes.STRING)
        
        if material.readenvmap:
            texture = self.RwTexture(self, material, texName, 1, material.envIntensity)
            material.setEnvTexture(texture)
        else:
            texture = self.RwTexture(self, material, texName, 0, 1)
            material.setTexture(texture)
        
        self.readSection(RwTypes.EXTENSION)
        
        return header, None
        
    def readSectionMaterial(self, header, geometry):
        metaHeader, slice = self.readSection(RwTypes.STRUCT)
        (flags,), slice = self.readSlice("I", slice)
        col, slice = self.readSlice("BBBB", slice)
        (x, textured, ambient, specular, diffuse), slice = self.readSlice("iifff", slice)
        
        material = self.RpMaterial(geometry, flags, col, textured, ambient, specular, diffuse)
        geometry.addMaterial(material)
        
        if textured > 0:
            self.readSection(RwTypes.TEXTURE, material)
            
        self.readSection(RwTypes.EXTENSION, material)
        
        return header, None
        
    def readSectionMaterialList(self, header, geometry):
        metaHeader, slice = self.readSection(RwTypes.STRUCT)
        (matCount,), slice = self.readSlice("i", slice)
        
        for i in range(matCount):
            junk, slice = self.readSlice("i", slice)
            
        for i in range(matCount):
            self.readSection(RwTypes.MATERIAL, geometry)
            
        return header, None
    
    def readSectionFrameList(self, header):
        metaHeader, slice = self.readSection(RwTypes.STRUCT)
        (frameCount,), slice = self.readSlice("i", slice)
        
        self.childrenOf = []
        
        for i in range(frameCount+1):
            self.childrenOf.append([])
        
        for i in range(frameCount):
            rot, slice = self.readSlice("fffffffff", slice)
            pos, slice = self.readSlice("fff", slice)
            (parent, flags), slice = self.readSlice("ii", slice)
            
            self.frames.append(self.RwFrame(self, i, rot, pos, parent))
        
        for i in range(frameCount):
            self.readSection(RwTypes.EXTENSION, self.frames[i])
            
        return header, None
    
    def readSectionGeometry(self, header, index):
        metaHeader, slice = self.readSection(RwTypes.STRUCT)
        (flags, texCount, triCount, vertCount, morphCount), slice = self.readSlice("HHiii", slice)
        
        geometry = self.RpGeometry(self, index)
        self.geoms.append(geometry)
        
        geometry.flags = flags
        
        if metaHeader[2] < 0x34001:
            (surfAmbient, surfSpecular, surfDiffuse), slice = self.readSlice("fff", slice)
        
        for i in range(vertCount):
            geometry.addVertex(self.RwVertex(None, None))
            
        if flags & RpGeomFlag.PRELIT:
            geometry.vertCol = []
            
            for i in range(vertCount):
                (vcr, vcg, vcb, vca), slice = self.readSlice("BBBB", slice)
                
                geometry.vertCol.append((vcr / 255, vcg / 255, vcb / 255))
            
        for i in range(vertCount):
            uv, slice = self.readSlice("ff", slice)
            geometry.vertices[i].uv = (uv[0], 1-uv[1])
            
        if texCount > 1:
            geometry.hasEnvUV = True
            
            for i in range(vertCount):
                uv_env, slice = self.readSlice("ff", slice)
                geometry.vertices[i].uv_env = (uv_env[0], 1-uv_env[1])
            
        if texCount > 2:
            slice = slice[struct.calcsize("ff")*(texCount-2)*(vertCount):]
            
        for i in range(triCount):
            (c, b, mat, a), slice = self.readSlice("HHHH", slice)
            
            if a >= vertCount or b >= vertCount or c >= vertCount:
                raise Exception("Vertex indices out of range for triangle.")
            
            geometry.addTriangle(self.RwTriangle((a, b, c), mat))
            
        if morphCount is not 1:
            raise Exception("Multiple frames not supported")
        
        for i in range(morphCount):
            (bx, by, bz, br, hasVerts, hasNormals), slice = self.readSlice("ffffii", slice)
            
            if hasVerts > 0:
                for j in range(vertCount):
                    coords, slice = self.readSlice("fff", slice)
                    geometry.vertices[j].coords = coords
            
            if hasNormals > 0:
                geometry.hasNormals = True
                
                for j in range(vertCount):
                    normal, slice = self.readSlice("fff", slice)
                    
                    geometry.vertices[j].normal = normal
        
        self.readSection(RwTypes.MATERIALLIST, geometry)
        self.readSection(RwTypes.EXTENSION, geometry)
        
        return header, None
    
    def readSectionClump(self, header):
        metaHeader, slice = self.readSection(RwTypes.STRUCT)
        (atomicCount,), slice = self.readSlice("i", slice)
        
        print("header output: ["+str(hex(header[0]))+"]["+str(hex(header[1]))+"]["+str(hex(header[2]))+"]")
        
        smth = str(hex(header[2]))
        
        version = str(smth[2])+"."+str(smth[3])+"."+str(smth[4])+"."+str(smth[5])
               
        print("Reporting RenderWare version: " + version + " ("+smth+")" )
        
        if metaHeader[2] > 0x33000:
            (lightCount, cameraCount), slice = self.readSlice("ii", slice)
        
        self.readSection(RwTypes.FRAMELIST)
        self.readSection(RwTypes.GEOMETRYLIST)
        
        for i in range(atomicCount):
            self.readSection(RwTypes.ATOMIC)
            
        self.readSection(RwTypes.EXTENSION)
        
        return header, None
        
    def readSectionAtomic(self, header):
        metaHeader, slice = self.readSection(RwTypes.STRUCT)
        (frameIndex, geomIndex, flags, x, x, x, x), slice = self.readSlice("iiBBBBi", slice)
        
        atomic = self.RpAtomic(self, self.frames[frameIndex], self.geoms[geomIndex], flags)
        
        self.readSection(RwTypes.EXTENSION, atomic)
        
        return header, None
    
    def readSectionGeometryList(self, header):
        metaHeader, slice = self.readSection(RwTypes.STRUCT)
        (geomCount,), slice = self.readSlice("i", slice)
        
        for i in range(geomCount):
            self.readSection(RwTypes.GEOMETRY, i)
    
    def readSectionMorphPLG(self, header, geometry):
        return header, None
    
    def readSectionBinMeshPLG(self, header, geometry):
        slice = self.f.read(header[1])
        
        (type, splits, total), slice = self.readSlice("iii", slice)
        
        if type != 0 and type != 1:
            print("Morph PLG section in unknown type - ignoring.")
            return header, None
        
        lookup = {}
        
        for i in range(len(geometry.triangles)):
            v = geometry.triangles[i].verts
            v = list(v)
            v.sort()
            
            lookup[tuple(v)] = i
            
        totals = 0
        
        for i in range(splits):
            (sub, mat), slice = self.readSlice("ii", slice)
            
            if type == 0:
                for j in range(sub//3):
                    vx, slice = self.readSlice("iii", slice)
                    vx = list(vx)
                    vx.sort()
                    vx = tuple(vx)
                    
                    if vx in lookup:
                        geometry.triangles[lookup[vx]].mat = mat
            else:
                elems = deque()
                
                for j in range(sub):
                    if len(elems) > 2:
                        elems.popleft()
                    
                    (item,), slice = self.readSlice("i", slice)
                    
                    if len(elems) > 1:
                        checklist = [elems[0], elems[1], item]
                        checklist.sort()
                        check = tuple(checklist)
                        
                        if check in lookup:
                            geometry.triangles[lookup[check]].mat = mat
                            
                    elems.append(item)
                    
        return header, None
    
    def readSectionFrameName(self, header, frame):
        frame.name = self.f.read(header[1]).decode("ascii")
        
        return header, None
    
    def readSectionCollision(self, header, geometry):
        if not self.childrenOf or len(self.childrenOf[0]) is 0:
            print("Collision extension - no frame to attach to.")
            return header, None
        
        binary = self.f.read(header[1])
            
        self.colhex = base64.b64encode(zlib.compress(binary)).decode("ascii")
        
        return header, None
    
    def readSectionMatEffects(self, header, parent):
        if parent.__class__ == self.RpMaterial:
            return self.readSectionMaterialMatEffects(header, parent)
        elif parent.__class__ == self.RpAtomic:
            return self.readSectionAtomicMatEffects(header, parent)
        
        return header, None
    
    def readSectionMaterialMatEffects(self, header, material):
        (flags,) = self.readFormat("I")
        
        for i in range(2):
            (effectType,) = self.readFormat("I")
            
            if effectType == 0:
                continue
            elif effectType != 2:
                print("Unknown material effect type.")
                return header, None
            
            (coefficient, frameBufferAlpha, textured) = self.readFormat("fii")
            
            if textured:
                material.readenvmap = True
                material.envIntensity = coefficient
                
                self.readSection(RwTypes.TEXTURE, material)
        
    def readSectionAtomicMatEffects(self, header, atomic):
        (check,) = self.readFormat("i")
        
        if check != 0:
            atomic.matfxpipe = True
        
        return header, None
    
    def readSectionMatSpecular(self, header, material):
        slice = self.f.read(header[1])
        
        (intensity,), slice = self.readSlice("f", slice)
        
        specName = ""
        
        for i in range(len(slice)):
            if int(slice[i]) == 0:
                break
            
            specName += slice[i:i+1].decode("ascii")
            
        texture = self.RwTexture(self, material, specName, 2, intensity)
        material.setSpecTexture(texture)
        
        return header, None
        
    def readSectionMatReflection(self, header, material):
        slice = self.f.read(header[1])
        
        colour, slice = self.readSlice("fff", slice)
        (x, intensity), slice = self.readSlice("ff", slice)
        
        material.setReflection(colour, intensity)
        
        return header, None
        
    def readSectionMeshExtension(self, header, geometry):
        slice = self.f.read(header[1])
        
        (hasData,), slice = self.readSlice("i", slice)
        
        if hasData:
            print("Mesh extension extension actually has data. Not sure what to do with it.")
            
        return header, None
    
    def readSectionRenderRights(self, header, atomic):
        if not hasattr(atomic, "__class__") or atomic.__class__ != self.RpAtomic:
            print("Render rights extension is not in the right section, should be in atomic.")
            return
            
        slice = self.f.read(header[1])
        (plugin, extra), slice = self.readSlice("ii", slice)
        
        atomic.setRenderRights(plugin, extra)
        
    def readSectionHAnimPLG(self, header, frame):
        if not hasattr(frame, "__class__") or frame.__class__ != self.RwFrame:
            print("HAnim extension is not in the right section, should be in frame.")
            return
        
        binary = self.f.read(header[1])
        
        frame.hanimdata = base64.b64encode(zlib.compress(binary)).decode("ascii")
        
        return header, None
    
    def readSectionSkinPLG(self, header, geometry):
        if not hasattr(geometry, "__class__") or geometry.__class__ != self.RpGeometry:
            print("Skin extension is not in the right section, should be in geometry.")
            return
        
        binary = self.f.read(header[1])
        
        geometry.skindata = base64.b64encode(zlib.compress(binary)).decode("ascii")
        
        return header, None
        
    def readSectionNightCols(self, header, geometry):
        if not hasattr(geometry, "__class__") or geometry.__class__ != self.RpGeometry:
            print("Night vertex colours extension is not in the right section, should be in geometry.")
            return
            
        slice = self.f.read(header[1])
        (x,), slice = self.readSlice("I", slice)
        
        geometry.nightVertCol = []
        
        for i in range(len(geometry.vertices)):
            (vcr, vcg, vcb, vca), slice = self.readSlice("BBBB", slice)
            
            geometry.nightVertCol.append((vcr / 255, vcg / 255, vcb / 255))
        
        return header, None

class ExportRenderware:
    class RwChunkHeader:
        def __init__(self, type, size):
            self.type = type
            self.size = size
            
        def bin(self):
            return struct.pack("III", self.type, self.size, ExportRenderware.targetVer)
        
    class RwVector3:
        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z
            
        def bin(self):
            return struct.pack("fff", self.x, self.y, self.z)
            
    class RwRotMatrix:
        def __init__(self):
            self.m = [1, 0, 0, 0, 1, 0, 0, 0, 1]
            
        def bin(self):
            return struct.pack("9f", *self.m)

    class RwFrameList:
        def __init__(self):
            self.R = ExportRenderware
            
            self.frames = []
            
        def bin(self):
            payload = struct.pack("i", len(self.frames))
            
            for frame in self.frames:
                payload += frame.binraw()
                
            payload = self.R.RwChunkHeader(RwTypes.STRUCT, len(payload)).bin() + payload
                
            for frame in self.frames:
                payload += frame.binext()
            
            header = self.R.RwChunkHeader(RwTypes.FRAMELIST, len(payload)).bin()
            
            return header + payload

    class RwFrame:
        def __init__(self, clump, object, parentFrame):
            self.R = ExportRenderware
            
            self.clump = clump
            self.object = object
            
            self.index = len(clump.frameList.frames)
            clump.frameList.frames.append(self)
            
            self.name = self.object.name
            self.parent = parentFrame
            
            self.rotation = self.R.RwRotMatrix()
            self.position = self.R.RwVector3(0, 0, 0)
            
            if parentFrame is not None:
                ux = object.matrix_local.to_3x3()
                self.rotation.m = [ux[0][0], ux[0][1], ux[0][2], ux[1][0], ux[1][1], ux[1][2], ux[2][0], ux[2][1], ux[2][2]]
                self.position.x = object.matrix_local.translation[0]
                self.position.y = object.matrix_local.translation[1]
                self.position.z = object.matrix_local.translation[2]
            
            if str(object.type) == "MESH":
                self.atomic = self.R.RpAtomic(self)
            elif str(object.type) == "EMPTY":
                self.atomic = None
            else:
                raise Exception("Unsupported object type selected: " + str(object.type))
                
            for child in self.object.children:
                if str(object.type) != "MESH" and str(object.type) != "EMPTY":
                    print("Ignoring object " + object.name + ", type " + object.type)
                    continue
                
                self.R.RwFrame(self.clump, child, self)
                
            if not clump.colbin:
                try:
                    if len(object.collhex) > 0:
                        textf = bpy.data.texts[object.collhex].as_string()
                        clump.colbin = zlib.decompress(base64.b64decode(bytes(textf, "ascii")))
                except:
                    clump.colbin = None
                
        def binraw(self):
            payload = self.rotation.bin()
            payload += self.position.bin()
            payload += struct.pack("ii", -1 if self.parent is None else self.parent.index, 0)
            
            return payload
            
        def binext_name(self):
            noname = "noname_"
            
            if self.name[:len(noname)] == noname:
                return b""
        
            writename = self.R.unmangleName(self.name)
            
            if len(writename) > 23:
                writename = writename[:23]
                print("Warning, frame name '", writename , "' truncated to 23 characters.")
        
            payload = struct.pack(str(len(writename)) + "s", bytearray(writename, "ascii"))
            header = self.R.RwChunkHeader(RwTypes.FRAMENAME, len(payload)).bin()
            
            return header + payload
            
        def binext_hanim(self):
            object = self.object
        
            try:
                if len(object.rw_hanimdata) > 0:
                    textf = bpy.data.texts[object.rw_hanimdata].as_string()
                    rawdata = zlib.decompress(base64.b64decode(bytes(textf, "ascii")))
                else:
                    return b""
            except:
                return b""
                
            payload = rawdata
            header = self.R.RwChunkHeader(RwTypes.HANIMPLG, len(payload)).bin()
            
            return header + payload
        
        def binext(self):
            payload = self.binext_name() + self.binext_hanim()
            header = self.R.RwChunkHeader(RwTypes.EXTENSION, len(payload)).bin()
            
            return header + payload
                
    class RpAtomicChunkInfo:
        def __init__(self, frameIndex, geometryIndex, flags):
            self.R = ExportRenderware
            
            self.frameIndex = frameIndex
            self.geometryIndex = geometryIndex
            self.flags = flags
            
        def bin(self):
            payload = struct.pack("iiii", self.frameIndex, self.geometryIndex, self.flags, 0)
            header = self.R.RwChunkHeader(RwTypes.STRUCT, len(payload)).bin()
            
            return header + payload
                
    class RpAtomic:
        def __init__(self, frame):
            self.R = ExportRenderware
            
            self.clump = frame.clump
            self.frame = frame
            self.mesh = frame.object.to_mesh(self.clump.context.scene, False, "PREVIEW")
            self.geometry = self.R.RpGeometry(self)
            self.flags = 5
            
        def binext_rights(self):
            if self.frame.object.renderright == 0:
                return b""
                
            payload = struct.pack("ii", self.frame.object.renderright, self.frame.object.renderextra)
            header = self.R.RwChunkHeader(RwTypes.RENDERRIGHTS, len(payload)).bin()
                
            return header + payload
            
        def binext_matfx(self):
            if self.frame.object.matfxpipe != True and self.R.decodedVer > 0x34003:
                return b""
        
            payload = struct.pack("i", 1)
            header = self.R.RwChunkHeader(RwTypes.MATEFFECTS, len(payload)).bin()
                
            return header + payload
            
        def bin(self):
            payload = self.R.RpAtomicChunkInfo(self.frame.index, self.geometry.index, self.flags).bin()
            
            extensions = self.binext_rights() + self.binext_matfx()
            extensions = self.R.RwChunkHeader(RwTypes.EXTENSION, len(extensions)).bin() + extensions
            
            payload += extensions
            
            header = self.R.RwChunkHeader(RwTypes.ATOMIC, len(payload)).bin()
            
            return header + payload

    class RpVertex:
        def __init__(self, pos, uv, uve, normal):
            self.pos = pos
            self.uv = uv
            self.uve = uve
            self.normal = normal

    class RpTriangle:
        def __init__(self, a, b, c, mat):
            self.a = a
            self.b = b
            self.c = c
            self.mat = mat
            
        def bin(self):
            return struct.pack("HHHH", self.a, self.b, self.mat, self.c)

    class RwUVCoord:
        def __init__(self, u, v):
            self.u = u
            self.v = v
        
        def bin(self):
            return struct.pack("ff", self.u, 1-self.v)
        
    class RwTexture:
        def __init__(self, material, bltexslot):
            self.R = ExportRenderware
            
            self.material = material
            self.bltexslot = bltexslot
            self.bltex = bltexslot.texture
            
        def bin(self):
            payload = struct.pack("HH", 0x1106, 0)
            
            payload = self.R.RwChunkHeader(RwTypes.STRUCT, len(payload)).bin() + payload
            
            strdata = struct.pack(str(len(self.bltex.name)) + "s", bytearray(self.bltex.name, "ascii"))
            
            for i in range(4 - (len(self.bltex.name)&3)):
                strdata += struct.pack("B", 0)
                
            payload += self.R.RwChunkHeader(RwTypes.STRING, len(strdata)).bin() + strdata
            
            strdata = struct.pack("i", 0)
            payload += self.R.RwChunkHeader(RwTypes.STRING, len(strdata)).bin() + strdata
                
            extensions = b""
            extensions = self.R.RwChunkHeader(RwTypes.EXTENSION, len(extensions)).bin() + extensions
            payload += extensions
            
            header = self.R.RwChunkHeader(RwTypes.TEXTURE, len(payload)).bin()
            
            return header + payload
        
    class RpMaterial:
        def __init__(self, materialList, blMaterial):
            self.R = ExportRenderware
            
            self.materialList = materialList
            
            self.index = len(materialList.mats)
            self.mesh = materialList.mesh
            self.blmaterial = blMaterial
            
            self.red = min(255, max(0, blMaterial.diffuse_color[0] * 256))
            self.green = min(255, max(0, blMaterial.diffuse_color[1] * 256))
            self.blue = min(255, max(0, blMaterial.diffuse_color[2] * 256))
            self.alpha = min(255, max(0, blMaterial.alpha * 256))
            
            self.ambient = blMaterial.ambient
            self.specular = blMaterial.specular_intensity
            self.diffuse = blMaterial.diffuse_intensity
            
            self.bltex_diffuse = self.findTexSlot("DIFFUSE")
            self.bltex_specular = self.findTexSlot("SPECULAR")
            self.bltex_envmap = self.findTexSlot("ENVMAP")
            
            self.tex_diffuse = None
            self.tex_envmap = None
            
            if self.bltex_diffuse:
                self.tex_diffuse = self.R.RwTexture(self, self.bltex_diffuse)
                
                if self.bltex_diffuse.texture_coords == "UV" and len(self.bltex_diffuse.uv_layer) > 0 and not self.materialList.geometry.uvname_diff:
                    self.materialList.geometry.uvname_diff = self.bltex_diffuse.uv_layer
                
            if self.bltex_envmap:
                self.tex_envmap = self.R.RwTexture(self, self.bltex_envmap)
                
                if self.bltex_envmap.texture_coords == "UV" and len(self.bltex_envmap.uv_layer) > 0 and not self.materialList.geometry.uvname_env:
                    self.materialList.geometry.uvname_env = self.bltex_envmap.uv_layer
                
        def findTexSlot(self, type):
            for i in range(len(self.blmaterial.texture_slots)):
                textype = ""
                slot = self.blmaterial.texture_slots[i]
            
                if slot and slot.texture:
                    if slot.texture.type == "ENVIRONMENT_MAP":
                        textype = "ENVMAP"
                    elif slot.use_map_color_spec and not slot.use_map_color_diffuse:
                        textype = "SPECULAR"
                    elif slot.use_map_color_diffuse and not slot.use_map_color_spec:
                        textype = "DIFFUSE"
                        
                if textype == type:
                    return slot
                    
            return None
            
        def binext_matfx(self):
            if not self.tex_envmap:
                return b""
                
            payload = struct.pack("iifii", 2, 2, self.bltex_envmap.specular_color_factor, 0, 1)
            payload += self.tex_envmap.bin()
            payload += struct.pack("i", 0)
            
            header = self.R.RwChunkHeader(RwTypes.MATEFFECTS, len(payload)).bin()
            
            return header + payload
            
        def binext_reflect(self):
            if not self.blmaterial.raytrace_mirror.use and ExportRenderware.decodedVer <= 0x34003:
                return b""
                
            factor = self.blmaterial.raytrace_mirror.reflect_factor if self.blmaterial.raytrace_mirror.use else 0
            
            colour = self.blmaterial.mirror_color
            payload = struct.pack("fffffi", colour[0], colour[1], colour[2], 1, self.blmaterial.raytrace_mirror.reflect_factor, 0)
            
            header = self.R.RwChunkHeader(RwTypes.MATREFLECTION, len(payload)).bin()
            
            return header + payload
            
        def binext_specular(self):
            if not self.bltex_specular:
                return b""
                
            payload = struct.pack("f", self.bltex_specular.specular_color_factor)
            
            texname = bytes(self.bltex_specular.texture.name, "ascii")
            payload += texname[:23]
            
            nullbyte = struct.pack("B", 0)
            
            for i in range(24 - min(23, len(texname))):
                payload += nullbyte
            
            header = self.R.RwChunkHeader(RwTypes.MATSPECULAR, len(payload)).bin()
            
            return header + payload
        
        def bin(self):
            payload = struct.pack("iBBBBiIfff", 0, int(self.red), int(self.green), int(self.blue), int(self.alpha), 0, 1 if self.tex_diffuse else 0, self.ambient, self.specular, self.diffuse)
            payload = self.R.RwChunkHeader(RwTypes.STRUCT, len(payload)).bin() + payload
            
            if self.tex_diffuse:
                payload += self.tex_diffuse.bin()
            
            extensions = self.binext_matfx() + self.binext_reflect() + self.binext_specular()
            extensions = self.R.RwChunkHeader(RwTypes.EXTENSION, len(extensions)).bin() + extensions
            
            payload += extensions
            
            header = self.R.RwChunkHeader(RwTypes.MATERIAL, len(payload)).bin()
            
            return header + payload
        
    class RpMaterialList:
        def __init__(self, geometry):
            self.R = ExportRenderware
            
            self.geometry = geometry
            self.clump = geometry.clump
            
            self.mesh = geometry.mesh
            
            self.mats = []
            
            for mat in self.mesh.materials:
                self.mats.append(self.R.RpMaterial(self, mat))
            
        def bin(self):
            payload = struct.pack("i", len(self.mesh.materials))
            
            for mat in self.mats:
                payload += struct.pack("i", -1)
                
            payload = self.R.RwChunkHeader(RwTypes.STRUCT, len(payload)).bin() + payload
            
            for mat in self.mats:
                payload += mat.bin()
            
            header = self.R.RwChunkHeader(RwTypes.MATERIALLIST, len(payload)).bin()
                
            return header + payload

    class RpGeometryList:
        def __init__(self):
            self.R = ExportRenderware
            
            self.geoms = []
            
        def bin(self):
            payload = struct.pack("i", len(self.geoms))
            payload = self.R.RwChunkHeader(RwTypes.STRUCT, len(payload)).bin() + payload
            
            for geom in self.geoms:
                payload += geom.bin()
                
            header = self.R.RwChunkHeader(RwTypes.GEOMETRYLIST, len(payload)).bin()
            
            return header + payload
            
    class RpGeometryChunkInfo:
        def __init__(self):
            self.flags = RpGeomFlag.TEXTURED | RpGeomFlag.NORMALS | RpGeomFlag.LIGHT | RpGeomFlag.MODULATEMATERIALCOLOR
            self.texCount = 1
            self.triangleCount = 0
            self.vertexCount = 0
            self.frameCount = 1
            
        def binraw(self):
            return struct.pack("HHiii", self.flags, self.texCount, self.triangleCount, self.vertexCount, self.frameCount)
            
    class RpGeometry:
        def __init__(self, atomic):
            self.R = ExportRenderware
            
            self.clump = atomic.clump
            self.atomic = atomic
            self.mesh = atomic.mesh
            self.index = len(self.clump.geometryList.geoms)
            self.clump.geometryList.geoms.append(self)
            self.chunkInfo = self.R.RpGeometryChunkInfo()
            
            self.uvname_diff = None
            self.uvname_env = None
            
            self.materialList = self.R.RpMaterialList(self)
            
            self.matTris = []
            
            for i in range(len(self.materialList.mats)):
                self.matTris.append([])
            
            mesh = self.mesh
            
            self.vdict = []
            
            for i in range(len(mesh.vertices)):
                self.vdict.append({})

            self.uvc = self.getUVData(self.uvname_diff)
            self.uvce = None
            
            if self.uvname_env and self.uvname_env != self.uvname_diff:
                self.uvce = self.getUVData(self.uvname_env)
            
            self.vertices = []
            self.triangles = []
            
            self.vertCol = None
            self.nightVertCol = None
            
            self.vertColData = None
            self.nightVertColData = None
            
            for vcol in self.mesh.vertex_colors:
                if vcol.name.lower() == "night" and self.nightVertCol is None:
                    self.nightVertCol = []
                    self.nightVertColData = vcol.data
                elif self.vertCol is None:
                    self.vertCol = []
                    self.vertColData = vcol.data
            
            for poly in mesh.polygons:
                self.addBlenderPoly(poly)
                
            if len(self.vertices) > 65535:
                raise Exception("Aborting export: vertex count exceeds 65535")
                    
            self.maxDist = 0
            
            for v in self.mesh.vertices:
                self.maxDist = max(self.maxDist, math.sqrt(v.co[0]*v.co[0] + v.co[1]*v.co[1] + v.co[2]*v.co[2]))
                
            self.chunkInfo.triangleCount = len(self.triangles)
            self.chunkInfo.vertexCount = len(self.vertices)
            
            if self.uvce:
                self.chunkInfo.texCount = 2
                self.chunkInfo.flags = self.chunkInfo.flags & (~RpGeomFlag.TEXTURED)
                self.chunkInfo.flags |= RpGeomFlag.TEXTURED2
                
            if self.R.decodedVer > 0x34003:
                self.chunkInfo.flags |= RpGeomFlag.POSITIONS
                
            if self.vertColData:
                self.chunkInfo.flags |= RpGeomFlag.PRELIT
                
        def findVertex(self, type):
            for i in range(len(self.blmaterial.texture_slots)):
                textype = ""
                slot = self.blmaterial.texture_slots[i]
            
                if slot and slot.texture:
                    if slot.texture.type == "ENVIRONMENT_MAP":
                        textype = "ENVMAP"
                    elif slot.use_map_color_spec and not slot.use_map_color_diffuse:
                        textype = "SPECULAR"
                    elif slot.use_map_color_diffuse and not slot.use_map_color_spec:
                        textype = "DIFFUSE"
                        
                if textype == type:
                    return slot
                    
            return None
            
        def getUVData(self, name):
            for i in range(len(self.mesh.uv_textures)):
                if name and self.mesh.uv_textures[i] and self.mesh.uv_textures[i].name == name:
                    return self.mesh.uv_layers[i].data
                    
            return None
            
        def newVertId(self, id, uv, uve):
            if (uv + uve) not in self.vdict[id]:
                self.vdict[id][uv + uve] = len(self.vertices)
                
                self.vertices.append(self.R.RpVertex(self.mesh.vertices[id].co, uv, uve, self.mesh.vertices[id].normal))
                
                if self.vertColData:
                    self.vertCol.append((int(self.vertColData[id].color[0]*255), int(self.vertColData[id].color[1]*255), int(self.vertColData[id].color[2]*255)))
                
                if self.nightVertColData:
                    self.nightVertCol.append((int(self.nightVertColData[id].color[0]*255), int(self.nightVertColData[id].color[1]*255), int(self.nightVertColData[id].color[2]*255)))
            
            return self.vdict[id][(uv + uve)]
            
        def addRawPoly(self, verts, uvs, mat):
            newIds = []
        
            for i in range(3):
                uv = tuple(self.uvc[uvs[i]].uv) if self.uvc else (0, 0)
                uve = tuple(self.uvce[uvs[i]].uv) if self.uvce else (0, 0)
                
                newIds.append(self.newVertId(verts[i], uv, uve))
                    
            self.triangles.append(self.R.RpTriangle(newIds[0], newIds[1], newIds[2], mat))
            
            if mat >= 0:
                self.matTris[mat].append(newIds[0])
                self.matTris[mat].append(newIds[1])
                self.matTris[mat].append(newIds[2])
            
        def addBlenderPoly(self, p):
            if len(p.vertices) < 3 or len(p.vertices) > 4:
                raise Exception("Aborting export: Invalid number of vertices on an edge.")
            
            self.addRawPoly([p.vertices[0], p.vertices[1], p.vertices[2]], [p.loop_indices[0], p.loop_indices[1], p.loop_indices[2]], p.material_index)
            if len(p.vertices) == 4:
                self.addRawPoly([p.vertices[0], p.vertices[3], p.vertices[2]], [p.loop_indices[0], p.loop_indices[3], p.loop_indices[2]], p.material_index)
        
        def binext_binmesh(self):
            payload = b""
            splits = 0
            total = 0
            
            for i in range(len(self.matTris)):
                if len(self.matTris[i]) == 0:
                    continue
                
                splits += 1
                total += len(self.matTris[i])
                payload += struct.pack("ii", len(self.matTris[i]), i)
                
                for id in self.matTris[i]:
                    payload += struct.pack("i", id)
            
            payload = struct.pack("iii", 0, splits, total) + payload
            
            header = self.R.RwChunkHeader(RwTypes.BINMESHPLG, len(payload)).bin()
            
            return header + payload
            
        def binext_morph(self):
            if self.R.decodedVer > 0x34003 or self.R.decodedVer < 0x33000:
                return b""
                
            payload = struct.pack("i", 0)
            header = self.R.RwChunkHeader(RwTypes.MORPHPLG, len(payload)).bin()
            
            return header + payload
            
        def binext_meshext(self):
            if self.R.decodedVer <= 0x34003:
                return b""
                
            payload = struct.pack("i", 0)
            header = self.R.RwChunkHeader(RwTypes.MESHEXTENSION, len(payload)).bin()
            
            return header + payload
            
        def binext_skin(self):
            object = self.atomic.frame.object
        
            try:
                if len(object.rw_skindata) > 0:
                    textf = bpy.data.texts[object.rw_skindata].as_string()
                    rawdata = zlib.decompress(base64.b64decode(bytes(textf, "ascii")))
                else:
                    return b""
            except:
                return b""
                
            payload = rawdata
            header = self.R.RwChunkHeader(RwTypes.SKINPLG, len(payload)).bin()
            
            return header + payload
            
        def binext_nightcol(self):
            if not self.nightVertCol:
                return b""
                
            payload = struct.pack("I", 1)
            
            for col in self.nightVertCol:
                payload += struct.pack("BBBB", col[0], col[1], col[2], 255)
                
            header = self.R.RwChunkHeader(RwTypes.NIGHTCOLS, len(payload)).bin()
            
            return header + payload
        
        def bin(self):
            payload = self.chunkInfo.binraw()
            
            if self.R.decodedVer < 0x34001:
                payload += struct.pack("fff", 0, 0, 1)
                
            if self.vertCol:
                for col in self.vertCol:
                    payload += struct.pack("BBBB", col[0], col[1], col[2], 255)
            
            for vertex in self.vertices:
                payload += self.R.RwUVCoord(vertex.uv[0], vertex.uv[1]).bin()
                
            if self.uvce:
                for vertex in self.vertices:
                    payload += self.R.RwUVCoord(vertex.uve[0], vertex.uve[1]).bin()
                
            for triangle in self.triangles:
                payload += triangle.bin()
            
            payload += struct.pack("ffffii", 0, 0, 0, self.maxDist, 1, 1)
            
            for vertex in self.vertices:
                payload += self.R.RwVector3(vertex.pos[0], vertex.pos[1], vertex.pos[2]).bin()
            
            for vertex in self.vertices:
                payload += self.R.RwVector3(vertex.normal[0], vertex.normal[1], vertex.normal[2]).bin()
                
            payload = self.R.RwChunkHeader(RwTypes.STRUCT, len(payload)).bin() + payload
            
            payload += self.materialList.bin()
            
            extensions = self.binext_binmesh() + self.binext_skin() + self.binext_morph() + self.binext_meshext() + self.binext_nightcol()
            extensions = self.R.RwChunkHeader(RwTypes.EXTENSION, len(extensions)).bin() + extensions
            payload += extensions
            
            header = self.R.RwChunkHeader(RwTypes.GEOMETRY, len(payload)).bin()
            
            return header + payload
            
    class RpClumpChunkInfo:
        def __init__(self, atomicCount, lightCount, cameraCount):
            self.R = ExportRenderware
            
            self.atomicCount = atomicCount
            self.lightCount = lightCount
            self.cameraCount = cameraCount
            
        def bin(self):
            payload = struct.pack("i", self.atomicCount)
            
            if self.R.decodedVer > 0x33000:
                payload += struct.pack("ii", self.lightCount, self.cameraCount)
            
            header = self.R.RwChunkHeader(RwTypes.STRUCT, len(payload)).bin()
            
            return header + payload
        
    class RpClump:
        def __init__(self, context, exportVer):
            self.R = ExportRenderware
            self.R.targetVer = exportVer
            self.R.decodedVer = RwTypes.decodeVersion(self.R.targetVer)
        
            self.context = context
            self.frameList = self.R.RwFrameList()
            self.geometryList = self.R.RpGeometryList()
            self.colbin = None
            
            exportables = []
            
            for object in context.selected_objects:
                parent = object.parent
                add = True
                
                while parent:
                    if parent in context.selected_objects:
                        add = False
                        break
                    
                    parent = parent.parent
                    
                if add:
                    exportables.append(object)
            
            for object in exportables:
                if str(object.type) != "MESH" and str(object.type) != "EMPTY":
                    print("Ignoring object " + object.name + ", type " + object.type)
                    continue
                
                self.R.RwFrame(self, object, None)
            
            if len(self.frameList.frames) == 0:
                raise Exception("Aborting export: no frames selected.")
                
        def binext_coll(self):
            if not self.colbin:
                return b""
                
            payload = self.colbin
            header = self.R.RwChunkHeader(RwTypes.COLLISION, len(self.colbin)).bin()
            
            return header + payload
            
        def bin(self):
            payload = self.R.RpClumpChunkInfo(len(self.geometryList.geoms), 0, 0).bin()
            payload += self.frameList.bin()
            payload += self.geometryList.bin()
            
            for geometry in self.geometryList.geoms:
                payload += geometry.atomic.bin()
            
            extensions = self.binext_coll()
            extensions = self.R.RwChunkHeader(RwTypes.EXTENSION, len(extensions)).bin() + extensions
            payload += extensions
                
            header = self.R.RwChunkHeader(RwTypes.CLUMP, len(payload)).bin()
            
            return header + payload    

    def __init__(self, context, exportVerIndex, filepath):
        if exportVerIndex == "1":
            exportVer = 0x0800FFFF
        elif exportVerIndex == "2":
            exportVer = 0x1003FFFF
        else:
            exportVer = 0x1803FFFF
        
        outf = open(filepath, "wb")
        outf.write(self.RpClump(context, exportVer).bin())
        outf.close()
        
    def unmangleName(name):
        if len(name) > 4 and name[-4] == "." and name[-3:].isnumeric():
            return name[:-4]
        else:
            return name

class ExportRenderwareMenu(bpy.types.Operator):
    expVersionValues = (("1", "GTA III", ""), ("2", "Vice City", ""), ("3", "San Andreas", ""))
    
    bl_idname = "export_rw.dff"
    bl_label = "Export Renderware (.dff)"
    
    filename_ext = ".dff"
    
    filepath = StringProperty(subtype = "FILE_PATH")
    expVersion = EnumProperty(name = "Export version", items = expVersionValues, default="2")
    
    def invoke(self, context, event):
        wm = context.window_manager
        
        wm.fileselect_add(self)
        
        return {"RUNNING_MODAL"}
    
    def execute(self, context):
        setupProps()
        
        ExportRenderware(context,  self.expVersion, self.filepath)
        
        return {"FINISHED"}

class ImportRenderwareMenu(bpy.types.Operator):
    bl_idname = "import_rw.dff"
    bl_label = "Import Renderware (.dff)"
    
    filename_ext = ".dff"
    filter_glob = StringProperty(
            default="*.dff",
            options={'HIDDEN'},
            )
    
    filepath = StringProperty(subtype = "FILE_PATH")
    files = CollectionProperty(type=bpy.types.PropertyGroup)

    
    def invoke(self, context, event):
        wm = context.window_manager
        
        wm.fileselect_add(self)
        
        return {"RUNNING_MODAL"}
    
    def execute(self, context):
        ts = time.time()
        setupProps()
        
        folder = (os.path.dirname(self.filepath))
        
        for x in self.files:
            path_to_file = (os.path.join(folder, x.name))
            ImportRenderware(path_to_file)
            
        print("Done!")
        return {"FINISHED"}

class ImportIPL(bpy.types.Operator):
    bl_idname = "import_rw.ipl"
    bl_label = "Import models from map file (.ipl)"
    filename_ext = ".ipl"
    filter_glob = StringProperty(
            default="*.ipl",
            options={'HIDDEN'},
            )
            
    
    filepath = StringProperty(subtype = "FILE_PATH")
    selected_files = CollectionProperty(type=bpy.types.PropertyGroup)
    
    dff_models=StringProperty(
        name="DFF Directory",
        description="Directory where models are stored "
        "(For better results, extract all game's models and textures into a folder and extract all the textures.)",
        subtype = "FILE_PATH")
    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {"RUNNING_MODAL"}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "dff_models")
    
        self.layout = layout
    
    def execute(self, context):
        if not os.path.isdir(os.path.normcase(dff_models)):
            return {"RUNNING_MODAL"}
        
        setupProps()
        folder = (os.path.dirname(self.filepath))
        
        for x in self.selected_files:
            path_to_file = (os.path.join(folder, x.name))
            print(path_to_file)
            ParseIPL(path_to_file)
        
        return {"FINISHED"}

def export_func(self, context):
    self.layout.operator(ExportRenderwareMenu.bl_idname, text="GTA RenderWare compatible model (.dff)")

def import_func(self, context):
    self.layout.operator(ImportRenderwareMenu.bl_idname, text="GTA RenderWare compatible model (.dff)")
    #self.layout.operator(ImportIPL.bl_idname, text="GTA item definitions / Map (.ipl)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(export_func)
    bpy.types.INFO_MT_file_import.append(import_func)
    #bpy.utils.register_class(renderwareToolsPanel)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(export_func)
    bpy.types.INFO_MT_file_import.remove(import_func)
    #bpy.utils.unregister_class(renderwareToolsPanel)

def setupProps():
    class renderwarePanel(bpy.types.Panel):
        bl_space_type = "VIEW_3D"
        bl_region_type = "UI"
        bl_label = "Renderware"
        
        def draw(self, context):
            self.layout.prop(bpy.context.active_object, "renderright")
            self.layout.prop(bpy.context.active_object, "renderextra")
            self.layout.prop(bpy.context.active_object, "matfxpipe")
            self.layout.prop(bpy.context.active_object, "collhex")
            self.layout.prop(bpy.context.active_object, "rw_hanimdata")
            self.layout.prop(bpy.context.active_object, "rw_skindata")
    
    if hasattr(bpy.types.Object, "collhex"):
        return
    
    bpy.types.Object.collhex = bpy.props.StringProperty(name = "Collision", description = "Name of the text object that contains collision binary data.", maxlen = 100)
    bpy.types.Object.renderright = bpy.props.IntProperty(name = "RenderRight", description = "Index of the plugin whose pipeline is used for rendering.")
    bpy.types.Object.renderextra = bpy.props.IntProperty(name = "RenderExtra", description = "Extra arguments to the render pipeline.")
    bpy.types.Object.matfxpipe = bpy.props.BoolProperty(name = "MatFX pipeline", description = "Whether rendering is handled by MatFX pipeline.")
    bpy.types.Object.rw_hanimdata = bpy.props.StringProperty(name = "HAnimData", description = "Info for this skin bone.", maxlen = 100)
    bpy.types.Object.rw_skindata = bpy.props.StringProperty(name = "SkinData", description = "Skin data (bone vertices etc) for this mesh.", maxlen = 100)
    
    bpy.utils.register_class(renderwarePanel)

if __name__ == "__main__":
    unregister()
    register()
    setupProps()