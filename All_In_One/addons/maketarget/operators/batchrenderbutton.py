import bpy
from ..utils import *
from ..error import *
from bpy.props import BoolProperty
from ..maketarget import batchRenderTargets

class VIEW3D_OT_BatchRenderButton(bpy.types.Operator):
    bl_idname = "mh.batch_render"
    bl_label = "Batch Render"
    bl_description = "Render all targets in directory"
    bl_options = {'UNDO'}
    opengl = BoolProperty()

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        global TargetSubPaths
        setObjectMode(context)
        scn = context.scene
        folder = os.path.expanduser(scn.MhTargetPath)
        outdir = os.path.join(getMHBlenderDirectory(), "pictures/")
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        scn.frame_start = 1
        scn.frame_end = 1
        for subfolder in TargetSubPaths:
            if scn["Mh%s" % subfolder]:
                batchRenderTargets(context, os.path.join(folder, subfolder), self.opengl, outdir)
        print("All targets rendered")
        return {'FINISHED'}