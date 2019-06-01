import bpy
from ..utils import *
from ..error import *
from bpy.props import StringProperty
from ..maketarget import getSettings
from .. import utils

def loadTargetFile(context, filepath):
    global Comments
    setObjectMode(context)
    ob = context.object
    settings = getSettings(ob)
    if ob.MhMeshVertsDeleted:
        _,Comments = utils.loadTarget(
            filepath,
            context,
            irrelevant=settings.irrelevantVerts[ob.MhAffectOnly],
            offset=settings.offsetVerts[ob.MhAffectOnly])
    else:
        _,Comments = utils.loadTarget(filepath, context)

class VIEW3D_OT_LoadTargetButton(bpy.types.Operator):
    bl_idname = "mh.load_target"
    bl_label = "Load Target File"
    bl_description = "Load a target file"
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
        try:
            loadTargetFile(context, self.properties.filepath)
        except MHError:
            handleMHError(context)
        print("Target loaded")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}