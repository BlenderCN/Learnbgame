# This directory is a Python package.
bl_info = {
    "name": "Prozess",
    "author": "Erik Lovlie",
    "version": (1, 0),
    "blender": (2, 5, 7),
    "api": 35011,
    "location": "File > Export",
    "description": "Dump scene as python source",
    "category": "Learnbgame",
}

# To support reload properly, try to access a package var, if it's there, reload everything
if "init_data" in locals():
    import imp
    imp.reload(prozblend)
else:
    from prozess import prozblend

init_data = True

def register():
    import bpy
    bpy.utils.register_module(__name__)

def unregister():
    import bpy
    bpy.utils.unregister_module(__name__)

