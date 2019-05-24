
bl_info = {
    "name": "Jet",
    "author": "Oliver Villar <oliver@blendtuts.com>, Roberto Noya <negucio@gmail.com>",
    "description": "",
    "version": (0, 2, 1),
    "blender": (2, 7, 9),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
}

import bpy
from . import data, ui, handler

def register():
    ui.register()
    data.register()
    handler.register()


def unregister():
    handler.unregister()
    data.unregister()
    ui.unregister()
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()

