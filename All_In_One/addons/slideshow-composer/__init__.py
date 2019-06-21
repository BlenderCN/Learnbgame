bl_info = {
    "name": "SlideShow Composer",
    "description": "Helps creating slide shows from pictures/videos",
    "author": "Piotr Marcinkowski",
    "version": (0, 1, 0),
    "blender": (2, 78, 0),
    "location": "sequencer",    
    "wiki_url": "",    
    "category": "Learnbgame",
}

import bpy
import os
from .menus import SlideShowMainMenu
from .operator_import import ImportFiles

# load and reload submodules
import importlib
from . import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())

import traceback

def register():
    try:
        bpy.utils.register_module(__name__)
    except:
        traceback.print_exc()

    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))

def unregister():
    try:
        bpy.utils.unregister_module(__name__)
    except:
        traceback.print_exc()
    print("Unregistered {}".format(bl_info["name"]))

