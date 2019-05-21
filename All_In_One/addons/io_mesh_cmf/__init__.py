# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, 2018
#
# ##### END LICENSE BLOCK #####

bl_info = {
    "name": "Clustered Mesh Format",
    "author": "Dummiesman",
    "version": (0, 3, 0),
    "blender": (2, 77, 0),
    "location": "File > Import-Export",
    "description": "Import-Export CMF files",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.7/Py/"
                "Scripts/Import-Export/CMF",
    "support": 'COMMUNITY',
    "category": "Learnbgame"
}

import bpy
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        StringProperty,
        CollectionProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        )

class ImportCMF(bpy.types.Operator, ImportHelper):
    """Import from CMF file format (.CMF)"""
    bl_idname = "import_scene.cmf"
    bl_label = 'Import CMF'
    bl_options = {'UNDO'}

    filename_ext = ".CMF"
    filter_glob = StringProperty(default="*.CMF", options={'HIDDEN'})

    def execute(self, context):
        from . import import_cmf
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "check_existing",
                                            ))

        return import_cmf.load(self, context, **keywords)


class ExportCMF(bpy.types.Operator, ExportHelper):
    """Export to CMF file format (.CMF)"""
    bl_idname = "export_scene.cmf"
    bl_label = 'Export CMF'

    filename_ext = ".CMF"
    filter_glob = StringProperty(
            default="*.CMF",
            options={'HIDDEN'},
            )

    apply_modifiers = BoolProperty(
        name="Apply Modifiers",
        description="Do you desire modifiers to be applied in the CMF?",
        default=True,
        )

        
    def execute(self, context):
        from . import export_cmf
        
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "check_existing",
                                            ))
                                    
        return export_cmf.save(self, context, **keywords)


# Add to a menu
def menu_func_export(self, context):
    self.layout.operator(ExportCMF.bl_idname, text="Clustered Mesh Format (.CMF)")


def menu_func_import(self, context):
    self.layout.operator(ImportCMF.bl_idname, text="Clustered Mesh Format (.CMF)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
