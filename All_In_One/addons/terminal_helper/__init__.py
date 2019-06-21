bl_info = {
    "name": "Terminal Helper",
    "description": "Easily create commands to be executed in the terminal",
    "author": "Jacques Lucke",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "Render",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
}


import bpy


# load and reload submodules
##################################

import importlib
from . import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())


# register
##################################

import traceback

def register():
    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()

    for module in modules:
        if hasattr(module, "register"):
            module.register()

    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))

def unregister():
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()

    for module in modules:
        if hasattr(module, "unregister"):
            module.unregister()

    print("Unregistered {}".format(bl_info["name"]))
