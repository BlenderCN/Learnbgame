bl_info = {
	"name": "Asset Creation Toolset",
	"description": "Toolset for easy create assets for Unity 3D/3D Stocks/etc.",
	"author": "Ivan 'mrven' Vostrikov",
	"version": (2, 2, 0),
	"blender": (2, 7, 9),
	"location": "3D View > Object Mode > Toolshelf > Asset Creation Toolset",
	"warning": "For use tool 'Texture to Vertex Colors' requires enabled 'Bake UV-Texture to Vertex Colors' Add-on",
	"category": "Object",
}

import bpy
import os
import bmesh
import math
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, CollectionProperty
from bpy.types import Operator, OperatorFileListElement


#-------------------------------------------------------
# FBX-Export
class Multi_FBX_export(bpy.types.Operator):
	"""Export FBXs to Unity"""
	bl_idname = "object.multi_fbx_export"
	bl_label = "Export FBXs to Unity"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		blend_not_saved = False
		#check saved blend file
		if len(bpy.data.filepath) == 0:
			self.report({'INFO'}, 'Objects don\'t export, because Blend file is not saved')
			blend_not_saved = True
		if blend_not_saved == False:
			# Save selected objects
			current_selected_obj = bpy.context.selected_objects
			current_unit_system = bpy.context.scene.unit_settings.system
			name = bpy.context.active_object.name
			bpy.context.scene.unit_settings.system = 'METRIC'
			bpy.context.scene.unit_settings.scale_length = 0.01
			active_ob = context.active_object
			current_pivot_point = bpy.context.space_data.pivot_point

			#Export as one fbx
			if context.scene.export_one_fbx == True and len(bpy.context.selected_objects) > 1:

				print('EXPORTING AS ONE')
				##### EXPORT SINGLE ASSET #####

				# Set Transform Pivot
				bpy.ops.view3d.snap_cursor_to_active()
				bpy.context.space_data.pivot_point = 'CURSOR'


				# Edit Transforms for Unity
				for ob in current_selected_obj:
					if ob.type == 'MESH':
						bpy.context.scene.objects.active = ob

						# X-rotation fix
						bpy.ops.object.mode_set(mode='EDIT')
						bpy.ops.mesh.select_all(action='SELECT')
						bpy.ops.transform.resize(value=(100, 100, 100))
						bpy.ops.object.mode_set(mode='OBJECT')

				#Create export folder
				path = bpy.path.abspath('//Meshes/')
				if not os.path.exists(path):
					os.makedirs(path)

				# Revert Active Object
				bpy.context.scene.objects.active = active_ob

				# Export as One FBX
				bpy.ops.export_scene.fbx(filepath=str(path + name + '.fbx'), version='BIN7400', ui_tab='MAIN', use_selection=True, global_scale=1, apply_unit_scale=True)

				# Revert Transforms
				for ob in current_selected_obj:
					if ob.type == 'MESH':
						bpy.context.scene.objects.active = ob
						
						# Revert Transforms
						bpy.ops.object.mode_set(mode='EDIT')
						bpy.ops.mesh.select_all(action='SELECT')
						bpy.ops.transform.resize(value=(0.01, 0.01, 0.01))
						bpy.ops.object.mode_set(mode='OBJECT')

						
				# Revert Active Object
				bpy.context.scene.objects.active = active_ob
				bpy.context.space_data.pivot_point = 'MEDIAN_POINT'



			else:
			#Individual Export
				current_pivot_point = bpy.context.space_data.pivot_point
				bpy.context.space_data.pivot_point = 'CURSOR'


				for ob in current_selected_obj:
					# Select only current object
					bpy.ops.object.select_all(action='DESELECT')
					if ob.type == 'MESH':
						ob.select = True
						bpy.context.scene.objects.active = ob
						bpy.ops.view3d.snap_cursor_to_selected()
						object_loc = bpy.context.scene.cursor_location.copy()
						bpy.ops.view3d.snap_cursor_to_center()
						bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)

						# Edit Transforms for Unity
						bpy.ops.object.mode_set(mode='EDIT')
						bpy.ops.mesh.select_all(action='SELECT')
						bpy.ops.transform.resize(value=(100, 100, 100))
						bpy.ops.transform.rotate(value = -1.5708, axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'GLOBAL')
						bpy.ops.object.mode_set(mode='OBJECT')
						bpy.ops.transform.rotate(value = 1.5708, axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'GLOBAL')   

						# FBX Export
						path = bpy.path.abspath('//Meshes/')
						if not os.path.exists(path):
							os.makedirs(path)
						name = ob.name
						
						bpy.ops.export_scene.fbx(filepath=str(path + name + '.fbx'), version='BIN7400', ui_tab='MAIN', use_selection=True, global_scale=1, apply_unit_scale=True)
						bpy.context.scene.cursor_location = object_loc
						bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
						bpy.ops.view3d.snap_cursor_to_selected()

						bpy.ops.object.mode_set(mode='EDIT')
						bpy.ops.transform.resize(value=(0.01, 0.01, 0.01))
						bpy.ops.transform.rotate(value=1.5708, axis=(1, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='ENABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
						bpy.ops.object.mode_set(mode='OBJECT')
						bpy.context.object.rotation_euler[0] = 0
						bpy.context.space_data.pivot_point = 'MEDIAN_POINT'







					#Development Function
				'''
					if context.scene.fbx_save_rotation == False:
						# Select only current object
						bpy.ops.object.select_all(action='DESELECT')
						if x.type == 'MESH':
							x.select = True
							bpy.ops.view3d.snap_cursor_to_selected()
							object_loc = bpy.context.scene.cursor_location.copy()
							bpy.ops.view3d.snap_cursor_to_center()
							bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
							# X-rotation fix
							bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
							bpy.ops.transform.rotate(value = -1.5708, axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'GLOBAL')
							bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
							bpy.ops.transform.rotate(value = 1.5708, axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'GLOBAL')
							# FBX Export
							path = bpy.path.abspath('//FBXs/')
							if not os.path.exists(path):
								os.makedirs(path)
							name = x.name
							bpy.ops.transform.resize(value=(100, 100, 100))
							bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
							bpy.ops.export_scene.fbx(filepath=str(path + name + '.fbx'), version='BIN7400', ui_tab='MAIN', use_selection=True, global_scale=1, apply_unit_scale=True)
							bpy.context.scene.cursor_location = object_loc
							bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
							bpy.ops.view3d.snap_cursor_to_center()
							bpy.ops.transform.resize(value=(0.01, 0.01, 0.01))
							bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
					if context.scene.fbx_save_rotation == True:
						# Select only current object
						bpy.ops.object.select_all(action='DESELECT')
						if x.type == 'MESH':
							x.select = True
							bpy.ops.view3d.snap_cursor_to_selected()
							object_loc = bpy.context.scene.cursor_location.copy()
							bpy.ops.view3d.snap_cursor_to_center()
							bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
							# X-rotation fix
							#bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
							bpy.ops.object.mode_set(mode = 'EDIT')
							bpy.ops.mesh.reveal()
							bpy.ops.mesh.select_all(action='SELECT')
							bpy.context.space_data.pivot_point = 'CURSOR'
							bpy.ops.transform.rotate(value = -1.5708, axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'LOCAL')
							bpy.context.space_data.pivot_point = 'MEDIAN_POINT'
							bpy.ops.object.mode_set(mode = 'OBJECT')
							bpy.ops.transform.rotate(value = 1.5708, axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'LOCAL')
							# FBX Export
							path = bpy.path.abspath('//FBXs/')
							if not os.path.exists(path):
								os.makedirs(path)
							name = x.name
							bpy.ops.transform.resize(value=(100, 100, 100))
							bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
							bpy.ops.export_scene.fbx(filepath=str(path + name + '.fbx'), version='BIN7400', ui_tab='MAIN', use_selection=True, global_scale=1, apply_unit_scale=True)
							bpy.context.scene.cursor_location = object_loc
							bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
							bpy.ops.view3d.snap_cursor_to_center()
							bpy.ops.transform.resize(value=(0.01, 0.01, 0.01))
							bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
					'''
				bpy.context.space_data.pivot_point = current_pivot_point
			# Select again objects
			for j in current_selected_obj:
				j.select = True;
			bpy.context.scene.unit_settings.scale_length = 1
			bpy.context.scene.unit_settings.system = current_unit_system
		
		return {'FINISHED'}

#-------------------------------------------------------
# Palette Texture Creator
class PaletteCreate(bpy.types.Operator):
	"""Palette Texture Creator"""
	bl_idname = "object.palette_creator"
	bl_label = "Palette Texture Creator"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		#check opened image editor window
		IE_area = 0
		flag_exist_area = False
		for area in range(len(bpy.context.screen.areas)):
			if bpy.context.screen.areas[area].type == 'IMAGE_EDITOR':
				IE_area = area
				flag_exist_area = True
				bpy.context.screen.areas[area].type = 'CONSOLE'

		# get selected MESH objects and get active object name
		current_objects = []
		for selected_mesh in bpy.context.selected_objects:
			if selected_mesh.type == 'MESH':
				current_objects.append(selected_mesh)
				# remove empty material slots
				for q in reversed(range(len(selected_mesh.data.materials))):
					if selected_mesh.data.materials[q] == None:
						bpy.context.object.active_material_index = q
						# unlink empty slots
						selected_mesh.data.materials.pop(q, update_data=True)
						
		add_name_palette = bpy.context.active_object.name

		# set tool setting for uv editor
		bpy.context.scene.tool_settings.use_uv_select_sync = False
		bpy.context.scene.tool_settings.uv_select_mode = 'FACE'

		# get materials from selected objects
		me = []
		for x in current_objects:
			me += x.data.materials

		# check exist material Palette_background
		flag_exist_mat = False
		for a in range(len(bpy.data.materials)):
			if bpy.data.materials[a].name == 'Palette_background':
				flag_exist_mat = True
				palette_back_color = bpy.data.materials[a]

		# create or not palette background material
		if flag_exist_mat == False:
			palette_back_color = bpy.data.materials.new('Palette_background')
			palette_back_color.diffuse_color = 0.8, 0.8, 0.8

		# check exist palette plane
		flag_exist_obj = False
		for o in range(len(bpy.data.objects)):
			if bpy.data.objects[o].name == ('Palette_' + add_name_palette):
				flag_exist_obj = True

		if flag_exist_obj == True:
			bpy.ops.object.select_all(action='DESELECT')
			bpy.data.objects['Palette_' + add_name_palette].select = True
			bpy.ops.object.delete()
				
		bpy.ops.mesh.primitive_plane_add(location = (0, 0, 0))
		pln = bpy.context.object
		pln.name = 'Palette_' + add_name_palette

		# Add palette background material to palette plane
		pln.data.materials.append(palette_back_color)

		# Add materials to palette plane
		mat_offset = len(me)
		i = 0
		for i in range(mat_offset):
			flag_non = False
			palette_mat = pln.data.materials
			palette_mat_len = len(palette_mat)
			j = 0
			
			for j in range(palette_mat_len):
				if palette_mat[j] == me[i]:
					flag_non = True
					
			if flag_non == False:
				pln.data.materials.append(me[i])
				
		# compute number of subdivide palette plane from number of materials
		palette_mat = pln.data.materials
		palette_mat_len = len(palette_mat)
		palette_mat_wobg = palette_mat_len - 1
		number_of_subdiv = 0
		if palette_mat_wobg > 1 and palette_mat_wobg <= 4:
			number_of_subdiv = 1
			
		if palette_mat_wobg > 4 and palette_mat_wobg <= 16:
			number_of_subdiv = 2

		if palette_mat_wobg > 16 and palette_mat_wobg <= 64:
			number_of_subdiv = 3

		if palette_mat_wobg > 64 and palette_mat_wobg <= 256:
			number_of_subdiv = 4
			
		# subdivide palette plane
		bpy.ops.object.mode_set(mode = 'EDIT')
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
		n = 0
		for n in range(number_of_subdiv):
			bpy.ops.mesh.subdivide(smoothness=0)

		#TEST check exist texture image

		# create texture and unwrap
		bpy.ops.mesh.select_all(action='SELECT')

		#TEST check exist texture image
		flag_exist_texture = False
		for t in range(len(bpy.data.images)):
			if bpy.data.images[t].name == ('Palette_' + add_name_palette):
				flag_exist_texture = True
				
		# create or not texture
		if flag_exist_texture == False:
			bpy.ops.image.new( name='Palette_' + add_name_palette, width = 32, height = 32)

		bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
		bpy.data.screens['UV Editing'].areas[1].spaces[0].image = bpy.data.images['Palette_' + add_name_palette]


		# set materials to plane's polygons
		bpy.ops.object.mode_set(mode = 'OBJECT')
		ob = bpy.context.object

		for poly in ob.data.polygons:   
			if (poly.index + 1) < palette_mat_len:
				poly.material_index = poly.index + 1

		# bake palette texture
		bpy.context.scene.render.bake_type = 'TEXTURE' 
		bpy.ops.object.bake_image()

		# Create collection materials with (mat_name, uv_x_mat, uv_y_mat)
		mat_coll_array = []
		collect_uv_mat = 1
		current_area = bpy.context.area.type

		for collect_uv_mat in range(palette_mat_len - 1):

			# select polygon
			bpy.ops.object.mode_set(mode = 'EDIT')
			bpy.ops.mesh.select_all(action='DESELECT')
			bpy.ops.object.mode_set(mode = 'OBJECT')
			ob.data.polygons[collect_uv_mat].select = True
			bpy.ops.object.mode_set(mode = 'EDIT')

			# get mat_name
			mat_index = ob.data.polygons[collect_uv_mat].material_index
			mat_name = ob.data.materials[mat_index].name

			bpy.context.area.type = 'IMAGE_EDITOR'
			
			if bpy.context.area.spaces[0].image != None:
				if bpy.context.area.spaces[0].image.name == 'Render Result':
					bpy.context.area.spaces[0].image = None
			
			bpy.ops.uv.snap_cursor(target='SELECTED')

			# get coord center poly
			x_loc = (1/256)*bpy.context.area.spaces[0].cursor_location[0]
			y_loc = (1/256)*bpy.context.area.spaces[0].cursor_location[1]
			mat_coll_list = [mat_name, x_loc, y_loc]
			mat_coll_array.append(mat_coll_list)
			
		bpy.ops.object.mode_set(mode = 'OBJECT')

		bpy.context.area.type = 'VIEW_3D'
			
		for r in current_objects:   
			bpy.ops.object.select_all(action='DESELECT')
			r.select = True
			# unwrap selected objects and add palette texture
			bpy.context.scene.objects.active = r	
			bpy.ops.object.mode_set(mode = 'EDIT')
			bpy.ops.mesh.select_all(action='SELECT')
			bpy.ops.uv.smart_project(angle_limit=89, island_margin=0.01, user_area_weight=0, use_aspect=True)
			bpy.data.screens['UV Editing'].areas[1].spaces[0].image = bpy.data.images['Palette_' + add_name_palette]
			
			bpy.ops.mesh.select_all(action='DESELECT')
			# select poly with 1 material 
			r_mats = r.data.materials
			r_mats_len = len(r_mats)
			r_mat_index = 0
			print(r_mats, r_mats_len)
			for r_mat_index in range(r_mats_len):
				bpy.ops.mesh.select_all(action='DESELECT')
				bpy.context.object.active_material_index = r_mat_index
				r_mat_name = bpy.context.object.data.materials[r_mat_index].name
				bpy.ops.object.material_slot_select()
				bpy.ops.uv.select_all(action = 'SELECT')
				print(r_mat_index)
				# get XY material on UV
				h = 0
				r_mat_x = 0
				r_mat_y = 0
				for h in range (len(mat_coll_array)):
					if (r_mat_name == mat_coll_array[h][0]):
						r_mat_x = mat_coll_array[h][1]
						r_mat_y = mat_coll_array[h][2]
				
				# scale uv to color on palette texture
				bpy.context.area.type = 'IMAGE_EDITOR'
				bpy.ops.uv.cursor_set(location = (r_mat_x, r_mat_y))
				bpy.context.space_data.pivot_point = 'CURSOR'
				bpy.ops.transform.resize(value=(0, 0, 1),\
					 constraint_axis=(False, False, False),\
					  constraint_orientation='GLOBAL', mirror=False,\
					   proportional='DISABLED', proportional_edit_falloff='SMOOTH',\
						proportional_size=1, snap=False, snap_target='CLOSEST',\
						 snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0),\
						  texture_space=False, release_confirm=False)
						  
			bpy.ops.object.mode_set(mode = 'OBJECT')
		
		# Delete Palette Plane
		bpy.ops.object.select_all(action='DESELECT')
		bpy.data.objects['Palette_' + add_name_palette].select = True
		bpy.ops.object.delete()
		
		# Select again objects
		for j in current_objects:
			j.select = True;		
			
		bpy.context.area.type = current_area

		if flag_exist_area == True:
			bpy.context.screen.areas[IE_area].type = 'IMAGE_EDITOR'

		return {'FINISHED'}

#-------------------------------------------------------
# Quick Bake Vertex Colors from Texture
class BakeVC(bpy.types.Operator):
	"""Quick Bake Vertex Colors from Texture"""
	bl_idname = "object.bake_vc"
	bl_label = "Quick Bake Vertex Colors from Texture"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		selected_obj = bpy.context.selected_objects
		active_obj = bpy.context.active_object
		
		for x in selected_obj:
			bpy.ops.object.select_all(action='DESELECT')
			x.select = True
			if x.type == 'MESH':
				if len(x.data.uv_layers) > 0:
					bpy.context.scene.objects.active = x
					bpy.ops.paint.vertex_paint_toggle()
					bpy.context.object.data.use_paint_mask = True
					bpy.ops.paint.face_select_all(action='SELECT')
					bpy.ops.uv.bake_texture_to_vcols()
					bpy.ops.object.mode_set(mode='OBJECT')
					bpy.ops.mesh.uv_texture_remove()
			
		# Select again objects
		for j in selected_obj:
			j.select = True;
		
		bpy.context.scene.objects.active = active_obj
							
		return {'FINISHED'}

#-------------------------------------------------------
# Clear Custom Split Normals
class ClearNormals(bpy.types.Operator):
	"""Clear Custom Split Normals"""
	bl_idname = "object.clear_normals"
	bl_label = "Clear Custom Split Normals"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		selected_obj = bpy.context.selected_objects
		active_obj = bpy.context.active_object
		
		for x in selected_obj:
			bpy.ops.object.select_all(action='DESELECT')
			x.select = True
			if x.type == 'MESH':
				bpy.context.scene.objects.active = x
				bpy.ops.mesh.customdata_custom_splitnormals_clear()
				bpy.context.object.data.auto_smooth_angle = 3.14159
				
		# Select again objects
		for j in selected_obj:
			j.select = True;
		
		bpy.context.scene.objects.active = active_obj
							
		return {'FINISHED'}		
		
#-------------------------------------------------------
# Recalculate Normals
class CalcNormals(bpy.types.Operator):
	"""Recalculate Normals"""
	bl_idname = "object.calc_normals"
	bl_label = "Flip/Calculate Normals"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		selected_obj = bpy.context.selected_objects
		active_obj = bpy.context.active_object
		
		for x in selected_obj:
			bpy.ops.object.select_all(action='DESELECT')
			x.select = True
			if x.type == 'MESH':
				bpy.context.scene.objects.active = x
				bpy.ops.object.mode_set(mode = 'EDIT')
				bpy.ops.mesh.reveal()
				bpy.ops.mesh.select_all(action='SELECT')
				if context.scene.calc_normals_en == False:
					bpy.ops.mesh.flip_normals()
				else:
					bpy.ops.mesh.normals_make_consistent(inside=context.scene.normals_inside)
				bpy.ops.mesh.select_all(action='DESELECT')
				bpy.ops.object.mode_set(mode='OBJECT')
				
		# Select again objects
		for j in selected_obj:
			j.select = True;
		
		bpy.context.scene.objects.active = active_obj
							
		return {'FINISHED'}
		
#-------------------------------------------------------
# Batch Import FBX and OBJ
class ImportFBXOBJ(bpy.types.Operator, ImportHelper):
	"""Batch Import FBX and OBJ"""
	bl_idname = "object.import_fbxobj"
	bl_label = "Import FBXs/OBJs"
	bl_options = {'REGISTER', 'UNDO'}
	files = CollectionProperty(name="File Path", type=OperatorFileListElement)
	directory = StringProperty(subtype="DIR_PATH")
	
	def execute(self, context):
		directory = self.directory
		for f in self.files:
			filepath = os.path.join(directory, f.name)
			extension = (os.path.splitext(f.name)[1])[1:]
			#print(filepath)
			#print(extension)
			if extension == "fbx" or extension == "FBX":
				bpy.ops.import_scene.fbx(filepath = filepath)
			if extension == "obj" or extension == "OBJ":
				bpy.ops.import_scene.obj(filepath = filepath)
			
		return {'FINISHED'}

#-------------------------------------------------------
# Rename object(s)
class RenameObject(bpy.types.Operator):
	"""Rename object(s)"""
	bl_idname = "object.rename_object"
	bl_label = "Rename object(s)"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		old_str = context.scene.old_text
		new_str = context.scene.new_text
		selected_obj = bpy.context.selected_objects
		
		#New name
		if bpy.context.scene.rename_select == '3':
			for x in selected_obj:
				x.name = old_str
		
		#Add Postfix
		if bpy.context.scene.rename_select == '1':
			for x in selected_obj:
				ob_name = x.name
				new_name = ob_name + old_str
				x.name = new_name
		
		#Add Prefix
		if bpy.context.scene.rename_select == '0':
			for x in selected_obj:
				ob_name = x.name
				new_name = old_str + ob_name
				x.name = new_name
		
		#Replace
		if bpy.context.scene.rename_select == '2':
			for x in selected_obj:
				if x.name.find(old_str) > -1:
					ob_name = x.name
					new_name = ob_name.replace(old_str, new_str)
					x.name = new_name
					
		return {'FINISHED'}

# Rename UV(s)
class RenameUV(bpy.types.Operator):
	"""Rename UV(s)"""
	bl_idname = "object.uv_rename"
	bl_label = "Rename UV(s)"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		selected_obj = bpy.context.selected_objects	
		uv_index = bpy.context.scene.uv_layer_index
		uv_name = bpy.context.scene.uv_name
		
		for x in selected_obj:
			if len(x.data.uv_layers) > 0:
				if uv_index < len(x.data.uv_layers):
					x.data.uv_layers[uv_index].name = uv_name
				
		return {'FINISHED'}
		

#-------------------------------------------------------
# UV-Remover
class UVremove(bpy.types.Operator):
	"""Remove UV layer"""
	bl_idname = "object.uv_remove"
	bl_label = "Remove UV layer"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		selected_obj = bpy.context.selected_objects
		active_obj = bpy.context.active_object
		for x in selected_obj:
			bpy.ops.object.select_all(action='DESELECT')
			x.select = True
			bpy.context.scene.objects.active = x
			if x.type == 'MESH':
				for a in range(len(x.data.uv_layers)):
					bpy.ops.mesh.uv_texture_remove()			
		
		# Select again objects
		for j in selected_obj:
			j.select = True;
			
		bpy.context.scene.objects.active = active_obj
		
		return {'FINISHED'}

#------------------Align Origin To Min-------------------------------
class AlignMin(bpy.types.Operator):
	"""Origin To Min """
	bl_idname = "object.align_min"
	bl_label = "Origin To Min"
	bl_options = {'REGISTER', 'UNDO'}
	TypeAlign = bpy.props.StringProperty()
	
	def execute(self, context):

		# Save selected objects and current position of 3D Cursor
		current_selected_obj = bpy.context.selected_objects
		current_active_obj = bpy.context.active_object
		saved_cursor_loc = bpy.context.scene.cursor_location.copy()
		bpy.ops.object.mode_set(mode = 'OBJECT')
		# Change individual origin point
		for x in current_selected_obj:
			# Select only current object (for setting origin)
			bpy.ops.object.select_all(action='DESELECT')
			x.select = True
			bpy.context.scene.objects.active = x
			# Save current origin and relocate 3D Cursor
			saved_origin_loc = x.location.copy() 
			if x.type == 'MESH':
				bpy.ops.object.mode_set(mode = 'EDIT')
				
				if self.TypeAlign == 'X':
					MinCo = FindMinMaxVerts(x, 0, 0)
					if MinCo == None:
						MinCo = saved_origin_loc[0]
				if self.TypeAlign == 'Y':
					MinCo = FindMinMaxVerts(x, 1, 0)
					if MinCo == None:
						MinCo = saved_origin_loc[1]
				if self.TypeAlign == 'Z':
					MinCo = FindMinMaxVerts(x, 2, 0)
					if MinCo == None:
						MinCo = saved_origin_loc[2]
				
				if context.scene.align_geom_to_orig == False:
					bpy.ops.object.mode_set(mode = 'OBJECT')
					if self.TypeAlign == 'X':
						bpy.context.scene.cursor_location = [MinCo, saved_origin_loc[1], saved_origin_loc[2]] 
					if self.TypeAlign == 'Y':
						bpy.context.scene.cursor_location = [saved_origin_loc[0], MinCo, saved_origin_loc[2]] 
					if self.TypeAlign == 'Z':
						bpy.context.scene.cursor_location = [saved_origin_loc[0], saved_origin_loc[1], MinCo]
						
					# Apply origin to Cursor position
					bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
					# Reset 3D Cursor position  
					bpy.context.scene.cursor_location = saved_cursor_loc
				
				if context.scene.align_geom_to_orig == True:
					if self.TypeAlign == 'X':
						Difference = saved_origin_loc[0] - MinCo
					if self.TypeAlign == 'Y':
						Difference = saved_origin_loc[1] - MinCo
					if self.TypeAlign == 'Z':
						Difference = saved_origin_loc[2] - MinCo
					
					bpy.ops.mesh.reveal()
					bpy.ops.mesh.select_all(action='SELECT')
					if self.TypeAlign == 'X':
						bpy.ops.transform.translate(value=(Difference, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
					if self.TypeAlign == 'Y':
						bpy.ops.transform.translate(value=(0, Difference, 0), constraint_axis=(False, True, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
					if self.TypeAlign == 'Z':
						bpy.ops.transform.translate(value=(0, 0, Difference), constraint_axis=(False, False, True), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
						
					bpy.ops.object.mode_set(mode = 'OBJECT')

		# Select again objects
		for j in current_selected_obj:
			j.select = True;
			
		bpy.context.scene.objects.active = current_active_obj
		
		return {'FINISHED'}
	
#------------------Align Origin To Max-------------------------------
class AlignMax(bpy.types.Operator):
	"""Origin To Max """
	bl_idname = "object.align_max"
	bl_label = "Origin To Max"
	bl_options = {'REGISTER', 'UNDO'}
	TypeAlign = bpy.props.StringProperty()
	
	def execute(self, context):

		# Save selected objects and current position of 3D Cursor
		current_selected_obj = bpy.context.selected_objects
		current_active_obj = bpy.context.active_object
		saved_cursor_loc = bpy.context.scene.cursor_location.copy()
		bpy.ops.object.mode_set(mode = 'OBJECT')
		# Change individual origin point
		for x in current_selected_obj:
			# Select only current object (for setting origin)
			bpy.ops.object.select_all(action='DESELECT')
			x.select = True
			bpy.context.scene.objects.active = x
			# Save current origin and relocate 3D Cursor
			saved_origin_loc = x.location.copy() 
			if x.type == 'MESH':
				bpy.ops.object.mode_set(mode = 'EDIT')
				
				if self.TypeAlign == 'X':
					MaxCo = FindMinMaxVerts(x, 0, 1)
					if MaxCo == None:
						MaxCo = saved_origin_loc[0]
				if self.TypeAlign == 'Y':
					MaxCo = FindMinMaxVerts(x, 1, 1)
					if MaxCo == None:
						MaxCo = saved_origin_loc[1]
				if self.TypeAlign == 'Z':
					MaxCo = FindMinMaxVerts(x, 2, 1)
					if MaxCo == None:
						MaxCo = saved_origin_loc[2]
				
				if context.scene.align_geom_to_orig == False:
					bpy.ops.object.mode_set(mode = 'OBJECT')
					if self.TypeAlign == 'X':
						bpy.context.scene.cursor_location = [MaxCo, saved_origin_loc[1], saved_origin_loc[2]] 
					if self.TypeAlign == 'Y':
						bpy.context.scene.cursor_location = [saved_origin_loc[0], MaxCo, saved_origin_loc[2]] 
					if self.TypeAlign == 'Z':
						bpy.context.scene.cursor_location = [saved_origin_loc[0], saved_origin_loc[1], MaxCo]
						
					# Apply origin to Cursor position
					bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
					# Reset 3D Cursor position  
					bpy.context.scene.cursor_location = saved_cursor_loc
				
				if context.scene.align_geom_to_orig == True:
					if self.TypeAlign == 'X':
						Difference = saved_origin_loc[0] - MaxCo
					if self.TypeAlign == 'Y':
						Difference = saved_origin_loc[1] - MaxCo
					if self.TypeAlign == 'Z':
						Difference = saved_origin_loc[2] - MaxCo
					
					bpy.ops.mesh.reveal()
					bpy.ops.mesh.select_all(action='SELECT')
					if self.TypeAlign == 'X':
						bpy.ops.transform.translate(value=(Difference, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
					if self.TypeAlign == 'Y':
						bpy.ops.transform.translate(value=(0, Difference, 0), constraint_axis=(False, True, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
					if self.TypeAlign == 'Z':
						bpy.ops.transform.translate(value=(0, 0, Difference), constraint_axis=(False, False, True), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
						
					bpy.ops.object.mode_set(mode = 'OBJECT')

		# Select again objects
		for j in current_selected_obj:
			j.select = True;
			
		bpy.context.scene.objects.active = current_active_obj
		
		return {'FINISHED'}
	
#------------------Align Cursor------------------
class AlignCur(bpy.types.Operator):
	"""Origin Align To Cursor"""
	bl_idname = "object.align_cur"
	bl_label = "Origin To Cursor"
	bl_options = {'REGISTER', 'UNDO'}
	TypeAlign = bpy.props.StringProperty()
	
	def execute(self, context):

		# Save selected objects and current position of 3D Cursor
		current_selected_obj = bpy.context.selected_objects
		saved_cursor_loc = bpy.context.scene.cursor_location.copy()
		bpy.ops.object.mode_set(mode = 'OBJECT')
		# Change individual origin point
		for x in current_selected_obj:
			# Select only current object (for setting origin)
			bpy.ops.object.select_all(action='DESELECT')
			x.select = True
			# Save current origin and relocate 3D Cursor
			saved_origin_loc = x.location.copy()
			#Align to 3D Cursor
			if self.TypeAlign == 'X':
				bpy.context.scene.cursor_location = [saved_cursor_loc[0], saved_origin_loc[1], saved_origin_loc[2]] 
			if self.TypeAlign == 'Y':
				bpy.context.scene.cursor_location = [saved_origin_loc[0], saved_cursor_loc[1], saved_origin_loc[2]] 
			if self.TypeAlign == 'Z':
				bpy.context.scene.cursor_location = [saved_origin_loc[0], saved_origin_loc[1], saved_cursor_loc[2]] 
			# Apply origin to Cursor position
			if context.scene.align_geom_to_orig == False:
				bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
			else:
				if self.TypeAlign == 'X':
					Difference = saved_cursor_loc[0] - saved_origin_loc[0]
					bpy.ops.transform.translate(value=(Difference, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
				if self.TypeAlign == 'Y':
					Difference = saved_cursor_loc[1] - saved_origin_loc[1]
					bpy.ops.transform.translate(value=(0, Difference, 0), constraint_axis=(False, True, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
				if self.TypeAlign == 'Z':
					Difference = saved_cursor_loc[2] - saved_origin_loc[2]
					bpy.ops.transform.translate(value=(0, 0, Difference), constraint_axis=(False, False, True), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
			# Reset 3D Cursor position  
			bpy.context.scene.cursor_location = saved_cursor_loc
		
		# Select again objects
		for j in current_selected_obj:
			j.select = True;
		
		return {'FINISHED'}

#------------------Align Coordinate------------------ 
class AlignCo(bpy.types.Operator):
	"""Origin Align To Spec Coordinate"""
	bl_idname = "object.align_co"
	bl_label = "Origin Align To Spec Coordinate"
	bl_options = {'REGISTER', 'UNDO'}
	TypeAlign = bpy.props.StringProperty()

	def execute(self, context):
		wrong_align_co = False
		#Check coordinate if check tgis option
		try:
			align_coordinate = float(context.scene.align_co)
		except:
			self.report({'INFO'}, 'Coordinate is wrong')
			wrong_align_co = True   
		
		if wrong_align_co == False:
			# Save selected objects and current position of 3D Cursor
			current_selected_obj = bpy.context.selected_objects
			saved_cursor_loc = bpy.context.scene.cursor_location.copy()
			bpy.ops.object.mode_set(mode = 'OBJECT')
			# Change individual origin point
			for x in current_selected_obj:
				# Select only current object (for setting origin)
				bpy.ops.object.select_all(action='DESELECT')
				x.select = True
				# Save current origin and relocate 3D Cursor
				saved_origin_loc = x.location.copy()
				
				#Align to Coordinate
				if self.TypeAlign == 'X':
					bpy.context.scene.cursor_location = [align_coordinate, saved_origin_loc[1], saved_origin_loc[2]] 
				if self.TypeAlign == 'Y':
					bpy.context.scene.cursor_location = [saved_origin_loc[0], align_coordinate, saved_origin_loc[2]] 
				if self.TypeAlign == 'Z':
					bpy.context.scene.cursor_location = [saved_origin_loc[0], saved_origin_loc[1], align_coordinate] 
				
				if context.scene.align_geom_to_orig == False:
					bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
				else:
					if self.TypeAlign == 'X':
						Difference = align_coordinate - saved_origin_loc[0]
						bpy.ops.transform.translate(value=(Difference, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
					if self.TypeAlign == 'Y':
						Difference = align_coordinate - saved_origin_loc[1]
						bpy.ops.transform.translate(value=(0, Difference, 0), constraint_axis=(False, True, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
					if self.TypeAlign == 'Z':
						Difference = align_coordinate - saved_origin_loc[2]
						bpy.ops.transform.translate(value=(0, 0, Difference), constraint_axis=(False, False, True), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
				# Reset 3D Cursor position  
				bpy.context.scene.cursor_location = saved_cursor_loc
			
			# Select again objects
			for j in current_selected_obj:
				j.select = True;
			
		return {'FINISHED'}

#-------------------------------------------------------
# OriginRotate
class OriginRotate(bpy.types.Operator):
	"""Rotate Origin"""
	bl_idname = "object.origin_rotate"
	bl_label = "Rotate Origin"
	bl_options = {'REGISTER', 'UNDO'}
	TypeRot = bpy.props.StringProperty()
	def execute(self, context):
		
		wrong_angle = False
		#Check value if check this option
		try:
			RotValue = float(context.scene.origin_rotate_value)
		except:
			self.report({'INFO'}, 'Angle is wrong')
			wrong_angle = True   
		
		if bpy.context.scene.orientation_select == '0':
			Ori_Constaraint = 'GLOBAL'
		if bpy.context.scene.orientation_select == '1':
			Ori_Constaraint = 'LOCAL'
		
		if wrong_angle == False:
			active_obj = bpy.context.active_object
			bpy.ops.object.select_all(action='DESELECT')
			active_obj.select = True
			if active_obj.type == 'MESH':
				bpy.ops.object.duplicate()
				dupli_object = bpy.context.active_object
				if self.TypeRot == 'X+':
					bpy.ops.transform.rotate(value= (math.pi * RotValue / 180), axis=(1, 0, 0), constraint_axis=(True, False, False), constraint_orientation=Ori_Constaraint, mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
				if self.TypeRot == 'X-':
					bpy.ops.transform.rotate(value= -(math.pi * RotValue / 180), axis=(1, 0, 0), constraint_axis=(True, False, False), constraint_orientation=Ori_Constaraint, mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
				if self.TypeRot == 'Y+':
					bpy.ops.transform.rotate(value= (math.pi * RotValue / 180), axis=(0, 1, 0), constraint_axis=(False, True, False), constraint_orientation=Ori_Constaraint, mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
				if self.TypeRot == 'Y-':
					bpy.ops.transform.rotate(value= -(math.pi * RotValue / 180), axis=(0, 1, 0), constraint_axis=(False, True, False), constraint_orientation=Ori_Constaraint, mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
				if self.TypeRot == 'Z+':
					bpy.ops.transform.rotate(value= (math.pi * RotValue / 180), axis=(0, 0, 1), constraint_axis=(False, False, True), constraint_orientation=Ori_Constaraint, mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
				if self.TypeRot == 'Z-':
					bpy.ops.transform.rotate(value= -(math.pi * RotValue / 180), axis=(0, 0, 1), constraint_axis=(False, False, True), constraint_orientation=Ori_Constaraint, mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)	
				bpy.ops.object.mode_set(mode = 'EDIT')
				bpy.ops.mesh.reveal()
				bpy.ops.mesh.select_all(action='SELECT')
				bpy.ops.mesh.delete()
				bpy.ops.object.mode_set(mode = 'OBJECT')
				active_obj.select = True
				name = active_obj.name
				geo_name = active_obj.data.name 
				bpy.ops.object.join()
				bpy.context.active_object.name = name
				bpy.context.active_object.data.name = geo_name
			
		return {'FINISHED'}
		
#-------------------------------------------------------
#FUNCTIONS
#Find Min and Max Vertex Coordinates
def FindMinMaxVerts(obj, CoordIndex, MinOrMax):
	
	bpy.ops.mesh.reveal()
	
	#get bmesh from active object
	bm = bmesh.from_edit_mesh(obj.data)
	bm.verts.ensure_lookup_table()
	
	if len(bm.verts) == 0:
		result = None
	else:
		min_co = (obj.matrix_world*bm.verts[0].co)[CoordIndex]
		max_co = (obj.matrix_world*bm.verts[0].co)[CoordIndex]
		
		for v in bm.verts:
			if (obj.matrix_world*v.co)[CoordIndex] < min_co:
				min_co = (obj.matrix_world*v.co)[CoordIndex]
			if (obj.matrix_world*v.co)[CoordIndex] > max_co:
				max_co = (obj.matrix_world*v.co)[CoordIndex]
		
		if MinOrMax == 0:
			result = min_co
		else:
			result = max_co
		
	return result	
		
#-------------------------------------------------------
# Set Origin To Selection
class SetOriginToSelect(bpy.types.Operator):
	"""Set Origin To Selection"""
	bl_idname = "object.set_origin_to_select"
	bl_label = "Set Origin To Selection"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		selected_obj = bpy.context.selected_objects
		saved_cursor_loc = bpy.context.scene.cursor_location.copy()
		bpy.ops.view3d.snap_cursor_to_selected()
		bpy.ops.object.mode_set(mode = 'OBJECT')
		# Apply origin to Cursor position
		bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
		# Reset 3D Cursor position  
		bpy.context.scene.cursor_location = saved_cursor_loc
		bpy.ops.object.mode_set(mode = 'EDIT')
		return {'FINISHED'} 	

#-------------------------------------------------------
# Select Faces by sides
class SelectFacesBySides(bpy.types.Operator):
	"""Set Faces By Sides"""
	bl_idname = "object.select_faces_by_sides"
	bl_label = "Set Faces By Sides"
	bl_options = {'REGISTER', 'UNDO'}
	Select_Operation = bpy.props.StringProperty()
	
	def execute(self, context):
		
		# Get Number Sides 
		try:
			input_sides = int(context.scene.sides_number)
		except:
			input_sides = 4
			message = "Number is wrong. Number will be set is 4"
			self.report({'INFO'}, message)
		
		bpy.ops.mesh.reveal()
		bpy.ops.mesh.select_mode(type="FACE")
		bpy.ops.mesh.select_all(action='DESELECT')
		
		#Ref Poly
		bpy.ops.mesh.primitive_circle_add(vertices=input_sides, fill_type='NGON')
		
		
		#get bmesh from active object
		bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
		bm.faces.ensure_lookup_table()
		
		# get index of Ref Poly
		for f in bm.faces:
			if f.select:
				ref_face_index = f.index
		
		bpy.ops.mesh.select_similar(type='SIDES', compare=self.Select_Operation, threshold=0.5)
		
		# Delete Ref Poly
		for v in bm.faces[ref_face_index].verts:
			bm.verts.remove(v)
		
		# It's for Apply Removing
		bpy.ops.object.mode_set(mode = 'OBJECT')
		bpy.ops.object.mode_set(mode = 'EDIT')
		
		return {'FINISHED'}
		
#-------------------------------------------------------
# Copy Texture Assignment
class CopyTextAssign(bpy.types.Operator):
	"""Copy Texture Assignment"""
	bl_idname = "object.copy_text_assign"
	bl_label = "Copy Texture Assignment"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		selected_obj = bpy.context.selected_objects
		active_obj = bpy.context.active_object
		
		if active_obj.type == 'MESH' and active_obj.data.uv_textures.active != -1:
			UVdata = active_obj.data.uv_textures.active.data[0]
			if UVdata.image != None:
				img = UVdata.image.name
				
			for x in selected_obj:
				bpy.ops.object.select_all(action='DESELECT')
				x.select = True
				if x.type == 'MESH':
					bpy.context.scene.objects.active = x
					bpy.ops.object.mode_set(mode = 'EDIT')
					bpy.ops.mesh.reveal()
					bpy.ops.mesh.select_all(action='SELECT')
					
					if x.data.uv_textures.active != -1:
						if UVdata.image != None:
							bpy.data.screens['UV Editing'].areas[1].spaces[0].image = bpy.data.images[img]
						else:
							bpy.data.screens['UV Editing'].areas[1].spaces[0].image = None
					
					bpy.ops.mesh.select_all(action='DESELECT')
					bpy.ops.object.mode_set(mode='OBJECT')
					
		# Select again objects
		for j in selected_obj:
			j.select = True;
			
		bpy.context.scene.objects.active = active_obj
		UVdata = None
		img = None
		
		return {'FINISHED'}
		
#-------------------------------------------------------
# Panels
class VIEW3D_PT_Origin_Tools_panel(bpy.types.Panel):
	bl_label = "Origin Tools"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_options = {'DEFAULT_CLOSED'}

	@classmethod
	def poll(self, context):
		return (True)

	def draw(self, context):
		layout = self.layout
		if context.object is not None:
			if context.mode == 'OBJECT':
				row = layout.row()
				row.label("Origin Rotation")
				row = layout.row()
				row.prop(context.scene, 'orientation_select', expand=False)
				row = layout.row()
				row.prop(context.scene, "origin_rotate_value", text="Angle")
				row = layout.row()
				c = row.column()
				row = c.row()
				split = row.split(percentage=0.5)
				c = split.column()
				c.operator("object.origin_rotate", text="X-").TypeRot = 'X-'
				split = split.split()
				c = split.column()
				c.operator("object.origin_rotate", text="X+").TypeRot = 'X+'
				row = layout.row()
				c = row.column()
				row = c.row()
				split = row.split(percentage=0.5)
				c = split.column()
				c.operator("object.origin_rotate", text="Y-").TypeRot = 'Y-'
				split = split.split()
				c = split.column()
				c.operator("object.origin_rotate", text="Y+").TypeRot = 'Y+'
				row = layout.row()
				c = row.column()
				row = c.row()
				split = row.split(percentage=0.5)
				c = split.column()
				c.operator("object.origin_rotate", text="Z-").TypeRot = 'Z-'
				split = split.split()
				c = split.column()
				c.operator("object.origin_rotate", text="Z+").TypeRot = 'Z+'
				layout.separator()
				
				row = layout.row()
				row.label("Origin Align")
				row = layout.row()
				row.prop(context.scene, "align_co", text="Coordinate")
				row = layout.row()
				row.prop(context.scene, "align_geom_to_orig", text="Geometry To Origin")
				
				#--Aligner Labels----
				row = layout.row()
				c = row.column()
				row = c.row()
				split = row.split(percentage=0.33)
				c = split.column()
				c.label("X")
				split = split.split(percentage=0.5)
				c = split.column()
				c.label("Y")
				split = split.split()
				c = split.column()
				c.label("Z")
				
				#--Aligner Min Buttons----
				row = layout.row()
				c = row.column()
				row = c.row()
				split = row.split(percentage=0.33)
				c = split.column()
				c.operator("object.align_min", text="Min").TypeAlign='X'
				split = split.split(percentage=0.5)
				c = split.column()
				c.operator("object.align_min", text="Min").TypeAlign='Y'
				split = split.split()
				c = split.column()
				c.operator("object.align_min", text="Min").TypeAlign='Z'
				
				#--Aligner Max Buttons----
				row = layout.row()
				c = row.column()
				row = c.row()
				split = row.split(percentage=0.33)
				c = split.column()
				c.operator("object.align_max", text="Max").TypeAlign='X'
				split = split.split(percentage=0.5)
				c = split.column()
				c.operator("object.align_max", text="Max").TypeAlign='Y'
				split = split.split()
				c = split.column()
				c.operator("object.align_max", text="Max").TypeAlign='Z'
				
				#--Aligner Cursor Buttons----
				row = layout.row()
				c = row.column()
				row = c.row()
				split = row.split(percentage=0.33)
				c = split.column()
				c.operator("object.align_cur", text="Cursor").TypeAlign='X'
				split = split.split(percentage=0.5)
				c = split.column()
				c.operator("object.align_cur", text="Cursor").TypeAlign='Y'
				split = split.split()
				c = split.column()
				c.operator("object.align_cur", text="Cursor").TypeAlign='Z'
				
				#--Aligner Coordinates Buttons----
				row = layout.row()
				c = row.column()
				row = c.row()
				split = row.split(percentage=0.33)
				c = split.column()
				c.operator("object.align_co", text="Coordinates").TypeAlign='X'
				split = split.split(percentage=0.5)
				c = split.column()
				c.operator("object.align_co", text="Coordinates").TypeAlign='Y'
				split = split.split()
				c = split.column()
				c.operator("object.align_co", text="Coordinates").TypeAlign='Z'
				
		if context.object is not None:
			if context.object.mode == 'EDIT':
				row = layout.row()
				row.operator("object.set_origin_to_select", text="Set Origin To Selected")
				layout.separator()

class VIEW3D_PT_Rename_Tools_panel(bpy.types.Panel):
	bl_label = "Rename Tools"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_options = {'DEFAULT_CLOSED'}

	@classmethod
	def poll(self, context):
		return (True)

	def draw(self, context):
		layout = self.layout	
		if context.object is not None:
			if context.mode == 'OBJECT':
				layout.label("Rename UV")
				row = layout.row()
				row.prop(context.scene, "uv_layer_index", text="UV Index")
				row = layout.row()
				row.prop(context.scene, "uv_name")
				row = layout.row()
				row.operator("object.uv_rename", text="Rename UV(s)")
				layout.separator()
				
				layout.label("Rename Objects")
				row = layout.row()
				row.prop(context.scene, 'rename_select', expand=False)
				row = layout.row()
				row.prop(context.scene, "old_text")
				if bpy.context.scene.rename_select == '2':
					row = layout.row()
					row.prop(context.scene, "new_text")
				row = layout.row()
				row.operator("object.rename_object", text="Rename Object(s)")
				
class VIEW3D_PT_ImportExport_Tools_panel(bpy.types.Panel):
	bl_label = "Import/Export Tools"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_options = {'DEFAULT_CLOSED'}

	@classmethod
	def poll(self, context):
		return (True)

	def draw(self, context):
		layout = self.layout	
		if context.object is not None:
			if context.mode == 'OBJECT':
				row = layout.row()
				row.operator("object.clear_normals", text="Clear Custom Normals")
				row = layout.row()
				row.operator("object.calc_normals", text="Flip/Calculate Normals")
				layout.prop(context.scene, "calc_normals_en", text="Recalc Normals")
				layout.prop(context.scene, "normals_inside", text="Inside")
				layout.separator()
				
			if context.mode == 'OBJECT':
				row = layout.row()
				row.operator("object.multi_fbx_export", text="Export FBX to Unity")
				layout.prop(context.scene, "export_one_fbx", text="Selected in One FBX")
				#layout.prop(context.scene, "fbx_save_rotation", text="Save Rotation")
		
		if context.mode == 'OBJECT':
			row = layout.row()
			row.operator("object.import_fbxobj", text="Import FBXs/OBJs")
				
class VIEW3D_PT_LowPolyArt_Tools_panel(bpy.types.Panel):
	bl_label = "Low Poly Art Tools"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_options = {'DEFAULT_CLOSED'}

	@classmethod
	def poll(self, context):
		return (True)

	def draw(self, context):
		layout = self.layout
		if context.object is not None:
			if context.mode == 'OBJECT':
				row = layout.row()
				row.operator("object.palette_creator", text="Create Palette Texture")
				layout.separator()
			
			if context.mode == 'OBJECT':
				row = layout.row()
				row.operator("object.bake_vc", text="Texture to Vertex Colors")
				layout.separator()
			
			if context.mode == 'OBJECT':
				row = layout.row()
				row.operator("object.uv_remove", text="Clear UV Maps")
				layout.separator()
		
class VIEW3D_PT_tools_asset_toolset(bpy.types.Panel):
	bl_label = "Other Tools"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_options = {'DEFAULT_CLOSED'}

	@classmethod
	def poll(self, context):
		return (True)

	def draw(self, context):
		layout = self.layout	
				
		if context.object is not None:
			if context.object.mode == 'EDIT':
				row = layout.row()
				layout.label("Select Faces by Sides")
				row = layout.row()
				row.prop(context.scene, "sides_number", text="Number of Sides")
				#--Select Faces Buttons----
				row = layout.row()
				c = row.column()
				row = c.row()
				split = row.split(percentage=0.33)
				c = split.column()
				c.operator("object.select_faces_by_sides", text="<").Select_Operation='LESS'
				split = split.split(percentage=0.5)
				c = split.column()
				c.operator("object.select_faces_by_sides", text="=").Select_Operation='EQUAL'
				split = split.split()
				c = split.column()
				c.operator("object.select_faces_by_sides", text=">").Select_Operation='GREATER'
		
		if context.object is not None:
			if context.mode == 'OBJECT':
				row = layout.row()
				row.operator("object.copy_text_assign", text="Copy Texture Assignment")
				layout.separator()

#-------------------------------------------------------		
def register():
	bpy.utils.register_module(__name__)
	bpy.types.Scene.old_text = bpy.props.StringProperty(
		name="Find/Add",
		description="Text for search and add",
		default="")
	
	bpy.types.Scene.new_text = bpy.props.StringProperty(
		name="Replace",
		description="Text for replace",
		default="")
		
	bpy.types.Scene.align_co = bpy.props.FloatProperty(
		name="",
		description="Coordinate",
		default=0.00,
		min = -9999,
        max = 9999,
		step = 50)
	
	axis_items = (('0','X',''),('1','Y',''), ('2','Z',''))
	bpy.types.Scene.axis_select = bpy.props.EnumProperty(name="Axis", items = axis_items)
	
	rename_menu_items = (('0','Add Prefix',''),('1','Add Postfix',''), ('2','Replace',''), ('3','New name',''))
	bpy.types.Scene.rename_select = bpy.props.EnumProperty(name="Rename function", items = rename_menu_items)
	
	orientation_menu_items = (('0','GLOBAL',''),('1','LOCAL',''))
	bpy.types.Scene.orientation_select = bpy.props.EnumProperty(name="Orientation", items = orientation_menu_items)
	
	bpy.types.Scene.export_one_fbx = bpy.props.BoolProperty(
		name="Selected in One FBX",
		description="Export Selected in One FBX",
		default = False)
	
	bpy.types.Scene.normals_inside = bpy.props.BoolProperty(
		name="Inside Normals",
		description="Recalculate Normals Inside",
		default = False)
	
	bpy.types.Scene.calc_normals_en = bpy.props.BoolProperty(
		name="Recalc Normals",
		description="Recalculate Normals",
		default = False)
		
	bpy.types.Scene.sides_number = bpy.props.IntProperty(
		name="Sides",
		description="Number Sides for Selection",
		default=4,
		min = 3,
        max = 128)

	bpy.types.Scene.align_geom_to_orig = bpy.props.BoolProperty(
		name="Geometry To Origin",
		description="Align Geometry To Origin",
		default = False)
	
	bpy.types.Scene.fbx_save_rotation = bpy.props.BoolProperty(
		name="Save Object Rotation",
		description="Save Object Rotation",
		default = False)
	
	bpy.types.Scene.origin_rotate_value = bpy.props.FloatProperty(
		name="",
		description="Angle for Origin Rotate ",
		default=5.00,
		min = -1000,
        max = 1000,
		step = 50)
	
	bpy.types.Scene.uv_layer_index = bpy.props.IntProperty(
        name = "UV Index", 
        description = "UV Index",
		default = 0,
		min = 0,
        max = 10)
	
	bpy.types.Scene.uv_name = bpy.props.StringProperty(
		name="UV Name",
		description="UV Name",
		default="")
	
def unregister():
	bpy.utils.unregister_module(__name__)
	del bpy.types.Scene.old_text
	del bpy.types.Scene.new_text
	del bpy.types.Scene.axis_select
	del bpy.types.Scene.export_one_fbx
	del bpy.types.Scene.normals_inside
	del bpy.types.Scene.calc_normals_en
	del bpy.types.Scene.align_co
	del bpy.types.Scene.align_geom_to_orig
	del bpy.types.Scene.fbx_save_rotation
	del bpy.types.Scene.orientation_select
	del bpy.types.Scene.uv_layer_index


if __name__ == "__main__":
	register()
