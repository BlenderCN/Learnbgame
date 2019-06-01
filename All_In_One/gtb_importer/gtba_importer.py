# -*- coding: utf8 -*-
import os
import sys
import bmesh
import bpy
from . import six
import mathutils
import json
import zlib

def import_gtba(filepath, armature, rotation_resample):
	gtb = load_raw(filepath)

	bpy.ops.object.mode_set(mode='EDIT')
	
	bind_pose = calc_bind_pose_transforma(armature)
	bpy.ops.object.mode_set()
	
	for motion_name, motion in gtb["animations"].items():
		import_action(motion, armature, motion_name, bind_pose,
					  rotation_resample=rotation_resample)
		
	default_pose = gtb["pose"].get("default")
	if default_pose:
		apply_pose(armature, default_pose, bind_pose)
		
	return {'FINISHED'}

def load_raw(filepath):
	f = open(filepath, "rb")
	fourcc = f.read(4)
	if fourcc == b"GTBA":
		uz_bytes = zlib.decompress(f.read())
		uz_string = uz_bytes.decode("utf-8")
		gtb = json.loads(uz_string)
		f.close()
	else:
		f.close()
		f = open(filepath, "r")
		gtb = json.load(f)
		f.close()
	return gtb
		
def import_action(motion, armature, motion_name, bind_pose, rotation_resample=False):
	if motion_name in bpy.data.actions:
		action = bpy.data.actions[motion_name]
	else:	# adding
		action = bpy.data.actions.new(name=motion_name)
	# force Blender to save even if it has no users
	action.use_fake_user = True
	# a hint about which armature this action should be applied to
	action.target_user = armature.name	
	if armature.animation_data is None:
		armature.animation_data_create()
	armature.animation_data.action = action
	# This dictionary maps 'bone_id' to 'bone_name'.
	# In DMC4SE, bone_name is made up as "Bone" + str(bone_index), so 'bone_mapping' acts just
	# like a 'bone_id' to 'bone_index' mapping.
	#
	# When artists create an animation, a set of bones is used. When artists create a model,
	# another set of bones is used. If these two sets of bones match perfectly, you don't
	# have a problem of applying animations.
	# What if the two sets of bones don't match? Instead of fail to apply animations, you probably
	# want the animations to be 'partially applied'. For example, the animation is created for
	# a bone set with bones for extra addons, such as tail, cloak, etc, while the model uses
	# a skeletal without those bones, you might want that the animation for the body part can
	# be applied correctly. So, there must be a way to tell which bone matches which. That's why
	# a unique 'bone_id' is used, it makes sharing animations between models much easier.
	#
	bone_mapping = armature["bone_mapping"]
	pose_bones = armature.pose.bones
	for bone_id, v in motion.items():
		loc, rot, scale = v
		bone_name = bone_mapping.get(bone_id)
		if bone_name is None:
			continue
		pose_bone = pose_bones[bone_name]
		# location keyframes
		if loc is None:
			pose_bone.location = mathutils.Vector([0, 0, 0])
			pose_bone.keyframe_insert("location", index=-1, frame=1)
		else:
			for loc_k in loc:
				f = loc_k[0] + 1
				pose_bone.location = mathutils.Vector(loc_k[1:4])
				pose_bone.location -= bind_pose[bone_name][0]
				pose_bone.keyframe_insert("location", index=-1, frame=f)
		# rotation keyframes
		if rot is None:
			pose_bone.rotation_quaternion = mathutils.Quaternion([1, 0, 0, 0])
			pose_bone.keyframe_insert("rotation_quaternion", index=-1, frame=1)
		else:
			prev_f = 1
			for rot_k in rot:
				f = rot_k[0] + 1
				# In blender, quaternion is stored in order of w, x, y, z
				q = mathutils.Quaternion(
					[rot_k[4], rot_k[1], rot_k[2], rot_k[3]]
				)
				q = bind_pose[bone_name][1].inverted() * q
				if f - prev_f > 1 and rotation_resample:
					prev_q = mathutils.Quaternion(pose_bone.rotation_quaternion)
					step = 1.0 / (f - prev_f)
					fraction = 0.0
					for i in range(f - prev_f):
						fraction += step
						_q = prev_q.slerp(q, fraction)
						pose_bone.rotation_quaternion = _q
						pose_bone.keyframe_insert("rotation_quaternion", index=-1, frame=prev_f + i + 1)
				else:
					pose_bone.rotation_quaternion = q
					pose_bone.keyframe_insert("rotation_quaternion", index=-1, frame=f)
				prev_f = f
		# scale keyframes
		if scale is None:
			pose_bone.scale = mathutils.Vector([1, 1, 1])
			pose_bone.keyframe_insert("scale", index=-1, frame=1)
		else:
			for scale_k in scale:
				f = scale_k[0] + 1
				pose_bone.scale = mathutils.Vector(scale_k[1:4])
				pose_bone.scale.x /= bind_pose[bone_name][2].x
				pose_bone.scale.y /= bind_pose[bone_name][2].y
				pose_bone.scale.z /= bind_pose[bone_name][2].z								
				pose_bone.keyframe_insert("scale", index=-1, frame=f)
	# force linear interpolation now
	for fcurve in action.fcurves:
		for keyframe_point in fcurve.keyframe_points:
			keyframe_point.interpolation = 'LINEAR'

def apply_pose(armature, pose, bind_pose):
	bone_mapping = armature["bone_mapping"]
	pose_bones = armature.pose.bones
	for bone_id, (loc, rot, scale) in pose.items():
		bone_name = bone_mapping.get(bone_id)
		if bone_name is None:
			continue
		pose_bone = pose_bones[bone_name]
		if loc is not None:
			pose_bone.location = mathutils.Vector(loc[:3])
			pose_bone.location -= bind_pose[bone_name][0]
		else:
			pose_bone.location = mathutils.Vector([0, 0, 0])
		if rot is not None:
			# In blender, quaternion is stored in order of w, x, y, z
			pose_bone.rotation_quaternion = mathutils.Quaternion(
				[rot[3], rot[0], rot[1], rot[2]]
			)
			# to relative rotation
			pose_bone.rotation_quaternion = bind_pose[bone_name][1].inverted() * pose_bone.rotation_quaternion
		else:
			pose_bone.rotation_quaternion = mathutils.Quaternion([1, 0, 0, 0])
		
		if scale is not None:
			pose_bone.scale = mathutils.Vector(scale[:3])
			# to relative scale
			pose_bone.scale.x /= bind_pose[bone_name][2].x
			pose_bone.scale.y /= bind_pose[bone_name][2].y
			pose_bone.scale.z /= bind_pose[bone_name][2].z
		else:
			pose_bone.scale = mathutils.Vector([1, 1, 1])

def calc_bind_pose_transforma(armature):
	m = mathutils.Matrix()
	m[0].xyzw = 1, 0, 0, 0
	m[1].xyzw = 0, 0, 1, 0
	m[2].xyzw = 0,-1, 0, 0
	m[3].xyzw = 0, 0, 0, 1
	
	bind_pose = {}
	for bone in armature.data.edit_bones:
		if bone.parent is None:
			loc_mat = m * bone.matrix
		else:
			loc_mat = (m * bone.parent.matrix).inverted() * (m * bone.matrix)
		loc, rot, scale = loc_mat.decompose()
		bind_pose[bone.name] = (loc, rot, scale)
	return bind_pose