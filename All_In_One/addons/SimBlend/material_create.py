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
	material_create.py

	Creates a list of materials from the list of existing ion masses in the import data
	which are added to the created Blender objects

	Original author:  Dominik Sand
	Version: 0.1
'''

import bpy


def material_create(Masslist):
	for item in Masslist:
		if bpy.context.scene.animation_type == 'path_id':
			mat = bpy.data.materials.new(item)
			mat.type = 'SURFACE'
			if(bpy.context.scene.ion_tube_mod == True):
				mat.use_vertex_color_light = True
		if bpy.context.scene.animation_type == 'sphere_id':
			mat = bpy.data.materials.new(item)
			mat.type = 'SURFACE'
			if(bpy.context.scene.ion_splat == True):
				bpy.data.materials.new((item + " red_splat"))
				bpy.data.materials.get(item + " red_splat").diffuse_color[0] = 1
				bpy.data.materials.get(item + " red_splat").diffuse_color[1] = 0
				bpy.data.materials.get(item + " red_splat").diffuse_color[2] = 0
		if bpy.context.scene.animation_type == 'particle_id':
			mat = bpy.data.materials.new(item + "Halo")
			mat.type = 'HALO'