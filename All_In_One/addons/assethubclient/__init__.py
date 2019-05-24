bl_info = {
    "name": "AssetHub Client",
    "author": ("portnov@bk.ru"),
    "version": (0, 0, 0, 1),
    "blender": (2, 7, 8),
    "location": "?",
    "description": "AssetHub client for Blender",
    "warning": "",
    "wiki_url": "https://github.com/portnov/assethub/wiki",
    "tracker_url": "https://github.com/portnov/assethub/issues",
    "category": "Learnbgame",
}

import bpy
import importlib

from . import blenderclient

def register():
    #bpy.utils.register_module(__name__)
    blenderclient.register()

def unregister():
    blenderclient.unregister()

if __name__ == "__main__":
    register()

