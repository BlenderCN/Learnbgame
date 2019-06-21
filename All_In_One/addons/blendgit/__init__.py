bl_info = {
    "name": "BlendGit",
    "author": "scorpion81",
    "version": (1, 0),
    "blender": (2, 6, 3),
    "api": 48582,
    "location": "Object",
    "description": "Keep track of revisions of blend files in git from blender",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

if not __name__ in "__main__":
    if "bpy" in locals():
       import imp
       imp.reload(frontend_git)
    else:
        from . import frontend_git 

import bpy

def register():
    bpy.utils.register_module(__name__)
    

def unregister():
    bpy.utils.unregister_module(__name__)
     
    
