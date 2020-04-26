bl_info = {
    "name": ".sls exporter",
    "author": "Massinissa Mokhtari",
    "category": "Learnbgame",
    "version": (0, 0, 1),
    "blender": (2, 77, 0),
    "location": "File > Export > Export to SLS",
    "description": ".SLS exporter for Blender",
    "wiki_url": "https://github.com/massile/sls-blender-exporter",
    "category": "Learnbgame",
}

import bpy
from . import operator, ui


def register():
    bpy.utils.register_class(operator.Exporter)
    bpy.types.INFO_MT_file_export.prepend(ui.menu)


def unregister():
    bpy.utils.unregister_class(operator.Exporter)
    bpy.types.INFO_MT_file_export.prepend(ui.menu)
