bl_info = {
    "name": "SpeckleBlender",
    "author": "Tom Svilans",
    "version": (1, 0, 0),
    "blender": (2, 79, 0),
    "location": "Properties > Object",
    "warning": "ALPHA. Not to be trusted.",
    "description": "SpeckleWorks is an open source initiative for developing an extensible Design & AEC data communication protocol and platform.",
    "wiki_url": "https://speckle.works",
    "category": "Learnbgame",
}

# import Blender

import bpy

# load and reload submodules

import importlib
from . import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())

# register

import traceback

def register():
    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()

    from . properties.scene import SpeckleSceneSettings, SpeckleSceneObject, SpeckleUserAccountObject
    
    #bpy.types.Scene.speckle_act_acc = bpy.props.IntProperty(default=0)
    #bpy.types.Scene.speckle_act_str = bpy.props.IntProperty(default=0)
    bpy.types.Scene.speckle = bpy.props.PointerProperty(type=SpeckleSceneSettings)

    from . properties.object import SpeckleObjectSettings
    bpy.types.Object.speckle = bpy.props.PointerProperty(type=SpeckleObjectSettings)

    from speckle import SpeckleApiClient
    bpy.types.Scene.speckle_client = SpeckleApiClient()

    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))

def unregister():
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()

    print("Unregistered {}".format(bl_info["name"]))