
import bpy

from . import level
from . import ogf


def menu_func_import(self, context):

    self.layout.operator(
        level.operator.StalkerImportLevelOperator.bl_idname,
        text='X-Ray level (level)'
    )

    self.layout.operator(
        ogf.operator.StalkerImportOGFOperator.bl_idname,
        text='X-Ray game object (.ogf)'
    )


def register():
    bpy.utils.register_class(level.operator.StalkerImportLevelOperator)
    bpy.utils.register_class(ogf.operator.StalkerImportOGFOperator)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(ogf.operator.StalkerImportOGFOperator)
    bpy.utils.unregister_class(level.operator.StalkerImportLevelOperator)
