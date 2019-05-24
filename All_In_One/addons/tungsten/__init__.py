import bpy

bl_info = {
    "name": "Tungsten",
    "author": "Aaron Griffith <aargri@gmail.com>",
    "description": "Tungsten renderer integration",
    "category": "Learnbgame",
    "blender": (2, 6, 7),
    "location": "Info Header (engine dropdown)",
}

MODULES = [
    'base',
    'props',
    
    'tungsten',
    'preferences',
    'scene',
    'engine',
    'node',

    'texture',
    'material',
    'medium',

    'render',
    'mesh',
    'lamp',
    'camera',
    'world',
]

import importlib, imp
for mod in MODULES:
    if mod in locals():
        imp.reload(locals()[mod])
    else:
        locals()[mod] = importlib.import_module('.' + mod, __package__)

def register():
    base.register()

def unregister():
    base.unregister()

if __name__ == "__main__":
    register()
