# STILL WORK IN PROGRESS #
# I have no idea what the specs of ASF are. I tried to base myself off the code already present in export_asf, but it seems like i'm a total retard.
# Croteam, please help

import bpy
import re
from collections import OrderedDict
from mathutils import Vector, Matrix
from . import se3

def sanitize_name(name):
	return re.sub(r"\s*", "", name)

def gen_matrix(line):
	line = line.replace(";", "")
	tmp = re.sub(r"\s*", "", line).split(",")
	return [ float(x) for x in tmp ]

def se3_get_skeleton_from_file(operator, context):
	filepath = operator.filepath

	current_bone = ""

	bone_data = OrderedDict()

	is_in_limits = False
	is_in_pose = False

	with open(filepath, "r") as file:
		for line in file:
			if "SE_SKELETON" in line or "BONES" in line:
				continue

			if "NAME" in line:
				name = line
				name = name.replace('NAME ', "")
				name = name.replace('"', "")
				current_bone = sanitize_name(name)
				bone_data[current_bone] = {"name": current_bone, "parent": "", "root_bone": False, "matrix": [], "length": 0.0}

			if "PARENT" in line:
				parent = line
				parent = parent.replace('PARENT ', "")
				parent = parent.replace('"', "")
				parent = sanitize_name(parent)
				if parent is "":
					bone_data[current_bone]["root_bone"] = True
					continue
				else:
					bone_data[current_bone]["parent"] = parent

			if "LENGTH" in line:
				length = line
				length = length.replace("LENGTH ", "")
				length = length.replace('"', "")
				length = sanitize_name(length)
				bone_data[current_bone]["length"] = float(length)

			if "LIMITS" in line:
				is_in_limits = True
				continue

			if is_in_limits and "DEFAULT_POSE" not in line:
				continue

			if "DEFAULT_POSE" in line:
				is_in_limits = False
				is_in_pose = True
				continue

			if is_in_pose and "}" not in line:
				matrix = line
				bone_data[current_bone]["matrix"] = gen_matrix(matrix)

			if is_in_pose and "}" in line:
				is_in_pose = False
				continue

	armature_da = bpy.data.armatures.new("Armature")
	armature_ob = bpy.data.objects.new("Armature", armature_da)
	armature_ob.show_x_ray = True

	bpy.context.scene.objects.link(armature_ob)

	bpy.context.scene.objects.active = armature_ob
	bpy.ops.object.mode_set(mode='EDIT')

	ob = bpy.context.object

	for name, bone in bone_data.items():
		print(name)
		if bone["root_bone"]:
			m = Matrix()
			constraints = bone["matrix"]
			m[0][0:2] = -constraints[0], constraints[2], -constraints[1]
			m[1][0:2] = constraints[8], -constraints[10], constraints[9]
			m[2][0:2] = constraints[4], -constraints[6], constraints[5]

			v = Vector((-constraints[3], constraints[11], constraints[7]))
		else:
			m = Matrix()
			constraints = bone["matrix"]
			m[0][0:2] = constraints[0], -constraints[2], constraints[1]
			m[1][0:2] = -constraints[8], constraints[10], -constraints[9]
			m[2][0:2] = constraints[4], -constraints[6], constraints[5]

			v = Vector((constraints[3], -(constraints[11] - bone_data[bone["parent"]]["length"]), constraints[7]))

		edit_bone = armature_ob.data.edit_bones.new(bone["name"])
		edit_bone.matrix = m

		print(m.decompose())
		print(v)
		print("-------------------")

		edit_bone.head = v
		edit_bone.length = bone["length"]

		if not bone["root_bone"]:
			edit_bone.parent = armature_ob.data.edit_bones[bone["parent"]]

	return {"FINISHED"}

