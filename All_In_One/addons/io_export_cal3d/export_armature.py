import os
from math import *

import bpy
from mathutils import *

from . import armature_classes
from .armature_classes import *


def treat_bone(b, scale, parent, skeleton):
	# skip bones that start with _
	# also skips children of that bone so be careful
	if len(b.name) == 0 or  b.name[0] == '_':
		return

	name = b.name
	bone_matrix = b.matrix.copy()

	bone_head = b.head.copy()
	bone_tail = b.tail.copy()

	# if bones aren't connected, we need to create an 
	# extra bone for the animation correctness
	if bone_head.length != 0:
		head_bone_loc = bone_head * scale
		head_bone = Bone(skeleton, parent, name+"_head",
		                 head_bone_loc, Quaternion((1.0, 0.0, 0.0, 0.0)))
		parent = head_bone

	bone_trans = (bone_tail - bone_head) * scale
	bone_quat = bone_matrix.to_quaternion()

	bone = Bone(skeleton, parent, name, bone_trans, bone_quat)

	for child in b.children:
		treat_bone(child, scale, bone, skeleton)
	
	# This adds an extra bone to extremities; this is
	# purely a hack to make these bones show up in the Cal3D viewer 
	# for debugging.  These "leaf" bones otherwise have
	# no effect so they are not added by default.
	add_leaf_bones = True
	if len(b.children) == 0 and add_leaf_bones:
		tail = (b.tail - b.head) * scale
		bone = Bone(skeleton, bone, name + "_leaf",
		            Vector((0.0, 0.0, 0.0)),
		            Quaternion((1.0, 0.0, 0.0, 0.0)))


def create_cal3d_skeleton(arm_obj, arm_data,
						  base_rotation,
						  base_translation,
						  base_scale,
						  xml_version):

	base_matrix = Matrix.Scale(base_scale, 4)          * \
	              base_rotation.to_4x4()               * \
	              Matrix.Translation(base_translation) * \
	              arm_obj.matrix_world

	(total_translation, total_rotation, total_scale) = base_matrix.decompose()

	skeleton = Skeleton(arm_obj.name, total_scale, xml_version)

	service_root = Bone(skeleton, None, "_root",
	                    total_translation, 
	                    total_rotation)

	scalematrix = Matrix()
	scalematrix[0][0] = total_scale.x
	scalematrix[1][1] = total_scale.y
	scalematrix[2][2] = total_scale.z

	for bone in arm_data.bones.values():
		if not bone.parent and bone.name[0] != "_":
			treat_bone(bone, scalematrix, service_root, skeleton)

	return skeleton

