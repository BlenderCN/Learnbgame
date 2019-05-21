bl_info = {
    "name": "AIFOV",
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
from bpy.types import Operator
from bpy.props import FloatProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
from math import acos, atan, cos, sin, sqrt, pi, pow
import numpy as np
#
def add_object(self, context):
    verts = []
    edges = []
    faces = []
    
    errorOffset = Vector((0.02, 0.02, 0.02))
    
    AI_X = self.AIRadius * cos(self.AIAngle)
    AI_Y = self.AIRadius * sin(self.AIAngle)
    
    AIV = Vector((AI_X, AI_Y, 0))
    
    
    Player_X = self.PlayerDistance * cos(self.PlayerAngle)
    Player_Y = self.PlayerDistance * sin(self.PlayerAngle)
    
    PV = Vector((Player_X, Player_Y, 0))
    
    try:
        AngularDistance = acos((AIV.dot(PV)/(self.AIRadius * self.PlayerDistance)))*180/pi
    except ValueError:
        AIV -= errorOffset
        AngularDistance = acos((AIV.dot(PV)/(self.AIRadius * self.PlayerDistance)))*180/pi

    print("Angular Distance: ", AngularDistance-self.AIFOV)
    Total_X = AI_X + Player_X
    Total_Y = AI_Y + Player_Y
    

    AIFOV_LX = self.AIRadius*cos(self.AIAngle + self.AIFOV)
    AIFOV_LY = self.AIRadius*sin(self.AIAngle + self.AIFOV)
    AIFOV_RX = self.AIRadius*cos(self.AIAngle - self.AIFOV)
    AIFOV_RY = self.AIRadius*sin(self.AIAngle - self.AIFOV)

    verts.append(Vector((0,0,0)))
    
    verts.append(Vector((AIFOV_LX, AIFOV_LY, 0)))
    verts.append(Vector((AIFOV_RX, AIFOV_RY, 0)))
    edges.append([0,1])
    edges.append([1,2])
    edges.append([2,0])
    
    verts.append(Vector((Player_X, Player_Y, 0)))
    edges.append([0, len(verts)-1])


    if(AngularDistance-self.AIFOV*180/pi <= 0 and self.AIRadius >= self.PlayerDistance):
        faces.append([2,1,0])
    
    mesh = bpy.data.meshes.new(name="New Object Mesh")
    mesh.from_pydata(verts, edges, faces)
    object_data_add(context, mesh, operator=self)

def selection(x):
    print(x)

class OBJECT_OT_add_object(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_object"
    bl_label = "2D Vectors"
    bl_options = {'REGISTER', 'UNDO'}
    
    AIRadius = FloatProperty(
              name = "Vision Range",
              default = 20,
              precision = 6,
              subtype = 'DISTANCE',
              description = "AI Vision Range",)
    
    AIFOV = FloatProperty(
            name = "AI Field of Vision",
            default = 30*pi/180,
            precision = 6,
            subtype = 'ANGLE',
            description = 'AI Field of Vision',)
              
    AIAngle = FloatProperty(
          name = "Enemy Vision Angle",
          default = 90*pi/180,
          precision = 6,
          step = 100,
          subtype = 'ANGLE',
          description = 'AI Vision Angle',)
          
    PlayerDistance = FloatProperty(
             name = "Player Distance",
             default = 20,
             precision = 6,
             subtype = 'DISTANCE',
             description = "Player's distance from AI",
             )
    PlayerAngle = FloatProperty(
                  name = "Player Angle",
                  default = 0,
                  step = 100,
                  precision = 6,
                  subtype = 'ANGLE',
                  description = "Player's angle from the AI",)
             
    def execute(self, context):
        add_object(self, context)
        return {'FINISHED'}


# Registration

def add_object_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_object.bl_idname,
        text="2D Vector Addition",
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
