bl_info = {
    "name": "Procedural Fruit",
    "category": "Learnbgame",
    "author": "Rafael",
    "version": (0, 0),
    }

import bpy
from .util import linkAndSelect
from .fruit import Fruit

def register():
    Fruit.registerOperators()
    
def unregister():
    Fruit.unregisterOperators()

if __name__ == "__main__": # lets you run the script from a Blender text block; useful during development
    register()
