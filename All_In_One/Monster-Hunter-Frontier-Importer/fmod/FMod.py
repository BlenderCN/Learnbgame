# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 23:03:36 2019

@author: AsteriskAmpersand
"""
try:
    from ..fmod.FBlock import FBlock
    from ..common.FileLike import FileLike
except:
    import sys
    sys.path.insert(0, r'..\common')
    sys.path.insert(0, r'..\fmod')
    from FBlock import FBlock
    from FileLike import FileLike    

class FFaces():
    def __init__(self, FaceBlock):
        self.Faces = []
        for tristripArray in FaceBlock.Data:
            for tristrip in tristripArray.Data:
                verts=tristrip.Data.vertices
                self.Faces += [[v1.id,v2.id,v3.id] for v1, v2, v3 in zip(verts[:-2], verts[1:-1], verts[2:])]

class FUnkSing():
    def __init__(self, UnknownSingularBlock):
        pass

class FTriData():
    def __init__(self, FaceDataBlock):
        self.Data = [faceElement.Data for faceElement in FaceDataBlock.Data]

class FVertices():
    def __init__(self, VertexBlock):
        self.Vertices = [(Vertex.Data.x, Vertex.Data.y, Vertex.Data.z) for Vertex in VertexBlock.Data]
        
class FNormals():
    def __init__(self, NormalsBlock):
        self.Normals = [[Normal.Data.x, Normal.Data.y, Normal.Data.z] for Normal in NormalsBlock.Data]
        
class FUVs():
    def __init__(self, UVBlock):
        self.UVs = [[UV.Data.u, 1-UV.Data.v] for UV in UVBlock.Data]
        
class FRGB():
    def __init__(self,RGBBlock):
        self.RGB = [[rgb.Data.x,rgb.Data.y,rgb.Data.z,rgb.Data.w] for rgb in RGBBlock.Data]

class FMesh():
    def __init__(self, ObjectBlock):
        Objects = iter(ObjectBlock.Data)
        self.Faces = FFaces(next(Objects))
        self.UnknownSingular = FUnkSing(next(Objects))
        self.UnknownTriData = FTriData(next(Objects))
        self.Vertices = FVertices(next(Objects))
        self.Normals = FNormals(next(Objects))
        self.UVs = FUVs(next(Objects))
        self.RGBLike = FRGB(next(Objects))
        
    def traditionalMeshStructure(self):
        return {"vertices":self.Vertices.Vertices, 
                "faces":self.Faces.Faces, 
                "normals":self.Normals.Normals, 
                "uvs":self.UVs.UVs}
        
class FModel():
    def __init__(self, FilePath):
        with open(FilePath, "rb") as modelFile:
            frontierFile = FBlock()
            frontierFile.marshall(FileLike(modelFile.read()))
        Meshes = frontierFile.Data[1].Data
        self.Meshparts = [FMesh(Mesh) for Mesh in Meshes]
    
    def traditionalMeshStructure(self):
        return [mesh.traditionalMeshStructure() for mesh in self.Meshparts]
    
    

