from itertools import chain
from .shared import * # for brevity use star import, also imports modules

def create_fcurves(action, data_path, dim, group=""):
	return tuple(action.fcurves.new(data_path, i, group) for i in range(dim))

def insert_keyframe(fcurves, time, values, interpolation="LINEAR"):
	for fcu, val in zip(fcurves, values):
		kf = fcu.keyframe_points.insert(time, val, {'FAST'})
		kf.interpolation = interpolation

def mat_offset(pose_bone):
	bone = pose_bone.bone
	mat = bone.matrix.to_4x4()
	mat.translation = bone.head
	if pose_bone.parent:
		mat.translation.y += bone.parent.length
	return mat

class JointInfo:
	fmt = "{: <20s} {:2d} {:6b} {:4d}"

	def __init__(self, mobj=None):
		if mobj is not None:
			self.from_mobj(mobj)
		else:
			self.name = ""
			self.parent = -1
			self.flags = 63
			self.start_index = -1

		self.pose_bone = None
		self.bf = None
		self.fcu_loc = None
		self.fcu_rot = None

		self.mat_offset = None
		self.mat_rest_inv = None
		self.mat_world = None

	def from_mobj(self, mobj):
		self.name 		 = mobj.group(1)
		self.parent 	 = int(mobj.group(2))
		self.flags  	 = int(mobj.group(3))
		self.start_index = int(mobj.group(4))

	def from_pose_bone(self, pose_bone):
		self.name = pose_bone.name
		self.pose_bone = pose_bone
		self.mat_offset = mat_offset(pose_bone)
		self.mat_rest_inv = pose_bone.bone.matrix_local.inverted()

	def update(self, frame, values):
		if self.pose_bone is None: return

		loc = self.bf.loc.copy()
		rot = self.bf.rot.copy()
		si = self.start_index
		j = 0

		for i in range(3):
			if self.flags & 1 << i:
				loc[i] = values[si + j]
				j += 1

		for i in range(3):
			if self.flags & 1 << (i + 3):
				rot[i] = values[si + j]
				j += 1

		rot = restore_quat(*rot)
		mat_basis = (Matrix.Translation(loc) *
					 rot.to_matrix().to_4x4())

		mat_basis = mat_offset(self.pose_bone).inverted() * mat_basis
		loc, rot, scale = mat_basis.decompose()

		insert_keyframe(self.fcu_loc, frame, loc)
		insert_keyframe(self.fcu_rot, frame, rot)

	def update_from_scene(self):
		self.mat_world = self.pose_bone.matrix.copy()

	def write_hierarchy_data(self, stream):
		fmt = "\t\"{name:s}\" {parent:d} {flags:d} {start_index:d}\n"
		stream.write(fmt.format(
			name = self.name,
			parent = self.parent,
			flags = self.flags,
			start_index = self.start_index
		))

	def write_baseframe(self, stream):
		fmt_row3f = "( {:.6f} {:.6f} {:.6f} )"
		fmt = "\t{loc:s} {rot:s}\n"

		mat = self.mat_offset * self.pose_bone.matrix_basis
		loc, rot, scale = mat.decompose()
		rot *= -1.0

		stream.write(fmt.format(
			loc = fmt_row3f.format(*loc),
			rot = fmt_row3f.format(*rot[1:])
		))

	def write_frame_data(self, stream):
		fmt = "\t{:.6f} {:.6f} {:.6f} {:.6f} {:.6f} {:.6f}\n"
		mat = self.mat_offset * self.pose_bone.matrix_basis
		loc, rot, scale = mat.decompose()
		rot *= -1.0
		arg = tuple(loc) + tuple(rot[1:])
		stream.write(fmt.format(*arg))

class BaseFrame:
	def __init__(self, mobj):
		self.loc = unpack_tuple(mobj, 1, 3)
		self.rot = unpack_tuple(mobj, 4, 6)

def read_md5anim(filepath):
	obj = bpy.context.active_object
	assert obj.type == "ARMATURE"

	if not obj.animation_data:
		obj.animation_data_create()

	action = bpy.data.actions.new("test")
	obj.animation_data.action = action
	pose_bones = obj.pose.bones
	data_path_loc = 'pose.bones["{:s}"].location'
	data_path_rot = 'pose.bones["{:s}"].rotation_quaternion'

	t_Int	= r"(-?\d+)"
	t_Float = r"(-?\d+\.\d+)"
	t_Word	= r"(\S+)"
	t_QuotedString = '"([^"]*)"' # does not allow escaping \"
	t_Tuple2f = "\\s+".join(("\\(", t_Float, t_Float, "\\)"))
	t_Tuple3f = "\\s+".join(("\\(", t_Float, t_Float, t_Float, "\\)"))

	re_end = construct("\\}")
	re_num_frames = construct("numFrames", t_Int)
	re_framerate = construct("frameRate", t_Int)
	re_num_components = construct("numAnimatedComponents", t_Int)
	re_hierarchy = construct("hierarchy", "\\{")
	re_joint = construct(t_QuotedString, t_Int, t_Int, t_Int)
	re_bounds = construct("bounds", "\\{")
	re_bbox = construct(t_Tuple3f, t_Tuple3f)
	re_baseframe = construct("baseframe", "\\{")
	re_bframe = construct(t_Tuple3f, t_Tuple3f)
	re_frame = construct("frame", t_Int, "\\{")
	re_float = construct(t_Float)
	re_endline = construct("\n")

	def read_floats(line):
		result = []
		pos = 0

		while True:
			if re_endline.match(line, pos):
				return result

			mobj = re_float.match(line, pos)
			if mobj is None:
				raise ValueError

			result.append(float(mobj.group(1)))
			pos += len(mobj.group(0))

	def to_int(x):
		return int(x[0].group(1))

	with open(filepath) as fobj: lines = iter(fobj.readlines())

	num_frames, framerate, num_components = gather_multi(
		[re_num_frames, re_framerate, re_num_components],
		re_hierarchy,
		lines
	)

	num_frames = to_int(num_frames)
	framerate  = to_int(framerate)
	num_components = to_int(num_components)

	joints  = gather(re_joint,  re_end, lines)
	skip_until(re_bounds, lines)
	bboxes  = gather(re_bbox,   re_end, lines)
	skip_until(re_baseframe, lines)
	bframes = gather(re_bframe, re_end, lines)

	process_match_objects(joints,  JointInfo)
	process_match_objects(bframes, BaseFrame)

	for joint, base_frame in zip(joints, bframes):
		joint.pose_bone = pose_bones.get(joint.name)
		if joint.pose_bone is None: return

		joint.is_valid = True
		joint.bf = base_frame

		joint.fcu_loc = create_fcurves(
			action, data_path_loc.format(joint.name), 3, joint.name)
		joint.fcu_rot = create_fcurves(
			action, data_path_rot.format(joint.name), 4, joint.name)

	frames = [[] for i in range(num_frames)]

	while True:
		line = skip_until(re_frame, lines)
		if line is None:
			break

		frame_index = int(re_frame.match(line).group(1))
		parameters = frames[frame_index]
		for line in lines:
			if re_end.match(line) is not None:
				break
			parameters.extend(read_floats(line))

	for fi in range(num_frames):
		for ji, joint in enumerate(joints):
			joint.update(fi, frames[fi])

	return action

#-------------------------------------------------------------------------------
# Write md5anim
#-------------------------------------------------------------------------------

def vec_cmp(vec, vec_other, func):
	return tuple(func(a, b) for a, b in zip(vec, vec_other))

def calc_bbox_from_object(mesh_objects):
	bbox_iter = (mesh_obj.bound_box for mesh_obj in mesh_objects)
	bbox_iter = chain.from_iterable(bbox_iter)
	bb_min = bb_max = next(bbox_iter)

	for vec in bbox_iter:
		bb_min = vec_cmp(bb_min, vec, min)
		bb_max = vec_cmp(bb_max, vec, max)

	return bb_min, bb_max

def get_parent_index(bone, lut):
	if bone.parent is None: return -1
	return lut[bone.parent.name]

def write_md5anim(filepath, scene, arm_obj, bone_layer, skip_bbox=False):
	mesh_objects = []
	for mesh_obj in filter(is_mesh_object, scene.objects):
		if has_armature_modifier(mesh_obj, arm_obj):
			mesh_objects.append(mesh_obj)

	action = arm_obj.animation_data.action
	frame_start, frame_end = tuple(map(int, action.frame_range))
	frame_count = frame_end - frame_start + 1

	pose_bones = [pb for pb in arm_obj.pose.bones if pb.bone.layers[bone_layer]]
	nof_joints = len(pose_bones)
	name_to_index = get_name_to_index_dict(arm_obj)
	joint_infos = [JointInfo() for i in range(nof_joints)]

	for pose_bone in pose_bones:
		index = name_to_index[pose_bone.name]
		joint_info = joint_infos[index]
		joint_info.from_pose_bone(pose_bone)
		joint_info.parent = get_parent_index(pose_bone, name_to_index)
		joint_info.start_index = index * 6

	filler = "\t( 0.000000 0.000000 0.000000 ) ( 0.000000 0.000000 0.000000 )\n"

	with open(filepath, "w") as stream:
		stream.write("MD5Version 10\n")
		stream.write("commandline \"\"\n\n")

		stream.write("numFrames %d\n" % frame_count)
		stream.write("numJoints %d\n" % nof_joints)
		stream.write("frameRate %d\n" % scene.render.fps)
		stream.write("numAnimatedComponents %d\n" % (6 * nof_joints))

		stream.write("\nhierarchy {\n")
		for joint_info in joint_infos:
			joint_info.write_hierarchy_data(stream)
		stream.write("}\n")

		stream.write("\nbounds {\n")
		for frame_index in range(frame_start, frame_end + 1):
			if skip_bbox:
				stream.write(filler)
				continue

			scene.frame_set(frame_index)
			bb_min, bb_max = calc_bbox_from_object(mesh_objects)
			stream.write("\t{bb_min:s} {bb_max:s}\n".format(
				bb_min=fmt_row3f.format(*bb_min),
				bb_max=fmt_row3f.format(*bb_max)))

		stream.write("}\n")

		stream.write("\nbaseframe {\n")
		scene.frame_set(frame_start)
		for joint_info in joint_infos:
			joint_info.write_baseframe(stream)
		stream.write("}\n")

		for frame_index in range(frame_start, frame_end + 1):
			stream.write("\nframe %d {\n" % frame_index)
			scene.frame_set(frame_index)
			for joint_info in joint_infos:
				joint_info.write_frame_data(stream)
			stream.write("}\n")

#-------------------------------------------------------------------------------
# Test
#-------------------------------------------------------------------------------

def test():
	import os

	filepath = os.path.expanduser(
		"~/Downloads/Games"
		"/sauerbraten_2013/sauerbraten/packages"
		"/models/mrfixit/swim.md5anim")

	output = os.path.expanduser("~/Dokumente/Blender/Scripts/addons/md5/test.md5anim")

	read_md5anim(filepath)

	scene = bpy.context.scene
	arm_obj = scene.objects.active
	write_md5anim(output, scene, arm_obj, 0)

	read_md5anim(output)
