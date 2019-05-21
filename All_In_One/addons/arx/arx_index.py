# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import os
import shutil
import bpy, mathutils,re
from bpy.props import *

from bpy_extras.object_utils import AddObjectHelper, object_data_add
from . arx_base import Base_Material
from . arx_texture import *

class OP_Make_Alpha(bpy.types.Operator):

	bl_idname="object.arx_index_render"
	bl_label="Index Render"
	bl_description="Change materials for index render pass"

	r = 0
	g = 0
	b = 0

	r_on = 1
	r_off = 0
	g_on = 1
	g_off = 0
	b_on = 1
	b_off = 0

	loop_main = 0
	loop_local = 0

	global_ids={}

	def set_color(self):

		factor = 1.3

		if self.loop_main == 1 :
			self.r_on /= factor
			self.g_on /= factor
			self.b_on /= factor
		
			self.loop_main=0
			
		# ON
		if self.loop_local == 0 :
			self.r = self.r_on
			self.g = self.g_off
			self.b = self.b_off
			
			self.loop_local += 1

		elif self.loop_local == 1 :
			self.r = self.r_on
			self.g = self.g_on
			self.b = self.b_off
			self.loop_local += 1

		elif self.loop_local == 2 :
			self.r = self.r_on
			self.g = self.g_off
			self.b = self.b_on
			self.loop_local += 1

		# OFF
		elif self.loop_local == 3 :
			self.r = self.r_off
			self.g = self.g_on
			self.b = self.b_off

			self.loop_local += 1

		elif self.loop_local == 4 :
			self.r = self.r_off
			self.g = self.g_off
			self.b = self.b_on

			self.loop_local += 1

		elif self.loop_local == 5 :
			self.r = self.r_off
			self.g = self.g_on
			self.b = self.b_on

			self.loop_local = 0
			self.loop_main = 1

	def store_data(self,material): 


		# create group
		if(material.name in bpy.data.groups):
			settings=bpy.data.groups[material.name]
		else:
			settings = bpy.data.groups.new(material.name)

		# store data

		print("MATERIAL:" + material.name)

		mydict = {
							"diffuse_color_0":material.diffuse_color[0],
							"diffuse_color_1":material.diffuse_color[1],	
							"diffuse_color_2":material.diffuse_color[2],	
							"alpha":material.alpha,
							"use_transparency":material.use_transparency,
							"use_raytrace":material.use_raytrace,
							"use_shadeless":material.use_shadeless,
							"use_textures":material.use_textures[0],
							"use_nodes":material.use_nodes,
							"mirror":material.raytrace_mirror.use,
						}

		slots = material.texture_slots

		if(slots):
			slot = slots[0]
			if(slot):
				#print(material.texture_slots[0])
				if(material.texture_slots[0]):

					mydict["use_rgb_to_intensity"]=slot.use_rgb_to_intensity

		settings["data"] = mydict



	def unstore_data(self,material):

		for original in bpy.data.groups:
			if material.name == original.name:
				material.diffuse_color[0] = original["data"]["diffuse_color_0"]		
				material.diffuse_color[1] = original["data"]["diffuse_color_1"]		
				material.diffuse_color[2] = original["data"]["diffuse_color_2"]
				material.alpha =  original["data"]["alpha"]
				material.use_transparency = original["data"]["use_transparency"]
				material.use_raytrace= original["data"]["use_raytrace"]
				material.use_shadeless = original["data"]["use_shadeless"] 
				material.use_textures[0]=original["data"]["use_textures"]
				material.use_nodes=original["data"]["use_nodes"]
				material.raytrace_mirror.use=original["data"]["mirror"]

				if(material.texture_slots[0]):
					material.texture_slots[0].use_rgb_to_intensity=original["data"]["use_rgb_to_intensity"]


	def invoke(self,context,event):

		materials = bpy.data.materials
		lst = []

		scene = bpy.context.scene
		vegetal_only = scene.arx_alpha_vegetal_only

		# SWITCH TO ALPHA MODE
		if bpy.context.scene.arx_alpha == False:

			# switch button 
			bpy.context.scene.arx_alpha = True

			# create default material
			if(bpy.data.materials.find('Material')<0):
				bpy.data.materials.new('Material')

			# check for mesh without material
			for ob in bpy.data.objects:
				if ob.type == 'MESH':
					mesh=ob.data
					if len(mesh.materials) ==0:
						mesh.materials.append(bpy.data.materials['Material'])
			
			# BACKUP GLOBAL SETTINGS
			if("env" in bpy.data.groups):
				env=bpy.data.groups["env"]
			else:
				env = bpy.data.groups.new("env")

			env["use_ambient_occlusion"] = bpy.context.scene.world.light_settings.use_ambient_occlusion
			env["use_environment_light"] = bpy.context.scene.world.light_settings.use_environment_light
			env["use_raytrace"] = bpy.context.scene.render.use_raytrace
			env["use_textures"] = bpy.context.scene.render.use_textures
			env["use_shadows"] = bpy.context.scene.render.use_shadows
			env["horizon_color"] = bpy.context.scene.world.horizon_color
			env["zenith_color"] = bpy.context.scene.world.zenith_color
			env["use_sky_blend"] = bpy.context.scene.world.use_sky_blend
			env["use_nodes"] = bpy.context.scene.use_nodes


			# CHANGES GLOBAL SETTINGS

			bpy.context.scene.world.light_settings.use_ambient_occlusion = False
			bpy.context.scene.world.light_settings.use_environment_light = False
			bpy.context.scene.world.horizon_color = mathutils.Color((1,1,1))
			bpy.context.scene.world.zenith_color = mathutils.Color((1,1,1))
			bpy.context.scene.world.use_sky_blend = False
			bpy.context.scene.render.use_raytrace = False
			bpy.context.scene.render.use_textures = True
			bpy.context.scene.render.use_shadows = False
			bpy.context.scene.render.use_border = False
			bpy.context.scene.render.image_settings.file_format = 'PNG'
			bpy.context.scene.render.image_settings.color_mode = 'RGBA'
			bpy.context.scene.render.engine='BLENDER_RENDER'
		
			# LAMPS
			for object in bpy.context.scene.objects:
				if object.type == 'LAMP':
					if object.data.type == 'SUN':
						env["use_sky"] = object.data.sky.use_sky	
						object.data.sky.use_sky = False
		
			# MATERIALS
			for material in materials:

				textures = material.texture_slots

				# check if alpha rendering
				if(material.arx_alpha_exclude):

					# STORE DATA
					self.store_data(material)

					material.use_nodes=0
					material.use_transparency=1;
					material.alpha=0
					material.raytrace_mirror.use=False
					material.use_textures[0]=False
					material.transparency_method = 'Z_TRANSPARENCY'


				else:
					# IF GLOBAL ID
					if(material.arx_alpha_use_global_id==1):
						# USE EXISTING
						if(str(material.arx_alpha_global_id) in self.global_ids):
							self.r=self.global_ids[str(material.arx_alpha_global_id)][0]
							self.g=self.global_ids[str(material.arx_alpha_global_id)][1]
							self.b=self.global_ids[str(material.arx_alpha_global_id)][2]
						# CREATE NEW
						else:
							self.set_color()	
							self.global_ids[str(material.arx_alpha_global_id)]=[self.r,self.g,self.b]

							self.r=self.global_ids[str(material.arx_alpha_global_id)][0]
							self.g=self.global_ids[str(material.arx_alpha_global_id)][1]
							self.b=self.global_ids[str(material.arx_alpha_global_id)][2]
					# ELSE NEW ID
					else:
						if vegetal_only:
							if("vegetal_only" in self.global_ids):
								self.r=self.global_ids["vegetal_only"][0]
								self.g=self.global_ids["vegetal_only"][1]
								self.b=self.global_ids["vegetal_only"][2]
							else:
								self.set_color()	
								self.global_ids["vegetal_only"]=[self.r,self.g,self.b]
								self.r=self.global_ids["vegetal_only"][0]
								self.g=self.global_ids["vegetal_only"][1]
								self.b=self.global_ids["vegetal_only"][2]

						else:
							self.set_color()	

					# USE NODES
					mat_type=material.arx_material_type
					if (mat_type != ('Human' or 'Vegetal')):
						material.use_nodes=0


					# STORE DATA
					self.store_data(material)

					# COLORS
					material.diffuse_color[0] = self.r 		
					material.diffuse_color[1] = self.g  
					material.diffuse_color[2] = self.b 
					# SHADELESS
					material.use_shadeless = True

					# USE TEXTURE AS ALPHA
					if(material.arx_alpha_use_texture==1):
						material.transparency_method = 'Z_TRANSPARENCY'

						if(material.texture_slots[0] != ""):
							material.texture_slots[0].use_rgb_to_intensity=1
							material.texture_slots[0].texture.use_color_ramp=1
							material.texture_slots[0].color[0]=self.r
							material.texture_slots[0].color[1]=self.g
							material.texture_slots[0].color[2]=self.b

					# REGULAR
					else:
						material.alpha = 1
						material.use_transparency = False
						material.transparency_method = 'Z_TRANSPARENCY'
						material.use_textures[0]=False
				
			
		# RESTORE DATA
		else:
			bpy.context.scene.arx_alpha = False

			# MATERIALS
			for material in materials:
				self.unstore_data(material)
			

			# GLOBAL SETTINGS
			bpy.context.scene.world.light_settings.use_ambient_occlusion = bpy.data.groups["env"]["use_ambient_occlusion"] 
			bpy.context.scene.world.light_settings.use_environment_light = bpy.data.groups["env"]["use_environment_light"]			
			bpy.context.scene.render.use_raytrace = bpy.data.groups["env"]["use_raytrace"]
			bpy.context.scene.render.use_textures = bpy.data.groups["env"]["use_textures"]
			bpy.context.scene.render.use_shadows = bpy.data.groups["env"]["use_shadows"]
			bpy.context.scene.world.horizon_color = mathutils.Color(
								(bpy.data.groups["env"]["horizon_color"][0],
								bpy.data.groups["env"]["horizon_color"][1],
								bpy.data.groups["env"]["horizon_color"][2]))
			bpy.context.scene.world.zenith_color = mathutils.Color(
								(bpy.data.groups["env"]["zenith_color"][0],
								bpy.data.groups["env"]["zenith_color"][1],
								bpy.data.groups["env"]["zenith_color"][2]))
			bpy.context.scene.world.use_sky_blend = bpy.data.groups["env"]["use_sky_blend"]

			# LIGHTS
			for object in bpy.context.scene.objects:
				if object.type == 'LAMP':
					if object.data.type == 'SUN':
						object.data.sky.use_sky = bpy.data.groups["env"]["use_sky"]


		return {'FINISHED'}


# PANEL RENDER
class RVBA_Render_Panel(bpy.types.Panel):

	bl_space_type='PROPERTIES'
	bl_region_type='WINDOW'
	bl_context="render"
	bl_label="Index Render"

	bpy.types.Scene.arx_alpha_vegetal_only = bpy.props.BoolProperty("arx_alpha_vegetal_only", default=False)

	@classmethod
	def poll(cls,context):
		return context.scene

	def draw(self,context):

		scene = bpy.context.scene
		layout=self.layout
		col=layout.column(align=True)

		if bpy.context.scene.arx_alpha == False:
			col.operator(OP_Make_Alpha.bl_idname,text="Make")
		else:
			col.operator(OP_Make_Alpha.bl_idname,text="Restore")

		col.prop(scene,"arx_alpha_vegetal_only",text="Only vegetal")






