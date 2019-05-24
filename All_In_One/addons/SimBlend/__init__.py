'''
	SimBlend, a Blender import module for SIMION ion trajectory data

	Copyright (C) 2013 - Physical and Theoretical Chemistry /
	Institute of Pure and Applied Mass Spectrometry
	of the University of Wuppertal, Germany


	This file is part of SimBlend

	SimBlend is free software: You may redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
	------------
	__init__.py

	This is the Blender addon module initialization file,
	registers the addon in blender and defines configuration parameters for the addon
	(UI elements etc.)

	Original author:  Dominik Sand
	Version: 0.1
'''

import os
import bpy
from .options_panel import *
from bpy.utils import register_module,unregister_module
from .import_script import SimionToAnimation

#Blender relevant information which is displayed in the addon menu
bl_info = {
	"name": "SimBlend",
	"description": "Converts SIMION ion trajectory data to Mesh / Animation data.",
	"author": "Dominik Sand",
	"version": (0, 1),
	"blender": (2, 66, 0),
	"location": "", #todo: check out meaning of this key
	"wiki_url": "", #todo: check out meaning of this key
	"tracker_url": "", #todo: check out meaning of this key
	"category": "Learnbgame",
	}

#UI element definition: "Simion to Animation" which starts the data import process
def add_SoA_button(self, context):
	self.layout.operator(SimionToAnimation.bl_idname, text="SimBlend: SIMION Trajectories")

#add the defined button to file-> import menu
def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_import.append(add_SoA_button)

#remove the defined button from file-> import menu
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_import.remove(add_SoA_button)

#Blender API register function    
if __name__ == "__main__":
	register()
