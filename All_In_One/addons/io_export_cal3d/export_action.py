import bpy
import mathutils

from . import armature_classes
from .armature_classes import *

from . import action_classes
from .action_classes import *

def get_action_group_fcurve(action_group, data_path, array_index):
	for fcu in action_group.channels:
		if fcu.data_path.find(data_path) != -1 and \
		    fcu.array_index == array_index:
			return fcu

	return None


def get_keyframes_list(fcu):
	keyframes_list = []
	if fcu:
		for keyframe in fcu.keyframe_points:
			keyframes_list.append(keyframe.co[0])
	return keyframes_list


def evaluate_loc(loc_x_fcu, loc_y_fcu, loc_z_fcu, keyframe):
	loc_x = 0.0
	loc_y = 0.0
	loc_z = 0.0

	if loc_x_fcu:
		loc_x = loc_x_fcu.evaluate(keyframe)

	if loc_y_fcu:
		loc_y = loc_y_fcu.evaluate(keyframe)

	if loc_z_fcu:
		loc_z = loc_z_fcu.evaluate(keyframe)

	return mathutils.Vector([loc_x, loc_y, loc_z])


def evaluate_quat(quat_x_fcu, quat_y_fcu, quat_z_fcu, quat_w_fcu, keyframe):
	quat_x = 0.0
	quat_y = 0.0
	quat_z = 0.0
	quat_w = 0.0

	if quat_x_fcu:
		quat_x = quat_x_fcu.evaluate(keyframe)

	if quat_y_fcu:
		quat_y = quat_y_fcu.evaluate(keyframe)

	if quat_z_fcu:
		quat_z = quat_z_fcu.evaluate(keyframe)

	if quat_w_fcu:
		quat_w = quat_w_fcu.evaluate(keyframe)


	return mathutils.Quaternion([quat_x, quat_y, quat_z, quat_w])


def track_sort_key(track):
	return track.bone_index


def create_cal3d_animation(cal3d_skeleton, action, fps, xml_version):
	cal3d_animation = Animation(action.name, xml_version)

	initialized_borders = False
	last_keyframe = 0
	first_keyframe = 0

	for action_group in action.groups:
		cal3d_bone = None

		for bone in cal3d_skeleton.bones:
			if bone.name == action_group.name:
				cal3d_bone = bone
				break

		if not cal3d_bone:
			continue

		cal3d_track = Track(cal3d_bone.index)

		loc_x_fcu = get_action_group_fcurve(action_group, "location", 0)
		loc_y_fcu = get_action_group_fcurve(action_group, "location", 1)
		loc_z_fcu = get_action_group_fcurve(action_group, "location", 2)

		quat_x_fcu = get_action_group_fcurve(action_group, 
				                             "rotation_quaternion", 0)
		quat_y_fcu = get_action_group_fcurve(action_group,
				                             "rotation_quaternion", 1)
		quat_z_fcu = get_action_group_fcurve(action_group,
				                             "rotation_quaternion", 2)
		quat_w_fcu = get_action_group_fcurve(action_group,
				                             "rotation_quaternion", 3)

		keyframes_list = []

		keyframes_list.extend(get_keyframes_list(loc_x_fcu))
		keyframes_list.extend(get_keyframes_list(loc_y_fcu))
		keyframes_list.extend(get_keyframes_list(loc_z_fcu))

		keyframes_list.extend(get_keyframes_list(quat_x_fcu))
		keyframes_list.extend(get_keyframes_list(quat_y_fcu))
		keyframes_list.extend(get_keyframes_list(quat_z_fcu))
		keyframes_list.extend(get_keyframes_list(quat_w_fcu))

		# remove duplicates
		keyframes_set = set(keyframes_list)
		keyframes_list = list(keyframes_set)
		keyframes_list.sort()
		
		if len(keyframes_list) == 0:
			continue

		if initialized_borders:
			first_keyframe = min(keyframes_list[0], first_keyframe)
			last_keyframe = max(keyframes_list[len(keyframes_list) - 1], 
			                    last_keyframe)
		else:
			first_keyframe = keyframes_list[0]
			last_keyframe = keyframes_list[len(keyframes_list) - 1]
			initialized_borders = True

		cal3d_track.keyframes = []

		for keyframe in keyframes_list:
			dloc = evaluate_loc(loc_x_fcu, loc_y_fcu, loc_z_fcu, keyframe)
			dquat = evaluate_quat(quat_x_fcu, quat_y_fcu, 
			                      quat_z_fcu, quat_w_fcu, keyframe)

			quat = dquat.copy()
			quat.rotate(cal3d_bone.quat)
			quat.normalize()

			dloc.x *= cal3d_skeleton.anim_scale.x
			dloc.y *= cal3d_skeleton.anim_scale.y
			dloc.z *= cal3d_skeleton.anim_scale.z

			dloc.rotate(cal3d_bone.quat)
			loc = cal3d_bone.loc + dloc

			cal3d_keyframe = KeyFrame(keyframe, loc, quat)
			cal3d_track.keyframes.append(cal3d_keyframe)

		if len(cal3d_track.keyframes) > 0:
			cal3d_animation.tracks.append(cal3d_track)

	cal3d_animation.duration = ((last_keyframe - first_keyframe) / fps)
	cal3d_animation.tracks.sort(key=track_sort_key)

	for track in cal3d_animation.tracks:
		for keyframe in track.keyframes:
			keyframe.time = (keyframe.time - first_keyframe) / fps


	if len(cal3d_animation.tracks) > 0:
		return cal3d_animation

	return None

