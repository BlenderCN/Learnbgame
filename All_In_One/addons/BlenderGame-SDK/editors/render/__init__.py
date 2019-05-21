import bpy
import ATOM_Types
import ctypes
from bpy.app.handlers import persistent
import Properties
import ATOM_utils
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
config = ATOM_utils.Config(os.path.join(ROOT_PATH, "config.ini"), {"ADDON_ROOT":ROOT_PATH})

############### FOR STANDALONE ADDON RELEASE ################


from . import RenderEngine, Properties

bl_info = {
    "name": "Render Editor",
    "author": "BluStroke®",
    "version": (1, 0),
    "blender": (2, 78, 0),
    "location": "",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "category": "System",
    }

def register():

    RenderEngine.register()
    Properties.register()

def unregister():

    RenderEngine.unregister()
    Properties.unregister()

if __name__ == "__main__":
    print("ok")
    register()

 ############################################################




# @persistent
# def register_properties(dummy):
#     Properties.register()

    # ATOM.addons = ATOM_utils.Addon.install_addons(config.EXT_SOURCE_PATH if ATOM.config.DEBUG else config.EXT_PATH, ATOM_Types.InstallMod.LOCAL)

    # bpy.app.handlers.load_post.append(ATOM_utils.Addon.load_addons)

    # pack_addons(os.path.join(os.path.dirname(__file__), r"extentions\legacy\source"),
    #                     os.path.join(os.path.dirname(__file__), r"extentions\legacy"))