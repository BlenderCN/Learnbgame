bl_info = {
    "name": "Text Editor Autocomplete",
    "author": "scorpion81",
    "version": (0, 1),
    "blender": (2, 6, 3),
    "api": 50083,
    "location": "Text Editor > Left Panel > Autocomplete",
    "description": "Simple autocompletion for Blender Text Editor (for Python only currently)",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
} 


if not __name__ in "__main__":
    if "bpy" in locals():
       import imp
       imp.reload(auto_complete)
    else:
        from text_auto_complete import auto_complete

import bpy

def register():
    bpy.utils.register_module(__name__)
    

def unregister():
    bpy.utils.unregister_module(__name__)
     
if __name__ == "__main__":
    import auto_complete
    auto_complete.register()