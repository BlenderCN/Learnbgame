import bpy
from ..utils import *
from ..error import *
from bpy.props import *
from .. import utils
from ..maketarget import discardTarget

def discardAllTargets(context):
    ob = context.object
    while utils.isTarget(ob):
        discardTarget(context)
    return

class VIEW3D_OT_DiscardAllTargetsButton(bpy.types.Operator):
    bl_idname = "mh.discard_all_targets"
    bl_label = "Discard All Targets"
    bl_description = "Discard all targets in the target stack"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        try:
            setObjectMode(context)
            discardAllTargets(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}