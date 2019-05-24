from SDK_utils import *

bl_info = {
    "name": "Scene Editor",
    "author": "BluStroke®",
    "version": (1, 0),
    "blender": (2, 78, 0),
    "location": "",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
    }

@registerclass
class SceneEditor:
    bl_idname = "SDK_scene_editor"
    bl_name = "Scene Editor"

    def __init__(self):
        pass