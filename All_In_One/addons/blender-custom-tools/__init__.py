#----------------------------------------------------------
# File __init__.py
#----------------------------------------------------------

#    Addon info
bl_info = {
    "name": "Custom Tools",
    "description": "Tools for general improved functionality.",
    "author": "Anthony Esau",
    "version": (0, 1),
    "blender": (2, 78, 2),
    "location": "View3D > Tool Shelf > Custom Tools",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

# To support reload properly, try to access a package var,
# if it's there, reload everything
if "bpy" in locals():
    import imp
    imp.reload(dimprop)
    imp.reload(parenttools)
    print("Reloaded multifiles")
else:
    from . import dimprop, parenttools
    print("Imported multifiles")


import bpy


#
#    Registration
#

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
