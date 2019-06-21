

import os

bl_info = {
    "name"       : "EclipseDebugger",
    "description": "EclipseDebugger",
    "author"     : "Nodebench" ,
    "version"    : (0, 0, 1),
    "blender"    : (2, 67, 0),
    "api"        : 57908,
    "category": "Learnbgame",
    "tooltip"    : "Eclipse Interactive Debugger",
    "license"    : "GPL Version 2",
    }




def plugin_path():
    return os.path.dirname(os.path.realpath(__file__))

if 'core' in locals():
    import imp
    imp.reload(core)
else:
    import bpy
    from . import core
    
    def register():
        return core.register()

    def unregister():
        return core.unregister()
    

