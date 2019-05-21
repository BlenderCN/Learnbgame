import bpy

from . import paint_select


bl_info = {
    'name'        : "Paint Selection",
    'author'      : "miniukof",
    'description' : "Select by painting on the objects. Modo/Softimage style.",
    'location'    : "Add shortcut to `view3d.paint_select`",
    'category'    : "Mesh",
    'blender'     : (2, 76, 11),
    'version'     : (0, 0, 2),
    'wiki_url'    : 'https://github.com/miniukof/bl-paint_select',
}


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
