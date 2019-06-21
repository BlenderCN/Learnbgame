import bpy
import mathutils
from mathutils import *
import math
from math import acos, pi
from bpy.app.handlers import persistent
from . import auto_rig_datas
from operator import itemgetter

print ("\n Starting Auto-Rig Pro Functions... \n")

# Global vars
hands_ctrl = ["c_hand_ik", "c_hand_fk"]
sides = [".l", ".r"]
eye_aim_bones = ["c_eye_target.x", "c_eye"]
auto_eyelids_bones = ["c_eye", "c_eyelid_top", "c_eyelid_bot"]

fk_arm = ["c_arm_fk", "c_forearm_fk", "c_hand_fk", "arm_fk_pole"]
ik_arm = ["arm_ik", "forearm_ik", "c_hand_ik", "c_arms_pole", "c_arm_ik"]

fk_leg = ["c_thigh_fk", "c_leg_fk", "c_foot_fk", "c_toes_fk", "leg_fk_pole"]
ik_leg = ["thigh_ik", "leg_ik", "c_foot_ik", "c_leg_pole", "c_toes_ik", "c_foot_01", "c_foot_roll_cursor", "foot_snap_fk", "c_thigh_ik"]


#CLASSES ###########################################################################################################


	
class ARP_OT_set_picker_camera_func(bpy.types.Operator):	 
	
	"""Display the bone picker of the selected character in this active view"""
	
	bl_idname = "id.set_picker_camera_func"
	bl_label = "set_picker_camera_func"
	bl_options = {'UNDO'}	
	
	@classmethod
	def poll(cls, context):
		if context.object != None:
			if is_object_arp(context.object):
				return True

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:		   
			_set_picker_camera(self)		
					   
		finally:
			context.preferences.edit.use_global_undo = use_global_undo		   
		return {'FINISHED'}


class ARP_OT_toggle_multi(bpy.types.Operator):
	"""Toggle multi-limb visibility"""

	bl_idname = "id.toggle_multi"
	bl_label = "toggle_multi"
	bl_options = {'UNDO'}
	
	limb : bpy.props.StringProperty(name="Limb")
	id : bpy.props.StringProperty(name="Id")
	key : bpy.props.StringProperty(name="key")
	"""
	@classmethod
	def poll(cls, context):
		return (context.active_object != None and context.mode == 'POSE')
	"""
	
	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:
			_toggle_multi(self.limb, self.id, self.key)
		finally:
			context.preferences.edit.use_global_undo = use_global_undo
		return {'FINISHED'}
		

class ARP_OT_arp_snap_pole(bpy.types.Operator):
	"""Switch and snap the IK pole parent"""
	
	bl_idname = "pose.arp_snap_pole"
	bl_label = "Arp Snap FK arm to IK"
	bl_options = {'UNDO'}

	side : bpy.props.StringProperty(name="bone side")	
	bone_type : bpy.props.StringProperty(name="arm or leg")
	

	@classmethod
	def poll(cls, context):
		return (context.active_object != None and context.mode == 'POSE')

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:
			_arp_snap_pole(context.active_object, self.side, self.bone_type)
		finally:
			context.preferences.edit.use_global_undo = use_global_undo
		return {'FINISHED'}
		
		
class ARP_OT_arm_switch_snap(bpy.types.Operator):
	"""Switch and snap the IK-FK arm"""
	
	bl_idname = "pose.arp_arm_switch_snap"
	bl_label = "Arp Switch and Snap IK FK Arm"
	bl_options = {'UNDO'}

	side : bpy.props.StringProperty(name="bone side")	

	@classmethod
	def poll(cls, context):
		return (context.active_object != None and context.mode == 'POSE')

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:
			
			hand_ik = context.object.pose.bones[ik_arm[2] + self.side]
			if hand_ik['ik_fk_switch'] < 0.5:				
				fk_to_ik_arm(context.active_object, self.side)
			else:
				ik_to_fk_arm(context.active_object, self.side)
		finally:
			context.preferences.edit.use_global_undo = use_global_undo
		return {'FINISHED'}	
		

class ARP_OT_arm_fk_to_ik(bpy.types.Operator):
	"""Snaps an FK arm to an IK arm"""
	
	bl_idname = "pose.arp_arm_fk_to_ik_"
	bl_label = "Arp Snap FK arm to IK"
	bl_options = {'UNDO'}

	side : bpy.props.StringProperty(name="bone side")	
	

	@classmethod
	def poll(cls, context):
		return (context.active_object != None and context.mode == 'POSE')

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:
			fk_to_ik_arm(context.active_object, self.side)
		finally:
			context.preferences.edit.use_global_undo = use_global_undo
		return {'FINISHED'}


class ARP_OT_arm_ik_to_fk(bpy.types.Operator):
	"""Snaps an IK arm to an FK arm"""
	
	bl_idname = "pose.arp_arm_ik_to_fk_"
	bl_label = "Arp Snap IK arm to FK"
	bl_options = {'UNDO'}

	side : bpy.props.StringProperty(name="bone side")

	@classmethod
	def poll(cls, context):
		return (context.active_object != None and context.mode == 'POSE')

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:
			ik_to_fk_arm(context.active_object, self.side)
		finally:
			context.preferences.edit.use_global_undo = use_global_undo
		return {'FINISHED'}


		
class ARP_OT_leg_switch_snap(bpy.types.Operator):
	"""Switch and snap the IK-FK leg"""
	
	bl_idname = "pose.arp_leg_switch_snap"
	bl_label = "Arp Switch and Snap IK FK Leg"
	bl_options = {'UNDO'}

	side : bpy.props.StringProperty(name="bone side")	

	@classmethod
	def poll(cls, context):
		return (context.active_object != None and context.mode == 'POSE')

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:
			
			foot_ik = context.object.pose.bones[ik_leg[2] + self.side]
			if foot_ik['ik_fk_switch'] < 0.5:				
				fk_to_ik_leg(context.active_object, self.side)
			else:
				ik_to_fk_leg(context.active_object, self.side)
		finally:
			context.preferences.edit.use_global_undo = use_global_undo
		return {'FINISHED'}		
		
class ARP_OT_leg_fk_to_ik(bpy.types.Operator):
	"""Snaps an FK leg to an IK leg"""
	
	bl_idname = "pose.arp_leg_fk_to_ik_"
	bl_label = "Arp Snap FK leg to IK"
	bl_options = {'UNDO'}

	side : bpy.props.StringProperty(name="bone side")	

	@classmethod
	def poll(cls, context):
		return (context.active_object != None and context.mode == 'POSE')

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:
			fk_to_ik_leg(context.active_object, self.side)
		finally:
			context.preferences.edit.use_global_undo = use_global_undo
		return {'FINISHED'}


class ARP_OT_leg_ik_to_fk(bpy.types.Operator):
	"""Snaps an IK leg to an FK leg"""
	
	bl_idname = "pose.arp_leg_ik_to_fk_"
	bl_label = "Arp Snap IK leg to FK"
	bl_options = {'UNDO'}

	side : bpy.props.StringProperty(name="bone side")	

	@classmethod
	def poll(cls, context):
		return (context.active_object != None and context.mode == 'POSE')

	def execute(self, context):
		use_global_undo = context.preferences.edit.use_global_undo
		context.preferences.edit.use_global_undo = False
		try:
			ik_to_fk_leg(context.active_object, self.side)
		finally:
			context.preferences.edit.use_global_undo = use_global_undo
		return {'FINISHED'}



###FUNCTIONS ##############################################

def set_active_object(object_name):
	 bpy.context.view_layer.objects.active = bpy.data.objects[object_name]
	 bpy.data.objects[object_name].select_set(state=1)

def is_object_arp(object):
	if object.type == 'ARMATURE':
		if object.pose.bones.get('c_pos') != None:
			return True

def _set_picker_camera(self):
	
	# go to object mode
	bpy.ops.object.mode_set(mode='OBJECT')
	
	#save current scene camera
	current_cam = bpy.context.scene.camera	  
	
	rig = bpy.context.active_object
	bpy.ops.object.select_all(action='DESELECT')	
	cam_ui = None
	rig_ui = None
	ui_mesh = None
	char_name_text = None
	
	for child in rig.children:
		if child.type == 'CAMERA' and 'cam_ui' in child.name:
			cam_ui = child
		if child.type == 'EMPTY' and 'rig_ui' in child.name:
			rig_ui = child
			for _child in rig_ui.children:
				if _child.type == 'MESH' and 'mesh' in _child.name:
					ui_mesh = _child
	
	# ui cam not found, generate one
	active_obj_name = bpy.context.active_object.name
	
	if not cam_ui:
		bpy.ops.object.camera_add(view_align=True, enter_editmode=False, location=(0.001321, -59.7455, -56.2155), rotation=(math.radians(90), 0, 0))
		# set cam data
		bpy.context.active_object.name = "cam_ui"
		cam_ui = bpy.data.objects["cam_ui"]
		cam_ui.data.type = "ORTHO"
		cam_ui.data.display_size = 0.1
		cam_ui.data.show_limits = False
		cam_ui.data.show_passepartout = False
		cam_ui.parent = bpy.data.objects[active_obj_name]
		# set collections
		for col in bpy.data.objects[active_obj_name].users_collection:
			col.objects.link(cam_ui)
		
	set_active_object(active_obj_name)
	
	if cam_ui:
		cam_ui.select_set(state=1)
		print("Selected", cam_ui.name)
		bpy.context.view_layer.objects.active = cam_ui
		bpy.ops.view3d.object_as_camera()
		
		# set viewport display options
		#bpy.context.space_data.lock_camera_and_layers = False 
		bpy.context.space_data.overlay.show_relationship_lines = False
		bpy.context.space_data.overlay.show_text = False
		bpy.context.space_data.overlay.show_cursor = False
		current_area = bpy.context.area
		space_view3d = [i for i in current_area.spaces if i.type == "VIEW_3D"]		
		space_view3d[0].shading.type = 'SOLID'
		space_view3d[0].shading.show_object_outline = False
		space_view3d[0].shading.show_specular_highlight = False
		space_view3d[0].show_gizmo_navigate = False	
		space_view3d[0].use_local_camera = True	
		bpy.context.space_data.lock_camera = False#unlock camera to view
		
		
		rig_ui_scale = 1.0
		
		if rig_ui:
			rig_ui_scale = rig_ui.scale[0]
	
		units_scale = bpy.context.scene.unit_settings.scale_length
		fac_ortho = 1.8# * (1/units_scale)
		
		
			
		# Position the camera height to the backplate height		
		if ui_mesh:
			vert_pos = [v.co for v in ui_mesh.data.vertices]
			vert_pos = sorted(vert_pos, reverse = False, key=itemgetter(2))
			max1 = ui_mesh.matrix_world @ vert_pos[0]
			max2 = ui_mesh.matrix_world @ vert_pos[len(vert_pos)-1] 
			picker_size = (max1-max2).magnitude
			picker_center = (max1 + max2)/2		
			
			# save the camera loc, rot, scale
			cam_ui_loc = cam_ui.location.copy()
			cam_ui_rot =  cam_ui.rotation_euler.copy()
			cam_ui_scale =	cam_ui.scale.copy()
			
			# set the camera matrix to the picker center
			cam_ui.matrix_world = mathutils.Matrix.Translation(picker_center)
			
			# Restore the necessary camera transforms, since only the cam height has to change
			cam_ui.location[0], cam_ui.location[1] = cam_ui_loc[0], cam_ui_loc[1]
			cam_ui.rotation_euler = cam_ui_rot
			cam_ui.scale = cam_ui_scale
			
		
			bpy.context.scene.update()
			dist = (cam_ui.matrix_world.to_translation() - picker_center).length
			
			cam_ui.data.clip_start = dist*0.9
			cam_ui.data.clip_end = dist*1.1
			cam_ui.data.ortho_scale = fac_ortho * picker_size
			
			
		
		
		#restore the scene camera
		bpy.context.scene.camera = current_cam
		
	else:
		self.report({'ERROR'}, 'No picker camera found for this rig')
	
	#back to pose mode
	bpy.ops.object.select_all(action='DESELECT')
	rig.select_set(state=1)
	bpy.context.view_layer.objects.active = rig
	bpy.ops.object.mode_set(mode='POSE')
	
	# enable the picker addon
	try:		
		bpy.context.scene.Proxy_Picker.active = True
	except:
		pass	


def get_pose_matrix_in_other_space(mat, pose_bone):
	rest = pose_bone.bone.matrix_local.copy()
	rest_inv = rest.inverted()
	
	if pose_bone.parent and pose_bone.bone.use_inherit_rotation:
		par_mat = pose_bone.parent.matrix.copy()
		par_inv = par_mat.inverted()
		par_rest = pose_bone.parent.bone.matrix_local.copy()
		
	else:		
		par_mat = Matrix()
		par_inv = Matrix()
		par_rest = Matrix()		
	
	smat = rest_inv @ (par_rest @ (par_inv @ mat))
	

	return smat




def set_pos(pose_bone, mat):	
	if pose_bone.bone.use_local_location == True:
		pose_bone.location = mat.to_translation()
	else:
		loc = mat.to_translation()

		rest = pose_bone.bone.matrix_local.copy()
		if pose_bone.bone.parent:
			par_rest = pose_bone.bone.parent.matrix_local.copy()
		else:
			par_rest = Matrix()

		q = (par_rest.inverted() @ rest).to_quaternion()
		pose_bone.location = q @ loc


def set_pose_rotation(pose_bone, mat):
	q = mat.to_quaternion()

	if pose_bone.rotation_mode == 'QUATERNION':
		pose_bone.rotation_quaternion = q
	elif pose_bone.rotation_mode == 'AXIS_ANGLE':
		pose_bone.rotation_axis_angle[0] = q.angle
		pose_bone.rotation_axis_angle[1] = q.axis[0]
		pose_bone.rotation_axis_angle[2] = q.axis[1]
		pose_bone.rotation_axis_angle[3] = q.axis[2]
	else:
		pose_bone.rotation_euler = q.to_euler(pose_bone.rotation_mode)



def snap_pos(pose_bone, target_bone):
	# Snap a bone to another bone. Supports child of constraints and parent.
	"""
	mat = get_pose_matrix_in_other_space(target_bone.matrix, pose_bone)
	set_pos(pose_bone, mat)
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.mode_set(mode='POSE')
	"""	
	
	# if the pose_bone has direct parent
	if pose_bone.parent:		
		# apply double time because of dependecy lag
		pose_bone.matrix = target_bone.matrix
		#update hack
		bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, False, False), constraint_orientation='NORMAL', mirror=False)
		# second apply
		pose_bone.matrix = target_bone.matrix
	else:		
		# is there a child of constraint attached?
		child_of_cns = None
		if len(pose_bone.constraints) > 0:
			all_child_of_cns = [i for i in pose_bone.constraints if i.type == "CHILD_OF" and i.influence == 1.0 and i.mute == False and i.target]
			if len(all_child_of_cns) > 0:
				child_of_cns = all_child_of_cns[0]# in case of multiple child of constraints enabled, use only the first for now
		
		if child_of_cns != None:
			if child_of_cns.subtarget != "" and get_pose_bone(child_of_cns.subtarget):
				# apply double time because of dependecy lag
				pose_bone.matrix = get_pose_bone(child_of_cns.subtarget).matrix_channel.inverted() @ target_bone.matrix
				bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, False, False), constraint_orientation='NORMAL', mirror=False)
				pose_bone.matrix = get_pose_bone(child_of_cns.subtarget).matrix_channel.inverted() @ target_bone.matrix
			else:
				pose_bone.matrix = target_bone.matrix
				
		else:		
			pose_bone.matrix = target_bone.matrix
			
			

def snap_rot(pose_bone, target_bone):
	mat = get_pose_matrix_in_other_space(target_bone.matrix, pose_bone)
	set_pose_rotation(pose_bone, mat)
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.mode_set(mode='POSE')


def set_inverse_child(b):
	pbone = bpy.context.active_object.pose.bones[b]
	context_copy = bpy.context.copy()
	context_copy["constraint"] = pbone.constraints["Child Of"]
	bpy.context.active_object.data.bones.active = pbone.bone
	bpy.ops.constraint.childof_set_inverse(context_copy, constraint="Child Of", owner='BONE')	  


def fk_to_ik_arm(obj, side):	
	
	arm_fk  = obj.pose.bones[fk_arm[0] + side]
	forearm_fk  = obj.pose.bones[fk_arm[1] + side]
	hand_fk  = obj.pose.bones[fk_arm[2] + side]
	
	arm_ik = obj.pose.bones[ik_arm[0] + side]
	forearm_ik = obj.pose.bones[ik_arm[1] + side]
	hand_ik = obj.pose.bones[ik_arm[2] + side]
	pole = obj.pose.bones[ik_arm[3] + side]

	# Stretch
	if hand_ik['auto_stretch'] == 0.0:
		hand_fk['stretch_length'] = hand_ik['stretch_length']
	else:	
		diff = (arm_ik.length+forearm_ik.length) / (arm_fk.length+forearm_fk.length)
		hand_fk['stretch_length'] *= diff

	#Snap rot
	snap_rot(arm_fk, arm_ik)
	snap_rot(forearm_fk, forearm_ik)	
	snap_rot(hand_fk, hand_ik)
	
	#Snap scale
	hand_fk.scale =hand_ik.scale
	
	#rot debug
	forearm_fk.rotation_euler[0]=0
	forearm_fk.rotation_euler[1]=0
	
	#switch
	hand_ik['ik_fk_switch'] = 1.0

	#udpate view
	bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, False, False), constraint_orientation='NORMAL', mirror=False)

	
	#insert key if autokey enable
	if bpy.context.scene.tool_settings.use_keyframe_insert_auto == True:
		#fk chain
		hand_ik.keyframe_insert(data_path='["ik_fk_switch"]')
		hand_fk.keyframe_insert(data_path='["stretch_length"]')
		hand_fk.keyframe_insert(data_path="scale")
		hand_fk.keyframe_insert(data_path="rotation_euler")
		arm_fk.keyframe_insert(data_path="rotation_euler")
		forearm_fk.keyframe_insert(data_path="rotation_euler")
				
		#ik chain
		hand_ik.keyframe_insert(data_path='["stretch_length"]')
		hand_ik.keyframe_insert(data_path='["auto_stretch"]')
		hand_ik.keyframe_insert(data_path="location")
		hand_ik.keyframe_insert(data_path="rotation_euler")
		hand_ik.keyframe_insert(data_path="scale")
		pole.keyframe_insert(data_path="location")
		
	# change FK to IK hand selection, if selected
	if hand_ik.bone.select:
		hand_fk.bone.select = True
		hand_ik.bone.select = False
		



def ik_to_fk_arm(obj, side):
	
	arm_fk  = obj.pose.bones[fk_arm[0] + side]
	forearm_fk  = obj.pose.bones[fk_arm[1] + side]
	hand_fk  = obj.pose.bones[fk_arm[2] + side]
	pole_fk = obj.pose.bones[fk_arm[3] + side]
	
	arm_ik = obj.pose.bones[ik_arm[0] + side]
	forearm_ik = obj.pose.bones[ik_arm[1] + side]
	hand_ik = obj.pose.bones[ik_arm[2] + side]
	pole  = obj.pose.bones[ik_arm[3] + side]
 
	# reset custom pole angle if any
	if obj.pose.bones.get("c_arm_ik" + side) != None:
		obj.pose.bones["c_arm_ik" + side].rotation_euler[1] = 0.0

	# Stretch
	hand_ik['stretch_length'] = hand_fk['stretch_length']	
	
	# Child Of constraint or parent cases
	constraint = None
	bone_parent_string = ""
	parent_type = ""	
	valid_constraint = True
	
	if len(hand_ik.constraints) > 0:		
		for c in hand_ik.constraints:
			if not c.mute and c.influence > 0.5 and c.type == 'CHILD_OF':
				if c.target:
					#if bone
					if c.target.type == 'ARMATURE':
						bone_parent_string = c.subtarget
						parent_type = "bone"
						constraint = c
					#if object
					else:
						bone_parent_string = c.target.name
						parent_type = "object"
						constraint = c				
						
	
	if constraint != None:
		if parent_type == "bone":
			if bone_parent_string == "":
				valid_constraint = False
	
	# Snap
	if constraint and valid_constraint:	
		if parent_type == "bone":
			bone_parent = bpy.context.object.pose.bones[bone_parent_string]
			hand_ik.matrix = bone_parent.matrix_channel.inverted()@hand_fk.matrix
		if parent_type == "object":
			bone_parent = bpy.data.objects[bone_parent_string]
			obj = bpy.data.objects[bone_parent_string]
			hand_ik.matrix = constraint.inverse_matrix.inverted() @obj.matrix_world.inverted() @ hand_fk.matrix
	 
	else:
		hand_ik.matrix = hand_fk.matrix
		
		
	# Pole target position
	snap_pos(pole, pole_fk)		

	
	
	
	#switch
	hand_ik['ik_fk_switch'] = 0.0
	
	#update view
	bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, False, False), constraint_orientation='NORMAL', mirror=False)
	
	 #insert key if autokey enable
	if bpy.context.scene.tool_settings.use_keyframe_insert_auto == True:
		#ik chain
		hand_ik.keyframe_insert(data_path='["ik_fk_switch"]')
		hand_ik.keyframe_insert(data_path='["stretch_length"]')
		hand_ik.keyframe_insert(data_path='["auto_stretch"]')
		hand_ik.keyframe_insert(data_path="location")
		hand_ik.keyframe_insert(data_path="rotation_euler")
		hand_ik.keyframe_insert(data_path="scale")
		pole.keyframe_insert(data_path="location")
		
		#ik controller if any
		if obj.pose.bones.get("c_arm_ik" + side) != None:
			obj.pose.bones["c_arm_ik" + side].keyframe_insert(data_path="rotation_euler", index=1)
		
		#fk chain
		hand_fk.keyframe_insert(data_path='["stretch_length"]')
		hand_fk.keyframe_insert(data_path="location")		  
		hand_fk.keyframe_insert(data_path="rotation_euler")
		hand_fk.keyframe_insert(data_path="scale")
		arm_fk.keyframe_insert(data_path="rotation_euler")
		forearm_fk.keyframe_insert(data_path="rotation_euler")
		
		
	# change FK to IK hand selection, if selected
	if hand_fk.bone.select:
		hand_fk.bone.select = False
		hand_ik.bone.select = True


def fk_to_ik_leg(obj, side):
	
	
	thigh  = obj.pose.bones[fk_leg[0] + side]
	leg	 = obj.pose.bones[fk_leg[1] + side]
	foot_fk  = obj.pose.bones[fk_leg[2] + side]
	toes_fk = obj.pose.bones[fk_leg[3] + side]
	
	thighi = obj.pose.bones[ik_leg[0] + side]
	legi = obj.pose.bones[ik_leg[1] + side]	
	foot_ik = obj.pose.bones[ik_leg[2] + side]
	pole = obj.pose.bones[ik_leg[3] + side]
	toes_ik = obj.pose.bones[ik_leg[4] + side]
	foot_01 = obj.pose.bones[ik_leg[5] + side]
	foot_roll = obj.pose.bones[ik_leg[6] + side]
	footi_rot = obj.pose.bones[ik_leg[7] + side]	
	

	# Stretch
	if foot_ik['auto_stretch'] == 0.0:
		foot_fk['stretch_length'] = foot_ik['stretch_length']
	else:
		diff = (thighi.length+legi.length) / (thigh.length+leg.length)
	   
		foot_fk['stretch_length'] *= diff

	# Thigh snap
	snap_rot(thigh, thighi)

	# Leg snap
	snap_rot(leg, legi)	  

	# foot_fk snap
	snap_rot(foot_fk, footi_rot)
		#scale	  
	foot_fk.scale =foot_ik.scale	
	
	#Toes snap
	snap_rot(toes_fk, toes_ik)
		#scale
	toes_fk.scale =toes_ik.scale	
	
	#rotation debug
	leg.rotation_euler[0]=0
	leg.rotation_euler[1]=0
	
	 #switch
	foot_ik['ik_fk_switch'] = 1.0
	
	#insert key if autokey enable
	if bpy.context.scene.tool_settings.use_keyframe_insert_auto == True:
		#fk chain
		foot_ik.keyframe_insert(data_path='["ik_fk_switch"]')
		foot_fk.keyframe_insert(data_path='["stretch_length"]')
		foot_fk.keyframe_insert(data_path="scale")
		foot_fk.keyframe_insert(data_path="rotation_euler")
		thigh.keyframe_insert(data_path="rotation_euler")
		leg.keyframe_insert(data_path="rotation_euler")
		toes_fk.keyframe_insert(data_path="rotation_euler")
		toes_fk.keyframe_insert(data_path="scale")
		
		#ik chain		 
		foot_ik.keyframe_insert(data_path='["stretch_length"]')
		foot_ik.keyframe_insert(data_path='["auto_stretch"]')
		foot_ik.keyframe_insert(data_path="location")
		foot_ik.keyframe_insert(data_path="rotation_euler")
		foot_ik.keyframe_insert(data_path="scale")
		foot_01.keyframe_insert(data_path="rotation_euler")
		foot_roll.keyframe_insert(data_path="location")		  
		toes_ik.keyframe_insert(data_path="rotation_euler")
		toes_ik.keyframe_insert(data_path="scale")		
		pole.keyframe_insert(data_path="location")
		
		#ik angle controller if any
		if obj.pose.bones.get("c_thigh_ik" + side) != None:
			obj.pose.bones["c_thigh_ik" + side].keyframe_insert(data_path="rotation_euler", index=1)
			
	# change IK to FK foot selection, if selected
	if foot_ik.bone.select:
		foot_fk.bone.select = True
		foot_ik.bone.select = False
  

def ik_to_fk_leg(obj, side):

	
	thigh  = obj.pose.bones[fk_leg[0] + side]
	leg	 = obj.pose.bones[fk_leg[1] + side]
	foot_fk  = obj.pose.bones[fk_leg[2] + side]
	toes_fk = obj.pose.bones[fk_leg[3] + side]
	pole_fk = obj.pose.bones[fk_leg[4] + side]
	
	thighi = obj.pose.bones[ik_leg[0] + side]
	legi = obj.pose.bones[ik_leg[1] + side]
	foot_ik = obj.pose.bones[ik_leg[2] + side]
	pole  = obj.pose.bones[ik_leg[3] + side]
	toes_ik = obj.pose.bones[ik_leg[4] + side]
	foot_01 = obj.pose.bones[ik_leg[5] + side]
	foot_roll = obj.pose.bones[ik_leg[6] + side]
	

	# Stretch
	foot_ik['stretch_length'] = foot_fk['stretch_length']
   
	# reset IK foot_01 and foot_roll
	foot_01.rotation_euler = [0,0,0]
	
	foot_roll.location[0]=0
	foot_roll.location[2]=0
	
	# reset custom pole angle if any
	if obj.pose.bones.get("c_thigh_ik" + side) != None:
		obj.pose.bones["c_thigh_ik" + side].rotation_euler[1] = 0.0
	
	
	#toes snap	  	
	toes_ik.rotation_euler= toes_fk.rotation_euler
	toes_ik.scale = toes_fk.scale
	
	# Child Of constraint or parent cases
	constraint = None
	bone_parent_string = ""
	parent_type = ""	
	valid_constraint = True
	
	if len(foot_ik.constraints) > 0:		
		for c in foot_ik.constraints:
			if not c.mute and c.influence > 0.5 and c.type == 'CHILD_OF':
				if c.target:
					#if bone
					if c.target.type == 'ARMATURE':
						bone_parent_string = c.subtarget
						parent_type = "bone"
						constraint = c
					#if object
					else:
						bone_parent_string = c.target.name
						parent_type = "object"
						constraint = c				
						
	
	if constraint != None:
		if parent_type == "bone":
			if bone_parent_string == "":
				valid_constraint = False
	
	# Snap
	if constraint and valid_constraint:	
		if parent_type == "bone":		
			bone_parent = bpy.context.object.pose.bones[bone_parent_string]
			foot_ik.matrix = bone_parent.matrix_channel.inverted()@foot_fk.matrix
		if parent_type == "object":
			bone_parent = bpy.data.objects[bone_parent_string]
			obj = bpy.data.objects[bone_parent_string]
			foot_ik.matrix = constraint.inverse_matrix.inverted() @ obj.matrix_world.inverted() @ foot_fk.matrix
	 
	else:
		foot_ik.matrix = foot_fk.matrix
		
	
	
	# Pole target position
	snap_pos(pole, pole_fk)

	
	 #switch
	foot_ik['ik_fk_switch'] = 0.0	
	
	
	#update hack
	bpy.ops.transform.translate(value=(0, 0, 0))
	
	#insert key if autokey enable
	if bpy.context.scene.tool_settings.use_keyframe_insert_auto == True:
		#ik chain
		foot_ik.keyframe_insert(data_path='["ik_fk_switch"]')
		foot_ik.keyframe_insert(data_path='["stretch_length"]')
		foot_01.keyframe_insert(data_path="rotation_euler")
		foot_roll.keyframe_insert(data_path="location")
		foot_ik.keyframe_insert(data_path='["auto_stretch"]')
		foot_ik.keyframe_insert(data_path="location")
		foot_ik.keyframe_insert(data_path="rotation_euler")
		foot_ik.keyframe_insert(data_path="scale")
		toes_ik.keyframe_insert(data_path="rotation_euler")
		toes_ik.keyframe_insert(data_path="scale")		
		pole.keyframe_insert(data_path="location")
		
		#ik controller if any
		if obj.pose.bones.get("c_thigh_ik" + side) != None:
			obj.pose.bones["c_thigh_ik" + side].keyframe_insert(data_path="rotation_euler", index=1)
		
		#fk chain
		foot_fk.keyframe_insert(data_path='["stretch_length"]')
		foot_fk.keyframe_insert(data_path="rotation_euler")
		foot_fk.keyframe_insert(data_path="scale")
		thigh.keyframe_insert(data_path="rotation_euler")
		leg.keyframe_insert(data_path="rotation_euler")
		toes_fk.keyframe_insert(data_path="rotation_euler")
		toes_fk.keyframe_insert(data_path="scale")

	# change IK to FK foot selection, if selected
	if foot_fk.bone.select:
		foot_fk.bone.select = False
		foot_ik.bone.select = True
		
def _arp_snap_pole(ob, side, bone_type):
	if get_pose_bone('c_' + bone_type + '_pole' + side) != None:
		pole = get_pose_bone('c_' + bone_type + '_pole' + side)
		
		
		if "pole_parent" in pole.keys():
			# save the pole matrix
			pole_mat = pole.matrix.copy()
		
			# switch the property
			if pole["pole_parent"] == 0:
				pole["pole_parent"] = 1
			else:
				pole["pole_parent"] = 0
			
			#update view
			bpy.ops.transform.translate(value=(0, 0, 0))
	
			# are constraints there?
			cons = [None, None]
			for cns in pole.constraints:
				if cns.name == "Child Of_local":
					cons[0] = cns
				if cns.name == "Child Of_global":
					cons[1] = cns
			
			
			# if yes, set parent inverse
			if cons[0] != None and cons[1] != None:
				if pole["pole_parent"] == 0:
					pole.matrix = get_pose_bone(cons[1].subtarget).matrix_channel.inverted() @ pole_mat
					#pole.matrix = get_pose_bone(cons[1].subtarget).matrix.inverted()
					
					
				if pole["pole_parent"] == 1:
					pole.matrix = get_pose_bone(cons[0].subtarget).matrix_channel.inverted() @ pole_mat
					#pole.matrix = get_pose_bone(cons[0].subtarget).matrix.inverted()
				
		else:
			print("No pole_parent poprerty found")
			
	else:
		print("No c_leg_pole found")
		
		
def get_data_bone(name):
	try:
		return bpy.context.object.data.bones[name]
	except:
		return None
		
def get_pose_bone(name):  
	if bpy.context.object.pose.bones.get(name):
		return bpy.context.object.pose.bones[name]
	else:
		return None
		
def _toggle_multi(limb, id, key):
	bone_list = []

	if limb == 'arm':
		bone_list = auto_rig_datas.arm_displayed + auto_rig_datas.fingers_displayed
	if limb == 'leg':
		bone_list = auto_rig_datas.leg_displayed
		
	if get_pose_bone('c_pos')[key] == 1:
		get_pose_bone('c_pos')[key] = 0
	else:
		get_pose_bone('c_pos')[key] = 1
		
	for bone in bone_list:
		
		current_bone = get_data_bone(bone+'_dupli_'+id)
		if current_bone != None:
			arp_layer = current_bone['arp_layer']		
			
			if get_pose_bone('c_pos')[key] == 0:	  
				current_bone.layers[22] = True
				current_bone.layers[arp_layer] = False
			else:#need to set an active first
				current_bone.layers[arp_layer] = True
				current_bone.layers[22] = False
				
"""				
def update_head_lock(self, context):
	
	
	context.active_pose_bone["head_free"] = context.active_object.head_lock_obj
	
	scale_fix_bone = None	
	if context.active_object.data.bones.get("c_head_scale_fix.x") != None:
		scale_fix_bone = context.active_object.data.bones["c_head_scale_fix.x"]
	if context.active_object.data.bones.get("head_scale_fix.x") != None:
		scale_fix_bone = context.active_object.data.bones["head_scale_fix.x"]
		
	scale_fix_bone.use_inherit_rotation = 1-context.active_pose_bone["head_free"]
	scale_fix_bone.use_inherit_scale = 1-context.active_pose_bone["head_free"]
"""
	
	
	


		



# Rig UI Panels ##################################################################################################################

class ARP_PT_rig_ui(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "View"	
	bl_label = "Rig Main Properties"
	bl_idname = "_arp_rig_ui"

	@classmethod
	def poll(self, context):
		if context.mode != 'POSE':
			return False
		else:
			if context.active_object.data.get("rig_id") != None:
				return True
		

	def draw(self, context):
		layout = self.layout
		pose_bones = context.active_object.pose.bones
		try:			
			selected_bones = context.active_pose_bone.name
			
		except (AttributeError, TypeError):
			return
			
		bone_name = context.active_pose_bone.name
			
		# Get bone side
		bone_side = bone_name[-2:]
		
		if "_dupli_" in bone_name:
			bone_side = bone_name[-12:]		

		def is_selected(names):			
			if type(names) == list:				
				for name in names:	
					if not "." in name[-2:]:
					
						if name + bone_side == selected_bones:					
							return True						
					else:
						if name[-2:] == ".x":							
							if name[:-2] + bone_side == selected_bones:
								return True
			elif names == selected_bones:
				return True
			return False  


		if not 'humanoid' in bpy.context.active_object.name:
	  
		   #LEG						
			if (is_selected(fk_leg) or is_selected(ik_leg)):				
				
			   # Stretch length property
				if is_selected(fk_leg):
					layout.prop(pose_bones["c_foot_fk" + bone_side], '["stretch_length"]', text="Stretch Length (FK)", slider=True)			
				if is_selected(ik_leg):
					layout.prop(pose_bones["c_foot_ik" + bone_side], '["stretch_length"]', text="Stretch Length (IK)", slider=True)
					#auto_stretch ik property
					layout.prop(pose_bones["c_foot_ik" + bone_side], '["auto_stretch"]', text="Auto Stretch", slider=True) 					
					
					
				# Fix_roll prop		 
				layout.prop(pose_bones["c_foot_ik" + bone_side], '["fix_roll"]', text="Fix Roll", slider=True) 
				  
				layout.separator()				  
					
				# IK-FK Switch
				col = layout.column(align=True)
				row = col.row(align=True)
				p = row.operator("pose.arp_leg_switch_snap", text="Snap IK-FK")	
				p.side = bone_side
				row.prop(bpy.context.scene, "show_ik_fk_advanced", text="", icon="SETTINGS")		
				col.prop(pose_bones["c_foot_ik" + bone_side], '["ik_fk_switch"]', text="IK-FK Switch", slider=True)
				
				if bpy.context.scene.show_ik_fk_advanced:
					p = col.operator("pose.arp_leg_fk_to_ik_", text="Snap FK > IK")	
					p.side = bone_side
					p = col.operator("pose.arp_leg_ik_to_fk_", text="Snap IK > FK")
					p.side = bone_side
				
				if is_selected(ik_leg):	
					if "pole_parent" in pose_bones["c_leg_pole" + bone_side].keys():		
						# IK Pole parent
						col = layout.column(align=True)
						op = col.operator("pose.arp_snap_pole", text = "Snap Pole Parent")
						op.side = bone_side
						op.bone_type = "leg"
						col.prop(pose_bones["c_leg_pole" + bone_side], '["pole_parent"]', text="Pole Parent", slider=True)
				
			
			
			#ARM				
			if is_selected(fk_arm) or is_selected(ik_arm):
				
			   # Stretch length property
				if is_selected(fk_arm):
					layout.prop(pose_bones["c_hand_fk" + bone_side], '["stretch_length"]', text="Stretch Length (FK)", slider=True)			
				if is_selected(ik_arm):
					layout.prop(pose_bones["c_hand_ik" + bone_side], '["stretch_length"]', text="Stretch Length (IK)", slider=True)
				
				# Auto_stretch ik property
					layout.prop(pose_bones["c_hand_ik" + bone_side], '["auto_stretch"]', text="Auto Stretch", slider=True)	 
			
				layout.separator()				   
					
				# IK-FK Switch
				col = layout.column(align=True)
				row = col.row(align=True)
				p = row.operator("pose.arp_arm_switch_snap", text="Snap IK-FK")	
				p.side = bone_side
				row.prop(bpy.context.scene, "show_ik_fk_advanced", text="", icon="SETTINGS")			
				col.prop(pose_bones["c_hand_ik" + bone_side], '["ik_fk_switch"]', text="IK-FK Switch", slider=True)	
				
				if bpy.context.scene.show_ik_fk_advanced:
					p=col.operator("pose.arp_arm_fk_to_ik_", text="Snap FK > IK")
					p.side = bone_side				
					p=col.operator("pose.arp_arm_ik_to_fk_", text="Snap IK > FK")	
					p.side = bone_side
				
				if is_selected(ik_arm):
					# IK Pole parent
					if "pole_parent" in pose_bones["c_arms_pole" + bone_side].keys():						
						col = layout.column(align=True)
						op = col.operator("pose.arp_snap_pole", text = "Snap Pole Parent")
						op.side = bone_side
						op.bone_type = "arms"
						col.prop(pose_bones["c_arms_pole" + bone_side], '["pole_parent"]', text="Pole Parent", slider=True)

							
			# EYE AIM		 			
			if is_selected(eye_aim_bones):				
				layout.prop(pose_bones["c_eye_target" + bone_side[:-2] + '.x'], '["eye_target"]', text="Eye Target", slider=True)
				
			
			#AUTO EYELID
			for eyel in auto_eyelids_bones:				
				if is_selected(eyel + bone_side):					
					eyeb = pose_bones["c_eye" + bone_side]
					#retro compatibility, check if property exists
					if len(eyeb.keys()) > 0:
						if "auto_eyelid" in eyeb.keys():
							layout.separator()							
							layout.prop(pose_bones["c_eye" + bone_side], '["auto_eyelid"]', text="Auto-Eyelid", slider=True)
				
			
			# FINGERS BEND
			
			thumb_00 = "c_thumb1_base" + bone_side			
			index_00 = "c_index1_base" + bone_side			
			middle_00 = "c_middle1_base" + bone_side			
			ring_00 = "c_ring1_base"+ bone_side			
			pinky_00 = "c_pinky1_base"+ bone_side			
			
			fingers = [thumb_00, index_00, middle_00, ring_00, pinky_00]
					
			if is_selected(fingers):
				if (bone_side[-2:] == ".l"):
					finger_side = "Left "
				if (bone_side[-2:] == ".r"):
					finger_side = "Right "				  
				text_upper = (bone_name[:3]).upper()
				layout.label(text=finger_side + text_upper[2:] + bone_name[3:-8] + ":")
				layout.prop(pose_bones[bone_name], '["bend_all"]', text="Bend All Phalanges", slider=True)
			
			
			#FINGERS GRASP					
			if is_selected(hands_ctrl):					
				if 'fingers_grasp' in pose_bones["c_hand_fk" + bone_side].keys():#if property exists, retro-compatibility check
					layout.label(text="Fingers:")
					layout.prop(pose_bones["c_hand_fk" + bone_side],  '["fingers_grasp"]', text = "Fingers Grasp", slider = False)
			
			
			
			
			
			# PINNING 
			pin_arms = ["c_stretch_arm_pin", "c_stretch_arm_pin", "c_stretch_arm", "c_stretch_arm"]		 			
			if is_selected(pin_arms):
				if (bone_name[-2:] == ".l"):
					layout.label(text="Left Elbow Pinning")
					layout.prop(pose_bones["c_stretch_arm"+ bone_side], '["elbow_pin"]', text="Elbow pinning", slider=True)
				if (bone_name[-2:] == ".r"):
					layout.label(text="Right Elbow Pinning")
					layout.prop(pose_bones["c_stretch_arm"+bone_side], '["elbow_pin"]', text="Elbow pinning", slider=True)
						
			pin_legs = ["c_stretch_leg_pin", "c_stretch_leg_pin", "c_stretch_leg", "c_stretch_leg"]	 
			
		
			if is_selected(pin_legs):
				if (bone_name[-2:] == ".l"):
					layout.label(text="Left Knee Pinning")
					layout.prop(pose_bones["c_stretch_leg"+bone_side], '["leg_pin"]', text="Knee pinning", slider=True)
				if (bone_name[-2:] == ".r"):
					layout.label(text="Right Knee Pinning")
					layout.prop(pose_bones["c_stretch_leg"+bone_side], '["leg_pin"]', text="Knee pinning", slider=True)
				
			
			#HEAD LOCK
			if is_selected('c_head' + bone_side):
				if len(pose_bones['c_head' + bone_side].keys()) > 0:
					if 'head_free' in pose_bones['c_head' + bone_side].keys():#retro compatibility
						layout.prop(context.active_pose_bone, '["head_free"]', text = 'Head Lock', slider = True)
						
							
			
			#LIPS RETAIN
			if is_selected('c_jawbone' + bone_side):
				if len(pose_bones['c_jawbone' + bone_side].keys()) > 0:
					if 'lips_retain' in pose_bones['c_jawbone' + bone_side].keys():#retro compatibility
						layout.prop(pose_bones["c_jawbone" + bone_side], '["lips_retain"]', text = 'Lips Retain', slider = True)
						layout.prop(pose_bones["c_jawbone" + bone_side], '["lips_stretch"]', text = 'Lips Stretch', slider = True)
			
						
			
			
			#Multi Limb display
			if is_selected('c_pos'):
				layout.label(text='Multi-Limb Display:')
				#look for multi limbs
				
				if len(get_pose_bone('c_pos').keys()) > 0:
					for key in get_pose_bone('c_pos').keys():
						
						if 'leg' in key or 'arm' in key:
							row = layout.column(align=True)
							b = row.operator('id.toggle_multi', text=key)
							if 'leg' in key:
								b.limb = 'leg'
							if 'arm' in key:
								b.limb = 'arm'
							b.id = key[-5:]
							b.key = key
							row.prop(pose_bones['c_pos'], '["'+key+'"]', text=key)			  
							
				else:
					layout.label(text='No Multiple Limbs')
					
			#Set Picker Camera
			layout.separator()
			layout.label(text="Picker Camera")
			col = layout.column(align=True)
			col.operator(ARP_OT_set_picker_camera_func.bl_idname, text="Set Picker Cam")#, icon = 'CAMERA_DATA')
			row = col.row(align=True)
			"""
			op = row.operator("pp.start_picker", text="Start Picker", icon="PLAY")
			op.state = True
			op = row.operator("pp.start_picker", text="", icon="PAUSE")
			op.state = False
			"""
			
				
					
###########	 REGISTER  ##################
classes = (ARP_OT_set_picker_camera_func, ARP_OT_toggle_multi, ARP_OT_arp_snap_pole, ARP_OT_arm_switch_snap, ARP_OT_arm_fk_to_ik, ARP_OT_arm_ik_to_fk, ARP_OT_leg_switch_snap, ARP_OT_leg_fk_to_ik, ARP_OT_leg_ik_to_fk, ARP_PT_rig_ui)

def register():
	from bpy.utils import register_class

	for cls in classes:
		register_class(cls)	
		
	bpy.types.Scene.show_ik_fk_advanced = bpy.props.BoolProperty(name="Show IK-FK operators", description="Show IK-FK manual operators", default=False)
	
	
def unregister():	
	from bpy.utils import unregister_class

	for cls in classes:
		unregister_class(cls)	
		
	del bpy.types.Scene.show_ik_fk_advanced