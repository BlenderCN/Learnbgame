#Ported to blender from "MT Framework tools" https://www.dropbox.com/s/4ufvrgkdsioe3a6/MT%20Framework.mzp?dl=0 
#(https://lukascone.wordpress.com/2017/06/18/mt-framework-tools/)



import math
import bpy
from array import array

from ..config import initConfig
from ..dbg import dbg
from ..common import fileOperations as fileOp
from ..common import constants as cons
from ..vertexbuffers import mhw as mod3

(config,CHUNK_PATH,PATH) = initConfig()



class matrix3:
    def __init__(self,v):
        self.col1 = [v,v,v]
        self.col2 = [v,v,v]
        self.col3 = [v,v,v]
        self.col4 = [v,v,v]

def readmatrix44(headerref):
    mtx = matrix3(0)
    vectorRead = fileOp.ReadBEVector4 if headerref.bendian else fileOp.ReadVector4
    mtx.col1 = vectorRead(headerref.fl)
    mtx.col2 = vectorRead(headerref.fl)
    mtx.col3 = vectorRead(headerref.fl)
    mtx.col4 = vectorRead(headerref.fl)
    return mtx
    
def facesFromPolygons(vertexSub, polygons, verts2):
    faces = []
    verts = [vert.co for vert in verts2]
    vertIdxMap = {i2:i1 for i1, i2 in enumerate([vert.index for vert in verts2])}
    for p in polygons:
        v0 = p.vertices[0]
        for v1,v2 in zip(p.vertices[1:],p.vertices[2:]):   
            faces.append(vertexSub+vertIdxMap[v0])
            faces.append(vertexSub+vertIdxMap[v1])
            faces.append(vertexSub+vertIdxMap[v2])
    return verts, vertIdxMap, faces

def calculateTangentSpace(bm, vertIdxMap, export_normals):
    uvs = {}
    tangents = {}
    normals = {}
    if len(bm.uv_layers)>0:
        for p in bm.polygons:
            for loop in p.loop_indices:
                vId = vertIdxMap[bm.loops[loop].vertex_index]
                uvs[vId] = bm.uv_layers[0].data[loop].uv
                if export_normals:
                    tangents[vId] = (bm.loops[loop].tangent,bm.loops[loop].bitangent_sign)
                    normals[vId] = bm.loops[loop].normal
    return uvs, tangents, normals

def calculateSkelleton(vertices, vertexGroup):
    weights = {}
    bones = {}
    for v in vertices:
        bones[v.index] = []
        for g in v.groups:
            vg = vertexGroup[g.group]
            if vg.name[0:4] == 'Bone':
                bones[v.index].append(int(vg.name.split(".")[1]))
        vertWeights = []
        for g in v.groups:
            if math.isnan(g.weight):
                raise Exception("NaN as weight found for group %d and vertice index: %d" % (g.group,v.index))
            vertWeights.append(g.weight)
        if len(vertWeights)>8:
            bpy.context.scene.cursor_location = (v.co[0], v.co[1], v.co[2])
            raise Exception#("Overflowing maximum number of 8 weights for %s %s: %f, %f, %f." % (self.id, self.uid, v.co[0], v.co[1], v.co[2]))
        weights[v.index] = vertWeights 
    return weights, bones

#TODO, rename me
class UnknS2:
    def __init__(self,fl,ui):
        self.id = ui
        self.offset = fileOp.getPos(fl)
        self.unkn1 = fileOp.ReadByte(fl)
        self.unkn2 = fileOp.ReadByte(fl)
        self.unkn3 = fileOp.ReadShort(fl)
        self.unkn4 = fileOp.ReadByte(fl)
        self.unkn5 = fileOp.ReadByte(fl)
        self.unkn6 = fileOp.ReadShort(fl)
        self.texIdx = fileOp.ReadLong(fl)
        self.unkn7 = fileOp.ReadLong(fl)

class Material:
    def __init__(self,fl,mi):
        self.id = mi
        self.headId = fileOp.ReadLong(fl)
        self.unkn1 = fileOp.ReadByte(fl)
        self.unkn2 = fileOp.ReadByte(fl)
        self.unkn3 = fileOp.ReadByte(fl)
        self.unkn4 = fileOp.ReadByte(fl)
        self.skinid1 = fileOp.ReadLong(fl)
        self.skinid2 = fileOp.ReadLong(fl)
        self.matSize = fileOp.ReadLong(fl)
        self.unkn5 = fileOp.ReadBytes(fl,12+1+15)
        self.startAddr = fileOp.ReadLong(fl)
        self.unkn6 = fileOp.ReadLong(fl)
    
class MeshPart:
    def __init__(self,
            MeshPartOffset,
            uid,
            id,
            Material,
            UnknS2Idx,
            LOD,
            BlockSize,
            BlockType,
            VertexSub,
            VertexCount,
            VertexOffset,
            FaceOffset,
            FaceCount,
            VertexBase,
            meshdata,
            boneremapid,
            headerref,
            loadmeshdata,
            writemeshdata):
            self.MeshPartOffset = MeshPartOffset
            self.uid = uid
            self.id = id
            self.Material = Material
            self.UnknS2Idx = UnknS2Idx
            self.LOD = LOD
            self.BlockSize = BlockSize
            self.BlockType = BlockType
            if BlockType == 0:
                raise Exception("BlockType was 0")
            self.VertexSub = VertexSub
            self.VertexCount = VertexCount
            self.VertexOffset = VertexOffset
            self.FaceOffset = FaceOffset
            self.FaceCount = FaceCount
            self.VertexBase = VertexBase
            self.meshdata = meshdata
            self.boneremapid = boneremapid
            self.headerref = headerref
            self.loadmeshdataF = loadmeshdata
            self.writemeshdataF = writemeshdata
            self.customName = None
            
    def loadmeshdata(self):
        self.loadmeshdataF(self)
        
    def calcVertexBufferSize(self):
        cls = mod3.MODVertexBufferSelector(self.BlockType)
        return self.VertexCount*cls.getStructSize()
    
    def getVertexRegionEnd(self):
        meshPart = self
        headerref = self.headerref
        cls = mod3.MODVertexBufferSelector(self.BlockType)
        VOFF = headerref.VertexOffset+meshPart.VertexOffset
        BOFF = meshPart.VertexSub+meshPart.VertexBase
        START = VOFF+meshPart.BlockSize*BOFF
        RES = START+self.VertexCount*cls.getStructSize()
        dbg("#%d getVertexRegionEnd %08x [START=%08x,VertexCount=%d]" % (self.uid,RES,START,self.VertexCount))
        return RES
    
    def updateVertexOffsets(self, parts, newVertexCount, cls):
        for i,p in enumerate(parts):
            if p.getVertexRegionEnd() > self.currentRegionEnd:
                dbg("#%d oldVertexOffset: 0x%08x VertexSub: 0x%08x VertexRegionEnd: 0x%08x currentRegionEnd: 0x%08x" % (i,p.VertexSub,p.VertexOffset,p.getVertexRegionEnd(),self.currentRegionEnd))
                if p.VertexOffset+cls.getStructSize()*(newVertexCount-self.VertexCount)>0xFFFFFFFF:
                    p.writeVertexSub(p.VertexSub+(newVertexCount-self.VertexCount))
                elif p.VertexOffset+cls.getStructSize()*(newVertexCount-self.VertexCount)>0:
                    p.writeVertexOffset(p.VertexOffset+cls.getStructSize()*(newVertexCount-self.VertexCount))
                else:
                    if(p.VertexBase>0):
                        p.writeVertexBase(p.VertexBase-(self.VertexCount-newVertexCount))
                    else:
                        if p.VertexSub+(newVertexCount-self.VertexCount)>=0:
                            p.writeVertexSub(p.VertexSub+(newVertexCount-self.VertexCount))
                        else:
                            dbg("p.VertexSub+(newVertexCount-self.VertexCount): %d < 0" % (p.VertexSub+(newVertexCount-self.VertexCount)))
                            raise Exception("No clue how to handle case where VertexBase=0 and VertexSub<0")
    
    def modifyVertexCount(self,parts,newVertexCount):
        dbg("modifyVertexCount %d [oldVertexCount: %d]" % (newVertexCount,self.VertexCount))
        if newVertexCount==self.VertexCount:
            return
        self.currentRegionEnd = self.getVertexRegionEnd()
        cls = mod3.MODVertexBufferSelector(self.BlockType)
        fl = self.headerref.fl
        headerref = self.headerref
        self.updateVertexOffsets(parts, newVertexCount, cls)
        oldVertexCount = self.VertexCount
        self.VertexCount = newVertexCount
        vertexDifference = newVertexCount - oldVertexCount
        dbg("FaceOffset before %08x" % self.headerref.FaceOffset)
        self.headerref.FaceOffset += cls.getStructSize()*(vertexDifference)
        dbg("FaceOffset after %08x" % self.headerref.FaceOffset)
        fileOp.Seek(fl,self.MeshPartOffset+cons.MESH_PART_VERTEX_COUNT_REL_OFFSET)
        fileOp.WriteLongs(fl,[self.VertexCount])
        appendEmptyVertices = cls.appendEmptyVertices
        appendEmptyVertices(headerref.fl,self.currentRegionEnd,oldVertexCount,vertexDifference)
        
    def writeVertexSub(self,newVertexSub):
        fl = self.headerref.fl
        self.VertexSub = newVertexSub
        fileOp.Seek(fl,self.MeshPartOffset+0x10)
        fileOp.WriteLongs(fl,[self.VertexSub])
        
    def writeVertexBase(self,newVertexBase):
        fl = self.headerref.fl
        self.VertexBase = newVertexBase
        fileOp.Seek(fl,self.MeshPartOffset+0x24)
        fileOp.WriteLongs(fl,[self.VertexBase])
        
    def modifyFaceCount(self,parts,newFaceCount):
        newFaceCount *= 3
        dbg("#%d modifyFaceCount %d [oldFaceCount: %d] [headerRef.FaceOffset: %08x , self.FaceOffset: %08x]" %
            (self.uid, newFaceCount, self.FaceCount, self.headerref.FaceOffset, self.FaceOffset))
        if newFaceCount==self.FaceCount:
            return
        fl = self.headerref.fl
        headerref = self.headerref
        for p in parts:
            #file order will not allow this ... hopefully
            #if headerref.VertexOffset+p.VertexOffset > headerref.FaceOffset+self.FaceOffset:
            #    p.writeVertexOffset(p.VertexOffset+3*2*(newFaceCount-self.FaceCount))
            if headerref.FaceOffset+p.FaceOffset > headerref.FaceOffset+self.FaceOffset:
                p.writeFaceOffset(p.FaceOffset+(newFaceCount-self.FaceCount))
        self.appendEmptyFaces(headerref.FaceOffset+self.FaceOffset*2, int(self.FaceCount/3), int((newFaceCount-self.FaceCount)/3))
        self.FaceCount = newFaceCount
        fileOp.Seek(fl,self.MeshPartOffset+0x20)
        fileOp.WriteLongs(fl,[self.FaceCount])
        
    def appendEmptyFaces(self,FaceOffset,oldFaceCount,diffFaceCount):
        dbg("appendEmptyFaces %08x %d %d" % (FaceOffset,oldFaceCount,diffFaceCount))
        fl = self.headerref.fl
        if(diffFaceCount > 0):
            fileOp.InsertEmptyBytes(fl,FaceOffset+diffFaceCount*2*3,diffFaceCount*2*3)
        elif(diffFaceCount < 0):
            SubFaceCount = 0-diffFaceCount
            fileOp.DeleteBytes(fl,FaceOffset+oldFaceCount*2*3-SubFaceCount*2*3,SubFaceCount*2*3)
            
    def writeVertexOffset(self,newOffset):
        dbg("writeVertexOffset %08x [%08x]" % (newOffset,self.MeshPartOffset+0x14))
        if newOffset < 0:
            raise Exception("Calcucated invalid VertexOffset %08x [oldVertexOffset %08x] " % (newOffset,self.VertexOffset))
        self.VertexOffset = newOffset
        fileOp.Seek(self.headerref.fl,self.MeshPartOffset+0x14)
        fileOp.WriteLongs(self.headerref.fl,[self.VertexOffset])
        
    def writeFaceOffset(self,newOffset):
        dbg("writeFaceOffset %08x [%08x,%08x]" % (newOffset,self.MeshPartOffset+0x1C,newOffset*2+self.headerref.FaceOffset))
        self.FaceOffset = newOffset
        fileOp.Seek(self.headerref.fl,self.MeshPartOffset+0x1C)
        fileOp.WriteLongs(self.headerref.fl,[self.FaceOffset])
        
    def writeCustomProperties(self,fl):
        dbg("writeCustomProperties")
        headerref = self.headerref
        n = self.getName()
        if not n in bpy.data.objects:
            dbg("Mesh %s not found!" % n)
            return
        obj = bpy.data.objects[n]
        bm = obj.data
        if "LOD" in bm:
            self.writeLOD(fl,bm["LOD"])
        if "Material" in bm:
            if bm["Material"] in headerref.materials:
                self.writeMaterial(fl,headerref.materials.index(bm["Material"]))
                
    def writeMaterial(self,fl,materialIndex):
        fileOp.Seek(fl,self.MeshPartOffset+self.getMaterialOffset())
        fileOp.WriteShorts(fl,[materialIndex])
        
    def writeLOD(self,fl,lod):
        fileOp.Seek(fl,self.MeshPartOffset+self.getLODOffset())
        fileOp.WriteLongs(fl,[lod])
    def getLODOffset(self):
        return 8
    def getMaterialOffset(self):
        return 6
    
    def writeVertexes(self,fl,do_write_bones,export_normals):
        dbg("writeVertexes uid:%d" % self.uid)
        n = self.getName()
        if not n in bpy.data.objects:
            dbg("Mesh %s not found!" % n)
            return
        obj = bpy.data.objects[n]
        bm = obj.data
        
        my_id = bm.vertex_layers_int['id']
        verts2 = sorted(bm.vertices, key=lambda v: my_id.data[v.index].value)
        verts, vertIdxMap, faces  = facesFromPolygons(self.VertexSub, bm.polygons, verts2)
        uvs, tangents, normals  = calculateTangentSpace(bm, vertIdxMap, export_normals)
        weights, bones = calculateSkelleton(verts2, obj.vertex_groups)     
        self.writemeshdataF(self,fl,verts,uvs,faces,weights,bones,normals,tangents)
        
    def getName(self):
        if self.customName is None:
            return "MyObject.%05d.%08x" % (self.uid,self.BlockType)
        return self.customName
    def setName(self,name):
        self.customName = name
    def getNewUid(self,parts):
        res = 0
        for p in parts:
            res = max(res,p.uid)
        dbg("getNewUid result 0x%08x" % res)
        return res+1
    def getNewId(self,parts):
        res = 0
        for p in parts:
            res = max(res,p.id)
        dbg("getNewId result 0x%08x" % res)
        return res+1
    def getNewVertexOffset(self,parts):
        res = 0
        for p in parts:
            r = p.VertexOffset+(p.VertexSub+p.VertexCount)*self.BlockSize
            dbg("0x%08x = 0x%08x + (%d + %d)*%d" % (r ,p.VertexOffset,p.VertexSub,p.VertexCount,self.BlockSize))
            res = max(res,r)
        dbg("getNewVertexOffset result 0x%08x ()" % res)
        return res
    def getNewFaceOffset(self,parts):
        res = 0
        for p in parts:
            res = max(res,p.FaceOffset+p.FaceCount)
        dbg("getNewFaceOffset result 0x%08x" % res)
        return res
    def getNewMeshPartOffset(self,parts):
        res = 0
        for p in parts:
            res = max(res,p.MeshPartOffset+cons.MESH_PART_SIZE)
        dbg("getNewMeshPartOffset result 0x%08x" % res)
        return res
    def createEmptyClone(self,parts):
        dbg("createEmptyClone")
        fl = self.headerref.fl
        mpo = self.getNewMeshPartOffset(parts)
        dbg("mpo: %08x" % mpo)
        fileOp.Seek(fl,self.MeshPartOffset)
        data = fileOp.ReadBytes(fl,cons.MESH_PART_SIZE)
        data = array('B', data)
        dbg("data:")
        dbg(data)
        fileOp.InsertBytes(fl,mpo,data)
        fileOp.Seek(fl,mpo+cons.MESH_PART_VERTEX_COUNT_REL_OFFSET)
        dbg("write 0 at: %08x" % fileOp.getPos(fl))
        fileOp.WriteShorts(fl,[0])
        fileOp.Seek(fl,mpo+cons.MESH_PART_FACE_COUNT_REL_OFFSET)
        dbg("write 0 at: %08x" % fileOp.getPos(fl))
        fileOp.WriteShorts(fl,[0])
        p = MeshPart(
            mpo,
            self.getNewUid(parts),
            self.getNewId(parts),
            self.Material,
            self.UnknS2Idx,
            self.LOD,
            self.BlockSize,
            self.BlockType,
            0,
            0,
            self.getNewVertexOffset(parts),
            self.getNewFaceOffset(parts),
            0,
            0,
            None,
            self.boneremapid,
            self.headerref,
            self.loadmeshdataF,
            self.writemeshdataF)
        p.writeVertexSub(0)
        p.writeVertexBase(0)
        p.writeVertexOffset(p.VertexOffset)
        p.writeFaceOffset(p.FaceOffset)
        return p

class MODBoneInfo2:
    def __init__(self,internalId,fl,bendian):
        #self.id = fileOp.ReadShort(fl)
        #self.internalId = internalId
        fileOp.ReadShort(fl)
        self.id = internalId
        self.parentid = fileOp.ReadByte(fl)
        self.child = fileOp.ReadByte(fl)
        fileOp.fseek(fl,4)
        self.length = fileOp.ReadFloat(fl)
        self.x = fileOp.ReadFloat(fl)
        self.y = fileOp.ReadFloat(fl)
        self.z = fileOp.ReadFloat(fl)
        

"""
def CollectStrips(fl,modf=1):
    dbg("CollectStrips")
    raise Exception("TODO")
    resarray = []
    f1t = fileOp.ReadShort(fl)
    f2t = fileOp.ReadShort(fl) 
    f = 2
    while f < num:
        cf = fileOp.ReadShort(fl) 
        if cf == 0xffff:
            f1t = fileOp.ReadShort(fl)
            f2t = fileOp.ReadShort(fl) 
            f += 3
        else:
            if (f % 2) == 1:
                cfa = [cf,f2t,f1t]
            else:
                cfa = [f1t,f2t,cf]
            resarray.append([x+modf for x in cfa])
            f1t = f2t
            f2t = cf
            f += 1
    return resarray

def CollectTris(fl,num,modf=1):
    dbg("CollectTris %d" % num)
    res = []
    for i in range(0 ,num):
        res.append([x+modf for x in [fileOp.ReadShort(fl) , fileOp.ReadShort(fl) ,fileOp.ReadShort(fl)]])
    return res

def CollectBETris(fl,num,modf=1):
    dbg("CollectBETris %d" % num)
    res = []
    for i in range(0 ,num):
        res.append([x+modf for x in [fileOp.ReadBEShort(fl) , fileOp.ReadBEShort(fl) ,fileOp.ReadBEShort(fl)]])
    return res

def CollectBEStrips(fl,modf=1):
    dbg("CollectBEStrips")
    resarray = []
    f1t = fileOp.ReadBEShort(fl)
    f2t = fileOp.ReadBEShort(fl) 
    f = 2
    while f < num:
        cf = fileOp.ReadBEShort(fl) 
        if cf == 0xffff:
            f1t = fileOp.ReadBEShort(fl)
            f2t = fileOp.ReadBEShort(fl) 
            f += 3
        else:
            if (f % 2) == 1:
                cfa = [cf,f2t,f1t]
            else:
                cfa = [f1t,f2t,cf]
            resarray.append(cfa+modf)
            f1t = f2t
            f2t = cf
            f += 1
    return resarray
"""