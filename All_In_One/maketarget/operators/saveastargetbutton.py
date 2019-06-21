import bpy
from ..utils import *
from ..error import *
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper
from ..maketarget import doSaveTarget

class VIEW3D_OT_SaveasTargetButton(bpy.types.Operator, ExportHelper):
    bl_idname = "mh.saveas_target"
    bl_label = "Save Target As"
    bl_description = "Save target(s) to new file. If Active Only is selected, only save the last target, otherwise save the sum of all targets"
    bl_options = {'UNDO'}

    filename_ext = ".target"
    filter_glob = StringProperty(default="*.target", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
        name="File Path",
        description="File path used for target file",
        maxlen= 1024, default= "")

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        setObjectMode(context)
        try:
            doSaveTarget(context, self.properties.filepath)
        except MHError:
            handleMHError(context)
        print("Target saved")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}