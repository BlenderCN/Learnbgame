import bpy
from ..utils import *
from ..error import *
from bpy.props import *

def fixInconsistency(context):
    ob = context.object
    if ob.data.shape_keys:
        ob["NTargets"] = len(ob.data.shape_keys.key_blocks)
    else:
        ob.shape_key_add(name="Basis")
        ob["NTargets"] = 0

class VIEW3D_OT_FixInconsistencyButton(bpy.types.Operator):
    bl_idname = "mh.fix_inconsistency"
    bl_label = "Fix It!"
    bl_description = "Due to a bug, the target stack has become corrupt. Fix it."
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            setObjectMode(context)
            fixInconsistency(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}