import bpy
from mathutils import Matrix, Vector, Quaternion
import mathutils
from math import acos, pi
from bpy.app.handlers import persistent
from . import auto_rig_datas


############################
## Math utility functions ##
############################
rig_id = ""

print ("\n Starting Auto-Rig Pro Functions... \n")

def perpendicular_vector(v):
	""" Returns a vector that is perpendicular to the one given.
		The returned vector is _not_ guaranteed to be normalized.
	"""
	# Create a vector that is not aligned with v.
	# It doesn't matter what vector.  Just any vector
	# that's guaranteed to not be pointing in the same
	# direction.
	if abs(v[0]) < abs(v[1]):
		tv = Vector((1,0,0))
	else:
		tv = Vector((0,1,0))

	# Use cross prouct to generate a vector perpendicular to
	# both tv and (more importantly) v.
	return v.cross(tv)


def rotation_difference(mat1, mat2):
	""" Returns the shortest-path rotational difference between two
		matrices.
	"""
	q1 = mat1.to_quaternion()
	q2 = mat2.to_quaternion()
	angle = acos(min(1,max(-1,q1.dot(q2)))) * 2
	if angle > pi:
		angle = -angle + (2*pi)
	return angle


#########################################
## "Visual Transform" helper functions ##
#########################################

def get_pose_matrix_in_other_space(mat, pose_bone):
	""" Returns the transform matrix relative to pose_bone's current
		transform space.  In other words, presuming that mat is in
		armature space, slapping the returned matrix onto pose_bone
		should give it the armature-space transforms of mat.
		TODO: try to handle cases with axis-scaled parents better.
	"""
	rest = pose_bone.bone.matrix_local.copy()
	rest_inv = rest.inverted()
	if pose_bone.parent:
		par_mat = pose_bone.parent.matrix.copy()
		par_inv = par_mat.inverted()
		par_rest = pose_bone.parent.bone.matrix_local.copy()
	else:
		par_mat = Matrix()
		par_inv = Matrix()
		par_rest = Matrix()

	# Get matrix in bone's current transform space
	smat = rest_inv * (par_rest * (par_inv * mat))

	# Compensate for non-local location
	#if not pose_bone.bone.use_local_location:
	#	 loc = smat.to_translation() * (par_rest.inverted() * rest).to_quaternion()
	#	 smat.translation = loc

	return smat


def get_local_pose_matrix(pose_bone):
	""" Returns the local transform matrix of the given pose bone.
	"""
	return get_pose_matrix_in_other_space(pose_bone.matrix, pose_bone)


def set_pose_translation(pose_bone, mat):
	""" Sets the pose bone's translation to the same translation as the given matrix.
		Matrix should be given in bone's local space.
	"""
	if pose_bone.bone.use_local_location == True:
		pose_bone.location = mat.to_translation()
	else:
		loc = mat.to_translation()

		rest = pose_bone.bone.matrix_local.copy()
		if pose_bone.bone.parent:
			par_rest = pose_bone.bone.parent.matrix_local.copy()
		else:
			par_rest = Matrix()

		q = (par_rest.inverted() * rest).to_quaternion()
		pose_bone.location = q * loc


def set_pose_rotation(pose_bone, mat):
	""" Sets the pose bone's rotation to the same rotation as the given matrix.
		Matrix should be given in bone's local space.
	"""
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


def set_pose_scale(pose_bone, mat):
	""" Sets the pose bone's scale to the same scale as the given matrix.
		Matrix should be given in bone's local space.
	"""
	pose_bone.scale = mat.to_scale()


def match_pose_translation(pose_bone, target_bone):
	""" Matches pose_bone's visual translation to target_bone's visual
		translation.
		This function assumes you are in pose mode on the relevant armature.
	"""
	mat = get_pose_matrix_in_other_space(target_bone.matrix, pose_bone)
	set_pose_translation(pose_bone, mat)
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.mode_set(mode='POSE')


def match_pose_rotation(pose_bone, target_bone):
	""" Matches pose_bone's visual rotation to target_bone's visual
		rotation.
		This function assumes you are in pose mode on the relevant armature.
	"""
	mat = get_pose_matrix_in_other_space(target_bone.matrix, pose_bone)
	set_pose_rotation(pose_bone, mat)
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.mode_set(mode='POSE')


def match_pose_scale(pose_bone, target_bone):
	""" Matches pose_bone's visual scale to target_bone's visual
		scale.
		This function assumes you are in pose mode on the relevant armature.
	"""
	mat = get_pose_matrix_in_other_space(target_bone.matrix, pose_bone)
	set_pose_scale(pose_bone, mat)
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.mode_set(mode='POSE')


##############################
## IK/FK snapping functions ##
##############################

def match_pole_target(ik_first, ik_last, pole, match_bone, length):
	""" Places an IK chain's pole target to match ik_first's
		transforms to match_bone.  All bones should be given as pose bones.
		You need to be in pose mode on the relevant armature object.
		ik_first: first bone in the IK chain
		ik_last:  last bone in the IK chain
		pole:  pole target bone for the IK chain
		match_bone:	 bone to match ik_first to (probably first bone in a matching FK chain)
		length:	 distance pole target should be placed from the chain center
	"""
	a = ik_first.matrix.to_translation()
	b = ik_last.matrix.to_translation() + ik_last.vector

	# Vector from the head of ik_first to the
	# tip of ik_last
	ikv = b - a

	# Get a vector perpendicular to ikv
	pv = perpendicular_vector(ikv).normalized() * length

	def set_pole(pvi):
		""" Set pole target's position based on a vector
			from the arm center line.
		"""
		# Translate pvi into armature space
		ploc = a + (ikv/2) + pvi

		# Set pole target to location
		mat = get_pose_matrix_in_other_space(Matrix.Translation(ploc), pole)
		set_pose_translation(pole, mat)

		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.mode_set(mode='POSE')

	set_pole(pv)

	# Get the rotation difference between ik_first and match_bone
	angle = rotation_difference(ik_first.matrix, match_bone.matrix)

	# Try compensating for the rotation difference in both directions
	pv1 = Matrix.Rotation(angle, 4, ikv) * pv
	set_pole(pv1)
	ang1 = rotation_difference(ik_first.matrix, match_bone.matrix)

	pv2 = Matrix.Rotation(-angle, 4, ikv) * pv
	set_pole(pv2)
	ang2 = rotation_difference(ik_first.matrix, match_bone.matrix)

	# Do the one with the smaller angle
	if ang1 < ang2:
		set_pole(pv1)	 


def fk2ik_arm(obj, fk, ik):
	""" Matches the fk bones in an arm rig to the ik bones.
		obj: armature object
		fk:	 list of fk bone names
		ik:	 list of ik bone names
	"""
	uarm  = obj.pose.bones[fk[0]]
	farm  = obj.pose.bones[fk[1]]
	hand  = obj.pose.bones[fk[2]]
	uarmi = obj.pose.bones[ik[0]]
	farmi = obj.pose.bones[ik[1]]
	handi = obj.pose.bones[ik[2]]
	switch = obj.pose.bones[ik[3]]
	pole = obj.pose.bones[ik[4]]

	# Stretch
	if handi['auto_stretch'] == 0.0:
		hand['stretch_length'] = handi['stretch_length']
	else:
		#print("diff=", uarmi.length / uarm.length, farmi.length / farm.length)
		diff = (uarmi.length+farmi.length) / (uarm.length+farm.length)
		hand['stretch_length'] *= diff

	# Upper arm snap
	match_pose_rotation(uarm, uarmi)
	#match_pose_scale(uarm, uarmi)

	# Forearm snap
	match_pose_rotation(farm, farmi)
	#match_pose_scale(farm, farmi)

	# Hand snap
	match_pose_rotation(hand, handi)
	
	hand.scale[0]=handi.scale[0]
	hand.scale[1]=handi.scale[1]
	hand.scale[2]=handi.scale[2]
	
	#rot debug
	farm.rotation_euler[0]=0
	farm.rotation_euler[1]=0
	
	#switch
	handi['ik_fk_switch'] = 1.0

	#udpate view
	bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, False, False), constraint_orientation='NORMAL', mirror=False)

	
	#insert key if autokey enable
	if bpy.context.scene.tool_settings.use_keyframe_insert_auto == True:
		#fk chain
		handi.keyframe_insert(data_path='["ik_fk_switch"]')
		hand.keyframe_insert(data_path='["stretch_length"]')
		hand.keyframe_insert(data_path="scale")
		hand.keyframe_insert(data_path="rotation_euler")
		uarm.keyframe_insert(data_path="rotation_euler")
		farm.keyframe_insert(data_path="rotation_euler")
				
		#ik chain
		handi.keyframe_insert(data_path='["stretch_length"]')
		handi.keyframe_insert(data_path='["auto_stretch"]')
		handi.keyframe_insert(data_path="location")
		handi.keyframe_insert(data_path="rotation_euler")
		handi.keyframe_insert(data_path="scale")
		pole.keyframe_insert(data_path="location")
		

def set_inverse_child(b):
		pbone = bpy.context.active_object.pose.bones[b]
		context_copy = bpy.context.copy()
		context_copy["constraint"] = pbone.constraints["Child Of"]
		bpy.context.active_object.data.bones.active = pbone.bone
		bpy.ops.constraint.childof_set_inverse(context_copy, constraint="Child Of", owner='BONE')	 


def ik2fk_arm(obj, fk, ik):
	""" Matches the ik bones in an arm rig to the fk bones.
		obj: armature object
		fk:	 list of fk bone names
		ik:	 list of ik bone names
	"""
	uarm  = obj.pose.bones[fk[0]]
	farm  = obj.pose.bones[fk[1]]
	hand  = obj.pose.bones[fk[2]]
	polefk = obj.pose.bones[fk[3]]
	uarmi = obj.pose.bones[ik[0]]
	farmi = obj.pose.bones[ik[1]]
	handi = obj.pose.bones[ik[2]]
	pole  = obj.pose.bones[ik[3]]
	#switch = obj.pose.bones[ik[4]]
 

	# Stretch
	handi['stretch_length'] = hand['stretch_length']
	
	# Hand position
	""""
	match_pose_translation(handi, hand)
	match_pose_rotation(handi, hand)
	
	# Hand scale
	handi.scale[0]=hand.scale[0]
	handi.scale[1]=hand.scale[1]
	handi.scale[2]=hand.scale[2]
	"""
	# 'child-of' constraints handling
	cns = None
	
	try:
		cns = handi.constraints
		constraint = cns[0]
	except:
		pass
		
	bone_parent_string = ""
	parent_type = ""	
	
	if cns != None:
		# get active Child Of constraint, target and subtarget
		for c in cns:
			if not c.mute and c.influence > 0.5 and c.type == 'CHILD_OF':
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
		
		# snap
		if parent_type == "bone":
			bone_parent = bpy.context.object.pose.bones[bone_parent_string]
			handi.matrix = bone_parent.matrix_channel.inverted()*hand.matrix
		if parent_type == "object":
			bone_parent = bpy.data.objects[bone_parent_string]
			obj = bpy.data.objects[bone_parent_string]
			handi.matrix = constraint.inverse_matrix.inverted() *obj.matrix_world.inverted() *	hand.matrix

			
	# Pole target position
	match_pose_translation(pole, polefk)	
	
	#switch
	handi['ik_fk_switch'] = 0.0
	
	# set inverse for child of constraint
	#set_inverse_child(handi.name)	 
	
	#update view
	bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, False, False), constraint_orientation='NORMAL', mirror=False)
	
	 #insert key if autokey enable
	if bpy.context.scene.tool_settings.use_keyframe_insert_auto == True:
		#ik chain
		handi.keyframe_insert(data_path='["ik_fk_switch"]')
		handi.keyframe_insert(data_path='["stretch_length"]')
		handi.keyframe_insert(data_path='["auto_stretch"]')
		handi.keyframe_insert(data_path="location")
		handi.keyframe_insert(data_path="rotation_euler")
		handi.keyframe_insert(data_path="scale")
		pole.keyframe_insert(data_path="location")
		
		#fk chain
		hand.keyframe_insert(data_path='["stretch_length"]')
		hand.keyframe_insert(data_path="location")		  
		hand.keyframe_insert(data_path="rotation_euler")
		hand.keyframe_insert(data_path="scale")
		uarm.keyframe_insert(data_path="rotation_euler")
		farm.keyframe_insert(data_path="rotation_euler")
		
		
		  


def fk2ik_leg(obj, fk, ik):
	""" Matches the fk bones in an arm rig to the ik bones.
		obj: armature object
		fk:	 list of fk bone names
		ik:	 list of ik bone names
	"""
	thigh  = obj.pose.bones[fk[0]]
	leg	 = obj.pose.bones[fk[1]]
	foot  = obj.pose.bones[fk[2]]
	toes = obj.pose.bones[fk[3]]
	thighi = obj.pose.bones[ik[0]]
	legi = obj.pose.bones[ik[1]]
	footi = obj.pose.bones[ik[2]]	 
	toesi = obj.pose.bones[ik[3]]
	footi_rot = obj.pose.bones[ik[4]]
	#switch = obj.pose.bones[ik[5]]
	foot_01 = obj.pose.bones[ik[6]]
	foot_roll = obj.pose.bones[ik[7]]
	pole = obj.pose.bones[ik[8]]


	# Stretch
	if footi['auto_stretch'] == 0.0:
		foot['stretch_length'] = footi['stretch_length']
	else:
		diff = (thighi.length+legi.length) / (thigh.length+leg.length)
	   
		foot['stretch_length'] *= diff

	# Thigh snap
	match_pose_rotation(thigh, thighi)

	# Leg snap
	match_pose_rotation(leg, legi)	  

	# Foot snap
	match_pose_rotation(foot, footi_rot)
		#scale	  
	foot.scale[0]=footi.scale[0]
	foot.scale[1]=footi.scale[1]
	foot.scale[2]=footi.scale[2]
	
	
	#Toes snap
	match_pose_rotation(toes, toesi)
		#scale
	toes.scale[0]=toesi.scale[0]
	toes.scale[1]=toesi.scale[1]
	toes.scale[2]=toesi.scale[2]	

	#rotation debug
	leg.rotation_euler[0]=0
	leg.rotation_euler[1]=0
	
	 #switch
	footi['ik_fk_switch'] = 1.0
	
	#insert key if autokey enable
	if bpy.context.scene.tool_settings.use_keyframe_insert_auto == True:
		#fk chain
		footi.keyframe_insert(data_path='["ik_fk_switch"]')
		foot.keyframe_insert(data_path='["stretch_length"]')
		foot.keyframe_insert(data_path="scale")
		foot.keyframe_insert(data_path="rotation_euler")
		thigh.keyframe_insert(data_path="rotation_euler")
		leg.keyframe_insert(data_path="rotation_euler")
		toes.keyframe_insert(data_path="rotation_euler")
		toes.keyframe_insert(data_path="scale")
		
		#ik chain		 
		footi.keyframe_insert(data_path='["stretch_length"]')
		footi.keyframe_insert(data_path='["auto_stretch"]')
		footi.keyframe_insert(data_path="location")
		footi.keyframe_insert(data_path="rotation_euler")
		footi.keyframe_insert(data_path="scale")
		foot_01.keyframe_insert(data_path="rotation_euler")
		foot_roll.keyframe_insert(data_path="location")		  
		toesi.keyframe_insert(data_path="rotation_euler")
		toesi.keyframe_insert(data_path="scale")		
		pole.keyframe_insert(data_path="location")
  

def ik2fk_leg(obj, fk, ik):
	""" Matches the ik bones in an arm rig to the fk bones.
		obj: armature object
		fk:	 list of fk bone names
		ik:	 list of ik bone names
	"""
	thigh  = obj.pose.bones[fk[0]]
	leg	 = obj.pose.bones[fk[1]]
	foot  = obj.pose.bones[fk[2]]
	toes = obj.pose.bones[fk[3]]
	polefk = obj.pose.bones[fk[4]]
	thighi = obj.pose.bones[ik[0]]
	legi = obj.pose.bones[ik[1]]
	footi = obj.pose.bones[ik[2]]
	pole  = obj.pose.bones[ik[3]]
	toesi = obj.pose.bones[ik[4]]
	foot_01 = obj.pose.bones[ik[5]]
	foot_roll = obj.pose.bones[ik[6]]
	#switch = obj.pose.bones[ik[7]]

	# Stretch
	footi['stretch_length'] = foot['stretch_length']
   
	#reset IK foot_01 and foot_roll
	foot_01.rotation_euler[0]=0
	foot_roll.location[0]=0
	foot_roll.location[2]=0
	
	"""
	# foot snap
	match_pose_translation(footi, foot)
	match_pose_rotation(footi, foot)
	
		#scale
	footi.scale[0]=foot.scale[0]
	footi.scale[1]=foot.scale[1]
	footi.scale[2]=foot.scale[2]
	"""
	#toes snap	  
	#match_pose_rotation(toesi, toes)
	toesi.rotation_euler= toes.rotation_euler
	toesi.scale = toes.scale
	
	# 'child-of' constraints handling
	cns = None
	
	try:
		cns = footi.constraints
		constraint = cns[0]
	except:
		pass
		
	bone_parent_string = ""
	parent_type = ""	
	
	if cns != None:
		# get active Child Of constraint, target and subtarget
		for c in cns:
			if not c.mute and c.influence > 0.5 and c.type == 'CHILD_OF':
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
		
		# snap
		if parent_type == "bone":
			bone_parent = bpy.context.object.pose.bones[bone_parent_string]
			footi.matrix = bone_parent.matrix_channel.inverted()*foot.matrix
		if parent_type == "object":
			bone_parent = bpy.data.objects[bone_parent_string]
			obj = bpy.data.objects[bone_parent_string]
			footi.matrix = constraint.inverse_matrix.inverted() *obj.matrix_world.inverted() *	foot.matrix
	
	
		#scale
		"""
	toesi.scale[0]=toes.scale[0]
	toesi.scale[1]=toes.scale[1]
	toesi.scale[2]=toes.scale[2] 
	"""
	
	# Pole target position
	pole_parent = None
	if pole.parent:
		pole_parent = pole.parent
	
	if pole_parent != None:
		# apply double time because of dependecy lag
		pole.matrix = polefk.matrix
		#update view
		bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, False, False), constraint_orientation='NORMAL', mirror=False)
		# second apply
		pole.matrix = polefk.matrix
	else:
		pole.matrix = polefk.matrix
	#match_pose_translation(pole, polefk)
	
	 #switch
	footi['ik_fk_switch'] = 0.0
	
	# set inverse for child of constraints
	#set_inverse_child(footi.name)	 
	
	#update view
	bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, False, False), constraint_orientation='NORMAL', mirror=False)
	
	#insert key if autokey enable
	if bpy.context.scene.tool_settings.use_keyframe_insert_auto == True:
		#ik chain
		footi.keyframe_insert(data_path='["ik_fk_switch"]')
		footi.keyframe_insert(data_path='["stretch_length"]')
		foot_01.keyframe_insert(data_path="rotation_euler")
		foot_roll.keyframe_insert(data_path="location")
		footi.keyframe_insert(data_path='["auto_stretch"]')
		footi.keyframe_insert(data_path="location")
		footi.keyframe_insert(data_path="rotation_euler")
		footi.keyframe_insert(data_path="scale")
		toesi.keyframe_insert(data_path="rotation_euler")
		toesi.keyframe_insert(data_path="scale")		
		pole.keyframe_insert(data_path="location")
		
		#fk chain
		foot.keyframe_insert(data_path='["stretch_length"]')
		foot.keyframe_insert(data_path="rotation_euler")
		foot.keyframe_insert(data_path="scale")
		thigh.keyframe_insert(data_path="rotation_euler")
		leg.keyframe_insert(data_path="rotation_euler")
		toes.keyframe_insert(data_path="rotation_euler")
		toes.keyframe_insert(data_path="scale")

@persistent
def auto_ui_cam(dummy): 

	has_active_ob = False
	
	try:
		ob = bpy.context.active_object	
		has_active_ob = True
	except:
		pass
		
	if has_active_ob:
		rig = ob		
		scene = bpy.context.scene			
 
		try:
			# select character mesh case		
			if ob.type == 'MESH':		   
				ob_parent = ob.parent			 
				for child in ob_parent.children:
					if 'char_' or 'char1_' in child.name:					 
						for child1 in child.children:
							if 'rig' in child1.name:							
								for child2 in child1.children:
									if 'cam_ui' in child2.name:
										rig = child1
													
					
			for children in rig.children:				 
				if "cam_ui" in children.name:					  
					for area in bpy.context.screen.areas: # iterate through areas in current screen
						if area.type == 'VIEW_3D':						   
							for space in area.spaces: # iterate through spaces in current VIEW_3D area
								if space.type == 'VIEW_3D': # check if space is a 3D view								  
									if space.lock_camera_and_layers == False:
										if space.camera != children:
											space.camera = children	  
											
		except:
			pass

			
def get_data_bone(name):
	try:
		return bpy.context.object.data.bones[name]
	except:
		return None
		
def get_pose_bone(name):  
	return bpy.context.object.pose.bones[name]
		
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
	
	
	

class toggle_multi(bpy.types.Operator):
	"""Toggle multi-limb visibility"""

	bl_idname = "id.toggle_multi" + rig_id
	bl_label = "toggle_multi"
	bl_options = {'UNDO'}
	
	limb = bpy.props.StringProperty(name="Limb")
	id = bpy.props.StringProperty(name="Id")
	key = bpy.props.StringProperty(name="key")
	"""
	@classmethod
	def poll(cls, context):
		return (context.active_object != None and context.mode == 'POSE')
	"""
	
	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:
			_toggle_multi(self.limb, self.id, self.key)
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo
		return {'FINISHED'}

class Rigify_Arm_FK2IK(bpy.types.Operator):
	""" Snaps an FK arm to an IK arm.
	"""
	bl_idname = "pose.rigify_arm_fk2ik_" + rig_id
	bl_label = "Rigify Snap FK arm to IK"
	bl_options = {'UNDO'}

	uarm_fk = bpy.props.StringProperty(name="Upper Arm FK Name")
	farm_fk = bpy.props.StringProperty(name="Forerm FK Name")
	hand_fk = bpy.props.StringProperty(name="Hand FK Name")

	uarm_ik = bpy.props.StringProperty(name="Upper Arm IK Name")
	farm_ik = bpy.props.StringProperty(name="Forearm IK Name")
	hand_ik = bpy.props.StringProperty(name="Hand IK Name")
	pole	= bpy.props.StringProperty(name="Pole IK Name")
	switch = bpy.props.StringProperty(name="Switch Name")
	

	@classmethod
	def poll(cls, context):
		return (context.active_object != None and context.mode == 'POSE')

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:
			fk2ik_arm(context.active_object, fk=[self.uarm_fk, self.farm_fk, self.hand_fk], ik=[self.uarm_ik, self.farm_ik, self.hand_ik, self.switch, self.pole])
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo
		return {'FINISHED'}


class Rigify_Arm_IK2FK(bpy.types.Operator):
	""" Snaps an IK arm to an FK arm.
	"""
	bl_idname = "pose.rigify_arm_ik2fk_" + rig_id
	bl_label = "Rigify Snap IK arm to FK"
	bl_options = {'UNDO'}

	uarm_fk = bpy.props.StringProperty(name="Upper Arm FK Name")
	farm_fk = bpy.props.StringProperty(name="Forerm FK Name")
	hand_fk = bpy.props.StringProperty(name="Hand FK Name")
	pole_fk = bpy.props.StringProperty(name="Pole FK Name")

	uarm_ik = bpy.props.StringProperty(name="Upper Arm IK Name")
	farm_ik = bpy.props.StringProperty(name="Forearm IK Name")
	hand_ik = bpy.props.StringProperty(name="Hand IK Name")
	pole	= bpy.props.StringProperty(name="Pole IK Name")
	switch = bpy.props.StringProperty(name="Switch Name")

	@classmethod
	def poll(cls, context):
		return (context.active_object != None and context.mode == 'POSE')

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:
			ik2fk_arm(context.active_object, fk=[self.uarm_fk, self.farm_fk, self.hand_fk, self.pole_fk], ik=[self.uarm_ik, self.farm_ik, self.hand_ik, self.pole, self.switch])
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo
		return {'FINISHED'}


class Rigify_Leg_FK2IK(bpy.types.Operator):
	""" Snaps an FK leg to an IK leg.
	"""
	bl_idname = "pose.rigify_leg_fk2ik_" + rig_id
	bl_label = "Rigify Snap FK leg to IK"
	bl_options = {'UNDO'}

	thigh_fk = bpy.props.StringProperty(name="Thigh FK Name")
	leg_fk	= bpy.props.StringProperty(name="Shin FK Name")
	foot_fk	 = bpy.props.StringProperty(name="Foot FK Name")
	toes_fk = bpy.props.StringProperty(name="Toes FK Name")

	thigh_ik = bpy.props.StringProperty(name="Thigh IK Name")
	leg_ik	= bpy.props.StringProperty(name="Shin IK Name")	   
	foot_ik	 = bpy.props.StringProperty(name="Foot IK Name")
	foot_01 = bpy.props.StringProperty(name="Foot_01 IK Name")
	foot_roll = bpy.props.StringProperty(name="Foot_roll IK Name")
	toes_ik = bpy.props.StringProperty(name="Toes IK Name")
	foot_ik_rot = bpy.props.StringProperty(name="Foot IK Name")	   
	pole = bpy.props.StringProperty(name="Pole IK  Name")
	switch = bpy.props.StringProperty(name="Switch Name")

	@classmethod
	def poll(cls, context):
		return (context.active_object != None and context.mode == 'POSE')

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:
			fk2ik_leg(context.active_object, fk=[self.thigh_fk, self.leg_fk, self.foot_fk, self.toes_fk], ik=[self.thigh_ik, self.leg_ik, self.foot_ik, self.toes_ik, self.foot_ik_rot, self.switch, self.foot_01, self.foot_roll, self.pole])
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo
		return {'FINISHED'}


class Rigify_Leg_IK2FK(bpy.types.Operator):
	""" Snaps an IK leg to an FK leg.
	"""
	bl_idname = "pose.rigify_leg_ik2fk_" + rig_id
	bl_label = "Rigify Snap IK leg to FK"
	bl_options = {'UNDO'}

	thigh_fk = bpy.props.StringProperty(name="Thigh FK Name")
	leg_fk = bpy.props.StringProperty(name="Shin FK Name")
	foot_fk = bpy.props.StringProperty(name="Foot FK Name")
	toes_fk = bpy.props.StringProperty(name="Toes FK Name")
	pole_fk = bpy.props.StringProperty(name="Pole FK Name")

	thigh_ik = bpy.props.StringProperty(name="Thigh IK Name")
	leg_ik = bpy.props.StringProperty(name="Shin IK Name")	  
	foot_ik = bpy.props.StringProperty(name="Foot IK Name")
	pole = bpy.props.StringProperty(name="Pole IK Name")
	toes_ik = bpy.props.StringProperty(name="Toes IK Name")
	foot_01= bpy.props.StringProperty(name="Foot01 IK Name")
	foot_roll= bpy.props.StringProperty(name="Foot_roll IK Name")
	switch = bpy.props.StringProperty(name="Switch Name")

	@classmethod
	def poll(cls, context):
		return (context.active_object != None and context.mode == 'POSE')

	def execute(self, context):
		use_global_undo = context.user_preferences.edit.use_global_undo
		context.user_preferences.edit.use_global_undo = False
		try:
			ik2fk_leg(context.active_object, fk=[self.thigh_fk, self.leg_fk, self.foot_fk, self.toes_fk, self.pole_fk], ik=[self.thigh_ik, self.leg_ik, self.foot_ik, self.pole, self.toes_ik, self.foot_01, self.foot_roll, self.switch])
		finally:
			context.user_preferences.edit.use_global_undo = use_global_undo
		return {'FINISHED'}


	
  

###################
## Rig UI Panels ##
###################

class RigUI(bpy.types.Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_label = "Rig Main Properties"
	bl_idname = rig_id + "_PT_rig_ui"

	@classmethod
	def poll(self, context):
		if context.mode != 'POSE':
			return False
		try:
			return (context.active_object.data.get("rig_id") == rig_id)
		except (AttributeError, KeyError, TypeError):
			return False

	def draw(self, context):
		layout = self.layout
		pose_bones = context.active_object.pose.bones
		try:
			selected_bones = [bone.name for bone in context.selected_pose_bones]
			selected_bones += [context.active_pose_bone.name]
			
		except (AttributeError, TypeError):
			return
			
		try:
			temp_bone_id = context.active_pose_bone.name[:-2][-3:]
		   
			bone_id = ""
			if temp_bone_id.isdigit():
				bone_id = "_dupli_"+temp_bone_id
			#print(bone_id)
		except:
			pass

		def is_selected(names):
			# Returns whether any of the named bones are selected.
			if type(names) == list:
				for name in names:
					if name in selected_bones:
						return True
			elif names in selected_bones:
				return True
			return False 

		if not 'humanoid' in bpy.context.active_object.name:
	  
		   #LEFT LEG
			fk_leg = ["c_thigh_fk" + bone_id + ".l", "c_leg_fk" + bone_id + ".l", "c_foot_fk" + bone_id + ".l", "c_toes_fk"+ bone_id +".l", "leg_fk_pole" + bone_id + ".l"]
			ik_leg = ["thigh_ik" + bone_id + ".l", "leg_ik" + bone_id + ".l", "c_foot_ik"+ bone_id + ".l", "c_leg_pole" + bone_id + ".l", "c_toes_ik" + bone_id + ".l", "c_foot_01" + bone_id + ".l", "c_foot_roll_cursor" + bone_id + ".l", "foot_snap_fk" + bone_id + ".l", "c_ikfk_leg" + bone_id + ".l"]
	   
		   
							
			if is_selected(fk_leg) or is_selected(ik_leg):
				layout.label("Left Leg:")
				
			   #stretch length property
				if is_selected(fk_leg):
					layout.prop(pose_bones["c_foot_fk"+bone_id+".l"], '["stretch_length"]', text="Stretch Length (FK)", slider=True)			
				if is_selected(ik_leg):
					layout.prop(pose_bones["c_foot_ik"+bone_id+".l"], '["stretch_length"]', text="Stretch Length (IK)", slider=True)
					#auto_stretch ik property
					layout.prop(pose_bones["c_foot_ik"+bone_id+".l"], '["auto_stretch"]', text="Auto Stretch", slider=True) 
					
				#fix_roll prop		 
				layout.prop(pose_bones["c_foot_ik"+bone_id+".l"], '["fix_roll"]', text="Fix Roll", slider=True) 
				  
				layout.separator()				  
					
				layout.prop(pose_bones["c_foot_ik"+bone_id+".l"], '["ik_fk_switch"]', text="IK-FK Switch", slider=True)
				p = layout.operator("pose.rigify_leg_fk2ik_" + rig_id, text="Snap FK > IK")
				p.thigh_fk = fk_leg[0]
				p.leg_fk = fk_leg[1]
				p.foot_fk = fk_leg[2]
				p.toes_fk = fk_leg[3]			 
				p.thigh_ik = ik_leg[0]
				p.leg_ik  = ik_leg[1]
				p.foot_ik = ik_leg[2]
				p.pole = ik_leg[3]
				p.toes_ik = ik_leg[4]
				p.foot_01 = ik_leg[5]
				p.foot_roll = ik_leg[6]
				p.foot_ik_rot = ik_leg[7]
				p.switch = ik_leg[8]			
				p = layout.operator("pose.rigify_leg_ik2fk_" + rig_id, text="Snap IK > FK")
				p.thigh_fk = fk_leg[0]
				p.leg_fk = fk_leg[1]  
				p.foot_fk = fk_leg[2]
				p.toes_fk = fk_leg[3]
				p.pole_fk = fk_leg[4]		  
				p.thigh_ik = ik_leg[0]
				p.leg_ik = ik_leg[1]
				p.foot_ik = ik_leg[2] 
				p.pole = ik_leg[3]
				p.toes_ik = ik_leg[4]
				p.foot_01 = ik_leg[5]
				p.foot_roll = ik_leg[6]
				p.switch = ik_leg[8] 

			if is_selected(fk_leg+ik_leg):
				layout.separator()
			
			#RIGHT LEG		  
			fk_leg = ["c_thigh_fk"+bone_id+".r", "c_leg_fk"+bone_id+".r", "c_foot_fk"+bone_id+".r","c_toes_fk"+bone_id+".r", "leg_fk_pole"+bone_id+".r"]
			ik_leg = ["thigh_ik"+bone_id+".r", "leg_ik"+bone_id+".r", "c_foot_ik"+bone_id+".r", "c_leg_pole"+bone_id+".r", "c_toes_ik"+bone_id+".r", "c_foot_01"+bone_id+".r", "c_foot_roll_cursor"+bone_id+".r", "foot_snap_fk"+bone_id+".r", "c_ikfk_leg"+bone_id+".r"]
			
						
			if is_selected(fk_leg) or is_selected(ik_leg): 
				layout.label("Right Leg:")
			   #stretch length property
				if is_selected(fk_leg):
					layout.prop(pose_bones["c_foot_fk"+bone_id+".r"], '["stretch_length"]', text="Stretch Length (FK)", slider=True)			
				if is_selected(ik_leg):
					layout.prop(pose_bones["c_foot_ik"+bone_id+".r"], '["stretch_length"]', text="Stretch Length (IK)", slider=True)
					#auto_stretch ik property
					layout.prop(pose_bones["c_foot_ik"+bone_id+".r"], '["auto_stretch"]', text="Auto Stretch", slider=True) 
					
				#fix_roll prop					 
				layout.prop(pose_bones["c_foot_ik"+bone_id+".r"], '["fix_roll"]', text="Fix Roll", slider=True) 
				   
				
				layout.separator() 
				layout.prop(pose_bones["c_foot_ik"+bone_id+".r"], '["ik_fk_switch"]', text="IK-FK Switch", slider=True)
				#Snap buttons
				p = layout.operator("pose.rigify_leg_fk2ik_" + rig_id, text="Snap FK > IK")
				p.thigh_fk = fk_leg[0]
				p.leg_fk = fk_leg[1]
				p.foot_fk = fk_leg[2]
				p.toes_fk = fk_leg[3]			  
				p.thigh_ik = ik_leg[0]
				p.leg_ik = ik_leg[1]
				p.foot_ik = ik_leg[2]
				p.pole = ik_leg[3]
				p.toes_ik = ik_leg[4]
				p.foot_01 = ik_leg[5]
				p.foot_roll = ik_leg[6]
				p.foot_ik_rot = ik_leg[7]
				p.switch = ik_leg[8]			   
				p = layout.operator("pose.rigify_leg_ik2fk_" + rig_id, text="Snap IK > FK")
				p.thigh_fk = fk_leg[0]
				p.leg_fk = fk_leg[1]
				p.foot_fk = fk_leg[2]
				p.toes_fk = fk_leg[3]
				p.pole_fk = fk_leg[4]				   
				p.thigh_ik = ik_leg[0]
				p.leg_ik = ik_leg[1]
				p.foot_ik = ik_leg[2] 
				p.pole = ik_leg[3]
				p.toes_ik = ik_leg[4]
				p.foot_01 = ik_leg[5]
				p.foot_roll = ik_leg[6]
				p.switch = ik_leg[8]
			   
			if is_selected(fk_leg+ik_leg):
				layout.separator()
			
			#LEFT ARM		 
			fk_arm = ["c_arm_fk" + bone_id +".l", "c_forearm_fk" + bone_id + ".l", "c_hand_fk" + bone_id + ".l", "arm_fk_pole" + bone_id + ".l"]
			ik_arm = ["arm_ik" + bone_id + ".l", "forearm_ik" + bone_id + ".l", "c_hand_ik" + bone_id + ".l", "c_arms_pole" + bone_id + ".l"]			

				#Snap buttons
			if is_selected(fk_arm) or is_selected(ik_arm):
				layout.label("Left Arm:")
			   #stretch length property
				if is_selected(fk_arm):
					layout.prop(pose_bones["c_hand_fk" + bone_id + ".l"], '["stretch_length"]', text="Stretch Length (FK)", slider=True)			
				if is_selected(ik_arm):
					layout.prop(pose_bones["c_hand_ik" + bone_id + ".l"], '["stretch_length"]', text="Stretch Length (IK)", slider=True)
				#auto_stretch ik property
					layout.prop(pose_bones["c_hand_ik" + bone_id + ".l"], '["auto_stretch"]', text="Auto Stretch", slider=True)	 
			
				layout.separator()				   
					
				layout.prop(pose_bones["c_hand_ik" + bone_id + ".l"], '["ik_fk_switch"]', text="IK-FK Switch", slider=True)
				
				props = layout.operator("pose.rigify_arm_fk2ik_" + rig_id, text="Snap FK > IK")
				props.uarm_fk = fk_arm[0]
				props.farm_fk = fk_arm[1]
				props.hand_fk = fk_arm[2]
				props.uarm_ik = ik_arm[0]
				props.farm_ik = ik_arm[1]
				props.hand_ik = ik_arm[2]
				props.pole = ik_arm[3]
				props.switch = ik_arm[2]
				props = layout.operator("pose.rigify_arm_ik2fk_" + rig_id, text="Snap IK > FK")
				props.uarm_fk = fk_arm[0]
				props.farm_fk = fk_arm[1]
				props.hand_fk = fk_arm[2]
				props.pole_fk = fk_arm[3]
				props.uarm_ik = ik_arm[0]
				props.farm_ik = ik_arm[1]
				props.hand_ik = ik_arm[2]
				props.pole = ik_arm[3]
				props.switch = ik_arm[2]	  

			if is_selected(fk_arm+ik_arm):
				layout.separator()
				
			 #RIGHT ARM			   
			fk_arm = ["c_arm_fk" + bone_id +".r", "c_forearm_fk" + bone_id + ".r", "c_hand_fk" + bone_id + ".r", "arm_fk_pole" + bone_id + ".r"]
			ik_arm = ["arm_ik" + bone_id + ".r", "forearm_ik" + bone_id + ".r", "c_hand_ik" + bone_id + ".r", "c_arms_pole" + bone_id + ".r"]
		   
			if is_selected(fk_arm) or is_selected(ik_arm):
				layout.label("Right Arm:")
			   #stretch length property
				if is_selected(fk_arm):
					layout.prop(pose_bones["c_hand_fk" + bone_id + ".r"], '["stretch_length"]', text="Stretch Length (FK)", slider=True)			
				if is_selected(ik_arm):
					layout.prop(pose_bones["c_hand_ik" + bone_id + ".r"], '["stretch_length"]', text="Stretch Length (IK)", slider=True)
				#auto_stretch ik property
					layout.prop(pose_bones["c_hand_ik" + bone_id + ".r"], '["auto_stretch"]', text="Auto Stretch", slider=True)	 
			
				layout.separator() 
				layout.prop(pose_bones["c_hand_ik" + bone_id + ".r"], '["ik_fk_switch"]', text="IK-FK Switch", slider=True)
				props = layout.operator("pose.rigify_arm_fk2ik_" + rig_id, text="Snap FK > IK")
				props.uarm_fk = fk_arm[0]
				props.farm_fk = fk_arm[1]
				props.hand_fk = fk_arm[2]
				props.uarm_ik = ik_arm[0]
				props.farm_ik = ik_arm[1]
				props.hand_ik = ik_arm[2]
				props.pole = ik_arm[3]
				props.switch = ik_arm[2]
				props = layout.operator("pose.rigify_arm_ik2fk_" + rig_id, text="Snap IK > FK")
				props.uarm_fk = fk_arm[0]
				props.farm_fk = fk_arm[1]
				props.hand_fk = fk_arm[2]
				props.pole_fk = fk_arm[3]
				props.uarm_ik = ik_arm[0]
				props.farm_ik = ik_arm[1]
				props.hand_ik = ik_arm[2]
				props.pole = ik_arm[3]
				props.switch = ik_arm[2]	  
		   
			if is_selected(fk_arm+ik_arm):
				layout.separator()
				
			# EYE AIM		 
			eye_aim_bones = ["c_eye_target.x", "c_eye_target.l", "c_eye_target.r", "c_eye.l", "c_eye.r"]
			if is_selected(eye_aim_bones):
				
				layout.prop(pose_bones["c_eye_target.x"], '["eye_target"]', text="Eye target follow", slider=True)
				
			# FINGERS BEND
			
			thumb_l = "c_thumb1_base" + bone_id + ".l"
			thumb_r = "c_thumb1_base" + bone_id + ".r"
			index_l = "c_index1_base" + bone_id + ".l"
			index_r = "c_index1_base" + bone_id + ".r"
			middle_l = "c_middle1_base" + bone_id + ".l"
			middle_r = "c_middle1_base" + bone_id + ".r"
			ring_l = "c_ring1_base"+ bone_id + ".l"
			ring_r = "c_ring1_base"+ bone_id + ".r"
			pinky_l = "c_pinky1_base"+ bone_id +".l"
			pinky_r = "c_pinky1_base"+ bone_id + ".r"	
			
			fingers = [thumb_l, thumb_r, index_l, index_r, middle_l, middle_r, ring_l, ring_r, pinky_l, pinky_r]
			finger_side = ""
			for fing in fingers:
				if is_selected(fing):
					if (fing[-2:] == ".l"):
						finger_side = "Left "
					if (fing[-2:] == ".r"):
						finger_side = "Right "				  
					text_upper = (fing[:3]).upper()
					layout.label(finger_side + text_upper[2:] + fing[3:-8] + ":")
					layout.prop(pose_bones[fing], '["bend_all"]', text="Bend All Phalanges", slider=True)
					
			# PINNING 
			pin_arms = ["c_stretch_arm_pin"+bone_id+".l", "c_stretch_arm_pin"+bone_id+".r", "c_stretch_arm"+bone_id+".l", "c_stretch_arm"+bone_id+".r"]		 
						
			for pin_arm in pin_arms:
				if is_selected(pin_arm):
					if (pin_arm[-2:] == ".l"):
						layout.label("Left Elbow Pinning")
						layout.prop(pose_bones["c_stretch_arm"+bone_id+".l"], '["elbow_pin"]', text="Elbow pinning", slider=True)
					if (pin_arm[-2:] == ".r"):
						layout.label("Right Elbow Pinning")
						layout.prop(pose_bones["c_stretch_arm"+bone_id+".r"], '["elbow_pin"]', text="Elbow pinning", slider=True)
						
			pin_legs = ["c_stretch_leg_pin"+bone_id+".l", "c_stretch_leg_pin"+bone_id+".r", "c_stretch_leg"+bone_id+".l", "c_stretch_leg"+bone_id+".r"]	 
			
			for pin_leg in pin_legs:
				if is_selected(pin_leg):
					if (pin_leg[-2:] == ".l"):
						layout.label("Left Knee Pinning")
						layout.prop(pose_bones["c_stretch_leg"+bone_id+".l"], '["leg_pin"]', text="Knee pinning", slider=True)
					if (pin_leg[-2:] == ".r"):
						layout.label("Right Knee Pinning")
						layout.prop(pose_bones["c_stretch_leg"+bone_id+".r"], '["leg_pin"]', text="Knee pinning", slider=True)
					
			#Head lock
			if is_selected(['c_head.x']):
				if len(pose_bones['c_head.x'].keys()) > 0:
					if 'head_free' in pose_bones['c_head.x'].keys():#retro compatibility
						layout.prop(pose_bones['c_head.x'], '["head_free"]', text = 'Head Lock', slider = True)
					
			#Multi Limb display
			if is_selected('c_pos'):
				layout.label('Multi-Limb Display:')
				#look for multi limbs
				
				if len(get_pose_bone('c_pos').keys()) > 0:
					for key in get_pose_bone('c_pos').keys():
						
						if 'leg' in key or 'arm' in key:
							row = layout.column(align=True)
							b = row.operator('id.toggle_multi', key)
							if 'leg' in key:
								b.limb = 'leg'
							if 'arm' in key:
								b.limb = 'arm'
							b.id = key[-5:]
							b.key = key
							row.prop(pose_bones['c_pos'], '["'+key+'"]', text=key)			  
							
				else:
					layout.label('No Multiple Limbs')
					
				
					
###########	 REGISTER  ##################

def register():	  
	#bpy.types.Scene.enable_auto_ui_cam	 = bpy.props.BoolProperty(name="enable_auto_ui_cam", description = "Enable auto UI camera switch for multiple characters", default = False)
	bpy.app.handlers.scene_update_pre.append(auto_ui_cam)
	
def unregister():	
	#del bpy.types.Scene.enable_auto_ui_cam
	bpy.app.handlers.scene_update_pre.remove(auto_ui_cam)
		