bl_info = {
    'name': 'Quake DEM format',
    'author': 'Joshua Skelton',
    'version': (0, 0, 1),
    'blender': (2, 79, 0),
    'location': 'File > Import-Export',
    'description': 'Load a Quake DEM file.',
    'warning': '',
    'wiki_url': '',
    'support': 'COMMUNITY',
    "category": "Learnbgame",
}

if 'bpy' in locals():
    import importlib

    if 'import_bsp' in locals():
        importlib.reload(import_dem)

import bpy
from bpy.props import (
    StringProperty,
    BoolProperty,
    FloatProperty
)

from bpy_extras.io_utils import (
    ImportHelper
)


class ImportDEM(bpy.types.Operator, ImportHelper):
    """Load a Quake DEM file"""

    bl_idname = 'import_scene.dem'
    bl_label = 'Import DEM'
    bl_options = {'UNDO', 'PRESET'}

    filename_ext = '.dem'
    filter_glob = StringProperty(
        default='*.dem',
        options={'HIDDEN'}
    )

    global_scale = FloatProperty(
        name='Scale',
        min=0.001, max=1000.0,
        default=1.0 / 32.0,
    )

    def execute(self, context):
        keywords = self.as_keywords(ignore=('filter_glob',))
        from . import import_dem

        return import_dem.load(self, context, **keywords)


def menu_func_import(self, context):
    self.layout.operator(ImportDEM.bl_idname, text='Quake DEM (.dem)')


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == '__main__':
    register()
