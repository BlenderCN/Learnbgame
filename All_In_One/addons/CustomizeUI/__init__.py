bl_info = {
    "name": "Customize UI",
    "author": "Christophe Seux",
    "version": (0, 1),
    "blender": (2, 79, 0),
    "category": "Learnbgame",
}


if "bpy" in locals():
    import importlib
    importlib.reload(operators)
    importlib.reload(panels)
    importlib.reload(properties)
    importlib.reload(functions)

else :
    from . import operators
    from . import panels
    from . import properties
    from . import functions

import time,bpy
from bpy.app.handlers import persistent

@persistent
def apply_UI_handler(dummy):
    functions.hide_panels()


def register() :
    bpy.utils.register_module(__name__)

    bpy.types.INFO_HT_header.append(panels.menu_func)
    bpy.app.handlers.load_post.append(apply_UI_handler)

    try :
        functions.hide_panels()
    except :
        pass

def unregister() :
    functions.show_panels()
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_HT_header.remove(panels.menu_func)
    bpy.app.handlers.load_post.remove(apply_UI_handler)
