
bl_info = {
    "name": "Panda3D (BPB)",
    "author": "rdb",
    "blender": (2, 69, 0),
    "location": "",
    "description": "Blender->Panda3D bridge",
    "warning": "Work in progress, not yet functional",
    "wiki_url": "",
    "tracker_url": "",
    "support": "",
    "category": "Render"
}

import bpy
from . import engine

def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
