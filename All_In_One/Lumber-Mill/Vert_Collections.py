"""----------------------------------------------------

Create mesh

----------------------------------------------------"""

import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper
from mathutils import Vector

from Lumber_Mill_add_on import Lumber_Mill # working
from Lumber_Mill_add_on import Estimator


# add mesh code---------------------------------------------------

def add_object(self, context):

    # scale of 1 in blender Imperial units is a foot
    inch = 1 / 12

    #unitScale = 3.28125 = 26.25 / 8
    #           where 26' 3" is what blender will use as an 8' length imperial
    if bpy.context.scene.unit_settings.system == "IMPERIAL": #error
        unitScale = 3.2810409 #adjusted
        scale_x = self.scale.x / unitScale
        scale_y = self.scale.y / unitScale
        scale_z = self.scale.z / unitScale
    elif bpy.context.scene.unit_settings.system == "METRIC" or "NONE":
        scale_x = self.scale.x
        scale_y = self.scale.y
        scale_z = self.scale.z

    length = Lumber_Mill.length
    width  = Lumber_Mill.width
    height = Lumber_Mill.height

    # x,y,z format  # Vector(( * scale_x,  * scale_y, ))
    verts = [Vector((-length * scale_x,  (inch * width) * scale_y, -(inch * height) * scale_z)),      #0
             Vector(( length * scale_x,  (inch * width) * scale_y, -(inch * height) * scale_z)),      #1
             Vector(( length * scale_x, -(inch * width) * scale_y, -(inch * height) * scale_z)),      #2
             Vector((-length * scale_x, -(inch * width) * scale_y, -(inch * height) * scale_z)),      #3
             Vector((-length * scale_x,  (inch * width) * scale_y,  (inch * height) * scale_z)),      #4
             Vector(( length * scale_x,  (inch * width) * scale_y,  (inch * height) * scale_z)),      #5
             Vector(( length * scale_x, -(inch * width) * scale_y,  (inch * height) * scale_z)),      #6
             Vector((-length * scale_x, -(inch * width) * scale_y,  (inch * height) * scale_z)),      #7
            ]

    edges = [(0, 1), (1, 2), (2, 3), (3, 0),
             (0, 4), (1, 5), (2, 6), (3, 7),
             (4, 5), (5, 6), (6, 7), (7, 4)
            ]

    faces = [[0, 1, 2, 3],
             [0, 1, 5, 4],
             [1, 2, 6, 5],
             [2, 3, 7, 6],
             [0, 3, 7, 4],
             [4, 5, 6, 7]
            ]
    """
    Vertex Layout

        4 ------------5
    7---|----------6  |
    |   0----------|--1
    3--------------2

    Edges:
    - edges labeled from 0 clockwise to 3 and back to 0
    - next is vertical edges from bottom to top starting at (0,4)
        clockwise
    - top edges like the bottom plane start at 4 and go clockwise
        to 7 and back to 4
    Faces:
    - first face is botton plane same 0 to 0 clockwise fasion as edges
        as view from inside of polygon facing out and down
    - the vertical planes start in the back from 0 to 4 clockwise facing
        the plane from the outside
    - this same pattern follows clockwise around the polygon as viewed from
        the top
    - the last face is 4 to 4 clockwise facing down on the polygon from
        the outside
    """
    mesh_data = bpy.data.meshes.new(name ="Lumber")
    mesh_data.from_pydata(verts, edges, faces)
    mesh_data.update()

    #the string argument below is what the object gets named as
    #this needs to be dynamic also
    obj_name = Lumber_Mill.obj_string1 + Lumber_Mill.obj_string2
    obj = bpy.data.objects.new(obj_name, mesh_data)

    scene = bpy.context.scene
    scene.objects.link(obj)
    bpy.context.scene.objects.active = obj
    obj.select = True


# makes add mesh code accessible as a button------------------------------

class OBJECT_OT_add_object(Operator, AddObjectHelper):
    """Create Dimensional Lumber"""
    bl_idname = "mesh.add_object"
    bl_label = "Add Lumber"
    bl_options = {'REGISTER', 'UNDO'}

    scale = FloatVectorProperty(
            name="scale",
            default=(1.0, 1.0, 1.0),
            subtype='TRANSLATION',
            description="scaling",
            )

    def execute(self, context):
        add_object(self, context)

        string = Lumber_Mill.obj_string1 + Lumber_Mill.obj_string2
        if string not in Estimator.boardNames:
            Estimator.boardNames.append(string)

        #testing code
        dimensions = [Lumber_Mill.width * 2, Lumber_Mill.height * 2,
                      Lumber_Mill.length * 2]
        for value in dimensions:
            print(value)
        # end testing

        return {'FINISHED'}
