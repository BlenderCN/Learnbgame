bl_info = {
    'name': 'Lithtech ABC Format',
    'description': 'Import and export ABC models and animations files from Lithtech 2.1 games (eg. No One Lives Forever).',
    'author': 'Colin Basnett',
    'version': (1, 0, 0),
    'blender': (2, 79, 0),
    'location': 'File > Import-Export',
    'warning': 'This add-on is under development.',
    'wiki_url': 'https://github.com/cmbasnett/io_scene_abc/wiki',
    'tracker_url': 'https://github.com/cmbasnett/io_scene_abc/issues',
    'support': 'COMMUNITY',
    'category': 'Import-Export'
}

if 'bpy' in locals():
    import importlib
    if 's3tc'       in locals(): importlib.reload(s3tc)
    if 'dxt'        in locals(): importlib.reload(dtx)
    if 'abc'        in locals(): importlib.reload(abc)
    if 'builder'    in locals(): importlib.reload(builder)
    if 'reader'     in locals(): importlib.reload(reader)
    if 'writer'     in locals(): importlib.reload(writer)
    if 'importer'   in locals(): importlib.reload(importer)
    if 'exporter'   in locals(): importlib.reload(exporter)

import bpy
from . import s3tc
from . import dtx
from . import abc
from . import builder
from . import reader
from . import writer
from . import importer
from . import exporter

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(importer.ImportOperator.menu_func_import)
    bpy.types.INFO_MT_file_export.append(exporter.ExportOperator.menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(importer.ImportOperator.menu_func_import)
    bpy.types.INFO_MT_file_export.remove(exporter.ExportOperator.menu_func_export)

