#!BPY
# -*- coding: UTF-8 -*-
# Utilities of F-Cureve
#
# 2018.07.22 Natukikazemizo

import bpy

def is_valid_layer(src_list, tgt_list):
	"""Check if there is a valid layer in both layers."""
	for i, val in enumerate(src_list):
		if val and tgt_list[i]:
			return True
	return False

def get_bone_list(armature, layer_list):
	"""Get Bone name List of selected layers"""
	ret = []
	for bone in armature.data.bones:
		if is_valid_layer(bone.layers, layer_list):
			ret.append(bone.name)
	return ret
