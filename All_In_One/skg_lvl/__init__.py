import os

from . import export_lvl, import_lvl


bl_info = {
    "name": "SkullGirls .lvl plugin",
    "author": "0xFAIL",
    "version": (0, 5, 0),
    "blender": (2, 72, 0),
    "category": "Learnbgame",
    "location": "File > Import/Export",
    "description": "Import SkullGirls stages"
}

import bpy

from bpy.props import (CollectionProperty,
                       StringProperty)

from bpy_extras.io_utils import (ImportHelper,
                                 ExportHelper)

class ImportLVL(bpy.types.Operator, ImportHelper):
    """Load a lvl file and all the other stuff around it"""
    bl_idname = "import_mesh.skglvl"
    bl_label = "Import LVL"
    bl_options = {'UNDO'}

    files = CollectionProperty(name="File Path",
                               description="File path used for importing the lvl file",
                               type=bpy.types.OperatorFileListElement)

    directory = StringProperty()

    filename_ext = '.lvl'
    filter_glob = StringProperty(default='*.lvl', options={'HIDDEN'})

    def execute(self, context):
        paths = [os.path.join(self.directory, name.name)
                 for name in self.files]
        if not paths:
            paths.append(self.filepath)

        for path in paths:
            import_lvl.load(self, context, path)
        return {'FINISHED'}


class ExportLVL(bpy.types.Operator, ExportHelper):
    """Export current scene as a sgi file"""
    bl_idname = "export_mesh.skglvl"
    bl_label = "Export sgi"

    filename_ext = ".sgi.msb"
    filter_glob = StringProperty(default="*.sgi.msb", options={'HIDDEN'})

    def execute(self, context):
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)

        return export_lvl.save(self, context, filepath)


def menu_func_import(self, context):
    self.layout.operator(ImportLVL.bl_idname, text="SkullGirls stage (.lvl)")


def menu_func_export(self, context):
    self.layout.operator(ExportLVL.bl_idname, text="SkullGirls stage info (.sgi.msb)")


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
