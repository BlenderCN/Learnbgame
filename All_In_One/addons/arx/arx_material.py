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

import bpy
import re
from . arx_base import Base_Material

# SHADOW MATERIAL
class OP_Make_Shadow_Material(Base_Material,bpy.types.Operator):

	bl_idname = "material.make_shadow_material"
	bl_label = "New material"
	bl_description = "Make a new material"

	def execute(self, context):

		if not self.error:
			self.report({'INFO'}, "OK"  )
		else:
			self.report({'INFO'},self.msg)

		return {'FINISHED'}

	def invoke(self,context,event):
		self.build_shadow_material(context,context.object)

		return self.execute(context)

# New Material with Tree Node (Blender + Cycles)
class OP_Make_New_Material(Base_Material,bpy.types.Operator):

	bl_idname = "material.make_new_material"
	bl_label = "New material"
	bl_description = "Make a new material"

	def execute(self, context):

		if not self.error:
			self.report({'INFO'}, "OK"  )
		else:
			self.report({'INFO'},self.msg)

		return {'FINISHED'}

	def invoke(self,context,event):
		self.build(context,context.object)

		return self.execute(context)

class OP_Material_Set_Global(bpy.types.Operator):

	bl_idname="material.set_global"
	bl_label="Set Global"
	bl_description="Set global materials"

	def invoke(self,context,event):

		for mat in bpy.data.materials:

			if(context.scene.arx_material_global_transparent_shadows_do):
				if(context.scene.arx_material_global_transparent_shadows):
					mat.use_transparent_shadows=True
				else:
					mat.use_transparent_shadows=False

			if(context.scene.arx_material_global_node_use_do):
				if(context.scene.arx_material_global_node_use):
					mat.use_nodes=True
				else:
					mat.use_nodes=False

			if(context.scene.arx_material_global_shadeless_do):
				if(context.scene.arx_material_global_shadeless):
					mat.use_shadeless=True
				else:
					mat.use_shadeless=False


		for image in bpy.data.images:

			if(context.scene.arx_material_global_premultiply_do):
				if(context.scene.arx_material_global_premultiply):
					image.premultiply=True
				else:
					image.premultiply=False

		return {'FINISHED'}

class OP_Globaly_Change_materials(bpy.types.Operator):

	bl_idname = "object.globaly_change_materials"
	bl_label = "Change material"
	bl_description = "Change all object's materials SRC by DEST "

	def execute(self, context):
		self.report({'INFO'}, "DONE"  )
		return {'FINISHED'}

	def invoke(self,context,event):
		objects = bpy.data.objects
		try: origin = bpy.context.scene['arx_mat_src']
		except: origin = 0
		try: dest  = bpy.context.scene['arx_mat_dst']
		except: dest=0

		if origin != 0 and dest != 0:
			for ob in objects:
				if ob.type == 'MESH':
					if len(ob.material_slots) > 0:
						materials = ob.material_slots
						for mat in materials:
							print(mat.name)
							if mat.name == origin:
								ob.material_slots[mat.name].material = bpy.data.materials[dest]

		return self.execute(context)

class OP_Remove_all_materials(bpy.types.Operator):

	bl_idname = "object.remove_all_materials"
	bl_label = "Remove all materials"
	bl_description = "Remove all materials by default Material"

	def invoke(self,context,event):
		objects = bpy.data.objects
		matname = 0

		# create default material
		if(bpy.data.materials.find('Material')<0):
			bpy.data.materials.new('Material')

		for ob in objects:
			if ob.type == 'MESH':
				if len(ob.material_slots) > 0:
					materials = ob.material_slots
					for mat in materials:
						ob.material_slots[mat.name].material = bpy.data.materials['Material']
		
		return {'FINISHED'}


class OP_Remove_double_materials(bpy.types.Operator):

	bl_idname = "object.remove_double_materials"
	bl_label = "Remove double materials"
	bl_description = "Replace all material.xxx by material"

	msg=""

	def execute(self, context):

		self.report({'INFO'}, "[Double materials]"  )
		self.report({'INFO'}, self.msg)
		self.report({'INFO'}, "[DONE]"  )
		return {'FINISHED'}

	def invoke(self,context,event):

		objects = bpy.data.objects

		for ob in objects:
			if ob.type == 'MESH':
				if len(ob.material_slots) > 0:
					materials = ob.material_slots
					i = 0
					for mat in materials:
						matName = mat.name
						# all digits + - _
						pat = re.compile('([\w\-_]*)\.(\w*)')
						mat = pat.match(matName)
					
						if (mat != None):

							mat.groups()
							oldName = mat.groups()[0]

							try:	
							
								ob.material_slots[matName].material = bpy.data.materials[oldName]
								self.msg+=matName+" > "+oldName+"\n"

								# clear users
								if(bpy.context.scene.arx_mat_user_clear):
									bpy.data.materials[matName].user_clear()
							except:
								continue
		return self.execute(context) 


class OP_Remove_all_unused_materials(bpy.types.Operator):

	bl_idname = "object.remove_all_unused_materials"
	bl_label = "Remove unsused materials"
	bl_description = "Remove ALL unused materials (not used by any faces in object)"

	loop=1
	lst=[]
	msg=""

	def execute(self, context):
		self.report({'INFO'},self.msg)
		self.report({'INFO'},"DONE")
		return {'FINISHED'}

	def get_indices(self,ob):

		# for all faces : get material indices
		mesh = ob.data
		mesh.update()
		faces=mesh.polygons
		self.lst=[]
		for face in faces:
			add=1
			indice = face.material_index 
			for item in self.lst:
				if item == indice:
					add=0
			if add:
				self.lst.append(indice)

	def remove_slot(self,ob):

		materials = ob.material_slots
		# reset looping
		self.loop=0

		i=0
		for mat in materials:

			# check if this indice is in use (lst)
			remove=1
			if(len(self.lst)==0): remove=0
			for item in self.lst:
				if item == i:
					remove =0 
				
			# delete unused slot
			if remove:
				# set loop
				self.loop=1
				# set current object to be selected
				bpy.context.scene.objects.active = bpy.data.objects[ob.name] 
				ob.active_material_index=i
				self.msg += ob.name + " removed: " + materials[i].name + "\n"
				bpy.ops.object.material_slot_remove('EXEC_SCREEN')
				break

			i+=1
		

	def invoke(self,context,event):
		objects = bpy.data.objects

		for ob in objects:
			if ob.type == 'MESH':
				if len(ob.material_slots) > 0:

					self.loop=1
					while(self.loop==1):
						self.get_indices(ob)
						self.remove_slot(ob)


		return self.execute(context)


class OP_Remove_unused_materials(bpy.types.Operator):

	bl_idname = "object.remove_all_unused_materials"
	bl_label = "Remove unsused materials"
	bl_description = "Remove ALL unused materials (not used by any faces in object)"

	loop=1
	lst=[]
	msg=""
	_selected=0

	def execute(self, context):
		if(self._selected):
			self.report({'INFO'},self.msg)
			self.report({'INFO'},"DONE")
		else:
			self.report({'INFO'},"[WARNING] no object selected")
			
		return {'FINISHED'}

	def get_indices(self,ob):

		# for all faces : get material indices
		mesh = ob.data
		mesh.update()
		faces=mesh.polygons
		self.lst=[]
		for face in faces:
			add=1
			indice = face.material_index 
			for item in self.lst:
				if item == indice:
					add=0
			if add:
				self.lst.append(indice)

	def remove_slot(self,ob):

		materials = ob.material_slots
		# reset looping
		self.loop=0

		i=0
		for mat in materials:

			# check if this indice is in use (lst)
			remove=1
			if(len(self.lst)==0): remove=0
			for item in self.lst:
				if item == i:
					remove =0 
				
			# delete unused slot
			if remove:
				# set loop
				self.loop=1
				# set current object to be selected
				bpy.context.scene.objects.active = bpy.data.objects[ob.name] 
				ob.active_material_index=i
				self.msg += ob.name + " removed: " + materials[i].name + "\n"
				bpy.ops.object.material_slot_remove('EXEC_SCREEN')
				break

			i+=1
		

	def invoke(self,context,event):

		#ob = bpy.context.active_object
			
		objects=bpy.context.selected_objects
		if(len(objects)>0):
			self._selected=1
			for ob in objects:
				if ob.type == 'MESH':
					if len(ob.material_slots) > 0:

						self.loop=1
						while(self.loop==1):
							self.get_indices(ob)
							self.remove_slot(ob)
		else:
			self._selected=0


		return self.execute(context)

# PANEL MATERIAL GLOBAL
class Panel_Material_Set_Global(bpy.types.Panel):

	bl_space_type='PROPERTIES'
	bl_region_type='WINDOW'
	bl_context="material"
	bl_label="Global Materials"

	bpy.types.Scene.arx_material_global_transparent_shadows = bpy.props.BoolProperty("arx_material_global_transparent_shadows", default=False)
	bpy.types.Scene.arx_material_global_transparent_shadows_do = bpy.props.BoolProperty("arx_material_global_transparent_shadows_do", default=False)

	bpy.types.Scene.arx_material_global_node_use = bpy.props.BoolProperty("arx_material_global_node_use", default=False)
	bpy.types.Scene.arx_material_global_node_use_do = bpy.props.BoolProperty("arx_material_node_use_do", default=False)

	bpy.types.Scene.arx_material_global_shadeless = bpy.props.BoolProperty("arx_material_global_shadeless",default=False)
	bpy.types.Scene.arx_material_global_shadeless_do = bpy.props.BoolProperty("arx_material_global_shadeless_do",default=False)
	bpy.types.Scene.arx_material_global_premultiply = bpy.props.BoolProperty("arx_material_global_premultiply",default=False)
	bpy.types.Scene.arx_material_global_premultiply_do = bpy.props.BoolProperty("arx_material_global_premultiply_do",default=False)

	bpy.types.Scene.arx_alpha = bpy.props.BoolProperty("arx_alpha",default=False)
	bpy.types.Scene.arx_mat_src  = bpy.props.StringProperty("arx_mat_src")
	bpy.types.Scene.arx_mat_dst  = bpy.props.StringProperty("arx_mat_dst")
	bpy.types.Scene.arx_mat_user_clear = bpy.props.BoolProperty("arx_mat_user_clear",default=True)

	def draw(self,context):



		col=self.layout.column(align=True)
		col.label("Materials",icon='MODIFIER')
		col.prop(context.scene,"arx_mat_src", text="Source") 
		col.prop(context.scene,"arx_mat_dst", text="Dest")

		row = self.layout.row()
		row.operator(OP_Globaly_Change_materials.bl_idname,text="Replace material")

		col=self.layout.column(align=True)

		col.prop(context.scene,"arx_mat_user_clear",text="clear users")
		col.operator(OP_Remove_double_materials.bl_idname,text="Remove double materials")
		col.operator(OP_Remove_all_unused_materials.bl_idname,text="Remove unused materials")
		col.operator(OP_Remove_unused_materials.bl_idname,text="Remove selected unused materials")
		col.operator(OP_Remove_all_materials.bl_idname,text="Remove all materials")


		col.separator()

		row=col.row()
		row.alignment = 'LEFT'
		row.prop(context.scene,"arx_material_global_transparent_shadows_do",text="")
		row.prop(context.scene,"arx_material_global_transparent_shadows",text="")
		row.label("Transparent Shadows")

		row=col.row()
		row.alignment = 'LEFT'
		row.prop(context.scene,"arx_material_global_node_use_do",text="")
		row.prop(context.scene,"arx_material_global_node_use",text="")
		row.label("Use Node")

		row=col.row()
		row.alignment = 'LEFT'
		row.prop(context.scene,"arx_material_global_shadeless_do",text="")
		row.prop(context.scene,"arx_material_global_shadeless",text="")
		row.label("Shadeless")

		row=col.row()
		row.alignment = 'LEFT'
		row.prop(context.scene,"arx_material_global_premultiply_do",text="")
		row.prop(context.scene,"arx_material_global_premultiply",text="")
		row.label("Premultiply")

		col=self.layout.column(align=True)
		row=col.row()
		row.operator(OP_Material_Set_Global.bl_idname,text="Set Materials")

# PANEL MATERIAL
class RVBA_Material_Panel(bpy.types.Panel):

	bl_space_type='PROPERTIES'
	bl_region_type='WINDOW'
	bl_context="material"
	bl_label="Alpha Tools"

	bpy.types.Material.arx_alpha_use_texture = bpy.props.BoolProperty("arx_alpha_use_texture", default=False)
	bpy.types.Material.arx_alpha_exclude = bpy.props.BoolProperty("arx_alpha_exclude", default=False)
	bpy.types.Material.arx_alpha_use_global_id = bpy.props.BoolProperty("arx_alpha_use_global_id", default=False)
	bpy.types.Material.arx_alpha_global_id = bpy.props.IntProperty("arx_alpha_global_id", default=False)
	bpy.types.Material.arx_material_is_shadow = bpy.props.IntProperty("arx_material_is_shadow", default=False)

	bpy.types.Material.arx_material_type = bpy.props.EnumProperty(
						items=[
							("Default","Default","Default material"),
							("Texture","Texture","Texture material"),
							("Vegetal","Vegetal","Vegetal material"),
							("Human","Human","Human material"),
							("Cutout","Cutout","Cutout"),
							],
						name="arx_material_type")

	def draw(self,context):

		mat=context.material
		if(mat):
			row=self.layout.row()
			row.prop(mat,"arx_alpha_use_texture",text="use texture for alpha rendering")
			row=self.layout.row()
			row.prop(mat,"arx_alpha_exclude",text="exclude from alpha rendering")
			row=self.layout.row()
			row.prop(mat,"arx_alpha_use_global_id",text="use global ID")
			row.prop(mat,"arx_alpha_global_id",text="ID")

			col=self.layout.column(align=True)
			col.prop(mat,"arx_material_type",text="")
			col.operator(OP_Make_New_Material.bl_idname,text="Build material")

			col=self.layout.column(align=True)
			col.operator(OP_Make_Shadow_Material.bl_idname,text="Build shadow material")



