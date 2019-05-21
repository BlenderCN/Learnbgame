bl_info = {
    "name": "Torque Terrain (TER) format",
    "author": "port",
    "version": (0, 0, 1),
    "blender": (2, 76, 0),
    "location": "File > Import > Torque Terrain",
    "description": "Import Torque Terrain (TER) files",
    "warning": "",
    "support": "COMMUNITY",
    "category": "Import-Export"
}

if "bpy" in locals():
    import importlib
    if "import_ter" in locals():
        importlib.reload(import_ter)

import os

import bpy
from . import import_ter
from bpy.props import (
        StringProperty,
        BoolProperty,
        CollectionProperty,
        EnumProperty,
        FloatProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        orientation_helper_factory,
        axis_conversion,
        )
from bpy.types import (
        Operator,
        OperatorFileListElement,
        )

class ImportTER(Operator, ImportHelper):
    bl_idname = "import_mesh.ter"
    bl_label = "Import Torque Terrain"
    bl_options = {"UNDO"}

    filename_ext = ".ter"

    filter_glob = StringProperty(
        default="*.ter",
        options={'HIDDEN'},
    )

    def execute(self, context):
        keywords = self.as_keywords(ignore=("filter_glob",
                                            "split_mode",
                                            ))

        return import_ter.load(context, **keywords)

def menu_import(self, context):
    self.layout.operator(ImportTER.bl_idname, text="Torque Terrain (.ter)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_import)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_import)

if __name__ == "__main__":
    register()
