"""------------------------------------------------------

Create a list of necessary lumber (actual lumber not bd ft)
    give cost based on actual lumber list and input costs
    
------------------------------------------------------"""

import bpy
import bmesh
from bpy.types import Operator


# globals---------------------------------------

global boards
boards = []
global boardLengths
boardLengths = []
global boardNames
boardNames = []


def get_board_lengths (self, context):
    # make sure no objects are selected first--------
    for unselect in bpy.data.objects:
        bpy.data.objects[unselect.name].select = False

    n = 0
    for obj in bpy.data.objects:
        string = ".00%s" % str(n)
        #print (string) #testing

        # make dynamic
        for name_string in boardNames:
            if obj.name == name_string or obj.name == name_string + string:
                print ("%s added to boards" % obj.name)
                boards.append(obj.name)
                n += 1
            else:
                #print ("%s not added to boards" % obj.name)
                n += 1

    # cycle through the board list and get longest edge of each
    for name in boards:
       bpy.context.scene.objects.active = bpy.data.objects[name]
       bpy.data.objects[name].select = True
       bpy.ops.object.mode_set(mode='EDIT')

       obj = bpy.data.objects[name]
       bm = bmesh.from_edit_mesh(obj.data)

       edges = []
       for edge in bm.edges:
           # test bm.edges[] and calc_length are correct
           #print(edge.calc_length())
           unitScale = 3.2810409
           if bpy.context.scene.unit_settings.system == "IMPERIAL":
               edges.append(edge.calc_length() * unitScale)

           if bpy.context.scene.unit_settings.system == "METRIC" or "NONE":
               edges.append(edge.calc_length())

       # test edges is populated correctly
       # for e in edges:
       # print (e)

       longest_edge = max(edges)
       boardLengths.append(longest_edge)

       bpy.ops.object.mode_set(mode='OBJECT')
       bpy.data.objects[name].select = False
       bmesh.types.BMesh.free

# makes add mesh code accessible as a button------------------------------

class OBJECT_OT_get_board_lengths(Operator):
    """Create Dimensional Lumber"""
    bl_idname = "get.board_lengths"
    bl_label = "Calculate Board Lengths"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        get_board_lengths(self, context)
        for length in boardLengths:
                print(length)
        boards.clear()
        boardLengths.clear()

        return {'FINISHED'}
