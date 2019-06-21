bl_info = {
    "name": "Export Utils",
    "author": "Toda Shuta",
    "version": (0, 1, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Toolshelf > Export Utility",
    "description": "Utility for Export Models (Substance Painter, etc.)",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}


if "bpy" in locals():
    import importlib
    importlib.reload(export_util)
else:
    from . import export_util

import bpy


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
