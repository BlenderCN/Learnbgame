import bpy
from ..utils import *
from ..error import *
from bpy.props import *
from ..maketarget import applyTargets

class VIEW3D_OT_ApplyTargetsButton(bpy.types.Operator):
    bl_idname = "mh.apply_targets"
    bl_label = "Apply Targets"
    bl_description = "Apply all shapekeys to mesh"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        try:
            setObjectMode(context)
            applyTargets(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}