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
	options_panel.py

	Defines an option panel for the Blender UI with the options for the data import process
	sources : http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Cookbook/Code_snippets/Interface

	Original author:  Dominik Sand
	Version: 0.1
'''
import bpy

#UI elements of the option panel 
bpy.types.Scene.obj_size = bpy.props.FloatProperty( 
	name="Object size",
	default=0.1,
	min =0,
	max =1)

bpy.types.Scene.obj_distance = bpy.props.FloatProperty(
	name="Distance scale",
	default=1,
	min=0,
	max=5)

bpy.types.Scene.frame_num = bpy.props.IntProperty(
	name="Number of frames",
	default=300,
	min=0,
	max=500000)

bpy.types.Scene.animation_type = bpy.props.EnumProperty(
	items = [
		("path_id","Path","animates data as path"),
		("sphere_id","Spheres","animates data as spheres")],
		#("particle_id","Particle","animates data as particles")],
	default="path_id",
	name="Animation Type",
	description="Animation Properties")

bpy.types.Scene.number_pathverts = bpy.props.IntProperty(
	name="Path tube vertices",
	default=8,
	min=3,
	max=64)

bpy.types.Scene.number_merge = bpy.props.IntProperty(
	name="Merged trajectory samples",
	default=1,
	min=1,
	max=50)

bpy.types.Scene.ion_splat = bpy.props.BoolProperty(
	name="Mark Ion Splat",
	default=False)

bpy.types.Scene.ion_tube_mod = bpy.props.BoolProperty(
	name="Material Tube Modifier",
	default=False)


#Panel class: defines where the panel is located
#and the layout of the panel
class options_panel(bpy.types.Panel) :
	bl_space_type="PROPERTIES"
	bl_region_type="WINDOW"
	bl_context="scene"
	bl_label="SimBlend"

	def draw(self, context):
		scn = bpy.context.scene
		layout = self.layout
		column  = layout.row()
		column.prop(scn,"obj_size")
		column = layout.row()
		column.prop(scn,"obj_distance")
		column = layout.row()
		column.prop(scn,"frame_num")
		column = layout.row()
		column.prop(scn,"number_pathverts")
		column = layout.row()
		column.prop(scn,"number_merge")
		column = layout.row()
		column.prop(scn,"ion_splat")
		#column = layout.row()
		#column.prop(scn,"ion_tube_mod")
		column = layout.row()
		column.prop(scn,"animation_type")
