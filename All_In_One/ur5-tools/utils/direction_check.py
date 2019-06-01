import bpy

"""
In most cases, we want the Elbow mesh to be pointing semi-downwards in the -z direction. 

In general, the Elbow Mesh, Shoulder mesh and the table would make a "triangle"

Extended to other meshes/bones

Returns if the direction of the Elbow mesh is right
"""

def direction_vector(start_bone, end_bone):
	"""
	Returns the vector from the head of the start_bone to the tail of the end_bone
	"""
	start = start_bone.head
	end = end_bone.tail

	return end-start

def check_elbow_direction():
	"""
	Returns if the elbow has a negative z direction
	"""
	start_bone = bpy.data.objects['Armature'].pose.bones['Shoulder']
	end_bone = bpy.data.objects['Armature'].pose.bones['Elbow']
	vector = direction_vector(start_bone, end_bone)
	return vector.z < 0

def check_wrist2_direction(direction = 1):
	"""
	Returns if the wrist2 is in given direction
	
	Direction defaults to upwards
	"""

	bone = bpy.data.objects['Armature'].pose.bones['Wrist2']
	if(direction > 0):
		return direction_vector(bone,bone) < 0
	else:
		return direction_vector(bone,bone) > 0

def _get_local_orientation(pose_bone):
	"""
	Returns the translation/location matrix of a bone
	"""

    local_orientation = pose_bone.matrix_channel.to_translation()
 
    if pose_bone.parent is None:
        return local_orientation
    else:
        my_orientation = pose_bone.matrix_channel.copy()
        parent_orientation = pose_bone.parent.matrix_channel.copy()
 
        my_orientation.invert()
        orientation = (my_orientation * parent_orientation).to_translation()
 
    return orientation

def check_target_align():
	"""
	Returns whether the IK target is aligned with the Wrist3 bone or if the two bones are connected
	"""
	
	target = bpy.data.objects['IK Target'].pose.bones['Bone']
	wrist = bpy.data.objects['Armature'].pose.bones['Wrist3']
	target_translation =_get_local_orientation(bpy.data.objects['IK Target'].pose.bones['Bone'])
	wrist_translation = _get_local_orientation(bpy.data.objects['Armature'].pose.bones['Wrist3'])
	target_vector_normalized = target.vector.normalized
	wrist_vector_normalized = wrist.vector.normalized
	if(target_vector_normalized != wrist_vector_normalized):
		return False
	if((target.tail + target_translation) != (wrist.head + wrist_translation)):
		return False
	return True