bl_info = {
    "name": "Randomize",
    "description": "Randomize object transformations.",
    "author": "Perry Parks",
    "version": (0,5),
    "blender": (2, 5, 8),
    "api": 2148,
    "location": "Add from Spacebar menu, then View3D > Toolshelf",
    "warning": 'Under development',
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

import bpy

from Randomize import AddRandomizeObject
from Randomize import ui
from Randomize import key_child_delta_transforms
from Randomize import delete_child_keys
from Randomize import object_tools

def register():
    AddRandomizeObject.register()
    ui.register()
    key_child_delta_transforms.register()
    delete_child_keys.register()
    object_tools.register()

    #bpy.utils.register_module(__name__)

def unregister():
    AddRandomizeObject.unregister()
    ui.unregister()
    key_child_delta_transforms.unregister()
    delete_child_keys.unregister()
    object_tools.unregister()

    #bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
