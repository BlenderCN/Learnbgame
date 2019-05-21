import bpy
import sys

bl_info = {
    "name": "Python Tool Shelf",
    "author": "Ryan Gordon",
    "version": (0, 1, 0),
    "blender": (2, 77, 0),
    "location": "Tool Shelf, Python Tab",
    "description": "Python Tool shelf for long running scripts",
    "warning": "",
    "category": "Learnbgame"
}


def register():
    from . import ui
    from . import operators
    bpy.utils.register_module(__name__)

def unregister():
    from . import ui
    from . import operators
    bpy.utils.unregister_module(__name__)
