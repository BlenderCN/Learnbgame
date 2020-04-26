bl_info = {
    "name": "SWC format",
    "author": "Martin Pyka",
    "version": (1, 0, 0),
    "blender": (2, 74, 0),
    "location": "File > Import > SWC",
    "description": "Import SWC files",
    "license": "GPL v2",
    "category": "Learnbgame",
}

__author__ = bl_info['author']
__license__ = bl_info['license']
__version__ = ".".join([str(s) for s in bl_info['version']])

import bpy
from . import operator_swc_import

def register():
    #bpy.utils.register_module(__name__)
    operator_swc_import.register()
    
def unregister():
    #bpy.utils.unregister_module(__name__)
    operator_swc_import.unregister()

if __name__ == "__main__":
    register()

