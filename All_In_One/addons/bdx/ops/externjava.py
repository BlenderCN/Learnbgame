import os
import bpy
from .. import utils as ut


class ExternJava(bpy.types.Operator):
    """Make internal java files external"""
    bl_idname = "object.externjava"
    bl_label = "Make internal java files external"

    def execute(self, context):
        ut.save_internal_java_files(ut.src_root(), overwrite=True)

        # Delete internal java texts
        for t in bpy.data.texts:
            if t.name.endswith(".java"):
                bpy.data.texts.remove(t)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ExternJava)


def unregister():
    bpy.utils.unregister_class(ExternJava)
