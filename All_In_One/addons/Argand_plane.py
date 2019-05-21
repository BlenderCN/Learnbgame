bl_info = {
    "name": "Rotational math",
    "author": "40N91",
    "version": (1, 0),
    "blender": (2, 75, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Adds a new Mesh Object",
    "warning": "",
    "wiki_url": "",
    "category": "Add Mesh",
    }


import bpy
import numpy as np
from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
from math import *

#Notes on how to add/subtract and multiply/divide imaginary numbers and convert them to polar and cartesian forms,
#and how imaginary numbers are used in rotational math.

class cpol:
    def __init__(self, a):
        if(type(a)== complex):
            self.mod = sqrt( pow(a.real, 2) + pow(a.imag, 2) )
            self.arg = atan( a.imag / a.real ) * 180 / pi
            
            if( a.real > 0 and a.imag > 0 ):
                self.arg = self.arg
                
            if( a.real < 0 ):
                self.arg = 180 + self.arg
                
            if( a.real > 0 and a.imag < 0):
                self.arg = 360 + self.arg

        elif(type(a) == tuple):
            self.mod = a[0]
            self.arg = a[1]
            
            if( self.mod > 0 and self.arg > 0 ):
                self.arg = self.arg
                
            if( self.mod < 0 ):
                self.arg = 180 + self.arg
                
            if( self.mod > 0 and self.arg < 0):
                self.arg = 360 + self.arg
                
        else:
            print("Invalid arguments")
            return

    def __repr__(self):
        return("%s∠%s"%(self.mod, self.arg))

    def __mul__(self, other):
        return(cpol((self.mod * other.mod, self.arg + other.arg)))

    def __truediv__(self, other):
        return( cpol((self.mod/other.mod, self.arg-other.arg)))

    def cart(self):
        return( self.mod*cos(self.arg*pi/180) +
              ( self.mod*sin(self.arg*pi/180) * 1j ))

    def __add__(self, other):
        return(cpol(self.cart() + other.cart()))

    def __sub__(self, other):
        return(cpol(self.cart() - other.cart()))
    
def add_object(self, context):

    rot = self.rot
    radius = self.radius
    
    rotor = cpol((radius, rot*180/pi))
    
    
    rot_mat = np.array([[ 1+1j, -1+1j],[-1-1j, 1-1j]]) * radius 
    #Points of argand plane
    
    rot_mat = rot_mat * rotor.cart()
    verts = []
    
    angles = []
    for x in range(0, int(sqrt(rot_mat.size)) ):
        for y in range(0, int(sqrt(rot_mat.size))):
            a = rot_mat[x,y]
            real = a.real
            imag = a.imag
            
            verts.append(Vector((real, imag, 0)))
    
    verts.append(verts[0]*2)

    edges = []

    faces = [[0,1,2,3], [0,4]]

    

    mesh = bpy.data.meshes.new(name="New Object Mesh")
    mesh.from_pydata(verts, edges, faces)
    object_data_add(context, mesh, operator=self)


class OBJECT_OT_add_object(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_object"
    bl_label = "Add Mesh Object"
    bl_options = {'REGISTER', 'UNDO'}

    radius = FloatProperty(
                name = "radius",
                default = 1,
                precision = 6,
                subtype = 'NONE',
                description = 'radius',)
                
    rot = FloatProperty(
            name="rotation",
            default = 0,
            precision = 6,
            step = 100,
            subtype='ANGLE',
            description="rotation",
            )
    
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
