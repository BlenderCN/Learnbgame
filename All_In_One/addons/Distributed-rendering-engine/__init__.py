# This directory is a Python package.
# It contains :-
# DistributedRenderingEngine.py : Contains the main rendering engine class

bl_info = {
    "name": "DRE",
    "author": "Rupinder Singh",
    "version": (0, 1),
    "blender": (2, 78, 0),
    "location": "Render > Engine > DRE",
    "description": "Distributed Rendering Engine for Blender",
    "warning": "work in progress",
    "wiki_url": "http://easyportfolio.xyz",
    "category": "Render",
}

if "reload_modules" in locals():
    import importlib
    importlib.reload(rendering_engine)
    importlib.reload(ui)
    importlib.reload(operators)
    importlib.reload(configs)
else:
    from dre import rendering_engine
    from dre import ui
    from dre import operators
    from dre import configs

reload_modules=True

def register():
    import bpy
    bpy.utils.register_module(__name__)

def unregister():
    import bpy
    bpy.utils.unregister_module(__name__)