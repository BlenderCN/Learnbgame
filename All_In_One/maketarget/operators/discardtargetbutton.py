import bpy
from ..utils import *
from ..error import *
from bpy.props import *
from ..maketarget import discardTarget

class VIEW3D_OT_DiscardTargetButton(bpy.types.Operator):

    bl_idname = "mh.discard_target"
    bl_label = "Discard Target"
    bl_description = "Remove the active target and make the second last active"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        try:
            setObjectMode(context)
            discardTarget(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}