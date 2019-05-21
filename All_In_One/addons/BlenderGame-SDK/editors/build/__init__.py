import bpy
import ATOM_Types
import ctypes
from bpy.app.handlers import persistent
import Properties
import utils
import sys, os

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       FloatVectorProperty,
                       IntVectorProperty,
                       BoolVectorProperty,
                       CollectionProperty)
                       
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       Property,
                       AddonPreferences)

ROOT_PATH = os.path.dirname(__file__)
config = utils.Config(os.path.join(ROOT_PATH, "config.ini"), ADDON_ROOT=ROOT_PATH).config

if config.debug:
    platforms = utils.Addon.list_extentions(config.platforms)
else:
    from ..platforms import Android, IOS, Linux, OSX, PS3, PS4, Windows, XBOX_ONE, XBOX_360

############### FOR STANDALONE ADDON RELEASE ################

if config.standalone:

    from . import FileManager, Properties, Types, utils

    bl_info = {
        "name": "Build editor",
        "author": "BluStroke®",
        "version": (1, 0),
        "blender": (2, 78, 0),
        "location": "",
        "description": "Building tool for multiplatform release",
        "warning": "",
        "wiki_url": "",
        "category": "System",
        }
  
    def register():
        
        FileManager.register()
        Properties.register()
        Types.register()
        utils.register()

    def unregister():

        FileManager.unregister()
        Properties.unregister()
        Types.unregister()
        utils.unregister()

    if __name__ == "__main__":
        
        register()

 ############################################################




# @persistent
# def register_properties(dummy):
#     Properties.register()

    # ATOM.addons = ATOM_utils.Addon.install_addons(config.EXT_SOURCE_PATH if ATOM.config.DEBUG else config.EXT_PATH, ATOM_Types.InstallMod.LOCAL)

    # bpy.app.handlers.load_post.append(ATOM_utils.Addon.load_addons)

    # pack_addons(os.path.join(os.path.dirname(__file__), r"extentions\legacy\source"),
    #                     os.path.join(os.path.dirname(__file__), r"extentions\legacy"))