bl_info = {
    "name": "Quake MDL format",
    "author": "Joshua Skelton",
    "version": (0, 0, 1),
    "blender": (2, 77, 0),
    "location": "File > Import-Export",
    "description": "Load a Quake MDL file.",
    "warning": "",
    "wiki_url": "",
    "support": 'COMMUNITY',
    "category": "Learnbgame"
}

if "bpy" in locals():
    import importlib

    if "import_mdl" in locals():
        importlib.reload(import_mdl)
    if "export_mdl" in locals():
        importlib.reload(export_mdl)


import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper


class ImportMDL(bpy.types.Operator, ImportHelper):
    """Load a Quake MDL File"""
    bl_idname = "import_scene.mdl"
    bl_label = "Import MDL"
    bl_options = {'UNDO'}

    filename_ext = ".mdl"
    filter_glob = StringProperty(
        default="*.mdl",
        options={'HIDDEN'},
    )

    def execute(self, context):
        from . import import_mdl

        return import_mdl.load(self, context, self.filepath)

    def draw(self, context):
        layout = self.layout


class ExportMDL(bpy.types.Operator, ExportHelper):
    """Save a Quake MDL File"""

    bl_idname = "export_scene.mdl"
    bl_label = 'Export MDL'
    bl_options = {'PRESET'}

    filename_ext = ".mdl"
    filter_glob = StringProperty(
        default="*.mdl",
        options={'HIDDEN'},
    )

    check_extension = True

    def execute(self, context):
        from . import export_mdl

        return export_mdl.save(self, context, self.filepath)


def menu_func_import(self, context):
    self.layout.operator(ImportMDL.bl_idname,
                         text="Quake MDL (.mdl)")


def menu_func_export(self, context):
    self.layout.operator(ExportMDL.bl_idname,
                         text="Quake MDL (.mdl)")


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
