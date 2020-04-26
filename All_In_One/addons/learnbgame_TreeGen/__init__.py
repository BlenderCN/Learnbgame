bl_info = {
    "name": "Tree_Gen",
    "category": "Learnbgame",
    "description": "Generate high quality tree models",
    "author": "Charlie Hewitt and Luke Pflibsen-Jones",
    "version": (0, 0, 1),
    'blender': (2, 80, 0),
    'location': 'View3D > Tools > Learnbgame',
    'warning': '',
    'wiki_url': 'https://github.com/BlenderCN/Learnbgame/wiki',
    'tracker_url': 'https://github.com/BlenderCN/Learnbgame/issues',
}


import bpy
from . import gui


def register():
    gui.register()


def unregister():
    # Reversing order is best-practice
    gui.unregister()


if __name__ == "__main__":
    register()
