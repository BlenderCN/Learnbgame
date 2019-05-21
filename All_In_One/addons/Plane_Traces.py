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
from math import *
from bpy.types import Operator
from bpy.props import FloatVectorProperty, FloatProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector


def add_object(self, context):
    verts = []
    edges = []
    faces = []
    
    Eq = self.AxByCz
    D = int(self.D)
    Range = int(self.Range)
    #Where equation of the plane is
    #-2x + 3y + 1z - 6
    #-2x = -3y - 1z + 6
    #x = (3/2)y + (1/2)z - (6/2)
    # 3y = 2x - 1z + 6
    # y = (2x/3) - (1z/3) + (6/3)
    #Ax + By + Cz = D
    #By = -Ax - Cz + D
    #y = -(A/B)x - (C/B)z + (D/B)
 
    """
    for x in range(-D, D+1, 1):
        for z in range(-D, D+1, 1):
            y = (2*x)/3 - (1*z)/3 + 6/3
            verts.append(Vector((x, y, z)))
    """ 
    """
    [0,1,5,6]
    
    """
    for x in range(-Range, Range+1, 1):
        for z in range(-Range, Range+1, 1):
            y = ( -(Eq[0]*x)/Eq[1]) - (Eq[2]*z/Eq[1]) + D/Eq[1]
            verts.append(Vector((x, y, z)))
            #y = -x - z + 4
            #1y = -(x/1) - (z/1) + 4
    a = 1
    c = Range*2+1
    for x in range(1, len(verts)-(c)):
        a = x
        if(a%(c)==0):
            a+=1
        faces.append([a, a-1, a+c-1, a+c])
        #faces.append([a+c, a+c-1, a-1,a  ])
        
    mesh = bpy.data.meshes.new(name="Plane Equation")
    mesh.from_pydata(verts, edges, faces)
    object_data_add(context, mesh, operator=self)


class OBJECT_OT_add_object(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_object"
    bl_label = "Add Mesh Object"
    bl_options = {'REGISTER', 'UNDO'}

    AxByCz = FloatVectorProperty(
        name = "Plane Equation",
        default = (3,-9, 2),
        precision = 6,
        description = 'The equation of a plane',)
    
    D = FloatProperty( 
        name = "D", 
        default = 9,
        precision = 6,
        description = 'Plane is equal to...',)
        
    Range = FloatProperty(
        name = "Range",
        default = 10,
        precision = 6,
        description = "How long the plane should extend to",)
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
