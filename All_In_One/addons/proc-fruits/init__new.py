bl_info = {
    "name": "Procedural Fruit",
    "category": "Learnbgame",
    "author": "Rafael",
    "version": (0, 0),
    "blender": (2,80,0),
    }

import bpy
from . import addon_operator
from . import addon_property
from . import addon_ui

def register():
    addon_property.register()
    addon_ui.register()
    addon_operator.register()
    
def unregister():
    addon_operator.unregister()
    addon_ui.unregister()
    addon_property.register()

if __name__ == "__main__": # lets you run the script from a Blender text block; useful during development
    register()
