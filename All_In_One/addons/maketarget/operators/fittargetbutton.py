import bpy
from ..utils import *
from ..error import *
from bpy.props import *
from ..maketarget import fitTarget

class VIEW3D_OT_FitTargetButton(bpy.types.Operator):
    bl_idname = "mh.fit_target"
    bl_label = "Fit Target"
    bl_description = "Fit clothes to character"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return (not context.object.MhMeshVertsDeleted)

    def execute(self, context):
        try:
            setObjectMode(context)
            fitTarget(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

