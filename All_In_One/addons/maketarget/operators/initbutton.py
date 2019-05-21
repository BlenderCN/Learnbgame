import bpy
from ..utils import *
from ..error import *
from bpy.props import *

class VIEW3D_OT_InitButton(bpy.types.Operator):
    bl_idname = "mh.init"
    bl_label = "Initialize"
    bl_description = ""
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        #initScene(context.scene)
        return{'FINISHED'}