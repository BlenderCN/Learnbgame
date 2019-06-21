import bpy, bmesh, math, re, operator, os, difflib
from math import degrees, pi, radians, ceil
from bpy.types import Panel, UIList
import mathutils
from mathutils import Vector, Euler, Matrix
from . import auto_rig_reset, auto_rig_datas, auto_rig
from bpy_extras.io_utils import ExportHelper




print ("\n Starting Auto-Rig Pro: Game Engine Exporter... \n")

fingers_deform = ["thumb1", "c_thumb2", "c_thumb3", 'c_index1_base', "index1", "c_index2", "c_index3", 'c_middle1_base', "middle1", "c_middle2", "c_middle3", 'c_ring1_base', "ring1", "c_ring2", "c_ring3", 'c_pinky1_base', "pinky1", "c_pinky2", "c_pinky3"]

fingers_names = ["pinky", "ring", "index", "middle", "thumb"]

bend_bones = ['c_ankle_bend', 'c_leg_bend_02', 'c_leg_bend_01', 'c_knee_bend', 'c_thigh_bend_02', 'c_thigh_bend_01', 'c_thigh_bend_contact', 'c_waist_bend.x', 'c_root_bend.x', 'c_spine_01_bend.x', 'c_spine_02_bend.x', 'c_shoulder_bend', 'c_arm_bend', 'c_elbow_bend', 'c_forearm_bend', 'c_wrist_bend', 'c_bot_bend', 'c_breast_01', 'c_breast_02', 'c_neck_01.x']

bend_bones_add = ['c_ankle_bend', 'c_leg_bend_02', 'c_leg_bend_01', 'c_knee_bend', 'c_thigh_bend_02', 'c_thigh_bend_01', 'c_thigh_bend_contact', 'c_waist_bend.x', 'c_shoulder_bend', 'c_arm_bend', 'c_elbow_bend', 'c_forearm_bend', 'c_wrist_bend', 'c_bot_bend']	

default_facial_bones = ['c_eyebrow_full', 'c_eyebrow_01_end', 'c_eyebrow_01', 'c_eyebrow_02', 'c_eyebrow_03', 'c_eye', 'c_eye_offset', 'eyelid_bot', 'eyelid_top', 'jawbone.x', 'c_lips_smile', 'c_eye_target']

additional_facial_bones = ['c_teeth_bot', 'c_teeth_top', 'c_lips_bot', 'c_lips_bot_01', 'c_lips_top', 'c_lips_top_01', 'c_chin_01', 'c_chin_02', 'c_cheek_smile', 'c_nose_03', 'c_nose_01', 'c_nose_02', 'c_cheek_inflate', 'c_eye_ref_track', 'tong_03', 'tong_02', 'tong_01', 'c_skull_01', 'c_skull_02', 'c_skull_03', 'c_eyelid_top_01', 'c_eyelid_top_02', 'c_eyelid_top_03', 'c_eyelid_bot_01', 'c_eyelid_bot_02', 'c_eyelid_bot_03', 'c_eyelid_corner_01', 'c_eyelid_corner_02']

facial_transfer_jaw = ["c_lips_bot_01", "c_lips_bot", "c_teeth_bot", "c_chin_01", "c_chin_02", "tong_03", "tong_01", "tong_02"]
facial_transfer_head = [i for i in additional_facial_bones if not (i in facial_transfer_jaw or 'eyelid' in i)]
facial_transfer_ears = ["c_ear_01", "c_ear_02", "c_ear_03", "c_ear_04", "c_ear_05", "c_ear_06"]





##########################	CLASSES	 ##########################


class ARP_OT_delete_action(bpy.types.Operator):
	  
	#tooltip
	"""Delete the selected action"""
	
	bl_idname = "arp.delete_action"
	bl_label = "The action will be permanently removed from the scene, ok?"
	bl_options = {'UNDO'}	
	
	action_name : bpy.props.StringProperty(default="")
	
	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event)

		
	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:
		
			if self.action_name != "":				
				if bpy.data.actions.get(self.action_name):
					bpy.data.actions.remove(bpy.data.actions[self.action_name])
			
			
					
		finally:		
			context.preferences.edit.use_global_undo = use_global_undo	   
		
		return {'FINISHED'}
		
	
		



class ARP_OT_set_standard_scale(bpy.types.Operator):
	  
	#tooltip
	"""Restore the default Blender units"""
	
	bl_idname = "id.set_standard_scale"
	bl_label = "set_standard_scale"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		if context.active_object != None:
			if bpy.context.scene.arp_rename_for_ue == False:
				unit_system = bpy.context.scene.unit_settings			
				if unit_system.system != 'None':
					if unit_system.scale_length > 0.01-0.0003 and unit_system.scale_length < 0.01+0.0003:
						return True

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:
			try:
				bpy.data.objects['rig']
			except:
				self.report({'ERROR'}, "Append the Auto-Rig Pro armature in the scene first.")
				return {'FINISHED'}
				
			#save current mode
			active_obj = bpy.context.active_object
			current_mode = context.mode					
			#bpy.ops.object.mode_set(mode='EDIT')  
			
			_set_standard_scale(self)
			
			
			 #restore saved mode	
			  
			try: 
				
				bpy.ops.object.mode_set(mode=current_mode)
				set_active_object(active_obj.name)
				
				self.report({'INFO'}, "Done.")
			except:
				pass
	 
		finally:
			context.preferences.edit.use_global_undo = use_global_undo	   
		
		return {'FINISHED'}
		




		

		
class ARP_OT_set_mped_rig(bpy.types.Operator):
	  
	#tooltip
	"""Create and set the Mped armature as the deforming armature"""
	
	bl_idname = "id.set_mped_rig"
	bl_label = "set_mped_rig"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):	
		if bpy.data.objects.get("rig") != None and context.active_object != None:
			return True

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		
		try:							
			_set_mped_rig("rig", "rig_add", True)				
	 
		finally:
			context.preferences.edit.use_global_undo = use_global_undo	   
		
		return {'FINISHED'}
		
######### FOR RETRO COMPATIBILITY ONLY#########
class ARP_OT_unset_humanoid_rig(bpy.types.Operator):
	  
	#tooltip
	"""Unset the Humanoid armature"""
	
	bl_idname = "id.unset_humanoid_rig"
	bl_label = "unset_humanoid_rig"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):		
			
		if context.active_object:			
			if bpy.data.objects.get("rig_humanoid"):
				return True				
			else:
				return False
		
		
	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		
		try:	   
			try:
				bpy.data.objects["rig_humanoid"]				
			except:
				self.report({'ERROR'}, "The Humanoid armature has not been set yet.")
				return{'FINISHED'} 
			try:
				bpy.data.objects["rig"]
			except:
				self.report({'ERROR'}, "The Humanoid armature has not been set yet.")
				return{'FINISHED'} 
		   
			#save current mode			 
			current_mode = context.mode
			bpy.ops.object.mode_set(mode='OBJECT')	  
			current_obj = bpy.context.active_object				
			current_frame = bpy.context.scene.frame_current#save current frame	
			
			_unset_humanoid_rig(self, context)
			
			
			try:
				#restore current frame
				bpy.context.scene.frame_current = current_frame
				bpy.context.scene.frame_set(bpy.context.scene.frame_current)#debug					
			except:
				pass
				
			try:
				#restore object
				bpy.ops.object.mode_set(mode='OBJECT')
				set_active_object(current_obj.name)								
				bpy.ops.object.mode_set(mode=current_mode)	
			except:
				try:
					set_active_object("rig")				
					bpy.ops.object.mode_set(mode='OBJECT')
				except:
					print("Could not set rig object")
				
			self.report({'INFO'}, "Done.")
	 
		finally:
			context.preferences.edit.use_global_undo = use_global_undo	   
		
		return {'FINISHED'}
		
		
limb_sides = auto_rig.Limb_Sides()
		
class ARP_OT_export_fbx(bpy.types.Operator):

	"""Export character in .fbx file format"""
	bl_idname = "id.export_fbx"
	bl_label = "Export .FBX"	
	
	def execute(self, context):	
		self.armature_name = ""
		self.armature_add_name = ""
		self.char_objects = None
		self.message_final = ""	
		self.non_armature_actions = []
		
		current_selection = [bpy.context.active_object.name, [i.name for i in bpy.context.selected_objects]]
		
		# Initial checks and warnings
		# Is the armature selected?		
		if bpy.context.active_object == None:
			self.report({"ERROR"}, 'Select the armature to export')
			return {'FINISHED'}	
		else:
			# set the armature as active object (if any)
			if bpy.context.active_object.type != "ARMATURE":
				for obj in bpy.context.selected_objects:
					if obj.type == "ARMATURE":
						set_active_object(obj.name)
						break
		
			if bpy.context.active_object.type != "ARMATURE":
				self.report({"ERROR"}, 'Select the armature to export')
				return {'FINISHED'}	
			else:
				# check for materials linked to Object instead of Data
				# is the selected armature a proxy?			
				armature_base_name = bpy.context.active_object.name	
				if bpy.context.active_object.proxy:			
					armature_base_name = bpy.context.active_object.proxy.name
					print("The armature is a proxy. Real name = ", armature_base_name)		
				
				# iterate over objects
				for obj in bpy.context.scene.objects:					
					if obj.type == "MESH":
						
						# is a mesh with shape keys linked to the selected armature?
						if obj.data.shape_keys and obj.find_armature():
							if obj.find_armature().name == armature_base_name:
							
								# is material linked to object?
								is_ob_material = any(ms.link == 'OBJECT' for ms in obj.material_slots)
							
								if is_ob_material:
									self.report({"ERROR"}, '"' + obj.name + '" is a deformed mesh with shape keys, with material linked set to Object. Shape keys cannot be exported.\nLink the material to Data instead.')
									return {'FINISHED'}	
						
				limb_sides.get_multi_limbs()
				
				# check the facial bones are up to date
				if len(limb_sides.head_sides) > 0:
					jawbone_x = bpy.context.active_object.data.bones.get("jawbone.x")
					c_jawbone_x = bpy.context.active_object.data.bones.get("c_jawbone.x")
					eyelid_top = bpy.context.active_object.data.bones.get("eyelid_top.l")
					c_eyelid_top = bpy.context.active_object.data.bones.get("c_eyelid_top.l")
					
					if (jawbone_x == None and c_jawbone_x) or (eyelid_top == None and c_eyelid_top):
						self.report({"ERROR"}, "Armature not up to date. Click 'Update Armature'")
						return {'FINISHED'}	
				
		
		# Can the rig_add be found?		
		self.armature_name = bpy.context.active_object.name
		rig_add = get_rig_add(self.armature_name)
		if rig_add == None:
			self.report({"ERROR"}, 'rig_add not found. Invalid rig hierarchy.')
			return {'FINISHED'}	
			
		
		limb_sides.get_multi_limbs()
		
		# If Humanoid is selected, is it really a humanoid rig?
		found_subneck = False
		for b in bpy.context.active_object.data.bones:
			if 'c_subneck_' in b.name:
				found_subneck = True
				break
		
		if context.scene.arp_export_rig_type == "humanoid":		
			if len(limb_sides.arm_sides) > 2 or len(limb_sides.leg_sides) > 2 or len(limb_sides.head_sides) > 1 or len(limb_sides.ear_sides) > 2 or found_subneck:				
				self.report({"ERROR"}, ' This is not a humanoid rig: it contains duplicated limbs or non-humanoid limbs.\nSwitch to Universal type instead.')
				return {'FINISHED'}	
		
		
		# Is the NLA in tweak mode?
		nla_check()

		
		print("\n..............................Starting ARP FBX Export..............................")
		
		units_before_export = bpy.context.scene.unit_settings.scale_length
		
		# Disable the proxy picker to avoid bugs		
		proxy_picker_value = None
		try:	   
			proxy_picker_value = bpy.context.scene.Proxy_Picker.active
			bpy.context.scene.Proxy_Picker.active = False			
		except:
			pass
		
		# Disable auto-keyframe
		save_auto_key = context.scene.tool_settings.use_keyframe_insert_auto
		context.scene.tool_settings.use_keyframe_insert_auto = False
		
		# Enable all collections visibility
		saved_collection_vis = [i.hide_viewport for i in bpy.data.collections]
		
		for col in bpy.data.collections:
			is_cs_collection = False
			if len(col.objects) > 0:
				for obj in col.objects:
					if obj.name[:3] == "cs_":
						is_cs_collection = True
						break
			if not is_cs_collection:
				col.hide_viewport = False
			
		# Save the scene units type
		saved_unit_type = context.scene.unit_settings.system

		self.armature_add_name = get_rig_add(self.armature_name)	
		
		# Create copy objects
		create_copies(self)		
		
		# Initialize arp_armatures scales
		arm_scale = bpy.data.objects[self.armature_name + '_arpexport'].scale[0]
		if arm_scale != 1.0:
			init_armatures_scales(self.armature_name, self.armature_add_name)		
			print("Scale initialized from", arm_scale, "to 1.0")		
		
		
		def initialize_fbx_armature_rotation(root_armature_name):		
			root_armature = bpy.data.objects[root_armature_name]
			
			# parent meshes to armature
			for obj in bpy.context.selected_objects:
				if obj.type == "MESH":
					obj_mat = obj.matrix_world.copy()
					obj.parent = root_armature
					obj.matrix_world = obj_mat						
			
			# add -90 degrees rotation offset on X
			root_armature.rotation_euler[0] = math.radians(-90)
			
			# disable Copy Transforms constraint
			if len(root_armature.constraints) > 0:
				if root_armature.constraints[0].type == "COPY_TRANSFORMS":
					root_armature.constraints[0].mute = True
					
			# add copy location and copy scale instead
			cns1 = root_armature.constraints.new("COPY_LOCATION")
			cns1.target = bpy.data.objects[self.armature_name + "_arpexport"]
			cns2 = root_armature.constraints.new("COPY_SCALE")
			cns2.target = bpy.data.objects[self.armature_name + "_arpexport"]				
					
			# apply rotation
			set_active_object(root_armature_name)
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.select_all(action='DESELECT')
			set_active_object(root_armature_name)
			bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
			
			# revert rotation
			root_armature.rotation_euler[0] = math.radians(90)
		
				
		# Humanoid Export?
		if context.scene.arp_export_rig_type == "humanoid":
			
			# Set the humanoid armature
			_set_humanoid_rig(self.armature_name, self.armature_add_name)			
			
			if context.scene.arp_engine_type == "unreal":				
							
				# Rename for UE?
				if context.scene.arp_rename_for_ue:
					rename_for_ue()
					
					# Mannequin Axes?
					if context.scene.arp_mannequin_axes:						
						_set_mannequin_orientations()	
						
					
				# IK Bones?
				if context.scene.arp_ue_ik:
					_add_ik_bones()	
			
			# Bake Actions?	
			
			if context.scene.arp_bake_actions and len(bpy.data.actions) > 0:
				_bake_all(self.armature_name, "rig_humanoid", self)
			else:
				_bake_pose("rig_humanoid")
			
			
			# x100 units?			
			if context.scene.arp_units_x100:
				_set_units_x100_baked(self.armature_name)
			
			# If root motion, parent the meshes to the humanoid rig for correct transformations export
			if context.scene.arp_engine_type == "unreal":
				if context.scene.arp_ue_root_motion:					
					bpy.data.objects[self.armature_name + "_arpexport"].data.pose_position = 'REST'
					bpy.context.scene.update()
					
					for obj_name in self.char_objects:
						if bpy.data.objects[obj_name + "_arpexport"].type == "MESH":
							ob = bpy.data.objects[obj_name + "_arpexport"]
							mat = ob.matrix_world
							ob.parent = bpy.data.objects["rig_humanoid"]
							ob.matrix_world = mat
					
					bpy.data.objects[self.armature_name + "_arpexport"].data.pose_position = 'POSE'	
				
			
			# Initialize Fbx armature rotation? << Experimental feature! >>
			if context.scene.arp_init_fbx_rot:
				initialize_fbx_armature_rotation("rig_humanoid")
			
			# Select objects to export
			_select_exportable(self.armature_name)
		
			# Rename "rig_humanoid" to root"		
				#another "root" name in scene?
			for obj in bpy.data.objects:
				if obj.name == "root":
					obj.name = "root_temp"
			
			bpy.data.objects["rig_humanoid"].name = "root"	
			
			
			
		# M-Ped Export?
		if context.scene.arp_export_rig_type == "mped":
			# Set the mped armature
			_set_mped_rig(self.armature_name, self.armature_add_name, False)	
						
			
			# Bake Actions?		
				
			if context.scene.arp_bake_actions and len(bpy.data.actions) > 0:
				_bake_all(self.armature_name, "rig_mped", self)
			else:
				_bake_pose("rig_mped")
			
			# x100 units?			
			if context.scene.arp_units_x100:
				_set_units_x100_baked(self.armature_name)
				
				
			# If root motion, parent the meshes to the mped rig for correct transformations export
			if context.scene.arp_engine_type == "unreal":
				if context.scene.arp_ue_root_motion:					
					bpy.data.objects[self.armature_name + "_arpexport"].data.pose_position = 'REST'
					bpy.context.scene.update()
					
					for obj_name in self.char_objects:
						if bpy.data.objects[obj_name + "_arpexport"].type == "MESH":
							ob = bpy.data.objects[obj_name + "_arpexport"]
							mat = ob.matrix_world
							ob.parent = bpy.data.objects["rig_mped"]
							ob.matrix_world = mat
					
					bpy.data.objects[self.armature_name + "_arpexport"].data.pose_position = 'POSE'	
			
			
			# Initialize Fbx armature rotation? << Experimental feature! >>
			if context.scene.arp_init_fbx_rot:
				initialize_fbx_armature_rotation("rig_mped")
			
			# Select objects to export
			_select_exportable(self.armature_name)
			
			# Rename "rig_mped" to root"		
				#another "root" name in scene?
			for obj in bpy.data.objects:
				if obj.name == "root":
					obj.name = "root_temp"
			
			bpy.data.objects["rig_mped"].name = "root"

			
		
					
		# Generic Export?
		if context.scene.arp_export_rig_type == "generic":
			_setup_generic(self.armature_name, self.armature_add_name)
			
			# x100 units?
			if context.scene.arp_units_x100:
				_set_units_x100_generic(self.armature_name, self.armature_add_name)
		
			_select_exportable(self.armature_name)
			
		
		# Rename to right names before export
		print("Renaming to def names...")
		for obj in bpy.data.objects:
			if "_arpexport" in obj.name:
				if bpy.data.objects.get(obj.name.replace("_arpexport", "")):
					#rename base object to "_arpbaseobject" instead, temporarily
					obj_name = obj.name.replace("_arpexport", "")
					bpy.data.objects[obj_name].name = obj_name + "_arpbaseobject"
					
					#rename _arpexport to right name
					obj.name = obj.name.replace("_arpexport", "")
				else:
					print("	   Cannot find base object name", obj.name)
			
			
	
		
		
		# Export		
		print("\n..............................FBX Export..............................")
		bpy.ops.arp_export_scene.fbx(filepath=self.filepath, use_selection = True, global_scale = context.scene.arp_global_scale, use_mesh_modifiers=True, use_armature_deform_only = True, add_leaf_bones=False, apply_unit_scale = True, humanoid_actions = context.scene.arp_export_h_actions, bake_anim_simplify_factor = context.scene.arp_simplify_fac, mesh_smooth_type = context.scene.arp_mesh_smooth_type, primary_bone_axis=context.scene.arp_bone_axis_primary_export, secondary_bone_axis=context.scene.arp_bone_axis_secondary_export)
		
		print("Done.")
		
		# Revert name changes
		print("Revert name changes...")
		for obj in bpy.data.objects:
			if "_arpbaseobject" in obj.name:
				if bpy.data.objects.get(obj.name.replace("_arpbaseobject", "")):
					#rename final objects to "_arpexport"
					obj_name = obj.name.replace("_arpbaseobject", "")
					bpy.data.objects[obj_name].name = obj_name + "_arpexport"
					
					#rename _arpexport to right name
					obj.name = obj.name.replace("_arpbaseobject", "")
				else:
					print("	   Cannot find base object name", obj.name)
		
		
		# Revert animation curves location scale (x100 Units)		
		if units_before_export != context.scene.unit_settings.scale_length:
			print("\nRevert units changes")
			
			for action in bpy.data.actions:
				for fcurve in action.fcurves:
					if 'location' in fcurve.data_path:
						for point in fcurve.keyframe_points:					
							point.co[1] *= 0.01
							point.handle_left[1] *= 0.01
							point.handle_right[1] *= 0.01
			
			bpy.context.scene.unit_settings.scale_length = units_before_export
			
		# Revert animation curves location scale (initialized scale)	
		if arm_scale != 1.0:
			print("\nRevert action translation scale, since armature scale is:", arm_scale)
			for action in bpy.data.actions:
				for fcurve in action.fcurves:
					if 'location' in fcurve.data_path:
						for point in fcurve.keyframe_points:					
							point.co[1] *= 1/arm_scale
							point.handle_left[1] *= 1/arm_scale
							point.handle_right[1] *= 1/arm_scale
			
		# Revert push bend bones		
		if context.scene.arp_keep_bend_bones and context.scene.arp_push_bend:
			print("\nRevert Push Bend Bones")
			
			for _action in bpy.data.actions:		
				_push_bend_bones(_action, 0.5)		
							
				
		# Delete humanoid/mped actions
		if context.scene.arp_bake_actions:
			print("Deleting baked actions...")
			for action in bpy.data.actions:
				if action.name[:2] == "h_" or action.name[:3] == "mp_" or action.name[-9:] == "_humanoid":
					bpy.data.actions.remove(action, do_unlink = True)
		
		# Delete temporary objects
		print("Deleting copies...")
		for obj in bpy.data.objects:
			if "_arpexport" in obj.name or obj.name == "rig_humanoid" or obj.name == "root" or obj.name == "rig_mped" or "arp_dummy_mesh" in obj.name:				
				bpy.data.objects.remove(obj, do_unlink = True)
				
		for m in bpy.data.meshes:
			if "arp_dummy_mesh" in m.name:
				bpy.data.meshes.remove(m, do_unlink = True)		
	
				
		# Rename the renamed root object if any
		if bpy.data.objects.get("root_temp") != None:
			bpy.data.objects["root_temp"].name = "root"
			
		#Hide rig_add
		if bpy.data.objects.get(self.armature_add_name) != None:
			bpy.data.objects[self.armature_add_name].hide_viewport = True			
		
		# Set auto-key if needed		
		context.scene.tool_settings.use_keyframe_insert_auto = save_auto_key
		
		# Restore collections		
		for i, vis_value in enumerate(saved_collection_vis):			
			bpy.data.collections[i].hide_viewport = vis_value
			
		# Restore scene units type		
		context.scene.unit_settings.system = saved_unit_type
		
		#Restore the proxy picker		
		if proxy_picker_value != None:
			try:		
				bpy.context.scene.Proxy_Picker.active = proxy_picker_value
			except:
				pass
		
		# Restore selection
		set_active_object(current_selection[0])
		for i in current_selection[1]:
			bpy.data.objects[i].select_set(True)
		
		bpy.context.scene.update()
		
		print("\nARP FBX Export Done!")
		
		# Warning message
		if len(self.non_armature_actions) > 0:
			self.message_final += 'Some actions have been exported, that do not contain bones datas:'
			for act_name in self.non_armature_actions:
				self.message_final += '\n-' + act_name		
			self.message_final += '\nMay corrupt character animation!.\nCheck "Only Containing" to export only the armature action name'
			
			auto_rig.Report_Message.message = self.message_final
			auto_rig.Report_Message.icon_type = 'ERROR'
			bpy.ops.arp.report_message('INVOKE_DEFAULT')
		else:
			self.report({'INFO'}, 'Character Exported')
		
		return {'FINISHED'}

	def invoke(self, context, event):	
		context.window_manager.fileselect_add(self)	
		print("INVOKED!")
		return {'RUNNING_MODAL'}
	

			
class ARP_OT_export_dae(bpy.types.Operator):

	"""Export character in .dae file format"""
	bl_idname = "id.export_dae"
	bl_label = "Export .DAE"

	
	def execute(self, context):	
		self.armature_name = ""
		self.armature_add_name = ""
		self.char_objects = None	
		self.message_final = ""	
		self.non_armature_actions = []
		
		current_selection = [bpy.context.active_object.name, [i.name for i in bpy.context.selected_objects]]
		
		# Initial checks and warnings
			# is the addon installed?
		if not "io_scene_dae" in bpy.context.preferences.addons.keys():
			self.report({"ERROR"}, 'Install the "Better Collada Exporter" addon')
			return {'FINISHED'}	
	
		# Is the armature selected?		
		if bpy.context.active_object == None:
			self.report({"ERROR"}, 'Select the armature to export')
			return {'FINISHED'}	
		else:
			# set the armature as active object (if any)
			if bpy.context.active_object.type != "ARMATURE":
				for obj in bpy.context.selected_objects:
					if obj.type == "ARMATURE":
						set_active_object(obj.name)
						break
		
			if bpy.context.active_object.type != "ARMATURE":
				self.report({"ERROR"}, 'Select the armature to export')
				return {'FINISHED'}	
			else:
				# check for materials linked to Object instead of Data
				# is the selected armature a proxy?			
				armature_base_name = bpy.context.active_object.name	
				if bpy.context.active_object.proxy:			
					armature_base_name = bpy.context.active_object.proxy.name
					print("The armature is a proxy. Real name = ", armature_base_name)		
				
								
				limb_sides.get_multi_limbs()
				
				# check the facial bones are up to date
				if len(limb_sides.head_sides) > 0:
					jawbone_x = bpy.context.active_object.data.bones.get("jawbone.x")
					c_jawbone_x = bpy.context.active_object.data.bones.get("c_jawbone.x")
					eyelid_top = bpy.context.active_object.data.bones.get("eyelid_top.l")
					c_eyelid_top = bpy.context.active_object.data.bones.get("c_eyelid_top.l")
					
					if (jawbone_x == None and c_jawbone_x) or (eyelid_top == None and c_eyelid_top):
						self.report({"ERROR"}, "Armature not up to date. Click 'Update Armature'")
						return {'FINISHED'}	
				
		
		# Can the rig_add be found?		
		self.armature_name = bpy.context.active_object.name
		rig_add = get_rig_add(self.armature_name)
		if rig_add == None:
			self.report({"ERROR"}, 'rig_add not found. Invalid rig hierarchy.')
			return {'FINISHED'}	
			
		
		limb_sides.get_multi_limbs()
		
		# If Humanoid is selected, is it really a humanoid rig?
		found_subneck = False
		for b in bpy.context.active_object.data.bones:
			if 'c_subneck_' in b.name:
				found_subneck = True
				break
		
		if context.scene.arp_export_rig_type == "humanoid":		
			if len(limb_sides.arm_sides) > 2 or len(limb_sides.leg_sides) > 2 or len(limb_sides.head_sides) > 1 or len(limb_sides.ear_sides) > 2 or found_subneck:				
				self.report({"ERROR"}, ' This is not a humanoid rig: it contains duplicated limbs or non-humanoid limbs.\nSwitch to Universal type instead.')
				return {'FINISHED'}	
		
		
		# Is the NLA in tweak mode?
		nla_check()

		
		print("\n..............................Starting ARP DAE Export..............................")
		
		units_before_export = bpy.context.scene.unit_settings.scale_length
		
		# Disable the proxy picker to avoid bugs		
		proxy_picker_value = None
		try:	   
			proxy_picker_value = bpy.context.scene.Proxy_Picker.active
			bpy.context.scene.Proxy_Picker.active = False			
		except:
			pass
		
		# Disable auto-keyframe
		save_auto_key = context.scene.tool_settings.use_keyframe_insert_auto
		context.scene.tool_settings.use_keyframe_insert_auto = False
		
		# Enable all collections visibility
		saved_collection_vis = [i.hide_viewport for i in bpy.data.collections]
		
		for col in bpy.data.collections:
			is_cs_collection = False
			if len(col.objects) > 0:
				for obj in col.objects:
					if obj.name[:3] == "cs_":
						is_cs_collection = True
						break
			if not is_cs_collection:
				col.hide_viewport = False
			
		# Save the scene units type
		saved_unit_type = context.scene.unit_settings.system		
	
		self.armature_add_name = get_rig_add(self.armature_name)	
		
		# Create copy objects
		create_copies(self)	
		
		# Initialize arp_armatures scales
		arm_scale = bpy.data.objects[self.armature_name + '_arpexport'].scale[0]
		if arm_scale != 1.0:
			init_armatures_scales(self.armature_name, self.armature_add_name)		
			print("Scale initialized from", arm_scale, "to 1.0")		
		
		
		def initialize_armature_rotation(root_armature_name):
		
				root_armature = bpy.data.objects[root_armature_name]
				
				# parent meshes to armature
				for obj in bpy.context.selected_objects:
					if obj.type == "MESH":
						obj_mat = obj.matrix_world.copy()
						obj.parent = root_armature
						obj.matrix_world = obj_mat						
				
				# add -90 degrees rotation offset on X
				root_armature.rotation_euler[0] = math.radians(-90)
				
				# disable Copy Transforms constraint
				if len(root_armature.constraints) > 0:
					if root_armature.constraints[0].type == "COPY_TRANSFORMS":
						root_armature.constraints[0].mute = True
						
				# add copy location and copy scale instead
				cns1 = root_armature.constraints.new("COPY_LOCATION")
				cns1.target = bpy.data.objects[self.armature_name + "_arpexport"]
				cns2 = root_armature.constraints.new("COPY_SCALE")
				cns2.target = bpy.data.objects[self.armature_name + "_arpexport"]				
						
				# apply rotation
				set_active_object(root_armature_name)
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.select_all(action='DESELECT')
				set_active_object(root_armature_name)
				bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
				
				# revert rotation
				root_armature.rotation_euler[0] = math.radians(90)
		
				
		# Humanoid Export?
		if context.scene.arp_export_rig_type == "humanoid":
			
			# Set the humanoid armature
			_set_humanoid_rig(self.armature_name, self.armature_add_name)			
			
			# Bake Actions?				
			if context.scene.arp_bake_actions and len(bpy.data.actions) > 0:
				_bake_all(self.armature_name, "rig_humanoid", self)
			else:
				_bake_pose("rig_humanoid")
			
			
			# x100 units?			
			if context.scene.arp_units_x100:
				_set_units_x100_baked(self.armature_name)
			
			#parent the meshes to the humanoid rig for correct transformations export						
			bpy.data.objects[self.armature_name + "_arpexport"].data.pose_position = 'REST'
			bpy.context.scene.update()
			
			for obj_name in self.char_objects:
				if bpy.data.objects[obj_name + "_arpexport"].type == "MESH":
					ob = bpy.data.objects[obj_name + "_arpexport"]
					mat = ob.matrix_world
					ob.parent = bpy.data.objects["rig_humanoid"]
					ob.matrix_world = mat
			
			bpy.data.objects[self.armature_name + "_arpexport"].data.pose_position = 'POSE'	
				
			
			# Initialize armature rotation? << Experimental feature! >>
			if context.scene.arp_init_fbx_rot:
				initialize_armature_rotation("rig_humanoid")
			
			# Select objects to export
			_select_exportable(self.armature_name)
		
			# Rename "rig_humanoid" to root"		
				#another "root" name in scene?
			for obj in bpy.data.objects:
				if obj.name == "root":
					obj.name = "root_temp"
			
			bpy.data.objects["rig_humanoid"].name = "root"	
			
			
			
		# M-Ped Export?
		if context.scene.arp_export_rig_type == "mped":
			# Set the mped armature
			_set_mped_rig(self.armature_name, self.armature_add_name, False)	
						
			
			# Bake Actions?				
			if context.scene.arp_bake_actions and len(bpy.data.actions) > 0:
				_bake_all(self.armature_name, "rig_mped", self)
			else:
				_bake_pose("rig_mped")
			
			# x100 units?			
			if context.scene.arp_units_x100:
				_set_units_x100_baked(self.armature_name)
				
				
			# parent the meshes to the mped rig					
			bpy.data.objects[self.armature_name + "_arpexport"].data.pose_position = 'REST'
			bpy.context.scene.update()
			
			for obj_name in self.char_objects:
				if bpy.data.objects[obj_name + "_arpexport"].type == "MESH":
					ob = bpy.data.objects[obj_name + "_arpexport"]
					mat = ob.matrix_world
					ob.parent = bpy.data.objects["rig_mped"]
					ob.matrix_world = mat
			
			bpy.data.objects[self.armature_name + "_arpexport"].data.pose_position = 'POSE'	
			
			
			# Initialize Fbx armature rotation? << Experimental feature! >>
			if context.scene.arp_init_fbx_rot:
				initialize_armature_rotation("rig_mped")
			
			# Select objects to export
			_select_exportable(self.armature_name)
			
			# Rename "rig_mped" to root"		
				#another "root" name in scene?
			for obj in bpy.data.objects:
				if obj.name == "root":
					obj.name = "root_temp"
			
			bpy.data.objects["rig_mped"].name = "root"

			
		
					
		# Generic Export?
		if context.scene.arp_export_rig_type == "generic":
			_setup_generic(self.armature_name, self.armature_add_name)
			
			# x100 units?
			if context.scene.arp_units_x100:
				_set_units_x100_generic(self.armature_name, self.armature_add_name)
		
			_select_exportable(self.armature_name)
			
		
		# Rename to right names before export
		print("Renaming to def names...")
		for obj in bpy.data.objects:
			if "_arpexport" in obj.name:
				if bpy.data.objects.get(obj.name.replace("_arpexport", "")):
					#rename base object to "_arpbaseobject" instead, temporarily
					obj_name = obj.name.replace("_arpexport", "")
					bpy.data.objects[obj_name].name = obj_name + "_arpbaseobject"
					
					#rename _arpexport to right name
					obj.name = obj.name.replace("_arpexport", "")
				else:
					print("	   Cannot find base object name", obj.name)
			
			
	
		bpy.context.scene["is_arp_export"] = True
		
		# Export		
		print("\n..............................DAE Export..............................")		
		
		bpy.ops.export_scene.dae(filepath=self.filepath, object_types={'ARMATURE', 'MESH'}, use_export_selected=True, use_mesh_modifiers=True, use_exclude_armature_modifier=True, use_active_layers=True, use_exclude_ctrl_bones=True, use_anim=True, use_anim_action_all=context.scene.arp_bake_actions, use_anim_optimize=context.scene.arp_bake_actions, use_shape_key_export=True)
		
		bpy.context.scene["is_arp_export"] = False		
		print("Done.")
		
		# Revert name changes
		print("Revert name changes...")
		for obj in bpy.data.objects:
			if "_arpbaseobject" in obj.name:
				if bpy.data.objects.get(obj.name.replace("_arpbaseobject", "")):
					#rename final objects to "_arpexport"
					obj_name = obj.name.replace("_arpbaseobject", "")
					bpy.data.objects[obj_name].name = obj_name + "_arpexport"
					
					#rename _arpexport to right name
					obj.name = obj.name.replace("_arpbaseobject", "")
				else:
					print("	   Cannot find base object name", obj.name)
		
		
		# Revert animation curves location scale (x100 Units)		
		if units_before_export != context.scene.unit_settings.scale_length:
			print("\nRevert units changes")
			
			for action in bpy.data.actions:
				for fcurve in action.fcurves:
					if 'location' in fcurve.data_path:
						for point in fcurve.keyframe_points:					
							point.co[1] *= 0.01
							point.handle_left[1] *= 0.01
							point.handle_right[1] *= 0.01
			
			bpy.context.scene.unit_settings.scale_length = units_before_export
			
		# Revert animation curves location scale (initialized scale)	
		if arm_scale != 1.0:
			print("\nRevert action translation scale, since armature scale is:", arm_scale)
			for action in bpy.data.actions:
				for fcurve in action.fcurves:
					if 'location' in fcurve.data_path:
						for point in fcurve.keyframe_points:					
							point.co[1] *= 1/arm_scale
							point.handle_left[1] *= 1/arm_scale
							point.handle_right[1] *= 1/arm_scale
			
		# Revert push bend bones		
		if context.scene.arp_keep_bend_bones and context.scene.arp_push_bend:
			print("\nRevert Push Bend Bones")
			
			for _action in bpy.data.actions:		
				_push_bend_bones(_action, 0.5)		
							
				
		# Delete humanoid/mped actions
		if context.scene.arp_bake_actions:
			print("Deleting baked actions...")
			for action in bpy.data.actions:
				if action.name[:2] == "h_" or action.name[:3] == "mp_" or action.name[-9:] == "_humanoid":
					bpy.data.actions.remove(action, do_unlink = True)
		
		# Delete temporary objects
		print("Deleting copies...")
		for obj in bpy.data.objects:
			if "_arpexport" in obj.name or obj.name == "rig_humanoid" or obj.name == "root" or obj.name == "rig_mped" or "arp_dummy_mesh" in obj.name:				
				bpy.data.objects.remove(obj, do_unlink = True)
				
		for m in bpy.data.meshes:
			if "arp_dummy_mesh" in m.name:
				bpy.data.meshes.remove(m, do_unlink = True)		
	
				
		# Rename the renamed root object if any
		if bpy.data.objects.get("root_temp") != None:
			bpy.data.objects["root_temp"].name = "root"
			
		#Hide rig_add
		if bpy.data.objects.get(self.armature_add_name) != None:
			bpy.data.objects[self.armature_add_name].hide_viewport = True			
		
		# Set auto-key if needed		
		context.scene.tool_settings.use_keyframe_insert_auto = save_auto_key
		
		# Restore collections		
		for i, vis_value in enumerate(saved_collection_vis):			
			bpy.data.collections[i].hide_viewport = vis_value
			
		# Restore scene units type		
		context.scene.unit_settings.system = saved_unit_type
		
		# Restore the proxy picker		
		if proxy_picker_value != None:
			try:		
				bpy.context.scene.Proxy_Picker.active = proxy_picker_value
			except:
				pass
				
		# Restore selection
		set_active_object(current_selection[0])
		for i in current_selection[1]:
			bpy.data.objects[i].select_set(True)
		
		bpy.context.scene.update()
		
		print("\nARP DAE Export Done!")
		
		# Warning message
		if len(self.non_armature_actions) > 0:
			self.message_final += 'Some actions have been exported, that do not contain bones datas:'
			for act_name in self.non_armature_actions:
				self.message_final += '\n-' + act_name		
			self.message_final += '\nMay corrupt character animation!.\nCheck "Only Containing" to export only the armature action name'
			
			auto_rig.Report_Message.message = self.message_final
			auto_rig.Report_Message.icon_type = 'ERROR'
			bpy.ops.arp.report_message('INVOKE_DEFAULT')
		else:
			self.report({'INFO'}, 'Character Exported')
		
		return {'FINISHED'}

	def invoke(self, context, event):	
		context.window_manager.fileselect_add(self)	
		print("INVOKED!")
		return {'RUNNING_MODAL'}
		
		
		
		
class ARP_OT_bind_humanoid(bpy.types.Operator):
	  
	#tooltip
	"""Bind the Humanoid armature to the Auto-Rig Pro armature"""
	
	bl_idname = "id.bind_humanoid"
	bl_label = "bind_humanoid"
	bl_options = {'UNDO'}	

	
	@classmethod
	def poll(cls, context):
		
		if context.active_object != None:		
			if bpy.data.objects.get("rig_humanoid") != None:	
				if len(bpy.data.objects['rig_humanoid'].keys()) > 0:
					#if 'set' in bpy.data.objects['rig_humanoid'].keys():
					if bpy.data.objects['rig_humanoid']['binded'] == 0:# and bpy.data.objects['rig_humanoid']['set'] == 1:						
						return True
					else:
						return False	
				else:
					return True
			else:
				return False
				

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		
		try:
				bpy.data.objects["rig_humanoid"]				
		except:
			self.report({'ERROR'}, "Please append the Humanoid armature in the scene.")
			return{'FINISHED'} 
		try:
			bpy.data.objects["rig"]
		except:
			self.report({'ERROR'}, "Please append the Auto-Rig Pro armature in the scene.")
			return{'FINISHED'} 
		
		#save current state			  
		current_mode = context.mode		   
		current_obj = context.active_object
		
		_constraint_rig(False)
		
		#restore state
		try:	 
			set_active_object(current_obj.name)
			bpy.ops.object.mode_set(mode=current_mode)			 
		   
		except:
			pass
			
		finally:
			context.preferences.edit.use_global_undo = use_global_undo	   
		
		return {'FINISHED'} 

class ARP_OT_unbind_humanoid(bpy.types.Operator):
	  
	#tooltip
	"""Unbind the Humanoid armature to the Auto-Rig Pro armature. \nUnbind when exporting multiple baked actions. Bind before baking actions"""
	
	bl_idname = "id.unbind_humanoid"
	bl_label = "unbind_humanoid"
	bl_options = {'UNDO'}	

	
	@classmethod
	def poll(cls, context):		
			
		if context.active_object != None:
			#if bpy.context.scene.arp_rename_for_ue == False:
			if bpy.data.objects.get("rig_humanoid") != None:
				if len(bpy.data.objects['rig_humanoid'].keys()) > 0:
					#if 'set' in bpy.data.objects['rig_humanoid'].keys():
					if bpy.data.objects['rig_humanoid']['binded'] == 1:# and bpy.data.objects['rig_humanoid']['set'] == 1:
						return True
					else:
						return False	
				else:
					return False
			else:
				return False
				

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		
		try:
				bpy.data.objects["rig_humanoid"]				
		except:
			self.report({'ERROR'}, "Please append the Humanoid armature in the scene.")
			return{'FINISHED'} 
		try:
			bpy.data.objects["rig"]
		except:
			self.report({'ERROR'}, "Please append the Auto-Rig Pro armature in the scene.")
			return{'FINISHED'} 
		
		#save current state			  
		current_mode = context.mode		   
		current_obj = context.active_object
		
		_constraint_rig(True)
		
		#restore state
		try:	 
			set_active_object(current_obj.name)
			bpy.ops.object.mode_set(mode=current_mode)			 
		   
		except:
			pass
			
		finally:
			context.preferences.edit.use_global_undo = use_global_undo	   
		
		return {'FINISHED'} 
		
 
	  
		
############ FUNCTIONS ##############################################################
def nla_check():	
	if bpy.context.scene.is_nla_tweakmode:
		# try to find the NLA context window for context override			
		win = bpy.context.window
		scr = win.screen
		areas3d = [area for area in scr.areas if area.type == 'NLA_EDITOR']
		if len(areas3d) > 0:
			region	 = [region for region in areas3d[0].regions if region.type == 'WINDOW']
			override = {'window':win, 'screen':scr,'area'  :areas3d[0],'region':region,'scene' :bpy.context.scene}
			
			# exit tweak mode
			bpy.ops.nla.tweakmode_exit(override)


def create_copies(self):
	print("\nCreate copies...")			
		# proxy?		
	armature_proxy_name = None
	if bpy.context.active_object.proxy:			
		armature_proxy_name = bpy.context.active_object.proxy.name
		print("The armature is a proxy. Real name = ", armature_proxy_name)					
	
		# store actions
	actions_list = [action.name for action in bpy.data.actions]	
	rig_action = bpy.data.objects[self.armature_name].animation_data.action
		
		# get meshes
	self.char_objects = get_char_objects(arm_name = self.armature_name, arm_add_name = self.armature_add_name, arm_proxy = armature_proxy_name)		
	print("Character objects:", self.char_objects)
	
		#clear selection and mode
	set_active_object(self.armature_name)
	bpy.ops.object.mode_set(mode='OBJECT')		
	bpy.ops.object.select_all(action='DESELECT')
	
		# duplicate
	for obj_name in self.char_objects:			
		# make sure it's selectable
		selectable_state = bpy.data.objects[obj_name].hide_select
		bpy.data.objects[obj_name].hide_select = False
		set_active_object(obj_name)
		
		try:
			bpy.ops.object.mode_set(mode='OBJECT')
		except:
			print("Cannot set mode to object for", obj_name, ". Proxy object?")				
		
		# get shape key action if any
		current_sk_action = None
		try:
			current_sk_action = bpy.data.objects[obj_name].data.shape_keys.animation_data.action
		except:
			pass
		
		# duplicate and rename
		bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
		bpy.context.active_object.name = obj_name + "_arpexport"		
		
		# assign object's shape key action if any
		if current_sk_action != None:
			bpy.context.active_object.data.shape_keys.animation_data.action = current_sk_action
			print("Assign action", current_sk_action.name)
		
		bpy.ops.object.select_all(action='DESELECT')	
		
		# restore selectable state
		bpy.data.objects[obj_name].hide_select = selectable_state			
		
				
		# parent meshes to armature		
	for obj_name in self.char_objects:
		ob = bpy.data.objects[obj_name + "_arpexport"]
		if ob.type == "MESH":
			ob_mat = ob.matrix_world.copy()
			ob.parent = bpy.data.objects[self.armature_name + "_arpexport"]
			ob.matrix_world = ob_mat
			
	deforming_arm = self.armature_name		
	
	if armature_proxy_name != None:
		deforming_arm = armature_proxy_name
	
		# assign the _arpexport rig as target for armature modifiers
	for obj in bpy.data.objects:
		if "_arpexport" in obj.name and obj.type == "MESH":
			if len(obj.modifiers) > 0:
				for mod in obj.modifiers:
					if mod.type == "ARMATURE":
						if mod.object != None:
							if mod.object.name == deforming_arm:									
								mod.object = bpy.data.objects[self.armature_name + "_arpexport"]								
															
							# delete the rig_add modifier
							if mod.object != None:
								if "rig_add" in mod.object.name:
									obj.modifiers.remove(mod)
	
		# delete duplicated actions
	for action in bpy.data.actions:
		if not action.name in actions_list:
			bpy.data.actions.remove(action, do_unlink = True)
			
		# assign the current action to the duplicated rig
	bpy.data.objects[self.armature_name + "_arpexport"].animation_data.action = rig_action
	
	
	print("Copied.")
			
			
			
def is_proxy_bone(bone):
	#bone = edit bone or pose bone
	
	if bone.parent:
			bone_parent1 = bone.parent.name
	else:
		bone_parent1 = "None"
			
	if '_proxy' in bone.name or 'Picker' in bone_parent1 or bone.name == "Picker":
		return True
		

def get_edit_bone(name):
	try:
		return bpy.context.active_object.data.edit_bones[name]
	except:
		return None

def is_deforming(bone):
	if get_edit_bone(bone) != None:
		return get_edit_bone(bone).use_deform	

	
def set_active_object(object_name):
	 bpy.context.view_layer.objects.active = bpy.data.objects[object_name]
	 bpy.data.objects[object_name].select_set(state=True)

def get_pose_bone(name):
	if bpy.context.active_object.pose.bones.get(name) != None:
		return bpy.context.active_object.pose.bones[name]
	else:
		return None
	
def set_inverse_child(b, cns_name):
	pbone = bpy.context.active_object.pose.bones[b]
	context_copy = bpy.context.copy()
	context_copy["constraint"] = pbone.constraints[cns_name]
	bpy.context.active_object.data.bones.active = pbone.bone
	try:
		bpy.ops.constraint.childof_set_inverse(context_copy, constraint=cns_name, owner='BONE')	
	except:
		print('Invalid bone constraint to set inverse child, skip it', b)
					
def is_facial_enabled(armature):
	if armature.data.bones.get("c_jawbone.x"):
		return True
	return False

					
def is_facial_bone(bone_name):
	for facebone in default_facial_bones:
		if facebone in bone_name:
			return True
	
	for facebone1 in additional_facial_bones:
		if facebone1 in bone_name:
			return True
			
def is_bend_bone(bone_name):		
	for bbone in bend_bones:
		if bbone in bone_name:
			return True
			
def _push_bend_bones(act, fac):
	for fcurve in act.fcurves:	   
		for bbone in bend_bones_add:
			if bbone in fcurve.data_path:				
				for key in fcurve.keyframe_points:
					if not 'scale' in fcurve.data_path:							
						key.co[1] *= fac
						key.handle_left[1] *= fac
						key.handle_right[1] *= fac						
						
					else:
						key.co[1] = 1 + (key.co[1] -1) * fac
						key.handle_left[1] = 1 + (key.handle_left[1] -1) * fac 
						key.handle_right[1] = 1 + (key.handle_right[1] -1) * fac
				break

def init_armatures_scales(armature_name, armature_add_name):			
	
		
	rig_humanoid = None
	
	set_active_object(armature_name + "_arpexport")
	bpy.ops.object.mode_set(mode='OBJECT')	
	
	arp_armature = bpy.data.objects[armature_name + '_arpexport']	
	rig_scale = arp_armature.scale[0]
	rig_add = bpy.data.objects[armature_add_name + '_arpexport']
	rig_add.hide_viewport = False
	
	# Apply Scale
	rig_add.scale = arp_armature.scale
	if bpy.data.objects.get("rig_humanoid"):
		rig_humanoid = bpy.data.objects["rig_humanoid"]
		rig_humanoid.scale = arp_armature.scale
		
	bpy.ops.object.select_all(action='DESELECT')
	set_active_object(rig_add.name)		
	bpy.ops.object.mode_set(mode='OBJECT')	
	bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
	
	bpy.ops.object.select_all(action='DESELECT')
	set_active_object(arp_armature.name)	
	
	bpy.ops.object.mode_set(mode='OBJECT')	
	bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)	
	
	print("scaling location:", rig_scale)
	# Apply scale to animation curves			 
	for action in bpy.data.actions:
		for fcurve in action.fcurves:
			if 'location' in fcurve.data_path and "pose.bones[" in fcurve.data_path:
				for point in fcurve.keyframe_points:					
					point.co[1] *= rig_scale
					point.handle_left[1] *= rig_scale
					point.handle_right[1] *= rig_scale
			
	# Reset set inverse child of constraints
	for pbone in bpy.context.active_object.pose.bones:		
		# do not reset child of of "cc_" bones... issues
		if pbone.name[:3] != "cc_" and len(pbone.constraints) > 0:
			for cns in pbone.constraints:
				if cns.type == "CHILD_OF" and not cns.mute:					
					if	cns.subtarget != "":					
						if get_pose_bone(cns.subtarget) != None:
							cns.inverse_matrix = bpy.context.active_object.matrix_world @ get_pose_bone(cns.subtarget).matrix
							print("Reset child of ", pbone.name)
					
	
	# Reset stretches				
		#store active pose			
	bpy.ops.object.mode_set(mode='POSE')
	bpy.ops.pose.select_all(action='SELECT')
	bpy.ops.pose.copy()
		#need to reset the pose
	auto_rig_reset.reset_all()
		#reset constraints
	for pbone in bpy.context.active_object.pose.bones:
		try:							
			pbone.constraints["Stretch To"].rest_length = 0.0					
		except:
			pass
		
		#restore the pose
		
	bpy.ops.pose.paste(flipped=False)
	
	rig_add.hide_viewport =True
	
	bpy.ops.object.mode_set(mode='OBJECT')	
	bpy.ops.object.select_all(action='DESELECT')
	
	
	
	# Rig Humanoid
	if bpy.data.objects.get("rig_humanoid"):
		# Apply Scale
		rig_humanoid = bpy.data.objects["rig_humanoid"]
		
		set_active_object("rig_humanoid")
		bpy.ops.object.mode_set(mode='OBJECT')	
		bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)	
						
		# Reset Child Of constraints
		
			# bind to main armature if not bound
		bind_state = rig_humanoid["binded"]		
		_constraint_rig(False)
		
			#set arp in rest pose
		arp_armature.data.pose_position = "REST"
		bpy.context.scene.update()
		
			#reset child of constraints		
		bpy.ops.object.mode_set(mode='POSE')
		rig_humanoid.data.layers[16] = True
		rig_humanoid.data.layers[17] = True		
			
		for pbone in bpy.context.active_object.pose.bones:
			if len(pbone.constraints) > 0:
				for cns in pbone.constraints:
					if 'Child Of' in cns.name:
						set_inverse_child(pbone.name, cns.name)
				
		
		rig_humanoid.data.layers[16] = False
		rig_humanoid.data.layers[17] = False
		
		#restore bind state
		if bind_state == 0:
			_constraint_rig(True)
			
		#Set arp in pose
		arp_armature.data.pose_position = "POSE"
		bpy.context.scene.update()
		
def _add_ik_bones():

	bpy.ops.object.mode_set(mode='EDIT')
	sides = [".l", ".r"]
	
	# Feet
	for side in sides:
		
		if get_edit_bone("foot" + side) != None:
			foot = get_edit_bone("foot" + side)
			# create the IK root bone
			if get_edit_bone("ik_foot_root") == None:
				new_bone = bpy.context.active_object.data.edit_bones.new("ik_foot_root")				
				new_bone.head = Vector((0,0,0))
				new_bone.tail = Vector((0,5,0))
				new_bone.roll = 0.0
			
			# create the IK foot				
			foot_ik = bpy.context.active_object.data.edit_bones.new("ik_foot" + side)				
			foot_ik.head = foot.head
			foot_ik.tail = foot.tail
			foot_ik.roll = foot.roll
			foot_ik.parent = get_edit_bone("ik_foot_root")
	
	# Hands
	# First check the right hand is there, since "ik_hand_gun" is located at the the right hand location
	if get_edit_bone("hand.r") != None:
		hand_r = get_edit_bone("hand.r")
		# create the IK root bone		
		ik_hand_root = bpy.context.active_object.data.edit_bones.new("ik_hand_root")				
		ik_hand_root.head = Vector((0,0,0))
		ik_hand_root.tail = Vector((0,5,0))
		ik_hand_root.roll = 0.0
		
		#create the IK hand gun
		ik_hand_gun = bpy.context.active_object.data.edit_bones.new("ik_hand_gun")				
		ik_hand_gun.head = hand_r.head
		ik_hand_gun.tail = hand_r.tail
		ik_hand_gun.roll = hand_r.roll
		ik_hand_gun.parent = ik_hand_root
		
		# create the IK hands
		for side in sides:		
			hand = get_edit_bone("hand" + side)
			ik_hand = bpy.context.active_object.data.edit_bones.new("ik_hand" + side)				
			ik_hand.head = hand.head
			ik_hand.tail = hand.tail
			ik_hand.roll = hand.roll
			ik_hand.parent = ik_hand_gun
			
				
			
		
def _set_mannequin_orientations():
	
	# Get 3D Viewport space_data
	space_viewport = None
	for screen in bpy.data.screens:	  
		for a in screen.areas:
			if a.type == "VIEW_3D":			
				for space in a.spaces:				
					if space.type == "VIEW_3D":
						space_viewport = space
	
	set_active_object("rig_humanoid")
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.select_all(action='DESELECT')
	set_active_object("rig_humanoid")
	bpy.ops.object.mode_set(mode='EDIT')
	
	bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
	
	
	_spine = ['pelvis', 'spine', 'neck', 'head']
	_arms = ['clavicle', 'upperarm', 'lowerarm']
	_hand = ['hand']
	_fingers = ['thumb', 'index', 'middle', 'ring', 'pinky']
	_legs = ['thigh', 'calf']
	_foot = ['foot']
	_toes = ['ball']
	
	bones_dict = {}				
	
	print("\nSet Mannequin Axes bones...")
			
	#display layers	
	bpy.context.active_object.data.layers[0] = True
	bpy.context.active_object.data.layers[16] = True
	bpy.context.active_object.data.layers[17] = True

	print("	   Build transform dict...")
	#build a dict of bones transforms, excluding custom bones, bend bones
	for e_bone in bpy.context.active_object.data.edit_bones:
		if not '_orient' in e_bone.name and e_bone.name[:3] != "cc_" and not is_bend_bone(e_bone.name):
			bones_dict[e_bone.name] = e_bone.head.copy(), e_bone.tail.copy(), e_bone.roll
		
	
	rotate_value = 0.0
	rotate_axis = (True, False, False)
	roll_value = 0.0
	
	
	print("	   Add new bones...")
	#Add new _childof and _orient bones
	for ebone in bones_dict:
		bone_to_create = ""
		
		#spine 
		for b in _spine:
			if b in ebone:				
				rotate_value = -pi/2
				roll_value = math.radians(-90)				
				bone_to_create = ebone
				rotate_axis = (True, False, False)
				break
		
		#arms
		if bone_to_create == "":
			for b in _arms:
				if b in ebone:
					if '.l' in ebone[-2:]:
						rotate_value = -pi/2
						roll_value = math.radians(180)
						
					if '.r' in ebone[-2:]:
						rotate_value = -pi/2
						roll_value = math.radians(0)
						
					bone_to_create = ebone
					rotate_axis = (False, False, True)
					break
			
		#hand
		if bone_to_create == "":
			for b in _hand:
				if b in ebone:
					if '.l' in ebone[-2:]:
						rotate_value = -pi/2
						roll_value = math.radians(-90)
						
					if '.r' in ebone[-2:]:
						rotate_value = pi/2
						roll_value = math.radians(-90)
						
					bone_to_create = ebone
					rotate_axis = (True, False, False)
					break
				
		#fingers
		if bone_to_create == "":
			for b in _fingers:
				if b in ebone:
					if '.l' in ebone[-2:]:
						rotate_value = -pi/2
						roll_value = math.radians(-90)
						
					if '.r' in ebone[-2:]:
						rotate_value = pi/2
						roll_value = math.radians(-90)
						
					bone_to_create = ebone
					rotate_axis = (True, False, False)
					break
					
					
		#legs		
		if bone_to_create == "":
			for b in _legs:
				if b in ebone:
					if '.l' in ebone[-2:]:
						rotate_value = pi/2
						roll_value = math.radians(180)
						
					if '.r' in ebone[-2:]:
						rotate_value = pi/2
						roll_value = math.radians(0)
						
					bone_to_create = ebone
					rotate_axis = (False, False, True)
					break
					
					
		#foot		
		if bone_to_create == "":
			for b in _foot:
				if b in ebone:
					if '.l' in ebone[-2:]:
						rotate_value = pi
						roll_value = math.radians(90)
						
					if '.r' in ebone[-2:]:
						rotate_value = 0.0
						roll_value = math.radians(-90)
						
					bone_to_create = ebone
					rotate_axis = (False, False, True)
					break
					
		#toes		
		if bone_to_create == "":
			for b in _toes:
				if b in ebone:
					if '.l' in ebone[-2:]:
						rotate_value = -pi/2
						roll_value = math.radians(-90)
						
					if '.r' in ebone[-2:]:
						rotate_value = pi/2
						roll_value = math.radians(-90)
						
					bone_to_create = ebone
					rotate_axis = (True, False, False)
					break				
				
		
				
				
		if bone_to_create != "" and get_edit_bone(bone_to_create + "_orient") == None:
			
			
			#create _childof bones
			new_bone = bpy.context.active_object.data.edit_bones.new(bone_to_create + "_childof") 
			new_bone.head = bones_dict[bone_to_create][0]
			new_bone.tail = bones_dict[bone_to_create][1]
			new_bone.roll = bones_dict[bone_to_create][2]	
			new_bone.use_deform = False

				#set in layer 16
			new_bone.layers[16] = True
			for i in range(0,31):
				if i != 16:
					new_bone.layers[i] = False					
					
					
			#disable deform of the other bones
			get_edit_bone(bone_to_create).use_deform = False							
			
			
			#orient it
				#select
			bpy.ops.armature.select_all(action='DESELECT')
			bpy.context.active_object.data.edit_bones.active = bpy.context.active_object.data.edit_bones[bone_to_create + "_childof"]
			bpy.context.active_object.data.edit_bones.active.select = True
			
				#selection debug
			bpy.ops.object.mode_set(mode='POSE')
			bpy.ops.object.mode_set(mode='EDIT')
			
				#rotate		
			bone_childof = get_edit_bone(bone_to_create + "_childof")
			save_head_pos = bone_childof.head.copy()
		
				
			bpy.ops.transform.rotate(value=-rotate_value, constraint_axis=rotate_axis, orient_type='NORMAL', mirror=False, proportional='DISABLED')
			
			# make sure the bone root is aligned... bug, individual origin rotation does not seem to work 
				
			translation_vec = save_head_pos - bone_childof.head			
			bone_childof.head += translation_vec
			bone_childof.tail += translation_vec					
			
			bone_childof.roll += roll_value
			
				#flatten toes, foot
			if 'foot' in bone_to_create:
				 # flatten vertically 95% since 100% may lead to rotation artefact in Unreal
				bone_childof.tail[2] += (bone_childof.head[2]-bone_childof.tail[2])*0.95
			
				#set roll
				bpy.ops.armature.select_all(action='DESELECT')
				bone_childof.select = True
				bone_childof.select_head = True
				bone_childof.select_tail = True
				bpy.ops.armature.calculate_roll(type='GLOBAL_NEG_X')
				
			if 'ball' in bone_to_create:
				bone_childof.tail[1] = bone_childof.head[1]
				bone_childof.tail[0] = bone_childof.head[0]
				
				#special spine orientations
			if 'spine_01' in bone_to_create:
				bone_childof.tail[2] = bone_childof.head[2]
				bpy.ops.transform.rotate(value=-math.radians(-7), constraint_axis=(False, False, True), orient_type='NORMAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SHARP', proportional_size=15.8631)
				
			if 'spine_02' in bone_to_create or 'spine_03' in bone_to_create:
				bone_childof.tail[2] = bone_childof.head[2]
				bpy.ops.transform.rotate(value=-math.radians(8), constraint_axis=(False, False, True), orient_type='NORMAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SHARP', proportional_size=15.8631)
				
				
						
			#create main orient bones			
			new_bone1 = bpy.context.active_object.data.edit_bones.new(bone_to_create + "_orient")			
			new_bone1.head = get_edit_bone(bone_to_create + "_childof").head.copy()
			new_bone1.tail = get_edit_bone(bone_to_create + "_childof").tail.copy()
			new_bone1.roll = get_edit_bone(bone_to_create + "_childof").roll

				#set in layer 16
			new_bone1.layers[17] = True
			for i in range(0,31):
				if i != 17:
					new_bone1.layers[i] = False					
			
			
			#add childof bones constraint
			bpy.ops.object.mode_set(mode='POSE')
			
			cns = get_pose_bone(bone_to_create + "_childof").constraints.new('CHILD_OF')		
			cns.target = bpy.context.active_object
			cns.subtarget = bone_to_create
			cns.inverse_matrix = get_pose_bone(bone_to_create).bone.matrix_local.to_4x4().inverted()
			
			#add main orient bone constraint
			cns1 = get_pose_bone(bone_to_create + "_orient").constraints.new('COPY_TRANSFORMS')		
			cns1.target = bpy.context.active_object
			cns1.subtarget = bone_to_create + "_childof"			
			
			bpy.ops.object.mode_set(mode='EDIT')
			
	
	print("	   Set parents...")
	#Set parents
	for ebone in bpy.context.active_object.data.edit_bones:
		# _orient bones parent
		if '_orient' in ebone.name:
			associated_bone = get_edit_bone(ebone.name.replace('_orient', ""))
			if associated_bone.parent:						
				ebone.parent = get_edit_bone(associated_bone.parent.name + "_orient")
				continue
		
		# _facial bones parent
		for facial_bone in default_facial_bones:	
			if ebone.parent != None:
				if facial_bone in ebone.name and get_edit_bone(ebone.parent.name + "_orient") != None:					
					ebone.parent = get_edit_bone(ebone.parent.name + "_orient")				
					break
				
		for add_facebone in additional_facial_bones:
			if ebone.parent != None:
				if add_facebone in ebone.name and get_edit_bone(ebone.parent.name + "_orient") != None:					
					ebone.parent = get_edit_bone(ebone.parent.name + "_orient")
					break
				
		# custom controllers, bend bones
		if ebone.name[:3] == "cc_" or is_bend_bone(ebone.name):
			if ebone.parent != None:
				if get_edit_bone(ebone.parent.name + "_orient") != None:
					ebone.parent = get_edit_bone(ebone.parent.name + "_orient")
					
		# tail bones
		if ebone.name[:7] == 'c_tail_':
			if ebone.parent:
				bone_parent_orient = get_edit_bone(ebone.parent.name + "_orient")
				if bone_parent_orient:						
					ebone.parent = bone_parent_orient
	
		
	
					
	
	print("	   Rename bones...")		
	#rename all
	for ebone in bpy.context.active_object.data.edit_bones:
		if ebone.name[:3] != "cc_" and not is_bend_bone(ebone.name) and not is_facial_bone(ebone.name) and ebone.name[:7] != 'c_tail_': 
			if not '_orient' in ebone.name and not '_childof' in ebone.name :
				if "pelvis" in ebone.name:
					print(ebone.name, "RENAMED", ebone.name + "_basebone")
				ebone.name = ebone.name + "_basebone"
				
			
	for ebone in bpy.context.active_object.data.edit_bones:
		if '_orient' in ebone.name:
			ebone.name = ebone.name.replace("_orient", "")
		
	print("	   Rename vgroups...")		
	#rename vgroups
	for obj in bpy.data.objects:
		if len(obj.vertex_groups) > 0:
			for vgroup in obj.vertex_groups:
				if '_basebone' in vgroup.name:
					vgroup.name = vgroup.name.replace("_basebone", "")
	
	bpy.ops.object.mode_set(mode='POSE')	
	
	#set to euler, orientation artefact when importing in Unreal with quaternions...
	for pbone in bpy.context.active_object.pose.bones:
		pbone.rotation_mode = 'XYZ'
	
	
	print("	   Done.")
	

def _unset_ue_orientations():	
	#save current mode
	active_obj = None
	current_mode = None
	
	try:		
		active_obj = bpy.context.active_object
		current_mode = bpy.context.mode	
	except:
		print("Could not save mode")

	set_active_object("rig_humanoid")
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.select_all(action='DESELECT')
	set_active_object("rig_humanoid")
	bpy.ops.object.mode_set(mode='EDIT')
	
	bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
	
	_spine = ['pelvis', 'spine', 'neck', 'head']
	_arms = ['clavicle', 'upperarm', 'lowerarm']
	_hand = ['hand']
	_fingers = ['thumb', 'index', 'middle', 'ring', 'pinky']
	_legs = ['thigh', 'calf']
	_foot = ['foot']
	_toes = ['ball']
	
	bones_dict = {}
	
	
	print("Unset Mannequin Axes...")
	#display layers	
	bpy.context.active_object.data.layers[0] = True
	bpy.context.active_object.data.layers[16] = True
	bpy.context.active_object.data.layers[17] = True
	
	
	print("Re-parent bones...")
	#Parent bones
	for ebone4 in bpy.context.active_object.data.edit_bones:
		if ebone4.parent:
			#parent custom controllers
			if ebone4.name[:3] == "cc_":
				ebone4.parent = get_edit_bone(ebone4.parent.name + "_basebone")
				
			#parent facial bones
			elif ebone4.parent.name == "head":
				ebone4.parent = get_edit_bone("head_basebone")		
			
			#parent bend bones
			elif is_bend_bone(ebone4.name):
				ebone4.parent = get_edit_bone(ebone4.parent.name + "_basebone")
			
	
	print("Delete mannequin axes bones...")
	#delete orient and childof bones
	for __ebone in bpy.context.active_object.data.edit_bones:
		if (not '_childof' in __ebone.name and not '_basebone' in __ebone.name and not is_facial_bone(__ebone.name) and __ebone.name[:3] != "cc_" and not is_bend_bone(__ebone.name)) or '_childof' in __ebone.name:				
			bpy.context.active_object.data.edit_bones.remove(__ebone)		

	print("Rename bones...")
	for ebone3 in bpy.context.active_object.data.edit_bones:
		#rename
		if "_basebone" in ebone3.name:
			ebone3.name = ebone3.name.replace("_basebone", "")
			
			#enable deform
			ebone3.use_deform = True
	
	
	bpy.ops.object.mode_set(mode='POSE')
	
			
	#display 16-17 layers	
	bpy.context.active_object.data.layers[0] = True
	
	#make sure a bone is selected_bones
	bpy.ops.pose.select_all(action='DESELECT')
	
	try:
		bpy.context.active_object.data.bones.active = bpy.context.active_object.data.bones["pelvis"]
		bpy.context.active_object.pose.bones["pelvis"].bone.select = True
	except:
		pass
	
	print("Done.")

	try:				
		bpy.ops.object.mode_set(mode=current_mode)
		set_active_object(active_obj.name)		
	except:
		print("Could not restore mode")
		
	print("Done.")

	
def _bake_pose(baked_armature_name):

	
	
	set_active_object(baked_armature_name)
	bpy.ops.object.mode_set(mode='POSE')	
	
	for pbone in bpy.context.active_object.pose.bones:
		mat = pbone.matrix.copy()
		pbone.matrix = mat
	
	_constraint_rig(True)
	
	
def _bake_all(armature_name, baked_armature_name, self):
	
	arp_armature = bpy.data.objects[armature_name + '_arpexport']
	scn = bpy.context.scene
		
	
	baked_armature = bpy.data.objects[baked_armature_name]		
	
	"""
	# Ensure the armature pose is exported if there's no action by keyframing the current pose to create an action
	if len(bpy.data.actions) == 0:		
		set_active_object(baked_armature.name)		
		bpy.ops.object.mode_set(mode='POSE')
		bpy.ops.pose.select_all(action='SELECT')
		bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')
		try:
			bpy.data.actions[0].name = '
	"""
	
	if len(bpy.data.actions) > 0:
	
		print("..............................Found actions, baking..............................")		
			
		actions = bpy.data.actions
		
		#make sure it's binded
		print("Binding")
		_constraint_rig(False)
		print("Binded.")
		
		i=0
		for action in actions:
			action_name_split = action.name.split('_')
			
			bake_this_action = False
			
			# Is the action not already a baked one?
			if scn.arp_export_rig_type == "humanoid":
				if action.name[:2] != 'h_' and not 'humanoid' in action_name_split[len(action_name_split)-1]:#if not a baked action
					bake_this_action = True
			
			if scn.arp_export_rig_type == "mped":
				if action.name[:3] != 'mp_' and not 'mped' in action_name_split[len(action_name_split)-1]:#if not a baked action
					bake_this_action = True
					
			
			# Is "only containing" enable? If yes does the action name contains the given word?
			if bpy.context.scene.arp_export_name_actions:
				if not bpy.context.scene.arp_export_name_string in action.name:
					bake_this_action = False
								
			
			
			if bake_this_action:
			
				print("Baking action:", action.name)
				frame_range =action.frame_range	
				
				# Check if this action contains no bones fcurves. If so, can lead to wrong animation export, a message is shown at the end to warn the user
				found_bone_fcurve = False
				
				for fc in action.fcurves:
					if "pose.bones[" in fc.data_path:
						found_bone_fcurve = True
						break
				
				if not found_bone_fcurve:
					self.non_armature_actions.append(action.name)			
				
				
				# Add 0.01 angle offset to rotation keyframes if values == 0.0 to fix wrong rotation export		
				if scn.arp_fix_fbx_rot:						
					for fcurve in action.fcurves:
						if 'rotation' in fcurve.data_path and "pose.bones" in fcurve.data_path:								
							for point in fcurve.keyframe_points:
								if point.co[1] == 0.0:
									point.co[1] += 0.0002
									point.handle_left[1] += 0.0002
									point.handle_right[1] += 0.0002
							
					set_active_object(arp_armature.name)		
					bpy.ops.object.mode_set(mode='POSE')
					for pbone in bpy.context.active_object.pose.bones:					
						if "c_" or "cc_" in pbone.name:
							if pbone.rotation_euler[0] == 0.0:
								pbone.rotation_euler[0] += 0.0002
							if pbone.rotation_euler[1] == 0.0:
								pbone.rotation_euler[1] += 0.0002
							if pbone.rotation_euler[2] == 0.0:
								pbone.rotation_euler[2] += 0.0002
					
					bpy.ops.object.mode_set(mode='OBJECT')
					bpy.ops.object.select_all(action='DESELECT')
					set_active_object(baked_armature.name)
				
				# assign the action to the object
				arp_armature.animation_data.action = action	
				if baked_armature.animation_data:
					baked_armature.animation_data.action = None		
				
				bpy.ops.object.mode_set(mode='POSE')
				
				# Only select the deforming bones for baking
				bpy.ops.pose.select_all(action='DESELECT')
				baked_armature.data.layers[16] = False
				bpy.ops.pose.select_all(action='SELECT')
				
				if scn.arp_mannequin_axes:	
					bpy.ops.pose.select_all(action='DESELECT')
					
					#select only deforming bones for baking
					for pbone in bpy.context.active_object.pose.bones:
						split = pbone.name.split("_")						
						if split[len(split)-1] != "childof" and split[len(split)-1] != "basebone":							
							pbone.bone.select = True								
				
				#if i == 1:
				#	print(br)
				
				# Bake bones transforms
				bpy.ops.nla.bake(frame_start=frame_range[0], frame_end=frame_range[1], visual_keying=True, only_selected= True, bake_types={'POSE', 'OBJECT'})
				
				
				# Bake fcurve of custom properties driving shape keys if any
				for ob in bpy.data.objects:
					if ob.type == "MESH" and "_arpexport" in ob.name:
						sk_drivers = get_shape_keys_drivers(ob)
						
						if sk_drivers != None:								
							for dr in sk_drivers:
								for var in dr.driver.variables:								
									if var.type == "SINGLE_PROP":										
										prop_dp = var.targets[0].data_path
										spl = prop_dp.split('"')
										# if it's a custom property, copy the fcurve
										if len(spl) == 5: 
											fcurve_source = arp_armature.animation_data.action.fcurves.find(prop_dp)
											
											if fcurve_source != None:
												print("Found custom prop driver fcurves for SK, copy it", prop_dp)												
												new_fc = bpy.context.active_object.animation_data.action.fcurves.new(fcurve_source.data_path)
												
												for fr in range(0, int(frame_range[1])):
													val = fcurve_source.evaluate(fr)
													new_fc.keyframe_points.insert(fr, val)
											
									
							
				
				
				#if same name already exists, delete old one
				action_prefix = ""
				
				if scn.arp_export_rig_type == "humanoid":
					action_prefix = "h_"
				if scn.arp_export_rig_type == "mped":
					action_prefix = "mp_"			
					
				if bpy.data.actions.get(action_prefix + action.name) != None:			
					bpy.data.actions.remove(bpy.data.actions[action_prefix + action.name], do_unlink = True)				
				
				try:
					baked_armature.animation_data.action.name = action_prefix + action.name
					baked_armature.animation_data.action.use_fake_user = True
				except:
					print("Error when assigning the action because it's used in the NLA. Remove it from the NLA to export.")
			
			
			
			i += 1
			
							
		"""
		print("\nRound keyframe rotation values")
		for action in actions:
			if action.name[:2] == "h_" or action.name[:2] == "mp_":
				for fcurve in action.fcurves:
					if 'rotation' in fcurve.data_path:						
						for point in fcurve.keyframe_points:
							point.co[1] = round(point.co[1], 2)	 
						
		"""
		
		print("Actions baked.")
		
		#unbind the rig
		_constraint_rig(True)
		
				
def _select_exportable(armature_name):

	arp_armature = bpy.data.objects[armature_name + "_arpexport"]
	
	if bpy.context.scene.arp_export_rig_type == "generic":		
	
		set_active_object(arp_armature.name)
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		
		# select meshes with ARP armature modifier
		for obj in bpy.data.objects:
			if obj.type == 'MESH' and "_arpexport" in obj.name:
				# objects parented to bones
				if obj.parent:					
					if obj.parent_type == "BONE" and obj.parent.name == arp_armature.name:
						set_active_object(obj.name)
						bpy.ops.object.mode_set(mode='OBJECT')			
						print("Collected mesh", obj.name)
						
				# objects with armature modifiers
				if len(obj.modifiers) > 0:
					for modif in obj.modifiers:
						if modif.type == 'ARMATURE':
							if modif.object != None:
								if modif.object == arp_armature:					  
									set_active_object(obj.name)
									bpy.ops.object.mode_set(mode='OBJECT')
				
		# select ARP armature
		set_active_object(arp_armature.name)
		
	if bpy.context.scene.arp_export_rig_type == "humanoid" or bpy.context.scene.arp_export_rig_type == "mped":
		
		baked_armature_name = ""
		
		if bpy.context.scene.arp_export_rig_type == "humanoid":
			baked_armature_name = "rig_humanoid"
		if bpy.context.scene.arp_export_rig_type == "mped":
			baked_armature_name = "rig_mped"
		
		set_active_object(arp_armature.name)
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')	
		
		# select meshes with Humanoid armature modifier
	
		for obj in bpy.data.objects:		
			if obj.type == 'MESH':
				print(obj.name)
				# objects parented to bones
				if obj.parent:
					if obj.parent_type == "BONE" and obj.parent.name == baked_armature_name:
						set_active_object(obj.name)
						bpy.ops.object.mode_set(mode='OBJECT')			
						print("Collected mesh", obj.name)
					
				# objects with armature modifiers
				if len(obj.modifiers) > 0:
					print(obj.name)
					for modif in obj.modifiers:
						if modif.type != 'ARMATURE':
							continue
						if modif.object:
							print(modif.object.name, obj.name)
							if modif.object.name == baked_armature_name:								   
								set_active_object(obj.name)
								bpy.ops.object.mode_set(mode='OBJECT')			
								print("Collected mesh", obj.name)
								
				
					
		#check if the meshes have shape keys and disable subsurf if any before export
		for obj in bpy.context.selected_objects:		
			if obj.type == 'MESH':
				if obj.data.shape_keys != None:					
					if len(obj.data.shape_keys.key_blocks) > 0:					
						if len(obj.modifiers) > 0:
							for modif in obj.modifiers:
								if modif.show_render:
									if modif.type == 'SUBSURF' or modif.type == 'SMOOTH' or modif.type == 'MASK' or modif.type == "MULTIRES":
										print(obj.name + " has shape keys, " + modif.type + " modifier won't be exported.")
										obj.modifiers.remove(modif)
					
		# select the export armature
		if bpy.data.objects.get(baked_armature_name) != None:
			bpy.data.objects[baked_armature_name].hide_viewport = False
			set_active_object(baked_armature_name) 
			
			
def get_char_objects(arm_name = None, arm_add_name = None, arm_proxy = None):		
	
	list_char_objects = [arm_name, arm_add_name]
	
	bpy.data.objects[arm_add_name].hide_viewport = False
	bpy.data.objects[arm_add_name].hide_select = False
	

	deforming_arm = arm_name
	
	if arm_proxy != None:
		deforming_arm = arm_proxy
	
	# Append meshes
	objs = []
	if bpy.context.scene.arp_ge_sel_only:
		objs = [obj for obj in bpy.context.selected_objects]
	else:
		objs = [obj for obj in bpy.data.objects]
	
	for obj in objs:
		if obj.type == 'MESH' and not obj.hide_viewport:			
			# obj parented to bone
			if obj.parent:
				if obj.parent.name == deforming_arm and obj.parent_type == "BONE":				
					if obj.parent_bone != "":
						list_char_objects.append(obj.name)	
						obj["arp_parent_bone"] = obj.parent_bone
		
			# obj with armature modifiers		
			if len(obj.modifiers) > 0:
				for mod in obj.modifiers:
					if mod.type == "ARMATURE" and mod.show_viewport:
						if mod.object != None:
							if mod.object.name == deforming_arm:
								list_char_objects.append(obj.name)						
								break
			
						
				
		
	#check if the meshes have shape keys and disable subsurf if any before export
	for obj_name in list_char_objects:
		obj = bpy.data.objects[obj_name]
		if obj.type == 'MESH':
			if obj.data.shape_keys != None:
				if len(obj.data.shape_keys.key_blocks) > 0:					
					if len(obj.modifiers) > 0:
						for modif in obj.modifiers:
							if modif.type == 'SUBSURF' or modif.type == "MULTIRES":
								modif.show_render = False
								print('\nMesh', obj.name, 'has shape keys, disable', modif.type,  'modifiers for export')

	
	# if the armature only is exported, add an extra dummy mesh to allow the armature's rest pose export and correct hierarchy in Unity
	add_dummy_mesh = True
	if add_dummy_mesh and len(list_char_objects) == 2:
		dum_ob = create_dummy_mesh()
		new_mod = dum_ob.modifiers.new(type="ARMATURE", name="rig")
		new_mod.object = bpy.data.objects[arm_name]
		list_char_objects.append(dum_ob.name)
		print("Created dummy mesh")
		
	return (list_char_objects)
	
	
def create_dummy_mesh():
	dummy_mesh = bpy.data.meshes.new("arp_dummy_mesh")
	dummy_object = bpy.data.objects.new("arp_dummy_mesh", dummy_mesh)
	bpy.context.scene.collection.objects.link(dummy_object)		  
	return(dummy_object)
	
def get_rig_add(rig):
	_rig_add_name = None	
	
	arm_parent = bpy.data.objects[rig].parent
	for child in arm_parent.children:
		if "rig_add" in child.name:	
			_rig_add_name = child.name
			break
	
	return _rig_add_name
			
def get_shape_keys_drivers(_obj):				
	try:
		sk_drivers = _obj.data.shape_keys.animation_data.drivers				
	except:
		return None	
		
	return sk_drivers
	
def _set_standard_scale(self):

	unit_system = bpy.context.scene.unit_settings
	current_frame = bpy.context.scene.frame_current#save current frame
	current_cursor_mode = bpy.context.scene.tool_settings.transform_pivot_point
	bpy.context.scene.tool_settings.use_keyframe_insert_auto = False
	
	if unit_system.system != 'None':
		if unit_system.scale_length > 0.01-0.0003 and unit_system.scale_length < 0.01+0.0003:
		
			
		
			humanoid_set = False			
			rig = bpy.data.objects['rig']
			
			rig_scale = rig.scale[0]
			
			if bpy.data.objects.get("rig_humanoid") != None:
				bpy.data.objects["rig_humanoid"].scale = rig.scale
				
				#disable Mannequin Axes if set
				if bpy.data.objects["rig_humanoid"].data.bones.get("thigh.l_basebone") != None:
					_unset_ue_orientations()
				
			#Get meshes
			meshes = []
			
				#Check if humanoid set
			for obj in bpy.data.objects:				
				if obj.type == 'MESH':
					if len(obj.modifiers) > 0:
						for mod in obj.modifiers:
							if mod.type == 'ARMATURE':
								if mod.object != None:
									if mod.object.name == 'rig_humanoid':
										humanoid_set = True
										meshes.append(obj)
				#If yes scale the humanoid armature		
			if humanoid_set:			
				bpy.data.objects['rig_humanoid'].scale *= 0.01
			else:
				#If not collect meshes
				for obj in bpy.data.objects:
					if not 'rig_ui' in obj.name:
						if obj.type == 'MESH':
							if len(obj.modifiers) > 0:
								for mod in obj.modifiers:
									if mod.type == 'ARMATURE':
										if mod.object == rig:
											meshes.append(obj)
				   
	
			if len(meshes) > 0:
			
				rig_add = bpy.data.objects['rig_add']
				rig_add.hide_viewport = False
			
				#update driver scale
				for mesh in meshes:
					has_sk_drivers = False
					
					try:
						drivers_list = mesh.data.shape_keys.animation_data.drivers
						has_sk_drivers = True
					except:
						pass			 
						
					if has_sk_drivers:
						for dr in drivers_list:
							try:
								if dr.driver.expression[-6:] == ')*0.01':
									dr.driver.expression = dr.driver.expression[:-6] + ')*1.0'									  
								else:
									dr.driver.expression = '(' + dr.driver.expression + ')*1.0'
							except:#no expression
								pass
								
				#Key controllers if necessary
				set_active_object(rig.name)
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.select_all(action='DESELECT')
				set_active_object(rig.name)
				bpy.ops.object.mode_set(mode='POSE')
				#Check if an action is linked			
				
				_action = bpy.context.active_object.animation_data.action
			

				if bpy.context.active_object.animation_data.action == None:
					_action = bpy.context.blend_data.actions.new('Action') 
					bpy.context.active_object.animation_data.action = _action
					
				bpy.ops.pose.select_all(action='DESELECT')

				#Check if the controller is keyed
				for pbone in bpy.context.active_object.pose.bones:
					if pbone.name[:2] == 'c_' and not is_proxy_bone(pbone):
						keyed = False
						for fcurve in _action.fcurves:			
							if pbone.name in fcurve.data_path:
								keyed = True
						if not keyed: 
							bpy.context.active_object.data.bones.active = pbone.bone

				#Key  if necessary 
				try:
					bpy.ops.anim.keyframe_insert_menu(type='LocRotScale')
				except:
					pass
								
				#Scale the Transformation constraints
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.select_all(action='DESELECT')
				set_active_object(rig.name)
				bpy.ops.object.mode_set(mode='POSE')
					
				for pbone in bpy.context.active_object.pose.bones:
					if len(pbone.constraints) > 0:
						for cns in pbone.constraints:
							if cns.type == 'TRANSFORM':
							
								cns.from_min_x *= 0.01
								cns.from_max_x *= 0.01
								cns.from_min_y *= 0.01
								cns.from_max_y *= 0.01
								cns.from_min_z *= 0.01
								cns.from_max_z *= 0.01
				
				bpy.ops.object.mode_set(mode='OBJECT')	
		
				#scale x0.01
					#set rig_add scale as rig scale
				rig_add.scale = rig.scale
				
				bpy.context.scene.cursor.location = [0,0,0]
				bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
				
				for mesh in meshes:				   
					set_active_object(mesh.name)
					
				set_active_object(rig.name)
				set_active_object(rig_add.name)
				bpy.ops.transform.resize(value=(0.01, 0.01, 0.01), constraint_axis=(False, False, False), orient_type='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
								
				#apply scale			
				bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
			 
				bpy.ops.object.select_all(action='DESELECT')
				set_active_object(rig.name)
				
				
				bpy.ops.object.mode_set(mode='POSE')
				
					#Active all layers
					#save current displayed layers
				_layers = bpy.context.active_object.data.layers
				
				for i in range(0,32):
					bpy.context.active_object.data.layers[i] = True
					
				#reset child of constraints				   
				for pbone in bpy.context.active_object.pose.bones:
					if 'hand' in pbone.name or 'foot' in pbone.name:
						for cns in pbone.constraints:
							if 'Child Of' in cns.name:
								set_inverse_child(pbone.name, cns.name)				
				
								
				#scale curves			   
				for action in bpy.data.actions:
					for fcurve in action.fcurves:
						if 'location' in fcurve.data_path:
							for point in fcurve.keyframe_points:					
								point.co[1] *= 0.01*rig_scale
								point.handle_left[1] *= 0.01*rig_scale
								point.handle_right[1] *= 0.01*rig_scale
				
				#display layers 16, 0, 1 only	
				_layers = bpy.context.active_object.data.layers
					#must enabling one before disabling others
				_layers[16] = True	
				for i in range(0,32):
					if i != 16:
						_layers[i] = False 
				_layers[0] = True
				_layers[1] = True	
				
	 
				bpy.ops.object.mode_set(mode='OBJECT')	
			
				
				#unit system			   
				bpy.context.scene.unit_settings.scale_length = 1.0
				
				if humanoid_set:
					set_active_object('rig_humanoid')
					bpy.ops.object.mode_set(mode='OBJECT')	
					bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
			
				#set the camera clip
				bpy.context.space_data.clip_end *= 0.01
				
				#restore cursor pivot_point
				bpy.context.scene.tool_settings.transform_pivot_point = current_cursor_mode
								
				
				#refresh
				bpy.context.scene.frame_current = current_frame
				bpy.context.scene.frame_set(bpy.context.scene.frame_current)#debug	 
				
				#RESET STRETCHES
				set_active_object(rig.name)
					#store active pose			
				bpy.ops.object.mode_set(mode='POSE')
				bpy.ops.pose.select_all(action='SELECT')
				bpy.ops.pose.copy()
					#need to reset the pose
				auto_rig_reset.reset_all()
					#reset stretches
				for pbone in bpy.context.active_object.pose.bones:
					try:							
						pbone.constraints["Stretch To"].rest_length = 0.0					
					except:
						pass
					
					#restore the pose
				bpy.ops.pose.paste(flipped=False)
				
				#center view
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.select_all(action='DESELECT')
				for mesh in meshes:
					set_active_object(mesh.name)		
				bpy.ops.view3d.view_selected(use_all_regions=False)
				
				#UI Cam scale
				bpy.data.objects['cam_ui'].data.ortho_scale *= 0.01
			   
				rig_add.hide_viewport = True
				
				print('Done	setting standard units.')
	
			else:
				self.report({'ERROR'}, "No skinned mesh found, units haven't been changed.")
		else:
			self.report({'ERROR'}, "Blender units already set.")
			
			
def _set_units_x100_baked(armature_name):
	
	scn = bpy.context.scene
	unit_system = scn.unit_settings
	scn.tool_settings.use_keyframe_insert_auto = False
	current_frame = scn.frame_current#save current frame
	
	if unit_system.system == 'NONE' or (unit_system.system != 'NONE' and (unit_system.scale_length > 1.0-0.0003 and unit_system.scale_length < 1.0+0.0003)):
		print("..............................Set Units x100 (baked)..............................")
		
		rig = bpy.data.objects[armature_name + '_arpexport']		
		rig_scale = rig.scale[0]		
		baked_armature_name = ""
		
		if scn.arp_export_rig_type == "humanoid":
			baked_armature_name = "rig_humanoid"
		if scn.arp_export_rig_type == "mped":
			baked_armature_name = "rig_mped"
			
		#Collect meshes
		meshes = []		
		
		for obj in bpy.data.objects:				
			if obj.type == 'MESH' and not obj.hide_viewport:
				if len(obj.modifiers) > 0:
					for mod in obj.modifiers:
						if mod.type == 'ARMATURE':
							if mod.object != None:
								if mod.object.name == baked_armature_name:								
									meshes.append(obj)								
	
		
		bpy.ops.object.mode_set(mode='OBJECT')
		
		
		for mesh in meshes:
			
			bpy.ops.object.select_all(action='DESELECT')

			# Unlock scale transform
			set_active_object(mesh.name)
			
			for i in range(0,3):
				mesh.lock_scale[i] = False
			
			# Apply Data Transfer modifier if any
			if len(bpy.context.active_object.modifiers) > 0:
				for mod in bpy.context.active_object.modifiers:
					if mod.type == "DATA_TRANSFER":
						bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
						
			
			
			# Scale shape keys drivers
			has_sk_drivers = False
			
			try:
				drivers_list = mesh.data.shape_keys.animation_data.drivers
				has_sk_drivers = True
			except:
				pass			 
				
			if scn.arp_push_drivers:
				if has_sk_drivers:
					for dr in drivers_list:
						try:
							if dr.driver.expression[-5:] == ')*1.0':
								dr.driver.expression = dr.driver.expression[:-5] + ')*0.01'									   
							else:
								dr.driver.expression = '(' + dr.driver.expression + ')*0.01'
						except:#no expression
							pass
								
		if 'mesh' in locals():
			del mesh
			
		# Scale transforms x100		
		bpy.ops.object.select_all(action='DESELECT')						
		
		set_active_object(baked_armature_name)
		set_active_object(rig.name)	

			# first make sure to delete scale keyframe on the baked armature
		for action in bpy.data.actions:		
			if action.name[:2] == "h_" or action.name[:3] == "mp_":
				for _fcurve in action.fcurves:
					if _fcurve.data_path == "scale":					
						action.fcurves.remove(_fcurve)
		
		# trigger the update manually, does not update automatically
		if bpy.data.objects[baked_armature_name].animation_data:
			current_action = bpy.data.objects[baked_armature_name].animation_data.action
			if current_action:
				current_action_name = current_action.name
				bpy.data.objects[baked_armature_name].animation_data.action = None
				bpy.context.scene.update()
				bpy.data.objects[baked_armature_name].animation_data.action = bpy.data.actions[current_action_name]
		
			# scale them
		for _obj in bpy.context.selected_objects:
			print("set scale", _obj.name, _obj.scale)
			_obj.location *= 100
			_obj.scale *= 100
			print("new scale", _obj.name, _obj.scale)
			# multiply the Merge Limit of the mirror modifier if any
			if len(_obj.modifiers) > 0:
				for mod in _obj.modifiers:
					if mod.type == "MIRROR":
						mod.merge_threshold *= 100
		
		unparented_meshes = []
		bpy.context.scene.update()
		
		# unparent mesh children
		for mesh in meshes:
			if mesh.parent == rig:			
				unparented_meshes.append(mesh.name)				
				mesh_mat = mesh.matrix_world.copy()				
				mesh.parent = None				
				bpy.context.scene.update()
				mesh.matrix_world = mesh_mat				
		
		# Apply scale			
		bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
		bpy.context.scene.update()
		
		# reparent mesh children
		for meshname in unparented_meshes:
			mesh = bpy.data.objects[meshname]
			mesh_mat = mesh.matrix_world.copy()
			bpy.data.objects[meshname].parent = rig
			bpy.context.scene.update()
			mesh.matrix_world = mesh_mat
				
		
		# initialize meshes scale too		
		for mesh in meshes:
			#mesh.scale *= 100
			set_active_object(mesh.name)
		
		bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)		
		
		# Scale anim location curves x100		 
		for action in bpy.data.actions:
			for fcurve in action.fcurves:
				if 'location' in fcurve.data_path:
					for point in fcurve.keyframe_points:					
						point.co[1] *= 100*rig_scale
						point.handle_left[1] *= 100*rig_scale
						point.handle_right[1] *= 100*rig_scale
						
		
		
		bpy.ops.object.mode_set(mode='OBJECT') 
		
		# Change units system
		scn.unit_settings.system = 'METRIC'
		scn.unit_settings.scale_length = 0.01			
					
		
		# Refresh
		scn.frame_current = current_frame
		scn.frame_set(scn.frame_current)#debug												
				
		
		print('x100 Units (baked) set successfully.')

					
	
	
			
def _set_units_x100_generic(armature_name, armature_add_name):

	scn = bpy.context.scene
	
	current_frame = scn.frame_current#save current frame
	unit_system = scn.unit_settings
	current_cursor_mode = bpy.context.scene.tool_settings.transform_pivot_point
	scn.tool_settings.use_keyframe_insert_auto = False

	if unit_system.system == 'NONE' or (unit_system.system != 'NONE' and (unit_system.scale_length > 1.0-0.0003 and unit_system.scale_length < 1.0+0.0003)):
	   
		print("..............................Set Units x100..............................")
		baked_armature_set = False
		
		rig = bpy.data.objects[armature_name + '_arpexport']		
		rig_scale = rig.scale[0]		
		
		#Get meshes
		meshes = []		
		
		for obj in bpy.data.objects:
			if not 'rig_ui' in obj.name and not obj.hide_viewport:
				if obj.type == 'MESH':
					if len(obj.modifiers) > 0:
						for mod in obj.modifiers:
							if mod.type == 'ARMATURE':
								if mod.object == rig:
									meshes.append(obj)

									
		#Start changing units
		if len(meshes) > 0:		
			rig_add = bpy.data.objects[armature_add_name + '_arpexport']
			rig_add.hide_viewport = False
			
			for mesh in meshes: 
				#Unlock scale check
				set_active_object(mesh.name)
				
				for i in range(0,3):
					mesh.lock_scale[i] = False
				
				#update driver scale
				has_sk_drivers = False
				
				try:
					drivers_list = mesh.data.shape_keys.animation_data.drivers
					has_sk_drivers = True
				except:
					pass			 
					
				if scn.arp_push_drivers:
					if has_sk_drivers:
						for dr in drivers_list:
							try:
								if dr.driver.expression[-5:] == ')*1.0':
									dr.driver.expression = dr.driver.expression[:-5] + ')*0.01'									   
								else:
									dr.driver.expression = '(' + dr.driver.expression + ')*0.01'
							except:#no expression
								pass
							
							
			#Key controllers if necessary
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.select_all(action='DESELECT')
			set_active_object(rig.name)
			bpy.ops.object.mode_set(mode='POSE')
			
			# Unprotect layers of proxy
			for i in range(0,32):
				bpy.context.active_object.data.layers_protected[i] = False
			
					
			
			#Scale the Transformation constraints
			for pbone in bpy.context.active_object.pose.bones:
				if len(pbone.constraints) > 0:
					for cns in pbone.constraints:
						if cns.type == 'TRANSFORM':
						
							cns.from_min_x *= 100*bpy.context.active_object.scale[0]
							cns.from_max_x *= 100*bpy.context.active_object.scale[0]
							cns.from_min_y *= 100*bpy.context.active_object.scale[0]
							cns.from_max_y *= 100*bpy.context.active_object.scale[0]
							cns.from_min_z *= 100*bpy.context.active_object.scale[0]
							cns.from_max_z *= 100*bpy.context.active_object.scale[0]
				
		
			
			bpy.ops.object.mode_set(mode='OBJECT')
			
			#Scale meshes and armatures
			for mesh in meshes:
				mesh.scale *= 100
				mesh.location *= 100
				
			rig_add.scale = rig.scale
			
			bpy.context.scene.cursor.location = [0,0,0]
			bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'		
			
			set_active_object(rig.name)			
			set_active_object(rig_add.name)			
			
			# -> Manual scaling from world center
			for obj in bpy.context.selected_objects:
				obj.location = obj.location * 100
				obj.scale = obj.scale * 100
				
				# multiply the Merge Limit of the mirror modifier if any
				if len(obj.modifiers) > 0:
					for mod in obj.modifiers:
						if mod.type == "MIRROR":
							mod.merge_threshold *= 100
							
			
			#apply scale	
			
			bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
			
			
			bpy.ops.object.select_all(action='DESELECT')
			set_active_object(rig.name)			
			
			bpy.ops.object.mode_set(mode='POSE')
		
						
				#Active all layers
				#save current displayed layers
			_layers = bpy.context.active_object.data.layers
			
			for i in range(0,32):
				bpy.context.active_object.data.layers[i] = True
			
			#scale curves			 
			for action in bpy.data.actions:
				for fcurve in action.fcurves:
					if 'location' in fcurve.data_path:
						for point in fcurve.keyframe_points:					
							point.co[1] *= 100*rig_scale
							point.handle_left[1] *= 100*rig_scale
							point.handle_right[1] *= 100*rig_scale
							
			# scale bones location if not keyframed
			for pbone in bpy.context.active_object.pose.bones:
				if pbone.name[:2] == "c_" or pbone.name[:2] == "cc_":
					pbone.location *= 100
			
			
			# Reset child of constraints
			for pbone in bpy.context.active_object.pose.bones:
				if 'hand' in pbone.name or 'foot' in pbone.name:
					for cns in pbone.constraints:						
						if 'Child Of' in cns.name:
							set_inverse_child(pbone.name, cns.name)
							print("set inverse", pbone.name, cns.name)											
			
						
			#display layers 16, 0, 1 only	
			_layers = bpy.context.active_object.data.layers
				#must enabling one before disabling others
			_layers[16] = True	
			for i in range(0,32):
				if i != 16:
					_layers[i] = False 
					
			_layers[0] = True
			_layers[1] = True	
			
			bpy.ops.object.mode_set(mode='OBJECT') 
			
			#unit system
			scn.unit_settings.system = 'METRIC'
			scn.unit_settings.scale_length = 0.01			
									
			
						
			#restore cursor pivot_point
			bpy.context.scene.tool_settings.transform_pivot_point = current_cursor_mode
			
			#refresh
			scn.frame_current = current_frame
			scn.frame_set(scn.frame_current)#debug	 
			
			#RESET STRETCHES -- WARNING only works at the end of the process??
			set_active_object(rig.name)
				#store active pose			
			bpy.ops.object.mode_set(mode='POSE')
			bpy.ops.pose.select_all(action='SELECT')
			bpy.ops.pose.copy()
				#need to reset the pose
			auto_rig_reset.reset_all()
				#reset stretches
			for pbone in bpy.context.active_object.pose.bones:
				try:							
					pbone.constraints["Stretch To"].rest_length = 0.0					
				except:
					pass
					
				#restore the pose
			bpy.ops.pose.paste(flipped=False)
		
			bpy.ops.object.mode_set(mode='OBJECT')
		
			
			rig_add.hide_viewport = True
			
			print('UE Units set successfully.')

		else:
			print("No skinned mesh found, units haven't been changed.")
		
	else:
		print("UE Units already set, no changes.")
		

def _setup_generic(armature_name, armature_add_name):

	print("\nSetup Generic Rig...")
	
	scn = bpy.context.scene
	
	arp_armature = bpy.data.objects[armature_name + '_arpexport']	
	
	# move cs_grp collection
	cs_collec = None
	for col in bpy.data.collections:
		if len(col.objects) > 0:
			for obj in col.objects:
				if obj.name[:3] == "cs_":
					cs_collec = col
					break
	
	cs_grp = bpy.data.objects["cs_grp"]
	if cs_collec:
		try:		
			for c in cs_grp.users_collection:
				c.objects.unlink(cs_grp)			
			cs_collec.objects.link(cs_grp)			
		except:
			pass	
	
	set_active_object(arp_armature.name)
	bpy.ops.object.mode_set(mode='EDIT')
	
	if scn.arp_fix_fbx_rot:
		fix_fbx_bones_rot()
	
	bpy.ops.object.mode_set(mode='OBJECT')
	
	clamp_dict = {'c_thigh_bend_contact': 'thigh_twist', 'c_thigh_bend_01': 'thigh_twist', 'c_thigh_bend_02': 'thigh_twist', 'c_knee_bend': 'leg_stretch', 'c_ankle_bend': 'leg_stretch', 'c_leg_bend_01': 'leg_stretch', 'c_leg_bend_02': 'leg_stretch','c_elbow_bend': 'arm_stretch', 'c_shoulder_bend': 'arm_stretch', 'c_wrist_bend': 'forearm_twist'}
	
	def clamp_weights(object=None, vertice=None, vertex_weight=None, group_name=None, dict=None):
	
		grp_name_base = group_name[:-2]	
		side = group_name[-2:]	
		
		if "_dupli_" in group_name:
			grp_name_base = group_name[:-12]
			side = "_" + group_name[-11:]				
		
		if grp_name_base in dict:													
			if dict[grp_name_base][-2:] == '.x':
				side = ''
				
			_target_group = dict[grp_name_base]+side						
			
			if object.vertex_groups.get(_target_group) != None:#if target group exists
				
				target_weight = 0.0
				
				for grp in vertice.groups:					
			
					#if obj.vertex_groups[grp.group] != None:						
					if obj.vertex_groups[grp.group].name == _target_group:
						target_weight = grp.weight				
				
				def_weight = min(vertex_weight, target_weight)
				object.vertex_groups[group_name].add([vertice.index], def_weight, 'REPLACE') 
				
	# Iterate over meshes linked to the armature
	collected_meshes = []
	
	for obj in bpy.data.objects:		
		if obj.type == 'MESH' and "_arpexport" in obj.name:	
			collected_meshes.append(obj.name)
			
			if len(obj.modifiers) > 0:
				for modif in obj.modifiers:					
					if modif.type == 'ARMATURE':
						
						if modif.object != None:
						
							#delete rig_add modifier
							if modif.object.name == armature_add_name:
								obj.modifiers.remove(modif)
					
							# Vertex groups
							if modif.object.name == arp_armature.name:
								
								set_active_object(obj.name)								
									
								for vert in obj.data.vertices:									
									if len(vert.groups) > 0:
										for grp in vert.groups:
											
											try:
												grp_name = obj.vertex_groups[grp.group].name
											except:											
												continue
											weight = grp.weight					
											
											if	scn.arp_keep_bend_bones:					
												# Clamp weights (make sure c_thigh_bend_contact influence is contained inside thigh_twist for better deformations)										
												clamp_weights(object=obj, vertice=vert, vertex_weight=weight, group_name=grp_name, dict=clamp_dict)
		
		
	
	# Change the shape keys drivers from rig to rig_arpexport
	for mesh in collected_meshes:
	
		obj = bpy.data.objects[mesh]
		drivers_list = get_shape_keys_drivers(obj)		
			
		if drivers_list != None:
			print(obj.name, "has shape keys drivers")
			for dr in drivers_list:
				for var in dr.driver.variables:				
					if var.targets[0].id_type == 'OBJECT' or var.type == "TRANSFORM":
						if var.targets[0].id.name == armature_name:
							var.targets[0].id = arp_armature
						
						
	# Assign parent bones of objects that are directly parented to bones (humanoid)
	"""
	for mesh in collected_meshes:	
		obj = bpy.data.objects[mesh]
		if len(obj.keys()) > 0:
			if "arp_parent_bone" in obj.keys():
				b_parent = obj["arp_parent_bone"]				
					
				obj_matrix = obj.matrix_world.copy()
				#obj.parent = bpy.data.objects["rig_humanoid"]
				obj.parent_bone = b_parent
				obj.matrix_world = obj_matrix
						
	"""
	
	sides = ['.l', '.r']
	
	#Keep bend bones?
	if scn.arp_keep_bend_bones:
		for bone in bend_bones:
			if bone[-2:] != '.x':
				for side in sides:
					bend_bone = arp_armature.data.bones.get(bone+side)
					if bend_bone:
						bend_bone.use_deform = True		
			else:
				bend_bone = arp_armature.data.bones.get(bone)
				if bend_bone:					
					bend_bone.use_deform = True	

		

		#push up the bend bones?
		if scn.arp_push_bend:
			for _action in bpy.data.actions:
				_push_bend_bones(_action, 2)			
							
		
	print("	   Done.")
	
	
######### FOR RETRO COMPATIBILITY ONLY !#########
def _unset_humanoid_rig(self, context):

	scene = context.scene	
	
	
	if bpy.data.objects.get('rig_humanoid') != None:
	
		humanoid_armature = bpy.data.objects['rig_humanoid']
		
		#disable Mannequin Axes if set
		if humanoid_armature.data.bones.get("thigh.l_basebone") != None:
			_unset_ue_orientations()
		
		if humanoid_armature.data.bones.get("pelvis") != None:		
			revert_rename_for_ue()
			print("Reverted UE names")
		
		#set surface subdivision to 0 to speed up
		simplify = bpy.context.scene.render.use_simplify #save
		simplify_value = bpy.context.scene.render.simplify_subdivision
		bpy.context.scene.render.use_simplify = True #set
		bpy.context.scene.render.simplify_subdivision = 0
		
		#get the armatures	 
		bpy.ops.object.mode_set(mode='OBJECT') 

		
		arp_armature = bpy.data.objects['rig']		
		 
		set_active_object(arp_armature.name)
		bpy.ops.object.mode_set(mode='POSE') 
		
		#unlock the root translation
		for i in range(0,3):
			get_pose_bone("c_root.x").lock_location[i] = False
			
		bpy.ops.object.mode_set(mode='OBJECT') 
		hide_state = humanoid_armature.hide_viewport
		humanoid_armature.hide_viewport = False

		# set the ARP armature as the deforming one
		
		#Check for deprecated groups names
		deprecated_groups_list = ["c_pinky1", "c_ring1", "c_middle1", "c_index1", "c_thumb1"]	
		found_new_finger_bone = False
		
		for bone in arp_armature.data.bones:
			if bone.name == "index1.l":
				found_new_finger_bone = True
				print("Found new finger bone")
				break	
								
								
		
		for obj in bpy.data.objects:
			if obj.type == 'MESH':	 
			
				found_rig_add = False
				found_rig = False
				
				for modif in obj.modifiers:
					if modif.type == 'ARMATURE':
						if modif.object == humanoid_armature: 
							found_rig = True
							modif.object = arp_armature
							modif.use_deform_preserve_volume = True
						if modif.object == bpy.data.objects["rig_add"]:
							found_rig_add = True
							
				if not found_rig_add and found_rig:
					#add the rig_add modifier					 
					new_mod = obj.modifiers.new("rig_add", 'ARMATURE')
					new_mod.object = bpy.data.objects["rig_add"]				
					#re order
					bpy.ops.object.mode_set(mode='OBJECT')
					bpy.ops.object.select_all(action='DESELECT')
					set_active_object(obj.name)
					for i in range(0,20):
						bpy.ops.object.modifier_move_up(modifier="rig")
					for i in range(0,20):
						bpy.ops.object.modifier_move_up(modifier="rig_add")
					#put mirror at first
					for m in bpy.context.active_object.modifiers:
						if m.type == 'MIRROR':
							for i in range(0,20):
								bpy.ops.object.modifier_move_up(modifier=m.name)
				
				#change deprecated vertex groups
				if found_new_finger_bone:			
					if len(obj.vertex_groups) > 0:
						for vgroup in obj.vertex_groups:	
							for name in deprecated_groups_list:
								if name in vgroup.name and not "base" in vgroup.name:				
									vgroup.name = vgroup.name[2:]
									print("Replaced vertex group:", vgroup.name)
							#rename arm twist vgroup
							if "arm_twist" in vgroup.name and not "forearm" in vgroup.name:
								vgroup.name = vgroup.name.replace("arm_twist", "c_arm_twist_offset")
								
				

		
		#Delete the humanoid
		bpy.ops.object.mode_set(mode='OBJECT') 
		bpy.ops.object.select_all(action='DESELECT')
		set_active_object(humanoid_armature.name)
		bpy.ops.object.mode_set(mode='OBJECT') 
		bpy.ops.object.delete()
		
		#Push the bend bones transform *0.5 
		if scene.arp_keep_bend_bones and scene.push_bend:
		
			_action = arp_armature.animation_data.action
			if _action != None:
				for fcurve in _action.fcurves:	   
					for bbone in bend_bones_add:
						if bbone in fcurve.data_path:#operate only on bend bone add fcurves					
							for key in fcurve.keyframe_points:
								if not 'scale' in fcurve.data_path:
									key.co[1] *= 0.5
									key.handle_right[1] *= 0.5
									key.handle_left[1] *= 0.5
									
								else:
									key.co[1] = (key.co[1] + 1) * 0.5
									key.handle_right[1] = (key.handle_right[1] + 1) * 0.5
									key.handle_left[1] = (key.handle_left[1] + 1) * 0.5
							break
						
		#restore simplification
		bpy.context.scene.render.use_simplify = simplify
		bpy.context.scene.render.simplify_subdivision = simplify_value
	
	else:
		print("rig_humanoid not found.")
		
		
		
	
def _set_humanoid_rig(armature_name, armature_add_name):

	print("\n..............................Building humanoid rig..............................")
	scn = bpy.context.scene
	sides = ['.l', '.r']
	
	# get skinned meshes
	collected_meshes = []
	for obj in bpy.data.objects:		
		if obj.type == 'MESH' and "_arpexport" in obj.name:	
			collected_meshes.append(obj.name)
	
	bpy.ops.object.mode_set(mode='OBJECT')	
	arp_armature = bpy.data.objects[armature_name + '_arpexport']	
		
	# append the humanoid armature	
	addon_directory = os.path.dirname(os.path.abspath(__file__))
	filepath = addon_directory + "/humanoid.blend"
	
	# load the objects data in the file
	with bpy.data.libraries.load(filepath) as (data_from, data_to):
		data_to.objects = data_from.objects
	
	# add the objects in the scene
	for obj in data_to.objects:
		if obj is not None:
			scn.collection.objects.link(obj)

	
	humanoid_armature = bpy.data.objects['rig_humanoid']
	humanoid_armature.location = arp_armature.location
	
	# if root motion, the armature object is constrained to the c_traj controller
	if scn.arp_ue_root_motion:		
		cns = humanoid_armature.constraints.new("CHILD_OF")
		cns.target = arp_armature
		cns.subtarget = "c_traj"
		
		arp_armature.data.pose_position = 'REST'	
		bpy.context.scene.update()
		cns.inverse_matrix = arp_armature.pose.bones["c_traj"].matrix.inverted()		
		arp_armature.data.pose_position = 'POSE'
		bpy.context.scene.update()
		
	else:
		# otherwise constrained to the source armature object
		cns = humanoid_armature.constraints.new("COPY_TRANSFORMS")
		cns.target = arp_armature
	
	
	print("	   Humanoid loaded. Setting up...")
	
	# Set the scale	  
	humanoid_armature.scale = arp_armature.scale
	set_active_object(humanoid_armature.name)
	
	hide_state = humanoid_armature.hide_viewport
	humanoid_armature.hide_viewport = False	
	
	# Setup spine bones amount

		# 4 spine bones
	if arp_armature.rig_spine_count == 4:
		set_active_object("rig_humanoid")
		bpy.ops.object.mode_set(mode='EDIT')
		if get_edit_bone('spine_03.x') == None:
			bpy.ops.armature.select_all(action='DESELECT')
			bpy.context.active_object.data.edit_bones.active = get_edit_bone('spine_02.x')
			bpy.ops.armature.subdivide()
			get_edit_bone('spine_02.x.001').name = 'spine_03.x'
			bpy.ops.object.mode_set(mode='POSE')
			bpy.ops.pose.select_all(action='DESELECT')
			get_pose_bone('spine_03.x').bone.select = True
			get_pose_bone('spine_02.x').bone.select = True			 
			#copy constraints
			bpy.ops.pose.constraints_copy()

			get_pose_bone('spine_03.x').constraints[0].subtarget = 'c_spine_03.x'
	
	
		# 3 spines
	if arp_armature.rig_spine_count == 3:
		set_active_object("rig_humanoid")
		bpy.ops.object.mode_set(mode='EDIT')
		if get_edit_bone('spine_03.x') != None:
			bpy.ops.armature.select_all(action='DESELECT')			 
			bpy.context.active_object.data.edit_bones.active = get_edit_bone('spine_03.x')
			bpy.ops.armature.delete()
			get_edit_bone('spine_02.x').tail = get_edit_bone('neck.x').head 

	bpy.ops.object.mode_set(mode='EDIT')  
	
	
	
	#Disable X Mirror
	bpy.context.active_object.data.use_mirror_x = False
	
	#Clear additional bones before creating them
	for edit_bone in bpy.context.active_object.data.edit_bones:
		if edit_bone.name[:3] == 'cc_' or is_bend_bone(edit_bone.name) or edit_bone.name[:-2] in additional_facial_bones:
			 bpy.context.active_object.data.edit_bones.remove(edit_bone)	
		 
	#Delete default facial if not set	
	if not is_facial_enabled(arp_armature):		
		for bone in default_facial_bones:
			if bone[-2:] != '.x':
				for side in sides:
					b = get_edit_bone(bone+side)
					if b:
						bpy.context.active_object.data.edit_bones.remove(b)	
			else:
				bone_name = bone
				
				# exception
				if bone == "jawbone.x":
					bone_name = "c_jawbone.x"
					
				bpy.context.active_object.data.edit_bones.remove(bpy.context.active_object.data.edit_bones[bone_name])	
					
				
	
	
	bpy.ops.object.mode_set(mode='POSE')  
	bpy.ops.pose.select_all(action='SELECT')
	selected_bones = bpy.context.selected_pose_bones
	
	#Create bones transform dict: name, head, tail, roll, use_deform
	bones_dict = {} 
	
	for pbone in selected_bones:		
		bpy.context.active_object.data.bones.active= pbone.bone	 
		
		#enable constraints
		for cns in pbone.constraints:		
			cns.target = bpy.data.objects[arp_armature.name]
			
			#store in dict
			if cns.name == 'Copy Transforms':
				_subtarget = pbone.name
				
				if pbone.name == "c_jawbone.x":
					_subtarget = "jawbone.x"
					
				if pbone.name == "eyelid_top.l" or pbone.name == "eyelid_bot.l" or pbone.name == "eyelid_top.r" or pbone.name == "eyelid_bot.r":
					_subtarget = pbone.name.replace("c_", "")
					
				bones_dict[pbone.name] = (pbone.name, [0.0,0.0,0.0], [0.0,0.0,0.0], 0.0, True)
				cns.subtarget = _subtarget	
	
	# Select the arp armature
	bpy.ops.object.mode_set(mode='OBJECT')
	set_active_object(arp_armature.name)
	
	
	# Define Humanoid rest pose from ARP armature	
	bpy.ops.object.mode_set(mode='POSE')
	
		#lock the root translation because no stretch allowed for Humanoid
	for i in range(0,3):
		get_pose_bone("c_root.x").lock_location[i] = True
		
	
	# change secondary arms/legs parent if necessary
	bpy.ops.object.mode_set(mode='EDIT')
	for edit_bone in arp_armature.data.edit_bones:
		bone = edit_bone.name
		if scn.arp_keep_bend_bones:		
		
			if not is_proxy_bone(edit_bone):
			
				if 'thigh_bend_contact' in bone or 'thigh_bend_01' in bone:
					new_parent = 'thigh_twist' + bone[-2:]								
					edit_bone.parent = arp_armature.data.edit_bones[new_parent]
					
				if 'ankle_bend' in bone:
					new_parent = 'leg_twist' + bone[-2:]				
					edit_bone.parent = arp_armature.data.edit_bones[new_parent]
				if 'shoulder_bend' in bone:
					new_parent = 'arm_twist' + bone[-2:]				
					edit_bone.parent = arp_armature.data.edit_bones[new_parent]
				if 'wrist_bend' in bone:
					new_parent = 'forearm_twist' + bone[-2:]				
					edit_bone.parent = arp_armature.data.edit_bones[new_parent]
		 
	
	
	# Store in dict
	
	# Additional humanoid bones		
	for edit_bone in arp_armature.data.edit_bones:
	
		# custom bones?
		if edit_bone.name[:3] == 'cc_':
			bones_dict[edit_bone.name] = (edit_bone.name, edit_bone.head.copy(), edit_bone.tail.copy(), edit_bone.roll, True)
			if scn.arp_debug_mode:
				print("storing custom bone:", edit_bone.name)
			
		# bend bones?
		if scn.arp_keep_bend_bones:
			if is_bend_bone(edit_bone.name) and not is_proxy_bone(edit_bone):
				if not bpy.context.active_object.data.bones[edit_bone.name].layers[22]:#check for disabled limb				
					bones_dict[edit_bone.name] = (edit_bone.name, edit_bone.head.copy(), edit_bone.tail.copy(), edit_bone.roll, True)				
			
				
		# facial?
			# build ears list
		for dupli in limb_sides.ear_sides:			
			ears_list = []
			
			for ear_id in range(0,17):	
				c_bone = get_edit_bone('c_ear_' + '%02d' % ear_id + dupli)
				if c_bone:
					if is_deforming(c_bone.name) and not c_bone.name[:-2] in additional_facial_bones:
						additional_facial_bones.append(c_bone.name[:-2])
						print("Added ear", c_bone.name[:-2])

			# get additional facial bones
		if scn.arp_full_facial and is_facial_enabled(arp_armature):			
			if edit_bone.name[:-2] in additional_facial_bones:				
				bones_dict[edit_bone.name] = (edit_bone.name, edit_bone.head.copy(), edit_bone.tail.copy(), edit_bone.roll, True)
				
			
		# toes?
		if 'c_toes_' in edit_bone.name:
			if edit_bone.use_deform:
				bones_dict[edit_bone.name] = (edit_bone.name, edit_bone.head.copy(), edit_bone.tail.copy(), edit_bone.roll, True)
	
		# tail?
		if edit_bone.name[:-4] == "c_tail_" and edit_bone.name[-2:] == ".x":
			if edit_bone.use_deform:
				bones_dict[edit_bone.name] = (edit_bone.name, edit_bone.head.copy(), edit_bone.tail.copy(), edit_bone.roll, True)
	
	eyelids = ['eyelid_bot.l', 'eyelid_bot.r', 'eyelid_top.l', 'eyelid_top.r']		
	
	#Main bones
	for key, value in bones_dict.items():
		if key[:3] != 'cc_' and not is_bend_bone(key):#every bones except cc, bend
			
			_bone = value[0]
				
			if _bone in eyelids:
				_bone = 'c_' + _bone
				
			edit_bone = arp_armature.data.edit_bones.get(_bone)
			if edit_bone == None:# the bone, such as fingers, is disabled. Then store it with null values
				bones_dict[key] = (value[0], (0,0,0), (0,0,0), 0, False)
				continue
				
			side = value[0][-2:]
			#Check for deform - Disabled limbs
			if 'spine' in _bone or 'root' in _bone:# or 'shoulder' in value[0]:#these bones can't be disabled in Humanoid, main structure
				b_use_deform = True
			#finger1 case
			elif 'c_pinky1' in _bone:				
				b_use_deform = arp_armature.data.edit_bones['c_pinky2'+side].use_deform
			elif 'c_ring1' in _bone:				
				b_use_deform = arp_armature.data.edit_bones['c_ring2'+side].use_deform
			elif 'c_middle1' in _bone:					
				b_use_deform = arp_armature.data.edit_bones['c_middle2'+side].use_deform
			elif 'c_index1' in _bone:					
				b_use_deform = arp_armature.data.edit_bones['c_index2'+side].use_deform
			elif 'c_thumb1' in _bone:						
				b_use_deform = arp_armature.data.edit_bones['c_thumb2'+side].use_deform
				
			# jaw case
			elif 'c_jawbone.x' in _bone:						
				b_use_deform = arp_armature.data.edit_bones['jawbone.x'].use_deform
				
				
			else:
				b_use_deform = edit_bone.use_deform
							
			bones_dict[key] = (value[0], edit_bone.head.copy(), edit_bone.tail.copy(), edit_bone.roll, b_use_deform)
	
	# Get the thigh real head pose, because thigh_stretch is halfway	
	for side in sides:
		bname = 'thigh_ref' + side
		thigh_ref = arp_armature.data.edit_bones[bname]
		bones_dict[bname] = (bname, thigh_ref.head.copy(), thigh_ref.tail.copy(), thigh_ref.roll, False)
		
	
	if is_facial_enabled(arp_armature):	
		# Get the jaw real transform
		jaw = arp_armature.data.edit_bones['jawbone.x']
		bones_dict['c_jawbone.x'] = ('c_jawbone.x', jaw.head.copy(), jaw.tail.copy(), jaw.roll, bones_dict['c_jawbone.x'][4])
		
		# Get the eyelids real transform
		for side in sides:
			for pos in ["_top", "_bot"]:
				bname = 'eyelid' + pos + side
				eyel = arp_armature.data.edit_bones[bname]
				bones_dict[bname] = (bname, eyel.head.copy(), eyel.tail.copy(), eyel.roll, bones_dict[bname][4])
	
	
	
	bpy.ops.object.mode_set(mode='POSE') 
	bpy.ops.object.mode_set(mode='OBJECT')
	set_active_object(humanoid_armature.name)
	bpy.ops.object.mode_set(mode='EDIT')	
	
	
	
	# Create additional bones
	custom_root_parent = []
	
	for bone in bones_dict:	
		# if the bone does not exist, create it
		if humanoid_armature.data.edit_bones.get(bone) == None:
			#do not create the thigh_ref, only there for placement reference
			if not 'thigh_ref' in bone:
				new_bone = bpy.context.active_object.data.edit_bones.new(bone) 
				new_bone.head = Vector((0,0,0))
				new_bone.tail = Vector((5,5,5))
				
		# Optional twist bones
	twist_bones = ["c_arm_twist_offset", "forearm_twist", "thigh_twist", "leg_twist"]
	
	if not scn.arp_transfer_twist:	
		for side in sides:
			for b in twist_bones:
				bname = b
				if b == "c_arm_twist_offset":
					bname = "arm_twist"
				new_bone = bpy.context.active_object.data.edit_bones.new(bname+side)			
				new_bone.head = Vector((0,0,0))
				new_bone.tail = Vector((5,5,5))
				if b == "c_arm_twist_offset":
					bparent =  get_edit_bone("arm_stretch"+ side) 
				else:
					bparent =  get_edit_bone(b.replace("twist", "stretch")+ side) 
				new_bone.parent = bparent
				
		
				
		
	bpy.ops.object.mode_set(mode='POSE') 
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.mode_set(mode='EDIT') 
	
	def is_in_facial_deform(bone):
		for b in auto_rig_datas.facial_deform:
			if b in bone:
				return True
	
	# matching bone parent function (humanoid)
	def find_matching_bone(par = None, item = None):
		_parent = ""
		
		if par == 'c_root_bend.x':
			_parent = 'root.x'					
		if par == 'c_root_master.x':
			_parent = 'root.x'	
			if item == "bone":
				custom_root_parent.append(bone)
		if par == 'c_root.x':
			_parent = 'root.x'
			if item == "bone":
				custom_root_parent.append(bone)
		if par == 'c_spine_01.x':
			_parent = 'spine_01.x'
		if par == 'c_spine_02.x':
			_parent = 'spine_02.x'
		if par == 'c_spine_03.x':
			_parent = 'spine_03.x'
		if 'neck' in par:
			_parent = 'neck.x'
		if 'head' in par or ('skull' in par and not scn.arp_full_facial and not is_facial_enabled(arp_armature)):
			_parent = 'head.x'
		if 'shoulder' in par:
			_parent = 'shoulder' + par[-2:]
		if 'arm' in par and not 'forearm' in par:
			_parent = 'arm_stretch' + par[-2:]
		if 'forearm' in par:
			_parent = 'forearm_stretch' + par[-2:]
		if 'hand' in par:
			_parent = 'hand' + par[-2:]
		if 'thigh' in par:
			_parent = 'thigh_stretch' + par[-2:]
		if 'leg' in par:
			_parent = 'leg_stretch' + par[-2:]
		if 'foot' in par:
			_parent = 'foot' + par[-2:]
		if 'toes' in par:
			_parent = 'toes_01' + par[-2:]
		if 'tong_03' in par:
			_parent = 'tong_02.x'					
		if 'tong_02' in par:
			_parent = 'tong_01.x'
		if 'tong_01' in par:
			_parent = 'c_jawbone.x'
		if 'eyelid' in par and not ("top_0" in bone or "bot_0" in bone):# not secondary eyelids
			_parent = 'c_eye_offset' + par[-2:]					
		if "c_eyelid_bot" in par:# secondary eyelids
			_parent = "eyelid_bot" + par[-2:]					
		if "c_eyelid_top" in par:
			_parent = "eyelid_top" + par[-2:]							
		if 'teeth_top_master' in par:
			if arp_armature.data.bones.get('c_skull_01.x'):
				_parent = 'c_skull_01.x'
			else:
				_parent = 'head.x'
		if 'teeth_bot_master' in par:
			_parent = 'c_jawbone.x'		
		if 'jawbone.x' in par:
			_parent = 'c_jawbone.x'	

		return _parent
	
	# Set their parent
	for bone in bones_dict:		
		
		if ('cc_' in bone) or (is_bend_bone(bone)) or (is_in_facial_deform(bone) and scn.arp_full_facial) or (bone[:-2] in additional_facial_bones or ('c_toes_' in bone) or (bone[:-4] == "c_tail_")):
									
			bone_parent = ""
			
			if arp_armature.data.bones[bone].parent:
				bone_parent = arp_armature.data.bones[bone].parent.name
			
			# override these parents
			_parent = ""
			if 'c_eye_ref' in bone:
				bone_parent = 'c_eye_offset' + bone[-2:]
				
			# full facial case parents
			if scn.arp_full_facial and is_facial_enabled(arp_armature):
				if 'jawbone' in bone:				
					if arp_armature.data.bones.get('c_skull_01.x'):
						bone_parent = 'c_skull_01.x'
					else:
						bone_parent = 'head.x'
				if 'eye_offset' in bone:
					if arp_armature.data.bones.get('c_skull_02.x'):
						bone_parent = 'c_skull_02.x'
					else:
						bone_parent = 'head.x'
				if 'lips_' in bone and '_offset' in bone_parent:
					if 'top' in bone or 'smile' in bone:
						if arp_armature.data.bones.get('c_skull_01.x'):
							bone_parent = 'c_skull_01.x'
						else:
							bone_parent = 'head.x'
					if 'bot' in bone:
						bone_parent = 'c_jawbone.x'				
				
					
			# secondary arms/legs cases
			if scn.arp_keep_bend_bones:
				if 'thigh_bend_contact' in bone or 'thigh_bend_01' in bone:
					bone_parent = 'thigh_twist' + bone[-2:]								
					
				if 'ankle_bend' in bone:
					bone_parent = 'leg_twist' + bone[-2:]				
					
				if 'shoulder_bend' in bone:
					bone_parent = 'arm_twist' + bone[-2:]				
					
				if 'wrist_bend' in bone:
					bone_parent = 'forearm_twist' + bone[-2:]		
					
					
			if bone_parent == 'root.x': 
				custom_root_parent.append(bone) 
					
			# try to find parent bone in the humanoid armature. If not found, look for other matches			
			if get_edit_bone(bone_parent):				
				_parent = bone_parent		
					
			else:
				_parent = find_matching_bone(par = bone_parent, item = "bone")
				
				
			# Assign the bone parent
			if get_edit_bone(_parent) != None:
				bpy.context.active_object.data.edit_bones[bone].parent = get_edit_bone(_parent)
				
				
	
	# Set eyelids parent to eye_offset if full facial
	eyelid_list = ['eyelid_top', 'eyelid_bot']
	if scn.arp_full_facial and is_facial_enabled(arp_armature):
		for el in eyelid_list:
			for side in [".l", ".r"]:
				if get_edit_bone(el + side) != None:
					get_edit_bone(el + side).parent = get_edit_bone("c_eye_offset" + side)	
					
	
	bpy.ops.object.mode_set(mode='POSE') 
	bpy.ops.object.mode_set(mode='EDIT') 
	
	
	
	# Set bones transforms rest pose from bone dict
	for b in humanoid_armature.data.edit_bones:		
		side = b.name[-2:]
		
		# arms and legs
		if b.name[:-2] == 'arm_stretch':
			b.head = bones_dict['shoulder' + side][2]
			b.tail= bones_dict[b.name][2]
			b.roll = bones_dict[b.name][3]
			b.use_deform = bones_dict[b.name][4]
			
		elif b.name[:-2] == 'forearm_stretch':
			b.head = bones_dict['arm_stretch' + side][2]
			b.tail= bones_dict['hand' + side][1]
			b.roll = bones_dict[b.name][3]
			b.use_deform = bones_dict[b.name][4]
			
		elif b.name[:-2] == 'thigh_stretch':
			b.head = bones_dict['thigh_ref' + side][1]
			b.tail= bones_dict['thigh_ref' + side][2]
			b.roll = bones_dict[b.name][3]
			b.use_deform = bones_dict[b.name][4]
		elif b.name[:-2] == 'leg_stretch':
			b.head = bones_dict[b.name][1]
			b.tail= bones_dict['foot' + side][1]
			b.roll = bones_dict[b.name][3]
			b.use_deform = bones_dict[b.name][4]
			
		
	
			
		# twists
		elif b.name[:-2] == 'leg_twist':
			b.head = bones_dict['leg_stretch' + side][2]
			b.tail = bones_dict['foot' + side][1]
			b.roll = bones_dict['leg_stretch' + side][3]
			
		elif b.name[:-2] == 'thigh_twist':
			b.head = bones_dict['thigh_ref' + side][1]
			b.tail = b.head +  (bones_dict['thigh_ref' + side][2] - bones_dict['thigh_ref' + side][1])*0.5
			b.roll = bones_dict['thigh_ref' + side][3]
			
		elif b.name[:-2] == 'arm_twist':
			b.head = bones_dict['shoulder' + side][2]
			b.tail = b.head + (bones_dict['arm_stretch' + side][2] - bones_dict['arm_stretch' + side][1])*0.5
			b.roll = bones_dict['arm_stretch' + side][3]
		
		elif b.name[:-2] == 'forearm_twist':
			b.head = bones_dict['forearm_stretch' + side][2]
			b.tail =bones_dict['hand' + side][1]
			b.roll = bones_dict['forearm_stretch' + side][3]
		
			
		else:
			b.head = bones_dict[b.name][1]
			b.tail= bones_dict[b.name][2]
			b.roll = bones_dict[b.name][3]			
			b.use_deform = bones_dict[b.name][4]	
			
					
		#don't deform bend bones if parent doesn't
		if '_bend' in b.name:
			if b.parent:
				b.use_deform = b.parent.use_deform
	
		
		#Switch the root direction
		if b.name == "root.x":						
			
			#remove parent before	
			get_edit_bone("spine_01.x").parent = None
			get_edit_bone("thigh_stretch.l").parent = None
			get_edit_bone("thigh_stretch.r").parent = None
			
			bpy.ops.armature.select_all(action='DESELECT')
			b.select = True
			bpy.ops.armature.switch_direction()
			#re-assign parent			
			get_edit_bone("spine_01.x").parent = get_edit_bone("root.x")
			get_edit_bone("thigh_stretch.l").parent = get_edit_bone("root.x")
			get_edit_bone("thigh_stretch.r").parent = get_edit_bone("root.x")
			get_edit_bone("spine_01.x").use_connect = True
			
			for bon in custom_root_parent:
				get_edit_bone(bon).parent = get_edit_bone('root.x')
	
	# Make sure eyelids deform when no Full Facial	
	if not scn.arp_full_facial:
		for el in eyelid_list:
			for side in [".l", ".r"]:
				if get_edit_bone(el + side) != None:
					get_edit_bone(el + side).use_deform = True
		
	
	# Workaround to fix the wrong bones orientation at export
	if scn.arp_fix_fbx_rot:
		fix_fbx_bones_rot()
	
	
	
	print("\nAdd constraints...")
	#Add constraints	
	for bone in bpy.context.active_object.pose.bones:			
	
		if bone.name[:3] == 'cc_' or is_bend_bone(bone.name) or (bone.name[:-2] in additional_facial_bones) or ('c_toes_' in bone.name) or (bone.name[:-4] == "c_tail_"):
			if len(bone.constraints) == 0:
				cns = bone.constraints.new('COPY_TRANSFORMS')
				cns.target = bpy.data.objects[arp_armature.name]
				cns.subtarget = bone.name					
		
		# eyelids
		#if bone.name in eyelids:
		#	bone.constraints[0].subtarget = "c_" + bone.constraints[0].subtarget
			
		#twist bones
		elif bone.name[:-2] in twist_bones or bone.name[:-2] == "arm_twist":
			if len(bone.constraints) == 0:
				cns = bone.constraints.new('COPY_TRANSFORMS')
				cns.target = bpy.data.objects[arp_armature.name]
				if bone.name[:-2] == "arm_twist":				
					cns.subtarget = "c_arm_twist_offset" +	bone.name[-2:]
				else:
					cns.subtarget = bone.name
					
				if "arp_twist_fac" in scn.keys():
					cns.influence = scn.arp_twist_fac	
		
		
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.object.mode_set(mode='POSE') 
	
	# Create and key first and last action frame range
	bpy.ops.pose.select_all(action='SELECT')
	
	
	if scn.arp_bake_actions:
		try:		
			action = bpy.data.objects[arp_armature.name].animation_data.action

			current_frame = scn.frame_current#save current frame	  

			for f in action.frame_range:	
				scn.frame_current = f
				scn.frame_set(scn.frame_current)#debug		 
				bpy.context.scn.update()
				
				for bone in bpy.context.selected_pose_bones:
					bone.keyframe_insert(data_path="rotation_euler")
					bone.keyframe_insert(data_path="location")

			#restore current frame
			scn.frame_current = current_frame
			scn.frame_set(scn.frame_current)#debug	

			bpy.data.objects[humanoid_armature.name].animation_data.action.name = action.name + "_humanoid"
			
		except:
			print("	   No action to create")
	
	
	
	bpy.ops.object.mode_set(mode='OBJECT')
	humanoid_armature.hide_viewport = hide_state
	
	
			
				
	#### Set armature modifiers ####
	
	# Transfer weights function		
	def transfer_weight(object=None, vertice=None, vertex_weight=None, group_name=None, dict=None, list=None, target_group=None):
											
		grp_name_base = group_name[:-2]
		side = grp_name[-2:]	
		
		#Dict mode
		if list == None:
			if grp_name_base in dict:													
				if dict[grp_name_base][-2:] == '.x':
					side = ''
				_target_group = dict[grp_name_base]+side
				
				# create the vgroup if necessary										
				if object.vertex_groups.get(_target_group) == None:
					object.vertex_groups.new(name=_target_group)
				
				# asssign weights
				object.vertex_groups[_target_group].add([vertice.index], vertex_weight, 'ADD')
		
		#List mode
		if dict == None:
			if grp_name_base in list:		
			
				# create the vgroup if necessary										
				if object.vertex_groups.get(target_group) == None:
					object.vertex_groups.new(name=target_group)
					
				# asssign weights
				object.vertex_groups[target_group].add([vertice.index], vertex_weight, 'ADD')	
				
					
					
	# Substract weight from one vertex group to another function				
	def substract_weight(object=None, vertice=None, vertex_weight=None, group_name=None, dict=None):
			
		grp_name_base = group_name[:-2]	
		side = grp_name[-2:]	
		
		if "_dupli_" in grp_name:
			grp_name_base = group_name[:-12]
			side = "_" + grp_name[-11:]				
		
		if grp_name_base in dict:													
			if dict[grp_name_base][-2:] == '.x':
				side = ''
			_target_group = dict[grp_name_base]+side
			
			
			if object.vertex_groups.get(_target_group) != None:#if exists					
				object.vertex_groups[_target_group].add([vertice.index], vertex_weight, 'SUBTRACT')
		
	def multiply_weight(object=None, vertice=None, vertex_weight=None, group_name=None, dict=None):
		
		grp_name_base = group_name[:-2]	
		side = grp_name[-2:]	
		
		if "_dupli_" in grp_name:
			grp_name_base = group_name[:-12]
			side = "_" + grp_name[-11:]		
	
		if grp_name_base in dict:		
			
			if object.vertex_groups.get(group_name) != None:#if exists					
				object.vertex_groups[group_name].add([vertice.index], vertex_weight * dict[grp_name_base], 'REPLACE')
				
	def clamp_weights(object=None, vertice=None, vertex_weight=None, group_name=None, dict=None):
	
		grp_name_base = group_name[:-2]	
		side = group_name[-2:]	
		
		if "_dupli_" in group_name:
			grp_name_base = group_name[:-12]
			side = "_" + group_name[-11:]				
		
		if grp_name_base in dict:													
			if dict[grp_name_base][-2:] == '.x':
				side = ''				
							
			_target_group = dict[grp_name_base]+side		
			target_weight = 0.0
			
			if object.vertex_groups.get(_target_group) != None:
				for grp in vertice.groups:							
					if obj.vertex_groups[grp.group].name == _target_group:
						target_weight = grp.weight					
				
			def_weight = min(vertex_weight, target_weight)
			object.vertex_groups[group_name].add([vertice.index], def_weight, 'REPLACE')	
					
					
	
	# Iterates over armature meshes (humanoid)
	deprecated_groups_list = ["pinky1", "ring1", "middle1", "index1", "thumb1", "jawbone.x"]
	found_deprecated = False	
	
	twist_dict = {'leg_twist':'leg_stretch', 'thigh_twist':'thigh_stretch', 'c_arm_twist_offset':'arm_stretch', 'forearm_twist':'forearm_stretch'}
							
	other_dict = {'c_index1_base':'hand', 'c_middle1_base':'hand', 'c_ring1_base':'hand', 'c_pinky1_base':'hand', 'c_thumb1_base':'c_thumb1'}		
	
	substract_inter_dict = {'c_forearm_bend':'forearm_stretch'}
	
	clamp_dict = {'c_thigh_bend_contact': 'thigh_twist', 'c_thigh_bend_01': 'thigh_twist', 'c_thigh_bend_02': 'thigh_twist', 'c_knee_bend': 'leg_stretch', 'c_ankle_bend': 'leg_stretch', 'c_leg_bend_01': 'leg_stretch', 'c_leg_bend_02': 'leg_stretch','c_elbow_bend': 'arm_stretch', 'c_shoulder_bend': 'arm_stretch', 'c_wrist_bend': 'forearm_twist'}
	
	secondary_eyelids_dict = {'c_eyelid_top_01': 'eyelid_top', 'c_eyelid_top_02': 'eyelid_top', 'c_eyelid_top_03': 'eyelid_top', 'c_eyelid_bot_01': 'eyelid_bot', 'c_eyelid_bot_02': 'eyelid_bot', 'c_eyelid_bot_03': 'eyelid_bot', 'c_eyelid_corner_01': 'head.x', 'c_eyelid_corner_02': 'head.x'}
	
	multiply_weight_dict = {"c_waist_bend":0.5, "c_elbow_bend":0.5}
	
	bend_bones_main = {'c_root_bend': 'root.x', 'c_spine_01_bend': 'spine_01.x', 'c_spine_02_bend': 'spine_02.x', 'c_bot_bend':'thigh_stretch', 'c_breast_01': 'spine_02.x', 'c_breast_02': 'spine_02.x', 'c_neck_01': 'spine_02.x'}
	
	
	
	#If there's a spine_03, transfer the neck_01 to spine_03 instead of spine_02	
	if bpy.data.objects[arp_armature.name].data.bones.get("spine_03.x") != None:					
		bend_bones_main['c_neck_01'] = "spine_03.x"				
	
	
			
	for obj_name in collected_meshes:
		obj = bpy.data.objects[obj_name]
		if len(obj.modifiers) > 0:
			for modif in obj.modifiers:					
				if modif.type == 'ARMATURE':	
					if modif.object != None:
						if modif.object.name == arp_armature.name:
							
							set_active_object(obj.name)
							
							#replace with humanoid armature
							modif.object = humanoid_armature
							modif.use_deform_preserve_volume = False											
							
						
							
							for vert in obj.data.vertices:
								
								if len(vert.groups) > 0:
									for grp in vert.groups:
										
										try:
											grp_name = obj.vertex_groups[grp.group].name
										except:											
											continue
										weight = grp.weight					
										
										# Twists bones						
										if scn.arp_transfer_twist:										
											transfer_weight(object=obj, vertice=vert, vertex_weight=weight, group_name=grp_name, dict=twist_dict)	
										
										
										# Advanced - Bend Bones					
										if not scn.arp_keep_bend_bones:										
											
											transfer_weight(object=obj, vertice=vert, vertex_weight=weight, group_name=grp_name, dict=bend_bones_main)
											
										else:
											# Clamp weights (make sure c_thigh_bend_contact influence is contained inside thigh_twist for better deformations)										
											clamp_weights(object=obj, vertice=vert, vertex_weight=weight, group_name=grp_name, dict=clamp_dict)
																						
										
											
										# Full Facial
										if not scn.arp_full_facial:											
											#transfer skulls
											transfer_weight(object=obj, vertice=vert, vertex_weight=weight, group_name=grp_name, list=["c_skull_01", "c_skull_02", "c_skull_03"], target_group = "head.x")											
											
											if is_facial_enabled(arp_armature):			
												# facial head
												transfer_weight(object=obj, vertice=vert, vertex_weight=weight, group_name=grp_name, list=facial_transfer_head+facial_transfer_ears, target_group='head.x')	
												
												# facial jaw
												transfer_weight(object=obj, vertice=vert, vertex_weight=weight, group_name=grp_name, list=facial_transfer_jaw, target_group = "jawbone.x")

												# secondary eyelids to main eyelids													
												transfer_weight(object=obj, vertice=vert, vertex_weight=weight, group_name=grp_name, dict=secondary_eyelids_dict)
												
										
										#else:# Full facial, tweak secondary eyelids
										
											# Substract secondary eyelids weights
											#substract_weight(object=obj, vertice=vert, vertex_weight=weight, group_name=grp_name, dict=secondary_eyelids_dict)
											
										# Lower some weights for better results
										multiply_weight(object=obj, vertice=vert, vertex_weight=grp.weight, group_name=grp_name, dict=multiply_weight_dict)
											
										
										# Others											
										transfer_weight(object=obj, vertice=vert, vertex_weight=weight, group_name=grp_name, dict=other_dict)

										
							
						
										
							# Rename the vgroups if necessary							
							for vgroup in obj.vertex_groups:
								#rename fingers vgroups
								for name in deprecated_groups_list:
									if name in vgroup.name and not "base" in vgroup.name and not "c_" in vgroup.name:
										vgroup.name = "c_" + vgroup.name
										found_deprecated = True
									
								if vgroup.name == "root.x" and humanoid_armature.data.bones.get("c_root_bend.x"):
									vgroup.name = "c_root_bend.x"

			
								#rename arm twist vgroup
								if "c_arm_twist_offset" in vgroup.name:
									vgroup.name = vgroup.name.replace("c_arm_twist_offset", "arm_twist")
							
						#Remove the Rig Add armature modifier
						if modif.object == bpy.data.objects[armature_add_name]: 
							obj.modifiers.remove(modif)
	
	
	

					
	# Change drivers targets of shape keys (if any) to the humanoid_rig
	set_active_object("rig_humanoid")	
	bpy.ops.object.mode_set(mode='POSE')
	
	for mesh in collected_meshes:	
		obj = bpy.data.objects[mesh]
		drivers_list = get_shape_keys_drivers(obj)
		
		if drivers_list != None:
			print(obj.name, "has shape keys drivers")
			for dr in drivers_list:
				for var in dr.driver.variables:				
					if var.targets[0].id_type == 'OBJECT' or var.type == "TRANSFORM":
						if var.targets[0].id:
							if var.targets[0].id.name == armature_name:
								var.targets[0].id = bpy.data.objects["rig_humanoid"]
						
						# If it's a driver custom property
						# create the bone custom property
						if var.targets[0].data_path:
							if 'pose.bones' in var.targets[0].data_path:
								p_b = var.targets[0].data_path.split('"')[1]								
								if var.targets[0].data_path.split('"')[2] == '][':
									p_b_prop = var.targets[0].data_path.split('"')[3]									
									# create the property
									get_pose_bone(p_b)[p_b_prop] = 0.0
								
	
	# Assign parent bones of objects that are directly parented to bones (humanoid)
	for mesh in collected_meshes:	
		obj = bpy.data.objects[mesh]
		if len(obj.keys()) > 0:
			if "arp_parent_bone" in obj.keys():
				b_parent = obj["arp_parent_bone"]
				
				# Look for the parent bone in the humanoid armature
				parent_found = False			
				
				if bpy.data.objects["rig_humanoid"].data.bones.get(b_parent):
					parent_found = True
					print('	 Object: "'+ obj.name + '" found direct parent bone "' + b_parent + '" in the humanoid armature.')		
			
				# If not found, tries to match with other bones
				if not parent_found:
					print('	 Object: "' + obj.name + '" did not found direct parent bone "' + b_parent + '" in the humanoid armature. Look for other bones...')			
					b_parent = find_matching_bone(par = b_parent, item = "object")
					
				obj_matrix = obj.matrix_world.copy()
				obj.parent = bpy.data.objects["rig_humanoid"]
				obj.parent_bone = b_parent
				obj.matrix_world = obj_matrix
	
	
	#Change deprecated constraints
	print("Change depdrecated constraints...")
	set_active_object(humanoid_armature.name)
	bpy.ops.object.mode_set(mode='POSE')

	if found_deprecated:
		for i in deprecated_groups_list:			
			for side in sides:
				_side = side
				if i[-2:] == ".x":
					_side = ""
					
				pbone = get_pose_bone("c_" + i + _side)
				if pbone != None:
					pbone.constraints[0].subtarget = i + _side
				print("c_" + i + _side, "not found")
		
	bpy.ops.object.mode_set(mode='OBJECT')
	
	print("Changed.")
	
	#Push the bend bones?
	if scn.arp_keep_bend_bones and scn.arp_push_bend:
				
		for _action in bpy.data.actions:		
			_push_bend_bones(_action, 2)
							
	
	
	humanoid_armature.data.pose_position = 'POSE'
	humanoid_armature['set'] = True
	humanoid_armature['binded'] = True
	
	
	
	#Done _set_humanoid_rig()
	
	
def fix_fbx_bones_rot(include_keywords = None, exclude_keywords = None):
	
	# optional include/exclude lists are used to only operate on given bones
			
	print("\nFix FBX rotation...")
	min_angle = 178.8
	max_angle = 181
	
	# Check if the bone-bone parent angle = 179-180° to fix the Fbx rotation issue!
	# Find bones with tedious angles
	bones_to_fix = []
	for b in bpy.context.active_object.data.edit_bones:
	
		operate_on_this_bone = True
		
		if include_keywords != None:
			operate_on_this_bone = False
			for str in include_keywords:
				if str in b.name:
					operate_on_this_bone = True
					break
		
		if exclude_keywords != None:
			for str in exclude_keywords:
				if str in b.name:
					operate_on_this_bone = False
					break							
		
		if operate_on_this_bone and b.parent != None:
			vec1 = b.y_axis
			vec1[1] = 0
			vec2 = b.parent.y_axis
			vec2[1] = 0
			if vec1.magnitude != 0 and vec2.magnitude != 0:
				angle = math.degrees(vec1.angle(vec2))
				if angle > min_angle and angle < max_angle:
					print("180 angle:", b.name, angle)	
					bones_to_fix.append(b)		

	# Add some slight offset to fix this - clumsy :( but works
	print("\nAdding noise...")
	
	def compare_vectors(vec1, vec2):
		true_count = 0
		for i in range(0, len(vec1)):
			if vec1[i] != 0 and vec2[i] != 0:
				if vec1[i]/vec2[i] < 1.001 and vec1[i]/vec2[i] > 0.999:
					true_count += 1
		
		if true_count == len(vec1):
			return True
				

	for b in bones_to_fix:
		
		angle_check = False
		count = 0
		base_length = b.length
		base_pos = b.tail.copy()
		chd_name = ""
		chd_base_pose = None
		
		while not angle_check:
			count += 1
			b_magnitude = (b.tail - b.head).magnitude
			
			# check if the bone has connected bones children, move the head too
			if len(b.children) > 0:
				for chd in b.children:
					if compare_vectors(chd.head, b.tail):
						# save the base pos
						if not chd_base_pose:
							chd_base_pose = chd.head.copy()
							chd_name = chd.name
						chd.head += Vector((b_magnitude*0.002, 0.0, 0.0))
			
			
			b.tail += Vector((b_magnitude*0.002, 0.0, 0.0))
			"""
			if "toes_middle" in b.name:
				print(b.name, b.parent.name)				
				print(count)
			"""
			
			vec1 = b.y_axis
			vec1[1] = 0
			vec2 = b.parent.y_axis
			vec2[1] = 0	
			if vec1.magnitude != 0 and vec2.magnitude != 0:
				angle = math.degrees(vec1.angle(vec2))
				"""
				if "toes_middle" in b.name:
					print(angle)
				"""
				if count > 1000:
					print(b.name, "Iteration exceeded maximum allowed, exit")
					angle_check = True
					
				if b.length / base_length > 1.001:
					print(b.name, "Bone length to long, reset transforms and exit")
					b.tail = base_pos
					if chd_base_pose:
						get_edit_bone(chd_name).head = chd_base_pose
					angle_check = True
					
				if angle < min_angle:		
					angle_check = True
					
			
		   
def _set_mped_rig(armature_name, armature_add_name, manual_set_debug):

	print("\n..............................Building Mped rig..............................")
	
		
	scn = bpy.context.scene
	sides = [".l", ".r"]
	
	# Select the arp armature
	if manual_set_debug:
		arp_armature = bpy.data.objects[armature_name]
	else:
		arp_armature = bpy.data.objects[armature_name + '_arpexport']
	print("selecting armature", arp_armature)
	set_active_object(arp_armature.name)
	bpy.ops.object.mode_set(mode='OBJECT')	
	bpy.ops.object.select_all(action='DESELECT')
	set_active_object(arp_armature.name)
	bpy.ops.object.mode_set(mode='EDIT')
	
	limb_sides.get_multi_limbs()
	

	
	#### Collect deforming bones datas ####	
	print("	 Collect deforming bones...")
	bones_coords = {}
				
	
	# Spine		
	if is_deforming("root.x"):	
		ebone = get_edit_bone("root.x")
		bones_coords["root.x"] = ebone.tail.copy(), ebone.head.copy(), ebone.roll, "None"
	
	if is_deforming("spine_01.x"):		
		ebone = get_edit_bone("spine_01.x")
		bones_coords["spine_01.x"] = ebone.head.copy(), ebone.tail.copy(), ebone.roll, "root.x"
		
	if is_deforming("spine_02.x"):	
		ebone = get_edit_bone("spine_02.x")
		bones_coords["spine_02.x"] = ebone.head.copy(), ebone.tail.copy(), ebone.roll, "spine_01.x"
		
	if is_deforming("spine_03.x"):	
		ebone = get_edit_bone("spine_03.x")
		bones_coords["spine_03.x"] = ebone.head.copy(), ebone.tail.copy(), ebone.roll, "spine_02.x"
	
	# Subnecks
	for bone in bpy.context.active_object.data.edit_bones:
		if "c_subneck_" in bone.name:
			if is_deforming(bone.name):
				bones_coords[bone.name] = bone.head.copy(), bone.tail.copy(), bone.roll, bone.parent.name
	
	
	# Neck - Head
	# Multi-limb support	
	
	for dupli in limb_sides.head_sides:		
		
		# Neck
		if get_edit_bone('neck' + dupli) != None and is_deforming('neck' + dupli):	
			neck = get_edit_bone('neck' + dupli)
			print("Found neck:", neck.name)			
			b_parent=""
			if get_edit_bone("neck_ref" + dupli).parent != None:
				print("Found neck_ref parent")
				ref_parent_name = get_edit_bone("neck_ref" + dupli).parent.name
				if "_ref" in ref_parent_name:
					if get_edit_bone(ref_parent_name.replace("_ref", "")) != None:
						b_parent = ref_parent_name.replace("_ref", "")
					elif get_edit_bone("c_" + ref_parent_name.replace("_ref", "")) != None:
						b_parent = "c_" + ref_parent_name.replace("_ref", "")
						
					print("Assign neck parent:", b_parent)
				else:
					b_parent = ref_parent_name
					print("Neck parent = ", b_parent)
			else:
				print("Could not find neck_ref" + dupli + " parent. Assign to None.")			
				b_parent = ""				
				
			bones_coords[neck.name] = neck.head.copy(), neck.tail.copy(), neck.roll, b_parent
		
			# Neck 01
			if get_edit_bone('c_neck_01' + dupli) != None and is_deforming('c_neck_01' + dupli):	
				neck01 = get_edit_bone('c_neck_01' + dupli)
				b01_parent = b_parent
				bones_coords[neck01.name] = neck01.head.copy(), neck01.tail.copy(), neck01.roll, b01_parent
				
		
		# Head		
		if get_edit_bone('head' + dupli) != None and is_deforming('head' + dupli):	
			head = get_edit_bone('head' + dupli)
			b_parent =""
			if get_edit_bone("head_ref" + dupli) != None:
				print("Found head ref bone")
				head_ref = get_edit_bone("head_ref" + dupli)
				if head_ref.parent != None:
					b_parent = head_ref.parent.name.replace("_ref", "")
				else:
					print("Could not retrieve head parent. Assign to root.")
					b_parent = "root.x"
			else:
				print("Could not retrieve head parent. Assign to root.")
				b_parent = "root.x"
				
			bones_coords[head.name] = head.head.copy(), head.tail.copy(), head.roll, b_parent
			
		#Skulls
		for i in range(1,4):
			if get_edit_bone("c_skull_0" + str(i) + dupli) != None:
				skull = get_edit_bone("c_skull_0" + str(i) + dupli)
				if is_deforming(skull.name):			
					bones_coords[skull.name] = skull.head.copy(), skull.tail.copy(), skull.roll, skull.parent.name
		
		
					
	# Facial
	# Multi limb support
	facial_duplis = []
	if get_edit_bone("jawbone.x") != None and is_deforming("jawbone.x"):
		facial_duplis.append(".x")
	
	for bone in bpy.context.active_object.data.edit_bones:
		if "jawbone_dupli_" in bone.name:
			dupli = bone.name[-12:]
			if not dupli in facial_duplis:
				facial_duplis.append(dupli)
	
	for dupli in facial_duplis:
		
		# Eyes targets
		bname = "c_eye_target" + dupli
		if get_edit_bone(bname) != None:
			ebone = get_edit_bone(bname)			
			bones_coords[ebone.name] = ebone.head.copy(), ebone.tail.copy(), ebone.roll, "None"
			
		for side in sides:
			bname = "c_eye_target" + dupli[:-2] + side
			if get_edit_bone(bname) != None:
				ebone = get_edit_bone(bname)
				bones_coords[ebone.name] = ebone.head.copy(), ebone.tail.copy(), ebone.roll, ebone.parent.name
		
					
		
		# Eyebrow full
		for side in sides:
			bname = "c_eyebrow_full" + dupli[:-2] + side
			if get_edit_bone(bname) != None:
				ebone = get_edit_bone(bname)
				b_parent = ""
				if get_edit_bone("c_skull_02" + dupli):
					b_parent = "c_skull_02" + dupli
				elif get_edit_bone("head" + dupli):
					b_parent = "head" + dupli
				bones_coords[ebone.name] = ebone.head.copy(), ebone.tail.copy(), ebone.roll, b_parent		
		
				
		# Main facial bones
		bones_parent_dict = {}
		for f_bone in auto_rig_datas.facial_deform + ["eyelid_top", "eyelid_bot"]:	
		
			if f_bone[-2:] == ".x":
				bname = f_bone[:-2] + dupli
				if get_edit_bone(bname) != None:
					parent_name = get_edit_bone(bname).parent.name					
					bones_parent_dict[bname] = parent_name				
					
			else:
				for side in sides:					
					suff = dupli[:-2] + side					
					if get_edit_bone(f_bone + suff) != None:	
						ebone = get_edit_bone(f_bone + suff)
						bones_parent_dict[f_bone + suff] = ebone.parent.name	
						
		for bname in bones_parent_dict:			
			if "jawbone" in bname:
				if get_edit_bone("c_skull_01" + dupli):
					bones_parent_dict[bname] = "c_skull_01" + dupli
				else:
					bones_parent_dict[bname] = "head" + dupli
			if "c_lips_bot" in bname:
				bones_parent_dict[bname] = "jawbone" + dupli
			if "c_lips_top" in bname:
				if get_edit_bone("c_skull_01" + dupli):
					bones_parent_dict[bname] = "c_skull_01" + dupli
				else:
					bones_parent_dict[bname] = "head" + dupli			
			if "c_lips_smile" in bname:
				if get_edit_bone("c_skull_01" + dupli):
					bones_parent_dict[bname] = "c_skull_01" + dupli
				else:
					bones_parent_dict[bname] = "head" + dupli
			if "tong_01" in bname:
				bones_parent_dict[bname] = "jawbone" + dupli
			if "tong_02" in bname:
				bones_parent_dict[bname] = "tong_01" + dupli
			if "tong_03" in bname:
				bones_parent_dict[bname] = "tong_02" + dupli
			
			if "eyelid" in bname and not ("_01" in bname or "_02" in bname or '_03' in bname or '_corner_' in bname):
				bones_parent_dict[bname] = "c_eye_offset" + dupli[:-2] + bname[-2:]
				
			
			if "c_eye_ref_track" in bname:
				bones_parent_dict[bname] = "c_eye_offset" + dupli[:-2] + bname[-2:]
			if "c_teeth_top" in bname:
				if get_edit_bone("c_skull_01" + dupli):
					bones_parent_dict[bname] = "c_skull_01" + dupli
				else:
					bones_parent_dict[bname] = "head" + dupli
			if "c_teeth_bot" in bname:
				bones_parent_dict[bname] = "jawbone" + dupli
		
			ebone = get_edit_bone(bname)
			bones_coords[bname] = ebone.head.copy(), ebone.tail.copy(), ebone.roll, bones_parent_dict[bname]
		

	
			
	# Ears
	# Multi-limb support	
	for dupli in limb_sides.ear_sides:	
	
		ears_list = []
		
		for ear_id in range(0,17):
			ear_n = 'ear_' + '%02d' % ear_id + '_ref' + dupli
			if get_edit_bone(ear_n):
				ears_list.append('c_ear_' + '%02d' % ear_id)
				
		
		for ear in ears_list:			
			if is_deforming(ear + dupli):				
				ebone = get_edit_bone(ear + dupli)
				b_parent = ebone.parent.name
				bones_coords[ebone.name] = ebone.head.copy(), ebone.tail.copy(), ebone.roll, b_parent
					
	# Breast
	breast_list = ["c_breast_01", "c_breast_02"]
	if bpy.context.active_object.data.bones.get("c_breast_01.l"):
		for side in sides:
			for breast_name in breast_list:
				if is_deforming(breast_name + side):
					ebone = get_edit_bone(breast_name + side)					
					b_parent = "spine_02.x"
					
					if scn.arp_keep_bend_bones:
						b_parent = "spine_02_bend.x"					
					
					bones_coords[ebone.name] = ebone.head.copy(), ebone.tail.copy(), ebone.roll, b_parent
					
	# Tail
	if bpy.context.active_object.data.bones.get("c_tail_00.x"):
		for i in range(0, bpy.context.active_object.rig_tail_count):		
		
			tail_name = 'c_tail_' + '%02d' % i + ".x"
			if is_deforming(tail_name):
				ebone = get_edit_bone(tail_name)
				b_parent = None
				if ebone.parent:
					b_parent = ebone.parent.name
				
				if "_00" in ebone.name:
					if b_parent:
						if b_parent[:2] == "c_":
							if get_edit_bone(b_parent[2:]) != None:						
								b_parent = b_parent[2:]
							
				if not b_parent:
					b_parent = "c_traj"
					print("Tail parent not set, assigned to null")				
					
						
				bones_coords[ebone.name] = ebone.head.copy(), ebone.tail.copy(), ebone.roll, b_parent
			
			
	# Legs	
	
		# Get bones transforms
	for bone_name in auto_rig_datas.leg_deform:
		for side in limb_sides.leg_sides:
			
			if is_deforming(bone_name + side):
			
				ebone = get_edit_bone(bone_name + side)
				
				if "c_toes" in bone_name:
					b_parent =	get_edit_bone(bone_name + side).parent.name
				
					bones_coords[ebone.name] = ebone.head.copy(), ebone.tail.copy(), ebone.roll, b_parent 
					# toes_01 is stored even if it does not deform
					bones_coords["toes_01"+side] = get_edit_bone("toes_01"+side).head.copy(), get_edit_bone("toes_01"+side).tail.copy(), get_edit_bone("toes_01"+side).roll, "foot" + side 
				
				if bone_name == "foot":
					b_parent = "leg_stretch" + side
					bones_coords[ebone.name] = ebone.head.copy(), ebone.tail.copy(), ebone.roll, b_parent
					
				if bone_name == "toes_01":
					b_parent = "foot" + side
					bones_coords[ebone.name] = ebone.head.copy(), ebone.tail.copy(), ebone.roll, b_parent
					
				if bone_name == "thigh_stretch":
				
					b_parent = get_edit_bone("thigh_twist" + side).parent.parent.name
					
					if b_parent[:2] == "c_":
						if get_edit_bone(b_parent[2:]) != None:						
							b_parent = b_parent[2:]
						else:
							b_parent = "root.x"
							print("	 Error with", bone_name + side, ", could not find the associated parent bone in the M-Ped armature:", get_edit_bone("thigh_twist" + side).parent.parent.name, "\nAssign root.x bone instead.")					
					
					
					bones_coords[ebone.name] = get_edit_bone("thigh_twist" + side).head.copy(), ebone.tail.copy(), ebone.roll, b_parent
					
				if bone_name == "leg_stretch":
					b_parent = "thigh_stretch" + side
					bones_coords[ebone.name] = ebone.head.copy(),  get_edit_bone("leg_twist" + side).tail.copy(), ebone.roll, b_parent
					
				if not scn.arp_transfer_twist:
					if bone_name == "leg_twist":
						b_parent = "leg_stretch" + side
						bones_coords[ebone.name] = ebone.head.copy(), ebone.tail.copy(), ebone.roll, b_parent
						
					if bone_name == "thigh_twist":
						b_parent = "thigh_stretch" + side
						bones_coords[ebone.name] = ebone.head.copy(), ebone.tail.copy(), ebone.roll, b_parent
						
				
	# Arms
	
		# Multi limbs support	

	
		# Get bones transforms
	for bone_name in auto_rig_datas.arm_deform:
		for side in limb_sides.arm_sides:
			if is_deforming(bone_name + side):
				
				ebone = get_edit_bone(bone_name + side)
				
				if bone_name == "shoulder":
					b_parent = get_edit_bone("c_shoulder" + side).parent.name
					bones_coords[ebone.name] = ebone.head.copy(), ebone.tail.copy(), ebone.roll, b_parent
					
					if b_parent[:2] == "c_":
						if get_edit_bone(b_parent[2:]) != None:						
							b_parent = b_parent[2:]
						else:
							b_parent = "root.x"
							print("	 Error with", bone_name + side, ", could not find the associated parent bone in the M-Ped armature:",  get_edit_bone("c_shoulder" + side).parent.name, "\nAssign root.x bone instead.")					
					
					
					bones_coords[ebone.name] = ebone.head.copy(), ebone.tail.copy(), ebone.roll, b_parent
					
				if bone_name == "arm_stretch":
					bones_coords[ebone.name] = get_edit_bone("c_arm_twist_offset" + side).head.copy(), ebone.tail.copy(), ebone.roll, "shoulder" + side
					
				if bone_name == "forearm_stretch":
					bones_coords[ebone.name] = ebone.head.copy(), get_edit_bone("forearm_twist" + side).tail.copy(), ebone.roll, "arm_stretch" + side
					
				if bone_name == "hand":
					bones_coords[ebone.name] = ebone.head.copy(), ebone.tail.copy(), ebone.roll, "forearm_stretch" + side
					
					
				if not scn.arp_transfer_twist:
					if bone_name == "c_arm_twist_offset":
						bones_coords["arm_twist" + side] = ebone.head.copy(), ebone.tail.copy(), ebone.roll, "arm_stretch" + side
						
					if bone_name == "forearm_twist":
						bones_coords["forearm_twist" + side] = ebone.head.copy(), ebone.tail.copy(), ebone.roll, "forearm_stretch" + side
						
				
						
						
	# Fingers	
	for side in limb_sides.arm_sides:
		for b_finger in fingers_deform:
			finger_name = b_finger + side
			if is_deforming(finger_name):
				ebone = get_edit_bone(finger_name)				
				
				if finger_name[:2] == "c_":
					finger_name = finger_name[2:]
				
				b_parent = ""
				
				if "thumb1" in finger_name or "index1_base" in finger_name or "middle1_base" in finger_name or "ring1_base" in finger_name or "pinky1_base" in finger_name:
					b_parent = "hand" + side
				else:
					if "thumb2" in finger_name:
						b_parent = "thumb1" + side
					if "thumb3" in finger_name:
						b_parent = "thumb2" + side
					if "index1" in finger_name:
						b_parent = "index1_base" + side
					if "index2" in finger_name:
						b_parent = "index1" + side
					if "index3" in finger_name:
						b_parent = "index2" + side
					if "middle1" in finger_name:
						b_parent = "middle1_base" + side
					if "middle2" in finger_name:
						b_parent = "middle1" + side
					if "middle3" in finger_name:
						b_parent = "middle2" + side
					if "ring1" in finger_name:
						b_parent = "ring1_base" + side
					if "ring2" in finger_name:
						b_parent = "ring1" + side
					if "ring3" in finger_name:
						b_parent = "ring2" + side
					if "pinky1" in finger_name:
						b_parent = "pinky1_base" + side
					if "pinky2" in finger_name:
						b_parent = "pinky1" + side
					if "pinky3" in finger_name:
						b_parent = "pinky2" + side
			
				
				bones_coords[finger_name] = ebone.head.copy(), ebone.tail.copy(), ebone.roll, b_parent
				
				
	# Advanced bones (bend bones)	
	if scn.arp_keep_bend_bones:
		for eb in bpy.context.active_object.data.edit_bones:
			if is_bend_bone(eb.name) and not is_proxy_bone(eb):
				if not bpy.context.active_object.data.bones[eb.name].layers[22]:#check for disabled limb	
					
					b_parent = eb.parent.name
					
					# Get bone side
					bone_side = ""
					if "_dupli_" in eb.name:
						bone_side = "_" + eb.name[-11:]
					else:
						bone_side = eb.name[-2:]
					
					# Set parent
					if not scn.arp_transfer_twist:
						if 'thigh_bend_contact' in eb.name or 'thigh_bend_01' in eb.name:
							b_parent = 'thigh_twist' + bone_side
						if 'ankle_bend' in eb.name:
							b_parent = 'leg_twist' + bone_side
						if 'shoulder_bend' in eb.name:
							b_parent = 'arm_twist' + bone_side
						if 'wrist_bend' in eb.name:						
							b_parent = 'forearm_twist' + bone_side
					else:
						if 'thigh_bend_contact' in eb.name or 'thigh_bend_01' in eb.name:
							b_parent = 'thigh_stretch' + bone_side
						if 'ankle_bend' in eb.name:
							b_parent = 'leg_stretch' + bone_side
						if 'shoulder_bend' in eb.name:
							b_parent = 'arm_stretch' + bone_side
						if 'wrist_bend' in eb.name:						
							b_parent = 'forearm_stretch' + bone_side
							
					if b_parent == "c_spine_02.x" or b_parent == "c_spine_03.x":
						b_parent = b_parent[2:]
					
					if 'c_root_bend' in eb.name:
						b_parent = "root.x"
					if 'c_waist_bend' in eb.name:
						b_parent = "root.x"
						
						
					# Store bone in dict
					bones_coords[eb.name] = eb.head.copy(), eb.tail.copy(), eb.roll, b_parent
					
		
					
					
	def is_bone_in_dict(bone):
		for b in bones_coords.keys():
			if b == bone:
				return True
				
	def find_matching_bone(bone_parent_name = None, item = None):
		if bone_parent_name[:2] == "c_":
			if is_bone_in_dict(bone_parent_name[2:]):					
				print('	   >Found matching parent: "' + bone_parent_name + '" > "' + bone_parent_name[2:] + '"')	
				bone_parent_name = bone_parent_name[2:]																			
			
			elif "leg_fk" in bone_parent_name:
				bone_match = bone_parent_name[2:].replace("leg_fk", "leg_stretch")
				
				if is_bone_in_dict(bone_match):
					print('	   >Found matching parent: "' + bone_parent_name + '" > "' + bone_match + '"')	
					bone_parent_name = bone_match
			
					
			elif "thigh_fk" in bone_parent_name:
				bone_match = bone_parent_name[2:].replace("thigh_fk", "thigh_stretch")
				
				if is_bone_in_dict(bone_match):
					print('	   >Found matching parent: "' + bone_parent_name + '" > "' + bone_match + '"')	
					bone_parent_name = bone_match						
			
					
			elif "c_arm_fk" in bone_parent_name:
				bone_match = bone_parent_name[2:].replace("arm_fk", "arm_stretch")
				
				if is_bone_in_dict(bone_match):
					print('	   >Found matching parent: "' + bone_parent_name + '" > "' + bone_match + '"')	
					bone_parent_name = bone_match							
			
					
			elif "c_forearm_fk" in bone_parent_name:
				bone_match = bone_parent_name[2:].replace("forearm_fk", "forearm_stretch")
				
				if is_bone_in_dict(bone_match):
					print('	   >Found matching parent: "' + bone_parent_name + '" > "' + bone_match + '"')	
					bone_parent_name = bone_match							
			
			elif "c_hand_fk" in bone_parent_name:
				bone_match = bone_parent_name.replace("c_hand_fk", "hand")
				
				if is_bone_in_dict(bone_match):
					print('	   >Found matching parent: "' + bone_parent_name + '" > "' + bone_match + '"')	
					bone_parent_name = bone_match	

			elif "c_hand_ik" in bone_parent_name:
				bone_match = bone_parent_name.replace("c_hand_ik", "hand")
				
				if is_bone_in_dict(bone_match):
					print('	   >Found matching parent: "' + bone_parent_name + '" > "' + bone_match + '"')	
					bone_parent_name = bone_match

			elif "c_foot_fk" in bone_parent_name:
				bone_match = bone_parent_name.replace("c_foot_fk", "foot")
				
				if is_bone_in_dict(bone_match):
					print('	   >Found matching parent: "' + bone_parent_name + '" > "' + bone_match + '"')	
					bone_parent_name = bone_match	

			elif "c_foot_ik" in bone_parent_name:
				bone_match = bone_parent_name.replace("c_foot_ik", "foot")
				
				if is_bone_in_dict(bone_match):
					print('	   >Found matching parent: "' + bone_parent_name + '" > "' + bone_match + '"')	
					bone_parent_name = bone_match	
					
			elif "c_root_master" in bone_parent_name:
				bone_match = bone_parent_name[2:].replace("root_master", "root")
					
				if is_bone_in_dict(bone_match):
					print('	   >Found matching parent: "' + bone_parent_name + '" > "' + bone_match + '"')	
					bone_parent_name = bone_match
				
			else:
				print('	 Error with ' + item.name + ', could not find the associated parent bone in the M-Ped armature: ' + bone_parent_name + '\nAssign to "root.x" bone instead.')
				bone_parent_name = "root.x"
						
		else:# if bone_parent_name[:2] != "c_"
			# Case where the user parented the custom bones to the twist bones, without exporting the twist bone!
			if scn.arp_transfer_twist:
				if "leg_twist" in bone_parent_name:
					bone_match = bone_parent_name.replace("leg_twist", "leg_stretch")
												
					if is_bone_in_dict(bone_match):
						print('	   >Found matching parent: "' + bone_parent_name + '" > "' + bone_match + '"')	
						bone_parent_name = bone_match
						
				elif "thigh_twist" in bone_parent_name:
					bone_match = bone_parent_name.replace("thigh_twist", "thigh_stretch")
					print(bone_match)
					if is_bone_in_dict(bone_match):
						print('	   >Found matching parent: "' + bone_parent_name + '" > "' + bone_match + '"')	
						bone_parent_name = bone_match

				elif "arm_twist" in bone_parent_name and not "forearm" in bone_parent_name:
					bone_match = bone_parent_name.replace("arm_twist", "arm_stretch")
					
					if is_bone_in_dict(bone_match):
						print('	   >Found matching parent: "' + bone_parent_name + '" > "' + bone_match + '"')	
						bone_parent_name = bone_match
	
				elif "forearm_twist" in bone_parent_name:
					bone_match = bone_parent_name.replace("forearm_twist", "forearm_stretch")
					
					if is_bone_in_dict(bone_match):
						print('	   >Found matching parent: "' + bone_parent_name + '" > "' + bone_match + '"')	
						bone_parent_name = bone_match
				else:
					print('	 Error with ' + item.name + ', could not find the associated parent bone in the M-Ped armature: ' + bone_parent_name + '\nAssign to "root.x" bone instead.')
					bone_parent_name = "root.x"
					
		return bone_parent_name
		
		
	# Custom bones
	for cc_bone in bpy.context.active_object.data.edit_bones:
		if cc_bone.name[:3] == 'cc_':
			print('\n  Adding custom bone "' + cc_bone.name + '"...')
			
			b_parent = ""
			
			if cc_bone.parent != None:
				b_parent = cc_bone.parent.name			
			
			# Look for the parent bone in the m-ped armature
			parent_found = False			
			
			if is_bone_in_dict(b_parent):
				parent_found = True
				print('	 Custom bone: "'+ cc_bone.name + '" found direct parent bone "' + b_parent + '" in the m-ped armature.')				
					
			# If not found, tries to match with other bones
			if not parent_found:
				print('	 Custom bone: "' + cc_bone.name + '" did not found direct parent bone "' + b_parent + '" in the m-ped armature. Look for other bones...')
				
				b_parent = find_matching_bone(bone_parent_name = b_parent, item = cc_bone)
				
				"""
				if b_parent[:2] == "c_":
					if is_bone_in_dict(b_parent[2:]):					
						print('	   >Found matching parent: "' + b_parent + '" > "' + b_parent[2:] + '"')	
						b_parent = b_parent[2:]																			
					
					elif "leg_fk" in b_parent:
						bone_match = b_parent[2:].replace("leg_fk", "leg_stretch")
						
						if is_bone_in_dict(bone_match):
							print('	   >Found matching parent: "' + b_parent + '" > "' + bone_match + '"')	
							b_parent = bone_match
					
							
					elif "thigh_fk" in b_parent:
						bone_match = b_parent[2:].replace("thigh_fk", "thigh_stretch")
						
						if is_bone_in_dict(bone_match):
							print('	   >Found matching parent: "' + b_parent + '" > "' + bone_match + '"')	
							b_parent = bone_match						
					
							
					elif "c_arm_fk" in b_parent:
						bone_match = b_parent[2:].replace("arm_fk", "arm_stretch")
						
						if is_bone_in_dict(bone_match):
							print('	   >Found matching parent: "' + b_parent + '" > "' + bone_match + '"')	
							b_parent = bone_match							
					
							
					elif "c_forearm_fk" in b_parent:
						bone_match = b_parent[2:].replace("forearm_fk", "forearm_stretch")
						
						if is_bone_in_dict(bone_match):
							print('	   >Found matching parent: "' + b_parent + '" > "' + bone_match + '"')	
							b_parent = bone_match							
					
							
					elif "c_root_master" in b_parent:
						bone_match = b_parent[2:].replace("root_master", "root")
							
						if is_bone_in_dict(bone_match):
							print('	   >Found matching parent: "' + b_parent + '" > "' + bone_match + '"')	
							b_parent = bone_match
						
					else:
						print('	 Error with ' + cc_bone.name + ', could not find the associated parent bone in the M-Ped armature: ' + b_parent + '\nAssign to "root.x" bone instead.')
						b_parent = "root.x"
								
				else:# if b_parent[:2] != "c_"
					# Case where the user parented the custom bones to the twist bones, without exporting the twist bone!
					if scn.arp_transfer_twist:
						if "leg_twist" in b_parent:
							bone_match = b_parent.replace("leg_twist", "leg_stretch")
														
							if is_bone_in_dict(bone_match):
								print('	   >Found matching parent: "' + b_parent + '" > "' + bone_match + '"')	
								b_parent = bone_match
								
						elif "thigh_twist" in b_parent:
							bone_match = b_parent.replace("thigh_twist", "thigh_stretch")
							print(bone_match)
							if is_bone_in_dict(bone_match):
								print('	   >Found matching parent: "' + b_parent + '" > "' + bone_match + '"')	
								b_parent = bone_match

						elif "arm_twist" in b_parent and not "forearm" in b_parent:
							bone_match = b_parent.replace("arm_twist", "arm_stretch")
							
							if is_bone_in_dict(bone_match):
								print('	   >Found matching parent: "' + b_parent + '" > "' + bone_match + '"')	
								b_parent = bone_match
			
						elif "forearm_twist" in b_parent:
							bone_match = b_parent.replace("forearm_twist", "forearm_stretch")
							
							if is_bone_in_dict(bone_match):
								print('	   >Found matching parent: "' + b_parent + '" > "' + bone_match + '"')	
								b_parent = bone_match
						else:
							print('	 Error with ' + cc_bone.name + ', could not find the associated parent bone in the M-Ped armature: ' + b_parent + '\nAssign to "root.x" bone instead.')
							b_parent = "root.x"
				"""
				
			#Store bone in dict			
			bones_coords[cc_bone.name] = cc_bone.head.copy(), cc_bone.tail.copy(), cc_bone.roll, b_parent
			
						
	

	
	#### Create M-Ped rig ####
	print("\n  Create the Mped rig...")
	bpy.ops.object.mode_set(mode='OBJECT')	
	bpy.ops.object.select_all(action='DESELECT')	
	
	# Create the armature
	amt = bpy.data.armatures.new('rig_mped_data')
	rig_mped = bpy.data.objects.new('rig_mped', amt)	
	rig_mped.show_in_front= True	 
	rig_mped.location = arp_armature.location
	rig_mped.scale = arp_armature.scale
	
	# if root motion, the armature object is constrained to the c_traj controller
	if scn.arp_ue_root_motion:		
		cns = rig_mped.constraints.new("CHILD_OF")
		cns.target = arp_armature
		cns.subtarget = "c_traj"
		
		arp_armature.data.pose_position = 'REST'	
		bpy.context.scene.update()
		cns.inverse_matrix = arp_armature.pose.bones["c_traj"].matrix.inverted()		
		arp_armature.data.pose_position = 'POSE'
		bpy.context.scene.update()
		
	else:
		cns = rig_mped.constraints.new("COPY_TRANSFORMS")
		cns.target = arp_armature
	
	
	scn.collection.objects.link(rig_mped)
	bpy.context.view_layer.objects.active = rig_mped
	scn.update()
	mped_armature = bpy.data.objects["rig_mped"]
	
		# create the bones
	print("	 Create bones...")
	bpy.ops.object.mode_set(mode='EDIT')
	
	for bone_name in bones_coords:
		new_bone = mped_armature.data.edit_bones.new(bone_name)
		new_bone.head = bones_coords[bone_name][0]
		new_bone.tail = bones_coords[bone_name][1]
		new_bone.roll = bones_coords[bone_name][2]
		
		# set the parent
	print("	 Set parents...")
	for bone_name in bones_coords:
		if bones_coords[bone_name][3] != "None":
			get_edit_bone(bone_name).parent = get_edit_bone(bones_coords[bone_name][3])
			
	bpy.ops.object.mode_set(mode='POSE')
	bpy.ops.object.mode_set(mode='EDIT')	
	
	if scn.arp_fix_fbx_rot:
		fix_fbx_bones_rot()
				
	
		# Assign the constraints
	print("\n  Create constraints...")
	
	# for debug only
	set_constraints = True
	
	bpy.ops.object.mode_set(mode='POSE')

	if set_constraints:
	
		def add_copy_transf(p_bone, b_name):	
			cns_transf = p_bone.constraints.new("COPY_TRANSFORMS")
			cns_transf.target = bpy.data.objects[arp_armature.name]
			cns_transf.subtarget = b_name			
			
			
		
		for bone_name in bones_coords:
			pbone = get_pose_bone(bone_name)
			
			bone_side = ""
			
			if "_dupli_" in pbone.name:
				bone_side = "_" + pbone.name[-11:]
			else:
				bone_side = pbone.name[-2:]
			
				
			# Spine
			if bone_name == "root.x":
				cns1 = pbone.constraints.new("COPY_TRANSFORMS")
				cns1.target = bpy.data.objects[arp_armature.name]
				cns1.subtarget = "root.x"
				cns1.head_tail = 1.0
				
				cns2 = pbone.constraints.new("LOCKED_TRACK")
				cns2.target = bpy.data.objects[arp_armature.name]
				cns2.subtarget = "root.x"
				cns2.track_axis = "TRACK_Y"
				cns2.lock_axis = "LOCK_X"
				
			if bone_name == "spine_01.x":			
				add_copy_transf(pbone, bone_name)					
				
			if bone_name == "spine_02.x":
				add_copy_transf(pbone, bone_name)

			if bone_name == "spine_03.x":
				add_copy_transf(pbone, bone_name)
				
			if "neck" in bone_name and ".x" in bone_name:
				add_copy_transf(pbone, bone_name)
				
			if "head" in bone_name and ".x" in bone_name:
				add_copy_transf(pbone, bone_name)
				
			if "c_skull_" in bone_name:
				add_copy_transf(pbone, bone_name)
				
			
				
			# Facial
			for bname in auto_rig_datas.facial_deform:
				_s = bname
				if ".x" in bname:
					_s = bname.replace(".x", "")
				if _s in bone_name:
					if len(pbone.constraints) == 0:
						add_copy_transf(pbone, bone_name)
				
			if "c_eye_target" in bone_name:
				add_copy_transf(pbone, bone_name)	
			
			
			# Ears
			if "c_ear_" in bone_name:
				add_copy_transf(pbone, bone_name)
			
			# Tail
			if "c_tail" in bone_name:
				add_copy_transf(pbone, bone_name)
			
			# Breast
			if "c_breast_" in bone_name:
				add_copy_transf(pbone, bone_name)
			
			
			
			# Legs
			if "toes_01" in bone_name or "foot" in bone_name or "leg_stretch" in bone_name or "thigh_stretch" in bone_name:			
				add_copy_transf(pbone, bone_name)
			
			if "thigh_twist" in bone_name or "leg_twist" in bone_name:
			
				cns_transf = pbone.constraints.new("COPY_TRANSFORMS")
				cns_transf.target = bpy.data.objects[arp_armature.name]
				cns_transf.subtarget = bone_name		
			
				if "arp_twist_fac" in bpy.context.scene.keys():
					cns_transf.influence = bpy.context.scene.arp_twist_fac
			
			if "thigh_stretch" in bone_name:
				cns_loc = pbone.constraints.new("COPY_LOCATION")
				cns_loc.target = bpy.data.objects[arp_armature.name]				
				cns_loc.subtarget = "thigh_twist" + bone_side
				
			# Toes
			if "c_toes" in bone_name:
				add_copy_transf(pbone, bone_name)
				
			
			# Arms
			if "shoulder" in bone_name or "arm_stretch" in bone_name or "hand" in bone_name or "forearm_stretch" in bone_name:
				add_copy_transf(pbone, bone_name)
				
			if "forearm_twist" in bone_name :
				cns_transf = pbone.constraints.new("COPY_TRANSFORMS")
				cns_transf.target = bpy.data.objects[arp_armature.name]
				cns_transf.subtarget = bone_name		
				
				if "arp_twist_fac" in bpy.context.scene.keys():
						cns_transf.influence = bpy.context.scene.arp_twist_fac
				
		
				
			if "arm_twist" in bone_name and not "forearm" in bone_name:
				cns1 = pbone.constraints.new("COPY_TRANSFORMS")
				cns1.target = bpy.data.objects[arp_armature.name]								
				cns1.subtarget = "c_arm_twist_offset" + bone_side			
			
				
					

			if "arm_stretch" in bone_name and not "forearm" in bone_name:
				cns_loc = pbone.constraints.new("COPY_LOCATION")
				cns_loc.target = bpy.data.objects[arp_armature.name]				
				cns_loc.subtarget = "c_arm_twist_offset" + bone_side
				
			
			
			# Fingers		
			for fing in fingers_names:
				if not "c_toes" in bone_name:
					if fing + "1" in bone_name or fing + "2" in bone_name or fing + "3" in bone_name:
						target_bone = bone_name
						if get_edit_bone(bone_name) == None:
							target_bone = "c_" + bone_name			
							
						add_copy_transf(pbone, target_bone)
			
			# Custom Bones
			if bone_name[:3] == 'cc_':
				add_copy_transf(pbone, bone_name)
			
			# Bend bones
			if is_bend_bone(bone_name):
				add_copy_transf(pbone, bone_name)
			
	
			
	#### Assign the armature modifiers and weights ####
	print("\n  Assign modifiers and weights...")	
	
	# Transfer Weight of one vertex group to another function
	def transfer_weight(object=None, vertice=None, vertex_weight=None, group_name=None, dict=None, list=None, target_group=None):
											
		grp_name_base = group_name[:-2]	
		side = grp_name[-2:]	
		
		if "_dupli_" in grp_name:
			grp_name_base = group_name[:-12]
			side = "_" + grp_name[-11:]
		
		#Dict mode
		if list == None:
			if grp_name_base in dict:													
				if dict[grp_name_base][-2:] == '.x':
					side = ''
				_target_group = dict[grp_name_base]+side				
				
				# create the vgroup if necessary										
				if object.vertex_groups.get(_target_group) == None:
					object.vertex_groups.new(name=_target_group)				
								
				# assign weights
				object.vertex_groups[_target_group].add([vertice.index], vertex_weight, 'ADD')
		
		#List mode
		if dict == None:
			if grp_name_base in list:	
				
				# create the vgroup if necessary										
				if object.vertex_groups.get(target_group) == None:
					object.vertex_groups.new(name=target_group)			
					
				# assign weights
				object.vertex_groups[target_group].add([vertice.index], vertex_weight, 'ADD')	
					
	# Substract weight from one vertex group to another function				
	def substract_weight(object=None, vertice=None, vertex_weight=None, group_name=None, dict=None):
			
		grp_name_base = group_name[:-2]	
		side = grp_name[-2:]	
		
		if "_dupli_" in grp_name:
			grp_name_base = group_name[:-12]
			side = "_" + grp_name[-11:]				
		
		if grp_name_base in dict:													
			if dict[grp_name_base][-2:] == '.x':
				side = ''
			_target_group = dict[grp_name_base]+side
			
			
			if object.vertex_groups.get(_target_group) != None:#if exists					
				object.vertex_groups[_target_group].add([vertice.index], vertex_weight, 'SUBTRACT')
		
	def multiply_weight(object=None, vertice=None, vertex_weight=None, group_name=None, dict=None):
		
		grp_name_base = group_name[:-2]	
		side = grp_name[-2:]	
		
		if "_dupli_" in grp_name:
			grp_name_base = group_name[:-12]
			side = "_" + grp_name[-11:]		
	
		if grp_name_base in dict:		
			
			if object.vertex_groups.get(group_name):			
				object.vertex_groups[group_name].add([vertice.index], vertex_weight * dict[grp_name_base], 'REPLACE')
				#print("multiply", group_name, vertex_weight, "*", dict[grp_name_base], " = ", vertex_weight*dict[grp_name_base])
				
	def clamp_weights(object=None, vertice=None, vertex_weight=None, group_name=None, dict=None):
	
		grp_name_base = group_name[:-2]	
		side = group_name[-2:]	
		
		if "_dupli_" in group_name:
			grp_name_base = group_name[:-12]
			side = "_" + group_name[-11:]				
		
		if grp_name_base in dict:													
			if dict[grp_name_base][-2:] == '.x':
				side = ''
				
			_target_group = dict[grp_name_base]+side			
			target_weight = 0.0
			
			if object.vertex_groups.get(_target_group) != None:
				for grp in vertice.groups:								
					if obj.vertex_groups[grp.group].name == _target_group:
						target_weight = grp.weight				
			
			def_weight = min(vertex_weight, target_weight)
			object.vertex_groups[group_name].add([vertice.index], def_weight, 'REPLACE')				
		
		
	
	def select_overlap(obj, vgroup1, vgroup2, vgroups):		
		print("Select Overlap")
		bpy.ops.mesh.select_all(action='DESELECT')#first					
		vgroups.active_index = vgroups[vgroup1].index
		bpy.ops.object.vertex_group_select()
		mesh = bmesh.from_edit_mesh(obj.data)					
		list1 = [vert.index for vert in mesh.verts if vert.select]
		bpy.ops.mesh.select_all(action='DESELECT')#second					
		vgroups.active_index = vgroups[vgroup2].index
		bpy.ops.object.vertex_group_select()					
		list2 = [vert.index for vert in mesh.verts if vert.select]
		bpy.ops.mesh.select_all(action='DESELECT')
		overlap = [i for i in list1 if i in list2]				

		for vert in mesh.verts:						
			if vert.index in overlap:							
				vert.select = True	
	
	twist_dict = {'leg_twist':'leg_stretch', 'thigh_twist':'thigh_stretch', 'c_arm_twist_offset':'arm_stretch', 'forearm_twist':'forearm_stretch'}

	other_dict = {'c_thumb1_base':'c_thumb1'}	

	bend_bones_dict = {'c_root_bend': 'root.x', 'c_spine_01_bend': 'spine_01.x', 'c_spine_02_bend': 'spine_02.x', 'c_bot_bend':'thigh_stretch'}	
			
	multiply_weight_dict = {"c_waist_bend":0.5, "c_elbow_bend":0.5}
	
	substract_inter_dict = {'c_forearm_bend':'forearm_stretch'}	
	
	clamp_dict = {'c_thigh_bend_contact': 'thigh_twist', 'c_thigh_bend_01': 'thigh_twist', 'c_thigh_bend_02': 'thigh_twist', 'c_knee_bend': 'leg_stretch', 'c_ankle_bend': 'leg_stretch', 'c_leg_bend_01': 'leg_stretch', 'c_leg_bend_02': 'leg_stretch','c_elbow_bend': 'arm_stretch', 'c_shoulder_bend': 'arm_stretch', 'c_wrist_bend': 'forearm_twist'}
	
	
	collected_meshes = []
	# Iterate over meshes (mped)	
	for obj in bpy.data.objects:		
		if obj.type == 'MESH' and ("_arpexport" in obj.name or manual_set_debug):
			collected_meshes.append(obj.name)
						
			# obj with armature modifiers
			if len(obj.modifiers) > 0:
				for modif in obj.modifiers:					
					if modif.type == 'ARMATURE':				
						if modif.object != None:
							if modif.object.name == arp_armature.name:				
								print("	 ..", obj.name)
								#replace with humanoid armature
								modif.object = bpy.data.objects["rig_mped"]							
								modif.use_deform_preserve_volume = False
								
								# Transfer weights
								for vert in obj.data.vertices:								
									if len(vert.groups) > 0:										
									
										for grp in vert.groups:										
											try:
												grp_name = obj.vertex_groups[grp.group].name
											except:											
												continue
												
											weight = grp.weight					
											
											# Twist bones						
											if scn.arp_transfer_twist:										
												transfer_weight(object=obj, vertice=vert, vertex_weight=weight, group_name=grp_name, dict=twist_dict)
										
											
											# Advanced - Bend bones
											if not scn.arp_keep_bend_bones:										
												transfer_weight(object=obj, vertice=vert, vertex_weight=weight, group_name=grp_name, dict=bend_bones_dict)	
												
											else:
												# Clamp weights (make sure additive influence is contained inside the main groups for better deformations)
												clamp_weights(object=obj, vertice=vert, vertex_weight=weight, group_name=grp_name, dict=clamp_dict)												
												
												
											# Multiply some weights for better results
											multiply_weight(object=obj, vertice=vert, vertex_weight=grp.weight, group_name=grp_name, dict=multiply_weight_dict)

											# Others														
											transfer_weight(object=obj, vertice=vert, vertex_weight=weight, group_name=grp_name, dict=other_dict)

											
					
								# Change fingers vertex groups names
								for vgroup in obj.vertex_groups:
									for f_name in fingers_names:
										if f_name in vgroup.name:
											if vgroup.name[:2] == "c_" and not "c_toes_" in vgroup.name:
												vgroup.name = vgroup.name[2:]
												
									if "c_arm_twist_offset" in vgroup.name:
										vgroup.name = vgroup.name.replace("c_arm_twist_offset", "arm_twist")
										
									if vgroup.name == "root.x" and mped_armature.data.bones.get("c_root_bend.x"):
										vgroup.name = "c_root_bend.x"
								
							if modif.object.name == "rig_add":
								obj.modifiers.remove(modif)
								
	
	# Rename some bones for retro-compatibility or better clarity
	facial_def_names = {"eyelid_top": "c_eyelid_top", "eyelid_bot": "c_eyelid_bot", "jawbone.x": "c_jawbone.x"}
	print("Bones renaming...")
	for dupli in facial_duplis:
		for side in sides:
			for b_name in facial_def_names:
				
				suffix = dupli[:-2] + side	
				_b_name = b_name
				#_side = side
				
				if b_name[-2:] == ".x":
					suffix = dupli
					_b_name = b_name[:-2]
					#_side = ""
				
				print(_b_name + suffix)
				
				if mped_armature.data.bones.get(_b_name + suffix) != None:
				
					n = facial_def_names[b_name] + suffix
					if facial_def_names[b_name][-2:] == ".x":
						n = facial_def_names[b_name][:-2] + suffix
						
					mped_armature.data.bones[_b_name + suffix].name = n
					print("Renamed:", _b_name + suffix, "to", n)
				
	
	
	
	
	# Change drivers targets of shape keys (if any) to the mped_rig
	set_active_object("rig_mped")	
	bpy.ops.object.mode_set(mode='POSE')
	
	for mesh in collected_meshes:	
		obj = bpy.data.objects[mesh]
		drivers_list = get_shape_keys_drivers(obj)		
			
		if drivers_list != None:
			print(obj.name, "has shape keys drivers")
			for dr in drivers_list:
				for var in dr.driver.variables:				
					if var.targets[0].id_type == 'OBJECT' or var.type == "TRANSFORM":
						if var.targets[0].id:
							if var.targets[0].id.name == armature_name:
								var.targets[0].id = bpy.data.objects["rig_mped"]
						
						# If it's a driver custom property
						# create the bone custom property
						if var.targets[0].data_path:
							if 'pose.bones' in var.targets[0].data_path:
								p_b = var.targets[0].data_path.split('"')[1]								
								if var.targets[0].data_path.split('"')[2] == '][':
									p_b_prop = var.targets[0].data_path.split('"')[3]									
									# create the property
									get_pose_bone(p_b)[p_b_prop] = 0.0
									
									
	# Assign parent bones of objects that are directly parented to bones (mped)
	for mesh in collected_meshes:	
		obj = bpy.data.objects[mesh]
		if len(obj.keys()) > 0:
			if "arp_parent_bone" in obj.keys():
				b_parent = obj["arp_parent_bone"]
				
				# Look for the parent bone in the m-ped armature
				parent_found = False			
				
				if is_bone_in_dict(b_parent):
					parent_found = True
					print('	 Object: "'+ obj.name + '" found direct parent bone "' + b_parent + '" in the m-ped armature.')				
						
				# If not found, tries to match with other bones
				if not parent_found:
					print('	 Object: "' + obj.name + '" did not found direct parent bone "' + b_parent + '" in the m-ped armature. Look for other bones...')			
					b_parent = find_matching_bone(bone_parent_name = b_parent, item = obj)
					
				obj_matrix = obj.matrix_world.copy()
				obj.parent = bpy.data.objects["rig_mped"]
				obj.parent_bone = b_parent
				obj.matrix_world = obj_matrix
	
	
	# Create and key first and last action frame range
	bpy.ops.pose.select_all(action='SELECT')
	try:
		action = bpy.data.objects[arp_armature.name].animation_data.action

		current_frame = scn.frame_current#save current frame	  

		for f in action.frame_range:	
			scn.frame_current = f
			scn.frame_set(scn.frame_current)#debug		 
			bpy.context.scn.update()
			
			for bone in bpy.context.selected_pose_bones:
				bone.keyframe_insert(data_path="rotation_euler")
				bone.keyframe_insert(data_path="location")

		#restore current frame
		scn.frame_current = current_frame
		scn.frame_set(scn.frame_current)#debug	

		bpy.data.objects[mped_armature.name].animation_data.action.name = action.name + "_mped"
		
	except:
		print("	 No action to create")
		
	
	#Push the bend bones?
	if scn.arp_keep_bend_bones and scn.arp_push_bend:				
		for _action in bpy.data.actions:		
			_push_bend_bones(_action, 2)


	
	bpy.data.armatures[mped_armature.data.name].pose_position = 'POSE'
	mped_armature['set'] = True
	mped_armature['binded'] = True
	
	
	print("\nMped rig built.")
	
	
	
def _constraint_rig(state):

	scn = bpy.context.scene
	baked_armature = None
	
	if scn.arp_export_rig_type == "humanoid":
		baked_armature = bpy.data.objects['rig_humanoid']
	if scn.arp_export_rig_type == "mped":
		baked_armature = bpy.data.objects['rig_mped']
	
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.select_all(action='DESELECT')
	
	#Unhide if hidden
	mute_state = baked_armature.hide_viewport
	baked_armature.hide_viewport = False	
	
	set_active_object(baked_armature.name)	
	
	#Switch to Pose mode
	bpy.ops.object.mode_set(mode='POSE')
	bpy.ops.pose.select_all(action='SELECT')
	
	#Mute or Unmute constraints
	for bone in bpy.context.selected_pose_bones:
		for cns in bone.constraints:
			if cns.name != "Track To" and cns.name != "Stretch To":
				cns.mute = state
				
	for cns in bpy.context.active_object.constraints:
		cns.mute = state
		   
	bpy.ops.object.mode_set(mode='OBJECT')
	#bpy.ops.transform.translate(value=(0, 0, 0))#update	  
	bpy.context.scene.update()
	
	#reset hide state
	baked_armature.hide_viewport = mute_state
	
	baked_armature['binded'] = not state 
	
	


def update_engine_type(self, context):
	if context.scene.arp_engine_type == "unity":
		
		#context.scene.arp_mannequin_axes = False		
		#context.scene.arp_rename_for_ue = False
		#context.scene.arp_ue_ik = False
		
		if context.scene.arp_export_rig_type != "mped":
			context.scene.arp_transfer_twist = True
			
	
def revert_rename_for_ue():	

	
	

	if bpy.data.objects.get("rig_humanoid") != None:
		for pbone in bpy.data.objects['rig_humanoid'].pose.bones:
			if not '_bend' in pbone.name:
				if 'thigh' in pbone.name and not 'stretch' in pbone.name:
					if not 'twist' in pbone.name:
						pbone.name = pbone.name.replace('thigh', 'thigh_stretch')
					else:
						pbone.name = pbone.name.replace('thigh_twist_01', 'thigh_twist')
				if 'calf' in pbone.name:
					if not 'twist' in pbone.name:
						pbone.name = pbone.name.replace('calf', 'leg_stretch')
					else:
						pbone.name = pbone.name.replace('calf_twist_01', 'leg_twist')
				if 'ball' in pbone.name:
					pbone.name = pbone.name.replace('ball', 'toes_01')
				if 'clavicle' in pbone.name:
					pbone.name = pbone.name.replace('clavicle','shoulder')
				if 'upperarm' in pbone.name:
					if not 'twist' in pbone.name:
						pbone.name = pbone.name.replace('upperarm', 'arm_stretch')
					else:
						pbone.name = pbone.name.replace('upperarm_twist_01', 'arm_twist')
				if 'lowerarm' in pbone.name:
					if not 'twist' in pbone.name:
						pbone.name = pbone.name.replace('lowerarm', 'forearm_stretch')
					else:
						pbone.name = pbone.name.replace('lowerarm_twist_01', 'forearm_twist')
				if 'index_01' in pbone.name:
					pbone.name = pbone.name.replace('index_01', 'c_index1')
				if 'index_02' in pbone.name:
					pbone.name = pbone.name.replace('index_02', 'c_index2')
				if 'index_03' in pbone.name:
					pbone.name = pbone.name.replace('index_03', 'c_index3')
				if 'middle_01' in pbone.name:
					pbone.name = pbone.name.replace('middle_01', 'c_middle1')
				if 'middle_02' in pbone.name:
					pbone.name = pbone.name.replace('middle_02', 'c_middle2')
				if 'middle_03' in pbone.name:
					pbone.name = pbone.name.replace('middle_03', 'c_middle3')
				if 'ring_01' in pbone.name:
					pbone.name = pbone.name.replace('ring_01', 'c_ring1')
				if 'ring_02' in pbone.name:
					pbone.name = pbone.name.replace('ring_02', 'c_ring2')
				if 'ring_03' in pbone.name:
					pbone.name = pbone.name.replace('ring_03', 'c_ring3')
				if 'pinky_01' in pbone.name:
					pbone.name = pbone.name.replace('pinky_01', 'c_pinky1')
				if 'pinky_02' in pbone.name:
					pbone.name = pbone.name.replace('pinky_02', 'c_pinky2')
				if 'pinky_03' in pbone.name:
					pbone.name = pbone.name.replace('pinky_03', 'c_pinky3')
				if 'thumb_01' in pbone.name:
					pbone.name = pbone.name.replace('thumb_01', 'c_thumb1')
				if 'thumb_02' in pbone.name:
					pbone.name = pbone.name.replace('thumb_02', 'c_thumb2')
				if 'thumb_03' in pbone.name:
					pbone.name = pbone.name.replace('thumb_03', 'c_thumb3')
				if 'neck_01' in pbone.name:
					pbone.name = 'neck.x'
				if 'spine_01' in pbone.name:
					pbone.name = 'spine_01.x'
				if 'spine_02' in pbone.name:
					pbone.name = 'spine_02.x'
				if 'spine_03' in pbone.name:
					pbone.name = 'spine_03.x'
				if 'head' in pbone.name:
					pbone.name = 'head.x'
				if 'pelvis' in pbone.name:
					pbone.name = 'root.x'
					
					
		
					
	else:
		print("rig_humanoid not found.")

		
def rename_for_ue():
	
	scene = bpy.context.scene
	
	if scene.arp_rename_for_ue:
		print("\nRename for UE")
		
		# save the rig_fist data paths, since it's being renamed as well by blender automatically by mistake(c_ring1 > ring1)
		action_fist = None
		fc_save = []
		
		for action in bpy.data.actions:
			if "rig_fist" in action.name:
				action_fist = action		
		
		if action_fist != None:
			print("saving rig fist action data path...")
			for fc in action_fist.fcurves:
				fc_save.append(fc.data_path)
			print("saved.")
			
			
		
		for pbone in bpy.data.objects['rig_humanoid'].pose.bones:
			# exclude secondary bones, custom controllers, from renaming
			if not '_bend' in pbone.name and pbone.name[:3] != "cc_":
				if 'thigh' in pbone.name:
					if not 'twist' in pbone.name:
						pbone.name = pbone.name.replace('thigh_stretch', 'thigh')
					else:
						pbone.name = pbone.name.replace('thigh_twist', 'thigh_twist_01')
				if 'leg' in pbone.name:
					if not 'twist' in pbone.name:
						pbone.name = pbone.name.replace('leg_stretch', 'calf')
					else:
						pbone.name = pbone.name.replace('leg_twist', 'calf_twist_01')
				if 'toes' in pbone.name:
					pbone.name = pbone.name.replace('toes_01', 'ball')
				if 'shoulder' in pbone.name:
					pbone.name = pbone.name.replace('shoulder','clavicle')
				if 'arm_stretch' in pbone.name and not 'forearm_stretch' in pbone.name:
					pbone.name = pbone.name.replace('arm_stretch', 'upperarm')
				if 'arm_twist' in pbone.name and not 'forearm_twist' in pbone.name:
					pbone.name = pbone.name.replace('arm_twist', 'upperarm_twist_01')
				if 'forearm_stretch' in pbone.name:
					pbone.name = pbone.name.replace('forearm_stretch', 'lowerarm')
				if 'forearm_twist' in pbone.name:
					pbone.name = pbone.name.replace('forearm_twist', 'lowerarm_twist_01')
				if 'forearm_inter' in pbone.name:
					pbone.name = pbone.name.replace('forearm_inter', 'lowerarm_inter')
				if 'index1' in pbone.name:
					pbone.name = pbone.name.replace('c_index1', 'index_01')
				if 'index2' in pbone.name:
					pbone.name = pbone.name.replace('c_index2', 'index_02')
				if 'index3' in pbone.name:
					pbone.name = pbone.name.replace('c_index3', 'index_03')
				if 'middle1' in pbone.name:
					pbone.name = pbone.name.replace('c_middle1', 'middle_01')
				if 'middle2' in pbone.name:
					pbone.name = pbone.name.replace('c_middle2', 'middle_02')
				if 'middle3' in pbone.name:
					pbone.name = pbone.name.replace('c_middle3', 'middle_03')
				if 'ring1' in pbone.name:
					pbone.name = pbone.name.replace('c_ring1', 'ring_01')
				if 'ring2' in pbone.name:
					pbone.name = pbone.name.replace('c_ring2', 'ring_02')
				if 'ring3' in pbone.name:
					pbone.name = pbone.name.replace('c_ring3', 'ring_03')
				if 'pinky1' in pbone.name:
					pbone.name = pbone.name.replace('c_pinky1', 'pinky_01')
				if 'pinky2' in pbone.name:
					pbone.name = pbone.name.replace('c_pinky2', 'pinky_02')
				if 'pinky3' in pbone.name:
					pbone.name = pbone.name.replace('c_pinky3', 'pinky_03')
				if 'thumb1' in pbone.name:
					pbone.name = pbone.name.replace('c_thumb1', 'thumb_01')
				if 'thumb2' in pbone.name:
					pbone.name = pbone.name.replace('c_thumb2', 'thumb_02')
				if 'thumb3' in pbone.name:
					pbone.name = pbone.name.replace('c_thumb3', 'thumb_03')
				if 'neck' in pbone.name and not 'c_neck_01.x' in pbone.name:
					pbone.name = 'neck_01'
				if 'spine_01' in pbone.name:
					pbone.name = 'spine_01'
				if 'spine_02' in pbone.name:
					pbone.name = 'spine_02'
				if 'spine_03' in pbone.name:
					pbone.name = 'spine_03'
				if 'head' in pbone.name:
					pbone.name = 'head'
				if 'root' in pbone.name:
					pbone.name = 'pelvis'
			
				# TODO: must be handled accordingly with the mannequin axes orientations function
				#pbone.name = pbone.name.replace(".", "_")
				
		# restore the rig_fist action data path
		if action_fist != None:
			print("restoring rig fist action data path...")
			for i, fc in enumerate(action_fist.fcurves):
				fc.data_path = fc_save[i]
				
			print("restored.")	 
	
###########	 UI PANEL  ###################

######### FOR RETRO COMPATIBILITY ONLY! #########
class ARP_PT_auto_rig_GE_panel(bpy.types.Panel):
	
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "ARP" 
	bl_label = "Auto-Rig Pro: Export"
	bl_idname = "id_auto_rig_ge"
	bl_options = {'DEFAULT_CLOSED'}
	
	def draw(self, context):
	
		layout = self.layout
		object = context.active_object
		scene = context.scene
		
		#BUTTONS		
		layout.operator(ARP_OT_GE_export_fbx_panel.bl_idname, text="Export FBX...")
		#layout.operator(ARP_OT_GE_export_dae_panel.bl_idname, text="Export DAE...")
		layout.separator()
		layout.prop(scene, "arp_show_ge_debug")
		
		if context.scene.arp_show_ge_debug:
			layout.label(text="Tools below are for debugging")
			layout.label(text="purposes only:")		
			layout.separator()		
			col = layout.column(align=True)			
			col.operator("id.unset_humanoid_rig", text="Unset")			
			col.operator("id.set_mped_rig", text="Set Mped Rig")		
			col.operator("id.set_standard_scale", text="Blender Units")
			layout.separator()
	


					
				
def show_action_row(_col, _act):
		row2 = _col.row(align=True)
		row2.label(text=_act)						
		op = row2.operator('arp.delete_action', text='', icon = 'X')
		op.action_name = _act
		
		

def is_arp_armature(obj):
	if obj.type == "ARMATURE":
		if obj.data.bones.get("c_traj"):	
			return True

			
				
class ARP_OT_GE_export_fbx_panel(bpy.types.Operator, ExportHelper):
	"""Export the Auto-Rig Pro character in Fbx file format"""
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_label = "Auto-Rig Pro FBX Export"
	bl_idname = "id.arp_export_fbx_panel"	
	
	filename_ext = ".fbx"
	filter_glob : bpy.props.StringProperty(default="*.fbx", options={'HIDDEN'})
	message_final = ''
	non_armature_actions = []
	

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		scene = context.scene
		
		rig = None
		
		# Check if the armature is selected
		for obj in bpy.context.selected_objects:
			if is_arp_armature(obj):
				rig = obj					
		
		if rig == None:
			# maybe the object is active but not stored in 'selected_objects', weirdly
			if bpy.context.active_object:
				if is_arp_armature(bpy.context.active_object):
					rig = bpy.context.active_object
		
		if rig == None:
			layout.label(text="Select the Auto-Rig Pro armature")
			return
	
		#BUTTONS		
		col = layout.column(align=True)		
	
		row = col.row(align=True)
		row.prop(scene, "arp_engine_type", expand=True)		
		row = col.row(align=True)
		row.prop(scene, "arp_export_rig_type", expand=True)		
			
		col.separator()
		
		col.prop(scene, "arp_ge_sel_only")		
		
		box = layout.box()
		box.label(text="Rig Definition:")
		col = box.column(align=True)	
		
		
		if scene.arp_export_rig_type == 'generic':			
				
			row = col.row(align = True)
			row.prop(scene, 'arp_keep_bend_bones')
			row1 = row.row()
			
			if scene.arp_keep_bend_bones:
				row1.enabled = True
			else:
				row1.enabled = False
				
			row1.prop(scene,"arp_push_bend")
			
			box = layout.box()		
			box.label(text="Units:")
			col = box.column(align=True)		
			row = col.row(align=True)	
			row.prop(scene, "arp_units_x100")	
			row2 = row.row(align=True)		
			row2.enabled = scene.arp_units_x100			
			row2.prop(scene, "arp_push_drivers")			
				
			col.separator()
			
			box = layout.box()	
			box.label(text="Animations:")
			col = box.column(align=True)		
			row = col.row(align=True)
			row.prop(scene, "arp_bake_actions")			
			
			row = col.row(align=True)
			if scene.arp_bake_actions:
				row.enabled = True
			else:
				row.enabled = False
			row.prop(scene, "arp_export_name_actions", text="Only Containing:")
			
			row1 = row.row()
			if scene.arp_bake_actions and scene.arp_export_name_actions:
				row1.enabled = True
			else:
				row1.enabled = False
			row1.prop(scene, "arp_export_name_string", text="")
			row.prop(scene, "arp_see_actions", text="", icon="HIDE_OFF")
			if scene.arp_see_actions:
				if len(bpy.data.actions) > 0:
					for act in bpy.data.actions:					
						show_it = True
						if scene.arp_export_name_actions:
							if not scene.arp_export_name_string in act.name:
								show_it = False
						if show_it:							
							show_action_row(col, act.name)

			
			row = layout.row(align=True)
			if scene.arp_bake_actions:
				row.enabled = True
			else:
				row.enabled = False
			row.prop(scene, "arp_simplify_fac")	
			
			
		if scene.arp_export_rig_type == 'humanoid':		
		
			row = col.row(align=True)		
			row.prop(scene,"arp_keep_bend_bones")
			row1 = row.row()
			if scene.arp_keep_bend_bones:
				row1.enabled = True
			else:
				row1.enabled = False
				
			row1.prop(scene,"arp_push_bend")
			
			row = col.row(align=True)
			row.prop(scene,"arp_full_facial")
			
			if scene.arp_engine_type == "unreal":
				row.prop(scene,"arp_transfer_twist")
				
			
				col = box.column(align=True)								
				row = col.row(align=True)
				if context.scene.arp_transfer_twist:
					row.enabled = False
				else:
					row.enabled = True
				
				row.prop(scene, "arp_twist_fac", slider=True)		
			
			col = layout.column(align=True)
			row = col.row(align=True)		
			
			box = layout.box()
			box.label(text="Units:")
			col = box.column(align=True)
			row = col.row(align=True)	
			row.prop(scene, "arp_units_x100")
			row1 = row.row(align=True)		
			row1.enabled = scene.arp_units_x100			
			row1.prop(scene, "arp_push_drivers")
			
			if scene.arp_engine_type == "unreal":
				box = layout.box()
				box.label(text="Unreal Options:")	
				col = box.column(align=True)					
				
				row = col.row(align=True)				
				row.prop(scene, "arp_ue_root_motion")
				row.prop(scene, "arp_rename_for_ue")
				
				row = col.row(align=True)
				row.prop(scene, "arp_ue_ik")
				
				row1 = row.row(align=True)	
				
				if scene.arp_rename_for_ue:
					if rig.data.bones.get("c_spine_03.x"):
						row1.enabled = True
					else:
						row1.enabled = False						
				else:
					row1.enabled = False
				row1.prop(scene, "arp_mannequin_axes")
			
			box = layout.box()				
			box.label(text="Animations:")
			col = box.column(align=True)		
			row = col.row(align=True)
			row.prop(scene, "arp_bake_actions")
			
			
			row = col.row(align=True)
			if scene.arp_bake_actions:
				row.enabled = True
			else:
				row.enabled = False
			row.prop(scene, "arp_export_h_actions")	
			
			row = col.row(align=True)
			if scene.arp_bake_actions:
				row.enabled = True
			else:
				row.enabled = False
			row.prop(scene, "arp_export_name_actions", text="Only Containing:")
			
			
			row1 = row.row()
			if scene.arp_bake_actions and scene.arp_export_name_actions:
				row1.enabled = True
			else:
				row1.enabled = False
			row1.prop(scene, "arp_export_name_string", text="")
			row.prop(scene, "arp_see_actions", text="", icon="HIDE_OFF")
			if scene.arp_see_actions:
				if len(bpy.data.actions) > 0:
					for act in bpy.data.actions:					
						show_it = True
						if scene.arp_export_name_actions:
							if not scene.arp_export_name_string in act.name:
								show_it = False
						if show_it:					
							show_action_row(col, act.name)
			
			row = box.row(align=True)
			if scene.arp_bake_actions:
				row.enabled = True
			else:
				row.enabled = False
			row.prop(scene, "arp_simplify_fac")
			
		if scene.arp_export_rig_type == 'mped':			
			
			row = col.row(align=True)		
			row.prop(scene,"arp_keep_bend_bones")
			row1 = row.row()
			if scene.arp_keep_bend_bones:
				row1.enabled = True
			else:
				row1.enabled = False
				
			row1.prop(scene,"arp_push_bend")			
		
			row = col.row(align=True)		
			row.prop(scene,"arp_transfer_twist")			
			
		
			col = box.column(align=True)								
			row = col.row(align=True)
			if context.scene.arp_transfer_twist:
				row.enabled = False
			else:
				row.enabled = True
			
			row.prop(scene, "arp_twist_fac", slider=True)		
			
			box = layout.box()
			box.label(text="Units:")
			col = box.column(align=True)
			#col.separator()			
			row = col.row(align=True)	
			row.prop(scene, "arp_units_x100")
			row1 = row.row(align=True)		
			row1.enabled = scene.arp_units_x100			
			row1.prop(scene, "arp_push_drivers")
			
			if scene.arp_engine_type == "unreal":
				box = layout.box()
				box.label(text="Unreal Options:")		
				col = box.column(align=True)			
				row = col.row(align=True)				
				row.prop(scene, "arp_ue_root_motion")
				
			#col.separator()
			box = layout.box()
			box.label(text="Animations:")
			col = box.column(align=True)			
			row = col.row(align=True)
			row.prop(scene, "arp_bake_actions")
			
			
			row = col.row(align=True)
			if scene.arp_bake_actions:
				row.enabled = True
			else:
				row.enabled = False
			row.prop(scene, "arp_export_h_actions", text="Export Baked Actions Only")	
			
			row = col.row(align=True)
			if scene.arp_bake_actions:
				row.enabled = True
			else:
				row.enabled = False
			row.prop(scene, "arp_export_name_actions", text="Only Containing:")
			
			row1 = row.row()
			if scene.arp_bake_actions and scene.arp_export_name_actions:
				row1.enabled = True
			else:
				row1.enabled = False
			row1.prop(scene, "arp_export_name_string", text="")
			row.prop(scene, "arp_see_actions", text="", icon="HIDE_OFF")
			if scene.arp_see_actions:
				if len(bpy.data.actions) > 0:
					
					for act in bpy.data.actions:					
						show_it = True
						if scene.arp_export_name_actions:
							if not scene.arp_export_name_string in act.name:
								show_it = False
						if show_it:							
							show_action_row(col, act.name)
							
							
			col = box.column(align=True)
			if scene.arp_bake_actions:
				col.enabled = True
			else:
				col.enabled = False
			col.prop(scene, "arp_simplify_fac")
			
		#layout.separator()	
		box = layout.box()
		box.label(text="Misc:")
		col = box.column(align=True)		
		col.prop(scene, "arp_global_scale")	
		col = box.column(align=True)
		col.prop(scene, "arp_mesh_smooth_type")
		row = box.column().row()
		row.prop(scene, "arp_fix_fbx_rot")
		row.prop(scene, "arp_fix_fbx_matrix")
		col = box.column(align=True)
		col.prop(scene, "arp_init_fbx_rot")
		col.separator()
		col.label(text="Bones Axes:")
		col.prop(scene, "arp_bone_axis_primary_export", text="Primary")
		col.prop(scene, "arp_bone_axis_secondary_export", text="Secondary")
		
		
			
			
	def execute(self, context):
		return ARP_OT_export_fbx.execute(self, context)


class ARP_OT_GE_export_dae_panel(bpy.types.Operator, ExportHelper):
	"""Export the Auto-Rig Pro character in DAE file format"""
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_label = "Auto-Rig Pro DAE Export"
	bl_idname = "id.arp_export_dae_panel"	
	
	filename_ext = ".dae"
	filter_glob : bpy.props.StringProperty(default="*.dae", options={'HIDDEN'})
	message_final = ''
	non_armature_actions = []
	

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		scene = context.scene
		
		rig = None
		
		# Check if the armature is selected
		for obj in bpy.context.selected_objects:
			if is_arp_armature(obj):
				rig = obj					
		
		if rig == None:
			# maybe the object is active but not stored in 'selected_objects', weirdly
			if bpy.context.active_object:
				if is_arp_armature(bpy.context.active_object):
					rig = bpy.context.active_object
		
		if rig == None:
			layout.label(text="Select the Auto-Rig Pro armature")
			return
	
		#BUTTONS		
		col = layout.column(align=True)
		
		row = col.row(align=True)
		row.prop(scene, "arp_export_rig_type", expand=True)		
			
		col.separator()
		
		col.prop(scene, "arp_ge_sel_only")		
		
		box = layout.box()
		box.label(text="Rig Definition:")
		col = box.column(align=True)	
		
		
		if scene.arp_export_rig_type == 'generic':				
			row = col.row(align = True)
			row.prop(scene, 'arp_keep_bend_bones')
			row1 = row.row()
			
			if scene.arp_keep_bend_bones:
				row1.enabled = True
			else:
				row1.enabled = False
				
			row1.prop(scene,"arp_push_bend")
			
			box = layout.box()		
			box.label(text="Units:")
			col = box.column(align=True)		
			row = col.row(align=True)	
			row.prop(scene, "arp_units_x100")	
			row2 = row.row(align=True)		
			row2.enabled = scene.arp_units_x100			
			row2.prop(scene, "arp_push_drivers")			
				
			col.separator()
			
			box = layout.box()	
			box.label(text="Animations:")
			col = box.column(align=True)		
			row = col.row(align=True)
			row.prop(scene, "arp_bake_actions")			
			
			row = col.row(align=True)
			if scene.arp_bake_actions:
				row.enabled = True
			else:
				row.enabled = False
			row.prop(scene, "arp_export_name_actions", text="Only Containing:")
			
			row1 = row.row()
			if scene.arp_bake_actions and scene.arp_export_name_actions:
				row1.enabled = True
			else:
				row1.enabled = False
			row1.prop(scene, "arp_export_name_string", text="")
			row.prop(scene, "arp_see_actions", text="", icon="HIDE_OFF")
			if scene.arp_see_actions:
				if len(bpy.data.actions) > 0:
					for act in bpy.data.actions:					
						show_it = True
						if scene.arp_export_name_actions:
							if not scene.arp_export_name_string in act.name:
								show_it = False
						if show_it:							
							show_action_row(col, act.name)

			"""
			row = layout.row(align=True)
			if scene.arp_bake_actions:
				row.enabled = True
			else:
				row.enabled = False
			row.prop(scene, "arp_simplify_fac")	
			"""
			
		if scene.arp_export_rig_type == 'humanoid':		
		
			row = col.row(align=True)		
			row.prop(scene,"arp_keep_bend_bones")
			row1 = row.row()
			if scene.arp_keep_bend_bones:
				row1.enabled = True
			else:
				row1.enabled = False
				
			row1.prop(scene,"arp_push_bend")
			
			row = col.row(align=True)
			row.prop(scene,"arp_full_facial")			
			
			row.prop(scene,"arp_transfer_twist")			
		
			col = box.column(align=True)								
			row = col.row(align=True)
			if context.scene.arp_transfer_twist:
				row.enabled = False
			else:
				row.enabled = True
			
			row.prop(scene, "arp_twist_fac", slider=True)		
			
			col = layout.column(align=True)
			row = col.row(align=True)		
			
			box = layout.box()
			box.label(text="Units:")
			col = box.column(align=True)
			row = col.row(align=True)	
			row.prop(scene, "arp_units_x100")
			row1 = row.row(align=True)		
			row1.enabled = scene.arp_units_x100			
			row1.prop(scene, "arp_push_drivers")			
			
			box = layout.box()		
			col = box.column(align=True)		
			row = col.row(align=True)			
			row.prop(scene, "arp_ue_root_motion")			
			
			box = layout.box()				
			box.label(text="Animations:")
			col = box.column(align=True)		
			row = col.row(align=True)
			row.prop(scene, "arp_bake_actions")
			
			
			row = col.row(align=True)
			if scene.arp_bake_actions:
				row.enabled = True
			else:
				row.enabled = False
			row.prop(scene, "arp_export_h_actions")	
			
			row = col.row(align=True)
			if scene.arp_bake_actions:
				row.enabled = True
			else:
				row.enabled = False
			row.prop(scene, "arp_export_name_actions", text="Only Containing:")
			
			
			row1 = row.row()
			if scene.arp_bake_actions and scene.arp_export_name_actions:
				row1.enabled = True
			else:
				row1.enabled = False
			row1.prop(scene, "arp_export_name_string", text="")
			row.prop(scene, "arp_see_actions", text="", icon="HIDE_OFF")
			if scene.arp_see_actions:
				if len(bpy.data.actions) > 0:
					for act in bpy.data.actions:					
						show_it = True
						if scene.arp_export_name_actions:
							if not scene.arp_export_name_string in act.name:
								show_it = False
						if show_it:					
							show_action_row(col, act.name)
			
			"""
			row = box.row(align=True)
			if scene.arp_bake_actions:
				row.enabled = True
			else:
				row.enabled = False
			row.prop(scene, "arp_simplify_fac")
			"""
			
		if scene.arp_export_rig_type == 'mped':			
			
			row = col.row(align=True)		
			row.prop(scene,"arp_keep_bend_bones")
			row1 = row.row()
			if scene.arp_keep_bend_bones:
				row1.enabled = True
			else:
				row1.enabled = False
				
			row1.prop(scene,"arp_push_bend")			
		
			row = col.row(align=True)		
			row.prop(scene,"arp_transfer_twist")			
			
		
			col = box.column(align=True)								
			row = col.row(align=True)
			if context.scene.arp_transfer_twist:
				row.enabled = False
			else:
				row.enabled = True
			
			row.prop(scene, "arp_twist_fac", slider=True)		
			
			box = layout.box()
			box.label(text="Units:")
			col = box.column(align=True)
			
			row = col.row(align=True)	
			row.prop(scene, "arp_units_x100")
			row1 = row.row(align=True)		
			row1.enabled = scene.arp_units_x100			
			row1.prop(scene, "arp_push_drivers")			
			
			box = layout.box()				
			col = box.column(align=True)			
			row = col.row(align=True)				
			row.prop(scene, "arp_ue_root_motion")
				
			#col.separator()
			box = layout.box()
			box.label(text="Animations:")
			col = box.column(align=True)			
			row = col.row(align=True)
			row.prop(scene, "arp_bake_actions")
			
			
			row = col.row(align=True)
			if scene.arp_bake_actions:
				row.enabled = True
			else:
				row.enabled = False
			row.prop(scene, "arp_export_h_actions", text="Export Baked Actions Only")	
			
			row = col.row(align=True)
			if scene.arp_bake_actions:
				row.enabled = True
			else:
				row.enabled = False
			row.prop(scene, "arp_export_name_actions", text="Only Containing:")
			
			row1 = row.row()
			if scene.arp_bake_actions and scene.arp_export_name_actions:
				row1.enabled = True
			else:
				row1.enabled = False
			row1.prop(scene, "arp_export_name_string", text="")
			row.prop(scene, "arp_see_actions", text="", icon="HIDE_OFF")
			if scene.arp_see_actions:
				if len(bpy.data.actions) > 0:
					
					for act in bpy.data.actions:					
						show_it = True
						if scene.arp_export_name_actions:
							if not scene.arp_export_name_string in act.name:
								show_it = False
						if show_it:							
							show_action_row(col, act.name)
							
			"""				
			col = box.column(align=True)
			if scene.arp_bake_actions:
				col.enabled = True
			else:
				col.enabled = False
			col.prop(scene, "arp_simplify_fac")
			"""
					
			
			
	def execute(self, context):
		return ARP_OT_export_dae.execute(self, context)
 
		
##################	REGISTER  ##################

classes = (ARP_OT_delete_action, ARP_OT_set_standard_scale, ARP_OT_set_mped_rig, ARP_OT_unset_humanoid_rig, ARP_OT_export_fbx, ARP_OT_export_dae, ARP_OT_bind_humanoid, ARP_OT_unbind_humanoid, ARP_PT_auto_rig_GE_panel, ARP_OT_GE_export_fbx_panel, ARP_OT_GE_export_dae_panel)

def register():	  
	from bpy.utils import register_class
	
	for cls in classes:
		register_class(cls)	
	
	bpy.types.Scene.arp_export_rig_type = bpy.props.EnumProperty(items=(
		("generic", "Generic", "Generic rig type, export all deforming bones, and non-deforming bones when they are parent of deforming bones"),
		("humanoid", "Humanoid", "Humanoid rig type, simple bones hierarchy to ensure animation retargetting"),
		("mped", "Universal", "Universal rig type, simple bones hierarchy for any creature (dog, spider...)")
		), name = "Unity Rig Type Export", description="Rig type to export", default = "mped")
		
	bpy.types.Scene.arp_engine_type = bpy.props.EnumProperty(items=(
		("unity", "Unity", "Export to Unity"),
		("unreal", "Unreal Engine", "Export to Unreal Engine")
		), name = "Game Engine Type", description="Game engine to export the character", update=update_engine_type)
	
	bpy.types.Scene.arp_rename_for_ue = bpy.props.BoolProperty(name="Rename for UE", description="Rename bones according to Unreal Engine humanoid names convention", default=False)
	bpy.types.Scene.arp_transfer_twist = bpy.props.BoolProperty(name='Transfer Twist', description="Transfer the twist weights to the main groups.\nUncheck to export twist bones", default=True)
	bpy.types.Scene.arp_twist_fac = bpy.props.FloatProperty(name='Twist Amount', description="Influence of the twist bones. Generally 0.5 gives better results since game engines do not support dual quaternions", default = 0.5, min=0.0, max=1.0)
	bpy.types.Scene.arp_keep_bend_bones = bpy.props.BoolProperty(name='Advanced', description="Include the advanced bones, bend, breasts... Useful for cartoons rigs. \nWarning: may change a little the bend bones skin weights", default=False)
	bpy.types.Scene.arp_full_facial = bpy.props.BoolProperty(name='Full Facial', description="Include all facial bones, with skulls", default=False)
	bpy.types.Scene.arp_push_bend = bpy.props.BoolProperty(name='Push Additive', description="(Animated armature only) Push up the additive bend bones transforms to compensate the lower weights, since the additive armature modifier is not exported", default=True)
	bpy.types.Scene.arp_mannequin_axes = bpy.props.BoolProperty(name='Mannequin Axes', description="Set the bones orientation to match the Unreal mannequin orientations.\nRequires 4 spine bones.", default=False)
	bpy.types.Scene.arp_ue_ik = bpy.props.BoolProperty(name='Add IK Bones', description="Add the IK bones (ik_foot_root, ik_foot_l...)", default=False)
	bpy.types.Scene.arp_ue_root_motion = bpy.props.BoolProperty(name='Root Motion', description='The "c_traj" controller animation will be baked to the root node for root motion in Unreal', default=False)

	bpy.types.Scene.arp_export_h_actions = bpy.props.BoolProperty(name='Export Humanoid Actions Only', description='Export baked actions only', default=True)
	bpy.types.Scene.arp_export_name_actions = bpy.props.BoolProperty(name='Export Only Containing:', description='Export only actions with names containing the given text\ne.g. to export only actions associated to "Bob", name the actions "Bob_ActionName"' , default=False)
	bpy.types.Scene.arp_export_name_string = bpy.props.StringProperty(name="Text", description="Word/Text to be looked for in the actions name when exporting")
	bpy.types.Scene.arp_units_x100 = bpy.props.BoolProperty(name='Units x100', description='Export with a x100 unit scale factor. This ensures retargetting in Unreal Engine and the rig scale set to 1.0 in Unity' , default=True)
	bpy.types.Scene.arp_push_drivers = bpy.props.BoolProperty(name='Push Drivers', description='If Units x100 is checked, it will scale the shape keys drivers accordingly, dividing by 100.\nOnly check this if shape keys are driven by bones transforms, not direct properties.' , default=False)
	bpy.types.Scene.arp_bake_actions = bpy.props.BoolProperty(name='Bake Actions', description='If the character is animated, bake all actions' , default=True)
	
	bpy.types.Scene.arp_simplify_fac = bpy.props.FloatProperty(name="Simplify Factor", default = 0.05, min=0.0, max=100, description="Simplify factor to compress the animation data size. Lower value = higher quality, higher file size")
	bpy.types.Scene.arp_global_scale = bpy.props.FloatProperty(name="Global Scale", default = 1.0, description="Global scale applied")
	bpy.types.Scene.arp_mesh_smooth_type = bpy.props.EnumProperty(name="Smoothing", items=(('OFF', "Normals Only", "Export only normals instead of writing edge or face smoothing data"), ('FACE', "Face", "Write face smoothing"), ('EDGE', "Edge", "Write edge smoothing")), description="Export smoothing information (prefer 'Normals Only' option if your target importer understand split normals)",default='OFF')
	bpy.types.Scene.arp_bone_axis_primary_export = bpy.props.EnumProperty(name="Primary Bone Axis", items=(('X', "X Axis", ""), ('Y', "Y Axis", ""),('Z', "Z Axis", ""),('-X', "-X Axis", ""),('-Y', "-Y Axis", ""),('-Z', "-Z Axis", "")),default='Y')
	bpy.types.Scene.arp_bone_axis_secondary_export = bpy.props.EnumProperty(name="Secondary Bone Axis", items=(('X', "X Axis", ""), ('Y', "Y Axis", ""),('Z', "Z Axis", ""),('-X', "-X Axis", ""),('-Y', "-Y Axis", ""),('-Z', "-Z Axis", "")),default='X')
	bpy.types.Scene.arp_fix_fbx_rot = bpy.props.BoolProperty(name='Fix Fbx Bones Rotations', description='Fix the Fbx bones rotations issue by avoiding 180 angles between bones and bones parent, adding a slight offset in the bone rotation' , default=True)
	bpy.types.Scene.arp_fix_fbx_matrix = bpy.props.BoolProperty(name='Fix Bones Matrix', description='Fix the Fbx bones matrix issue' , default=True)
	bpy.types.Scene.arp_init_fbx_rot =	bpy.props.BoolProperty(name='Initialize Fbx Armature Rotation', description='Export armature with rotations value set to 0.\nWarning, experimental feature. May not work if the armature object itself is animated' , default = False)
	bpy.types.Scene.arp_ge_sel_only =	bpy.props.BoolProperty(name='Selection Only', description='Export only selected objects, instead of exporting all skinned meshes' , default = False)
	bpy.types.Scene.arp_see_actions =  bpy.props.BoolProperty(name='Display Actions', description='Show exported actions' , default = True)
	bpy.types.Scene.arp_show_ge_debug = bpy.props.BoolProperty(name="Show Debug Tools", description="Show Game Engine export debug tools", default=False)


def unregister():	
	from bpy.utils import unregister_class
	
	for cls in reversed(classes):
		unregister_class(cls)	
		
	del bpy.types.Scene.arp_export_rig_type
	del bpy.types.Scene.arp_engine_type
	del bpy.types.Scene.arp_rename_for_ue
	del bpy.types.Scene.arp_transfer_twist
	del bpy.types.Scene.arp_twist_fac
	del bpy.types.Scene.arp_keep_bend_bones
	del bpy.types.Scene.arp_full_facial
	del bpy.types.Scene.arp_push_bend
	del bpy.types.Scene.arp_mannequin_axes
	del bpy.types.Scene.arp_ue_ik
	del bpy.types.Scene.arp_ue_root_motion
	del bpy.types.Scene.arp_export_h_actions
	del bpy.types.Scene.arp_export_name_actions
	del bpy.types.Scene.arp_export_name_string
	del bpy.types.Scene.arp_units_x100
	del bpy.types.Scene.arp_push_drivers
	del bpy.types.Scene.arp_bake_actions
	del bpy.types.Scene.arp_simplify_fac
	del bpy.types.Scene.arp_global_scale
	del bpy.types.Scene.arp_mesh_smooth_type
	del bpy.types.Scene.arp_bone_axis_primary_export
	del bpy.types.Scene.arp_bone_axis_secondary_export
	del bpy.types.Scene.arp_fix_fbx_rot
	del bpy.types.Scene.arp_fix_fbx_matrix
	del bpy.types.Scene.arp_init_fbx_rot
	del bpy.types.Scene.arp_ge_sel_only
	del bpy.types.Scene.arp_see_actions
	del bpy.types.Scene.arp_show_ge_debug
		