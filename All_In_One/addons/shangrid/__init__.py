bl_info = {
    "name": "Shangrid for Blender",
    "author": "Take@Elgraiv",
    "blender": (2, 78, 0),
    "location": "",
    "description": "Shangrid Add-on for Blender",
    "warning": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

import bpy
import shangrid.ShangridPanel
import shangrid.ShangridOp
import shangrid.ShangridCore
from bpy.props import (BoolProperty)

def register():
    import imp
    imp.reload(shangrid.ShangridPanel)
    imp.reload(shangrid.ShangridCore)
    imp.reload(shangrid.ShangridOp)

    bpy.utils.register_module(__name__)
    bpy.Shangrid=shangrid.ShangridCore.ShangridCore()

    bpy.types.Scene.shangrid_selected_only = bpy.props.BoolProperty(
        name="Selected Only",
        description="tooltips",
        default = True)


def unregister():
    del bpy.Shangrid
    del bpy.types.Scene.shangrid_selected_only
    bpy.utils.unregister_module(__name__)