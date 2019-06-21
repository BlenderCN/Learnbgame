bl_info = {
    "name": "VoronoiTest",
    "author": "scorpion81",
    "version": (0, 1),
    "blender": (2, 6, 0),
    "api": 41226,
    "location": "Object",
    "description": "Voronoi Test Script",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

#if not __name__ in "__main__":
#    if "bpy" in locals():
#       import imp
#       imp.reload(voronoi)
#    else:
#        from . import voronoi

import bpy

def register():
    bpy.utils.register_module(__name__)
    

def unregister():
    bpy.utils.unregister_module(__name__)
     
    
