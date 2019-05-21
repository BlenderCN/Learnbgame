import bpy
from ..utils import *
from ..error import *
from bpy.props import *
from ..maketarget import batchFitTargets

class VIEW3D_OT_BatchFitButton(bpy.types.Operator):
    bl_idname = "mh.batch_fit"
    bl_label = "Batch Fit Targets"
    bl_description = "Fit all targets in directory"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        global TargetSubPaths
        setObjectMode(context)
        scn = context.scene
        folder = os.path.realpath(os.path.expanduser(scn.MhTargetPath))
        batchFitTargets(context, folder)
        print("All targets fited")
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200, height=20)

    def draw(self, context):
        self.layout.label("Really batch fit targets?")