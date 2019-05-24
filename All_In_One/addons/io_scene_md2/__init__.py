bl_info = {
    'name': 'Quake 2 MD2 format',
    'author': 'Joshua Skelton',
    'version': (0, 0, 1),
    'blender': (2, 79, 0),
    'location': 'File > Import-Export',
    'description': 'Load a Quake 2 MD2 file.',
    'warning': '',
    'wiki_url': '',
    'support': 'COMMUNITY',
    "category": "Learnbgame",
}

if 'bpy' in locals():
    import importlib

    if 'import_md2' in locals():
        importlib.reload(import_md2)
        import_md2.reload()

    if 'export_md2' in locals():
        importlib.reload(export_md2)

import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper

class ImportMd2(bpy.types.Operator, ImportHelper):
    """Load a Quake 2 Md2 file"""

    bl_idname = 'import_scene.md2'
    bl_label = 'Import Md2'
    bl_options = {'UNDO'}

    filename_ext = '.md2'
    filter_glob = StringProperty(
        default='*.md2',
        options={'HIDDEN'}
    )

    def execute(self, context):
        from . import import_md2

        return import_md2.load(self, context, self.filepath)

    def draw(self, context):
        layout = self.layout


class ExportMd2(bpy.types.Operator, ExportHelper):
    """Save a Quake 2 MDL File"""

    bl_idname = 'export_scene.mdl'
    bl_label = 'Export MDL'
    bl_options = {'PRESET'}

    filename_ext = '.mdl'
    filter_glob = StringProperty(
        default='*.mdl',
        options={'HIDDEN'},
    )

    check_extension = True

    def execute(self, context):
        from . import export_md2

        return export_md2.save(self, context, self.filepath)


def menu_func_import(self, context):
    self.layout.operator(ImportMd2.bl_idname,
                         text='Quake 2 MD2 (.md2)')


def menu_func_export(self, context):
    self.layout.operator(ExportMd2.bl_idname,
                         text='Quake 2 MD2 (.md2)')


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == '__main__':
    register()
