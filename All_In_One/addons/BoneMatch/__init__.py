bl_info = {
    "name": "Bone Match",
    "author": "Christophe Seux",
    "version": (1, 0),
    "blender": (2, 78, 0),
    "location": "",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}


if "bpy" in locals():
    import imp
    imp.reload(operators)
    imp.reload(panels)

from . import operators
from . import panels

import bpy

class BoneMatchSettings(bpy.types.PropertyGroup) :
    metarig = bpy.props.PointerProperty(type=bpy.types.Object)
    autorig = bpy.props.PointerProperty(type=bpy.types.Object)

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.BoneMatch = bpy.props.PointerProperty(type = BoneMatchSettings)

def unregister():
    del bpy.types.Scene.BoneMatch
    bpy.utils.unregister_module(__name__)
