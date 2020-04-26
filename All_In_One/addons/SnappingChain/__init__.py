bl_info = {
    "name": "Snapping Chain",
    "author": "Christophe Seux",
    "version": (1, 0),
    "blender": (2, 78, 0),
    "location": "",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}



if "bpy" in locals():
    import importlib
    importlib.reload(operators)
    importlib.reload(panels)
    importlib.reload(properties)

from . operators import *
from . panels import *
from . properties import SnappingChainPrefs,SnappingChainSettings

import bpy

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.SnappingChainPrefs = bpy.props.PointerProperty(type= SnappingChainPrefs)
    bpy.types.Armature.SnappingChain = bpy.props.PointerProperty(type= SnappingChainSettings)

def unregister():
    del bpy.types.Armature.SnappingChain
    del bpy.types.Scene.SnappingChainPrefs
    bpy.utils.unregister_module(__name__)
