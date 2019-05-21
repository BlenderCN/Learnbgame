import bpy

from . import fuzzy_finder


bl_info = {
    'name': "Fuzzy Finder",
    'description': "Context sensitive search and select.",
    'location': "Add shortcut to `fuzzy_finder.select`",
    'author': "miniukof",
    'version': (0, 0, 1),
    'blender': (2, 77, 0),
    'category': "User Interface",
}


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
