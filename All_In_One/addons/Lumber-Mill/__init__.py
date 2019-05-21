'''------------------------------------------------------------------

Create add_on
    import necessary files (reload if needed)
    register module

------------------------------------------------------------------'''
bl_info = {
    "name": "Dimensional Lumber",
    "author": "Al Nolan",
    "version": (1, 0),
    "blender": (2, 77),
    "location": "Toolbar",
    "description": "add dimensional lumber to scene",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
    }


if "bpy" in locals():
    import imp
    imp.reload(Lumber_Mill)
    imp.reload(Vert_Collections)
    imp.reload(Estimator)
    print("Reloaded multifiles")
else:
    from . import Lumber_Mill, Vert_Collections, Estimator
    print("Imported multifiles")

import bpy


# Registration------------------------------------------------------------

def register():
    #bpy.utils.register_class(PropertyGroup)
    bpy.utils.register_module(__name__)

def unregister():
    #bpy.utils.unregister_class(PropertyGroup)
    bpy.utils.register_module(__name__)

if __name__ == "__main__":
    register()
