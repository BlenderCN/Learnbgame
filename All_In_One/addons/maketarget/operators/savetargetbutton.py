import bpy
from ..utils import *
from ..error import *
from bpy.props import StringProperty
from ..maketarget import doSaveTarget

class VIEW3D_OT_SaveTargetButton(bpy.types.Operator):
    bl_idname = "mh.save_target"
    bl_label = "Save Target"
    bl_description = "Save target(s), overwriting existing file. If Active Only is selected, only save the last target, otherwise save the sum of all targets"
    bl_options = {'UNDO'}

    filepath = StringProperty(default="")

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        setObjectMode(context)
        try:
            doSaveTarget(context, self.filepath)
            print("Target saved")
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

    def invoke(self, context, event):
        return invokeWithFileCheck(self, context, context.object["FilePath"])

    def draw(self, context):
        drawFileCheck(self)

