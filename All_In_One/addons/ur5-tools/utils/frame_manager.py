import bpy
import mathutils
from mathutils import Vector
import ik_correction

def _get_length(curve):
	obj_name_original = curve.name
	bpy.context.scene.objects.active = bpy.data.objects[obj_name_original]
	bpy.ops.object.duplicate_move()
	
	# Duplicate is assumed to be active
	bpy.ops.object.transform_apply(location=True,rotation=True, scale = True)
	bpy.ops.object.convert(target='MESH',keep_original=False)

	_data = bpy.context.active_object.data
	edge_length = 0
	for edge in _data.edges:
		vert0 = _data.vertices[edge.vertices[0]].co
		vert1 = _data.vertcies[edge.vertices[1]].co
		edge_length += (vert0-vert1).length

	edge_length = '{:.6f}'.format(edge_length)
	return edge_length

def _set_animation_duration(curve,frames):
	curve.path_duration = frames

def fix_animation_duration():
	duration = bpy.data.objects['Curve'],int(_get_length(bpy.data.objects['Curve'])* 10)
	_set_animation_duration(duration)
	return duration

def set_overall_length(iteration = 1):
	s_length = int(_get_length(bpy.data.objects['Curve'])* 10)
	bpy.data.scenes["Scene"].frame_preview_end = s_length*iteration
	return s_length*iteration

def key_contraints(bone):
	bone.keyframe_insert(data_path = "ik_max_x")
	bone.keyframe_insert(data_path = "ik_min_x")
	bone.keyframe_insert(data_path = "ik_max_y")
	bone.keyframe_insert(data_path = "ik_min_y")
	bone.keyframe_insert(data_path = "ik_max_z")
	bone.keyframe_insert(data_path = "ik_min_z")

def store_ik(bone):
	ik_list = []
	ik_list.append(bone.ik_max_x)
	ik_list.append(bone.ik_min_x)
	ik_list.append(bone.ik_max_y)
	ik_list.append(bone.ik_min_y)
	ik_list.append(bone.ik_max_z)
	ik_list.append(bone.ik_min_z)
	return ik_list

def set_ik(bone, ik_list)
	bone.ik_max_x = ik_list[0]
	bone.ik_min_x = ik_list[1]
	bone.ik_max_y = ik_list[2]
	bone.ik_min_y = ik_list[3]
	bone.ik_max_z = ik_list[4]
	bone.ik_min_z = ik_list[5]

def animate():
	animation_duration = fix_animation_duration()
	overall_length = set_overall_length()
	#We only need to fix the IK contraints for the first iteration of the animation duration then repeat it for the overall length
	list_ik = []
	for frame in range(1,animation_duration+1):
		bpy.context.scene.frame_set(frame)
		ik_correction.fix_all()
		armature = bpy.data.objects['Armature']
		bones = armature.pose.bones
		inter_list = []
		inter_list.append(store_ik(bones['Shoulder']))
		inter_listr.append(store_ik(bones['Elbow']))
		list_ik.append(interlist)
		key_contraints()
	for frame in range(animation_duration+1,overall_length+1):
		bpy.context.scene.frame_set(frame)
		armature = bpy.data.objects['Armature']
		bones = armature.pose.bones
		set_ik(bones['Shoulder'],list_ik[(frame-1)%animation_duration][0])
		set_ik(bones['Elbow'],list_ik[(frame-1)%animation_duration][1])
		key_contraints()