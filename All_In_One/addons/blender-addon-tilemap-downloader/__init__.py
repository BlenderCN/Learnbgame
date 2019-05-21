bl_info = {
    "name": "Tile Map Downloader",
    "author": "Toda Shuta",
    "version": (1, 3, 2),
    "blender": (2, 79, 0),
    "location": "Image Editor",
    "description": "Download and Stitching Tile Map",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Image"
}


if "bpy" in locals():
    import importlib
    importlib.reload(tilemapdownloader)
else:
    from . import tilemapdownloader


import bpy


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
