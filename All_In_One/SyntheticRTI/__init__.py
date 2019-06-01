bl_info = {
    "name": "SyntheticRTI",
    "author": "Andrea Dall'Alba",
    "version": (0, 4, 4),
    "blender": (2, 79, 0),
    "location": "View3D > Tools > SyntheticRTI",
    "description": "Plugin to help creating the synthetic database for RTI",
    "warning": "This addon is still in development.",
    "wiki_url": "https://github.com/giach68/SyntheticRTI",
    "category": "Learnbgame",
}

import bpy

# load and reload submodules
##################################

import importlib
from . import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())
from .srtiutilities import srtiproperties 
srtiproperties.register()

# register
##################################

import traceback

def register():
    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()

    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))

def unregister():
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()

    print("Unregistered {}".format(bl_info["name"]))
