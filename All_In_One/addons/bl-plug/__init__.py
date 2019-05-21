import bpy

from . import plug


bl_info = {
    'name': "Plug",
    'description': "Blender plugin manager.",
    'author': "miniukof",
    'version': (0, 0, 1),
    'blender': (2, 77, 0),
    'category': "System",
}


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
