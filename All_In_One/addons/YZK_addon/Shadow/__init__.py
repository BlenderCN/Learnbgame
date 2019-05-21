#
# @file    tools/plugin/blender/Shadow/__init__.py
# @author  Luke Tokheim, luke@motionshadow.com
# @version 2.5
#
# (C) Copyright Motion Workshop 2017. All rights reserved.
#
# The coded instructions, statements, computer programs, and/or related
# material (collectively the "Data") in these files contain unpublished
# information proprietary to Motion Workshop, which is protected by
# US federal copyright law and by international treaties.
#
# The Data may not be disclosed or distributed to third parties, in whole
# or in part, without the prior written consent of Motion Workshop.
#
# The Data is provided "as is" without express or implied warranty, and
# with no claim as to its suitability for any purpose.
#

from .mDevice import ModalOperator
from .mPanel import LuaOperator, ImportOperator, ShadowPanel
from .mImportAnim import ImportAnimOperator

import bpy

bl_info = {
    "name": "Shadow",
    "author": "Motion Workshop",
    "version": (2, 5),
    "description": "Stream Shadow animation data from the Motion Service into "
                   "the Blender scene. Use MotionSDK to handle socket "
                   "communication.",
    "category": "Animation"
}


def menu_func_import(self, context):
    self.layout.operator(
        ImportAnimOperator.bl_idname, text="Shadow Animation (.csv)")


def register():
    bpy.utils.register_class(ModalOperator)
    bpy.utils.register_class(LuaOperator)
    bpy.utils.register_class(ImportOperator)
    bpy.utils.register_class(ShadowPanel)
    bpy.utils.register_class(ImportAnimOperator)

    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ModalOperator)
    bpy.utils.unregister_class(LuaOperator)
    bpy.utils.unregister_class(ImportOperator)
    bpy.utils.unregister_class(ShadowPanel)
    bpy.utils.unregister_class(ImportAnimOperator)

    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
