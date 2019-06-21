import bpy
import math
import imp
from arnold import *
import ctypes
from mathutils import Matrix
from . import utils

class PolyMesh():
    def __init__(self,mesh,materials,scene):
        self.mesh = mesh
        self.subsurf = False
        if len(mesh.modifiers) > 0:
            for mod in mesh.modifiers:
                if mod.type == "SUBSURF" and mod.show_render:
                    self.subsurf = mod
                    try:
                        self.subsurf.show_render = False
                    except:
                        pass
            self.meshdata = mesh.to_mesh(scene,True,'RENDER')
            self.mustCleanup = True
        else:
            self.meshdata = mesh.data
            self.mustCleanup = False

        self.materials = materials

    def write(self):
        # create the node
        self.amesh = AiNode(b"polymesh")
        AiNodeSetStr(self.amesh,b"name",self.mesh.name.encode('utf-8')) 

        # create shorthand variables
        faces = self.meshdata.faces
        vertices = self.meshdata.vertices
        numFaces = len(faces)
        numVerts = len(vertices)

        # Number of sides per polygon
        nsides = AiArrayAllocate(numFaces, 1, AI_TYPE_UINT)
        for i in range(numFaces):
            face = faces[i]
            AiArraySetUInt(nsides, i, len(face.vertices))
        AiNodeSetArray(self.amesh,b"nsides",nsides)
       
        # IDs of each vertex
        numindex = 0
        for i in faces:
            numindex += len(i.vertices)

        vidxs = AiArrayAllocate(numindex, 1, AI_TYPE_UINT)
        count = 0
        for i in range(numFaces):
            face = faces[i]
            for j in face.vertices:
                AiArraySetUInt(vidxs, count, j.numerator)
                count +=1
        AiNodeSetArray(self.amesh,b"vidxs",vidxs)

        vlist = AiArrayAllocate(numVerts,1,AI_TYPE_POINT)
        for i in range(numVerts):
            vertex = vertices[i].co
            AiArraySetPnt(vlist,i,AtPoint(vertex.x,vertex.y,vertex.z))
        AiNodeSetArray(self.amesh,b"vlist",vlist)
        
        # uvs
        if len(self.meshdata.uv_textures) > 0:
            uvset = self.meshdata.uv_textures[0]
            numuv = len(uvset.data[0].uv)
            uvidxs = AiArrayAllocate(numuv,1,AI_TYPE_UINT)
            uvlist = AiArrayAllocate(numuv,1,AI_TYPE_POINT2)
            for i in range(numuv):
                AiArraySetUInt(uvidxs,i,i)
                AiArraySetPnt2(uvlist,i,AtPoint2(uvset.data[0].uv[i][0],uvset.data[0].uv[i][1]))
            AiNodeSetArray(self.amesh,b"uvidxs",uvidxs)
            AiNodeSetArray(self.amesh,b"uvlist",uvlist)

        # write the matrix
        mmatrix =self.mesh.matrix_world
        matrix = utils.getYUpMatrix(mmatrix)
        positions = AiArrayAllocate(1,1,AI_TYPE_MATRIX)
        AiArraySetMtx(positions,0,matrix)
        AiNodeSetArray(self.amesh,b'matrix',positions)

        # Material
        for mat in self.meshdata.materials:
            matid = mat.as_pointer()
            if matid in self.materials.materialDict.keys():
                AiNodeSetPtr(self.amesh,b"shader",self.materials.materialDict[matid])
        # Sub surface
        if self.subsurf != False:
            AiNodeSetInt(self.amesh,b"subdiv_type",1)
            AiNodeSetInt(self.amesh,b"subdiv_iterations",self.subsurf.render_levels)
            self.subsurf.show_render = True


        # delete data block if modifiers applied
        if self.mustCleanup:
            bpy.data.meshes.remove(self.meshdata)

