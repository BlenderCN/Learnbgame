import re
import math
import bpy
from mathutils import Vector, Matrix, Quaternion

fmt_row2f = "( {:.6f} {:.6f} )"
fmt_row3f = "( {:.6f} {:.6f} {:.6f} )"

def construct(*args):
	return re.compile("\s*" + "\s+".join(args))

def unpack_tuple(mobj, start, end, conv=float, seq=Vector):
	return seq(conv(mobj.group(i)) for i in range(start, end + 1))

def gather(regex, end_regex, lines):
	return gather_multi([regex], end_regex, lines)[0]

def gather_multi(regexes, end_regex, lines):
	results = [[] for regex in regexes]

	for line in lines:
		if end_regex.match(line):
			break

		for regex, result in zip(regexes, results):
			mobj = regex.match(line)
			if mobj:
				result.append(mobj)
				break

	return results

def skip_until(regex, lines):
	for line in lines:
		if regex.match(line):
			return line
	# iterator exhausted
	return None

def restore_quat(rx, ry, rz):
	EPS = -5e-2
	t = 1.0 - rx*rx - ry*ry - rz*rz
	if EPS > t: 	   raise ValueError
	if EPS < t  < 0.0: return  Quaternion((          0.0, rx, ry, rz))
	else:			   return -Quaternion((-math.sqrt(t), rx, ry, rz))

def is_mesh_object(obj):
	return obj.type == "MESH"

def has_armature_modifier(obj, arm_obj):
	for modifier in obj.modifiers:
		if modifier.type == "ARMATURE":
			if modifier.object == arm_obj:
				return True
	return False

def process_match_objects(mobj_list, cls):
	for index, mobj in enumerate(mobj_list):
		mobj_list[index] = cls(mobj)

def get_name_to_index_dict(arm_obj):
	name_to_index = arm_obj.get("name_to_index")

	if name_to_index is not None:
		name_to_index = name_to_index.to_dict()

	else:
		name_to_index = {}
		root_bones = (pb for pb in arm_obj.pose.bones if pb.parent is None)
		index = 0

		for root_bone in root_bones:
			name_to_index[root_bone.name] = index
			index += 1
			for child in root_bone.children_recursive:
				name_to_index[child.name] = index
				index += 1

		arm_obj["name_to_index"] = name_to_index

	return name_to_index
