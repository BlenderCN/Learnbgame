import os
import bpy
from .. import utils as ut


class PackBdxProject(bpy.types.Operator):
    """Create a packed copy of the BDX blend"""
    bl_idname = "object.packproj"
    bl_label = "Create packed BDX blend"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        self.filepath = "packedgame.blend"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        # save file (so we don't lose data when we reload below)
        bpy.ops.wm.save_mainfile()

        # load in audio
        j = os.path.join

        audio_dir = j(ut.project_root(), "android", "assets", "bdx", "audio")
        sounds = ut.listdir(j(audio_dir, "sounds"))
        music = ut.listdir(j(audio_dir, "music"))

        file_ext = lambda fp: fp.split('.')[-1]

        audio = [fp for fp in sounds + music 
                 if file_ext(fp) in ("wav", "mp3", "ogg")]

        for fp in audio:
            bpy.ops.sound.open(filepath=fp)

        # pack
        bpy.ops.file.pack_all()

        # save copy of blend, containing freshly packed resources
        bpy.ops.wm.save_as_mainfile(copy=True, filepath=self.filepath)

        # reload (a clean way to "undo" the pack, and keep working file clean)
        bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(PackBdxProject)


def unregister():
    bpy.utils.unregister_class(PackBdxProject)
