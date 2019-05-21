bl_info = {
    "name": "Linear Transformation example",
    "author": "4ON91",
    "version": (1, 0),
    "blender": (2, 75, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Adds a new Mesh Object",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh",
    }


import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty, FloatProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
from math import *
import numpy as np

class Joint:
    def __init__(self, Joint):
        self.Radius = Joint[0]
        self.Angle = Joint[1] * pi/180
        
        self.X = cos(self.Angle) * self.Radius
        self.Y = sin(self.Angle) * self.Radius
        
        self.RotMat = np.array([
            [cos(self.Angle), -sin(self.Angle), 0],
            [sin(self.Angle),  cos(self.Angle), 0],
            [              0,                0, 1]])
        self.LocMat = np.array([
            [1, 0, self.X],
            [0, 1, self.Y],
            [0, 0,      1]])
        
        #Not commutative
        self.LR = np.matmul(self.LocMat, self.RotMat)
        
        #The point in homogeneous coordinates
        self.HC = [self.X, self.Y, 1]
        
def add_object(self, context):
    print("\n"*10)
    verts = []
    edges = []
    faces = []
    
    A = Joint( self.Joint1 )
    B = Joint( self.Joint2 )
    C = Joint( self.Joint3 )
    D = Joint( self.Joint4 )
    E = Joint( self.Joint5 )
    
    #By using matrices, you can put each point into its own frame. 
    ABMat = np.matmul(A.LR,B.LR)
    A_   = [x for x in A.HC[:2]] + [0]
    AB  = [x for x in ABMat[:,2][:2]] + [0]
    
    ABCMat = np.matmul(ABMat, C.LR)
    ABC = [x for x in ABCMat[:,2][:2]] + [0]
    
    ABCDMat = np.matmul(ABCMat, D.LR)
    ABCD = [x for x in ABCDMat[:,2][:2]] + [0]
    
    ABCDE = [x for x in np.inner(ABCDMat, E.HC)[:2]] + [0]
    
    
    verts.append(Vector((0,0,0)))
    verts.append(Vector(A_))
    verts.append(Vector(AB))
    verts.append(Vector(ABC))
    verts.append(Vector(ABCD))
    verts.append(Vector(ABCDE))
    edges.append([0,1])
    edges.append([1,2])
    edges.append([2,3])
    edges.append([3,4])
    edges.append([4,5])
    
    mesh = bpy.data.meshes.new(name="New Object Mesh")
    mesh.from_pydata(verts, edges, faces)
    # useful for development when the mesh may be invalid.
    # mesh.validate(verbose=True)
    object_data_add(context, mesh, operator=self)


class OBJECT_OT_add_object(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_object"
    bl_label = "Add Mesh Object"
    bl_options = {'REGISTER', 'UNDO'}
    
    Joint1 = FloatVectorProperty(
        name = "Joint.001",
        default = (5,45),
        size = 2,
        precision = 6)
    
    Joint2 = FloatVectorProperty(
        name = "Joint.002",
        default = (4,45),
        size = 2,
        precision = 6)
    
    Joint3 = FloatVectorProperty(
        name = "Joint.003",
        default = (3,45),
        size = 2,
        precision = 6)
    
    Joint4 = FloatVectorProperty(
        name = "Joint.004",
        default = (2,45),
        size = 2,
        precision = 6)

    Joint5 = FloatVectorProperty(
        name = "Joint.005",
        default = (1,45),
        size = 2,
        precision = 6)
        
    def execute(self, context):

        add_object(self, context)

        return {'FINISHED'}


# Registration

def add_object_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_object.bl_idname,
        text="Add Object",
        icon='PLUGIN')


# This allows you to right click on a button and link to the manual
def add_object_manual_map():
    url_manual_prefix = "https://docs.blender.org/manual/en/dev/"
    url_manual_mapping = (
        ("bpy.ops.mesh.add_object", "editors/3dview/object"),
        )
    return url_manual_prefix, url_manual_mapping


def register():
    bpy.utils.register_class(OBJECT_OT_add_object)
    bpy.utils.register_manual_map(add_object_manual_map)
    bpy.types.INFO_MT_mesh_add.append(add_object_button)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_object)
    bpy.utils.unregister_manual_map(add_object_manual_map)
    bpy.types.INFO_MT_mesh_add.remove(add_object_button)


if __name__ == "__main__":
    register()
