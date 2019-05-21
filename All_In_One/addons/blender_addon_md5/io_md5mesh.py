import bmesh
import logging
from .shared import * # for brevity use star import, also imports modules

logging.basicConfig(style="{", level=logging.WARNING)

#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------

class Vert:
	def __init__(self, mobj=None):
		if mobj is not None:
			self.from_mobj(mobj)
		else:
			self.index = -1
			self.uv = None
			self.fwi = -1
			self.nof_weights = 0
			self.bmv = None

	def from_mobj(self, mobj):
		self.index = int(mobj.group(1))
		self.uv = unpack_tuple(mobj, 2, 3)
		self.fwi = int(mobj.group(4)) # first weight index
		self.nof_weights  = int(mobj.group(5))
		self.bmv = None

		self.uv.y = 1.0 - self.uv.y

	def get_weights(self, weights):
		return weights[self.fwi: self.fwi + self.nof_weights]

	def calc_position(self, weights, matrices):
		return sum((matrices[weight.joint_index][1] * weight.offset * weight.value
					for weight in self.get_weights(weights)), Vector())

	def serialize(self, stream):
		self.uv.y = 1.0 - self.uv.y
		fmt = "\tvert {index:d} {uv:s} {fwi:d} {nof_weights:d}\n"

		stream.write(fmt.format(
			index = self.index,
			uv = fmt_row2f.format(*self.uv),
			fwi = self.fwi,
			nof_weights = self.nof_weights
		))


class Weight:
	def __init__(self, mobj=None):
		if mobj is not None:
			self.from_mobj(mobj)
		else:
			self.index = -1
			self.joint_index = -1
			self.value = 0.0
			self.offset = None

	def from_mobj(self, mobj):
		self.joint_index = int(mobj.group(2))
		self.value = float(mobj.group(3))
		self.offset = unpack_tuple(mobj, 4, 6)

	def serialize(self, stream):
		fmt = "\tweight {index:d} {joint_index:d} {value:.6f} {offset:s}\n"
		stream.write(fmt.format(
			index = self.index,
			joint_index = self.joint_index,
			value = self.value,
			offset = fmt_row3f.format(*self.offset)
		))


class Mesh:
	def __init__(self, mesh_obj):
		mesh = mesh_obj.data

		self.mesh_obj = mesh_obj
		self.weights = []
		self.shader = (mesh.materials[0].name if mesh.materials
					   else "")

		self.bm = bmesh.new()
		self.bm.from_mesh(mesh)
		self.process_for_export()
		self.bm.verts.index_update()
		self.tris = [[v.index for v in f.verts]
							  for f in self.bm.faces]
		nof_verts = len(self.bm.verts)

		self.verts = [Vert() for i in range(nof_verts)]

	def process_for_export(self):
		bm = self.bm

		def vec_equals(a, b):
			return (a - b).magnitude < 5e-2

		# split vertices with multiple uv coordinates
		seams = []
		tag_verts = set()
		layer_uv = bm.loops.layers.uv.active

		for edge in bm.edges:
			if not edge.is_manifold: continue

			uvs   = [None] * 2
			loops = [None] * 2

			loops[0] = list(edge.link_loops)
			loops[1] = [loop.link_loop_next for loop in loops[0]]

			for i in range(2):
				uvs[i] = list(map(lambda l: l[layer_uv].uv, loops[i]))

			results = (vec_equals(uvs[0][0], uvs[1][1]),
					   vec_equals(uvs[0][1], uvs[1][0]))

			if not all(results):
				if results[0]: tag_verts.add(loops[0][0].vert)
				if results[1]: tag_verts.add(loops[0][1].vert)
				seams.append(edge)

		tag_verts = list(tag_verts)
		bmesh.ops.split_edges(bm, edges=seams, verts=tag_verts, use_verts=True)

		# triangulate
		bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method=0, ngon_method=0)

		# flip normals
		bmesh.ops.reverse_faces(bm, faces=bm.faces[:], flip_multires=False)

	def set_weights(self, joints, lut):
		vertex_groups = self.mesh_obj.vertex_groups
		layer_deform = self.bm.verts.layers.deform.active
		layer_uv = self.bm.loops.layers.uv.active
		first_index = 0
		nof_weights = 0

		for v, bmv in zip(self.verts, self.bm.verts):
			v.index = bmv.index
			first_index = first_index + nof_weights
			nof_weights = 0
			weights = []

			for key, value in bmv[layer_deform].items():
				if value < 5e-4:
					logging.warning("Skipping weight with value %.2f of vertex %d" % (value, bmv.index))
					continue

				vertex_group = vertex_groups[key]
				joint_index = lut[vertex_group.name]

				weight = Weight()
				weight.index = first_index + nof_weights
				weight.joint_index = joint_index
				weight.value = value
				weights.append(weight)
				nof_weights += 1

			v.fwi = first_index
			v.nof_weights = nof_weights
			self.weights.extend(weights)

			# r = Σ mi wi ri, ensure Σ wi = 1.0 and choose mi^-1 r
			co = (1 / sum(weight.value for weight in weights)) * bmv.co

			for weight in weights:
				weight.offset = joints[weight.joint_index].mat_inv * co

		for face in self.bm.faces:
			for loop in face.loops:
				vert = self.verts[loop.vert.index]
				vert.uv = loop[layer_uv].uv

	def serialize(self, stream):
		stream.write("\nmesh {\n")
		stream.write("\t// meshes: %s\n"   % self.mesh_obj.name)
		stream.write("\n\tshader \"%s\"\n" % self.shader)
		stream.write("\n\tnumverts %d\n"   % len(self.verts))

		for vert in self.verts:
			vert.serialize(stream)

		stream.write("\n\tnumtris %d\n"    % len(self.tris))
		for index, tri in enumerate(self.tris):
			stream.write("\ttri {:d} {:d} {:d} {:d}\n".format(index, *tri))

		stream.write("\n\tnumweights %d\n" % len(self.weights))
		for weight in self.weights:
			weight.serialize(stream)

		stream.write("}\n")

	def finish(self):
		self.bm.free()
		self.verts = None
		self.weights = None
		self.tris = None

class Joint:
	def __init__(self):
		self.name   = ""
		self.index  = -1
		self.parent_index = -1
		self.parent_name = ""

		self.mat     = None
		self.mat_inv = None

		self.loc = None
		self.rot = None

	def serialize(self, stream):
		fmt = "\t\"{name:s}\"\t{pindex:d} {loc:s} {rot:s}\t\t// {pname:s}\n"
		stream.write(fmt.format(
			name   = self.name,
			pindex = self.parent_index,
			loc    = fmt_row3f.format(*self.loc),
			rot    = fmt_row3f.format(*self.rot[1:]),
			pname  = self.parent_name
		))

	def from_bone(self, bone, index, lut):
		self.name = bone.name
		self.index = lut[bone.name] = index
		self.parent_index = self.get_parent_index(bone, lut)
		self.parent_name = bone.parent.name if bone.parent is not None else ""
		self.mat = bone.matrix_local.copy()
		self.mat_inv = self.mat.inverted()
		self.loc, self.rot, scale = self.mat.decompose()
		self.rot *= -1.0

	@classmethod
	def get_parent_index(cls, bone, lut):
		if bone.parent is None: return -1
		return lut[bone.parent.name]

#-------------------------------------------------------------------------------
# Read md5mesh
#-------------------------------------------------------------------------------

def read_md5mesh(filepath):
	t_Int   = r"(-?\d+)"
	t_Float = r"(-?\d+\.\d+)"
	t_Word  = r"(\S+)"
	t_QuotedString = '"([^"]*)"' # does not allow escaping \"
	t_Tuple2f = "\\s+".join(("\\(", t_Float, t_Float, "\\)"))
	t_Tuple3f = "\\s+".join(("\\(", t_Float, t_Float, t_Float, "\\)"))

	re_joint  = construct(t_QuotedString, t_Int, t_Tuple3f, t_Tuple3f)
	re_vert   = construct("vert", t_Int, t_Tuple2f, t_Int, t_Int)
	re_tri    = construct("tri", t_Int, t_Int, t_Int, t_Int)
	re_weight = construct("weight", t_Int, t_Int, t_Float, t_Tuple3f)
	re_end    = construct("\\}")
	re_joints = construct("joints", "\\{")
	re_nverts = construct("numverts", t_Int)
	re_mesh   = construct("mesh", "\\{")
	re_shader = construct("shader", t_QuotedString)
	re_mesh_label = construct(".*?// meshes: (.*)$") # comment, used by sauerbraten

	with open(filepath, "r") as fobj:
		lines = iter(fobj.readlines())

	skip_until(re_joints, lines)

	arm_obj, matrices = do_joints(lines, re_joint, re_end)
	results = []
	reg_exprs = re_shader, re_vert, re_tri, re_weight, re_end, re_nverts, re_mesh_label
	n = 0

	while True:
		results.append(do_mesh(lines, reg_exprs, matrices))
		n += 1

		if skip_until(re_mesh, lines) is None:
			break

	for label, shader, bm in results:
		mesh = bpy.data.meshes.new(label)
		bm.to_mesh(mesh)
		bm.free()

		mesh.auto_smooth_angle = math.radians(45)
		mesh.use_auto_smooth = True

		mesh_obj = bpy.data.objects.new(label, mesh)
		for joint_name, mat in matrices:
			mesh_obj.vertex_groups.new(name=joint_name)

		mesh_obj.parent = arm_obj
		arm_mod = mesh_obj.modifiers.new(type='ARMATURE', name="MD5_skeleton")
		arm_mod.object = arm_obj
		arm_mod.use_deform_preserve_volume = True

		bpy.context.scene.objects.link(mesh_obj)

		mat_name = label
		mat = (bpy.data.materials.get(mat_name) or
			   bpy.data.materials.new(mat_name))
		mesh.materials.append(mat)

	return arm_obj

def do_joints(lines, re_joint, re_end):
	joints = gather(re_joint, re_end, lines)

	arm = bpy.data.armatures.new("MD5")
	arm_obj = bpy.data.objects.new("MD5", arm)
	arm_obj.select = True
	bpy.context.scene.objects.link(arm_obj)
	bpy.context.scene.objects.active = arm_obj

	matrices = []
	name_to_index = {}
	VEC_Y = Vector((0.0, 1.0, 0.0))
	VEC_Z = Vector((0.0, 0.0, 1.0))

	bpy.ops.object.mode_set(mode='EDIT')
	edit_bones = arm.edit_bones

	for index, mobj in enumerate(joints):
		name = mobj.group(1)
		parent = int(mobj.group(2))
		loc  = unpack_tuple(mobj, 3, 5)
		quat = unpack_tuple(mobj, 6, 8, seq=tuple)
		name_to_index[name] = index

		eb = edit_bones.new(name)
		if parent >= 0:
			eb.parent = edit_bones[parent]

		quat = restore_quat(*quat)
		mat = Matrix.Translation(loc) * quat.to_matrix().to_4x4()
		matrices.append((name, mat))

		eb.head = loc
		eb.tail = loc + quat * VEC_Y
		eb.align_roll(quat * VEC_Z)

	for eb in arm.edit_bones:
		if len(eb.children) == 1:
			child = eb.children[0]
			head_to_head = child.head - eb.head
			projection = head_to_head.project(eb.y_axis)
			if eb.y_axis.dot(projection) > 5e-2:
				eb.tail = eb.head + projection

	bpy.ops.object.mode_set()
	arm_obj['name_to_index'] = name_to_index
	return arm_obj, matrices

def do_mesh(lines, reg_exprs, matrices):
	(re_shader,
	 re_vert,
	 re_tri,
	 re_weight,
	 re_end,
	 re_nverts,
	 re_label) = reg_exprs

	mobjs__label, mobjs_shader = gather_multi([re_label, re_shader], re_nverts, lines)
	label  = mobjs__label[0].group(1) if len(mobjs__label) > 0 else "md5mesh"
	shader = mobjs_shader[0].group(1) if len(mobjs_shader) > 0 else ""

	verts, tris, weights = gather_multi(
		[re_vert, re_tri, re_weight],
		re_end,
		lines
	)

	bm = bmesh.new()
	process_match_objects(verts,   Vert)
	process_match_objects(weights, Weight)

	layer_weight = bm.verts.layers.deform.verify()
	layer_uv	 = bm.loops.layers.uv.verify()

	for index, vert in enumerate(verts):
		vert.bmv = bm.verts.new(vert.calc_position(weights, matrices))
		for weight in vert.get_weights(weights):
			vert.bmv[layer_weight][weight.joint_index] = weight.value

	for mobj_tri in tris:
		vertex_indices = unpack_tuple(mobj_tri, 2, 4, int, list)
		bm_verts = [verts[vertex_index].bmv for vertex_index in vertex_indices]
		# bm_verts.reverse() - use bmesh operator instead
		try:
			face = bm.faces.new(bm_verts)
		except ValueError: # some models contain duplicate faces
			continue
		face.smooth = True

	for vert in verts:
		for loop in vert.bmv.link_loops:
			loop[layer_uv].uv = vert.uv
			vert.bmv = None

	# flip normals
	bmesh.ops.reverse_faces(bm, faces=bm.faces[:], flip_multires=False)

	return label, shader, bm

#-------------------------------------------------------------------------------
# Write md5mesh
#-------------------------------------------------------------------------------

def on_active_layer(scene, obj):
	layers_scene = scene.layers
	layers_obj   = obj.layers

	for i in range(20):
		if layers_scene[i] and layers_obj[i]:
			return True
	return False

def write_md5mesh(filepath, scene, arm_obj):
	meshes = []

	for mesh_obj in filter(is_mesh_object, scene.objects):
		if (on_active_layer(scene, mesh_obj) and
			has_armature_modifier(mesh_obj, arm_obj)):
			meshes.append(Mesh(mesh_obj))

	bones = arm_obj.data.bones
	joints = [Joint() for i in range(len(bones))]
	name_to_index = get_name_to_index_dict(arm_obj)

	for bone in bones:
		index = name_to_index[bone.name]
		joints[index].from_bone(bone, index, name_to_index)

	for mesh in meshes:
		mesh.set_weights(joints, name_to_index)

	with open(filepath, "w") as stream:
		stream.write("MD5Version 10\n")
		stream.write("commandline \"\"\n\n")

		stream.write("numJoints %d\n" % len(joints))
		stream.write("numMeshes %d\n" % len(meshes))

		stream.write("\njoints {\n")
		for joint in joints:
			joint.serialize(stream)
		stream.write("}\n")

		for mesh in meshes:
			mesh.serialize(stream)
			mesh.finish()

#-------------------------------------------------------------------------------
# Test
#-------------------------------------------------------------------------------

def test():
	import os

	filepath = os.path.expanduser(
		"~/Downloads/Games/sauerbraten_2013"
		"/sauerbraten/packages/models"
		"/snoutx10k/snoutx10k.md5mesh")

	output = os.path.expanduser("~/Dokumente/Blender/Scripts/addons/md5/test.md5mesh")

	layer_source   = tuple(i == 0 for i in range(20))
	layer_reimport = tuple(i == 1 for i in range(20))

	scene = bpy.context.scene
	scene.layers = layer_source

	while bpy.data.objects:
		obj = bpy.data.objects[0]
		scene.objects.unlink(obj)
		obj.user_clear()
		bpy.data.objects.remove(obj)

	read_md5mesh(filepath)
	write_md5mesh(output, scene, bpy.context.active_object)

	scene.layers = layer_reimport
	read_md5mesh(output)
