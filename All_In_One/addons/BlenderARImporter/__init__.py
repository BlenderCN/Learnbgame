# -------------------------------------------------------------------------------
#                    Extra Image List - Addon for Blender
#
# - Two display options (preview and plain list)
# - Button to clear all users for the selected image datablock
# - Double click on image in Node Editor opens the image in UV/Image Editor
#
# Version: 0.2
# Revised: 30.05.2017
# Author: Miki (meshlogic)
# -------------------------------------------------------------------------------
bl_info = {
    "name": "AR Importer",
    "author": "Jesse Vander Does",
    "category": "Import-Export",
    "description": "Import scenes captured with ARExporter",
    "location": "3D View > Tools > Image List",
    "version": (0, 2),
    "blender": (2, 78, 0)
}

import bpy


# load and reload submodules
##################################
from .ar_importer_utils import ARImporterAddonPreferences


# register
##################################

import traceback

def register():
    print("Register " + __name__)
    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()

def unregister():
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()

    print("Unregistered {}".format(bl_info["name"]))
