import bpy, bmesh, math, re, operator, os, difflib
from math import degrees, pi, radians, ceil
from bpy.types import Panel, UIList
import mathutils
from mathutils import Vector, Euler, Matrix
#import numpy
from . import auto_rig_reset, auto_rig_datas



print ("\n Starting Auto-Rig Pro: Game Engine Exporter... \n")

bend_bones = ['c_ankle_bend', 'c_leg_bend_02', 'c_leg_bend_01', 'c_knee_bend', 'c_thigh_bend_02', 'c_thigh_bend_01', 'c_thigh_bend_contact', 'c_waist_bend.x', 'c_root_bend.x', 'c_spine_01_bend.x', 'c_spine_02_bend.x', 'c_shoulder_bend', 'c_arm_bend', 'c_elbow_bend', 'c_forearm_bend', 'c_wrist_bend', 'c_bot_bend', 'c_breast_01', 'c_breast_02']

bend_bones_add = ['c_ankle_bend', 'c_leg_bend_02', 'c_leg_bend_01', 'c_knee_bend', 'c_thigh_bend_02', 'c_thigh_bend_01', 'c_thigh_bend_contact', 'c_waist_bend.x', 'c_shoulder_bend', 'c_arm_bend', 'c_elbow_bend', 'c_forearm_bend', 'c_wrist_bend', 'c_bot_bend']

bend_bones_main = {'c_root_bend': 'root.x', 'c_spine_01_bend': 'spine_01.x', 'c_spine_02_bend': 'spine_02.x', 'c_bot_bend':'thigh_stretch', 'c_breast_01': 'spine_02.x', 'c_breast_02': 'spine_02.x'}	

additional_facial_list = ['c_teeth_bot', 'c_teeth_top', 'c_lips_bot', 'c_lips_bot_01', 'c_lips_top', 'c_lips_top_01', 'c_chin_01', 'c_chin_02', 'c_cheek_smile', 'c_nose_03', 'c_nose_01', 'c_nose_02', 'c_cheek_inflate', 'c_eye_ref_track', 'tong_03', 'tong_02', 'tong_01', 'c_skull_01', 'c_skull_02', 'c_skull_03']


##########################	CLASSES	 ##########################
class bake_all(bpy.types.Operator):
	  
	#tooltip
	""" If the character is animated, bake all actions to the humanoid armature, outputs actions starting with "h_" (humanoid) """
	
	bl_idname = "id.bake_all"
	bl_label = "bake_all"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		humanoid_loaded = False
		try:
			bpy.data.objects['rig_humanoid']
			humanoid_loaded = True
		except:
			pass
			
		if context.active_object != None:
			#if bpy.context.scene.rename_for_ue == False:
			if humanoid_loaded:
				if len(bpy.data.objects['rig_humanoid'].keys()) > 0:
					if 'set' in bpy.data.objects['rig_humanoid'].keys():
						if bpy.data.objects['rig_humanoid']['set'] == 1:
							return True
				else:
					return True
			

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:
			try:
				bpy.data.objects['rig']
			except:
				self.report({'ERROR'}, "Append the Auto-Rig Pro armature in the scene first.")
				return {'FINISHED'}
				
			#save current mode
			active_obj = bpy.context.object
			current_mode = context.mode					
			#bpy.ops.object.mode_set(mode='EDIT')  
			
			_bake_all(context)
			
			
			 #restore saved mode	
			  
			try: 
				
				bpy.ops.object.mode_set(mode=current_mode)
				set_active_object(active_obj.name)
				
				self.report({'INFO'}, "Done.")
			except:
				pass
	 
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo	   
		
		return {'FINISHED'}

class set_standard_scale(bpy.types.Operator):
	  
	#tooltip
	"""Restore the default Blender units"""
	
	bl_idname = "id.set_standard_scale"
	bl_label = "set_standard_scale"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		if context.active_object != None:
			if bpy.context.scene.rename_for_ue == False:
				unit_system = bpy.context.scene.unit_settings			
				if unit_system.system != 'None':
					if unit_system.scale_length > 0.01-0.0003 and unit_system.scale_length < 0.01+0.0003:
						return True

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:
			try:
				bpy.data.objects['rig']
			except:
				self.report({'ERROR'}, "Append the Auto-Rig Pro armature in the scene first.")
				return {'FINISHED'}
				
			#save current mode
			active_obj = bpy.context.object
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
			context.user_preferences.edit.use_global_undo = use_global_undo	   
		
		return {'FINISHED'}

class set_unreal_scale(bpy.types.Operator):
	  
	#tooltip
	"""Set the units ready for Unreal Engine (ensure retargetting functions)"""
	
	bl_idname = "id.set_unreal_scale"
	bl_label = "set_unreal_scale"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		if context.active_object != None:
			if bpy.context.scene.rename_for_ue == False:
				unit_system = bpy.context.scene.unit_settings		
				if unit_system.system == 'NONE' or (unit_system.system != 'NONE' and (unit_system.scale_length > 1.0-0.0003 and unit_system.scale_length < 1.0+0.0003)):
					return True
					
	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:
			"""
			if context.object.type != 'MESH':
				self.report({'ERROR'}, "Select the body mesh")
				return{'FINISHED'}
			"""
			try:
				bpy.data.objects['rig']
			except:
				self.report({'ERROR'}, "Append the Auto-Rig Pro armature in the scene first.")
				return {'FINISHED'}
				
			#save current mode
			active_obj = bpy.context.object
			current_mode = context.mode					
			#bpy.ops.object.mode_set(mode='EDIT')  
			
			_set_unreal_scale(self)	   
			
			 #restore saved mode	
			  
			try: 
				
				bpy.ops.object.mode_set(mode=current_mode)
				set_active_object(active_obj.name)
				self.report({'INFO'}, "Done.")
			except:
				pass
	 
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo	   
		
		return {'FINISHED'}

class setup_generic(bpy.types.Operator):
	  
	#tooltip
	"""Make sure the character mesh in binded to the Auto-Rig Pro armature \nThen select the mesh and click to setup the rig"""
	
	bl_idname = "id.setup_generic"
	bl_label = "setup_generic"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None)

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:
			if context.object.type != 'MESH':
				self.report({'ERROR'}, "Select the body mesh")
				return{'FINISHED'}
			
			#save current mode
			body_obj = bpy.context.object
			current_mode = context.mode					
			current_frame = bpy.context.scene.frame_current#save current frame	
			
			_setup_generic()	   
			
			 #restore saved mode			  
			try:		
				#restore current frame
				bpy.context.scene.frame_current = current_frame
				bpy.context.scene.frame_set(bpy.context.scene.frame_current)#debug	
				
				bpy.ops.object.mode_set(mode=current_mode)
				set_active_object(body_obj.name)
				self.report({'INFO'}, "Done.")
			except:
				pass
	 
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo	   
		
		return {'FINISHED'}
		
class set_humanoid_rig(bpy.types.Operator):
	  
	#tooltip
	"""Create and set the Humanoid armature as the deforming armature """
	
	bl_idname = "id.set_humanoid_rig"
	bl_label = "set_humanoid_rig"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		humanoid_loaded = False
		try:
			bpy.data.objects['rig_humanoid']
			humanoid_loaded = True
		except:
			pass
			
		if context.active_object != None:
			
			if humanoid_loaded:
				if bpy.context.scene.rename_for_ue == False:
					if len(bpy.data.objects['rig_humanoid'].keys()) > 0:
						if 'set' in bpy.data.objects['rig_humanoid'].keys():
							if bpy.data.objects['rig_humanoid']['set'] == 0:
								return True
					else:
						return True
			else:
				return True

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		
		try:
		
			
			try:
				bpy.data.objects["rig"]
			except:
				self.report({'ERROR'}, "Please append the Auto-Rig Pro armature in the scene.")
				return{'FINISHED'} 
		   
			#save current mode			 
			current_mode = context.mode
			bpy.ops.object.mode_set(mode='OBJECT')	  
			current_obj = bpy.context.active_object
			current_frame = bpy.context.scene.frame_current#save current frame	
			
			_set_humanoid_rig()
			
			#restore active object 
			try:
				bpy.ops.object.mode_set(mode='OBJECT')
				set_active_object(current_obj.name)			   
				#restore saved mode					
				bpy.ops.object.mode_set(mode=current_mode)

				#restore current frame
				bpy.context.scene.frame_current = current_frame
				bpy.context.scene.frame_set(bpy.context.scene.frame_current)#debug	
				
				self.report({'INFO'}, "Done.")
			except:
				pass
	 
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo	   
		
		return {'FINISHED'}
		
class unset_humanoid_rig(bpy.types.Operator):
	  
	#tooltip
	""" Set the Auto-Rig Pro armature as the deforming armature """
	
	bl_idname = "id.unset_humanoid_rig"
	bl_label = "unset_humanoid_rig"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		humanoid_loaded = False
		try:
			bpy.data.objects['rig_humanoid']
			humanoid_loaded = True
		except:
			pass
			
		if context.active_object != None:
			if bpy.context.scene.rename_for_ue == False:
				if humanoid_loaded:
					if len(bpy.data.objects['rig_humanoid'].keys()) > 0:
						if 'set' in bpy.data.objects['rig_humanoid'].keys():
							if bpy.data.objects['rig_humanoid']['set'] == 1:
								return True
					else:
						return True
				else:
					return False

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		
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
			
			_unset_humanoid_rig()
			
			#restore active object 
			try:
				#restore current frame
				bpy.context.scene.frame_current = current_frame
				bpy.context.scene.frame_set(bpy.context.scene.frame_current)#debug	
			
				bpy.ops.object.mode_set(mode='OBJECT')
				set_active_object(current_obj.name)			   
				#restore saved mode					
				bpy.ops.object.mode_set(mode=current_mode)				 
				self.report({'INFO'}, "Done.")
			except:
				pass
	 
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo	   
		
		return {'FINISHED'}
		
class export_fbx(bpy.types.Operator):
	""" Export character in .fbx file format """
	bl_idname = "id.export_fbx"
	bl_label = "Export .fbx"

	filepath = bpy.props.StringProperty(subtype="FILE_PATH", default='fbx')
	type = bpy.props.StringProperty(name="Type")
	scale = bpy.props.FloatProperty(name="Scale", default=1.0)
	
	def execute(self, context):		  
		_select_exportable(self.type, self)
		
		#add extension
		if self.filepath[-4:] != ".fbx":
			self.filepath += ".fbx"
		
		bpy.ops.export_scene.fbx(filepath=self.filepath, use_selection = True, global_scale = self.scale, use_mesh_modifiers=True, use_armature_deform_only = True, add_leaf_bones=False, apply_unit_scale = True)

		return {'FINISHED'}

	def invoke(self, context, event):
		#self.filepath += 'char.fbx'
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

		
class select_exportable(bpy.types.Operator):
	  
	#tooltip
	"""Auto select the exportable armature and linked meshes to export """
	
	bl_idname = "id.select_exportable"
	bl_label = "select_exportable"
	bl_options = {'UNDO'}	
	
	type = bpy.props.StringProperty(name="Type")
	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None)

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		
		#save current mode			 
		current_mode = context.mode 
		
 
		_select_exportable(type)
			
		
		#restore saved mode
		try:				
			bpy.ops.object.mode_set(mode=current_mode)			 
		   
		except:
			pass
	 
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo	  
		
		return {'FINISHED'}
		
		
class bind_humanoid(bpy.types.Operator):
	  
	#tooltip
	""" Bind the Humanoid armature to the Auto-Rig Pro armature. """
	
	bl_idname = "id.bind_humanoid"
	bl_label = "bind_humanoid"
	bl_options = {'UNDO'}	

	
	@classmethod
	def poll(cls, context):
		humanoid_loaded = False
		try:
			bpy.data.objects['rig_humanoid']
			humanoid_loaded = True
		except:
			pass
			
		if context.active_object != None:
			if bpy.context.scene.rename_for_ue == False:
				if humanoid_loaded:		
					if len(bpy.data.objects['rig_humanoid'].keys()) > 0:
						if 'set' in bpy.data.objects['rig_humanoid'].keys():
							if bpy.data.objects['rig_humanoid']['binded'] == 0 and bpy.data.objects['rig_humanoid']['set'] == 1:						
								return True
							else:
								return False	
					else:
						return True
				else:
					return False
				

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		
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
		current_obj = context.object
		
		_constraint_rig(False)
		
		#restore state
		try:	 
			set_active_object(current_obj.name)
			bpy.ops.object.mode_set(mode=current_mode)			 
		   
		except:
			pass
			
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo	   
		
		return {'FINISHED'} 

class unbind_humanoid(bpy.types.Operator):
	  
	#tooltip
	""" Unbind the Humanoid armature to the Auto-Rig Pro armature. \nUnbind when exporting multiple baked actions. Bind before baking an action. """
	
	bl_idname = "id.unbind_humanoid"
	bl_label = "unbind_humanoid"
	bl_options = {'UNDO'}	

	
	@classmethod
	def poll(cls, context):
		humanoid_loaded = False
		try:
			bpy.data.objects['rig_humanoid']
			humanoid_loaded = True
		except:
			pass
			
		if context.active_object != None:
			if bpy.context.scene.rename_for_ue == False:
				if humanoid_loaded:	
					if len(bpy.data.objects['rig_humanoid'].keys()) > 0:
						if 'set' in bpy.data.objects['rig_humanoid'].keys():
							if bpy.data.objects['rig_humanoid']['binded'] == 1 and bpy.data.objects['rig_humanoid']['set'] == 1:
								return True
							else:
								return False	
					else:
						return False
				else:
					return False
				

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		
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
		current_obj = context.object
		
		_constraint_rig(True)
		
		#restore state
		try:	 
			set_active_object(current_obj.name)
			bpy.ops.object.mode_set(mode=current_mode)			 
		   
		except:
			pass
			
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo	   
		
		return {'FINISHED'} 
		
 
	  
		
############ FUNCTIONS ##############################################################
def get_edit_bone(name):
	try:
		return bpy.context.object.data.edit_bones[name]
	except:
		return None
	
def set_active_object(object_name):
	 bpy.context.scene.objects.active = bpy.data.objects[object_name]
	 bpy.data.objects[object_name].select = True

def get_pose_bone(name):
	return bpy.context.object.pose.bones[name]
	
def set_inverse_child(b):
				pbone = bpy.context.active_object.pose.bones[b]
				context_copy = bpy.context.copy()
				context_copy["constraint"] = pbone.constraints["Child Of"]
				bpy.context.active_object.data.bones.active = pbone.bone
				try:
					bpy.ops.constraint.childof_set_inverse(context_copy, constraint="Child Of", owner='BONE')	
				except:
					print('Invalid bone constraint', b)
					
					
def _bake_all(context):

	arp_armature = bpy.data.objects['rig']
	humanoid_armature = bpy.data.objects['rig_humanoid']
	_action = arp_armature.animation_data.action
	actions = bpy.data.actions
	
	for action in actions:
		if action.name[:2] != 'h_':#if not a baked action
			frame_range =action.frame_range
			arp_armature.animation_data.action = action		
			#make sure it's binded
			_constraint_rig(False)
			bpy.ops.object.mode_set(mode='POSE')
			bpy.ops.pose.select_all(action='SELECT')
			bpy.ops.nla.bake(frame_start=frame_range[0], frame_end=frame_range[1], visual_keying=True, bake_types={'POSE'})
			humanoid_armature.animation_data.action.name = 'h_' + action.name
			humanoid_armature.animation_data.action.use_fake_user = True


	#unbind the rig
	_constraint_rig(True)
					
					
def _select_exportable(export_type, self):
	if export_type == 'generic':
		try:
			arp_armature = bpy.data.objects['rig']
		except:
			self.report({'ERROR'}, "Please append the Auto-Rig Pro armature in the scene.")
			return{'FINISHED'} 
		
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		
		# select meshes with ARP armature modifier
		for obj in bpy.data.objects:
			if obj.type == 'MESH':
				try:
					for modif in obj.modifiers:
						if modif.type == 'ARMATURE':
							if modif.object == arp_armature:								  
								obj.select = True
					
				except:
					pass
		# select ARP armature
		set_active_object("rig")
		
	if export_type == 'humanoid':
		try:
			humanoid_armature = bpy.data.objects['rig_humanoid']
		except:
			self.report({'ERROR'}, "Please append the Humanoid armature in the scene.")
			return{'FINISHED'} 
		
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		
		# select meshes with Humanoid armature modifier
		for obj in bpy.data.objects:
			if obj.type == 'MESH':
				try:
					for modif in obj.modifiers:
						if modif.type == 'ARMATURE':
							if modif.object == humanoid_armature:								   
								obj.select = True							
					
				except:
					pass
					
		#check if the meshes have shape keys and disable subsurf if any before export
		for obj in bpy.context.selected_objects:		
			if obj.type == 'MESH':
				if obj.data.shape_keys != None:
					print('\nMesh', obj.name, 'have shape keys, disable subsurf modifiers for export')
					if len(obj.data.shape_keys.key_blocks) > 0:					
						if len(obj.modifiers) > 0:
							for modif in obj.modifiers:
								if modif.type == 'SUBSURF':
									modif.show_render = False
					
		# select Humanoid armature
		bpy.data.objects["rig_humanoid"].hide = False
		set_active_object("rig_humanoid") 
	
	
def _set_standard_scale(self):

	unit_system = bpy.context.scene.unit_settings
	current_frame = bpy.context.scene.frame_current#save current frame
	current_cursor_mode = bpy.context.space_data.pivot_point
	bpy.context.scene.tool_settings.use_keyframe_insert_auto = False
	
	if unit_system.system != 'None':
		if unit_system.scale_length > 0.01-0.0003 and unit_system.scale_length < 0.01+0.0003:
		
			humanoid_set = False			
			rig = bpy.data.objects['rig']
			
			rig_scale = rig.scale[0]
		
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
				rig_add.hide = False
			
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
				_action = bpy.context.object.animation_data.action

				if bpy.context.object.animation_data.action == None:
					_action = bpy.context.blend_data.actions.new('Action') 
					bpy.context.object.animation_data.action = _action
					
				bpy.ops.pose.select_all(action='DESELECT')

				#Check if the controller is keyed
				for pbone in bpy.context.object.pose.bones:
					if pbone.name[:2] == 'c_' and not 'proxy' in pbone.name:
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
					
				for pbone in bpy.context.object.pose.bones:
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
				
				bpy.context.space_data.cursor_location = [0,0,0]
				bpy.context.space_data.pivot_point = 'CURSOR'
				
				for mesh in meshes:				   
					set_active_object(mesh.name)
					
				set_active_object(rig.name)
				set_active_object(rig_add.name)
				bpy.ops.transform.resize(value=(0.01, 0.01, 0.01), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
								
				#apply scale			
				bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
			 
				bpy.ops.object.select_all(action='DESELECT')
				set_active_object(rig.name)
				
				
				bpy.ops.object.mode_set(mode='POSE')
				
					#Active all layers
					#save current displayed layers
				_layers = bpy.context.object.data.layers
				
				for i in range(0,32):
					bpy.context.object.data.layers[i] = True
					
				#reset child of constraints				   
				for pbone in bpy.context.object.pose.bones:
					if 'hand' in pbone.name or 'foot' in pbone.name:
						for cns in pbone.constraints:
							if 'Child Of' in cns.name:
								set_inverse_child(pbone.name)				
				
								
				#scale curves			   
				for action in bpy.data.actions:
					for fcurve in action.fcurves:
						if 'location' in fcurve.data_path:
							for point in fcurve.keyframe_points:					
								point.co[1] *= 0.01*rig_scale
								point.handle_left[1] *= 0.01*rig_scale
								point.handle_right[1] *= 0.01*rig_scale
				
				#display layers 16, 0, 1 only	
				_layers = bpy.context.object.data.layers
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
					bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
			
				#set the camera clip
				bpy.context.space_data.clip_end *= 0.01
				
				#restore cursor pivot_point
				bpy.context.space_data.pivot_point = current_cursor_mode
								
				
				#refresh
				bpy.context.scene.frame_current = current_frame
				bpy.context.scene.frame_set(bpy.context.scene.frame_current)#debug	 
				
				#RESET STRETCHES -- WARNING only works at the end of the process??
				set_active_object(rig.name)
					#store active pose			
				bpy.ops.object.mode_set(mode='POSE')
				bpy.ops.pose.select_all(action='SELECT')
				bpy.ops.pose.copy()
					#need to reset the pose
				auto_rig_reset.reset_all()
					#reset stretches
				for pbone in bpy.context.object.pose.bones:
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
			   
				rig_add.hide = True
				
				print('Done	 setting standard units')
	
			else:
				self.report({'ERROR'}, "No skinned mesh found, units haven't been changed.")
		else:
			self.report({'ERROR'}, "Blender units already set.")
			
			
			
def _set_unreal_scale(self):
	
	current_frame = bpy.context.scene.frame_current#save current frame
	unit_system = bpy.context.scene.unit_settings
	current_cursor_mode = bpy.context.space_data.pivot_point
	bpy.context.scene.tool_settings.use_keyframe_insert_auto = False

	if unit_system.system == 'NONE' or (unit_system.system != 'NONE' and (unit_system.scale_length > 1.0-0.0003 and unit_system.scale_length < 1.0+0.0003)):
	   
		humanoid_set = False
		
		rig = bpy.data.objects['rig']
		
		rig_scale = rig.scale[0]
		
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
			bpy.data.objects['rig_humanoid'].scale *= 100
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

									
		#Start changing units
		if len(meshes) > 0:		
			rig_add = bpy.data.objects['rig_add']
			rig_add.hide = False
			
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
			#Check if an action is linked
			_action = bpy.context.object.animation_data.action

			if bpy.context.object.animation_data.action == None:
				_action = bpy.context.blend_data.actions.new('Action') 
				bpy.context.object.animation_data.action = _action
				
			bpy.ops.pose.select_all(action='DESELECT')
			
				#remove scale keyframe on the armature if any
			for fcurve in _action.fcurves:
				if fcurve.data_path == 'scale':				
					print('found scale')
					_action.fcurves.remove(fcurve)
			
			#Check if the controller is keyed
			for pbone in bpy.context.object.pose.bones:
				if pbone.name[:2] == 'c_' and not 'proxy' in pbone.name:
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
			for pbone in bpy.context.object.pose.bones:
				if len(pbone.constraints) > 0:
					for cns in pbone.constraints:
						if cns.type == 'TRANSFORM':
						
							cns.from_min_x *= 100*bpy.context.object.scale[0]
							cns.from_max_x *= 100*bpy.context.object.scale[0]
							cns.from_min_y *= 100*bpy.context.object.scale[0]
							cns.from_max_y *= 100*bpy.context.object.scale[0]
							cns.from_min_z *= 100*bpy.context.object.scale[0]
							cns.from_max_z *= 100*bpy.context.object.scale[0]
				
		
			
			bpy.ops.object.mode_set(mode='OBJECT')
			
			#Scale meshes
				#set rig_add scale same as rig
			rig_add.scale = rig.scale
			
			bpy.context.space_data.cursor_location = [0,0,0]
			bpy.context.space_data.pivot_point = 'CURSOR'
			
			for mesh in meshes:
				set_active_object(mesh.name)				
				
			set_active_object(rig.name)			
			set_active_object(rig_add.name)
			
			bpy.ops.transform.resize(value=(100, 100, 100), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
			
			#remove scaling keys if any
			
			
			#apply scale			
			bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
			
			
			bpy.ops.object.select_all(action='DESELECT')
			set_active_object(rig.name)			
			
			bpy.ops.object.mode_set(mode='POSE')
		
						
				#Active all layers
				#save current displayed layers
			_layers = bpy.context.object.data.layers
			
			for i in range(0,32):
				bpy.context.object.data.layers[i] = True
			
			#scale curves			 
			for action in bpy.data.actions:
				for fcurve in action.fcurves:
					if 'location' in fcurve.data_path:
						for point in fcurve.keyframe_points:					
							point.co[1] *= 100*rig_scale
							point.handle_left[1] *= 100*rig_scale
							point.handle_right[1] *= 100*rig_scale
			
	 
			#reset child of constraints
			for pbone in bpy.context.object.pose.bones:
				if 'hand' in pbone.name or 'foot' in pbone.name:
					for cns in pbone.constraints:
						if 'Child Of' in cns.name:
							set_inverse_child(pbone.name)
			
			
			
			#display layers 16, 0, 1 only	
			_layers = bpy.context.object.data.layers
				#must enabling one before disabling others
			_layers[16] = True	
			for i in range(0,32):
				if i != 16:
					_layers[i] = False 
			_layers[0] = True
			_layers[1] = True	
			
			bpy.ops.object.mode_set(mode='OBJECT') 
			
			#unit system
			bpy.context.scene.unit_settings.system = 'METRIC'
			bpy.context.scene.unit_settings.scale_length = 0.01
			
			
						
			#apply humanoid scale		   
			if humanoid_set:
				set_active_object('rig_humanoid')
				bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
				
			#set the camera clip
			bpy.context.space_data.clip_end *= 100
			
			#restore cursor pivot_point
			bpy.context.space_data.pivot_point = current_cursor_mode
			
			#refresh
			bpy.context.scene.frame_current = current_frame
			bpy.context.scene.frame_set(bpy.context.scene.frame_current)#debug	 
			
			#RESET STRETCHES -- WARNING only works at the end of the process??
			set_active_object(rig.name)
				#store active pose			
			bpy.ops.object.mode_set(mode='POSE')
			bpy.ops.pose.select_all(action='SELECT')
			bpy.ops.pose.copy()
				#need to reset the pose
			auto_rig_reset.reset_all()
				#reset stretches
			for pbone in bpy.context.object.pose.bones:
				try:							
					pbone.constraints["Stretch To"].rest_length = 0.0					
				except:
					pass
					
				#restore the pose
			bpy.ops.pose.paste(flipped=False)
		
					
			#CENTER VIEW
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.select_all(action='DESELECT')
			for mesh in meshes:
				set_active_object(mesh.name)		
			bpy.ops.view3d.view_selected(use_all_regions=False)
			
			#UI Cam scale
			bpy.data.objects['cam_ui'].data.ortho_scale *= 100
			
			rig_add.hide = True
			
			print('Done	 setting units for Unreal Engine')

		else:
			self.report({'ERROR'}, "No skinned mesh found, units haven't been changed.")
   
	else:
		self.report({'ERROR'}, "UE units already set.")
		

def _setup_generic():
	scene = bpy.context.scene
	body_obj = bpy.context.object
	arp_armature = bpy.data.objects['rig']	
	
	
	# move cs_grp layer
	bpy.data.objects["cs_grp"].layers[19] = True
	bpy.data.objects["cs_grp"].layers[0] = False
	
	#delete rig_add modifier
	try:
		bpy.ops.object.modifier_remove(modifier="rig_add")
	except:
		pass
	# delete rig_add
	"""
	try:
		bpy.ops.object.select_all(action='DESELECT')
		bpy.data.objects["rig_add"].hide = False	
		bpy.data.objects["rig_add"].hide_select = False
		bpy.data.objects["rig_add"].select = True	 
		bpy.ops.object.delete()
	except:
		pass
	"""
	
	# delete unused vgroups	  
	try:
		vgroups = bpy.context.object.vertex_groups

		for x in vgroups:
			if 'c_eyelid_top_' in x.name or 'c_eyelid_bot_' in x.name or 'c_eyelid_corner_' in x.name:			  
				bpy.ops.object.vertex_group_set_active(group=x.name)
				bpy.ops.object.vertex_group_remove()
	except:
		pass
		
	sides = ['.l', '.r']
	#Keep bend bones?
	if scene.keep_bend_bones:
		for bone in bend_bones:
			if bone[-2:] != '.x':
				for side in sides:
					arp_armature.data.bones[bone+side].use_deform = True		
			else:
				arp_armature.data.bones[bone].use_deform = True		

		#push up the bend bones?
		if scene.push_bend:
			_action = arp_armature.animation_data.action
		
			for fcurve in _action.fcurves:	   
				for bbone in bend_bones_add:
					if bbone in fcurve.data_path:#operate only on bend bone add fcurves
						
						for key in fcurve.keyframe_points:
							if not 'scale' in fcurve.data_path:
								key.co[1] *= 2
								key.handle_left[1] *= 2
								key.handle_right[1] *= 2
								
							else:
								key.co[1] = -1 + (key.co[1]) * 2
								key.handle_left[1] = -1 + (key.handle_left[1]) * 2
								key.handle_right[1] = -1 + (key.handle_right[1]) * 2
						break
							
		

	
def _set_humanoid_rig():
	scene = bpy.context.scene
	sides = ['.l', '.r']
	
	#append it
	try:
		bpy.data.objects["rig_humanoid"]				
	except:
		
		#Append the humanoid armature in the scene
		addon_directory = os.path.dirname(os.path.abspath(__file__))
		filepath = addon_directory + "/humanoid.blend"
		
		#load the objects data in the file
		with bpy.data.libraries.load(filepath) as (data_from, data_to):
			data_to.objects = data_from.objects
		
		#add the objects in the scene
		for obj in data_to.objects:
			if obj is not None:
				bpy.context.scene.objects.link(obj)

	#get the armatures	 
	bpy.ops.object.mode_set(mode='OBJECT')	  
		
	humanoid_armature = bpy.data.objects['rig_humanoid']
	arp_armature = bpy.data.objects['rig']

	#set the scale	  
	humanoid_armature.scale = arp_armature.scale
	set_active_object(humanoid_armature.name)
	
	hide_state = humanoid_armature.hide
	humanoid_armature.hide = False
	
	
	#Spine bones amount
	
	# need 4 spine bones
	if bpy.data.objects['rig'].rig_spine_count == 4:
		set_active_object("rig_humanoid")
		bpy.ops.object.mode_set(mode='EDIT')
		if get_edit_bone('spine_03.x') == None:
			bpy.ops.armature.select_all(action='DESELECT')
			bpy.context.object.data.edit_bones.active = get_edit_bone('spine_02.x')
			bpy.ops.armature.subdivide()
			get_edit_bone('spine_02.x.001').name = 'spine_03.x'
			bpy.ops.object.mode_set(mode='POSE')
			bpy.ops.pose.select_all(action='DESELECT')
			get_pose_bone('spine_03.x').bone.select = True
			get_pose_bone('spine_02.x').bone.select = True			 
			#copy constraints
			bpy.ops.pose.constraints_copy()

			get_pose_bone('spine_03.x').constraints[0].subtarget = 'c_spine_03.x'
	
			
	if bpy.data.objects['rig'].rig_spine_count == 3:
		set_active_object("rig_humanoid")
		bpy.ops.object.mode_set(mode='EDIT')
		if get_edit_bone('spine_03.x') != None:
			bpy.ops.armature.select_all(action='DESELECT')			 
			bpy.context.object.data.edit_bones.active = get_edit_bone('spine_03.x')
			bpy.ops.armature.delete()
			get_edit_bone('spine_02.x').tail = get_edit_bone('neck.x').head 

	bpy.ops.object.mode_set(mode='EDIT')  
	
	def is_bend_bone(bone):		
		for bbone in bend_bones:
			if bbone in bone:
				return True
				break				
		
	
	#Disable X Mirror
	bpy.context.object.data.use_mirror_x = False
	
	#Clear additional bones before creating them
	for edit_bone in bpy.context.object.data.edit_bones:
		if edit_bone.name[:3] == 'cc_' or is_bend_bone(edit_bone.name) or edit_bone.name[:-2] in additional_facial_list:
			 bpy.context.object.data.edit_bones.remove(edit_bone)	
		 
	#Delete default facial if not set
	default_facial_bones = ['c_eyebrow_full', 'c_eyebrow_01_end', 'c_eyebrow_01', 'c_eyebrow_02', 'c_eyebrow_03', 'c_eye', 'c_eye_offset', 'eyelid_bot', 'eyelid_top', 'c_jawbone.x', 'c_lips_smile', 'c_eye_target']
	if not arp_armature.rig_facial:		
		for bone in default_facial_bones:
			if bone[-2:] != '.x':
				for side in sides:
					bpy.context.object.data.edit_bones.remove(bpy.context.object.data.edit_bones[bone+side])	
			else:
				bpy.context.object.data.edit_bones.remove(bpy.context.object.data.edit_bones[bone])	
					
				
			
	
	bpy.ops.object.mode_set(mode='POSE')  
	bpy.ops.pose.select_all(action='SELECT')
	selected_bones = bpy.context.selected_pose_bones
	
	#Create bones transform dict
	bones_dict = {} 
	
	for pbone in selected_bones:		
		bpy.context.object.data.bones.active= pbone.bone  
		
		#enable constraints
		for cns in pbone.constraints:		
			cns.target = bpy.data.objects[arp_armature.name]
			
			#store in dict
			if cns.name == 'Copy Transforms':
				bones_dict[pbone.name] = (pbone.name, [0.0,0.0,0.0], [0.0,0.0,0.0], 0.0, True)
				cns.subtarget = pbone.name
				
	
	
	#Define Humanoid rest pose from ARP armature		
	bpy.ops.object.mode_set(mode='OBJECT')
	set_active_object(arp_armature.name)
	bpy.ops.object.mode_set(mode='POSE')
	
		#lock the root translation because no stretch allowed for Humanoid
	for i in range(0,3):
		get_pose_bone("c_root.x").lock_location[i] = True
		 
	bpy.ops.object.mode_set(mode='EDIT')
		
	
	# Store in dict
	
	#Additional bones		
	for edit_bone in arp_armature.data.edit_bones:
		#custom bones?
		if edit_bone.name[:3] == 'cc_':
			bones_dict[edit_bone.name] = (edit_bone.name, edit_bone.head.copy(), edit_bone.tail.copy(), edit_bone.roll, True)
			
		#bend bones?
		if scene.keep_bend_bones:
			if is_bend_bone(edit_bone.name) and not 'proxy' in edit_bone.name:
				if not bpy.context.object.data.bones[edit_bone.name].layers[22]:#check for disabled limb				
					bones_dict[edit_bone.name] = (edit_bone.name, edit_bone.head.copy(), edit_bone.tail.copy(), edit_bone.roll, True)
				
		#facial?		
		if scene.full_facial and arp_armature.rig_facial:			
			if edit_bone.name[:-2] in additional_facial_list:
				
				bones_dict[edit_bone.name] = (edit_bone.name, edit_bone.head.copy(), edit_bone.tail.copy(), edit_bone.roll, True)
				
		#toes?
		if 'c_toes_' in edit_bone.name:
			if edit_bone.use_deform:
				bones_dict[edit_bone.name] = (edit_bone.name, edit_bone.head.copy(), edit_bone.tail.copy(), edit_bone.roll, True)
			
	#Main bones
	for key, value in bones_dict.items():
		if key[:3] != 'cc_' and not is_bend_bone(key):#every bones except cc and bend, already stored
		
			edit_bone = arp_armature.data.edit_bones[value[0]]
			
			#Check for deform - Disabled limbs
			if 'spine' in value[0] or 'root' in value[0]:# or 'shoulder' in value[0]:#these bones can't be disabled in Humanoid, main structure
				b_use_deform = True
			else:
				b_use_deform = edit_bone.use_deform
							
			bones_dict[key] = (value[0], edit_bone.head.copy(), edit_bone.tail.copy(), edit_bone.roll, b_use_deform)
			
	#add the thigh real head pose, because thigh_stretch is halfway
	
	for side in sides:
		thigh_ref = arp_armature.data.edit_bones['thigh_ref' + side]
		bones_dict['thigh_ref' + side] = ('thigh_ref' + side, thigh_ref.head.copy(), thigh_ref.tail.copy(), thigh_ref.roll, False)
		
	
	bpy.ops.object.mode_set(mode='POSE') 
	bpy.ops.object.mode_set(mode='OBJECT')
	set_active_object(humanoid_armature.name)
	bpy.ops.object.mode_set(mode='EDIT') 
	
	
	#Create additional bones
	custom_root_parent = []
	
	for bone in bones_dict:				
		#if bone[:3] == 'cc_' or is_bend_bone(bone):		
		try:
			humanoid_armature.data.edit_bones[bone]
		except:#additional bone does not exist yet, create it with default values atm
			if not 'thigh_ref' in bone:
				new_bone = bpy.context.object.data.edit_bones.new(bone) 
				new_bone.head = Vector((0,0,0))
				new_bone.tail = Vector((5,5,5))

				
	bpy.ops.object.mode_set(mode='POSE') 
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.mode_set(mode='EDIT') 
	
	
	
	#Set their parent
	for bone in bones_dict: 
		
		if ('cc_' in bone) or (is_bend_bone(bone)) or (bone in auto_rig_datas.facial_deform and scene.full_facial) or (bone[:-2] in additional_facial_list or ('c_toes_' in bone)):#jaw + skulls	
						
			#set parent translation
			bone_parent = arp_armature.data.bones[bone].parent.name
			
			#try to find parent in the humanoid armature, otherwise translate			
			_parent = ""
			if 'c_eye_ref' in bone:
				bone_parent = 'c_eye_offset' + bone[-2:]
				
			#full facial case parents
			if scene.full_facial and arp_armature.rig_facial:
				if 'jawbone' in bone:				
					bone_parent = 'c_skull_01.x'
				if 'eye_offset' in bone:
					bone_parent = 'c_skull_02.x'
			
			try:
				bpy.context.object.data.edit_bones[bone_parent]
				_parent = bone_parent
				
					
			except:				
					
				if bone_parent == 'c_root_master.x':
					_parent = 'root.x'				
					custom_root_parent.append(bone)
				if bone_parent == 'c_root.x':
					_parent = 'root.x'
					custom_root_parent.append(bone)
				if bone_parent == 'c_spine_01.x':
					_parent = 'spine_01.x'
				if bone_parent == 'c_spine_02.x':
					_parent = 'spine_02.x'
				if bone_parent == 'c_spine_03.x':
					_parent = 'spine_03.x'
				if 'neck' in bone_parent:
					_parent = 'neck.x'
				if 'head' in bone_parent or ('skull' in bone_parent and not scene.full_facial and not arp_armature.rig_facial):
					_parent = 'head.x'
				if 'shoulder' in bone_parent:
					_parent = 'shoulder' + bone_parent[-2:]
				if 'arm' in bone_parent and not 'forearm' in bone_parent:
					_parent = 'arm_stretch' + bone_parent[-2:]
				if 'forearm' in bone_parent:
					_parent = 'forearm_stretch' + bone_parent[-2:]
				if 'hand' in bone_parent:
					_parent = 'hand' + bone_parent[-2:]
				if 'thigh' in bone_parent:
					_parent = 'thigh_stretch' + bone_parent[-2:]
				if 'leg' in bone_parent:
					_parent = 'leg_stretch' + bone_parent[-2:]
				if 'foot' in bone_parent:
					_parent = 'foot' + bone_parent[-2:]
				if 'toes' in bone_parent:
					_parent = 'toes_01' + bone_parent[-2:]
				if 'tong_03' in bone_parent:
					_parent = 'tong_02.x'					
				if 'tong_02' in bone_parent:
					_parent = 'tong_01.x'
				if 'tong_01' in bone_parent:
					_parent = 'c_jawbone.x'
				if 'eyelid' in bone_parent:
					_parent = 'c_eye_offset' + bone_parent[-2:] 
				if 'teeth_top_master' in bone_parent:
					_parent = 'c_skull_01.x'
				if 'teeth_bot_master' in bone_parent:
					_parent = 'c_jawbone.x'
			
				
			
			try:
				if bone_parent == 'root.x': 
					custom_root_parent.append(bone) 
					
				bpy.context.object.data.edit_bones[bone].parent = get_edit_bone(_parent)
				
			except:
				print('Bone not found in armature:', _parent)
				pass
				

	#Add constraints
	bpy.ops.object.mode_set(mode='POSE') 
	bpy.ops.object.mode_set(mode='EDIT') 
	
	for bone in bpy.context.object.pose.bones:				
		if bone.name[:3] == 'cc_' or is_bend_bone(bone.name) or (bone.name[:-2] in additional_facial_list) or ('c_toes_' in bone.name):
			if len(bone.constraints) == 0:
				cns = bone.constraints.new('COPY_TRANSFORMS')
				cns.target = bpy.data.objects[arp_armature.name]
				cns.subtarget = bone.name				
		
	bpy.ops.object.mode_set(mode='EDIT')

	#Set bones transforms rest pose from bone dict
	for b in humanoid_armature.data.edit_bones:	  
		if b.name[:-2] != 'forearm_stretch' and b.name[:-2] != 'arm_stretch' and b.name[:-2]!= 'leg_stretch' and b.name[:-2] != 'thigh_stretch':
			b.head = bones_dict[b.name][1]
			b.tail= bones_dict[b.name][2]
			b.roll = bones_dict[b.name][3]
			b.use_deform = bones_dict[b.name][4]
		else:
			if b.name[:-2] == 'arm_stretch':
				b.head = bones_dict['shoulder' + b.name[-2:]][2]
				b.tail= bones_dict[b.name][2]
				b.roll = bones_dict[b.name][3]
				b.use_deform = bones_dict[b.name][4]
			if b.name[:-2] == 'forearm_stretch':
				b.head = bones_dict['arm_stretch' + b.name[-2:]][2]
				b.tail= bones_dict['hand' + b.name[-2:]][1]
				b.roll = bones_dict[b.name][3]
				b.use_deform = bones_dict[b.name][4]
				
			if b.name[:-2] == 'thigh_stretch':
				b.head = bones_dict['thigh_ref' + b.name[-2:]][1]
				b.tail= bones_dict['thigh_ref' + b.name[-2:]][2]
				b.roll = bones_dict[b.name][3]
				b.use_deform = bones_dict[b.name][4]
			if b.name[:-2] == 'leg_stretch':
				b.head = bones_dict[b.name][1]
				b.tail= bones_dict['foot' + b.name[-2:]][1]
				b.roll = bones_dict[b.name][3]
				b.use_deform = bones_dict[b.name][4]
			
			
				
		
				
		#don't deform bend bones if parent doesn't
		if '_bend' in b.name:
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
			
	
	bpy.ops.object.mode_set(mode='POSE') 
	
	# Create and key first and last action framerate
	bpy.ops.pose.select_all(action='SELECT')
	try:
		action = bpy.data.objects[arp_armature.name].animation_data.action

		current_frame = scene.frame_current#save current frame	  

		for f in action.frame_range:	
			scene.frame_current = f
			scene.frame_set(scene.frame_current)#debug		 
			bpy.ops.transform.translate(value=(0, 0, 0))#update	   
			for bone in bpy.context.selected_pose_bones:
				bone.keyframe_insert(data_path="rotation_euler")
				bone.keyframe_insert(data_path="location")

		#restore current frame
		scene.frame_current = current_frame
		scene.frame_set(scene.frame_current)#debug	

		bpy.data.objects[humanoid_armature.name].animation_data.action.name = action.name + "_humanoid"
		
	except:
		print("No action to create")
		
	
	
	bpy.ops.object.mode_set(mode='OBJECT')
	humanoid_armature.hide = hide_state
	
	
	# Transfer weights			
	def transfer_weight(object=None, vertice=None, vertex_weight=None, group_name=None, dict=None, list=None, target_group=None):
											
		grp_name_base = group_name[:-2]
		side = grp_name[-2:]	
		
		#Dict mode
		if list == None:
			if grp_name_base in dict:													
				if dict[grp_name_base][-2:] == '.x':
					side = ''
				_target_group = dict[grp_name_base]+side
				
				if object.vertex_groups.get(_target_group) != None:#if exists					
					object.vertex_groups[_target_group].add([vertice.index], vertex_weight, 'ADD')
		
		#List mode
		if dict == None:
			if grp_name_base in list:		
				if object.vertex_groups.get(target_group) != None:#if exists		
					object.vertex_groups[target_group].add([vertice.index], vertex_weight, 'ADD')			
				
	
		#iterates over armature meshes
	for obj in bpy.data.objects:
		if obj.type == 'MESH':
			if len(obj.modifiers) > 0:
				for modif in obj.modifiers:
					if modif.type == 'ARMATURE':
						if modif.object == arp_armature:
						
							set_active_object(obj.name)
							
							#change it to humanoid armature
							modif.object = humanoid_armature
							modif.use_deform_preserve_volume = False
							
							twist_dict = {'leg_twist':'leg_stretch', 'thigh_twist':'thigh_stretch', 'c_arm_twist_offset':'arm_stretch', 'forearm_twist':'forearm_stretch'}						
							
							other_dict = {'c_neck_01':'spine_02.x', 'c_index1_base':'hand', 'c_middle1_base':'hand', 'c_ring1_base':'hand', 'c_pinky1_base':'hand', 'c_thumb1_base':'c_thumb1'}			
							
							sides = ['.l', '.r']
								
							for vert in obj.data.vertices:
								if len(vert.groups) > 0:
									for grp in vert.groups:
										grp_name = obj.vertex_groups[grp.group].name										
										weight = grp.weight					
										
										#transfer twists?								
										if scene.transfer_twist:										
											transfer_weight(object=obj, vertice=vert, vertex_weight=weight, group_name=grp_name, dict=twist_dict)	
										
										#transfer bend bones?						
										if not scene.keep_bend_bones:																				
											transfer_weight(object=obj, vertice=vert, vertex_weight=weight, group_name=grp_name, dict=bend_bones_main)																						
										
										#transfer additional facial?
										if not scene.full_facial and not arp_armature.rig_facial:
											transfer_weight(object=obj, vertice=vert, vertex_weight=weight, group_name=grp_name, list=additional_facial_list, target_group='head.x')
										
										
										#merge others														
										transfer_weight(object=obj, vertice=vert, vertex_weight=weight, group_name=grp_name, dict=other_dict)	
										
										
						#Remove the Rig Add armature modifier
						if modif.object == bpy.data.objects['rig_add']: 
							bpy.ops.object.mode_set(mode='OBJECT')
							bpy.ops.object.select_all(action='DESELECT')
							set_active_object(obj.name)
							bpy.ops.object.modifier_remove(modifier=modif.name)
						

				
	#Push the bend bones?
	if scene.keep_bend_bones and scene.push_bend:
		_action = arp_armature.animation_data.action
		if _action != None:
			for fcurve in _action.fcurves:	   
				for bbone in bend_bones_add:
					if bbone in fcurve.data_path:#operate only on bend bone add fcurves					
						for key in fcurve.keyframe_points:
							if not 'scale' in fcurve.data_path:
								key.co[1] *= 2
								key.handle_left[1] *= 2
								key.handle_right[1] *= 2
								
							else:
								key.co[1] = -1 + (key.co[1]) * 2
								key.handle_left[1] = -1 + (key.handle_left[1]) * 2
								key.handle_right[1] = -1 + (key.handle_right[1]) * 2
						break
							
	

		
	
	bpy.data.armatures[humanoid_armature.data.name].pose_position = 'POSE'
	humanoid_armature['set'] = True
	humanoid_armature['binded'] = True
	
	#Done _set_humanoid_rig()
	
	
	   
	
def _unset_humanoid_rig():

	scene = bpy.context.scene
	#set surface subdivision to 0 to speed up
	simplify = bpy.context.scene.render.use_simplify #save
	simplify_value = bpy.context.scene.render.simplify_subdivision
	bpy.context.scene.render.use_simplify = True #set
	bpy.context.scene.render.simplify_subdivision = 0
	
	

	
	#get the armatures	 
	bpy.ops.object.mode_set(mode='OBJECT') 

	humanoid_armature = bpy.data.objects['rig_humanoid']
	arp_armature = bpy.data.objects['rig']		
	 
	set_active_object(arp_armature.name)
	bpy.ops.object.mode_set(mode='POSE') 
	
	#unlock the root translation
	for i in range(0,3):
		get_pose_bone("c_root.x").lock_location[i] = False
		
	bpy.ops.object.mode_set(mode='OBJECT') 
	hide_state = humanoid_armature.hide
	humanoid_armature.hide = False

	# set the ARP armature as the deforming one
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
				for m in bpy.context.object.modifiers:
					if m.type == 'MIRROR':
						for i in range(0,20):
							bpy.ops.object.modifier_move_up(modifier=m.name)
	
	"""
	#Keep the humanoid?
	bpy.data.armatures[humanoid_armature.data.name].pose_position = 'REST'	
	humanoid_armature.hide = hide_state
	humanoid_armature['set'] = False
	humanoid_armature['binded'] = False
	"""
	
	#Delete the humanoid
	bpy.ops.object.mode_set(mode='OBJECT') 
	bpy.ops.object.select_all(action='DESELECT')
	set_active_object(humanoid_armature.name)
	bpy.ops.object.mode_set(mode='OBJECT') 
	bpy.ops.object.delete()
	
	#Push the bend bones transform *0.5 
	if scene.keep_bend_bones and scene.push_bend:
	
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
	
	
	
def _constraint_rig(state):
	humanoid_armature = bpy.data.objects['rig_humanoid']
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.select_all(action='DESELECT')
	
	#Unhide if hidden
	mute_state = bpy.data.objects["rig_humanoid"].hide
	bpy.data.objects["rig_humanoid"].hide = False
	
	
	set_active_object("rig_humanoid")
	
	
	#Switch to Pose mode
	bpy.ops.object.mode_set(mode='POSE')
	bpy.ops.pose.select_all(action='SELECT')
	
	#Mute or Unmute constraints
	for bone in bpy.context.selected_pose_bones:
		for cns in bone.constraints:
			if cns.name != "Track To" and cns.name != "Stretch To":
				cns.mute = state
		   
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.transform.translate(value=(0, 0, 0))#update	  
	
	#reset hide state
	bpy.data.objects["rig_humanoid"].hide = mute_state
	
	humanoid_armature['binded'] = not state 


def update_rename_for_ue(self, context):

	scene = context.scene

	if scene.rename_for_ue:
		for pbone in bpy.data.objects['rig_humanoid'].pose.bones:
			if not '_bend' in pbone.name:
				if 'thigh' in pbone.name:
					pbone.name = pbone.name.replace('thigh_stretch', 'thigh')
				if 'leg' in pbone.name:
					pbone.name = pbone.name.replace('leg_stretch', 'calf')
				if 'toes' in pbone.name:
					pbone.name = pbone.name.replace('toes_01', 'ball')
				if 'shoulder' in pbone.name:
					pbone.name = pbone.name.replace('shoulder','clavicle')
				if 'arm_stretch' in pbone.name and not 'forearm_stretch' in pbone.name:
					pbone.name = pbone.name.replace('arm_stretch', 'upperarm')
				if 'forearm_stretch' in pbone.name:
					pbone.name = pbone.name.replace('forearm_stretch', 'lowerarm')
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
				if 'neck' in pbone.name:
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
			
		
	else:
		
		for pbone in bpy.data.objects['rig_humanoid'].pose.bones:
			if not '_bend' in pbone.name:
				if 'thigh' in pbone.name:
					pbone.name = pbone.name.replace('thigh', 'thigh_stretch')
				if 'calf' in pbone.name:
					pbone.name = pbone.name.replace('calf', 'leg_stretch')
				if 'ball' in pbone.name:
					pbone.name = pbone.name.replace('ball', 'toes_01')
				if 'clavicle' in pbone.name:
					pbone.name = pbone.name.replace('clavicle','shoulder')
				if 'upperarm' in pbone.name:
					pbone.name = pbone.name.replace('upperarm', 'arm_stretch')
				if 'lowerarm' in pbone.name:
					pbone.name = pbone.name.replace('lowerarm', 'forearm_stretch')
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

	return None
		   
	
###########	 UI PANEL  ###################

class auto_rig_GE_panel(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_label = "Auto-Rig Pro: Game Engine Export"
	bl_idname = "id_auto_rig_ge"
	

	def draw(self, context):
		layout = self.layout
		object = context.object
		scene = context.scene
		
		
		#BUTTONS
		
		#layout.label("Unity Export:")
		
		
		layout.label('For Unreal:')		
		row = layout.row(align=True)		
		row.operator("id.set_unreal_scale", "UE Units")
		row.operator("id.set_standard_scale", "Blender Units")
		
		box = layout.box()
		box.label('For Unreal / Unity:')
		box.row(align=True).prop(scene, "unity_rig_type", expand=True)
		
		
		
		if scene.unity_rig_type == 'generic': 
			row = box.row(align = True)
			row.prop(scene, 'keep_bend_bones')
			row1 = row.row()
			if scene.keep_bend_bones:
				row1.enabled = True
			else:
				row1.enabled = False
				
			row1.prop(scene,"push_bend")
			
			box.operator("id.setup_generic", "Setup Generic Rig")
		
			export=box.operator("id.export_fbx", "Export .fbx")
			export.type = 'generic'
			
		if scene.unity_rig_type == 'humanoid': 
			humanoid_loaded = False
			try:
				bpy.data.objects['rig_humanoid']
				humanoid_loaded = True
			except:
				pass
		
			row = box.row(align=True)
				
			row.prop(scene,"keep_bend_bones")
			row1 = row.row()
			if scene.keep_bend_bones:
				row1.enabled = True
			else:
				row1.enabled = False
				
			row1.prop(scene,"push_bend")
			
			row = box.row(align=True)
			row.prop(scene,"full_facial")
			row.prop(scene,"transfer_twist")		
			
			
			
			col = box.column(align=True)
			row = col.row(align=True)
			row.operator("id.set_humanoid_rig", "Set")						
			row.operator("id.unset_humanoid_rig", "Unset")
			
			row = col.row(align=True)
			button = row.operator("id.bind_humanoid", "Bind")	
			button = row.operator("id.unbind_humanoid", "Unbind")
	
			
			row = box.row(align=True)
			if bpy.data.objects.get('rig_humanoid') != None:
				row.enabled = True
			else:
				row.enabled = False
			row.prop(scene, "rename_for_ue")
			
			col = box.column(align=True)
			row = col.row(align=True)
			row.operator("id.bake_all", "Bake All")
			row = col.row(align=True)
			export=row.operator("id.export_fbx", "Export .fbx")
			export.type = 'humanoid'
			
			
			
		
		
			
		
 
##################	REGISTER  ##################

def register():	  

	bpy.types.Scene.unity_rig_type = bpy.props.EnumProperty(items=(
		("generic", "Generic", "Generic rig type, export all deforming bones"),
		("humanoid", "Humanoid", "Humanoid rig type, simple bone hierarchy to ensure animation retargetting")
		), name = "Unity Rig Type Export", description="Rig type to export")
	
	bpy.types.Scene.rename_for_ue = bpy.props.BoolProperty(name="Rename for UE", description="Rename bones according to Unreal Engine humanoid names convention. \nOther panel buttons will be greyed out, only check it before exporting", default=False, update=update_rename_for_ue)
	bpy.types.Scene.transfer_twist = bpy.props.BoolProperty(name='Transfer Twist', description="Transfer the twist bone weight groups on the main groups", default=True)
	bpy.types.Scene.keep_bend_bones = bpy.props.BoolProperty(name='Advanced', description="Include the advanced bones, bend, breasts... Useful for cartoons rigs. \nWarning: may change a little the bend bones skin weights", default=False)
	bpy.types.Scene.full_facial = bpy.props.BoolProperty(name='Full Facial', description="Include all facial bones, with skulls", default=False)
	bpy.types.Scene.push_bend = bpy.props.BoolProperty(name='Push Additive', description="(Animated armature only) Push up the additive bend bones transforms to compensate the lower weights, since the additive armature modifier is not exported", default=True)


def unregister():	
	
	del bpy.types.Scene.unity_rig_type
	del bpy.types.Scene.rename_for_ue
	del bpy.types.Scene.transfer_twist
	del bpy.types.Scene.keep_bend_bones
	del bpy.types.Scene.full_facial
	del bpy.types.Scene.push_bend

		