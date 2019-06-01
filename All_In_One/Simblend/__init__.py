'''
Author :  Dominik Sand 
Date : 23.04.2013

This is the Blender Addon registration file, so Addons can be used in Blender
'''

import os
import bpy
from .options_panel import * 
from bpy.utils import register_module , unregister_module
from .import_script import SimionToAnimation

#Blender relevant information which is displayed in the Addon Menu
bl_info = {
	"name": "Simion to Animation",
    "description": "Converts Simion delimter data to Mesh / Animation data.",
    "author": "Dominik Sand",
    "version": (1, 0),
    "blender": (2, 66, 0),
    "location": "", 
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
	}

#button definition for Blender UI
def add_SoA_button(self, context):
    self.layout.operator(SimionToAnimation.bl_idname, text="Simion to Animation")

#add button to file-> import menu
def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(add_SoA_button)

#remove button from file-> import menu
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(add_SoA_button)

#Blender API register function    
if __name__ == "__main__":
    register()
