# ##### BEGIN LICENSE BLOCK #####
#
# Royalty Free License
#
# The Royalty Free license grants you, the purchaser, the ability to make use of the purchased
# product for personal, educational, or commercial purposes as long as those purposes do not
# violate any of the following:
#
#   You may not resell, redistribute, or repackage the purchased product without explicit
#   permission from the original author
#
#   You may not use the purchased product in a logo, watermark, or trademark of any kind
#
#   Exception: shader, material, and texture products are exempt from this rule. These products
#   are much the same as colors, and such are a secondary meaning and may be used as part of a
#   logo, watermark, or trademark.
#
# ##### END LICENSE BLOCK #####

bl_info = {
	'name': 'Cuber',
	'author': 'Ian Lloyd Dela Cruz',
	'version': (2, 32),
	'blender': (2, 80, 0),
	'location': '3d View > Tool shelf',
	'description': 'Draw based boolean cutter and extends edit mode intersect functions',
	'warning': '',
	'wiki_url': '',
	'tracker_url': '',
	'category': 'Mesh'}

import bpy
import blf
import gpu
from gpu_extras.batch import batch_for_shader
import numpy as np
import bmesh
import math
from math import *
import mathutils
from mathutils import *
from mathutils.geometry import intersect_line_plane
from bpy.props import *
from bpy_extras import view3d_utils
from bpy.types import (
		AddonPreferences,
		Operator,
		Menu,
		Panel,
		)

def auto_smooth(context, ob, deg, set):

	ob.data.use_auto_smooth = set
	ob.data.auto_smooth_angle = deg

	mesh = ob.data
	if mesh.is_editmode:
		bm = bmesh.from_edit_mesh(mesh)
	else:
		bm = bmesh.new()
		bm.from_mesh(mesh)

	for f in bm.faces:
		f.smooth = True if set else False

	if mesh.is_editmode:
		bmesh.update_edit_mesh(mesh)
	else:
		bm.to_mesh(mesh)
		mesh.update()

def isolate_vgroup(context, ob, vg_name):

	mesh = ob.data
	cg = ob.vertex_groups[vg_name].index

	bm = bmesh.from_edit_mesh(mesh)

	geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
	for p in geom: p.select = False

	deform_layer = bm.verts.layers.deform.active
	if deform_layer is None: deform_layer = bm.verts.layers.deform.new()

	vgroup = [v for v in bm.verts if cg in v[deform_layer]]
	for v in vgroup:
		linked = v.link_faces
		for f in linked:
			f.select = True

	bmesh.update_edit_mesh(mesh)

	return vgroup

def show_faces(context, select_faces):

	ob = context.active_object
	mesh = ob.data

	bm = bmesh.from_edit_mesh(mesh)

	geom = bm.verts[:] + bm.edges[:] + bm.faces[:]

	for p in geom:
		p.hide = False
		p.select = True if select_faces else False

	bmesh.update_edit_mesh(mesh)

def rem_vgroup(context, ob, vgroup):

	mode_set = bpy.ops.object.mode_set
	old_mode = ob.mode

	mode_set(mode='OBJECT')

	cg = ob.vertex_groups[vgroup].index
	ob.vertex_groups.active_index = cg
	vg = ob.vertex_groups.active

	verts = []
	for vert in ob.data.vertices:
		if vert.select:
			verts.append(vert.index)
			vg.remove(verts)

	mode_set(mode=old_mode)

def add_cuber_vgroup(context):

	ob = context.active_object
	vg_name = "Intersect Faces"

	try:
		group_index = ob.vertex_groups[vg_name].index
	except:
		group = ob.vertex_groups.new(name=vg_name)
		group_index = group.index

	mesh = ob.data
	bm = bmesh.from_edit_mesh(mesh)

	deform_layer = bm.verts.layers.deform.active
	if deform_layer is None: deform_layer = bm.verts.layers.deform.new()

	for f in bm.faces:
		if f.select:
			for v in f.verts:
					v[deform_layer][group_index] = 1.0

	bmesh.update_edit_mesh(mesh)

def face_mat(ob, index):

	mesh = ob.data

	if mesh.is_editmode:
		bm = bmesh.from_edit_mesh(mesh)

		f_sel = [f for f in bm.faces if f.select]
		for f in f_sel: f.material_index = index

		bmesh.update_edit_mesh(mesh)
	else:
		bm = bmesh.new()
		bm.from_mesh(mesh)

		for f in bm.faces:
			f.material_index = index

		bm.to_mesh(mesh)
		mesh.update()

def add_mat(context, ob, mat_nam):

	ob_mats = ob.data.materials

	if not ob_mats:
		mat = bpy.data.materials.new(name=mat_nam)
		ob_mats.append(mat)

	mat = bpy.data.materials.new(name=mat_nam)
	ob_mats.append(mat)

	index = ob_mats.find(mat.name)
	face_mat(ob, index)
	rem_mat(context, ob)

	new_idx = ob_mats.find(mat.name)
	ob.active_material_index = new_idx

def rem_mat(context, ob):

	mesh = ob.data

	mode_set = bpy.ops.object.mode_set
	old_mode = ob.mode

	if mesh.is_editmode:
		bpy.ops.object.editmode_toggle()

	mat_slots = {}
	for f in mesh.polygons:
		mat_slots[f.material_index] = 1

	mat_slots = mat_slots.keys()
	bool_mats = []

	for mod in ob.modifiers:
		if mod.type == "BOOLEAN" and mod.object != None:
			for mat in mod.object.data.materials: bool_mats.append(mat)

	for i in reversed(range(len(ob.material_slots))):
		if i not in mat_slots:
			ob.active_material_index = i
			if i not in bool_mats:
				bpy.ops.object.material_slot_remove()

	mode_set(mode=old_mode)

def duplicate_obj(scene, name, copy_obj):

	ob_type = copy_obj.type

	if ob_type == "MESH":
		data_obj = bpy.data.meshes.new(name)
	elif ob_type == "CURVE":
		data_obj = bpy.data.curves.new(name, "CURVE")

	ob_new = bpy.data.objects.new(name, data_obj)

	ob_new.data = copy_obj.data.copy()
	ob_new.scale = copy_obj.scale
	ob_new.rotation_euler = copy_obj.rotation_euler
	ob_new.location = copy_obj.location

	if ob_type == "MESH":
		group_copy = copy_obj.vertex_groups
		if len(group_copy):
			for group in group_copy:
				ob_new.vertex_groups.new(name=group.name)

	scene.collection.objects.link(ob_new)
	ob_new.select_set(True)

	return ob_new

def remove_obj(scene, ob):

	in_master = True
	for c in bpy.data.collections:
		if ob.name in c.objects:
			c.objects.unlink(ob)
			in_master = False
			break

	if in_master:
		if ob.name in scene.collection.objects:
			scene.collection.objects.unlink(ob)

	bpy.data.objects.remove(ob)

def copy_mod(objs):

	orig_ob = objs[0]
	selected_objects = [o for o in objs
						if o != orig_ob and o.type == orig_ob.type]

	for obj in selected_objects:
		for mSrc in orig_ob.modifiers:
			mDst = obj.modifiers.get(mSrc.name, None)
			if not mDst:
				mDst = obj.modifiers.new(mSrc.name, mSrc.type)

			properties = [p.identifier for p in mSrc.bl_rna.properties
						  if not p.is_readonly]

			for prop in properties:
				setattr(mDst, prop, getattr(mSrc, prop))

def normalize_scale(context, ob):

	mode_set = bpy.ops.object.mode_set
	old_mode = ob.mode

	mat_world = ob.matrix_world
	w = Vector((1,1,1))

	mat = Matrix()
	scale = mat_world.to_scale()
	if mat_world.is_negative:
		scale = scale * -1
	if scale != w:
		mode_set(mode='OBJECT')
		mat[0][0], mat[1][1], mat[2][2] = scale
		ob.data.transform(mat)
		ob.matrix_world = ob.matrix_world.normalized()
		mode_set(mode=old_mode)

def add_bevel(self,
			context,
			use_angle,
			deg,
			width,
			segments,
			profile,
			clamp,
			slide,
			harden_normals,
			offset_type,
			face_strength_mode,
			push,
			clear):

	ob = context.active_object
	mod = ob.modifiers
	cm = ['Bevel', 'Weighted Normal']

	normalize_scale(context, ob)

	if not mod.get(cm[0]):
		if clear:
			for m in mod:
				if m.type == 'BEVEL': mod.remove(m)

		md = ob.modifiers.new(cm[0], "BEVEL")
		md.show_expanded = False
		md.show_in_editmode = False

	c_bvl = ob.modifiers[cm[0]]
	c_bvl.width = width
	c_bvl.segments = segments
	c_bvl.profile = profile
	c_bvl.use_clamp_overlap = clamp
	c_bvl.loop_slide = slide
	c_bvl.harden_normals = harden_normals
	c_bvl.offset_type = offset_type
	c_bvl.face_strength_mode = face_strength_mode

	if use_angle:
		c_bvl.limit_method = 'ANGLE'
		c_bvl.angle_limit = deg
	else:
		c_bvl.limit_method = 'WEIGHT'

	cm_down_stack(cm, mod, push)

def cm_down_stack(cm, mod, push):

	tm = len(mod[:-1])
	if push:
		if mod.get(cm[1]):
			while mod.find(cm[1]) != tm:
				bpy.ops.object.modifier_move_down(modifier=cm[1])
			tm -= 1

		while mod.find(cm[0]) != tm:
			bpy.ops.object.modifier_move_down(modifier=cm[0])

def sync_bevel_settings(context, ob, mod_nam):

	mod = ob.modifiers
	props = context.scene.BevelPG

	c_bvl = mod.get(mod_nam)
	if c_bvl:
		props.use_bevel = False

		props.width = c_bvl.width
		props.segments = c_bvl.segments
		props.profile = c_bvl.profile
		props.use_clamp = c_bvl.use_clamp_overlap
		props.use_slide = c_bvl.loop_slide
		props.harden_normals = c_bvl.harden_normals
		props.offset_type = c_bvl.offset_type
		props.face_strength_mode = c_bvl.face_strength_mode

		if c_bvl.limit_method == "ANGLE":
			props.use_angle = True
			props.bevel_deg = c_bvl.angle_limit
		else:
			props.use_angle = False

	if not props.use_bevel: props.use_bevel = True

def read_bevel(context, bm, bevel_layer):

	sce = context.scene
	ob = context.active_object

	sce.obj_read = ob.name
	bvl_weights = []

	for e in bm.edges:
		if e[bevel_layer]:
			bvl_weights.append(e[bevel_layer])

	unique_bweights = list(set(bvl_weights))
	sce.bweightList.clear()
	for i in sorted(unique_bweights):
		newCustomItem = sce.bweightList.add()
		newCustomItem.bevelweightsList = str(i)

def update_lock_list(context, newItem, obdata, noUserList, mode):

	sce = context.scene

	count = 0
	dup_count = 0

	for i in sce.bweightlockList:
		if mode == "Add":
			if i.obdataList == newItem:
				dup_count += 1
				if dup_count > 1:
					sce.bweightlockList.remove(count)
		elif mode == "Remove":
				if i.obdataList == obdata:
					sce.bweightlockList.remove(count)
		elif mode == "Clean":
				if i.obdataList in noUserList:
					sce.bweightlockList.remove(count)
		count += 1

class MESH_OT_fcol_to_vcol(Operator):
	'''Use material color as vertex color'''
	bl_idname = 'bake_vcol.cuber'
	bl_label = 'Material Color To Vertex Color'
	bl_options = {'REGISTER', 'UNDO'}

	brightness : bpy.props.FloatProperty(
		description = "Vertex Color Brightness",
		name        = "Brightness",
		default     = 0,
		min         = 0.0,
		max         = 1.0,
		step        = 0.1,
		precision   = 2
		)

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == 'OBJECT'

	def execute(self, context):
		vc_idx = "Material Color"

		for obs in context.selected_objects:
			if obs.type == 'MESH':
				mesh = obs.data
				vcol = mesh.vertex_colors

				index = 0
				for m in obs.data.materials:
					obs.active_material_index = index

					if not vc_idx in vcol:
						fcol = vcol.new()
						fcol.name = vc_idx

					vcol.active = vcol[vc_idx]
					color_layer = vcol.active

					i = 0
					for f in mesh.polygons:
						face_idx = f.material_index == index
						for idx in f.loop_indices:
							if face_idx:
								rgb = obs.active_material.diffuse_color
								channel = 0
								for col in rgb:
									color_layer.data[i].color[channel] = col + self.brightness
									channel += 1
							i += 1
					index += 1

		return {'FINISHED'}

	def draw(self, context):
		 layout = self.layout
		 layout.prop(self, "brightness")

class MESH_OT_auto_smooth(Operator):
	'''Auto smooth faces'''
	bl_idname = 'auto_smooth.cuber'
	bl_label = 'Auto Smooth Faces'
	bl_options = {'REGISTER', 'UNDO'}

	set_auto_smooth : BoolProperty(
		name        = "Use Auto Smooth",
		description = "Toggle auto smooth on or off",
		default     = True
		)
	deg : FloatProperty(
		name        = "Angle",
		description = "Auto smooth angle",
		default     = radians(30),
		min         = 0,
		max         = radians(180),
		step        = 10,
		precision   = 3,
		subtype     = "ANGLE"
		)

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == "EDIT"

	def execute(self, context):
		ob = context.active_object

		auto_smooth(context, ob, self.deg, self.set_auto_smooth)
		ob.data.update()

		return {'FINISHED'}

	def draw(self, context):
		layout = self.layout
		layout.prop(self, "deg")
		layout.prop(self, "set_auto_smooth")

class MESH_OT_add_face_mat(Operator):
	'''Assign new material to selected faces or object'''
	bl_idname = 'add_mat.cuber'
	bl_label = 'Assign Material'
	bl_options = {'REGISTER', 'UNDO'}

	mat_nam : StringProperty(
		name        = "Name",
		description = "Material name",
		default     = "Cuber Material"
		)

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		ob = context.active_object
		mesh = ob.data

		if ob.type == "MESH":
			add_mat(context, ob, self.mat_nam)

		if ob.type == "CURVE":
			mat = bpy.data.materials.new(name=self.mat_nam)
			mesh.materials.clear()
			mesh.materials.append(mat)

		return {'FINISHED'}

	def draw(self, context):
		layout = self.layout
		layout.prop(self, "mat_nam")

class MESH_OT_add_vcol_mat(Operator):
	'''Use vertex color in material shader'''
	bl_idname = 'vcol_mat.cuber'
	bl_label = 'Assign Material'
	bl_options = {'REGISTER', 'UNDO'}

	mat_nam : StringProperty(
		name        = "Name",
		description = "Material name",
		default     = "Cuber Material"
		)

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == 'OBJECT'

	def att_node(self, sce, mat_nt, vc_idx):

		bsdf = mat_nt.nodes.get("Principled BSDF")
		attr = mat_nt.nodes.new('ShaderNodeAttribute')
		attr.attribute_name = vc_idx

		mat_nt.links.new(attr.outputs[0], bsdf.inputs[0])

		space = 0
		for node in reversed(mat_nt.nodes):
			node.location.x = space
			space += node.width + 50
			node.location.y = 0

	def execute(self, context):
		sce = context.scene
		vc_idx = "Material Color"

		mat = bpy.data.materials.new(name=self.mat_nam)
		mat.use_nodes = True
		self.att_node(sce, mat.node_tree, vc_idx)

		for obs in context.selected_objects:
			if obs.type == 'MESH':
				mesh = obs.data
				vcol = mesh.vertex_colors

				if vc_idx in vcol:
					obs.data.materials.clear()
					obs.data.materials.append(mat)

		return {'FINISHED'}

	def draw(self, context):
		layout = self.layout
		layout.prop(self, "mat_nam")

class MESH_OT_isolate_intersect_faces(Operator):
	'''Isolate intersect faces'''
	bl_idname = 'isolate_vgroup.cuber'
	bl_label = 'Isolate Intersect Faces'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == 'EDIT'

	def execute(self, context):
		ob = context.active_object
		vg_name = "Intersect Faces"

		mesh = ob.data
		bm = bmesh.from_edit_mesh(mesh)

		view_toggle = False
		for f in bm.faces:
			if f.hide:
				f.hide = False
				view_toggle = True

		if not view_toggle and vg_name in ob.vertex_groups:
			isolate_vgroup(context, ob, vg_name)
			for f in bm.faces:
				if not f.select: f.hide = True

		bmesh.update_edit_mesh(mesh)

		return {'FINISHED'}

class MESH_OT_highlight_intersect_faces(Operator):
	'''Select intersect faces'''
	bl_idname = 'select_vgroup.cuber'
	bl_label = 'Highlight Intersect Faces'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == 'EDIT'

	def execute(self, context):
		ob = context.active_object
		vg_name = "Intersect Faces"

		if vg_name in ob.vertex_groups:
			isolate_vgroup(context, ob, vg_name)

		return {'FINISHED'}

class MESH_OT_cuber_symm(Operator):
	'''Symmetrize intersect faces or entire mesh'''
	bl_idname = 'cuber_symm.cuber'
	bl_label = 'Symmetrize'
	bl_options = {'REGISTER', 'UNDO'}

	use_axis_x : BoolProperty(
		name 		= 'X',
		default		= True
		)
	use_axis_y : BoolProperty(
		name 		= 'Y',
		default		= False
		)
	use_axis_z : BoolProperty(
		name 		= 'Z',
		default		= False
		)
	mirror_cg : BoolProperty(
		name 		= 'Mirror Intersect Faces',
		default		= False
		)

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def view_axis(self, context, ob):

		sce = context.scene
		region = context.region
		rv3d = context.region_data

		coord = region.width / 2, region.height / 2

		view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
		ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

		ray_target = ray_origin + view_vector

		def scene_ray_cast(matrix):

			matrix_inv = matrix.inverted()
			ray_origin_ob = matrix_inv @ ray_origin
			ray_target_ob = matrix_inv @ ray_target
			ray_direction_ob = ray_target_ob - ray_origin_ob

			hit, pos, normal, face_index, ob, matrix_world = sce.ray_cast(context.view_layer, ray_origin_ob, ray_direction_ob)

			if hit:
				return pos, normal, face_index
			else:
				return None, None, None

		matrix = ob.matrix_parent_inverse.copy()
		pos, normal, face_index = scene_ray_cast(matrix)
		if pos:
			hit_world = matrix @ pos
		else: hit_world = None

		return hit_world

	def get_vg(self, bm, ob, vg_name):

		vrt = []
		edg = []
		fce = []

		if vg_name in ob.vertex_groups:
			cg = ob.vertex_groups[vg_name].index

			deform_layer = bm.verts.layers.deform.active
			if deform_layer is None: deform_layer = bm.verts.layers.deform.new()

			vrt = [v for v in bm.verts if cg in v[deform_layer]]
			for v in vrt:
				for f in v.link_faces:
					fce.append(f)
				for e in v.link_edges:
					edg.append(e)

			edg = list(dict.fromkeys(edg))
			fce = list(dict.fromkeys(fce))

		if not vrt:
			self.report({'INFO'}, "No intersect faces present.")

		return vrt, edg, fce

	def execute(self, context):
		sce = context.scene
		ob = context.active_object
		vg_name = "Intersect Faces"

		mesh = ob.data
		if mesh.is_editmode:
			bm = bmesh.from_edit_mesh(mesh)
		else:
			bm = bmesh.new()
			bm.from_mesh(mesh)

		act_sel = bm.select_history.active
		if act_sel:
			act_v = [v for v in act_sel.verts] if hasattr(act_sel, 'verts') else [act_sel]
			avg_loc = sum([v.co for v in act_v], Vector()) / len(act_v)

			if self.info:
				self.report({'INFO'}, "Symmetrize by active selection axis.")
				self.info = False
		else:
			hit = self.view_axis(context, ob)
			avg_loc = (ob.matrix_world.inverted() @ hit) if hit else None

			if self.info:
				self.report({'INFO'}, "Symmetrize by view axis.")
				self.info = False

		if avg_loc:
			centr = ob.matrix_parent_inverse.translation

			px = (1,0,0) if avg_loc.x > centr.x else (-1,0,0)
			py = (0,1,0) if avg_loc.y > centr.y else (0,-1,0)
			pz = (0,0,1) if avg_loc.z > centr.z else (0,0,-1)

			pn = [px if self.use_axis_x else None, py if self.use_axis_y else None,
				pz if self.use_axis_z else None]

			for n in pn:
				if n:
					if self.mirror_cg:
						v, e, f = self.get_vg(bm, ob, vg_name)
						mid_p = v[:] + e[:] + f[:]
					else:
						mid_p = bm.verts[:] + bm.edges[:] + bm.faces[:]

					ret = bmesh.ops.bisect_plane(
						bm,
						geom		= mid_p,
						dist		= 0.00001,
						plane_co	= centr,
						plane_no	= n,
						clear_inner	= True,
						clear_outer	= False
						)

					if n in [(1,0,0),(-1,0,0)]: x = 'X'
					elif n in [(0,1,0),(0,-1,0)]: x = 'Y'
					elif n in [(0,0,1),(0,0,-1)]: x = 'Z'

					bmesh.ops.mirror(
						bm,
						geom		= ret['geom'],
						matrix		= Matrix.Translation(centr),
						merge_dist 	= -1,
						axis		= x
						)

					mid_v = [v for v in ret['geom_cut'] if isinstance(v, bmesh.types.BMVert)]
					bmesh.ops.automerge(bm, verts=mid_v, dist=0.00001)

					bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

		if mesh.is_editmode:
			bmesh.update_edit_mesh(mesh)
		else:
			bm.to_mesh(mesh)
			mesh.update()

		return {'FINISHED'}

	def invoke(self, context, event):
		self.info = True

		return self.execute(context)

	def draw(self, context):
		layout = self.layout
		col = layout.column(align=True)
		col.prop(self, "use_axis_x")
		col.prop(self, "use_axis_y")
		col.prop(self, "use_axis_z")
		col.prop(self, "mirror_cg")

class MESH_OT_bool_intersect_faces(Operator):
	'''Boolean and knife operation for intersect faces'''
	bl_idname = 'bool_intrsct_faces.cuber'
	bl_label = 'Boolean/Cut Intersect Faces'
	bl_options = {'REGISTER', 'UNDO'}

	this_op : StringProperty("")

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == 'EDIT'

	def mark_sharp(self, context, ob, edges):

		if context.scene.auto_sharp:
			for e in edges:
				angle = e.calc_face_angle(None)
				if (angle != None and
					angle > bpy.context.scene.angle_sharp): e.smooth = False

	def execute(self, context):
		ob = context.active_object
		mesh_op = bpy.ops.mesh
		vg_name = "Intersect Faces"

		add_cuber_vgroup(context)
		show_faces(context, False)

		cg = ob.vertex_groups[vg_name].index
		ob.vertex_groups.active_index = cg
		isolate_vgroup(context, ob, vg_name)

		mesh = ob.data
		bm = bmesh.from_edit_mesh(mesh)

		e_sharp = True

		if self.this_op == "CUT":
			mesh_op.intersect()

			isolate_vgroup(context, ob, vg_name)
			remv = [v for v in bm.verts if v.select]
			bmesh.ops.delete(bm, geom=remv, context='VERTS')

			e_sharp = False

		elif self.this_op == "INTERSECT":
			fcount = [f for f in bm.faces if f.select]
			if fcount:
				ret = bmesh.ops.duplicate(
					bm,
					geom = bm.faces[:]
					)

				for f in ret["geom"]: f.hide = True
				mesh_op.intersect_boolean(operation='INTERSECT')

				self.mark_sharp(context, ob, bm.edges)
				for f in bm.faces: f.select = True
				mesh_op.separate()

				for sel in context.selected_objects:
					if sel != ob:
						this_obj = bpy.data.objects[sel.name]
						this_obj.vertex_groups.remove(sel.vertex_groups[vg_name])
						this_obj.select_set(False)

				for f in ret["geom"]: f.hide = False
				isolate_vgroup(context, ob, vg_name)

				mesh_op.intersect_boolean(operation='DIFFERENCE')
		else:
			mesh_op.intersect_boolean(operation=self.this_op)

		for f in bm.faces: f.select = False
		if e_sharp: self.mark_sharp(context, ob, bm.edges)

		bmesh.update_edit_mesh(mesh, True, True)

		ob.vertex_groups.remove(ob.vertex_groups[vg_name])
		ob.vertex_groups.new(name=vg_name)

		return {'FINISHED'}

	def draw(self, context): None

class MESH_OT_add_intersect_faces(Operator):
	'''Add intersect faces'''
	bl_idname = 'add_intrsct_faces.cuber'
	bl_label = 'Add Intersect Faces'
	bl_options = {'REGISTER', 'UNDO'}

	intr_faces : EnumProperty(
		name = "Intersect Faces",
		items = (
			('CUBE', 'Cube','Add cube as intersect faces'),
			('CYLINDER', 'Cylinder','Add cylinder as intersect faces')),
		default = 'CUBE')
	align : EnumProperty(
		name = "Alignment",
		items = (
			('MANUAL', 'Manual','Rotate manually'),
			('VIEW', 'View','Align to view'),
			('ACTIVE', 'Active','Align to selected elements')),
		default = 'MANUAL')
	cu_radius : FloatProperty(
		name        = "Radius",
		description = "Radius",
		default     = 0.1,
		step        = 0.1,
		precision   = 2
		)
	circle_seg : IntProperty(
		name        = "Cylinder Segments",
		description = "Cylinder segments",
		default     = 32,
		min         = 3,
		max         = 500
		)
	size_x : FloatProperty(
		name        = "X",
		description = "Scale to X axis",
		default     = 1,
		step        = 0.5,
		precision   = 2
		)
	size_y : FloatProperty(
		name        = "Y",
		description = "Scale to Y axis",
		default     = 1,
		step        = 0.5,
		precision   = 2
		)
	size_z : FloatProperty(
		name        = "Z",
		description = "Scale to Z axis",
		default     = 1,
		step        = 0.5,
		precision   = 2
		)
	rad_x : FloatProperty(
		name        = "X",
		description = "Rotate to X axis",
		default     = 0,
		min         = radians(-360),
		max         = radians(360),
		step        = 10,
		precision   = 3,
		subtype     = "ANGLE"
		)
	rad_y : FloatProperty(
		name        = "Y",
		description = "Rotate to Y axis",
		default     = 0,
		min         = radians(-360),
		max         = radians(360),
		step        = 10,
		precision   = 3,
		subtype     = "ANGLE"
		)
	rad_z : FloatProperty(
		name        = "Z",
		description = "Rotate to Z axis",
		default     = 0,
		min         = radians(-360),
		max         = radians(360),
		step        = 10,
		precision   = 3,
		subtype     = "ANGLE"
		)
	init_scale : BoolProperty(
		name        = "Initialize Scale",
		description = "Initializes scale values upon reuse of operator",
		default     = True,
		)
	init_rot : BoolProperty(
		name        = "Initialize Rotation",
		description = "Initializes rotation values upon reuse of operator",
		default     = True,
		)
	common_mat : BoolProperty(
		name        = "Use Common Material",
		description = "Use most common material in selected faces",
		default     = True,
		)

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == 'EDIT'

	def initiate_scale(self, context):
		self.size_x = 1
		self.size_y = 1
		self.size_z = 1

	def initiate_rotation(self, context):
		self.rad_x = 0
		self.rad_y = 0
		self.rad_z = 0

	def execute(self, context):
		sce = context.scene
		ob = context.active_object

		mesh = ob.data
		bm = bmesh.from_edit_mesh(mesh)

		mat_index = []
		elem_sel = [v for v in bm.verts if v.select]

		if len(elem_sel) == 0:
			cur_loc = sce.cursor_location.copy()
			pivot = ob.matrix_world.inverted() @ cur_loc
			mat_index.append(ob.active_material_index)
		else:
			pivot = sum([v.co for v in elem_sel], Vector()) / len(elem_sel)

			for v in elem_sel:
				for l_f in v.link_faces:
					mat_index.append(l_f.material_index)

		geo = bm.verts[:] + bm.edges[:] + bm.faces[:]
		for p in geo: p.select = False

		if self.intr_faces == "CUBE":
			cutter_mesh = bmesh.ops.create_cube(bm, size=self.cu_radius)
		else:
			cutter_mesh = bmesh.ops.create_cone(
				bm,
				cap_ends	= True,
				segments	= self.circle_seg,
				diameter1	= self.cu_radius*0.5,
				diameter2	= self.cu_radius*0.5,
				depth		= self.cu_radius
				)

		move_sel = []
		for v in cutter_mesh['verts']:
			move_sel.append(v)
			linked = v.link_faces
			for f in linked:
				f.select = True
				if mat_index:
					f.material_index = (max(mat_index, key = mat_index.count)
						if self.common_mat else min(mat_index, key = mat_index.count))

		mat_world = ob.matrix_world

		if self.align == "ACTIVE" and elem_sel:
			normal_mean = sum([v.normal for v in elem_sel], Vector()) / len(elem_sel)
			quat = normal_mean.to_track_quat('-Z', 'Y')
			mat = mat_world @ quat.to_matrix().to_4x4()
			rot = mat.to_3x3().normalized()
		elif self.align == "VIEW":
			r3d = context.space_data.region_3d
			vrot = r3d.view_rotation
			mat = mat_world @ vrot.to_matrix().to_4x4()
			rot = mat.to_3x3().normalized()
		else:
			rotX = mathutils.Matrix.Rotation(self.rad_x, 4, "X")
			rotY = mathutils.Matrix.Rotation(self.rad_y, 4,"Y")
			rotZ = mathutils.Matrix.Rotation(self.rad_z, 4, "Z")
			rot = [rotX, rotY, rotZ]

		scale = mathutils.Vector((self.size_x,
			self.size_y,
			self.size_z))

		bmesh.ops.translate(
				bm,
				verts	= move_sel,
				vec		= pivot
				)

		bmesh.ops.scale(
			bm,
			vec		= scale,
			space	= Matrix.Translation(pivot).inverted(),
			verts	= move_sel
			)

		try:
			if self.align == "MANUAL":
				for axis in rot:
					bmesh.ops.rotate(
							bm,
							verts	= move_sel,
							cent	= pivot,
							matrix	= axis
							)
			else:
				bmesh.ops.rotate(
						bm,
						verts	= move_sel,
						cent	= pivot,
						matrix	= rot
						)
		except: pass

		bmesh.update_edit_mesh(mesh)

		add_cuber_vgroup(context)

		return {'FINISHED'}

	def draw(self, context):
		layout = self.layout
		col = layout.column(align=True)
		col.row(align=True).prop(self, "intr_faces", expand=True)
		col.prop(self, "cu_radius")
		col.prop(self, "circle_seg")
		col.label(text="Scale:")
		row = col.row(align=True)
		row.prop(self, "size_x")
		row.prop(self, "size_y")
		row.prop(self, "size_z")
		col.label(text="Rotation:")
		row = col.row(align=True)
		row.prop(self, "rad_x")
		row.prop(self, "rad_y")
		row.prop(self, "rad_z")
		col.label(text="Aligment:")
		col.row(align=True).prop(self, "align", expand=True)
		col.separator()
		row = col.row(align=True)
		row.prop(self, "init_scale")
		row.prop(self, "init_rot")
		col.prop(self, "common_mat")

	def invoke(self, context, event):
		if self.init_scale:
			self.initiate_scale(context)
		if self.init_rot:
			self.initiate_rotation(context)

		return context.window_manager.invoke_props_popup(self, event)

class MESH_OT_get_weighted_edges(Operator):
	'''Select beveled edges'''
	bl_idname = 'quick_select.cuber'
	bl_label = 'Quick Assign/Select'
	bl_options = {'REGISTER', 'UNDO'}

	bweight_idx : FloatProperty()

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == 'EDIT'

	def execute(self, context):
		sce = context.scene
		props = context.scene.BevelPG
		ob = context.active_object

		bvl_weight = None
		select_wght = True

		mesh = ob.data
		if mesh.is_editmode:
			bm = bmesh.from_edit_mesh(mesh)
		else:
			bm = bmesh.new()
			bm.from_mesh(mesh)

		if not bm.edges.layers.bevel_weight:
			bm.edges.layers.bevel_weight.new()
		bevelWeightLayer = bm.edges.layers.bevel_weight['BevelWeight']

		bvl_weight = self.bweight_idx
		for e in bm.edges:
			if e.select:
				select_wght = False
				break

		if bvl_weight:
			for e in bm.edges:
				if select_wght:
					edge_weight = e[bevelWeightLayer]
					if bvl_weight == edge_weight:
						e.select = True
				else:
					if e.select:
						if props.get_sharp:
							angle = e.calc_face_angle(None)
							if angle != None and \
								angle > props.angle_sharp:
								e[bevelWeightLayer] = bvl_weight
							else: e[bevelWeightLayer] = 0.0

			read_bevel(context, bm, bevel_layer = bevelWeightLayer)

		if mesh.is_editmode:
			bmesh.update_edit_mesh(mesh)
		else:
			bm.to_mesh(mesh)
			mesh.update()

		context.scene.BevelPG["bevel_weight"] = bvl_weight

		return {'FINISHED'}

	def draw(self, context): None

class OBJECT_OT_copy_bevel_settings(Operator):
	'''Copy cuber bevel modifier settings'''
	bl_idname = 'copy_bevel.cuber'
	bl_label = 'Copy Cuber Bevel Modifier Settings'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		ob = context.active_object
		mod_nam = "Bevel"

		sync_bevel_settings(context, ob, mod_nam)

		return {'FINISHED'}

class OBJECT_OT_reuse_bevel(Operator):
	'''Reuse bevel weight or angle'''
	bl_idname = 'reuse_bevel.cuber'
	bl_label = 'Reuse Bevel Weight'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		props = context.scene.BevelPG
		props.update_Bevel(context)

		return {'FINISHED'}

class OBJECT_OT_refresh_list(Operator):
	'''Update bevel weights list for active object'''
	bl_idname = 'refresh_list.cuber'
	bl_label = 'Update Bevel Weights List'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		sce = context.scene
		ob = context.active_object

		mesh = ob.data
		if mesh.is_editmode:
			bm = bmesh.from_edit_mesh(mesh)
		else:
			bm = bmesh.new()
			bm.from_mesh(mesh)

		if not bm.edges.layers.bevel_weight:
			bm.edges.layers.bevel_weight.new()
		bevelWeightLayer = bm.edges.layers.bevel_weight['BevelWeight']

		read_bevel(context, bm, bevel_layer = bevelWeightLayer)

		if mesh.is_editmode:
			bmesh.update_edit_mesh(mesh)
		else:
			bm.to_mesh(mesh)
			mesh.update()

		return {'FINISHED'}

class OBJECT_OT_apply_bevel_modifier(Operator):
	'''Apply/remove bevel modifier'''
	bl_idname = 'apply_bevel.cuber'
	bl_label = 'Apply/Remove Bevel Modifier'
	bl_options = {'REGISTER', 'UNDO'}

	action : EnumProperty(
		items = (
			('APPLY', '',''),
			('REMOVE', '','')),
		default = 'APPLY')
	remove_bweights : BoolProperty(
		name        =   "Remove Bevel Weights",
		description =   "Remove bevel weights along with Cuber Bevel modifier",
		default     =   False
		)

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		ob = context.active_object

		cm = ['Bevel', 'Weighted Normal']
		wn = ob.modifiers.get(cm[1])

		old_mode = ob.mode
		mode_set = bpy.ops.object.mode_set
		mode_set(mode="OBJECT")

		if self.action == "APPLY":
			bpy.ops.object.modifier_apply(modifier=cm[0])
			if wn:
				bpy.ops.object.modifier_apply(modifier=cm[1])
		else:
			bpy.ops.object.modifier_remove(modifier=cm[0])
			if wn:
				bpy.ops.object.modifier_remove(modifier=cm[1])

		mesh = ob.data
		bm = bmesh.new()
		bm.from_mesh(mesh)

		if not bm.edges.layers.bevel_weight:
			bm.edges.layers.bevel_weight.new()
		bevelWeightLayer = bm.edges.layers.bevel_weight['BevelWeight']

		if self.action == "APPLY" or self.remove_bweights:
			for edge in bm.edges: edge[bevelWeightLayer] = 0

		read_bevel(context, bm, bevel_layer = bevelWeightLayer)

		bm.to_mesh(mesh)
		mesh.update()

		mode_set(mode=old_mode)

		return {'FINISHED'}

	def draw(self, context):
		if self.action == "REMOVE":
			layout = self.layout
			layout.prop(self, "remove_bweights")

class OBJECT_OT_add_weighted_normal(Operator):
	'''Add weighted normal modifier and set to lower bevel segments'''
	bl_idname = 'add_weighted.cuber'
	bl_label = 'Add Weighted Normal Modifier'
	bl_options = {'REGISTER', 'UNDO'}

	deg : FloatProperty(
		name        = "Auto Smooth Angle",
		description = "Auto smooth angle",
		default     = radians(30),
		min         = 0,
		max         = radians(180),
		step        = 10,
		precision   = 3,
		subtype     = "ANGLE"
		)

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode != 'EDIT'

	def execute(self, context):
		sce = context.scene
		ob = context.active_object
		props = context.scene.BevelPG

		cm = ['Bevel', 'Weighted Normal']
		mod = ob.modifiers

		for m in mod:
			if m.type == 'WEIGHTED_NORMAL':
				ob.modifiers.remove(m)

		weight_op = ob.modifiers.new(cm[1], 'WEIGHTED_NORMAL')
		weight_op.show_expanded = False
		weight_op.show_in_editmode = False

		c_bvl = mod.get(cm[0])
		if not c_bvl:
			add_bevel(self,
				context,
				props.use_angle,
				props.bevel_deg,
				props.width,
				sce.weighted_segments,
				props.profile,
				props.use_clamp,
				props.use_slide,
				props.harden_normals,
				props.offset_type,
				props.face_strength_mode,
				props.push_bevel,
				props.clear_bevel)
		else:
			c_bvl.segments = sce.weighted_segments
			cm_down_stack(cm, mod, props.push_bevel)

		sync_bevel_settings(context, ob, cm[0])
		auto_smooth(context, ob, self.deg, True)

		return {'FINISHED'}

	def draw(self, context):
		layout = self.layout
		layout.prop(self, "deg")

class MESH_OT_get_sharp(Operator):
	'''Select sharp edges'''
	bl_idname = 'get_sharp.cuber'
	bl_label = 'Get Sharp'
	bl_options = {'REGISTER', 'UNDO'}

	sharpness : FloatProperty(
		description = "Edge sharpness",
		name        = "Sharpness",
		default     = radians(30),
		min         = radians(1),
		max         = radians(180),
		step        = 10,
		precision   = 3,
		subtype     = "ANGLE"
		)
	mark_sharp : BoolProperty(
		name        = "Mark Sharp",
		description = "Mark edges as sharp",
		default     = False
		)

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == 'EDIT'

	def edge_sharp(self, edge):

		angle = edge.calc_face_angle(None)
		if angle != None and \
			angle > self.sharpness:
			edge.select = True
			edge.smooth = False if self.mark_sharp else True

	def execute(self, context):
		ob = context.active_object

		mesh = ob.data
		bm = bmesh.from_edit_mesh(mesh)

		bpy.ops.mesh.select_mode(type='EDGE')

		edge_sel = [e for e in bm.edges if e.select]

		if edge_sel:
			for e in edge_sel:
				for f in e.link_faces: f.select = False

		if (edge_sel and
			len(edge_sel) < len(bm.edges[:])):
			for e in edge_sel:
				self.edge_sharp(e)
		else:
			for e in bm.edges:
				self.edge_sharp(e)

		bmesh.update_edit_mesh(mesh)

		return {'FINISHED'}

	def draw(self, context):
		layout = self.layout
		layout.prop(self, "sharpness")
		layout.prop(self, "mark_sharp")

class MESH_OT_mark_sharp(Operator):
	'''Mark selected edges as sharp'''
	bl_idname = 'mark_sharp.cuber'
	bl_label = 'Mark Sharp'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == 'EDIT'

	def execute(self, context):
		ob = context.active_object

		mesh = ob.data
		bm = bmesh.from_edit_mesh(mesh)

		for e in bm.edges:
			if e.select: e.smooth = False

		bmesh.update_edit_mesh(mesh)

		return {'FINISHED'}

class MESH_OT_clear_sharp(Operator):
	'''Unmark selected edges as sharp'''
	bl_idname = 'clear_sharp.cuber'
	bl_label = 'Clear Sharp'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == 'EDIT'

	def execute(self, context):
		ob = context.active_object

		mesh = ob.data
		bm = bmesh.from_edit_mesh(mesh)

		edge_sel = [e for e in bm.edges if e.select]

		if edge_sel:
			for e in edge_sel: e.smooth = True
		else:
			for e in bm.edges: e.smooth = True

		bmesh.update_edit_mesh(mesh)

		return {'FINISHED'}

class OBJECT_OT_bweight_lock(Operator):
	'''Lock/unlock quick assign and select feature on object'''
	bl_idname = "bweight_lock.cuber"
	bl_label = "Lock/Unlock Quick Assign And Select Feature On Object"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		sce = context.scene
		ob = context.active_object
		mode = ""

		lockList = [i.obdataList for i in sce.bweightlockList]
		if ob.name not in lockList:
			newListItem = sce.bweightlockList.add()
			newListItem.obdataList = ob.name
			mode = "Add"

			update_lock_list(context, newListItem.obdataList, ob.name, None, mode)
		else:
			mode = "Remove"
			update_lock_list(context, None, ob.name, None, mode)

		noUsers = [i.name for i in bpy.data.meshes if i.users == 0]
		mode = "Clean"
		update_lock_list(context, None, None, noUsers, mode)

		return {'FINISHED'}

class OBJECT_OT_bweight_lock_purge(Operator):
	'''Purge quick assign and select locked object list'''
	bl_idname = "bweight_lock_purge.cuber"
	bl_label = "Purge Quick Assign And Select Locked Object List"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		sce = context.scene

		self.report({'INFO'}, "Removed " + str(len(sce.bweightlockList)) + " object(s) from list.")
		sce.bweightlockList.clear()

		return {'FINISHED'}

class MESH_OT_cuber_vgroup_purge(Operator):
	'''Remove selected as intersect faces'''
	bl_idname = "cuber_vgroup_purge.cuber"
	bl_label = "Remove As Intersect Faces"
	bl_options = {'REGISTER', 'UNDO'}

	separate : BoolProperty(
		name        = "Separate",
		description = "Separate selected faces as new object",
		default     = False
		)

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == 'EDIT'

	def execute(self, context):
		sce = context.scene
		ob = context.active_object
		vg_name = "Intersect Faces"

		if ob.vertex_groups.get(vg_name):
			rem_vgroup(context, ob, vg_name)

		if self.separate:
			mesh = ob.data
			bm = bmesh.from_edit_mesh(mesh)

			faces_sel = [f for f in bm.faces if f.select]

			if faces_sel and \
				len(faces_sel) != len(bm.faces[:]):
				bpy.ops.mesh.separate()

			bmesh.update_edit_mesh(mesh)
		else:
			for sel_ob in context.selected_objects:
				if sel_ob != ob: remove_obj(sce, sel_ob)

		return {'FINISHED'}

	def draw(self, context):
		layout = self.layout
		layout.prop(self, "separate")

	def invoke(self, context, event):
		for sel_ob in context.selected_objects:
			if sel_ob != context.active_object: sel_ob.select_set(False)

		return self.execute(context)

def view3d_to_view2d(context, points):

	coord_2d = []

	x = type(None)
	for v in points:
		view2d_co = view3d_utils.location_3d_to_region_2d(context.region, \
										   context.space_data.region_3d, \
										   v)
		coord_2d.append([view2d_co.x,view2d_co.y] if not isinstance(view2d_co, x) else x)

	if x in coord_2d: coord_2d.clear()

	return coord_2d

def draw_line(context, ob):

	mesh = ob.data

	vertices = np.empty((len(mesh.vertices), 3), 'f')
	mesh.vertices.foreach_get("co", np.reshape(vertices, len(mesh.vertices) * 3))

	coord_2d = view3d_to_view2d(context, vertices)

	shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
	batch = batch_for_shader(shader, 'LINES', {"pos" : coord_2d})

	shader.bind()
	shader.uniform_float("color", context.scene.proxy_cutter_color)
	batch.draw(shader)

def draw_mesh(context, ob):

	mesh = ob.data

	vertices = np.empty((len(mesh.vertices), 3), 'f')
	indices = []

	mesh.vertices.foreach_get("co", np.reshape(vertices, len(mesh.vertices) * 3))
	for f in mesh.polygons:
		for e_keys in f.edge_keys:
			indices.append(e_keys)

	coord_2d = view3d_to_view2d(context, vertices)

	if coord_2d:
		shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
		batch = batch_for_shader(shader, 'LINES', {"pos" : coord_2d}, indices=indices)

		shader.bind()
		shader.uniform_float("color", context.scene.proxy_cutter_color)
		batch.draw(shader)

def draw_callback_px(self, context):

	if not self.set_thickness:
		if self.cutter_ob.data.polygons:
			draw_mesh(context, self.cutter_ob)
		else:
			draw_line(context, self.cutter_ob)
	else:
		draw_mesh(context, self.cutter_draw)

class OBJECT_OT_cuber_draw_cutter(Operator):
	'''Direct boolean draw cutter and draw based knife tool'''
	bl_idname = "draw_cutter.cuber"
	bl_label = "Gpencil Poly Cutter"
	bl_options = {'REGISTER', 'UNDO'}

	cutter_op : bpy.props.EnumProperty(
		items = (
			('CUT', 'Cut',''),
			('SLICE', 'Slice',''),
			('DRAW', 'Draw','')),
		default = 'CUT')

	cutter_met : bpy.props.EnumProperty(
		items = (
			('BOX', 'Box',''),
			('POLYGONAL', 'Polygonal',''),
			('CIRCLE', 'Circle','')),
		default = 'BOX')

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.type == 'MESH'

	def initialize(self, context, set):

		if set:
			context.region_data.view_perspective = "ORTHO"
		else:
			context.region_data.view_perspective = self.old_view
			context.area.header_text_set(None)
			for obs in bpy.data.meshes:
				if obs.users == 0 \
				and obs.name.startswith("Poly Cutter"):
					bpy.data.meshes.remove(obs)

	def create_header(self, context):

		sce = context.scene

		bevel_width = str('% 0.4f' % sce.cutter_bevel_width).strip()
		bevel_profile = str('% 0.2f' % sce.cutter_bevel_profile).strip()
		bevel_segments = str(sce.cutter_bevel_segments)
		circle_segments = str(sce.cutter_circle_segments)
		cutter_depth = str('% 0.4f' % sce.cutter_depth).strip()

		if not self.set_thickness:
			header = ", ".join(filter(None,
				[
				" ".join([self.cutter_op.title(), "Method (1/2/3): {method}"]),
				"Origin (Shift 1/2/3): {origin}",
				"Width (Alt+Mouse Drag): {width}",
				"Profile (Ctrl+MMB Roll): {profile}",
				"Segments (MMB Roll): {segments}",
				"Circle Segments (Shift+MMB Roll): {circle_segs}" if self.cutter_met == 'CIRCLE' else "",
				("Cut Through (MMB Click): " + ("Yes" if self.cut_thru else "No")) if self.cutter_op == 'DRAW' else "",
				"Shift: Slow increments/Snap to angle",
				"LMB: Add points",
				"Enter/Space: Confirm",
				"Esc/RMB: Cancel draw/points"
				]))
		else:
			header = ", ".join(
				[
				" ".join([self.cutter_op.title(), "Depth (Ctrl+Mouse Drag): {depth}"]),
				"Additional Controls: Shift/Alt 1-9 or Shift/Alt MMB Roll",
				"Shift: Slow increments",
				"Enter/Space: Confirm",
				"Esc: Cancel"
				])

		return header.format(
			method=self.cutter_met.title(),
			origin=self.hit_point,
			width=bevel_width,
			profile=bevel_profile,
			segments=bevel_segments,
			circle_segs=circle_segments,
			depth=cutter_depth)

	def create_ob(self, context):

		data_obj = bpy.data.meshes.new("Poly Cutter")
		new_ob = bpy.data.objects.new("Poly Cutter", data_obj)

		return new_ob

	def update_cutter_draw(self, context):

		full_draw = self.cutter_ob.to_mesh(context.depsgraph, True)
		self.cutter_draw.data = full_draw

	def update_ob(self, context, ob, points):

		sce = context.scene
		mat = ob.matrix_world

		mesh = ob.data
		bm = bmesh.new()
		bm.from_mesh(mesh)

		if bm.verts:
			bmesh.ops.delete(bm, geom=bm.verts, context='VERTS')

		for v_co in points:
			if self.hit_point == 'Surface':
				self.get_surface(context, v_co)

			loc = self.view_loc(context, v_co)
			loc = mat.inverted() @ loc

			new_v = bm.verts.new()
			new_v.co = loc

			if self.hit_point in ['Point', 'Center']:
				trim_co = intersect_line_plane(new_v.co, new_v.co + self.view_plane, self.hit_world, self.view_plane)
				if trim_co is not None: new_v.co = trim_co

		v_count = len(bm.verts)
		if v_count > 2:
			bm.faces.new(bm.verts)
		else:
			bmesh.ops.contextual_create(bm, geom=bm.verts)

		bmesh.ops.bevel(
			bm,
			geom            = bm.verts,
			offset          = sce.cutter_bevel_width,
			offset_type     = 'OFFSET',
			segments        = sce.cutter_bevel_segments,
			profile         = sce.cutter_bevel_profile,
			vertex_only     = True,
			clamp_overlap   = True,
			)

		bmesh.ops.remove_doubles(
			bm,
			verts   = bm.verts,
			dist    = 0.00001
			)

		bm.to_mesh(mesh)
		mesh.update()

	def get_center(self, ob):

		v_co = sum([v.co for v in ob.data.vertices], Vector()) / len(ob.data.vertices)
		center_3d = ob.matrix_world @ v_co

		return center_3d

	def get_surface(self, context, co):

		sce = context.scene
		region = context.region
		rv3d = context.region_data

		coord = []

		if co:
			coord = co[0], co[1]
		else:
			if self.hit_point == 'Point' \
				and self.mouse_pos:
				if self.cutter_met == 'BOX' or \
					self.cutter_met == 'CIRCLE':
					coord = self.mouse_pos[0][0], self.mouse_pos[0][1]
				else:
					coord = self.mouse_pos[1][0], self.mouse_pos[1][1]

			if self.hit_point == 'Center':
				center_3d = self.get_center(self.cutter_ob)
				focal_2d = view3d_utils.location_3d_to_region_2d(context.region, \
												   context.space_data.region_3d, \
												   center_3d.xyz)
				coord = focal_2d.x, focal_2d.y

		if not coord:
			coord = region.width / 2, region.height / 2

		view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
		ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

		ray_target = ray_origin + view_vector

		def selectable_objs_matrix():

			for ob in context.selectable_objects:
				if ob.type == 'MESH':
					yield (ob, ob.matrix_parent_inverse.copy())

		def scene_ray_cast(matrix):

			matrix_inv = matrix.inverted()
			ray_origin_ob = matrix_inv @ ray_origin
			ray_target_ob = matrix_inv @ ray_target
			ray_direction_ob = ray_target_ob - ray_origin_ob

			hit, pos, normal, face_index, ob, matrix_world = sce.ray_cast(context.view_layer, ray_origin_ob, ray_direction_ob)

			if hit:
				return pos, normal, face_index
			else:
				return None, None, None

		for ob, matrix in selectable_objs_matrix():
			if ob.type == 'MESH':
				pos, normal, face_index = scene_ray_cast(matrix)
				if pos is not None:
					self.hit_world = matrix @ pos
					self.view_plane = view_vector
					break

	def view_loc(self, context, coord):

		region = context.region
		rv3d = context.region_data

		ray_max = 1000.0
		view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
		ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

		if self.hit_world:
			origin = ray_origin
			point = self.hit_world
			distance = (origin-point).length

			ray_origin = ray_origin + distance * (rv3d.view_rotation @ Vector((0,0,-1)))
			loc = ray_origin
		else:
			loc = ray_origin - (view_vector * ray_max)
			loc = loc + (view_vector * ray_max)

		return loc

	def get_focal(self, context, event):

		if self.cutter_ob.data.vertices:
			center_3d = self.get_center(self.cutter_ob)
			focal_2d = view3d_utils.location_3d_to_region_2d(context.region, \
											   context.space_data.region_3d, \
											   center_3d.xyz)
		else:
			focal_2d = Vector((context.region.width / 2, \
				context.region.height / 2))

		curr_mouse = Vector((event.mouse_region_x, event.mouse_region_y))
		prev_mouse = Vector((event.mouse_prev_x - context.region.x,
			event.mouse_prev_y - context.region.y))

		dist1 = (focal_2d - curr_mouse).length
		dist2 = (focal_2d - prev_mouse).length

		return dist1, dist2

	def angle_to_2d(self, origin, point, angle):

		ox, oy = origin
		px, py = point

		dist = (origin - point).length

		qx = int(ox + dist * math.cos(angle))
		qy = int(oy + dist * math.sin(angle))

		return qx, qy

	def clean_obj_set(self, sce, set1, set2):

		if set1:
			for obs in set1:
				mod = obs.modifiers
				if mod.get(self.cutter_mod):
					mod.remove(mod[self.cutter_mod])

		if set2:
			for obs in set2:
				remove_obj(sce, obs)

	def clean_cutters(self, context):

		sce = context.scene

		cutter_set = [self.cutter_ob, self.cutter_draw]
		for obs in cutter_set:
			remove_obj(sce, obs)

	def cancel_draw(self, context, sce):

		self.clean_obj_set(sce, self.cut_set, self.slice_set)
		self.clean_cutters(context)

		self.initialize(context, set=False)
		bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

	def modal(self, context, event):
		sce = context.scene
		ob_sel = context.selected_objects

		context.area.tag_redraw()

		if self.set_thickness:
			cutter_shell = self.cutter_ob.modifiers.get("Solidify")
			sensitivity = sce.cutter_incr_sensitivity

			if self.cutter_ob:
				if event.type == 'ZERO':
					sce.cutter_depth = 0.0
					cutter_shell.thickness = sce.cutter_depth
				if event.type == 'ONE':
					sce.cutter_depth = sensitivity * 1.0
					if event.shift: sce.cutter_depth = sensitivity * 0.1
					if event.alt: sce.cutter_depth = sensitivity * 0.01
					cutter_shell.thickness = sce.cutter_depth
				if event.type == 'TWO':
					sce.cutter_depth = sensitivity * 2.0
					if event.shift: sce.cutter_depth = sensitivity * 0.2
					if event.alt: sce.cutter_depth = sensitivity * 0.02
					cutter_shell.thickness = sce.cutter_depth
				if event.type == 'THREE':
					sce.cutter_depth = sensitivity * 3.0
					if event.shift: sce.cutter_depth = sensitivity * 0.3
					if event.alt: sce.cutter_depth = sensitivity * 0.03
					cutter_shell.thickness = sce.cutter_depth
				if event.type == 'FOUR':
					sce.cutter_depth = sensitivity * 4.0
					if event.shift: sce.cutter_depth = sensitivity * 0.4
					if event.alt: sce.cutter_depth = sensitivity * 0.04
					cutter_shell.thickness = sce.cutter_depth
				if event.type == 'FIVE':
					sce.cutter_depth = sensitivity * 5.0
					if event.shift: sce.cutter_depth = sensitivity * 0.5
					if event.alt: sce.cutter_depth = sensitivity * 0.05
					cutter_shell.thickness = sce.cutter_depth
				if event.type == 'SIX':
					sce.cutter_depth = sensitivity * 6.0
					if event.shift: sce.cutter_depth = sensitivity * 0.6
					if event.alt: sce.cutter_depth = sensitivity * 0.06
					cutter_shell.thickness = sce.cutter_depth
				if event.type == 'SEVEN':
					sce.cutter_depth = sensitivity * 7.0
					if event.shift: sce.cutter_depth = sensitivity * 0.7
					if event.alt: sce.cutter_depth = sensitivity * 0.07
					cutter_shell.thickness = sce.cutter_depth
				if event.type == 'EIGHT':
					sce.cutter_depth = sensitivity * 8.0
					if event.shift: sce.cutter_depth = sensitivity * 0.8
					if event.alt: sce.cutter_depth = sensitivity * 0.08
					cutter_shell.thickness = sce.cutter_depth
				if event.type == 'NINE':
					sce.cutter_depth = sensitivity * 9.0
					if event.shift: sce.cutter_depth = sensitivity * 0.9
					if event.alt: sce.cutter_depth = sensitivity * 0.09
					cutter_shell.thickness = sce.cutter_depth

				if event.type in {'ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', \
					'SIX', 'SEVEN', 'EIGHT', 'NINE'}:
					self.update_cutter_draw(context)

			if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
				if event.type == 'WHEELUPMOUSE':
					if event.ctrl:
						incr = 1.0
						sce.cutter_depth += sensitivity * incr
						cutter_shell.thickness = sce.cutter_depth

					if event.shift:
						incr = 0.1
						sce.cutter_depth += sensitivity * incr
						cutter_shell.thickness = sce.cutter_depth

					if event.alt:
						incr = 0.01
						sce.cutter_depth += sensitivity * incr
						cutter_shell.thickness = sce.cutter_depth

				if event.type == 'WHEELDOWNMOUSE':
					if event.ctrl:
						incr = 1.0
						sce.cutter_depth -= sensitivity * incr
						cutter_shell.thickness = sce.cutter_depth

					if event.shift:
						incr = 0.1
						sce.cutter_depth -= sensitivity * incr
						cutter_shell.thickness = sce.cutter_depth

					if event.alt:
						incr = 0.01
						sce.cutter_depth -= sensitivity * incr
						cutter_shell.thickness = sce.cutter_depth

				if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
					if event.ctrl or event.shift \
						or event.alt:
						self.update_cutter_draw(context)

				return {'PASS_THROUGH'}

			if event.type == 'MOUSEMOVE':
				if event.ctrl:
					dist1, dist2 = self.get_focal(context, event)
					dim = self.avg_dim if self.avg_dim > 0.5 else 0.5
					cent = dist1 * 1.0e-5

					if event.shift: cent = cent / 10
					incr = round(dim * cent, 4)

					if dist1 > dist2:
						sce.cutter_depth += incr
					elif dist1 < dist2:
						sce.cutter_depth -= incr

					cutter_shell.thickness = sce.cutter_depth
					self.update_cutter_draw(context)
		else:
			if event.type in {'ONE'}:
				if event.value == 'PRESS':
					if event.shift:
						self.hit_point = 'Point'
					else:
						self.cutter_met = 'BOX'
			elif event.type in {'TWO'}:
				if event.value == 'PRESS':
					if event.shift:
						self.hit_point = 'Surface'
					else:
						self.cutter_met = 'POLYGONAL'
			elif event.type in {'THREE'}:
				if event.value == 'PRESS':
					if event.shift:
						self.hit_point = 'Center'
					else:
						self.cutter_met = 'CIRCLE'

			if event.type in {'ONE', 'TWO', 'THREE'}:
				if not event.shift:
					self.mouse_pos.clear()
					self.update_ob(context, self.cutter_ob, [])

			if event.type == 'WHEELUPMOUSE':
				if event.ctrl:
					incr = 0.1
					if event.shift: incr = 0.01
					sce.cutter_bevel_profile += incr
				elif event.shift:
					sce.cutter_circle_segments += 1
				else:
					sce.cutter_bevel_segments += 1

			if event.type == 'WHEELDOWNMOUSE':
				if event.ctrl:
					incr = 0.1
					if event.shift: incr = 0.01
					sce.cutter_bevel_profile -= incr
				elif event.shift:
					sce.cutter_circle_segments -= 1
				else:
					sce.cutter_bevel_segments -= 1

			if event.type == 'MIDDLEMOUSE':
				self.mmb = event.value == 'RELEASE'
				if self.mmb:
					if self.cutter_op == 'DRAW':
						if self.cut_thru:
							self.cut_thru = False
						else:
							self.cut_thru = True

			if event.type == 'MOUSEMOVE':
				if event.alt:
					dist1, dist2 = self.get_focal(context, event)
					dim = self.avg_dim if self.avg_dim > 0.5 else 0.5
					cent = dist1 * 1.0e-5

					if event.shift: cent = cent / 10
					incr = round(dim * cent, 4)

					if dist1 > dist2:
						sce.cutter_bevel_width += incr
					elif dist1 < dist2:
						sce.cutter_bevel_width -= incr

				if self.cutter_met == 'POLYGONAL':
					mouse_region_x = event.mouse_region_x
					mouse_region_y = event.mouse_region_y

					if (not event.alt
						and not event.ctrl):
						if event.shift:
							if len(self.mouse_pos) > 1:
								origin = Vector(self.mouse_pos[-2])
								point = Vector((event.mouse_region_x, event.mouse_region_y))

								rad = math.atan2(point.y - origin.y, point.x - origin.x)
								deg = math.degrees(rad)

								snap = ((deg + 15) // 45 * 45) % 360

								qx, qy = self.angle_to_2d(origin, point, math.radians(snap))

								mouse_region_x = qx
								mouse_region_y = qy

					if not self.mouse_pos:
						self.mouse_pos.append((event.mouse_region_x, event.mouse_region_y))
					else:
						self.mouse_pos.remove(self.mouse_pos[-1])
						self.mouse_pos.append((mouse_region_x, mouse_region_y))

			if event.type == 'LEFTMOUSE':
				self.lmb = event.value == 'PRESS'
				if self.lmb:
					self.mouse_pos.append((event.mouse_region_x, event.mouse_region_y))
					if self.cutter_met == 'BOX' \
						and len(self.mouse_pos) > 1:
							self.mouse_pos.remove(self.mouse_pos[-1])
					elif self.cutter_met == 'CIRCLE' \
						and len(self.mouse_pos) > 1:
							self.mouse_pos.remove(self.mouse_pos[-1])

			if event.type == 'RIGHTMOUSE':
				self.rmb = event.value == 'PRESS'
				if self.rmb:
					if self.cutter_met == 'BOX' or \
						self.cutter_met == 'CIRCLE':
						if self.mouse_pos:
							self.mouse_pos.remove(self.mouse_pos[-1])
							self.update_ob(context, self.cutter_ob, [])
						else:
							self.cancel_draw(context, sce)

							return {'CANCELLED'}
					else:
						if len(self.mouse_pos) > 1:
							self.mouse_pos.remove(self.mouse_pos[-1])
						else:
							self.cancel_draw(context, sce)

							return {'CANCELLED'}

			# update cutter object
			if self.cutter_met == "BOX":
				if self.mouse_pos:
					w = self.mouse_pos[0][0] - event.mouse_region_x
					h = self.mouse_pos[0][1] - event.mouse_region_y
					vco1 = self.mouse_pos[0][0] - w, self.mouse_pos[0][1] - h
					vco2 = self.mouse_pos[0][0], self.mouse_pos[0][1] - h
					vco3 = self.mouse_pos[0][0], self.mouse_pos[0][1]
					vco4 = self.mouse_pos[0][0] - w, self.mouse_pos[0][1]

					self.box_pos = [vco1, vco2, vco3, vco4]
					self.update_ob(context, self.cutter_ob, self.box_pos)
			elif self.cutter_met == "CIRCLE":
				if self.mouse_pos:
					num_segments = sce.cutter_circle_segments
					origin = Vector(self.mouse_pos[0])
					cx, cy = origin
					point = Vector((event.mouse_region_x, event.mouse_region_y))
					r = (origin - point).length

					theta = 2 * 3.1415926 / num_segments
					c = math.cos(theta)
					s = math.sin(theta)

					x = r
					y = 0

					self.circle_pos = []
					for i in range (num_segments):
						self.circle_pos.append((x + cx, y + cy))
						t = x
						x = c * x - s * y
						y = s * t + c * y

					self.update_ob(context, self.cutter_ob, self.circle_pos)
			elif self.cutter_met == "POLYGONAL":
				self.update_ob(context, self.cutter_ob, self.mouse_pos)

		if not self.set_thickness:
			if event.type in {'RET', 'NUMPAD_ENTER', 'SPACE'}:
				if event.value == 'PRESS':
					if self.cutter_met == 'BOX' or \
						self.cutter_met == 'CIRCLE':
						if not self.mouse_pos:
							self.report({'WARNING'}, "Not enough points.")
							self.cancel_draw(context, sce)

							return {'FINISHED'}
					else:
						if not len(self.mouse_pos) > 2:
							self.report({'WARNING'}, "Not enough points.")
							self.cancel_draw(context, sce)

							return {'FINISHED'}

					self.get_surface(context, None)
					if self.cutter_met == 'BOX':
						self.update_ob(context, self.cutter_ob, self.box_pos)
					elif self.cutter_met == 'CIRCLE':
						self.update_ob(context, self.cutter_ob, self.circle_pos)
					elif self.cutter_met == 'POLYGONAL':
						self.update_ob(context, self.cutter_ob, self.mouse_pos)

					if self.cutter_op == 'DRAW':
						sce.collection.objects.link(self.cutter_ob)

						ob_sel.append(self.cutter_ob)
						for obs in ob_sel:
							obs.select_set(True if obs in [self.orig_ob, self.cutter_ob]
								else False)

						context.view_layer.objects.active = self.orig_ob
						bpy.ops.mesh.knife_project(cut_through = self.cut_thru)

						if not self.cut_thru:
							bpy.ops.mesh.select_all(action='DESELECT')

						self.clean_cutters(context)

						self.initialize(context, set=False)
						bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

						return {'FINISHED'}
					else:
						self.set_thickness = True

						cutter_mod = self.cutter_ob.modifiers
						shell_op = cutter_mod.new("Solidify", "SOLIDIFY")
						shell_op.offset = 0.0
						shell_op.thickness = sce.cutter_depth

						self.update_cutter_draw(context)
						context.region_data.view_perspective = self.old_view

					for obs in ob_sel:
						if obs.type == 'MESH':
							ob_mod = obs.modifiers

							has_cutter = ob_mod.get(self.cutter_mod)
							if has_cutter:
								ob_mod.remove(ob_mod[self.cutter_mod])

							has_slice = ob_mod.get(self.cutter_mod)
							if has_slice:
								ob_mod.remove(ob_mod[self.slicer_mod])

							slice_op = ob_mod.new(self.cutter_mod, "BOOLEAN")
							slice_op.object = self.cutter_ob
							slice_op.operation = 'DIFFERENCE'

							slice_obs = []
							if self.cutter_op == 'SLICE':
								slice_ob = duplicate_obj(sce, "Cuber Slice", obs)

								self.cut_set.append(slice_ob)
								self.slice_set.append(slice_ob)

								mod = slice_ob.modifiers

								slice_op = mod.new(self.slicer_mod, 'BOOLEAN')
								slice_op.object = self.cutter_ob
								slice_op.operation = 'INTERSECT'

								if not slice_ob.data.polygons:
									remove_obj(sce, slice_ob)
								else:
									slice_obs = [obs, slice_ob]
									if sce.cutter_use_autosmooth:
										auto_smooth(context, obs, sce.cutter_autosmooth_angle, True)

							self.cut_set.append(obs)

							if slice_obs:
								copy_mod(objs = slice_obs)
								slice_obs[-1].modifiers.remove(slice_obs[-1].modifiers.get(self.cutter_mod))

							obs.select_set(True)
							context.view_layer.objects.active = obs

							while ob_mod.find(self.cutter_mod) != 0:
								bpy.ops.object.modifier_move_up(modifier=self.cutter_mod)
		else:
			if event.type in {'RET', 'NUMPAD_ENTER', 'SPACE'}:
				if event.value == 'PRESS':
					# temp
					new_mesh = self.cutter_ob.to_mesh(context.depsgraph, True)
					self.cutter_ob.modifiers.clear()
					self.cutter_ob.data = new_mesh

					cutter_data = self.cutter_ob.data
					bm = bmesh.new()
					bm.from_mesh(cutter_data)

					if not bm.edges.layers.bevel_weight:
							bm.edges.layers.bevel_weight.new()

					bm.to_mesh(cutter_data)
					cutter_data.update()

					for obs in self.cut_set:
						ob_mod = obs.modifiers

						obs.select_set(True)
						context.view_layer.objects.active = obs

						if ob_mod.get(self.cutter_mod):
							bpy.ops.object.modifier_apply(modifier=self.cutter_mod)

						if ob_mod.get(self.slicer_mod):
							bpy.ops.object.modifier_apply(modifier=self.slicer_mod)

						if not obs.data.polygons:
							remove_obj(sce, obs)
						else:
							if sce.cutter_use_autosmooth:
								auto_smooth(context, obs, sce.cutter_autosmooth_angle, True)

					self.clean_cutters(context)

					self.initialize(context, set=False)
					bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')

					return {'FINISHED'}

		if event.type in {'ESC'}:
			self.cancel_draw(context, sce)

			return {'CANCELLED'}

		context.area.header_text_set(self.create_header(context))

		return {'RUNNING_MODAL'}

	def invoke(self, context, event):
		if context.area.type == 'VIEW_3D':
			args = (self, context)

			self.orig_ob = context.active_object
			ob_dim = self.orig_ob.dimensions.copy()
			self.avg_dim = sum(d for d in ob_dim)/len(ob_dim)

			self.cutter_mod = "Poly Cut"
			self.slicer_mod = "Poly Slice"

			self.lmb = False
			self.rmb = False
			self.mmb = False

			self.box_pos = []
			self.circle_pos = []
			self.mouse_pos = []

			self.hit_point = 'Point'
			self.hit_world = Vector()
			self.view_plane = Vector()

			self.cut_thru = False
			self.set_thickness = False

			self.cut_set = []
			self.slice_set = []

			self.cutter_ob = self.create_ob(context)
			self.cutter_draw = self.create_ob(context)

			self.get_surface(context, None)

			sce = context.scene
			typ_sce = bpy.types.Scene
			if sce.cutter_reset_param:
				sce.cutter_bevel_width = typ_sce.cutter_bevel_width[1].get("default")
				sce.cutter_bevel_profile = typ_sce.cutter_bevel_profile[1].get("default")
				sce.cutter_bevel_segments = typ_sce.cutter_bevel_segments[1].get("default")
				sce.cutter_circle_segments = typ_sce.cutter_circle_segments[1].get("default")

			self.old_view = context.region_data.view_perspective
			self.initialize(context, set=True)

			self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

			context.window_manager.modal_handler_add(self)

			return {'RUNNING_MODAL'}
		else:
			self.report({'WARNING'}, "View3D not found, cannot run operator")

			return {'CANCELLED'}

		return {'RUNNING_MODAL'}

	def draw(self, context): None

class MATERIAL_OT_add_mat_palette(Operator):
	'''Add active material to palette list'''
	bl_idname = "mat_to_list.cuber"
	bl_label = "Add Material To Palette List"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def remove_dups(self, context, sce, newmat):
		count = 0
		dup_count = 0
		for i in sce.matPalette:
			if i.matList == newmat:
				dup_count += 1
				if dup_count > 1:
					sce.matPalette.remove(count)
			count += 1

	def execute(self, context):
		sce = context.scene
		ob = context.active_object

		material = bpy.data.materials.get(sce.selected_mat)
		mats = bpy.data.materials

		if material != None:
			newListItem = sce.matPalette.add()
			newListItem.matList = material.name

			self.remove_dups(context,
				sce,
				newListItem.matList)
		else:
			if ob.data.materials:
				newListItem = sce.matPalette.add()
				newListItem.matList = ob.active_material.name

				self.remove_dups(context,
					sce,
					newListItem.matList)

		return {'FINISHED'}

class MATERIAL_OT_assign_mat_palette(Operator):
	'''Assign material to selected faces or object'''
	bl_idname = "assign_mat.cuber"
	bl_label = "Assign Material To Faces"
	bl_options = {'REGISTER', 'UNDO'}

	this_mat : StringProperty("")

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		sce = context.scene
		ob = context.active_object
		mesh = ob.data

		if bpy.data.materials.get(self.this_mat):
			mat = bpy.data.materials[self.this_mat]

			if ob.type == "MESH":
				ob.data.materials.append(mat)

				index = ob.data.materials.find(mat.name)
				face_mat(ob, index)
				rem_mat(context, ob)

				new_idx = ob.data.materials.find(mat.name)
				ob.active_material_index = new_idx

			if ob.type == "CURVE":
				ob.data.materials.clear()
				ob.data.materials.append(mat)
		else:
			palette_list = sce.matPalette
			mat_idx = [i.matList for i in palette_list]

			for i in mat_idx:
				if not bpy.data.materials.get(i):
					palette_list.remove(mat_idx.index(i))
					mat_idx = [i.matList for i in palette_list]

			self.report({'WARNING'}, "Material not found! Removing from list...")

		return {'FINISHED'}

	def draw(self, context): None

class MATERIAL_OT_remove_mat_palette(Operator):
	'''Remove material from the list'''
	bl_idname = "remove_mat.cuber"
	bl_label = "Remove Material"
	bl_options = {'REGISTER', 'UNDO'}

	this_mat : StringProperty()

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		sce = context.scene
		palette_list = sce.matPalette
		mat_idx = [i.matList for i in palette_list]

		palette_list.remove(mat_idx.index(self.this_mat))

		return {'FINISHED'}

	def draw(self, context): None

class UI_PT_cuber(Panel):
	'''Modelling support functions'''
	bl_label = 'Cuber'
	bl_idname = 'Cuber_Main_Panel'
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Cuber'
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		sce = context.scene
		ob = context.active_object

		layout = self.layout

		col = layout.column(align=True)
		col.enabled = ob is not None
		col.operator("add_intrsct_faces.cuber", text="Add Intersect Faces", icon="MESH_CUBE")
		col.operator("cuber_symm.cuber", icon="AXIS_SIDE")
		row = col.row(align=True)
		row.operator("isolate_vgroup.cuber", text="Isolate", icon="RESTRICT_SELECT_ON")
		row.operator("select_vgroup.cuber", text="Highlight", icon="RESTRICT_SELECT_OFF")
		col.operator("cuber_vgroup_purge.cuber", text="Remove As Intersector", icon="GROUP_VERTEX")
		row = col.row(align=True)
		bool_op = row.operator("bool_intrsct_faces.cuber", text="Difference")
		bool_op.this_op = "DIFFERENCE"
		bool_op = row.operator("bool_intrsct_faces.cuber", text="Union")
		bool_op.this_op = "UNION"
		bool_op = row.operator("bool_intrsct_faces.cuber", text="Cut")
		bool_op.this_op = "CUT"
		bool_op = row.operator("bool_intrsct_faces.cuber", text="Slice")
		bool_op.this_op = "INTERSECT"
		col.menu("UI_MT_intersect_settings")
		colrow = col.row(align=True)
		colrow.operator("get_sharp.cuber", text="Get Sharp")
		colrow.operator("auto_smooth.cuber", text="Auto Smooth")
		colrow = col.row(align=True)
		colrow.operator("mark_sharp.cuber", text="Mark Sharp")
		colrow.operator("clear_sharp.cuber", text="Clear Sharp")

		colrow = col.row(align=True)
		if ob:
			ob_types = ob.type in ['MESH', 'CURVE']
			if ob_types:
				if ob.data.materials:
					mat = ob.active_material
					if mat:
						col.prop(mat, 'diffuse_color', text="")
						col.menu("UI_MT_material_viewport_settings")

		row = col.row().split(align=True)
		row.operator("add_mat.cuber", text="New Mat")
		row.operator("bake_vcol.cuber", text="To Vcol", icon="COLOR")
		row = col.row().split(align=True)
		row.operator("mat_to_list.cuber", text="To List")
		row.operator("vcol_mat.cuber", text="Vcol Mat", icon="VPAINT_HLT")

class UI_PT_draw_cutter(Panel):
	'''Cuber Poly Cutter'''
	bl_label = 'Draw Cutter'
	bl_idname = 'Cuber_Draw_Cutter'
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Cuber'
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		sce = context.scene
		ob = context.active_object

		layout = self.layout
		col = layout.column(align=True)

		if ob and ob.mode == 'OBJECT':
			draw_op = col.operator("draw_cutter.cuber", text="Draw Cut", icon="GREASEPENCIL")
			draw_op.cutter_op = "CUT"
			draw_op.cutter_met = sce.cutter_op_default
			draw_op = col.operator("draw_cutter.cuber", text="Draw Slice", icon="GREASEPENCIL")
			draw_op.cutter_op = "SLICE"
			draw_op.cutter_met = sce.cutter_op_default
		else:
			draw_op = col.operator("draw_cutter.cuber", text="Draw Cut (Knife)", icon="GREASEPENCIL")
			draw_op.cutter_op = "DRAW"
			draw_op.cutter_met = sce.cutter_op_default

		col.menu("UI_MT_draw_cutter_settings")
		col.prop(sce, "proxy_cutter_color", text="Cutter Color")

class UI_PT_bevels(Panel):
	'''Bevel weight manager'''
	bl_label = 'Bevels'
	bl_idname = 'Cuber_Bevels'
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Cuber'
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		ob = context.active_object
		sce = context.scene

		mod_nam = "Bevel"
		bweights = []
		props = context.scene.BevelPG
		vis_props = context.scene.ModVisPG
		lockList = [i.obdataList for i in sce.bweightlockList]

		layout = self.layout

		if ob:
			mod = ob.modifiers

		col = layout.column(align=True)
		colrow = col.row(align=True)
		colrow.label(text="Quick Assign")

		if ob and ob.name in lockList:
			colrow.operator("bweight_lock.cuber", text="", icon="LOCKED")
		else:
			colrow.operator("bweight_lock.cuber", text="", icon="UNLOCKED")

		colrow = col.row(align=True)
		colrow.operator("reuse_bevel.cuber", text="", icon="FILE_REFRESH")

		if props.use_angle:
			colrow.prop(props, "bevel_deg")
		else:
			colrow.prop(props, "bevel_weight")

		col.prop(props, "width")
		col.prop(props, "segments")
		col.prop(props, "profile")
		if ob:
			c_bvl = mod.get(mod_nam)
			if c_bvl:
				sync_settings = False

				if (props.width != c_bvl.width or
					props.segments != c_bvl.segments or
					props.profile != c_bvl.profile or
					props.use_clamp != c_bvl.use_clamp_overlap or
					props.use_slide != c_bvl.loop_slide or
					props.offset_type != c_bvl.offset_type or
					props.face_strength_mode != c_bvl.face_strength_mode or
					props.harden_normals != c_bvl.harden_normals):
					sync_settings = True

				if ((props.use_angle == True and c_bvl.limit_method == "WEIGHT") or
					(props.use_angle == False and c_bvl.limit_method == "ANGLE")): sync_settings = True

				if c_bvl.limit_method == "ANGLE":
					if props.bevel_deg != c_bvl.angle_limit: sync_settings = True

				if sync_settings:
					col.operator("copy_bevel.cuber", text="Synchronize Settings", icon="ERROR")

		colrow = col.row(align=True)
		colrow.menu("UI_MT_quick_assign_settings")

		if ob:
			col = layout.column(align=True)
			colrow = col.row(align=True)
			colrow.label(text="Quick Select")
			if ob and mod.get(mod_nam):
				colrow.prop(vis_props, "show_viewport", text="", icon="RESTRICT_VIEW_OFF")
				colrow.prop(vis_props, "show_in_editmode", text="", icon="EDITMODE_HLT")

			row = col.row(align=True)
			empty_box = " " * 8
			if ob.name == sce.obj_read:
				r = 0
				weightCol = 5
				for i in sce.bweightList:
					bevel_weight = float(i.bevelweightsList)
					r += 1
					w = '% 0.2f' % bevel_weight
					edge_sel = row.box().operator("quick_select.cuber", text=str(w), emboss=False)
					edge_sel.bweight_idx = bevel_weight
					if r == weightCol:
						row = col.row(align=True)
						r = 0

				empty_row = len(sce.bweightList)%weightCol
				fill_row = weightCol-empty_row

				if fill_row < weightCol or len(sce.bweightList) == 0:
					for r in range(fill_row):
						row.box().label(text=empty_box)
			else:
				for r in range(5):
					row.box().label(text=empty_box)

			col.operator("refresh_list.cuber", text="Update List For Active Object", icon="FILE_REFRESH")

			if mod.get(mod_nam):
				row = col.row(align=True)
				apply_bevl = row.operator("apply_bevel.cuber", text="Apply", icon="IMPORT")
				apply_bevl.action = "APPLY"
				remov_bvl = row.operator("apply_bevel.cuber", text="Remove", icon="X")
				remov_bvl.action = "REMOVE"

			col = layout.column(align=True)
			wn_mod = "Weighted Normal"
			if not mod.get(wn_mod):
				col.prop(sce, "weighted_segments")
				col.operator("add_weighted.cuber", text="Add Weighted Normal Modifier")
			else:
				mod_props = mod[wn_mod]
				col.label(text=wn_mod + ":")
				row = col.row(align=True)
				row.prop(mod_props, "mode", text="")
				row.prop_search(mod_props, "vertex_group", ob, "vertex_groups", text="")
				row.prop(mod_props, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')
				row = col.row(align=True)
				row.prop(mod_props, "weight")
				row.prop(mod_props, "thresh")
				row = col.row(align=True)
				row.prop(mod_props, "keep_sharp")
				row.prop(mod_props, "face_influence")

			col.separator()
			col.operator("bweight_lock_purge.cuber", text="Purge Locked Object List")

class UI_PT_mat_palette(Panel):
	'''Material Palette List'''
	bl_label = 'Material Palette'
	bl_idname = 'Material_Palette'
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'Cuber'
	bl_options = {'DEFAULT_CLOSED'}

	@classmethod
	def poll(cls, context):
		return len(bpy.data.materials) > 0

	def draw(self, context):
		sce = context.scene
		ob = context.active_object

		palette_list = sce.matPalette
		mat_idx = [i.matList for i in palette_list]

		layout = self.layout

		col = layout.column(align=True)
		colbox = col.box().column()

		if len(palette_list) == 0:
			colbox.label(text="Add A Material", icon="INFO")
		else:
			mat_order = sorted(mat_idx, reverse=sce.reverse_mat_pal) if sce.sort_mat_pal \
				else (reversed(mat_idx) if sce.reverse_mat_pal else mat_idx)
			for i in mat_order:
				mat = i

				has_col = False
				if bpy.data.materials.get(mat):
					view_col = bpy.data.materials[mat]
					mat_icon = view_col.preview.icon_id
					has_col = True

				space = 0.67
				boxrow = colbox.row(align=True)
				boxrow = boxrow.split(align=True, factor=space)
				if has_col:
					assign_mat = boxrow.operator("assign_mat.cuber", text=mat, icon_value=mat_icon, emboss=False)
				else:
					assign_mat = boxrow.operator("assign_mat.cuber", text=mat, icon="ERROR", emboss=False)
				assign_mat.this_mat = mat

				row = boxrow.split(align=True, factor=space)
				if has_col:
					view_col = bpy.data.materials[mat]
					row.prop(view_col, "diffuse_color", text="")
				else:
					row.prop(sce, "proxy_diff_picker", text="")

				rem_mat = row.operator("remove_mat.cuber", text="", icon="REMOVE", emboss=True)
				rem_mat.this_mat = i

		col.separator()
		row = col.row().split(align=True, factor=0.8)
		row.prop_search(
			sce,
			"selected_mat",
			bpy.data,
			"materials"
			)
		row.prop(sce, "sort_mat_pal", icon="SORTALPHA", icon_only=True)
		row.prop(sce, "reverse_mat_pal", icon="SORT_ASC", icon_only=True)
		col.operator("mat_to_list.cuber", text="Add Material To List")

class UI_MT_cuber(Menu):
	bl_label = "Cuber Operators"
	bl_idname = "Cuber_Pie_Menu"

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def draw(self, context):
		sce = context.scene
		ob = context.active_object

		props = context.scene.BevelPG
		vis_props = context.scene.ModVisPG
		lockList = [i.obdataList for i in sce.bweightlockList]

		mod = ob.modifiers
		mod_nam = "Bevel"

		layout = self.layout
		pie = layout.menu_pie()
		col = pie.column()

		max_button = " " * 10
		if ob.mode == "EDIT":
			col.operator("add_intrsct_faces.cuber", text="Add Intersect Faces", icon="MESH_CUBE")
			row = col.row().split(align=True, factor=0.5)
			row.operator("isolate_vgroup.cuber", text="Isolate", icon="RESTRICT_SELECT_ON")
			row.operator("select_vgroup.cuber", text="Highlight", icon="RESTRICT_SELECT_OFF")
			col.operator("cuber_vgroup_purge.cuber", text="Remove As Intersector", icon="GROUP_VERTEX")
			colrow = col.row().split(align=True, factor=0.5)
			colrow.operator("get_sharp.cuber", text="Get Sharp")
			colrow.operator("auto_smooth.cuber", text="Auto Smooth")
			colrow = col.row().split(align=True, factor=0.5)
			colrow.operator("mark_sharp.cuber", text="Mark Sharp")
			colrow.operator("clear_sharp.cuber", text="Clear Sharp")
			col.operator("cuber_symm.cuber", icon="AXIS_SIDE")
		else:
			colrow = col.row().split(align=True, factor=0.5)
			draw_op = colrow.operator("draw_cutter.cuber", text="Draw Cut" + (" " * 5), icon="GREASEPENCIL")
			draw_op.cutter_op = "CUT"
			draw_op.cutter_met = sce.cutter_op_default
			draw_op = colrow.operator("draw_cutter.cuber", text="Draw Slice" + (" " * 5), icon="GREASEPENCIL")
			draw_op.cutter_op = "SLICE"
			draw_op.cutter_met = sce.cutter_op_default
			col.menu("UI_MT_draw_cutter_settings", icon='RIGHTARROW')
			col.operator("cuber_symm.cuber", icon="AXIS_SIDE")

		col = pie.column()
		ob_types = ob.type in ['MESH', 'CURVE']
		if ob_types:
			if ob.data.materials:
				mat = ob.active_material
				if mat:
					colrow = col.row().split(align=True, factor=0.5)
					colrow.prop(mat, 'diffuse_color', text="")
					colrow.menu("UI_MT_material_viewport_settings", icon='RIGHTARROW')

		row = col.row().split(align=True, factor=0.5)
		row.operator("add_mat.cuber", text="New Mat" + (" " * 5))
		row.operator("bake_vcol.cuber", text="To Vcol" + (" " * 5), icon="COLOR")
		row = col.row().split(align=True, factor=0.5)
		row.operator("mat_to_list.cuber", text="To List" + (" " * 5))
		row.operator("vcol_mat.cuber", text="Vcol Mat" + (" " * 5), icon="VPAINT_HLT")
		col.operator("wm.call_menu_pie", text="Material Palette...").name="MatPalette_Pie_Menu"

		col = pie.column(align=True)
		if ob.mode == 'EDIT':
			row = col.row().split(align=True, factor=0.5)
			bool_op = row.operator("bool_intrsct_faces.cuber", text="Difference" + max_button)
			bool_op.this_op = "DIFFERENCE"
			bool_op = row.operator("bool_intrsct_faces.cuber", text="Union" + max_button)
			bool_op.this_op = "UNION"
			row = col.row().split(align=True, factor=0.5)
			bool_op = row.operator("bool_intrsct_faces.cuber", text="Cut")
			bool_op.this_op = "CUT"
			bool_op = row.operator("bool_intrsct_faces.cuber", text="Slice")
			bool_op.this_op = "INTERSECT"
			draw_op = col.operator("draw_cutter.cuber", text="Draw Cut (Knife)", icon="GREASEPENCIL")
			draw_op.cutter_op = "DRAW"
			draw_op.cutter_met = sce.cutter_op_default
			col.menu("UI_MT_intersect_settings", icon='RIGHTARROW')

		elif ob.mode == 'OBJECT':
			wn_mod = "Weighted Normal"
			if not mod.get(wn_mod):
				max = " " * 25
				col = col.column()
				col.prop(sce, "weighted_segments")
				col.operator("add_weighted.cuber", text="Add Weighted Normal Modifier" + max)
			else:
				mod_props_wn = mod[wn_mod]
				col.label(text=wn_mod + ":")
				row = col.row().split(align=True, factor=0.5)
				row.prop(mod_props_wn, "mode", text="")
				row_split = row.split(align=True, factor=0.9)
				row_split.prop_search(mod_props_wn, "vertex_group", ob, "vertex_groups", text="")
				row_split.prop(mod_props_wn, "invert_vertex_group", text="", icon='ARROW_LEFTRIGHT')
				row = col.row().split(align=True, factor=0.5)
				row.prop(mod_props_wn, "weight")
				row.prop(mod_props_wn, "thresh")
				row = col.row().split(align=True, factor=0.5)
				row.prop(mod_props_wn, "keep_sharp", emboss=False)
				row.prop(mod_props_wn, "face_influence", emboss=False)

		col = pie.column(align=True)
		colrow = col.row(align=True)
		colrow.label(text="Quick Assign")

		if ob.name in lockList:
			colrow.operator("bweight_lock.cuber", text="", icon="LOCKED")
		else:
			colrow.operator("bweight_lock.cuber", text="", icon="UNLOCKED")

		colrow = col.row(align=True)
		colrow.operator("reuse_bevel.cuber", text="", icon="FILE_REFRESH")

		if props.use_angle:
			colrow.prop(props, "bevel_deg")
		else:
			colrow.prop(props, "bevel_weight")

		col.prop(props, "width")
		col.prop(props, "segments")
		col.prop(props, "profile")

		c_bvl = mod.get(mod_nam)
		if c_bvl:
			sync_settings = False

			if (props.width != c_bvl.width or
				props.segments != c_bvl.segments or
				props.profile != c_bvl.profile or
				props.use_clamp != c_bvl.use_clamp_overlap or
				props.use_slide != c_bvl.loop_slide or
				props.offset_type != c_bvl.offset_type or
				props.face_strength_mode != c_bvl.face_strength_mode or
				props.harden_normals != c_bvl.harden_normals):
				sync_settings = True

			if ((props.use_angle == True and c_bvl.limit_method == "WEIGHT") or
				(props.use_angle == False and c_bvl.limit_method == "ANGLE")): sync_settings = True

			if c_bvl.limit_method == "ANGLE":
				if props.bevel_deg != c_bvl.angle_limit: sync_settings = True

			if sync_settings:
				col.operator("copy_bevel.cuber", text="Synchronize Settings", icon="ERROR")

		colrow = col.row()
		colrow.menu("UI_MT_quick_assign_settings", icon='RIGHTARROW')

		colrow = col.row(align=True)
		colrow.label(text="Quick Select")
		if mod.get(mod_nam):
			colrow.prop(vis_props, "show_viewport", text="", icon="RESTRICT_VIEW_OFF")
			colrow.prop(vis_props, "show_in_editmode", text="", icon="EDITMODE_HLT")

		row = col.row(align=True)
		empty_box = " " * 8
		if ob.name == sce.obj_read:
			r = 0
			weightCol = 5
			for i in sce.bweightList:
				bevel_weight = float(i.bevelweightsList)
				r += 1
				w = '% 0.2f' % bevel_weight
				edge_sel = row.box().operator("quick_select.cuber", text=str(w), emboss=False)
				edge_sel.bweight_idx = bevel_weight
				if r == weightCol:
					row = col.row(align=True)
					r = 0

			empty_row = len(sce.bweightList)%weightCol
			fill_row = weightCol-empty_row

			if fill_row < weightCol or len(sce.bweightList) == 0:
				for r in range(fill_row):
					row.box().label(text=empty_box)
		else:
			for r in range(5):
				row.box().label(text=empty_box)

		col.operator("refresh_list.cuber", text="Update List For Active Object", icon="FILE_REFRESH")

		if mod.get(mod_nam):
			row = col.row().split(align=True, factor=0.5)
			apply_bevl = row.operator("apply_bevel.cuber", text="Apply", icon="IMPORT")
			apply_bevl.action = "APPLY"
			remov_bvl = row.operator("apply_bevel.cuber", text="Remove", icon="X")
			remov_bvl.action = "REMOVE"

class UI_MT_mat_palette(Menu):
	bl_label = "Material Palette"
	bl_idname = "MatPalette_Pie_Menu"

	def draw(self, context):
		sce = context.scene
		ob = context.active_object

		palette_list = sce.matPalette
		mat_idx = [i.matList for i in palette_list]

		layout = self.layout
		pie = layout.menu_pie()

		col = pie.column()
		colbox = col.box().column()

		if len(palette_list) == 0:
			colbox.label(text="Add A Material", icon="INFO")
		else:
			mat_order = sorted(mat_idx, reverse=sce.reverse_mat_pal) if sce.sort_mat_pal \
				else (reversed(mat_idx) if sce.reverse_mat_pal else mat_idx)
			for i in mat_order:
				mat = i

				has_col = False
				if bpy.data.materials.get(mat):
					view_col = bpy.data.materials[mat]
					mat_icon = view_col.preview.icon_id
					has_col = True

				space = 0.67
				boxrow = colbox.row(align=True)
				boxrow = boxrow.split(align=True, factor=space)
				if has_col:
					assign_mat = boxrow.operator("assign_mat.cuber", text=mat, icon_value=mat_icon, emboss=False)
				else:
					assign_mat = boxrow.operator("assign_mat.cuber", text=mat, icon="ERROR", emboss=False)
				assign_mat.this_mat = mat

				row = boxrow.split(align=True, factor=space)
				if has_col:
					view_col = bpy.data.materials[mat]
					row.prop(view_col, "diffuse_color", text="")
				else:
					row.prop(sce, "proxy_diff_picker", text="")

				rem_mat = row.operator("remove_mat.cuber", text="", icon="REMOVE", emboss=True)
				rem_mat.this_mat = i

		col.separator()
		row = col.row().split(align=True, factor=0.8)
		row.prop_search(
			sce,
			"selected_mat",
			bpy.data,
			"materials"
			)
		row.prop(sce, "sort_mat_pal", icon="SORTALPHA", icon_only=True)
		row.prop(sce, "reverse_mat_pal", icon="SORT_ASC", icon_only=True)

class UI_MT_intersect_settings(Menu):
	bl_label = "Intersect Settings"

	def draw(self, context):
		sce = context.scene

		layout = self.layout

		layout.prop(sce, "angle_sharp")
		layout.prop(sce, "auto_sharp")
		layout.separator()
		view_sharp = context.space_data.overlay
		layout.prop(view_sharp, "show_edge_sharp", text="Draw Sharp")
		layout.prop(view_sharp, "show_edge_bevel_weight", text="Draw Weights")

class UI_MT_quick_assign_settings(Menu):
	bl_label = "Quick Assign Settings"

	def draw(self, context):
		props = context.scene.BevelPG

		layout = self.layout

		layout.prop_menu_enum(props, "offset_type")
		layout.prop(props, "use_clamp")
		layout.prop(props, "use_slide")
		layout.prop(props, "harden_normals")
		layout.separator()
		layout.prop(props, "use_angle")
		layout.prop_menu_enum(props, "face_strength_mode")
		layout.separator()
		layout.prop(props, "angle_sharp")
		layout.prop(props, "get_sharp")
		layout.separator()
		layout.prop(props, "push_bevel")
		layout.prop(props, "clear_bevel")

class UI_MT_draw_cutter_settings(Menu):
	bl_label = "Draw Cutter Settings"

	def draw(self, context):
		sce = context.scene

		layout = self.layout

		layout.prop(sce, "cutter_bevel_width")
		layout.prop(sce, "cutter_bevel_profile")
		layout.prop(sce, "cutter_bevel_segments")
		layout.prop(sce, "cutter_circle_segments")
		layout.prop(sce, "cutter_depth")
		layout.separator()
		layout.prop(sce, "cutter_incr_sensitivity")
		layout.prop(sce, "cutter_reset_param")
		layout.separator()
		layout.prop(sce, "cutter_autosmooth_angle")
		layout.prop(sce, "cutter_use_autosmooth")
		layout.separator()
		layout.prop_menu_enum(sce, "cutter_op_default")

class UI_MT_material_viewport_settings(Menu):
	bl_label = "Material Settings"

	def draw(self, context):
		ob = context.active_object

		layout = self.layout

		ob_types = ob.type == "MESH" or ob.type == "CURVE"
		if ob_types:
			if ob.data.materials:
				mat = ob.active_material
				if mat:
					layout.prop(mat, 'metallic')
					layout.prop(mat, 'specular_intensity')
					layout.prop(mat, 'roughness')
					layout.prop(mat, "use_nodes")

class ModVisPG(bpy.types.PropertyGroup):

	def update_viewport_Vis(self, context):
		''' Update function for bevel and wn modifier viewport visibility '''

		ob = context.active_object
		ob_mod = ob.modifiers

		c_bvl = ob_mod.get("Bevel")
		c_wn = ob_mod.get("Weighted Normal")

		if c_bvl:
			c_bvl.show_viewport = False if self.show_viewport else True

		if c_wn:
			c_wn.show_viewport = True if c_bvl.show_viewport else False

	def update_editmode_Vis(self, context):
		''' Update function for bevel and wn modifier editmode visibility '''

		ob = context.active_object
		ob_mod = ob.modifiers

		c_bvl = ob_mod.get("Bevel")
		c_wn = ob_mod.get("Weighted Normal")

		if c_bvl:
			c_bvl.show_in_editmode = False if self.show_in_editmode else True

		if c_wn:
			c_wn.show_in_editmode = True if c_bvl.show_in_editmode else False

	def get_viewport_vis(self):

		ob = bpy.context.active_object
		ob_mod = ob.modifiers

		viewport_vis = True if ob_mod["Bevel"].show_viewport else False

		return viewport_vis

	def get_editmode_vis(self):

		ob = bpy.context.active_object
		ob_mod = ob.modifiers

		editmode_vis = True if ob_mod["Bevel"].show_in_editmode else False

		return editmode_vis

	def set_viewport_vis(self, values):
		self.get_viewport_vis = values

	def set_editmode_vis(self, values):
		self.get_editmode_vis = values

	show_viewport : bpy.props.BoolProperty(
		description = "Display modifier in viewport",
		get         = get_viewport_vis,
		set         = set_viewport_vis,
		update      = update_viewport_Vis
	)
	show_in_editmode : bpy.props.BoolProperty(
		description = "Display modifier in Edit mode",
		get         = get_editmode_vis,
		set         = set_editmode_vis,
		update      = update_editmode_Vis
	)

class BevelPG(bpy.types.PropertyGroup):

	def update_Bevel(self, context):
		''' Update function for bevel properties '''

		if self.use_bevel:
			sce = context.scene
			ob = context.active_object

			mesh = ob.data
			mesh.use_customdata_edge_bevel = True
			lockList = [i.obdataList for i in sce.bweightlockList]

			if ob.name not in lockList:
				if not self.use_angle:
					if mesh.is_editmode:
						bm = bmesh.from_edit_mesh(mesh)
					else:
						bm = bmesh.new()
						bm.from_mesh(mesh)

					if not bm.edges.layers.bevel_weight:
						bm.edges.layers.bevel_weight.new()
					bevelWeightLayer = bm.edges.layers.bevel_weight['BevelWeight']

					edg_sel = [e for e in bm.edges if e.select]

					bvl_edg = []
					if self.get_sharp:
						for e in edg_sel:
							angle = e.calc_face_angle(None)
							if angle != None and \
								angle > self.angle_sharp:
								bvl_edg.append(e)
							else: e[bevelWeightLayer] = 0.0
					else: bvl_edg = edg_sel

					for e in bvl_edg:
						e[bevelWeightLayer] = self.bevel_weight

					read_bevel(context, bm, bevel_layer = bevelWeightLayer)

					if mesh.is_editmode:
						bmesh.update_edit_mesh(mesh)
					else:
						bm.to_mesh(mesh)
						mesh.update()

				add_bevel(self,
					context,
					self.use_angle,
					self.bevel_deg,
					self.width,
					self.segments,
					self.profile,
					self.use_clamp,
					self.use_slide,
					self.harden_normals,
					self.offset_type,
					self.face_strength_mode,
					self.push_bevel,
					self.clear_bevel)

	def clear_Select(self, context):
		''' Update function for bevel properties '''

		ob = context.active_object

		normalize_scale(context, ob)

		mesh = ob.data
		if mesh.is_editmode:
			bm = bmesh.from_edit_mesh(mesh)
		else:
			bm = bmesh.new()
			bm.from_mesh(mesh)

		geo = bm.verts[:] + bm.edges[:] + bm.faces[:]
		for p in geo: p.select = False

		if mesh.is_editmode:
			bmesh.update_edit_mesh(mesh)
		else:
			bm.to_mesh(mesh)
			mesh.update()

		self.update_Bevel(context)

	use_bevel : bpy.props.BoolProperty(
		default     = True,
	)
	use_clamp : bpy.props.BoolProperty(
		name        = "Clamp Overlap",
		description = "Clamp the width to avoid overlap",
		default     = False,
		update      = clear_Select
	)
	use_slide : bpy.props.BoolProperty(
		name        = "Loop Slide",
		description = "Prefer sliding along edges to having even widths",
		default     = True,
		update      = clear_Select
	)
	use_angle : bpy.props.BoolProperty(
		name        = "Use Angle Limit Method",
		description = "Use angle limit method if not use bevel weights",
		default     = True,
		update      = clear_Select
	)
	get_sharp : bpy.props.BoolProperty(
		name        = "Get Sharp",
		description = "Assign bevel weights to sharp edges only",
		default     = True,
	)
	push_bevel : bpy.props.BoolProperty(
		name        = "Make Bevel/Weighted Normal Modifier Latest",
		description = "Push bevel and weighted normal modifiers down the modifier stack",
		default     = True,
	)
	clear_bevel : bpy.props.BoolProperty(
		name        = "Remove Other Bevel Modifiers",
		description = "Remove other bevel modifiers",
		default     = True,
	)
	angle_sharp : bpy.props.FloatProperty(
		description = "Edge sharpness",
		name        = "Sharpness",
		default     = radians(30),
		min         = radians(1),
		max         = radians(180),
		step        = 10,
		precision   = 3,
		subtype     = "ANGLE"
		)
	bevel_weight : bpy.props.FloatProperty(
		description = "Bevel weight",
		name        = "Bevel Weight",
		default     = 0,
		min         = 0,
		max         = 1.0,
		step        = 0.1,
		precision   = 2,
		update      = update_Bevel
	)
	bevel_deg : FloatProperty(
		name        = "Angle",
		description = "Angle above which to bevel edges",
		default     = radians(30),
		min         = 0,
		max         = radians(180),
		step        = 10,
		precision   = 3,
		subtype     = "ANGLE",
		update      = update_Bevel
		)
	width : bpy.props.FloatProperty(
		description = "Bevel modifier width",
		name        = "Width",
		default     = 0.1,
		min         = 0,
		max         = 100,
		step        = 0.1,
		precision   = 4,
		update      = update_Bevel
	)
	segments : bpy.props.IntProperty(
		description = "Bevel modifier segments",
		name        = "Segments",
		default     = 6,
		min         = 1,
		max         = 100,
		step        = 1,
		update      = update_Bevel
		)
	profile : bpy.props.FloatProperty(
		description = "Bevel modifier profile",
		name        = "Profile",
		default     = 0.5,
		min         = 0,
		max         = 1,
		update      = update_Bevel
		)
	offset_type : bpy.props.EnumProperty(
		name 		= 'Width Method',
		description = "What distance Width measures",
		items 		= (
					('OFFSET', 'Offset',''),
					('WIDTH', 'Width',''),
					('DEPTH', 'Depth',''),
					('PERCENT', 'Percent','')),
					default = 'OFFSET',
		update      = update_Bevel
		)
	face_strength_mode : bpy.props.EnumProperty(
		name 		= 'Set Face Strength Mode',
		description = "Whether to set face strength, and which faces to set it on",
		items 		= (
					('FSTR_NONE', 'None',''),
					('FSTR_NEW', 'New',''),
					('FSTR_AFFECTED', 'Affected',''),
					('FSTR_ALL', 'All','')),
					default = 'FSTR_NONE',
		update      = update_Bevel
		)
	harden_normals : bpy.props.BoolProperty(
		name        = "Harden Normals",
		description = "Match normals of new faces to adjacent faces",
		default     = False,
		update      = update_Bevel
	)

class SETTINGS_OT_set_hotkey(Operator):
	'''Update hotkey settings'''
	bl_idname = "set_hotkey.cuber"
	bl_label = "Update Hotkey Settings"

	def execute(self, context):
		kc = context.window_manager.keyconfigs.addon

		ki = 0
		for ks in kc.keymaps.keys():
			for kp in kc.keymaps[ks].keymap_items.keys():
				try:
					if kc.keymaps[ks].keymap_items[ki].properties.name == "Cuber_Pie_Menu":
						kc.keymaps[ks].keymap_items.remove(kc.keymaps[ks].keymap_items[ki])
						kc.keymaps[ks].keymap_items[ki].active = False
				except: pass
				ki+=1

		addon_prefs = context.preferences.addons[__name__].preferences

		if kc:
			km = kc.keymaps.new(name='3D View', space_type='VIEW_3D', region_type='WINDOW')
			kmi = km.keymap_items.new('wm.call_menu_pie', addon_prefs.key, 'PRESS', ctrl=addon_prefs.ctrl, shift=addon_prefs.shift, alt=addon_prefs.alt)
			kmi.properties.name = 'Cuber_Pie_Menu'
			kmi.active = True
			addon_keymaps.append((km, kmi))

		return {"FINISHED"}

class UI_PT_cuber_addon_pref(AddonPreferences):
	bl_idname = __name__

	ctrl : bpy.props.BoolProperty(name="Ctrl", default=False)
	shift : bpy.props.BoolProperty(name="Shift", default=False)
	alt : bpy.props.BoolProperty(name="Alt", default=True)
	key : bpy.props.EnumProperty(
		items=(
			('A', "A", ""),
			('B', "B", ""),
			('C', "C", ""),
			('D', "D", ""),
			('E', "E", ""),
			('F', "F", ""),
			('G', "G", ""),
			('H', "H", ""),
			('I', "I", ""),
			('J', "J", ""),
			('K', "K", ""),
			('L', "L", ""),
			('M', "M", ""),
			('N', "N", ""),
			('O', "O", ""),
			('P', "P", ""),
			('Q', "Q", ""),
			('R', "R", ""),
			('S', "S", ""),
			('T', "T", ""),
			('U', "U", ""),
			('V', "V", ""),
			('W', "W", ""),
			('X', "X", ""),
			('Y', "Y", ""),
			('Z', "Z", "")
		),
		default='X', name = "Key",
	)

	def draw(self, context):
		layout = self.layout
		layout.label(text="Pie Menu Hotkey")
		row = layout.row(align=True)
		row.prop(self, "ctrl")
		row.prop(self, "shift")
		row.prop(self, "alt")
		row.prop(self, "key")
		layout.operator("set_hotkey.cuber", text="Update Hotkey")
		layout.label(text="Save User Preferences to keep changes.", icon="ERROR")

classes = (
	MESH_OT_fcol_to_vcol,
	MESH_OT_auto_smooth,
	MESH_OT_add_face_mat,
	MESH_OT_add_vcol_mat,
	MESH_OT_isolate_intersect_faces,
	MESH_OT_highlight_intersect_faces,
	MESH_OT_cuber_symm,
	MESH_OT_bool_intersect_faces,
	MESH_OT_add_intersect_faces,
	MESH_OT_get_weighted_edges,
	OBJECT_OT_copy_bevel_settings,
	OBJECT_OT_reuse_bevel,
	OBJECT_OT_refresh_list,
	OBJECT_OT_apply_bevel_modifier,
	OBJECT_OT_add_weighted_normal,
	MESH_OT_get_sharp,
	MESH_OT_mark_sharp,
	MESH_OT_clear_sharp,
	OBJECT_OT_bweight_lock,
	OBJECT_OT_bweight_lock_purge,
	MESH_OT_cuber_vgroup_purge,
	OBJECT_OT_cuber_draw_cutter,
	MATERIAL_OT_add_mat_palette,
	MATERIAL_OT_assign_mat_palette,
	MATERIAL_OT_remove_mat_palette,
	UI_PT_cuber,
	UI_PT_draw_cutter,
	UI_PT_bevels,
	UI_PT_mat_palette,
	UI_MT_cuber,
	UI_MT_mat_palette,
	UI_MT_intersect_settings,
	UI_MT_quick_assign_settings,
	UI_MT_draw_cutter_settings,
	UI_MT_material_viewport_settings,
	ModVisPG,
	BevelPG,
	SETTINGS_OT_set_hotkey,
	UI_PT_cuber_addon_pref,
	)
addon_keymaps = []

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.Scene.ModVisPG = bpy.props.PointerProperty( type = ModVisPG )
	bpy.types.Scene.BevelPG = bpy.props.PointerProperty( type = BevelPG )

	addon_prefs = bpy.context.preferences.addons[__name__].preferences

	kc = bpy.context.window_manager.keyconfigs.addon
	if kc:
		km = kc.keymaps.new(name='3D View', space_type='VIEW_3D', region_type='WINDOW')
		kmi = km.keymap_items.new('wm.call_menu_pie', addon_prefs.key, 'PRESS', ctrl=addon_prefs.ctrl, shift=addon_prefs.shift, alt=addon_prefs.alt)
		kmi.properties.name = 'Cuber_Pie_Menu'
		kmi.active = True
		addon_keymaps.append((km, kmi))

	bpy.types.Scene.cutter_op_default = bpy.props.EnumProperty(
		name 		= 'Default Cut Method',
		description = "Default method for draw cut/slice/draw",
		items = (
			('BOX', 'Box',''),
			('POLYGONAL', 'Polygonal',''),
			('CIRCLE', 'Circle','')),
		default = 'BOX')
	bpy.types.Scene.cutter_reset_param = bpy.props.BoolProperty(
		default     = True,
		name        = "Reset Parameters",
		description = "Resets cutter parameters to default"
		)
	bpy.types.Scene.cutter_use_autosmooth = bpy.props.BoolProperty(
		default     = True,
		name        = "Auto Smooth",
		description = "Auto smooth sliced objects"
		)
	bpy.types.Scene.cutter_autosmooth_angle = bpy.props.FloatProperty(
		name        = "Angle",
		description = "Auto smooth angle for sliced objects",
		default     = radians(30),
		min         = radians(1),
		max         = radians(180),
		step        = 10,
		precision   = 3,
		subtype     = "ANGLE"
		)
	bpy.types.Scene.cutter_bevel_width = bpy.props.FloatProperty(
		description = "Cutter corner verts bevel width",
		name        = "Width",
		default     = 0,
		min         = 0,
		max         = 100,
		step        = 0.1,
		precision   = 4
		)
	bpy.types.Scene.cutter_bevel_profile = bpy.props.FloatProperty(
		description = "Cutter corner verts bevel profile",
		name        = "Profile",
		default     = 0.5,
		min         = 0,
		max         = 1.0,
		step        = 0.1,
		precision   = 2
		)
	bpy.types.Scene.cutter_bevel_segments = bpy.props.IntProperty(
		description = "Cutter corner verts bevel segments",
		name        = "Segments",
		default     = 6,
		min         = 1,
		max         = 100,
		step        = 1
		)
	bpy.types.Scene.cutter_circle_segments = bpy.props.IntProperty(
		description = "Cutter circle segments",
		name        = "Circle Segments",
		default     = 32,
		min         = 3,
		max         = 500,
		step        = 1
		)
	bpy.types.Scene.cutter_depth = bpy.props.FloatProperty(
		description = "Cutter depth",
		name        = "Depth",
		default     = 2.0,
		min         = -100.0,
		max         = 100.0,
		step        = 0.1,
		precision   = 4
		)
	bpy.types.Scene.cutter_incr_sensitivity = bpy.props.FloatProperty(
		description = "Cutter depth numerical input increment sensitivity",
		name        = "Increment Sensitivity",
		default     = 1.0,
		min         = 0.001,
		max         = 1.0,
		step        = 0.1,
		precision   = 3
		)
	bpy.types.Scene.weighted_segments = bpy.props.IntProperty(
		description = "Weighted normals copy bevel segments",
		name        = "Use Bevel Segments",
		default     = 2,
		min         = 1,
		max         = 100,
		step        = 1
		)
	bpy.types.Scene.angle_sharp = bpy.props.FloatProperty(
		description = "Edge sharpness",
		name        = "Sharpness",
		default     = radians(30),
		min         = radians(1),
		max         = radians(180),
		step        = 10,
		precision   = 3,
		subtype     = "ANGLE"
		)
	bpy.types.Scene.auto_sharp = bpy.props.BoolProperty(
		default     = False,
		description = "Mark sharp edges after intersect",
		name        = "Auto Sharp"
		)
	bpy.types.Scene.obj_read = bpy.props.StringProperty()
	bpy.types.Scene.selected_mat = StringProperty(
		name        = "",
		description = "Add material to palette list",
		default     = "None"
		)
	bpy.types.Scene.sort_mat_pal = bpy.props.BoolProperty(
		default     = False,
		description = "Sort material palette list",
		)
	bpy.types.Scene.reverse_mat_pal = bpy.props.BoolProperty(
		default     = False,
		description = "Reverse material palette list",
		)
	bpy.types.Scene.proxy_diff_picker = bpy.props.FloatVectorProperty(
		subtype     = 'COLOR_GAMMA',
		default     = (0.0,0.0,0.0),
		min         = 0.0,
		max         = 1.0,
		description = "Diffuse color of the material"
		)
	bpy.types.Scene.proxy_cutter_color = bpy.props.FloatVectorProperty(
		subtype     = 'COLOR_GAMMA',
		default     = (0.0,1.0,0.0, 1.0),
		size		= 4,
		min         = 0.0,
		max         = 1.0,
		description = "Color of draw cutter"
		)

	class matpaletteGroup(bpy.types.PropertyGroup):
		matList : bpy.props.StringProperty()
	bpy.utils.register_class(matpaletteGroup)

	bpy.types.Scene.matPalette = bpy.props.CollectionProperty(type=matpaletteGroup)

	class bweightsGroup(bpy.types.PropertyGroup):
		bevelweightsList : bpy.props.StringProperty()
	bpy.utils.register_class(bweightsGroup)

	bpy.types.Scene.bweightList = bpy.props.CollectionProperty(type=bweightsGroup)

	class oblockedGroup(bpy.types.PropertyGroup):
		obdataList : bpy.props.StringProperty()
	bpy.utils.register_class(oblockedGroup)

	bpy.types.Scene.bweightlockList = bpy.props.CollectionProperty(type=oblockedGroup)

def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)

	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)

	addon_keymaps.clear()

	bpy.types.Scene.cutter_op_default = bpy.props.EnumProperty(
		name 		= 'Default Cut Method',
		description = "Default method for draw cut/slice/draw",
		items = (
			('BOX', 'Box',''),
			('POLYGONAL', 'Polygonal',''),
			('CIRCLE', 'Circle','')),
		default = 'BOX')
	bpy.types.Scene.cutter_reset_param = bpy.props.BoolProperty(
		default     = True,
		name        = "Reset Parameters",
		description = "Resets cutter parameters to default"
		)
	bpy.types.Scene.cutter_use_autosmooth = bpy.props.BoolProperty(
		default     = True,
		name        = "Auto Smooth",
		description = "Auto smooth sliced objects"
		)
	bpy.types.Scene.cutter_autosmooth_angle = bpy.props.FloatProperty(
		name        = "Angle",
		description = "Auto smooth angle for sliced objects",
		default     = radians(30),
		min         = radians(1),
		max         = radians(180),
		step        = 10,
		precision   = 3,
		subtype     = "ANGLE"
		)
	bpy.types.Scene.cutter_bevel_width = bpy.props.FloatProperty(
		description = "Cutter corner verts bevel width",
		name        = "Width",
		default     = 0,
		min         = 0,
		max         = 100,
		step        = 0.1,
		precision   = 4
		)
	bpy.types.Scene.cutter_bevel_profile = bpy.props.FloatProperty(
		description = "Cutter corner verts bevel profile",
		name        = "Profile",
		default     = 0.5,
		min         = 0,
		max         = 1.0,
		step        = 0.1,
		precision   = 2
		)
	bpy.types.Scene.cutter_bevel_segments = bpy.props.IntProperty(
		description = "Cutter corner verts bevel segments",
		name        = "Segments",
		default     = 6,
		min         = 1,
		max         = 100,
		step        = 1
		)
	bpy.types.Scene.cutter_circle_segments = bpy.props.IntProperty(
		description = "Cutter circle segments",
		name        = "Circle Segments",
		default     = 32,
		min         = 3,
		max         = 500,
		step        = 1
		)
	bpy.types.Scene.cutter_depth = bpy.props.FloatProperty(
		description = "Cutter depth",
		name        = "Depth",
		default     = 2.0,
		min         = -100.0,
		max         = 100.0,
		step        = 0.1,
		precision   = 4
		)
	bpy.types.Scene.cutter_incr_sensitivity = bpy.props.FloatProperty(
		description = "Cutter depth numerical input increment sensitivity",
		name        = "Increment Sensitivity",
		default     = 1.0,
		min         = 0.001,
		max         = 1.0,
		step        = 0.1,
		precision   = 3
		)
	bpy.types.Scene.weighted_segments = bpy.props.IntProperty(
		description = "Weighted normals copy bevel segments",
		name        = "Use Bevel Segments",
		default     = 2,
		min         = 1,
		max         = 100,
		step        = 1
		)
	bpy.types.Scene.angle_sharp = bpy.props.FloatProperty(
		description = "Edge sharpness",
		name        = "Sharpness",
		default     = radians(30),
		min         = radians(1),
		max         = radians(180),
		step        = 10,
		precision   = 3,
		subtype     = "ANGLE"
		)
	bpy.types.Scene.auto_sharp = bpy.props.BoolProperty(
		default     = False,
		description = "Mark sharp edges after intersect",
		name        = "Auto Sharp"
		)
	bpy.types.Scene.obj_read = bpy.props.StringProperty()
	bpy.types.Scene.selected_mat = StringProperty(
		name        = "",
		description = "Add material to palette list",
		default     = "None"
		)
	bpy.types.Scene.sort_mat_pal = bpy.props.BoolProperty(
		default     = False,
		description = "Sort material palette list",
		)
	bpy.types.Scene.reverse_mat_pal = bpy.props.BoolProperty(
		default     = False,
		description = "Reverse material palette list",
		)
	bpy.types.Scene.proxy_diff_picker = bpy.props.FloatVectorProperty(
		subtype     = 'COLOR_GAMMA',
		default     = (0.0,0.0,0.0),
		min         = 0.0,
		max         = 1.0,
		description = "Diffuse color of the material"
		)
	bpy.types.Scene.proxy_cutter_color = bpy.props.FloatVectorProperty(
		subtype     = 'COLOR_GAMMA',
		default     = (0.0,1.0,0.0, 1.0),
		size		= 4,
		min         = 0.0,
		max         = 1.0,
		description = "Color of draw cutter"
		)

	class matpaletteGroup(bpy.types.PropertyGroup):
		matList : bpy.props.StringProperty()
	bpy.utils.register_class(matpaletteGroup)

	bpy.types.Scene.matPalette = bpy.props.CollectionProperty(type=matpaletteGroup)

	class bweightsGroup(bpy.types.PropertyGroup):
		bevelweightsList : bpy.props.StringProperty()
	bpy.utils.register_class(bweightsGroup)

	bpy.types.Scene.bweightList = bpy.props.CollectionProperty(type=bweightsGroup)

	class oblockedGroup(bpy.types.PropertyGroup):
		obdataList : bpy.props.StringProperty()
	bpy.utils.register_class(oblockedGroup)

	bpy.types.Scene.bweightlockList = bpy.props.CollectionProperty(type=oblockedGroup)

if __name__ == '__main__':
	register()