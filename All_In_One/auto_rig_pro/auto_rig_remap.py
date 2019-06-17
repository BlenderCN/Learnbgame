import bpy, bmesh, math, re, operator, os, difflib, csv
from math import degrees, pi, radians, ceil, sqrt
from bpy.types import Panel, UIList
import mathutils
from mathutils import Vector, Euler, Matrix
#import numpy



print ("\n Starting Auto-Rig Pro: Remap... \n")

##########################	CLASSES	 ##########################

# BONES COLLECTION CLASS
class ARP_UL_items(UIList):
	
	@classmethod
	def poll(cls, context):
		return (context.scene.source_action != "" and context.scene.source_rig != "" and context.scene.target_rig != "")

	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		split = layout.split(factor=1.0)
		split.prop(item, "source_bone", text="", emboss=False, translate=False, icon='BONE_DATA')
		split = layout.split(factor=1.0)
		#split.label(">")		
		split.prop(item, "name", text="", emboss=False, translate=False, icon='BONE_DATA')

	def invoke(self, context, event):
		pass   


# OTHER CLASSES

class ARP_OT_freeze_armature(bpy.types.Operator):
	  
	#tooltip
	"""Clear animation datas from the armature object and initialized its transforms. Preserve bones animation"""
	
	bl_idname = "arp.freeze_armature"
	bl_label = "freeze_armature"
	bl_options = {'UNDO'}	
	
	
	@classmethod
	def poll(cls, context):
		if context.scene.source_rig != "":
			if bpy.data.objects[context.scene.source_rig]:
				return True
	

	def execute(self, context):
	
		#if not sanity_check(self):
		#	return {'FINISHED'}
		if bpy.data.objects.get(context.scene.source_rig) == None:
			message = "Source armature not found"
			print(message)
			self.report({'ERROR'}, message)	
			return {'FINISHED'}
	
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
				  
					
		try:			
		
			_freeze_armature(self)				
	 
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}


class ARP_OT_redefine_rest_pose(bpy.types.Operator):
	  
	#tooltip
	"""Edit the source armature rest pose, so that it looks like the target armature.\nClick Done to complete"""
	
	bl_idname = "arp.redefine_rest_pose"
	bl_label = "redefine_rest_pose"
	bl_options = {'UNDO'}	
	
	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None and context.scene.source_action != "" and context.scene.source_rig != "" and context.scene.target_rig != "")

	def execute(self, context):
		
		if not sanity_check(self):
			return {'FINISHED'}
			
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False		
				
		try:
			
			#set to object mode
			bpy.ops.object.mode_set(mode='OBJECT')
		
			_redefine_rest_pose(self, context)	
			
	 
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}


class ARP_OT_auto_scale(bpy.types.Operator):
	  
	#tooltip
	"""Automatic scale of the source armature to fit the target armature height"""
	
	bl_idname = "arp.auto_scale"
	bl_label = "auto_scale"
	bl_options = {'UNDO'}	
	
	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None and context.scene.source_action != "" and context.scene.source_rig != "" and context.scene.target_rig != "")

	def execute(self, context):
	
		#save current mode
		current_mode = context.mode
		active_obj_name = None
		try:
			active_obj_name = context.active_object.name
		except:
			pass
	
		if not sanity_check(self):
			return {'FINISHED'}
	
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
			
		
		try:
			
			#set to object mode
			bpy.ops.object.mode_set(mode='OBJECT')
		
			_auto_scale(self, context)	

			#restore saved mode	   
			if current_mode == 'EDIT_ARMATURE':
				current_mode = 'EDIT'		 
			try:
				bpy.ops.object.mode_set(mode='OBJECT')
				set_active_object(active_obj_name)	  
				print(active_obj_name)
				bpy.ops.object.mode_set(mode=current_mode)				 
				  
			except:
				pass
	 
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}

class ARP_OT_apply_offset(bpy.types.Operator):
	  
	#tooltip
	"""Add an offset"""
	
	bl_idname = "arp.apply_offset"
	bl_label = "apply_offset"
	bl_options = {'UNDO'}	
	
	
	value : bpy.props.StringProperty(name="offset_value")
	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None)

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:
			#save current mode
			current_mode = context.mode
			active_obj = None
			try:
				active_obj = context.active_object
			except:
				pass
			#set to object mode
			bpy.ops.object.mode_set(mode='OBJECT')
		
			_apply_offset(self, context, self.value)	

			#restore saved mode	   
			if current_mode == 'EDIT_ARMATURE':
				current_mode = 'EDIT'		 
			try:
				bpy.ops.object.mode_set(mode='OBJECT')
				set_active_object(active_obj.name)	  
				bpy.ops.object.mode_set(mode=current_mode)				 
				  
			except:
				pass
	 
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
		
class ARP_OT_cancel_redefine(bpy.types.Operator):
	#tooltip
	"""Cancel the rest pose edition"""
	
	bl_idname = "arp.cancel_redefine"
	bl_label = "cancel_redefine"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None)

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:				   
			_cancel_redefine()		 
	 
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
		
class ARP_OT_copy_bone_rest(bpy.types.Operator):
	  
	#tooltip
	"""Select the bones of the source armature that should get the same orientation as the bones of the target armature.\nThen click this button to match their orientation"""
	
	bl_idname = "arp.copy_bone_rest"
	bl_label = "copy_bone_rest"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None)

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:				   
			_copy_bone_rest(self, context)		 
	 
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
		


class ARP_OT_copy_raw_coordinates(bpy.types.Operator):
	  
	#tooltip
	"""Complete the rest pose edition (long animations may take a while to complete)"""
	
	bl_idname = "arp.copy_raw_coordinates"
	bl_label = "copy_raw_coordinates"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None)

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:				   
			_copy_raw_coordinates(self, context)		 
	 
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
		
class ARP_OT_pick_object(bpy.types.Operator):
	  
	#tooltip
	"""Pick the selected object/bone"""
	
	bl_idname = "arp.pick_object"
	bl_label = "pick_object"
	bl_options = {'UNDO'}	
	
	action : bpy.props.EnumProperty(
		items=(
				('pick_source', 'pick_source', ''),
				('pick_target', 'pick_target', ''),
				('pick_bone', 'pick_bone', ''),
				('pick_pole', 'pick_pole', '')
			)
		)
	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None)

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:				   
			_pick_object(self.action)		  
	 
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}

class ARP_OT_guess_orientation(bpy.types.Operator):
	  
	#tooltip
	"""Guess axes mapping, based on the bones rotation in rest pose. The source and target armature have to face the same direction while in T-Pose. Works best if their rest pose are very close visually"""
	
	bl_idname = "arp.guess_orientation"
	bl_label = "guess_orientation"
	bl_options = {'UNDO'}	
	
	guess_all : bpy.props.BoolProperty(name="guess all")

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		
		#save current mode
		current_mode = context.mode
		active_obj = None
		try:
			active_obj = context.active_object
		except:
			pass
		#set to object mode
		bpy.ops.object.mode_set(mode='OBJECT')
		
		try:			   
			_guess_orientation(context, self.guess_all) 
		   
			#restore saved mode	   
			if current_mode == 'EDIT_ARMATURE':
				current_mode = 'EDIT'		 
			try:
				bpy.ops.object.mode_set(mode='OBJECT')
				set_active_object(active_obj.name)	  
				bpy.ops.object.mode_set(mode=current_mode)				 
				  
			except:
				pass
	 
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
		
		

class ARP_OT_export_config(bpy.types.Operator):
	  
	#tooltip
	"""Export the current bones list and config to the file path"""
	
	bl_idname = "arp.export_config"
	bl_label = "export_config"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None)

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:				   
			_export_config()		 
	 
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
		
class ARP_OT_import_config(bpy.types.Operator):
	  
	#tooltip
	"""Import the bones list and config from the file path"""
	
	bl_idname = "arp.import_config"
	bl_label = "import_config"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None)

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:				   
			_import_config(self, context)		  
	 
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}


		
class ARP_OT_retarget_clicked(bpy.types.Operator):
	"""Retarget the source action on the selected armature"""

	bl_idname = "arp.retarget_clicked"
	bl_label = "retarget_clicked"
	bl_options = {'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None and context.scene.source_action != "" and context.scene.source_rig != "" and context.scene.target_rig != "")

	def execute(self, context):		
		#check if a Root bone has been assigned
		found_root = False
		for bone in context.scene.bones_map:
			if bone.set_as_root:
				found_root = True
				
		if not found_root:
			self.report({'ERROR'}, 'The root bone must be marked first: "Set as Root"')
			return {'FINISHED'}	
	
		# open the dialog if necessary to show a warning			
		# check for non-controller bones, for Auto-Rig Pro armatures
		invalid_controller_found = False
		target_armature = bpy.data.objects[context.scene.target_rig].data		
		if target_armature.bones.get("c_traj") and target_armature.bones.get("c_pos"):	
			for b in context.scene.bones_map:
				if target_armature.bones.get(b.name):
					if b.name[:2] != "c_":
						invalid_controller_found = True
						break
						
		
					
		if invalid_controller_found:
			bpy.ops.arp.retarget_dialog("INVOKE_DEFAULT")
		else:
			# else just run the default update
			bpy.ops.arp.retarget_operator()
			
		return {'FINISHED'}	
		

class ARP_OT_retarget_dialog(bpy.types.Operator):
	""" This update includes bones transforms change, then it can break the rig pose and animation"""
	bl_label = ''
	bl_idname = "arp.retarget_dialog"
	
	
	def draw(self, context):
		layout = self.layout
		layout.label(text='Warning!', icon='INFO')
		layout.label(text='The target armature is an Auto-Rig Pro armature, while some bones')
		layout.label(text='in the list are not controller (no "c_" prefix").')		
		layout.label(text='Retargetting to non-controller bones can potentially break the rig. Continue?')
		
	
	def execute(self, context):		
		bpy.ops.arp.retarget_operator()	
		return {"FINISHED"}
		
	def invoke(self, context, event):
		wm = context.window_manager 
		return wm.invoke_props_dialog(self, width=400)
		
		
class ARP_OT_retarget(bpy.types.Operator):
	  
	#tooltip
	"""Retarget the source action on the selected armature"""
	
	bl_idname = "arp.retarget_operator"
	bl_label = "retarget"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None and context.scene.source_action != "" and context.scene.source_rig != "" and context.scene.target_rig != "")

	def execute(self, context):
	
		if not sanity_check(self):
			return {'FINISHED'}
	
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		
		try:			
			
			#save current mode
			current_mode = context.mode
			active_obj = None
			try:
				active_obj = context.active_object
			except:
				pass
			#save to object mode
			bpy.ops.object.mode_set(mode='OBJECT')
			
			#execute function
			_retarget(self)
			
			#restore current mode
			try:
				set_active_object(active_obj.name)
			except:
				pass
				#restore saved mode	   
			if current_mode == 'EDIT_ARMATURE':
				current_mode = 'EDIT'
		
			try:
				bpy.ops.object.mode_set(mode=current_mode)
			except:
				pass
	
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
	
class ARP_OT_build_bones_list(bpy.types.Operator):
	  
	#tooltip
	"""Build the source and target bones list, and try to match their names with Auto-Rig Pro or any other armature"""
	
	bl_idname = "arp.build_bones_list"
	bl_label = "build_bones_list"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		return (context.active_object != None and context.scene.source_action != "" and context.scene.source_rig != "" and context.scene.target_rig != "")

	def execute(self, context):
	
		if not sanity_check(self):
			return {'FINISHED'}
	
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		
		
		
		try:
			#save current mode
			current_mode = context.mode
			active_obj = None
			try:
				active_obj = context.active_object
			except:
				pass
			#save to object mode
			bpy.ops.object.mode_set(mode='OBJECT')
			
			#execute function			 
			_build_bones_list()
			
			#restore current mode
			try:
				bpy.ops.object.select_all(action='DESELECT')
				set_active_object(active_obj.name)
			except:
				pass
				#restore saved mode	   
			if current_mode == 'EDIT_ARMATURE':
				current_mode = 'EDIT'
		
			try:
				bpy.ops.object.mode_set(mode=current_mode)
			except:
				pass
		
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
		
		
		
class ARP_OT_set_as_root(bpy.types.Operator):
	  
	#tooltip
	"""Set this bone as the root (hips) of the armature for correct motion"""
	
	bl_idname = "arp.set_as_root"
	bl_label = "set_as_root"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		return (context.scene.source_action != "" and context.scene.source_rig != "" and context.scene.target_rig != "")

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		
		try:
			#save current mode
			current_mode = context.mode
			active_obj = None
			try:
				active_obj = context.active_object
			except:
				pass
		   
			#execute function			 
			_set_as_root()
			
			#restore current mode
			try:
				bpy.ops.object.select_all(action='DESELECT')
				set_active_object(active_obj.name)
			except:
				pass
				#restore saved mode	   
			if current_mode == 'EDIT_ARMATURE':
				current_mode = 'EDIT'
		
			try:
				bpy.ops.object.mode_set(mode=current_mode)
			except:
				pass
		
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}
		

	
############ FUNCTIONS ##############################################################

def sanity_check(self):
	# check if both source and target armature are in the scene
	try:
		set_active_object(bpy.context.scene.source_rig)	
		set_active_object(bpy.context.scene.target_rig)	
		return True
		
	except:
		print("Armature not found")
		self.report({'ERROR'}, "Armature not found")	
		return False

#Math Utilities---------------------------------------------
def vec_roll_to_mat3(vec, roll):
	target = Vector((0, 0.1, 0))
	nor = vec.normalized()
	axis = target.cross(nor)
	if axis.dot(axis) > 0.0000000001: # this seems to be the problem for some bones, no idea how to fix
		axis.normalize()
		theta = target.angle(nor)
		bMatrix = Matrix.Rotation(theta, 3, axis)
	else:
		updown = 1 if target.dot(nor) > 0 else -1
		bMatrix = Matrix.Scale(updown, 3)				
		bMatrix[2][2] = 1.0

	rMatrix = Matrix.Rotation(roll, 3, nor)
	mat = rMatrix @ bMatrix
	return mat
		
def mat3_to_vec_roll(mat):
	vec = mat.col[1]
	vecmat = vec_roll_to_mat3(mat.col[1], 0)
	vecmatinv = vecmat.inverted()
	rollmat = vecmatinv @ mat
	roll = math.atan2(rollmat[0][2], rollmat[2][2])
	return roll

	
#Global utilities---------------------------------------------------------
def get_edit_bone(name):
	return bpy.context.object.data.edit_bones[name]
	
def add_empty(location_empty = (0,0,0), name_string="name_string"):
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.empty_add(type='PLAIN_AXES', radius=1, view_align=True, location=(location_empty), rotation=(0, 0, -0))
	

	bpy.context.object.name = name_string
	
#Main features-------------------------------------------------------------	
def _redefine_rest_pose(self,context):
	scene = context.scene
	
	#ensure the source armature selection
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.select_all(action='DESELECT')
	set_active_object(scene.source_rig)	
	bpy.ops.object.mode_set(mode='OBJECT')
	
	#set the target in rest pose for correct transform copy
	bpy.data.objects[scene.target_rig].data.pose_position = 'REST'

	
	bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, -1000, -10000), "constraint_axis":(False, True, False), "constraint_orientation":'GLOBAL', "mirror":False, "snap":False, "remove_on_cancel":False, "release_confirm":False})
	bpy.context.object.name = scene.source_rig + "_copy"
	
	bpy.ops.object.select_all(action='DESELECT')
	set_active_object(scene.source_rig)
	
	bpy.ops.object.mode_set(mode='POSE')
	bpy.context.object.animation_data.action = None
	bpy.ops.pose.select_all(action='SELECT')
	bpy.ops.pose.loc_clear()
	bpy.ops.pose.rot_clear()
	bpy.ops.pose.scale_clear()
	
	
	
def _copy_bone_rest(self,context):	
	scene = context.scene
	current_frame = bpy.context.scene.frame_current#save current frame
	target_rig = bpy.data.objects[scene.target_rig]
	source_rig = bpy.data.objects[scene.source_rig]
	
	for bone in context.selected_pose_bones:
		#get the target bone
		for b in scene.bones_map:
			if b.source_bone == bone.name:
				target_bone_name =b.name
				print("Target bone name", target_bone_name)
				
		if target_bone_name != "" and target_bone_name != None and target_rig.pose.bones.get(target_bone_name):
			target_bone = target_rig.pose.bones[target_bone_name]
			vec = (target_bone.tail - target_bone.head)
		
			#refresh
			bpy.context.scene.frame_current = current_frame
			bpy.context.scene.frame_set(bpy.context.scene.frame_current)#debug	 
			
			empty_loc = (source_rig.matrix_world @ bone.head) + target_rig.matrix_world @ (vec*10000)
		
			add_empty(location_empty =	empty_loc, name_string = bone.name + "_empty_track")
			
			set_active_object(source_rig.name)
			bpy.ops.object.mode_set(mode='POSE')		
			
			new_cns = bone.constraints.new('DAMPED_TRACK')
			new_cns.name = 'damped_track'
			new_cns.target = bpy.data.objects[bone.name + "_empty_track"]
			
			#refresh
			bpy.context.scene.frame_current = current_frame
			bpy.context.scene.frame_set(bpy.context.scene.frame_current)#debug	 
			
			# store the bone transforms
			bone_mat = bone.matrix.copy()
			
			#apply rest pose		
			#bpy.ops.pose.armature_apply()
			
			#clear constraints
			try:
				bone.constraints.remove(bone.constraints['damped_track'])
			except:
				pass
		
			# restore the transforms
			bone.matrix = bone_mat
			
	#clear empties helpers
	for object in bpy.data.objects:
		if 'empty_track' in object.name:
			bpy.data.objects.remove(object, do_unlink=True)
	
			


	
def _pick_object(action):
	obj = bpy.context.object
	scene = bpy.context.scene
	
	if action == "pick_source":
		scene.source_rig = obj.name
	if action == "pick_target":
		scene.target_rig = obj.name
	if action == 'pick_bone':
		try:
			pose_bones = obj.pose.bones
			scene.bones_map[scene.bones_map_index].name = bpy.context.active_pose_bone.name
		except:
			print("can't pick bone")
			
	if action == 'pick_pole':
		try:
			pose_bones = obj.pose.bones
			scene.bones_map[scene.bones_map_index].ik_pole = bpy.context.active_pose_bone.name
		except:
			print("can't pick bone")
		
def set_active_object(object_name):
	 bpy.context.view_layer.objects.active = bpy.data.objects[object_name]
	 bpy.data.objects[object_name].select_set(state=1)
	 
def _guess_orientation(context, guess_all):
	scene = context.scene
	tol = 45
	
	def dot_product(x, y):
		return sum([x[i] * y[i] for i in range(len(x))])

	def norm(x):
		return sqrt(dot_product(x, x))

	def normalize(x):
		return [x[i] / norm(x) for i in range(len(x))]

	def project_onto_plane(x, n):
		d = dot_product(x, n) / norm(n)
		p = [d * normalize(n)[i] for i in range(len(n))]
		return [x[i] - p[i] for i in range(len(x))]


	
	def set_orientation(bone, order, x, y, z):
		scene.bones_map[bone].axis_order = order
		scene.bones_map[bone].x_inv = x
		scene.bones_map[bone].y_inv = y
		scene.bones_map[bone].z_inv = z
		
	def tol_check(value, target, tol):
		if value < math.radians(target+tol) and value > math.radians(target-tol):
			return True
		else:
			return False
			
	#src_bone = scene.bones_map[scene.bones_map_index].source_bone
	#bone = scene.bones_map[scene.bones_map_index].name
			
	def guess_bone(src_bone, bone):	   
	
		if bone != "None" and bone != "":#if set			
			#AXIS ORDER
			#get target vectors
			bpy.ops.object.mode_set(mode='OBJECT')
			set_active_object(scene.target_rig)
			bpy.ops.object.mode_set(mode='EDIT')
			bone_target = context.active_object.data.edit_bones[bone]
			target_vec_z = bone_target.z_axis @ context.active_object.matrix_world.inverted()#world space
			target_vec_x = bone_target.x_axis @ context.active_object.matrix_world.inverted()#world space
			#target_vec_y = bone_target.y_axis * context.active_object.matrix_world.inverted()
			#target_matrix = bone_target.matrix * context.active_object.matrix_world.inverted()
			
			#get source vectors
			bpy.ops.object.mode_set(mode='OBJECT')
			set_active_object(scene.source_rig)
			bpy.ops.object.mode_set(mode='EDIT')
			bone_source = context.active_object.data.edit_bones[src_bone]
			source_vec_z= bone_source.z_axis @ context.active_object.matrix_world.inverted()#world space
			source_vec_y = bone_source.y_axis @ context.active_object.matrix_world.inverted()#world space
			z_diff = target_vec_z.angle(source_vec_z)					 
			x_diff = target_vec_x.angle(source_vec_z)		
			#source_matrix = bone_source.matrix * context.active_object.matrix_world.inverted()
			#print(math.degrees(z_diff))
			#print(math.degrees(x_diff))   
			#source_quat = source_matrix.to_quaternion()
			#target_quat = target_matrix.to_quaternion()
			
			
			
			if z_diff > math.radians(180):
				z_diff -= math.radians(360)
			if z_diff < math.radians(-180):
				z_diff += math.radians(360)			   
	   
			if tol_check(z_diff, 0, tol):
				set_orientation(bone, 'XYZ', False, False, False)
			
			if tol_check(z_diff, 90, tol):
				if tol_check(x_diff, 0, tol):					   
					set_orientation(bone, 'ZYX', False, False, True)
					#Offset Support
					#source_vec_y_p = project_onto_plane(source_vec_y, target_vec_x)	
					#x_rest_angle = bone2.z_axis.angle(bone1_z)
					"""
					source_euler = source_quat.to_euler()
					source_euler[1] += math.radians(90)
					source_quat = source_euler.to_quaternion()
					rot_diff = source_quat.rotation_difference(target_quat).to_euler()
					print(math.degrees(rot_diff[0]), math.degrees(rot_diff[2]))
					scene.bones_map[bone].offset_rot_x = -math.degrees(rot_diff[0])
					scene.bones_map[bone].offset_rot_z = -math.degrees(rot_diff[2])
					"""
				if tol_check(x_diff, 180, tol):						 
					set_orientation(bone, 'ZYX', True, False, False)
				
			if tol_check(z_diff, -180, tol) or tol_check(z_diff, 180, tol):				 
				set_orientation(bone, 'XYZ', True, False, True)
				
   
			
	if guess_all:
		for bone in scene.bones_map:
			guess_bone(bone.source_bone, bone.name)
	else:
		guess_bone(scene.bones_map[scene.bones_map_index].source_bone, scene.bones_map[scene.bones_map_index].name)
		
		
def _freeze_armature(self):

	
		
	context = bpy.context
	saved_frame = context.scene.frame_current
	context.scene.frame_set(bpy.context.scene.frame_current)		
	
	# Disable auto-keying
	bpy.context.scene.tool_settings.use_keyframe_insert_auto = False
	
	# Select the source armature
	set_active_object(context.scene.source_rig)
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.select_all(action='DESELECT')
	set_active_object(context.scene.source_rig)	

	base_arm_name = bpy.context.active_object.name
	base_action_name = bpy.context.active_object.animation_data.action.name	
	
	# is it animated?
	is_animated = False
	
	for fcurve in bpy.context.active_object.animation_data.action.fcurves:
		if not "pose.bones" in fcurve.data_path:
			if "location"in fcurve.data_path or "rotation" in fcurve.data_path or "scale" in fcurve.data_path:
				is_animated = True
				break
	
	# if not animated, just apply the rotation
	if not is_animated:
		bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
		context.scene.arp_freeze_armature_check = False
		print("Armature rotation initialized")
		return
	
	# if animated, freeze the armature animation
	else:
		# temporarily set keyframe rotation to 0
		bpy.context.active_object.rotation_euler = [0,0,0]
		bpy.context.active_object.rotation_quaternion = [0,0,0,0]
		
		# duplicate
		bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})

		bpy.context.active_object.animation_data.action.name = base_action_name + "_TEMP_COPY"
			
		# Constraint on the first armature
		bpy.ops.object.mode_set(mode='POSE')
		
		for pbone in bpy.context.active_object.pose.bones:
			cns = pbone.constraints.new('COPY_TRANSFORMS')
			cns.target = bpy.data.objects[base_arm_name]
			cns.subtarget = pbone.name
			cns.name = "arp_remap_temp"
		
		# Set frame 0
		bpy.context.scene.frame_current = 0
		bpy.context.scene.frame_set(bpy.context.scene.frame_current)			
		
		# Clear armature object keyframes	
		fcurves = bpy.context.active_object.animation_data.action.fcurves
		
		for fc_index, fc in enumerate(fcurves):
			if not "pose.bones" in fc.data_path:
				if "rotation" in fc.data_path or "location" in fc.data_path or "scale" in fc.data_path:						
					bpy.context.active_object.animation_data.action.fcurves.remove(fc)				
		
		
		
		# Apply transforms
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
		
		
		# Bake
		frame_range = bpy.context.active_object.animation_data.action.frame_range
		bpy.ops.nla.bake(frame_start=frame_range[0], frame_end=frame_range[1], visual_keying=True, only_selected = False, bake_types={'POSE'})
		
		# Delete constraints
		for pbone in bpy.context.active_object.pose.bones:
			pbone.constraints.remove(pbone.constraints["arp_remap_temp"])
			
		
		# Delete old armature
		bpy.data.objects.remove(bpy.data.objects[base_arm_name], do_unlink=True)
		bpy.context.active_object.name = base_arm_name
		
		# Delete old actions
		bpy.data.actions.remove(bpy.data.actions[base_action_name], do_unlink = True)
		try:
			bpy.data.actions.remove(bpy.data.actions[base_action_name + "_TEMP_COPY"], do_unlink = True)
		except:
			pass
		
		# Rename new action
		bpy.context.active_object.animation_data.action.name = base_action_name
		
		context.scene.frame_current = saved_frame
		context.scene.frame_set(bpy.context.scene.frame_current)

		context.scene.arp_freeze_armature_check = False
		
		print("Armature is now still.")
	
	
def _auto_scale(self, context):

	scene = context.scene
	source_rig = bpy.data.objects[scene.source_rig]
	target_rig = bpy.data.objects[scene.target_rig]
	#switch to rest pose
	source_rig.data.pose_position = 'REST'
	target_rig.data.pose_position = 'REST'
	#update	hack
	bpy.context.scene.frame_set(bpy.context.scene.frame_current)
	
	def get_armature_dim(arm_obj):
		bpy.ops.object.mode_set(mode='OBJECT')		
		bpy.ops.object.select_all(action='DESELECT')	
		set_active_object(arm_obj.name)			
		bpy.ops.object.mode_set(mode='POSE')
		
		is_arp = False
		
		# Auto-Rig Pro armature case, exclude the picker bones if any
		if bpy.context.active_object.data.bones.get("Picker"):
			is_arp = True
			
		# get the source armature dimension	
		highest = 0.0
		lowest = 100000000
		for bone in arm_obj.pose.bones:
			if is_arp:
				if bone.head[2] < 0:
					continue
					
			z_head = (arm_obj.matrix_world @ bone.head)[2]
			z_tail = (arm_obj.matrix_world @ bone.tail)[2]			
				
			if z_head > highest:
				highest = z_head			
			if z_tail > highest:
				highest = z_tail
			if z_head < lowest:
				lowest = z_head
			if z_tail < lowest:
				lowest = z_tail
			
		
		dim = highest - lowest		
		return dim
	
	
	source_dim = get_armature_dim(source_rig)
	print("source dim", source_dim)
	target_dim = get_armature_dim(target_rig)
	print("target dim", target_dim)	
	
	fac = target_dim / source_dim
	
	bpy.data.objects[scene.source_rig].scale *= fac * 0.87
	
	bpy.ops.object.mode_set(mode='OBJECT')		
	bpy.ops.object.select_all(action='DESELECT')
	
	#switch to pose position
	source_rig.data.pose_position = 'POSE'
	target_rig.data.pose_position = 'POSE'
	
	
	
def _apply_offset(self,context, value):
	scene = context.scene
	bpy.ops.object.mode_set(mode='OBJECT')		
	bpy.ops.object.select_all(action='DESELECT')
	set_active_object(scene.target_rig)	
	
	action_name = context.object.animation_data.action.name
	fcurves = bpy.data.actions[action_name].fcurves
	
	# Apply	 offset
	for f in fcurves:
		bone_name = (f.data_path.split('"')[1])		
		if "rot" in value:
			if 'rotation' in f.data_path: #rotation curves only					
				try:
					if bone_name == scene.bones_map[scene.bones_map_index].name:
						for key in f.keyframe_points: 
							
							if f.array_index == 0:	
								if "+x" in value:
									key.co[1] += scene.additive_rot
									key.handle_left[1] += scene.additive_rot
									key.handle_right[1] += scene.additive_rot
								if "-x" in value:
									key.co[1] -= scene.additive_rot
									key.handle_left[1] -= scene.additive_rot
									key.handle_right[1] -= scene.additive_rot
							if f.array_index == 1:	
								if "+y" in value:
									key.co[1] += scene.additive_rot
									key.handle_left[1] += scene.additive_rot
									key.handle_right[1] += scene.additive_rot
								if "-y" in value:
									key.co[1] -= scene.additive_rot
									key.handle_left[1] -= scene.additive_rot
									key.handle_right[1] -= scene.additive_rot
							if f.array_index == 2:	
								if "+z" in value:
									key.co[1] += scene.additive_rot
									key.handle_left[1] += scene.additive_rot
									key.handle_right[1] += scene.additive_rot
								if "-z" in value:
									key.co[1] -= scene.additive_rot
									key.handle_left[1] -= scene.additive_rot
									key.handle_right[1] -= scene.additive_rot
				except:
					pass
					
		if "loc" in value:
			if 'location' in f.data_path: #location curves only					
				try:
					if bone_name == scene.bones_map[scene.bones_map_index].name:
						for key in f.keyframe_points: 
							
							if f.array_index == 0:	
								if "+x" in value:
									key.co[1] += scene.additive_loc
									key.handle_left[1] += scene.additive_loc
									key.handle_right[1] += scene.additive_loc
								if "-x" in value:
									key.co[1] -= scene.additive_loc
									key.handle_left[1] -= scene.additive_loc
									key.handle_right[1] -= scene.additive_loc
							if f.array_index == 1:	
								if "+y" in value:
									key.co[1] += scene.additive_loc
									key.handle_left[1] += scene.additive_loc
									key.handle_right[1] += scene.additive_loc
								if "-y" in value:
									key.co[1] -= scene.additive_loc
									key.handle_left[1] -= scene.additive_loc
									key.handle_right[1] -= scene.additive_loc
							if f.array_index == 2:	
								if "+z" in value:
									key.co[1] += scene.additive_loc
									key.handle_left[1] += scene.additive_loc
									key.handle_right[1] += scene.additive_loc
								if "-z" in value:
									key.co[1] -= scene.additive_loc
									key.handle_left[1] -= scene.additive_loc
									key.handle_right[1] -= scene.additive_loc
				except:
					pass
					
		if "loc_scale" in value:
			if 'location' in f.data_path:
				try:					
					for key in f.keyframe_points:							
						if f.array_index == 0:									
								key.co[1] *= scene.loc_scale								
							
						if f.array_index == 1:									
								key.co[1] *= scene.loc_scale
						
						if f.array_index == 2:									
								key.co[1] *= scene.loc_scale								
				except:
					pass
	
	#update hack
	bpy.ops.object.mode_set(mode='OBJECT')	
	current_frame = bpy.context.scene.frame_current#save current frame
	bpy.context.scene.frame_set(bpy.context.scene.frame_current)#debug	

def _cancel_redefine():

	scene = bpy.context.scene	
	source_rig = bpy.data.objects[scene.source_rig]
	source_rig_copy =  bpy.data.objects[scene.source_rig + "_copy"]
	
	source_rig.data.pose_position = 'POSE'
	source_rig.animation_data.action = source_rig_copy.animation_data.action
	
	bpy.data.objects.remove(source_rig_copy, do_unlink=True)
	
	
	 
def _copy_raw_coordinates(self, context):

	
	scene = bpy.context.scene
	bpy.data.objects[scene.target_rig].data.pose_position = 'POSE'
	source_rig = bpy.data.objects[scene.source_rig]
	source_rig_copy =  bpy.data.objects[scene.source_rig + "_copy"]
	_action = source_rig_copy.animation_data.action
	action_name = _action.name
	fcurves = bpy.data.actions[action_name].fcurves
	frame_range = _action.frame_range
	current_frame = bpy.context.scene.frame_current#save current frame
	
	# Ensure the source armature selection
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.select_all(action='DESELECT')
	set_active_object(scene.source_rig)
	bpy.ops.object.mode_set(mode='POSE')

	
	# Apply as rest pose
	bpy.ops.pose.select_all(action='SELECT')
	bpy.ops.pose.armature_apply()
	
	# Bake constraints (faster)
	source_rig_copy.location = source_rig.location
		
		# Add constraints
	print("add constraints...")
	for bone in source_rig.pose.bones:
		cns = bone.constraints.new('COPY_TRANSFORMS')
		cns.name = 'arp_redefine'
		cns.target = source_rig_copy
		cns.subtarget = bone.name
	
		# Bake
	print("bake...")
	bpy.ops.nla.bake(frame_start=frame_range[0], frame_end=frame_range[1], visual_keying=True, bake_types={'POSE'})
		
		# Delete constraints
	print("delete constraints...")
	for bone in source_rig.pose.bones:
		if len(bone.constraints) > 0:
			for cns in bone.constraints:
				if cns.name == 'arp_redefine':
					bone.constraints.remove(cns)
	

	# Restore current frame
	bpy.context.scene.frame_current = current_frame
	bpy.context.scene.frame_set(bpy.context.scene.frame_current)#debug	

	bpy.data.objects.remove(source_rig_copy, do_unlink=True)
	print("Redefining done.")

def _rig_setup(inherit):

	scene = bpy.context.scene	
	obj = bpy.context.object
	pose_bones = obj.pose.bones	  
	
	if inherit:
		# arms and heads will inherit rotation from parent
		try:
			get_edit_bone("c_arm_fk.l").parent = get_edit_bone("c_shoulder.l")
			get_edit_bone("c_arm_fk.r").parent = get_edit_bone("c_shoulder.r")
			get_edit_bone("c_head_scale_fix.x").parent = get_edit_bone("neck.x")
		except:
			print("Setup ARP Armature: Not an Auto-Rig Pro armature. Skip.")
	else:
		# arms and head won't inherit rotation (default AutoRig Pro behaviour)
		try:
			get_edit_bone("c_arm_fk.l").parent = get_edit_bone("c_spine_02.x")
			get_edit_bone("c_arm_fk.r").parent = get_edit_bone("c_spine_02.x")
			get_edit_bone("c_head_scale_fix.x").parent = get_edit_bone("c_traj")
		except:
			print("Setup ARP Armature: Not an Auto-Rig Pro armature. Skip.")
	
	
	

		
def node_names_items(self, context): 
	# make a list of the names
	items = []

	if context is None:
		return items	
	
	i = 1
	names_string = context.scene.source_nodes_name_string
	if names_string != "":
		for name in names_string.split("+"):
			items.append((name, name, name, i))
			i += 1			 
	else:
		items.append(("None", "None", "None"))	

	return items
	
def node_axis_items(self, context):	 
	items=[]   
	items.append(('XYZ', 'XYZ', 'Default axis order', 1))
	items.append(('ZYX', 'ZYX', 'Typical', 2))
	items.append(('XZY', 'XZY', 'Less used', 3))

	
	return items


def _build_bones_list():
	
	scene = bpy.context.scene
	#select the target rig	 
	bpy.ops.object.select_all(action='DESELECT')
	set_active_object(scene.target_rig)		 
		
	pose_bones = bpy.context.object.pose.bones	 
	obj = bpy.context.object  

	# Get source action bone names	   
	scene.source_nodes_name_string = ""	   
	fcurves = bpy.data.actions[scene.source_action].fcurves
	
	#clear the collection
	if len(scene.bones_map) > 0:
		i = len(scene.bones_map)
		while i >= 0:		   
			scene.bones_map.remove(i)
			i -= 1
			
	# add the auto-rig pro bones to the collection
	bones_dict = {'head':['01','c_head.x'], 'neck':['02','c_neck.x'], 'spine_02':['03','c_spine_02.x'], 'spine_01': ['04','c_spine_01.x'],
						'root': ['05','c_root_master.x'], 'thighl': ['06','c_thigh_fk.l'], 'thighr':['07','c_thigh_fk.r'], 'legl': ['08','c_leg_fk.l'], 'legr':['09','c_leg_fk.r'], 'footl':['10','c_foot_fk.l'], 'footr':['11','c_foot_fk.r'], 'shoulderl':['12','c_shoulder.l'], 'shoulderr':['13','c_shoulder.r'], 'arml':['14','c_arm_fk.l'], 'armr':['15','c_arm_fk.r'], 'forearml':['16','c_forearm_fk.l'],'forearmr':['17','c_forearm_fk.r'], 'handl':['18','c_hand_fk.l'], 'handr':['19','c_hand_fk.r']
						} 
	
	#dict_sorted = sorted(bones_dict.items(), key=operator.itemgetter(1))
	 
	# create a string containing all the source bones names
	for f in fcurves:	 
		#bone_name = f.data_path.split('"')[1]
		string = f.data_path[12:]
		bone_name = string.partition('"')[0]
		#print(string.partition('"'))
		#print(string.partition('"')[0])
		# add bones names to the string list
		if f.array_index == 0 and 'rotation' in f.data_path:#avoid unwanted iterations
			scene.source_nodes_name_string += bone_name + "+"
	
	
	# create the collection items, one per source bone
	for i in scene.source_nodes_name_string.split("+"):
		if i != "":
			item = scene.bones_map.add()	   
			item.name = 'None'	
			item.source_bone = i
			item.axis_order = 'XYZ'
			item.x_inv = False
			item.y_inv = False
			item.z_inv = False
			
	pose_bones_list = []	
	is_arp_armature = False
	
	if pose_bones.get("c_traj") and pose_bones.get("c_pos"):
		is_arp_armature = True
		
		
	for b in pose_bones:
		if is_arp_armature:
			if b.name[:2] == "c_":
				pose_bones_list.append(b.name)
		else:
			pose_bones_list.append(b.name)
		
	# guess linked bones, try to find Auto-Rig Pro bones match, if not lambda name match
	for item in scene.bones_map:  
		found = False
			
		if 'head' in item.source_bone.lower():
			if pose_bones.get("c_head.x"):
				item.name = 'c_head.x'
				found = True
		  
		if 'neck' in item.source_bone.lower():
			if pose_bones.get("c_neck.x"):
				item.name = 'c_neck.x'
				found = True			
				   
		if 'abdomen' in item.source_bone.lower() or 'spine' in item.source_bone.lower():
			if pose_bones.get("c_spine_01.x"):
				item.name= 'c_spine_01.x'
				found = True
		
		if 'chest' in item.source_bone.lower() or 'spine2' in item.source_bone.lower():
			if pose_bones.get("c_spine_02.x"):
				item.name='c_spine_02.x'
				found = True
		 
		if 'hip' in item.source_bone.lower():
			if pose_bones.get("c_root_master.x"):
				item.name='c_root_master.x'
				found = True
				
		if 'tospine' in item.source_bone.lower():
			if pose_bones.get("c_root_master.x"):
				item.name='None'
				found = True	

				  
		if 'rcollar' in item.source_bone.lower() or ('right' in item.source_bone.lower() and 'shoulder' in item.source_bone.lower()):
			if pose_bones.get("c_shoulder.r"):
				item.name='c_shoulder.r'
				found = True
		  
		if 'lcollar' in item.source_bone.lower() or ('left' in item.source_bone.lower() and 'shoulder' in item.source_bone.lower()):
			if pose_bones.get("c_shoulder.l"):
				item.name='c_shoulder.l'
				found = True
		  
		if 'rshldr' in item.source_bone.lower() or ('right' in item.source_bone.lower() and 'arm' in item.source_bone.lower() and not 'fore' in item.source_bone.lower()):
			if pose_bones.get("c_arm_fk.r"):
				item.name='c_arm_fk.r'
				found = True
		   
		if 'lshldr' in item.source_bone.lower() or ('left' in item.source_bone.lower() and 'arm' in item.source_bone.lower() and not 'fore' in item.source_bone.lower()):
			if pose_bones.get("c_arm_fk.r"):
				item.name='c_arm_fk.l'
				found = True
		   
		if 'rforearm' in item.source_bone.lower() or ('right' in item.source_bone.lower() and 'forearm' in item.source_bone.lower()):
			if pose_bones.get("c_forearm_fk.r"):
				item.name='c_forearm_fk.r'
				found = True
		   
		if 'lforearm' in item.source_bone.lower() or ('left' in item.source_bone.lower() and 'forearm' in item.source_bone.lower()):
			if pose_bones.get("c_forearm_fk.l"):
				item.name='c_forearm_fk.l'
				found = True
			
		if 'rhand' in item.source_bone.lower() or ('right' in item.source_bone.lower() and 'hand' in item.source_bone.lower()):
			if pose_bones.get("c_hand_fk.r"):
				item.name='c_hand_fk.r'
				found = True
			
		if 'lhand' in item.source_bone.lower() or ('left' in item.source_bone.lower() and 'hand' in item.source_bone.lower()):
			if pose_bones.get("c_hand_fk.l"):
				item.name='c_hand_fk.l'
				found = True
		   
		if 'lthigh' in item.source_bone.lower() or ('left' in item.source_bone.lower() and 'thigh' in item.source_bone.lower()) or ('left' in item.source_bone.lower() and 'upleg' in item.source_bone.lower()):
			if pose_bones.get("c_thigh_fk.l"):
				item.name='c_thigh_fk.l'
				found = True			   
		   
		if 'rthigh' in item.source_bone.lower() or ('right' in item.source_bone.lower() and 'thigh' in item.source_bone.lower()) or ('right' in item.source_bone.lower() and 'upleg' in item.source_bone.lower()):
			if pose_bones.get("c_thigh_fk.r"):
				item.name='c_thigh_fk.r'
				found = True
				
		   
		if 'lshin' in item.source_bone.lower() or ('left' in item.source_bone.lower() and 'leg' in item.source_bone.lower() and not 'up' in item.source_bone.lower()):
			if pose_bones.get("c_leg_fk.l"):
				item.name='c_leg_fk.l'
				found = True
			
		if 'rshin' in item.source_bone.lower() or ('right' in item.source_bone.lower() and 'leg' in item.source_bone.lower() and not 'up' in item.source_bone.lower()):
			if pose_bones.get("c_leg_fk.r"):
				item.name='c_leg_fk.r'
				found = True
			
		if 'lfoot' in item.source_bone.lower() or ('left' in item.source_bone.lower() and 'foot' in item.source_bone.lower()):
			if pose_bones.get("c_foot_fk.l"):
				item.name='c_foot_fk.l'
				found = True
		   
		if 'rfoot' in item.source_bone.lower() or ('right' in item.source_bone.lower() and 'foot' in item.source_bone.lower()):
			if pose_bones.get("c_foot_fk.r"):
				item.name='c_foot_fk.r'
				found = True	
		
		finger_list = ['thumb', 'index', 'middle', 'ring', 'pinky']
		for fing in finger_list:
			for side in ['l', 'r']:
				for fing_idx in ['1', '2', '3']:
				
					full_side = ""
					if side == 'l':
						full_side = 'left'
					if side == 'r':
						full_side = 'right'
						
					# look for lThumb1 or LeftThumb1 or Thumb1_l or Thumb1_left or LeftHandThumb1
					item_name = item.source_bone.lower()
					if (fing+fing_idx+'_'+side) in item_name or (side+fing+fing_idx) in item_name or (full_side in item_name and fing+fing_idx in item_name):
						
						if pose_bones.get('c_'+fing+fing_idx+'.'+side):
							item.name = 'c_'+fing+fing_idx+'.'+side
							found = True

		
		
		
		if found == False:
			try:
				#print(item.source_bone,">", difflib.get_close_matches(item.source_bone, pose_bones_list)[0])				 
				item.name = difflib.get_close_matches(item.source_bone, pose_bones_list)[0]				  
			except:
				#print(item.source_bone,">None")
				pass
				
	scene.bones_map_index = 0
			

		   

def _set_as_root(): 
	  
	scene = bpy.context.scene
	bpy.ops.object.mode_set(mode='OBJECT') 
	
	if scene.remap_mode == 'manual':
		#select the source rig
		bpy.ops.object.select_all(action='DESELECT')
		set_active_object(scene.source_rig)		 
		bpy.ops.object.mode_set(mode='EDIT')	
	 
		#get hips bone		 
		hips_edit_bone = get_edit_bone(scene.bones_map[scene.bones_map_index].source_bone)
		hips_vec = hips_edit_bone.tail - hips_edit_bone.head
		hips_roll = hips_edit_bone.roll
		#select the target rig
		bpy.ops.object.mode_set(mode='OBJECT')		  
		bpy.ops.object.select_all(action='DESELECT')
		set_active_object(scene.target_rig)		   
		bpy.ops.object.mode_set(mode='EDIT')  
		#get hips bone		 
		hips_def_edit_bone = get_edit_bone(scene.bones_map[scene.bones_map_index].name)
		vec_length = (hips_def_edit_bone.tail-hips_def_edit_bone.head).length
		length_fac = vec_length/hips_vec.length		   
		hips_def_edit_bone.tail = hips_def_edit_bone.head + hips_vec*length_fac
		hips_def_edit_bone.roll = hips_roll
	
	"""
	if scene.remap_mode == 'auto':
		scene.root_bone = scene.bones_map[scene.bones_map_index].name
		print(scene.root_bone)
	"""
	bpy.ops.object.mode_set(mode='OBJECT')		   
		

   
def _retarget(self):
	
	scene = bpy.context.scene	
	context = bpy.context
	source_rig = bpy.data.objects[scene.source_rig]	
	
	
	#make sure the target armature is visible
	armature_hidden = bpy.data.objects[scene.target_rig].hide_viewport
	bpy.data.objects[scene.target_rig].hide_viewport = False	  
	current_frame = bpy.context.scene.frame_current#save current frame
		
		
	# proxy?			
	target_proxy_name = None
	
	if bpy.data.objects[scene.target_rig].proxy:			
		target_proxy_name = bpy.data.objects[scene.target_rig].proxy.name
		print("The target armature is a proxy. Real name = ", target_proxy_name)
		
	
	#select the target rig 
	bpy.ops.object.mode_set(mode='OBJECT')		
	bpy.ops.object.select_all(action='DESELECT')
	set_active_object(scene.target_rig)		

	if target_proxy_name != None:
		bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
		bpy.context.active_object.name = scene.target_rig + "_local"

	bpy.ops.object.mode_set(mode='OBJECT')	
	bpy.ops.object.select_all(action='DESELECT')
	set_active_object(scene.target_rig)	
	
	# setup ARP armature
	bpy.ops.object.mode_set(mode='EDIT')	
	_rig_setup(scene.arp_inherit_rot) 
	bpy.ops.object.mode_set(mode='POSE')  
	
	#Manual mode, hidden feature
	if scene.remap_mode == 'manual':	

		# Set the source action on the target rig
		pose_bones = bpy.context.object.pose.bones	 
		obj = bpy.context.object  
		action_copy = bpy.data.actions[scene.source_action].copy()

		try:
			obj.animation_data.action = bpy.data.actions.get(action_copy.name)
		except AttributeError:
			obj.animation_data_create()
			obj.animation_data.action = bpy.data.actions.get(action_copy.name)


			#get fcurves
		fcurves = obj.animation_data.action.fcurves
		
		#REMAP NAMES AND LOCATION SCALE
		for fcurve in fcurves:	
			try:
				bone_source_name = (fcurve.data_path.split('"')[1])
			except:#invalid data path
				continue
			for bone in scene.bones_map:
				if bone.source_bone == bone_source_name:
					bone_target_name = bone.name
					
			
			bone_exists = False
			try:
				pose_bones[bone_target_name]
				# only if a target bone is set for this source bone
				if scene.bones_map[bone_target_name].source_bone == bone_source_name:			 
					bone_exists = True
			except:			
				pass
				
			if bone_exists: #if exists	 
				# map the new target bone			
				fcurve.data_path = fcurve.data_path.replace(bone_source_name, bone_target_name)
				
				#apply scale on location
				if 'location' in fcurve.data_path:
					for key in fcurve.keyframe_points:
						key.co[1] *= scene.global_scale			  
				
			else:
				#delete the fcurve otherwise
				fcurves.remove(fcurve)
				
		# REMAP AXES
		fcurves = obj.animation_data.action.fcurves
		
		for f in fcurves:
			try:
				bone_name = (f.data_path.split('"')[1])
			except:#invalid 
				continue
		   
			# default values
			axis_order = 'XYZ'
			x_inv = False
			y_inv = False
			z_inv = False
			
			# get target bone properties values
			for bone in scene.bones_map:
				try:
					pose_bones[bone.name] #check the bone exists
					if bone.name in f.data_path:					
						axis_order = bone.axis_order			   
						x_inv = bone.x_inv
						y_inv = bone.y_inv
						z_inv = bone.z_inv	 
				   
				except KeyError:
					pass
	 
			# Switch axes
			if axis_order == 'ZYX':
				fcurves.find(f.data_path, 0).array_index = 10 #switch X to temp 10 index
				fcurves.find(f.data_path, 2).array_index = 0 # switch Z to X
				fcurves.find(f.data_path, 10).array_index = 2 # switch 10 to Z
				
				pose_bones[bone_name].rotation_mode = 'ZYX'			  
		  
			if axis_order == 'XZY':
				fcurves.find(f.data_path, 1).array_index = 10 #switch Y to temp 10 index
				fcurves.find(f.data_path, 2).array_index = 1 # switch Z to Y
				fcurves.find(f.data_path, 10).array_index = 2 # switch 10 to Z
				pose_bones[bone_name].rotation_mode = 'XZY'
			
			if axis_order == 'XYZ':
				pose_bones[bone_name].rotation_mode = 'XYZ'
				
				# negate axis if enabled
			if x_inv and f.array_index == 0 and not 'scale' in f.data_path :
				for key in f.keyframe_points:
					key.co[1] *= -1
			if y_inv and f.array_index == 1 and not 'scale' in f.data_path :
				for key in f.keyframe_points:
					key.co[1] *= -1
			if z_inv and f.array_index == 2 and not 'scale' in f.data_path :
				for key in f.keyframe_points:
					key.co[1] *= -1
			
		# Remove initial offset if enabled
			if scene.remove_offset:			 
				offset = 0
				for key in f.keyframe_points:
					if key.co[0] == 1: #find offset on the first frame
						offset = key.co[1]
				# offset all curve
				for key in f.keyframe_points:
					key.co[1] += -offset
					
		# Apply rotation offset
			if 'rotation' in f.data_path: #rotation curves only
				for key in f.keyframe_points: 
					if f.array_index == 0:					  
						key.co[1] += math.radians(scene.bones_map[bone_name].offset_rot_x)
					if f.array_index == 1:					  
						key.co[1] += math.radians(scene.bones_map[bone_name].offset_rot_y)
					if f.array_index == 2:					  
						key.co[1] += math.radians(scene.bones_map[bone_name].offset_rot_z)
						

	if scene.remap_mode == 'auto':
		
		#set source armature at target armature position
		source_armature_init_pos = bpy.data.objects[scene.source_rig].location.copy()		
		bpy.data.objects[scene.source_rig].location = bpy.data.objects[scene.target_rig].location		
		
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		
		if target_proxy_name == None:
			set_active_object(scene.target_rig)
		else:
			set_active_object(scene.target_rig + "_local")
			
		bpy.ops.object.mode_set(mode='EDIT')
		
		#create a transform dict of target bones
		bones_dict = {}	
		
		for edit_bone in context.object.data.edit_bones:
			bones_dict[edit_bone.name] = source_rig.matrix_world.inverted() @ edit_bone.head.copy(), source_rig.matrix_world.inverted() @ edit_bone.tail.copy(), mat3_to_vec_roll(source_rig.matrix_world.inverted().to_3x3() @ edit_bone.matrix.to_3x3())#edit_bone.roll			
			
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		set_active_object(scene.source_rig)
		frame_range = context.active_object.animation_data.action.frame_range
		bpy.ops.object.mode_set(mode='EDIT')
		
		
		print("Creating Bones...")
		ik_chains = {}
		
		#create bones	
		for bone in scene.bones_map:
			if bone.name != "" and bone.name != "None" and context.object.data.edit_bones.get(bone.source_bone) and bone.name in bones_dict:				
				#create a bone
				new_bone = context.object.data.edit_bones.new(bone.name+"_REMAP")				
				new_bone.head, new_bone.tail, new_bone.roll = bones_dict[bone.name]
				new_bone.parent = get_edit_bone(bone.source_bone)				
				
				#ik bones
				if bone.ik and bone.ik_pole != "":
					#track bone
					track_bone_name = bone.name+"_IK_REMAP"
					track_bone = context.object.data.edit_bones.new(track_bone_name)			
					
					bone_parent_1 = context.object.data.edit_bones[bone.source_bone].parent
					bone_parent_1_name = bone_parent_1.name
					bone_parent_2 = bone_parent_1.parent
					bone_parent_2_name = bone_parent_2.name
					
					#Check for ik chains straight alignment					
					if bone_parent_1.y_axis.angle(bone_parent_2.y_axis) == 0.0:
						print("Warning: Straight IK chain (" + bone.name + "), adding offset...")
						#find foot direction if any
						bone_vec = None
						for ed_bone in context.active_object.data.edit_bones:
							if 'foot' in ed_bone.name.lower():
								print("	   found a foot bone as reference for offset")
								bone_vec = ed_bone.tail - ed_bone.head
								break
						#else, get the current bone vector... not the good way to find the elbow direction :-(
						if bone_vec == None:		
							bone_vec = get_edit_bone(bone.source_bone).tail - get_edit_bone(bone.source_bone).head
						
						if 'hand' in bone.name.lower():
							bone_vec *= -1
							
						#offset the middle position
						bone_parent_1.head += bone_vec/5
						bone_parent_2.tail += bone_vec/5
							
					#track_bone coords
					track_bone.head = (bone_parent_1.tail + bone_parent_2.head)/2
					track_bone.tail = bone_parent_1.head					
					
					ik_chains[bone.source_bone] = [bone_parent_1_name, bone_parent_2_name, bone.ik_pole]
					
					# Fk pole
					fk_pole_name = bone.name+"_FK_POLE_REMAP"
					fk_pole = context.object.data.edit_bones.new(fk_pole_name)
					fk_pole.head = track_bone.tail + (track_bone.tail - track_bone.head)*60
					fk_pole.tail = fk_pole.head + (track_bone.tail - track_bone.head)*2
					
					if bone.ik_auto_pole:
						# auto pole, just parent the FK pole to the foot/hand...
						fk_pole.parent = get_edit_bone(bone.source_bone)
					else:
						# otherwise parent to the track bone to calculate the IK orientation
						fk_pole.parent = track_bone
					
					# Add constraints
					bpy.ops.object.mode_set(mode='POSE')
					p_track_bone = context.object.pose.bones[track_bone_name]					
					
					cns = p_track_bone.constraints.new('COPY_LOCATION')
					cns.target = context.object
					cns.subtarget = bone_parent_2_name
					cns.name += 'REMAP'
					
					cns = p_track_bone.constraints.new('COPY_LOCATION')
					cns.target = context.object
					cns.subtarget = bone_parent_1_name
					cns.head_tail = 1.0
					cns.influence = 0.5
					cns.name += 'REMAP'
					
					cns = p_track_bone.constraints.new('TRACK_TO')
					cns.target = context.object
					cns.subtarget = bone_parent_1_name				
					cns.influence = 1.0
					cns.name += 'REMAP'
					
					bpy.ops.object.mode_set(mode='EDIT')
					
										
		
		print("IK CHAINS:", ik_chains)
		
		print("Adding constraints...")
		#add constraints
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		set_active_object(scene.target_rig)
		bpy.ops.object.mode_set(mode='POSE')  
	
		for bone_target in scene.bones_map:
		
			if bone_target.name != "" and bone_target.name != "None" and context.object.pose.bones.get(bone_target.name):
				#select it
				pose_bone = context.object.pose.bones[bone_target.name]
				context.object.data.bones.active = pose_bone.bone	  
				
				#add constraints				
				cns = pose_bone.constraints.new('COPY_ROTATION')
				cns.target = bpy.data.objects[scene.source_rig]
				cns.subtarget = bone_target.name + "_REMAP"
				cns.name += 'REMAP'				
				
				
				if bone_target.ik or bone_target.set_as_root:
					cns = pose_bone.constraints.new('COPY_LOCATION')
					cns.target = bpy.data.objects[scene.source_rig]
					if bone_target.set_as_root:
						#cns.subtarget = "offset_bone_root_REMAP"
						cns.subtarget = bone_target.source_bone			
					else:
						cns.subtarget = bone_target.source_bone									
					cns.name += 'REMAP'
					
					if bone_target.ik_pole != "":
						pole = context.object.pose.bones[bone_target.ik_pole]
						cns = pole.constraints.new('COPY_LOCATION')
						cns.target = bpy.data.objects[scene.source_rig]
						cns.subtarget = bone_target.name+"_FK_POLE_REMAP"
						cns.name += 'REMAP'
						context.object.data.bones.active = context.object.pose.bones[bone_target.ik_pole].bone
						
						if "pole_parent" in pole.keys():
							pole['pole_parent'] = 0
						
		
		print("Baking constraints [" + str(frame_range[0]) + "-" + str(frame_range[1]) + "]")
		
		#bake constraints			
		bpy.ops.nla.bake(frame_start=frame_range[0], frame_end=frame_range[1], visual_keying=True, only_selected = True, bake_types={'POSE'})		
					
		#Change action name
		bpy.data.objects[scene.target_rig].animation_data.action.name = bpy.data.objects[scene.source_rig].animation_data.action.name + '_remap'
		
		print("Deleting constraints...")
		# Delete remap constraints
		for pose_bone in context.object.pose.bones:				
			
			for cns in pose_bone.constraints:
				if 'REMAP' in cns.name:
					pose_bone.constraints.remove(cns)
					
		bpy.ops.pose.select_all(action='DESELECT')

		""" useless there...
		# Set inverse for child of constraints of IK
		for bone_target in scene.bones_map:		
			if bone_target.name != "" and bone_target.name != "None":				
				pose_bone = context.object.pose.bones[bone_target.name]			
				if bone_target.ik:					
					if bone_target.ik_pole != "":
						pole = context.object.pose.bones[bone_target.ik_pole]
						for cns in pole.constraints:
							if cns.name == "Child Of_local":
								if bpy.context.object.pose.bones.get(cns.subtarget) != None:
									parent_bone = bpy.context.object.pose.bones[cns.subtarget]
									bpy.ops.transform.translate(value=(0, 0, 0))# udpate
									cns.inverse_matrix = parent_bone.matrix.inverted()										
									print("Set inverse constraint", cns.name)
									
		"""			
		
		print("Deleting bones...")
		# Delete helper bones
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		set_active_object(scene.source_rig)
		bpy.ops.object.mode_set(mode='EDIT')  
		
		for edit_bone in context.object.data.edit_bones:
			if '_REMAP' in edit_bone.name:
				 context.object.data.edit_bones.remove(edit_bone)
				 
		bpy.ops.object.mode_set(mode='OBJECT')
		
		#Clean IK poles when chains are straight			
		action_name = bpy.data.objects[scene.source_rig].animation_data.action.name
		fcurves = bpy.data.actions[action_name].fcurves
		angle_tolerance = 5
		
		for keyframe in fcurves[0].keyframe_points:
			#check angle at each frames			
			bpy.context.scene.frame_current = keyframe.co[0]
			bpy.context.scene.frame_set(bpy.context.scene.frame_current)#debug	
			
			for key, value in ik_chains.items():
				bone1 = bpy.data.objects[scene.source_rig].pose.bones[value[0]]
				bone2 = bpy.data.objects[scene.source_rig].pose.bones[value[1]]
				chain_angle = bone1.y_axis.angle(bone2.y_axis)
				
				if math.degrees(chain_angle) < angle_tolerance:
					#remove keyframe, just interpolate
					pole_bone = bpy.data.objects[scene.target_rig].pose.bones[value[2]]
					pole_bone.keyframe_delete(data_path = "location")				
		
		
		#restore source rig pos
		bpy.data.objects[scene.source_rig].location = source_armature_init_pos	
		
		#update hack
		bpy.ops.object.mode_set(mode='OBJECT')	
		current_frame = bpy.context.scene.frame_current#save current frame
		bpy.context.scene.frame_set(bpy.context.scene.frame_current)#debug		
	
	
	
	# Restore Initial armature visibility
	bpy.data.objects[scene.target_rig].hide_viewport = armature_hidden 
	
	# Delete proxy local copy if any
	if bpy.data.objects.get(scene.target_rig + "_local") != None:
		bpy.data.objects.remove(bpy.data.objects[scene.target_rig + "_local"], do_unlink=True)
	
	print("Retargetting done.\n")
	
	
	
def update_spine_root(self, context):
	scene = context.scene
	# set all other 'set_as_root' property False (only one possible)  
	for i in range(0,len(scene.bones_map)):
		if scene.bones_map[i].set_as_root and i != scene.bones_map_index:
			scene.bones_map[i].set_as_root = False	

			
class CustomProp(bpy.types.PropertyGroup):
	'''name = bpy.props.StringProperty() '''
	# Properties of each item
	source_bone : bpy.props.EnumProperty(items=node_names_items, name = "Source	 List", description="Source Bone Name")
	axis_order : bpy.props.EnumProperty(items=node_axis_items, name = "Axis Orders Switch", description="Axes Order")
	x_inv : bpy.props.BoolProperty(name = "X Axis Inverted", default = False, description = 'Inverse the X axis')
	y_inv : bpy.props.BoolProperty(name = "Y Axis Inverted", default = False, description = 'Inverse the Y axis')
	z_inv : bpy.props.BoolProperty(name = "Z Axis Inverted", default = False, description = 'Inverse the Z axis')
	id : bpy.props.IntProperty()
	set_as_root : bpy.props.BoolProperty(name = "Set As Root", default = False, description = 'Set this bone as the root (hips) of the armature ', update=update_spine_root)
	offset_rot_x : bpy.props.FloatProperty(name = "Offset X Rotation", default = 0.0, description = 'Offset X rotation value')
	offset_rot_y : bpy.props.FloatProperty(name = "Offset Y Rotation", default = 0.0, description = 'Offset Y rotation value')
	offset_rot_z : bpy.props.FloatProperty(name = "Offset Z Rotation", default = 0.0, description = 'Offset Z rotation value')
	
	ik : bpy.props.BoolProperty(name="IK", default = False, description="Use IK for this bone (precise hands, feet tracking)")
	ik_pole : bpy.props.StringProperty(default="", description="IK pole bone (arms, legs pole)")
	ik_auto_pole : bpy.props.BoolProperty(name="Auto Pole", default = False, description = "The pole bone will inherit the target bone transforms, instead of trying to match the IK chain orientation.\nUseful for legs, knees poles.")

	
def _export_config(): 
	scene=bpy.context.scene
	filepath = bpy.path.abspath(scene.file_path)
	
	#add extension
	if filepath[-5:] != ".bmap":
		filepath += ".bmap"
		scene.file_path += ".bmap"
		
	file = open(filepath, "w", encoding="utf8", newline="\n")
	
	for item in scene.bones_map:
		file.write(item.name+"\n") 
		file.write(item.source_bone+"\n")
		"""
		file.write(item.axis_order+"\n")
		file.write(str(item.x_inv)+"\n")
		file.write(str(item.y_inv)+"\n")
		file.write(str(item.z_inv)+"\n")
		file.write(str(item.set_as_root)+"\n")
		file.write(str(item.offset_rot_x)+"\n")
		file.write(str(item.offset_rot_y)+"\n")
		file.write(str(item.offset_rot_z)+"\n")
		"""
		file.write(str(item.set_as_root)+"\n")
		file.write(str(item.ik)+"\n")
		file.write(item.ik_pole+"\n")
		
	# close file
	file.close()
		
def _import_config(self, context):
 
	scene = bpy.context.scene	
	bones_not_found = []
	
	try:
		file = open(bpy.path.abspath(scene.file_path), 'rU')
	except:
		self.report({'ERROR'}, "The file path seems invalid.")
		return
		
	file_lines = file.readlines()
	total_lines = len(file_lines)
	props_count = 5
	bone_counts = total_lines / props_count
	
	#clear the bone collection
	if len(scene.bones_map) > 0:
		i = len(scene.bones_map)
		while i >= 0:		   
			scene.bones_map.remove(i)
			i -= 1
	
	
	#import items
	line = 0	
	error_load = False
	
	# is there a prefix?
	prefix = ""
	prefix = scene.source_nodes_name_string.split("+")[0].split(":")[0]			
	if prefix != "":
		print("Found prefix:", prefix)
	
	for i in range(0, int(bone_counts)):
		#add item		
		item = scene.bones_map.add()
		item.name = str(file_lines[line+0]).rstrip()
		
		found_name = False
		
		for n in scene.source_nodes_name_string.split("+"):			
			if scene.search_and_replace:
				if n == str(file_lines[line+1]).rstrip().replace(scene.name_search, scene.name_replace):				
					item.source_bone = str(file_lines[line+1]).rstrip().replace(scene.name_search, scene.name_replace)
					found_name = True
			else:
				if n == str(file_lines[line+1]).rstrip():					
					item.source_bone = str(file_lines[line+1]).rstrip()
					found_name = True
				# try to add the prefix and see if there's a match
				elif n == prefix + ":" + str(file_lines[line+1]).rstrip():
					item.source_bone = prefix + ":" + str(file_lines[line+1]).rstrip()					
					found_name = True
					print("Found match without prefix:", n, ">", str(file_lines[line+1]).rstrip())
			
		if not found_name:
		
			bones_not_found.append(str(file_lines[line+1]).rstrip())			
			error_load = True
			line += props_count
			continue
		
		item.set_as_root = string_to_bool(str(file_lines[line+2]).rstrip())
		item.ik = string_to_bool(str(file_lines[line+3]).rstrip())
		item.ik_pole = str(file_lines[line+4]).rstrip()
	   
		line += props_count
	
	# close file
	file.close()
	if len(bones_not_found) > 0:
		self.report({'ERROR'}, "Some preset bones do not exist in the armature:")
		for i in bones_not_found:
			self.report({'ERROR'}, i)
	
	#rebuild bone list in case of error
	#if error_load:
	#	build_bones_list.execute(self, context)

def string_to_bool(string):
	if string.lower() == 'true':
		return True
	if string.lower() == 'false':
		return False

def set_global_scale(context):
	source_rig = bpy.data.objects[context.scene.source_rig]
	target_rig = bpy.data.objects[context.scene.target_rig]
	try:
		context.scene.global_scale = source_rig.scale[0] / target_rig.scale[0]
	except:
		pass
		

		
def update_source_rig(self, context):
	if context.scene.source_rig != "":
		arm_obj = bpy.data.objects[context.scene.source_rig]
		context.scene.source_action = arm_obj.animation_data.action.name
		
		# is rotation initialized?
		for rot_axis in arm_obj.rotation_euler:
			if round(rot_axis, 3) != 0.0:
				context.scene.arp_freeze_armature_check = True		
				return
				
		# is the armature animated?	
		for fcurve in arm_obj.animation_data.action.fcurves:
			if not "pose.bones" in fcurve.data_path:
				if "location"in fcurve.data_path or "rotation" in fcurve.data_path or "scale" in fcurve.data_path:
					context.scene.arp_freeze_armature_check = True					
					return

	else:
		context.scene.arp_freeze_armature_check = False			
	
	#set global scale
	if context.scene.source_rig != "" and context.scene.target_rig != "":
		set_global_scale(context)
	
def update_target_rig(self,context):
	
	#set global scale
	if context.scene.source_rig != "" and context.scene.target_rig != "":
		set_global_scale(context)
	 

def entries_are_set():
	scene = bpy.context.scene
	
	if scene.source_action != "" and scene.source_rig != "" and scene.target_rig != "":
		return True
	else:
		return False
	
###########	 UI PANEL  ###################

class ARP_PT_auto_rig_remap_panel(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "ARP" 
	bl_label = "Auto-Rig Pro: Remap"
	bl_idname = "id_auto_rig_remap"
	bl_options = {'DEFAULT_CLOSED'}
	
	

	def draw(self, context):
		layout = self.layout
		object = context.object
		scene = context.scene
	
		#dict_sorted = sorted(bones_dict.items(), key=operator.itemgetter(1))

		#BUTTONS		  
		layout.label(text="Source Armature:")
		row = layout.row(align=True)		
		row.prop_search(scene, "source_rig", bpy.data, "objects", text="")
		row.operator("arp.pick_object", text="", icon='EYEDROPPER').action = 'pick_source' 
		if scene.arp_freeze_armature_check:
			layout.label(text="-- Source armature not initialized. Freeze it first below --", icon="ERROR")		
			col = layout.column(align=True)		
			col.operator("arp.freeze_armature", text="Freeze Source Armature")
		
		
		layout.label(text="Target Armature:")
		row = layout.row(align=True)		
		row.prop_search(scene, "target_rig", bpy.data, "objects", text="")
		row.operator("arp.pick_object", text="", icon='EYEDROPPER').action = 'pick_target'
		row = layout.row(align=True)	 
		
		col = layout.column(align=True)
		
		col.operator("arp.auto_scale", text="Auto Scale")
		
		
		"""
		col = layout.column(align=True)
		if entries_are_set():#display only if entries are set
			col.enabled = True
		else:
			col.enabled = False
		
		col.prop(scene, "remove_offset", "Remove Initial Offset")		
		col.prop(scene, "arp_inherit_rot", "ARP: Inherit Shoulder, Neck Rotation")
		"""
		row = layout.row(align=True)
		if entries_are_set():#display only if entries are set
			row.enabled = True
		else:
			row.enabled = False
		 
		
		col = layout.column(align=True)		
		col.operator("arp.build_bones_list", text="Build Bones List")		  
		#col.operator("arp.retarget", text="Re-Target")
		col.operator("arp.retarget_clicked", text="Re-Target")
		
		if entries_are_set():#only if entries are set
			target_armature = bpy.data.objects[scene.target_rig].data.name
			
			row = layout.row(align=True)	
			split = row.split(factor=0.5)			 
			split.label(text="Source Bones:")		
			split.label(text="Target Rig Bones:")
			row = layout.row(align=True)	
			row.template_list("ARP_UL_items", "", scene, "bones_map", scene, "bones_map_index", rows=2)
			
				#display bone item properties
			if len(scene.bones_map) > 0:	
				# make a box UI
				box = layout.box()
				row = box.row(align=True)
				"""
				row = layout.row(align=True)
				box = row.box()
				row=box.row(align=True)
				"""
				row.prop(scene.bones_map[scene.bones_map_index], "source_bone", text="")			
				row.prop_search(scene.bones_map[scene.bones_map_index], "name", bpy.data.armatures[target_armature], "bones", text="")
				row.operator("arp.pick_object", text="", icon='EYEDROPPER').action = 'pick_bone'
				
				row = box.row(align=True)			
				row.prop(scene.bones_map[scene.bones_map_index], "set_as_root", text="Set as Root")
								
				#row=box.row(align=True)			
				#row.prop(scene, "remap_mode", expand=True)
				
				if scene.remap_mode == "manual":
					row=box.row(align=True)					
					button = row.operator("arp.guess_orientation", text="Guess Orientation")
					button.guess_all = False
					button = row.operator("arp.guess_orientation", text="Guess All")
					button.guess_all = True
					row=box.row()
					
					split = row.split(factor=0.3)	   
					split.prop(scene.bones_map[scene.bones_map_index], "axis_order", "")			 
					split.prop(scene.bones_map[scene.bones_map_index],"x_inv", "-X")
					split.prop(scene.bones_map[scene.bones_map_index],"y_inv", "-Y")
					split.prop(scene.bones_map[scene.bones_map_index],"z_inv", "-Z")					  
					
					col = box.column(align=True)
					col.label("Rotation Offset:")
					col.prop(scene.bones_map[scene.bones_map_index], "offset_rot_x", "X")
					col.prop(scene.bones_map[scene.bones_map_index], "offset_rot_y", "Y") 
					col.prop(scene.bones_map[scene.bones_map_index], "offset_rot_z", "Z")  
					 

				if scene.remap_mode == "auto":
					row=box.row(align=True) 
					split = row.split(factor=0.2)		
					
					if scene.bones_map[scene.bones_map_index].set_as_root:
						split.enabled = False
						scene.bones_map[scene.bones_map_index].ik = False
					else:
						split.enabled = True
						
					split.prop(scene.bones_map[scene.bones_map_index],"ik", text="IK")	
					split2 = split.split(factor=0.9, align=True)
					if scene.bones_map[scene.bones_map_index].ik:
						split2.enabled = True
					else:
						split2.enabled = False
					split2.prop_search(scene.bones_map[scene.bones_map_index], "ik_pole", bpy.data.armatures[target_armature], "bones", text="Pole")
					split2.operator("arp.pick_object", text="", icon='EYEDROPPER').action = 'pick_pole'
					row = box.row(align=True)
					row.enabled = False
					if scene.bones_map[scene.bones_map_index].ik:
						row.enabled = True
					row.prop(scene.bones_map[scene.bones_map_index], "ik_auto_pole")
					
					col = box.column(align=True)
					col.label(text="Interactive Tweaks:")
					col.prop(scene, "additive_rot", text="Additive Rotation")
					row = col.row(align=True)					
					btn = row.operator("arp.apply_offset", text="+X")
					btn.value = "rot_+x"
					btn = row.operator("arp.apply_offset", text="-X")
					btn.value = "rot_-x"
					btn = row.operator("arp.apply_offset", text="+Y")
					btn.value = "rot_+y"
					btn = row.operator("arp.apply_offset", text="-Y")
					btn.value = "rot_-y"
					btn = row.operator("arp.apply_offset", text="+Z")
					btn.value = "rot_+z"
					btn = row.operator("arp.apply_offset", text="-Z")
					btn.value = "rot_-z"
					
					col = box.column(align=True)
					col.prop(scene, "additive_loc", text="Additive Location")
					row = col.row(align=True)					
					btn = row.operator("arp.apply_offset", text="+X")
					btn.value = "loc_+x"
					btn = row.operator("arp.apply_offset", text="-X")
					btn.value = "loc_-x"
					btn = row.operator("arp.apply_offset", text="+Y")
					btn.value = "loc_+y"
					btn = row.operator("arp.apply_offset", text="-Y")
					btn.value = "loc_-y"
					btn = row.operator("arp.apply_offset", text="+Z")
					btn.value = "loc_+z"
					btn = row.operator("arp.apply_offset", text="-Z")
					btn.value = "loc_-z"
					
					col = box.column(align=True)
					
					col.prop(scene, "loc_scale", text="Location Scale Multiplier")
					row = col.row(align=True)					
					btn = row.operator("arp.apply_offset", text="Set")
					btn.value = "loc_scale"
					
				row = layout.row(align=True) 
				row=box.row()	
				layout.label(text="Mapping Preset:")				   
				layout.prop(scene, "file_path", text="")
				row = layout.row(align=True)
				row.operator("arp.export_config", text="Export")
				row.operator("arp.import_config", text="Import")
				row = layout.row(align=True)
				row.prop(scene, "search_and_replace", text="Replace Namespace:")
				row = layout.row(align=True)
				if scene.search_and_replace:
					row.enabled = True
				else:
					row.enabled = False
				row.prop(scene, "name_search", text="Search")
				row.prop(scene, "name_replace", text="Replace")
				
		else:
			layout.label(text="Empty bone list")
		
		layout.separator()
		layout.alignment = 'CENTER'
		layout.label(text="Redefine Source Rest Pose:")
		button_state = 0
		
		try:
			bpy.data.objects[scene.source_rig + "_copy"]
			button_state = 1
		except:
			pass
			
		try:
			current_mode = bpy.context.mode
			if current_mode == 'POSE' and bpy.context.object.name == scene.source_rig + "_copy":
				button_state = 1
		except:
			pass			
		
		
			
		if button_state == 0:
			layout.operator("arp.redefine_rest_pose", text="Redefine Rest Pose")
		if button_state == 1:
			layout.operator("arp.copy_bone_rest", text="Copy Selected Target Bones", icon='COPYDOWN')
			row = layout.row(align=True)
			row.operator("arp.cancel_redefine", text="Cancel")
			row.operator("arp.copy_raw_coordinates", text="Apply")
			
		
	
	
		
				
		
		   
		
 
###########	 REGISTER  ##################

classes = (ARP_UL_items, ARP_OT_freeze_armature, ARP_OT_redefine_rest_pose, ARP_OT_auto_scale, ARP_OT_apply_offset, ARP_OT_cancel_redefine, ARP_OT_copy_bone_rest, ARP_OT_copy_raw_coordinates, ARP_OT_pick_object, ARP_OT_guess_orientation, ARP_OT_export_config, ARP_OT_import_config, ARP_OT_retarget, ARP_OT_retarget_dialog, ARP_OT_retarget_clicked, ARP_OT_build_bones_list, ARP_OT_set_as_root, CustomProp, ARP_PT_auto_rig_remap_panel)

def register():	  

	from bpy.utils import register_class

	for cls in classes:
		register_class(cls)
		
	bpy.types.Scene.target_rig = bpy.props.StringProperty(name = "Target Rig", default="", description="Destination armature to re-target the action", update=update_target_rig)
	bpy.types.Scene.source_rig = bpy.props.StringProperty(name = "Source Rig", default="", description="Source rig armature to take action from", update=update_source_rig)
	bpy.types.Scene.bones_map = bpy.props.CollectionProperty(type=CustomProp)
	bpy.types.Scene.bones_map_index = bpy.props.IntProperty()	 
	bpy.types.Scene.global_scale = bpy.props.FloatProperty(name="Global Scale", default=1.0, description="Global scale offset for the root location")
	bpy.types.Scene.source_nodes_name_string = bpy.props.StringProperty(name = "Source Names String", default="")
	bpy.types.Scene.source_action = bpy.props.StringProperty(name = "Source Action", default="", description="Source action data to load data from")
	#bpy.types.Scene.remove_offset = bpy.props.BoolProperty(name="Remove Initial Offset", default = False, description="Remove the initial offset (mainly for .BVH file, only use if the source actor is in T-Pose on frame 1)")	  
	bpy.types.Scene.arp_inherit_rot = bpy.props.BoolProperty(name="ARP Inherit Rotation", default=False, description="Auto-Rig Pro type armature only: if enabled, the bones hierarchy will be modified so that the arms and the head will inherit their parent bones rotation.")
	bpy.types.Scene.file_path = bpy.props.StringProperty(name="File Path", subtype='FILE_PATH', default="")
	"""bpy.types.Scene.armature_orientation = bpy.props.EnumProperty(items=(
		('X', 'X Axis', 'The armature faces the X Axis'),
		('-X', '-X Axis', 'Ther armature faces the -X Axis'),
		('Y', 'Y Axis', 'The armature faces the Y Axis'),
		('-Y', '-Y Axis', 'The armature faces the -Y Axis'),
		('Z', 'Z Axis', 'The armature faces the Z Axis'),
		('-Z', '-Z Axis', 'The armature faces the -Z Axis')),
		name="Armature Orientation", description="The armature faces this axis. Set it if you want to use the Guess Orientation feature for Auto-Rig Pro armature type")"""
	bpy.types.Scene.remap_mode = bpy.props.EnumProperty(
		items=(
				('auto', 'Auto', 'Automatic remapping. The source and target armatures have to face the same direction in T-Pose/Rest Pose.'),
				('manual', 'Manual', 'Manual remapping')
				
			),
			name="Remap mode", description="Remap mode", default = 'auto'
		)
	#bpy.types.Scene.root_bone = bpy.props.StringProperty(name="Root bone", default="")
	bpy.types.Scene.additive_rot = bpy.props.FloatProperty(name="Additive Rotation", default=math.radians(10), unit="ROTATION")
	bpy.types.Scene.additive_loc = bpy.props.FloatProperty(name="Additive Location", default=0.1)
	bpy.types.Scene.loc_scale = bpy.props.FloatProperty(name="Root Scale", default=0.9)
	bpy.types.Scene.name_search = bpy.props.StringProperty(name="Name search", default="")
	bpy.types.Scene.name_replace = bpy.props.StringProperty(name="Replace", default="")
	bpy.types.Scene.search_and_replace = bpy.props.BoolProperty(name="search_and_replace", default=False)
	bpy.types.Scene.arp_freeze_armature_check = bpy.props.BoolProperty(name="Label error", default=False)
	
	
def unregister():	

	from bpy.utils import unregister_class
	
	for cls in reversed(classes):
		unregister_class(cls)	
		
	del bpy.types.Scene.target_rig
	del bpy.types.Scene.source_rig
	del bpy.types.Scene.bones_map
	del bpy.types.Scene.bones_map_index	   
	del bpy.types.Scene.global_scale
	del bpy.types.Scene.source_nodes_name_string
	del bpy.types.Scene.source_action
	#del bpy.types.Scene.remove_offset 
	del bpy.types.Scene.arp_inherit_rot
	del bpy.types.Scene.file_path
	del bpy.types.Scene.remap_mode
	#del bpy.types.Scene.root_bone
	del bpy.types.Scene.additive_rot
	del bpy.types.Scene.additive_loc
	del bpy.types.Scene.loc_scale
	#del bpy.types.Scene.armature_orientation
	del bpy.types.Scene.name_search
	del bpy.types.Scene.name_replace
	del bpy.types.Scene.search_and_replace
	del bpy.types.Scene.arp_freeze_armature_check

	