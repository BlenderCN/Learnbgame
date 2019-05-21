bl_info = {
    "name": "New Object",
    "author": "Your Name Here",
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
from sympy import *
from math import *
from bpy.types import Operator
from bpy.props import FloatProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector


def add_object(self, context):
    verts = []
    edges = []
    faces = []

    
    precision   = self.precision

    enum_x = np.linspace(-self.limit_x, self.limit_x, num = self.limit_x*2*self.precision+1, retstep = True)
    enum_x = enum_x[0]
    
    enum_y = np.linspace(-self.limit_y, self.limit_y, num = self.limit_y*2*self.precision+1, retstep = True)
    enum_y = enum_y[0]
    
    enum_z = np.linspace(-self.limit_z, self.limit_z, num = self.limit_z*2*self.precision+1, retstep = True)
    enum_z = enum_z[0]

    for x in range(0, len(enum_x)):
        for z in range(0, len(enum_z)):
            X = enum_x[x]
            Z = enum_z[z]
    
            try:
                Y = sqrt(-pow(X/5, 2) - pow(Z/9, 2) + 1 ) * 7
            except ValueError:
                continue
                
            
            verts.append(Vector(( X, Y, Z)))
            verts.append(Vector((-X,-Y,-Z)))
        

    for y in range(0, len(enum_y)):
        for z in range(0, len(enum_z)):
            Y = enum_y[y]
            Z = enum_z[z]
            
            try:
                X = sqrt(-pow(Y/7, 2) - pow(Z/9, 2) + 1) * 5
            except ValueError:
                continue
            verts.append(Vector(( X, Y, Z)))
            verts.append(Vector((-X,-Y,-Z)))
    

    for x in range(0, len(enum_x)):
        for y in range(0, len(enum_y)):
            X = enum_x[x]
            Y = enum_y[y]
            
            try:
                Z = sqrt(-pow(X/5, 2) - pow(Y/7, 2) + 1)*9
            except ValueError:
                continue
            verts.append(Vector(( X,  Y,  Z)))
            verts.append(Vector((-X, -Y, -Z)))
    
    mesh = bpy.data.meshes.new(name="New Object Mesh")
    mesh.from_pydata(verts, edges, faces)
    object_data_add(context, mesh, operator=self)


class OBJECT_OT_add_object(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_object"
    bl_label = "Add Mesh Object"
    bl_options = {'REGISTER', 'UNDO'}

    precision = FloatProperty(
        name = "Precision",
        default = 10,
        precision = 6,
        min = 1,
        )
    
    limit_x = FloatProperty(
        name = "Limit X",
        precision = 6,
        min = 0,
        default = 5,)
        
    limit_y = FloatProperty(
        name = "Limit Y",
        precision = 6,
        min = 0,
        default = 0,)
        
    limit_z = FloatProperty(
        name = "Limit Z",
        precision = 6,
        min = 0,
        default = 9,)
        
    def execute(self, context):

        add_object(self, context)

        return {'FINISHED'}


# Registration

def add_object_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_object.bl_idname,
        text="Trace Plane",
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
