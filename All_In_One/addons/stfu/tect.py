import bpy
import bmesh
import random

from mathutils import Vector
from .shared import randomOnUnitSphere

class Tectonics:
    
    def __init__(self, nPlates):
        mesh = bmesh.new()
        # random points on unit sphere as plate centers
        origVerts = []
        for _ in range(nPlates):
            origVerts.append( mesh.verts.new(randomOnUnitSphere()) )
        
        # the convex hull forms a delaunay triangulation
        bmesh.ops.convex_hull(mesh, input=mesh.verts)
        # ... from which we construct the voronoi cells
        for vert in origVerts:
            newVerts = []
            loop = loop0 = vert.link_loops[0]
            while True:
                newVerts.append( mesh.verts.new(circumCenter(loop.face)) )
                loop = loop.link_loop_prev.link_loop_radial_next
                if loop == loop0:
                    break
            mesh.faces.new(newVerts)
        
        # misc cleanup
        for vert in origVerts:
            mesh.verts.remove(vert)
        bmesh.ops.remove_doubles(mesh, verts=mesh.verts)
        for vert in mesh.verts:
            vert.co.normalize()
        
        # assign plate movements, by choosing an edge as direction  
        # and plate ground levels randomly
        mesh.faces.index_update()
        self.movements = [None] * len(mesh.faces)
        self.groundLevels = [None] * len(mesh.faces)
        for f in mesh.faces:
            self.movements[f.index] = random.choice(f.edges)
            self.groundLevels[f.index] = random.choice((-.01, +.01))
        
        # save both regular mesh and bmesh
        self.bmesh = mesh
        self.mesh = bpy.data.meshes.new("tectonics")
        self.bmesh.to_mesh(self.mesh)
        
    def classifyEdge(self, edge):
        """
        Returns a dict with properties of the BMEdge.
        'collision': [-1,1]
            Values below 0 mean plates move away from one another.
            Values above 0 mean plates move towards each other.
        'shear': [0,1]
            A shear value of 1 indicates plates moving parallel to the edge, but in opposite directions.
        """
        def faceMovement(face): # movement vector in face plane
            fcenter = center(face)
            return ( center(self.movements[face.index]) - fcenter ).normalized() 
            
        def shear(face):
            shearVec = ( edge.verts[0].co - edge.verts[1].co ).normalized()
            return faceMovement(face).dot(shearVec)
        
        def collision(face):
            collVec = ( center(edge) - center(face) ).normalized() # vector towards edge
            return faceMovement(face).dot(collVec)
        
        assert len(edge.link_faces) == 2, len(edge.link_faces)
        faceAverage = lambda func: sum( map(func, edge.link_faces) ) / 2
        
        return {"shear" : abs( shear(edge.link_faces[0]) - shear(edge.link_faces[1]) ) / 2,
                "collision" : faceAverage(collision)}
    
    def linkMeshToScene(self, context):
        obj = bpy.data.objects.new(self.mesh.name, self.mesh)
        context.scene.objects.link(obj)
        bpy.ops.object.select_all(action = "DESELECT")
        obj.select = True
        context.scene.objects.active = obj

#############################################

def center(BMObj):
    return sum((v.co for v in BMObj.verts), Vector()) / len(BMObj.verts)

def circumCenter(face):
    "https://en.wikipedia.org/wiki/Circumscribed_circle#Higher_dimensions"
    assert len(face.verts) == 3
    b = face.verts[0].co - face.verts[2].co
    a = face.verts[1].co - face.verts[2].co
    return (a.length_squared * b - b.length_squared * a).cross(a.cross(b)) / (2 * a.cross(b).length_squared) + face.verts[2].co

#############################################

class TectonicsOp(bpy.types.Operator):
    bl_idname = "mesh.stfu_tect"
    bl_label = "Random Tectonics"
    bl_options = {"REGISTER", "UNDO"}
    
    nPlates = bpy.props.IntProperty(
        name        = "Plates",
        description = "Number of tectonic plates",
        default     = 25,
        min         = 4, soft_min = 8
    )
    
    def execute(self, context):
        t = Tectonics(self.nPlates)
        t.linkMeshToScene(context)
        t.bmesh.free()
        return {'FINISHED'}
