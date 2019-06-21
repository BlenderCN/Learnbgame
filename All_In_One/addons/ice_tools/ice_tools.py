# ##### BEGIN LICENSE BLOCK #####
#
# Royalty Free License
#
# The Royalty Free license grants you, the purchaser, the ability to make use of the purchased
# product for personal, educational, or commercial purposes as long as those purposes do not
# violate any of the following:
#
#	You may not resell, redistribute, or repackage the purchased product without explicit
#	permission from the original author
#
#	You may not use the purchased product in a logo, watermark, or trademark of any kind
#
#	Exception: shader, material, and texture products are exempt from this rule. These products
#	are much the same as colors, and such are a secondary meaning and may be used as part of a
#	logo, watermark, or trademark.
#
# ##### END LICENSE BLOCK #####

bl_info = {
	'name': 'Ice Tools',
	'author': 'Ian Lloyd Dela Cruz',
	'version': (2, 76),
	'blender': (2, 7, 0),
	'location': '3d View > Tool shelf',
	'description': 'Retopology, hard surface modelling support addon',
	'warning': '',
	'wiki_url': '',
	'tracker_url': '',
	'category': 'Retopology'}

import bpy
import bmesh
from math import *
from mathutils import *
from bpy.props import *
from bpy.types import (
		Operator,
		Menu,
		Panel,
		)

def add_mod(context, mod, link, wrapmethod):
	
	ob = context.object
	
	md = ob.modifiers.new(mod, "SHRINKWRAP")
	md.target = bpy.data.objects[link]
	md.wrap_method = wrapmethod
	
	if md.wrap_method == "PROJECT":
		md.use_negative_direction = True
		
	if md.wrap_method == "NEAREST_SURFACEPOINT":
		md.use_keep_above_surface = True
		
	if "link_frozen" in ob.vertex_groups:
		md.vertex_group = "link_thawed"
		
	md.show_on_cage = True
	md.show_expanded = False

def addmat(context, obj, link):

	scn = context.scene	
	ob = context.object
	me = ob.data
	matnam = ob.name

	mat = bpy.data.materials.get(matnam)
	
	if mat is None:
		mat = bpy.data.materials.new(name=matnam)
		
	if me.materials:
		if len(me.materials) == 0:
			me.materials[0] = mat
	else:
		me.materials.append(mat)

	if ob.name != scn.link_target:
		try:
			bm = bmesh.new()
			bm.from_mesh(me)
			
			linkfaces = [f for f in bm.faces]
			for f in linkfaces: f.material_index = 0
			
			bm.to_mesh(me)
			bm.free()
		
		except: pass

	if link == True:
		try:
			target = bpy.data.objects[scn.link_target]
			if target.data.materials.find(matnam) == -1:
				target.data.materials.append(mat)
				
		except: pass

def autosmooth(context, angle):
	
	ob = context.object
	modeset = bpy.ops.object.mode_set    
	oldmode = ob.mode
		
	ob.data.use_auto_smooth = True
	ob.data.auto_smooth_angle = pi * 30 / 180
	
	modeset(mode="OBJECT")
	
	for poly in ob.data.polygons: poly.use_smooth = True
	modeset(mode=oldmode)

def coverttomesh(context):

	ob = context.object
	
	ob.data = ob.data.copy()
	bpy.ops.object.convert(target="MESH")

def addvgroup(context):

	ob = context.object

	ob.vertex_groups.clear()
	ob.vertex_groups.new(ob.name)

	vg = ob.vertex_groups.active
	verts = []
	
	for vert in ob.data.vertices:
		verts.append(vert.index)
		vg.add(verts, 0.0, "ADD")

def editpurge(context):

	scn = context.scene
	editObj = scn.link_edit

	if scn.objects.find(editObj) != -1:
		remObj = bpy.data.objects[editObj]
		scn.objects.unlink(remObj)
		bpy.data.objects.remove(remObj)

def switchview(context, mode):

	for area in context.screen.areas:
		if area.type == "VIEW_3D":
			area.spaces[0].region_3d.view_perspective = mode

def link_clipping(obj, autoclip, clipcenter):

	if "Mirror" in bpy.data.objects[obj].modifiers:
		obj = bpy.context.active_object
		bm = bmesh.from_edit_mesh(obj.data)
		vcount = 0
		EPSILON = 1.0e-3

		if clipcenter == True:
			EPSILON_sel = 1.0e-1
			for v in bm.verts:
				if -EPSILON_sel <= v.co.x <= EPSILON_sel:
					if v.select == True: v.co.x = 0
		else:
			if autoclip == True:
				bpy.ops.mesh.select_all(action="DESELECT")
				for v in bm.verts:
					if -EPSILON <= v.co.x <= EPSILON:
						v.select = True
						bm.select_history.add(v)
						v1 = v
						vcount += 1
					if vcount > 1:
						bpy.ops.mesh.select_axis(mode="ALIGNED")
						bpy.ops.mesh.loop_multi_select()
						for v in bm.verts:
							if v.select == True: v.co.x = 0
						break

def link_update(context, meshlink, wrapmethod, autoclip, clipcenter):

	ob = context.object
	oldmod = ob.mode
	selmod = context.tool_settings.mesh_select_mode
	mod = ob.modifiers
	modnam = "Shrinkwrap"
	

	if selmod[0] == True:
		oldSel = "VERT"
	if selmod[1] == True:
		oldSel = "EDGE"
	if selmod[2] == True:
		oldSel = "FACE"

	context.scene.objects.active = ob
	bpy.ops.object.mode_set(mode="EDIT")
	bpy.ops.mesh.select_mode(type="VERT")

	link_clipping(ob.name, autoclip, clipcenter)

	if mod.get(modnam):
		bpy.ops.object.modifier_remove(modifier= "Shrinkwrap")

	if "link_thawed" in ob.vertex_groups:
		tv = ob.vertex_groups["link_thawed"].index
		ob.vertex_groups.active_index = tv
		bpy.ops.object.vertex_group_remove(all=False)

	if "link_frozen" in ob.vertex_groups:
		fv =ob.vertex_groups["link_frozen"].index
		ob.vertex_groups.active_index = fv
		
		bpy.ops.mesh.select_all(action="SELECT")
		bpy.ops.object.vertex_group_deselect()
		bpy.ops.object.vertex_group_add()
		ob.vertex_groups.active.name = "link_thawed"
		bpy.ops.object.vertex_group_assign()

	add_mod(context, modnam, meshlink, wrapmethod)

	bpy.ops.object.mode_set(mode="OBJECT")
	bpy.ops.object.modifier_apply(apply_as="DATA", modifier=modnam)
	bpy.ops.object.mode_set(mode="EDIT")

	link_clipping(ob.name, autoclip, False)

	bpy.ops.mesh.select_all(action="DESELECT")
	bpy.ops.mesh.select_mode(type=oldSel)

	if "link_vgroup" in ob.vertex_groups:
		vg = ob.vertex_groups["link_vgroup"].index
		ob.vertex_groups.active_index = vg
		bpy.ops.object.vertex_group_select()
		bpy.ops.object.vertex_group_remove(all=False)

	bpy.ops.object.mode_set(mode=oldmod)

def addstencilmod(context):

	scn = context.scene
	ob = context.object

	addvgroup(context)

	md = ob.modifiers.new("Mirror", "MIRROR")
	md.show_on_cage = True
	md.use_clip = True
	md.use_x = scn.symm_x
	md.use_y = scn.symm_y
	md.use_z = scn.symm_z
	md.show_expanded = False
	md.show_viewport = scn.add_mirror
	md.show_render = scn.add_mirror

	md = ob.modifiers.new("Bevel Flat", "BEVEL")
	md.width = scn.bevel_width_flat
	md.segments = scn.bevel_segment_flat
	md.profile = scn.bevel_profile_flat
	md.limit_method = "WEIGHT"
	md.vertex_group = ob.vertex_groups.active.name
	md.use_only_vertices = True
	md.use_clamp_overlap = False
	md.show_expanded = False
	md.show_viewport = scn.add_bevel_flat
	md.show_render = scn.add_bevel_flat

	md = ob.modifiers.new("Solidify", "SOLIDIFY")
	md.thickness = scn.solid_thick
	md.offset = scn.solid_offset
	md.use_even_offset = True
	md.use_rim_only = scn.solid_rim_only
	md.show_expanded = False
	md.show_viewport = scn.add_solid
	md.show_render = scn.add_solid

	md = ob.modifiers.new("Bevel Solid", "BEVEL")
	md.width = scn.bevel_width_solid
	md.segments = scn.bevel_segment_solid
	md.profile = scn.bevel_profile_solid
	md.use_clamp_overlap = False
	md.limit_method = "ANGLE"
	md.angle_limit = scn.bevel_angle_solid
	md.show_expanded = False
	md.show_viewport = scn.add_bevel_sol
	md.show_render = scn.add_bevel_sol

class CreateLinkObject(Operator):
	'''Create link mesh on active object'''
	bl_idname = 'create_link.ice'
	bl_label = 'Create Link Mesh'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == "OBJECT"

	def execute(self, context):
		scn = context.scene
		oldOb = context.object

		if oldOb.name == scn.link_edit:
			self.report({"WARNING"}, "Cannot Use On Extract Copy!")
			return {"FINISHED"}

		if scn.link_use_mouse_depth == True:
			context.user_preferences.view.use_mouse_depth_cursor = True
		else:
			context.user_preferences.view.use_mouse_depth_cursor = False

		matcount = [m for m in oldOb.data.materials]

		if len(matcount) == 0:
			mat = bpy.data.materials.new(name=oldOb.name)
			oldOb.data.materials.append(mat)

		curloc = scn.cursor_location.copy()
		bpy.ops.view3d.snap_cursor_to_active()
		bpy.ops.mesh.primitive_plane_add(enter_editmode = True)

		bpy.ops.mesh.delete(type="VERT")
		bpy.ops.object.editmode_toggle()

		scn.link_target = oldOb.name
		bpy.data.objects[oldOb.name].select = False

		newOb = context.object

		for SelectedObject in context.selected_objects:
			if SelectedObject != newOb:
				SelectedObject.select = False

		newOb.select = True

		addstencilmod(context)

		scn.tool_settings.grease_pencil_source = "OBJECT"
		
		if newOb.grease_pencil is None: bpy.ops.gpencil.data_add()
		
		if newOb.grease_pencil.layers.active is None: bpy.ops.gpencil.layer_add()

		try:
			context.scene.tool_settings.gpencil_stroke_placement_view3d = "SURFACE"
			context.object.grease_pencil.layers.active.line_change= 1
			context.object.grease_pencil.layers.active.show_x_ray = True
			context.object.grease_pencil.layers.active.use_onion_skinning = False
			ontext.object.grease_pencil.layers.active.use_volumetric_strokes = False
			context.object.grease_pencil.layers.active.use_onion_skinning = False
		except: pass
		
		bpy.ops.object.editmode_toggle()

		if scn.link_use_surface_snap == True:
			scn.tool_settings.use_snap = True
			scn.tool_settings.snap_element = "FACE"
			scn.tool_settings.snap_target = "CLOSEST"
			scn.tool_settings.use_snap_project = True
		else:
			if scn.tool_settings.snap_element == "FACE":
				scn.tool_settings.use_snap = False

		context.object.show_all_edges = True
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="VERT")

		scn.cursor_location = curloc
		scn.link_col = 0
		
		return {'FINISHED'}

class ApplyShrinkwrap(Operator):
	'''Apply shrinkwrap modifier using target object'''
	bl_idname = 'apply_shrinkwrap.ice'
	bl_label = 'Apply Shrinkwrap'
	bl_options = {'REGISTER', 'UNDO'}

	link_autoclip = bpy.props.BoolProperty(name = "Auto-Clip (X)", default = True)
	link_clipcenter = bpy.props.BoolProperty(name = "Clip Selected Verts (X)", default = False)
	link_wrapmethod = bpy.props.EnumProperty(
		name = 'Wrap Method',
		items = (
			('NEAREST_VERTEX', 'Nearest Vertex',''),
			('PROJECT', 'Project',''),
			('NEAREST_SURFACEPOINT', 'Nearest Surface Point','')),
		default = 'PROJECT')

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		scn = context.scene
		ob = context.object

		if  scn.objects.find(scn.link_target) == -1:
			self.report({"WARNING"}, "Set Target First!")
			return {"FINISHED"}
		else:
			if  ob.name == scn.link_target or ob.name == scn.link_edit:
				self.report({"WARNING"}, "Select Non-Target Meshes!")
				return {"FINISHED"}
			else:
				if ob.mode == "EDIT":
					bpy.ops.object.vertex_group_add()
					bpy.data.objects[ob.name].vertex_groups.active.name = "link_vgroup"
					bpy.ops.object.vertex_group_assign()

				link_update(context, scn.link_target, self.link_wrapmethod, self.link_autoclip, self.link_clipcenter)
				ob.select = True

		return {'FINISHED'}

class FreezeVerts(Operator):
	'''Immunize verts on shrinkwrap update'''
	bl_idname = 'freeze_verts.ice'
	bl_label = 'Freeze Verts'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == "EDIT"

	def execute(self, context):
		ob = context.object

		if "link_frozen" in ob.vertex_groups:
			fv = ob.vertex_groups["link_frozen"].index
			ob.vertex_groups.active_index = fv
			bpy.ops.object.vertex_group_assign()
		else:
			bpy.ops.object.vertex_group_add()
			ob.vertex_groups.active.name = "link_frozen"
			bpy.ops.object.vertex_group_assign()

		return {"FINISHED"}

class ThawFrozenVerts(Operator):
	'''Remove frozen verts'''
	bl_idname = 'thaw_frozen_verts.ice'
	bl_label = 'Thaw Frozen Verts'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == "EDIT"

	def execute(self, context):
		ob = context.object

		if "link_frozen" in ob.vertex_groups:
			tv = ob.vertex_groups["link_frozen"].index
			ob.vertex_groups.active_index = tv
			bpy.ops.object.vertex_group_remove_from()

		return {"FINISHED"}

class ShowFrozenVerts(Operator):
	'''Show frozen verts'''
	bl_idname = 'show_freeze_verts.ice'
	bl_label = 'Show Frozen Verts'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == "EDIT"

	def execute(self, context):
		ob = context.object

		if "link_frozen" in ob.vertex_groups:
			bpy.ops.mesh.select_mode(type="VERT")
			fv = ob.vertex_groups["link_frozen"].index
			ob.vertex_groups.active_index = fv
			bpy.ops.mesh.select_all(action="DESELECT")
			bpy.ops.object.vertex_group_select()

		return {"FINISHED"}

class HideBooleans(Operator):
	'''Hide/show all boolean objects'''
	bl_idname = 'bool_hide.ice'
	bl_label = 'Hides Boolean Objects'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == "OBJECT"

	def execute(self, context):
		ob = context.object
		scn = context.scene
		target = scn.link_target
		mod = ob.modifiers
		
		hidcount = 0
		viscount = 0

		for obj in context.selected_objects: obj.select = False

		for m in mod:
			if m.type == "BOOLEAN":
				if bpy.data.objects[m.object.name].hide == False:
					viscount += 1
				else:
					hidcount += 1

			if viscount > hidcount:
				vismode = True
			else:
				vismode = False

		for m in mod:
			if m.type == "BOOLEAN":
				bpy.data.objects[m.object.name].hide = vismode

		return {"FINISHED"}

class LinkBool(Operator):
	'''Perform boolean operation on target object'''
	bl_idname = 'link_bool.ice'
	bl_label = 'Link Boolean Operation'
	bl_options = {'REGISTER', 'UNDO'}

	angle = IntProperty(default=30, min=0, max=180)
	mode = StringProperty("")

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		scn = context.scene
		ob = context.object
		oldmode = ob.mode
		target = scn.link_target

		mesh = ob.data

		if mesh.is_editmode:
			bm = bmesh.from_edit_mesh(mesh)
		else:
			bm = bmesh.new()
			bm.from_mesh(mesh)            
			
		fcount = [f for f in bm.faces]
		
		if mesh.is_editmode:
			bmesh.update_edit_mesh(mesh)
		else:
			bm.to_mesh(mesh)
			mesh.update()         

		if  scn.objects.find(scn.link_target) == -1:
			self.report({"WARNING"}, "Set Target First!")
			return {"FINISHED"}
		elif len(fcount) == 0:
			self.report({"WARNING"}, "No Face(s) Detected!")
			return {"FINISHED"}            
		else:
			targetmod = bpy.data.objects[target].modifiers
			for mod in targetmod:
				if mod.type == "BOOLEAN":
					if mod.object == None:
						bpy.data.objects[target].modifiers.remove(mod)
					elif ob.name == mod.object.name:
							self.report({"WARNING"}, "Object Already Used for Boolean!")
							return {"FINISHED"}

		addmat(context, ob, True)
		scn.objects[ob.name].draw_type = "BOUNDS"
		scn.objects[ob.name].hide_render = True
		cyclesVis = scn.objects[ob.name].cycles_visibility

		cyclesVis.camera = False
		cyclesVis.diffuse = False
		cyclesVis.glossy = False
		cyclesVis.shadow = False
		cyclesVis.transmission = False

		sliceOp = bpy.data.objects[target].modifiers.new(ob.name, "BOOLEAN")
		sliceOp.object = bpy.data.objects[ob.name]
		sliceOp.operation = self.mode
		sliceOp.show_expanded = False

		autosmooth(context, self.angle)

		if ob.mode == "EDIT": bpy.ops.object.editmode_toggle()

		return {"FINISHED"}

	def draw(self, context):
		 layout = self.layout
		 layout.prop(self,"angle", "Auto Smooth Angle")

class SetTarget(Operator):
	'''Set/unset selected as target object'''
	bl_idname = 'set_target.ice'
	bl_label = 'SET TARGET'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == "OBJECT"

	def execute(self, context):
		scn = context.scene
		ob = context.object
		target = scn.link_target
		editObj = scn.link_edit
		matnam = ob.name

		if ob.name == editObj:
			self.report({"WARNING"}, "Cannot Use On Extract Copy!")
			return {"FINISHED"}

		if ob.name != target:
			if ob.name != editObj:
				try:
					bpy.data.objects[target].hide = False
				except: pass
				editpurge(context)

			scn.link_target = ob.name
			scn.link_edit = ""
			scn.link_col = 0
			addmat(context, ob, False)
		else:
			scn.link_target = ""

		return {"FINISHED"}

class MatToVcol(Operator):
	'''Assign viewport material color as vertex color'''
	bl_idname = 'assign_vcol.ice'
	bl_label = 'Use Material Color As Vcol'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == "VERTEX_PAINT"

	def execute(self, context):
		scn = context.scene
		obj = context.active_object
		mesh = obj.data

		index = 0
		for m in obj.data.materials:
			context.object.active_material_index = index
			mat_c1 = bpy.data.materials[m.name]

			bm = bmesh.new()
			bm.from_mesh(obj.data)

			for face in bm.faces:
				if face.material_index == index:
					face.select = True
				else:
					face.select = False

			bm.to_mesh(obj.data)
			bm.free()

			if not mesh.vertex_colors:
				mesh.vertex_colors.new()

			color_layer = mesh.vertex_colors.active

			faces = [f.index for f in mesh.polygons if f.select]
			i = 0
			for poly in mesh.polygons:
				face_is_selected = poly.index in faces
				for idx in poly.loop_indices:
					if face_is_selected:
						rgb = context.object.active_material.diffuse_color
						color_layer.data[i].color = rgb
					i += 1
			index += 1

		return {'FINISHED'}

class IsolateView(Operator):
	'''Show only target object'''
	bl_idname = 'isolate_view.ice'
	bl_label = 'Isolate View'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == "OBJECT"

	def execute(self, context):
		scn = context.scene
		target = scn.link_target

		editpurge(context)
		for obj in context.selected_objects: obj.select = False
		
		if scn.objects.get(target):
			bpy.data.objects[target].select = True
			bpy.data.objects[target].hide = False   
			scn.objects.active = bpy.data.objects[target]

			ob = context.object
			for m in ob.modifiers:
				if m.type == "BOOLEAN":
					bpy.data.objects[m.object.name].hide = True
				
		else:
			self.report({"WARNING"}, "Set Target First!")
			return {"FINISHED"}
			
		return {"FINISHED"}

class UseAutoSmooth(Operator):
	'''Smooth shade active object and use auto-smooth'''
	bl_idname = 'use_auto_smooth.ice'
	bl_label = 'Use Auto Smooth'
	bl_options = {'REGISTER', 'UNDO'}

	angle = IntProperty(default=30, min=0, max=180, name="Angle")

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		autosmooth(context, self.angle)

		return {"FINISHED"}

class CopyModifierSettings(Operator):
	'''Copy mirror and solidify modifier settings'''
	bl_idname = 'copy_mod_settings.ice'
	bl_label = ''

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		scn = context.scene
		ob = context.object
		mod = ob.modifiers

		for m in mod:
			if m.name == "Mirror":
				scn.symm_x = m.use_x
				scn.symm_y = m.use_y
				scn.symm_z = m.use_z
				scn.add_mirror = m.show_viewport

			if m.name == "Bevel Flat":
				scn.bevel_width_flat = m.width
				scn.bevel_segment_flat = m.segments
				scn.bevel_profile_flat = m.profile
				scn.add_bevel_flat = m.show_viewport

			if m.name == "Solidify":
				scn.solid_thick = m.thickness
				scn.solid_offset = m.offset
				scn.solid_rim_only = m.use_rim_only
				scn.add_solid = m.show_viewport

			if m.name == "Bevel Solid":
				scn.bevel_width_solid = m.width
				scn.bevel_segment_solid = m.segments
				scn.bevel_profile_solid = m.profile
				scn.bevel_angle_solid = m.angle_limit
				scn.add_bevel_sol = m.show_viewport

		self.report({"INFO"}, "Modifier Settings Copied!")

		return {"FINISHED"}

class SimplePlane(Operator):
	'''Generate plane primitive based on 3d cursor position'''
	bl_idname = 'simple_plane.ice'
	bl_label = 'Simple Plane'
	bl_options = {'REGISTER', 'UNDO'}

	type = bpy.props.EnumProperty(
		name = 'Type',
		items = (
			('Tri', 'Tri',''),
			('Quad', 'Quad',''),
			('Hex', 'Hex','')),
		default = 'Quad')
	fac = FloatProperty(default=0.1, min=0.001, max=1, name='Radius')
	alignto = bpy.props.EnumProperty(
		name = 'Axis',
		items = (
			('X', 'X',''),
			('Y', 'Y',''),
			('Z', 'Z',''),
			('View', 'View','')),
		default = 'X')

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == "EDIT"

	def execute(self, context):
		ob = context.object
		angle = pi * 90 / 180

		bpy.ops.mesh.select_all(action="DESELECT")

		if self.alignto == "X": rotaxis = [angle,0,0]
		if self.alignto == "Y": rotaxis = [0,angle,0]
		if self.alignto == "Z": rotaxis = [0,0,angle]
		if self.type == "Tri": vcount = 3
		if self.type == "Hex": vcount = 6

		if self.alignto == "View":
			if self.type == "Quad":
				bpy.ops.mesh.primitive_plane_add(radius=self.fac, view_align=True)
			else:
				bpy.ops.mesh.primitive_circle_add(vertices=vcount, radius=self.fac, fill_type="NGON", view_align=True)
			return {"FINISHED"}
		else:
			if self.type == "Quad":
				bpy.ops.mesh.primitive_plane_add(radius=self.fac, rotation=rotaxis)
			else:
				bpy.ops.mesh.primitive_circle_add(vertices=vcount, radius=self.fac, fill_type="NGON", rotation=rotaxis)

		return {"FINISHED"}

	def draw(self, context):
		 layout = self.layout
		 col = layout.column()
		 col.row().prop(self,"type",expand=True)
		 col.row().prop(self,"alignto",expand=True)
		 col.prop(self,"fac")

	def invoke(self, context, event):
		return context.window_manager.invoke_props_popup(self, event)

class ToggleEditMode(Operator):
	'''Extract faces from finished version of target object'''
	bl_idname = 'toggle_edit.ice'
	bl_label = 'Toggle Edit Mode'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == "OBJECT"

	def execute(self, context):
		scn = context.scene
		ob = context.object
		target = scn.link_target
		mod = ob.modifiers

		if scn.link_target == ob.name:
			bpy.ops.object.select_all(action="DESELECT")
			bpy.data.objects[target].select = True

			for m in mod:
				if m.type == "BOOLEAN":
					bpy.data.objects[m.object.name].hide = True

			bpy.ops.object.duplicate()
			bpy.data.objects[target].hide = True
			scn.link_edit = context.active_object.name
			coverttomesh(context)
			bpy.ops.object.editmode_toggle()
			bpy.ops.mesh.select_all(action="DESELECT")
		else:
			if scn.link_edit == ob.name:
				if scn.objects.find(target) == -1:
					self.report({"WARNING"}, "Target Not Found!")
					return {"FINISHED"}
				else:
					for obj in context.selected_objects:
						if obj != ob:
							obj.select = False
							
					ob.select = True
					bpy.ops.object.delete()
					bpy.data.objects[target].hide = False
					bpy.data.objects[target].select = True
					scn.objects.active = bpy.data.objects[scn.link_target]
					scn.link_edit = ""

		return {'FINISHED'}

class ExtractFaces(Operator):
	'''Extract faces and show target object'''
	bl_idname = 'extract_faces.ice'
	bl_label = 'Extract Faces'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		scn = context.scene
		ob = context.object
		target = scn.link_target
		mod = ob.modifiers
		
		bm = bmesh.from_edit_mesh(ob.data)
		fcount = 0

		if scn.objects.find(target) == -1:
			self.report({"WARNING"}, "Set Target First!")
			return {"FINISHED"}
		else:
			for f in bm.faces:
				if f.select == True: fcount += 1

			if fcount == 0:
				self.report({"WARNING"}, "No Faces Selected!")
				return {"FINISHED"}
			else:
				bpy.ops.mesh.separate()
				bpy.ops.object.editmode_toggle()

			purge = ob
			
			if len(context.selected_objects) == 2:
				for obj in context.selected_objects:
					if obj == ob:
						obj.select = False
					else:
						obj.select = True
						scn.objects.active = bpy.data.objects[obj.name]
						obj.data.materials.clear()
						addmat(context, obj, False)
						addstencilmod(context)
						
						for m in mod:
							if m.type == "BOOLEAN":
								bpy.data.objects[mod.object.name].hide = True
								
						bpy.data.objects[target].hide = False
						bpy.data.objects[target].select = False
						
			context.scene.objects.unlink(purge)
			bpy.data.objects.remove(purge)
			scn.link_edit = ""

		return {'FINISHED'}

class ApplyAll(Operator):
	'''Apply all boolean modifiers in target object'''
	bl_idname = 'apply_all.ice'
	bl_label = 'Apply Boolean Links'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == "OBJECT"

	def execute(self, context):
		scn = context.scene
		ob = context.object
		target = context.scene.link_target
		mod = ob.modifiers
		
		fcount = 0
		scount = 0
		listmat = []

		if scn.link_target == ob.name:
			for m in mod:
				if m.type == "BOOLEAN": fcount += 1

			bpy.ops.object.select_all(action="DESELECT")
			bpy.data.objects[target].select = True
			scn.objects.active = bpy.data.objects[scn.link_target]

			for m in mod:
				if m.type == "BOOLEAN":
					if floor(fcount*(scn.apply_perc/100)) == 0: break
					
					if scount == floor(fcount*(scn.apply_perc/100)):
						break
					else:
						listmat = listmat + [m.object.name]
						bpy.ops.object.modifier_apply(modifier=m.name)
						remObj = bpy.data.objects[m.object.name]
						context.scene.objects.unlink(remObj)
						bpy.data.objects.remove(remObj)
						scount += 1

			bpy.data.objects[target].select = True
			scn.objects.active = bpy.data.objects[scn.link_target]

			ob = context.object
			
			if scn.apply_perc == 100:
				mat_slots = {}
				
				for p in ob.data.polygons:
					mat_slots[p.material_index] = 1

				mat_slots = mat_slots.keys()

				for i in reversed(range(len(ob.material_slots))):
					if i not in mat_slots:
						bpy.context.scene.objects.active = ob
						ob.active_material_index = i
						bpy.ops.object.material_slot_remove()

				count = 0
				
				for mat in ob.data.materials:
					if mat.name != target:
						count += 1
						mat.name = target + " link mesh " + str(count)
			else:
				for obj in listmat:
					for mat in ob.data.materials:
						if mat.name == obj:
							mat.name = mat.name + " link mesh"

		mesh = ob.data

		bm = bmesh.new()
		bm.from_mesh(mesh)            
			
		bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0)
		
		bm.to_mesh(mesh)
		mesh.update()

		return {'FINISHED'}

class ViewByPerc(Operator):
	'''View boolean modifiers by percentage'''
	bl_idname = 'view_by_perc.ice'
	bl_label = 'View Boolean By Percentage'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == "OBJECT"

	def execute(self, context):
		scn = context.scene
		ob = context.object
		target = context.scene.link_target
		mod = ob.modifiers
		
		fcount = 0
		scount = 0
		vcount = 0

		if scn.link_target == ob.name:
			for obj in mod:
				if obj.type == "BOOLEAN": fcount += 1
				if mod[obj.name].show_viewport == False: vcount += 1

			bpy.ops.object.select_all(action="DESELECT")
			bpy.data.objects[target].select = True
			scn.objects.active = bpy.data.objects[scn.link_target]

			if vcount > 0:
				for obj in mod:
					mod[obj.name].show_viewport = True
					mod[obj.name].show_render = True
			else:
				rev = 100-scn.apply_perc
				for obj in reversed(mod):
					if obj.type == "BOOLEAN":
						if ceil(fcount*(rev/100)) == 0: break
						if scount == ceil(fcount*(rev/100)):
							break
						else:
							mod[obj.name].show_viewport = False
							mod[obj.name].show_render = False
							scount += 1

		return {'FINISHED'}

class AssignToVgroup(Operator):
	'''Assign the selected verts to the active vertex group'''
	bl_idname = 'assign_to_vgroup.ice'
	bl_label = ''

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == "EDIT"

	def execute(self, context):
		ob = context.object

		ob.modifiers["Bevel Flat"].limit_method = "VGROUP"
		bpy.ops.object.vertex_group_assign()

		return {"FINISHED"}

class FindLink(Operator):
	'''Find the boolean modifier object'''
	bl_idname = 'find_link.ice'
	bl_label = ''

	obj = StringProperty("")

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		scn = context.scene

		for ob in bpy.context.scene.objects:
			if (ob.name == self.obj):
				bpy.ops.object.select_all(action="TOGGLE")
				bpy.ops.object.select_all(action="DESELECT")
				bpy.context.scene.objects.active = ob
				ob.select = True
				ob.hide = False
				
		return {"FINISHED"}

class EnableLink(Operator):
	'''Enable/disable the boolean modifier'''
	bl_idname = 'enable_link.ice'
	bl_label = ''

	thisObj = StringProperty("")

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		scn = context.scene
		ob = context.object

		for mod in ob.modifiers:
			if mod.type == "BOOLEAN":
				if mod.object.name == self.thisObj:
					if mod.show_viewport == True:
						mod.show_viewport = False
						mod.show_render = False
					else:
						mod.show_viewport = True
						mod.show_render = True

		return {"FINISHED"}

class ChangeOp(Operator):
	'''Change the boolean modifier operation'''
	bl_idname = 'change_op.ice'
	bl_label = ''

	linkObj = StringProperty("")

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		scn = context.scene
		ob = context.object

		for mod in ob.modifiers:
			if mod.type == "BOOLEAN":
				if mod.object.name == self.linkObj:
					if mod.operation == "DIFFERENCE":
						mod.operation = "UNION"
					else:
						mod.operation = "DIFFERENCE"

		return {"FINISHED"}

class PushToTop(Operator):
	'''Push the boolean modifier to top of the list'''
	bl_idname = 'push_to_top.ice'
	bl_label = ''

	pushMod = StringProperty("")

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		scn = context.scene
		ob = context.object

		modcount = 0
		movcount = 0
		for mod in ob.modifiers:
			modcount += 1
			if mod.name == self.pushMod: break

		while movcount < (modcount-1):
			movcount += 1
			bpy.ops.object.modifier_move_up(modifier=self.pushMod)

		return {"FINISHED"}

class ClearOp(Operator):
	'''Removes the boolean modifier'''
	bl_idname = 'clear_op.ice'
	bl_label = ''

	remObj = StringProperty("")

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		scn = context.scene
		ob = context.object

		for mod in ob.modifiers:
			if mod.type == "BOOLEAN":
				if mod.object.name == self.remObj:
					ob.modifiers.remove(mod)

					obdata = bpy.data.objects[self.remObj]
					obdata.draw_type = "TEXTURED"
					obdata.hide = False
					obdata.hide_render = False
					cyclesVis = obdata.cycles_visibility

					cyclesVis.camera = True
					cyclesVis.diffuse = True
					cyclesVis.glossy = True
					cyclesVis.shadow = True
					cyclesVis.transmission = True

		return {"FINISHED"}

class GetMod(Operator):
	'''Show modifier settings'''
	bl_idname = 'get_mod.ice'
	bl_label = ''

	thisMod = StringProperty("")

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		scn = context.scene

		scn.mod_vis = self.thisMod

		return {"FINISHED"}

class EnableMod(Operator):
	'''Enable/disable modifier'''
	bl_idname = 'enable_mod.ice'
	bl_label = ''

	objMod = StringProperty("")

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		scn = context.scene
		ob = context.object

		for mod in ob.modifiers:
			if mod.name == self.objMod:
				if mod.show_viewport == True:
					mod.show_viewport = False
					mod.show_render = False
				else:
					mod.show_viewport = True
					mod.show_render = True

		return {"FINISHED"}

class GhostKnife(Operator):
	'''Enable ghost knife'''
	bl_idname = 'gknife.ice'
	bl_label = 'Ghost Knife'

	count = 0
	oldview = ""
	oldshade = ""

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == "EDIT"

	def modal(self, context, event):
		scn = context.scene
		self.count += 1
		actObj = context.active_object
		
		if self.count == 1:
			switchview(context, "ORTHO")
			context.space_data.viewport_shade = "WIREFRAME"
			bpy.ops.mesh.knife_tool("INVOKE_DEFAULT", use_occlude_geometry=False, only_selected=False)

		if event.type == "SPACE":
			switchview(context, self.oldview)
			context.space_data.viewport_shade = self.oldshade
			return {"FINISHED"}

		if event.type in {"RIGHTMOUSE", "ESC"}:
			switchview(context, self.oldview)
			context.space_data.viewport_shade = self.oldshade
			return {"CANCELLED"}

		return {"RUNNING_MODAL"}

	def invoke(self, context, event):
		for area in bpy.context.screen.areas:
			if area.type == "VIEW_3D":
				self.oldview = area.spaces[0].region_3d.view_perspective
				
		self.oldshade = bpy.context.space_data.viewport_shade
		context.window_manager.modal_handler_add(self)

		return {"RUNNING_MODAL"}

class IceTools(Panel):
	'''Modelling support functions'''
	bl_label = 'Ice Tools'
	bl_idname = 'OBJECT_PT_icetools'
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = 'Ice Tools'

	def draw(self, context):
		scn = context.scene
		ob = context.object
		target = scn.link_target
		extract_mesh = scn.link_edit

		layout = self.layout
		fac = 0.3
		modnam = ["Mirror","Bevel Flat","Solidify","Bevel Solid"]
		methlist = ["None", "Angle"]

		col = layout.column(True)

		if ob:
			mod = ob.modifiers

			if ob.name == target:
				col.box().label("Target", icon = "ROTATE")
			else:
				col.box().label("Link", icon = "CONSTRAINT")

		row = col.row(True)
		row.operator("create_link.ice", "Create Link Mesh")
		row.prop(scn, "link_use_mouse_depth", "", icon="CURSOR")
		row.prop(scn, "link_use_surface_snap", "", icon="SNAP_SURFACE")

		if  scn.objects.find(target) != -1:
			targetstat = target
		else:
			targetstat = "None"

		box = col.box()
		colbox = box.column(True)
		row = colbox.row()
		split = row.split(percentage=fac)
		split.label("Target:")
		split.label(targetstat)
		if ob:
			row = colbox.row()
			split = row.split(percentage=fac)
			split.label("Active:")
			split.label(ob.name)
		colbox.separator()

		row = col.row(True)
		col = row.column(True)
		col.operator("isolate_view.ice", "Make Target Active")

		if ob:
			if ob.mode == "OBJECT" and ob.name == target:
				col.operator("toggle_edit.ice", "Extract Mode")
			else:
				if ob.mode == "OBJECT" and ob.name == extract_mesh:
					col.operator("toggle_edit.ice", "Show Original")

			if ob.mode == "EDIT" and ob.name == extract_mesh:
				col.operator("extract_faces.ice", "Extract Faces")

			if ob.name != target and ob.name != extract_mesh:
				colrow = col.row(True)
				link_diff = colrow.operator("link_bool.ice", "Difference", icon="ROTATECENTER")
				link_diff.mode = "DIFFERENCE"
				link_union = colrow.operator("link_bool.ice", "Union", icon = "ROTATECOLLECTION")
				link_union.mode = "UNION"

			if ob.name == target:
				colrow = col.row(True)
				colrow.prop(scn, "apply_perc", "Links To Apply")
				colrow.operator("view_by_perc.ice", "", icon = "FILE_REFRESH")
				col.operator("apply_all.ice", "Apply Boolean Links")

			linkmod = [m for m in ob.modifiers if m.name in modnam]
			if ob.name != target and len(linkmod) > 0:
				col.operator("copy_mod_settings.ice", "Copy Modifier Settings", icon="SETTINGS")

			if ob.name != target:
				colbox = col.column(True)
				for m in mod:
					if m.name in modnam:
						if m.name == "Mirror": mod_icon = "MOD_MIRROR"
						if m.name == "Solidify": mod_icon = "MOD_SOLIDIFY"
						if m.name == "Bevel Flat" or m.name == "Bevel Solid": mod_icon = "MOD_BEVEL"
						inbox = colbox.box()
						row = inbox.row(True)
						getMod = row.operator("get_mod.ice", text=m.name, icon=mod_icon, emboss=False)
						getMod.thisMod = m.name

						EnableIcon = "RESTRICT_VIEW_ON"
						if (m.show_viewport):
							EnableIcon = "RESTRICT_VIEW_OFF"
						Enable = row.operator("enable_mod.ice", icon=EnableIcon, emboss=False)
						Enable.objMod = m.name

						if m.name == "Mirror" and scn.mod_vis == m.name:
							inbox = colbox.box()
							row = inbox.row()
							row.prop(mod[m.name], "use_x", "X")
							row.prop(mod[m.name], "use_y", "Y")
							row.prop(mod[m.name], "use_z", "Z")
							
						if m.name == "Bevel Flat" and scn.mod_vis == m.name:
							inbox = colbox.box()
							colmod = inbox.column()
							colmod.prop(mod[m.name], "width", "Width")
							colmod.prop(mod[m.name], "segments", "Segments")
							colmod.prop(mod[m.name], "profile", "Profile")
							colrow = colmod.row(True)
							colrow.operator("assign_to_vgroup.ice", "Assign Verts")
							colrow.operator("object.vertex_group_remove_from", "Remove Verts")
							
						if m.name == "Solidify" and scn.mod_vis == m.name:
							inbox = colbox.box()
							colmod = inbox.column()
							colmod.prop(mod[m.name], "thickness", "Thickness")
							colmod.prop(mod[m.name], "offset", "Offset")
							colmod.prop(mod[m.name], "use_rim_only", "Only Rim")
							
						if m.name == "Bevel Solid" and scn.mod_vis == m.name:
							inbox = colbox.box()
							colmod = inbox.column()
							colmod.prop(mod[m.name], "width", "Width")
							colmod.prop(mod[m.name], "segments", "Segments")
							colmod.prop(mod[m.name], "profile", "Profile")
							colmod.prop(mod[m.name], "angle_limit", "Angle")

			try:
				mat = context.object.material_slots[0].material
				col.prop(mat, "diffuse_color", text="")
			except: pass
			
			if ob.mode == "VERTEX_PAINT" and ob.name == target:    
				col.operator("assign_vcol.ice", "Viewport Color To Vertex Color", icon = "COLOR")
			
		col.operator("use_auto_smooth.ice", "Auto Smooth")

		col = col.column(True)
		col.operator("apply_shrinkwrap.ice", "Apply Shrinkwrap")
		colrow = col.row(True)
		colrow.operator("freeze_verts.ice", "Freeze")
		colrow.operator("thaw_frozen_verts.ice", "Thaw")
		colrow.operator("show_freeze_verts.ice", "Show")
		
		if ob:
			colrow = col.box().row(True)
			colrow.alignment = "EXPAND"
			colrow.prop(context.object, "show_wire", toggle = False)
			colrow.prop(context.object, "show_x_ray", toggle = False)
			colrow.prop(context.space_data, "show_occlude_wire", toggle = False)

class IceTools_LViewer(Panel):
	'''Modelling support functions'''
	bl_label = 'Boolean Links'
	bl_idname = 'OBJECT_PT_booleanlinks'
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = 'Ice Tools'

	def draw(self, context):
		scn = context.scene
		ob = context.object
		layout = self.layout
		icon=""

		if ob and ob.name == scn.link_target:
			row = layout.row()
			bcount = [b for b in ob.modifiers if b.type == "BOOLEAN"]

			if len(bcount) > 0:
				split = row.split(percentage=.25)
				split.label("Mode:")
				split.label("Difference", icon= "ROTATECENTER")
				split.label("Union", icon= "ROTATECOLLECTION")
				row = layout.row(True)

				if scn.link_order == True:
					pushicon = "TRIA_DOWN"
					ordinfo = "Newest To Oldest"
					order = reversed(ob.modifiers)
				else:
					pushicon = "TRIA_UP"
					ordinfo = "Oldest To Newest"
					order = ob.modifiers

				row.prop(scn, "link_order", ordinfo, icon = "SORTTIME")
				row.operator("bool_hide.ice", "Hide/Unhide", icon = "RESTRICT_VIEW_OFF")
				for mod in order:
					if mod.type == "BOOLEAN":
						if mod.object == None:
							try:
								ob.modifiers.remove(mod)
							except: pass
						else:
							if (mod.operation == "UNION"):
								icon = "ROTATECOLLECTION"
							if (mod.operation == "DIFFERENCE"):
								icon = "ROTATECENTER"

							row = layout.box().row(True)
							pushOp = row.operator("push_to_top.ice", "", icon=pushicon, emboss=False)
							pushOp.pushMod = mod.name
							split = row.split(align=True, percentage=.6)
							objSelect = split.operator("find_link.ice", text=mod.object.name, emboss=False)
							objSelect.obj = mod.object.name

							try:
								mat = bpy.data.objects[mod.object.name].material_slots[0].material
								split.prop(mat, "diffuse_color", text="")
							except: pass

							EnableIcon = "RESTRICT_VIEW_ON"
							if (mod.show_viewport):
								EnableIcon = "RESTRICT_VIEW_OFF"
							Enable = split.operator("enable_link.ice", icon=EnableIcon, emboss=False)
							Enable.thisObj = mod.object.name

							changeOp = split.operator("change_op.ice", icon=icon, emboss=False)
							changeOp.linkObj = mod.object.name

							clearOp = split.operator("clear_op.ice", icon="CANCEL", emboss=False)
							clearOp.remObj = mod.object.name

class IceTools_Menu(Menu):
	bl_label = 'Ice Tool Operators'
	bl_idname = 'IceTools_View_Main'

	def draw(self, context):
		scn = context.scene
		ob = context.object
		target = scn.link_target
		extract_mesh = scn.link_edit

		layout = self.layout
		pie = layout.menu_pie()
		col = pie.column()

		if ob:
			if ob.name == target:
				colrow = col.row(True)
				colrow.operator("create_link.ice", "Create Link Mesh")
				colrow.prop(scn, "link_use_mouse_depth", "", icon="CURSOR")
				colrow.prop(scn, "link_use_surface_snap", "", icon="SNAP_SURFACE")
				col.operator("toggle_edit.ice", "Extract Mode")

			if ob.name == extract_mesh:
				if ob.mode == "OBJECT":
					col.operator("toggle_edit.ice", "Show Original")
				if ob.mode == "EDIT":
					col.operator("extract_faces.ice", "Extract Faces")

			if ob.name != target and ob.name != extract_mesh:
				colrow = col.row(True)
				link_diff = colrow.operator("link_bool.ice", "Difference", icon = "ROTATECENTER")
				link_diff.mode = "DIFFERENCE"
				link_union = colrow.operator("link_bool.ice", "Union", icon = "ROTATECOLLECTION")
				link_union.mode = "UNION"

			col.operator("simple_plane.ice", "Simple Plane")
			col.operator("gknife.ice", "Ghost Knife")

			if ob.name == target:
				col = pie.column()
				try:
					mat = context.object.material_slots[0].material
					col.prop(mat, "diffuse_color", text="")
				except: pass

				if ob.mode == "VERTEX_PAINT" and ob.name == scn.link_target:
					col.operator("assign_vcol.ice", "Viewport Color To Vertex Color", icon = "COLOR")
				col.operator("isolate_view.ice", "Make Target Active")
				col.operator("use_auto_smooth.ice", "Auto Smooth")
				colrow = col.row(True)
				colrow.prop(scn, "apply_perc", "Links To Apply")
				colrow.operator("view_by_perc.ice", "", icon = "FILE_REFRESH")
				col.operator("apply_all.ice", "Apply Boolean Links")

			if ob.name != target:
				col = pie.column()

				try:
					mat = context.object.material_slots[0].material
					col.prop(mat, "diffuse_color", text="")
				except: pass

				col.operator("isolate_view.ice", "Make Target Active")
				col.operator("use_auto_smooth.ice", "Auto Smooth")
				col.operator("apply_shrinkwrap.ice", "Apply Shrinkwrap")
				colrow = col.row(True)
				colrow.operator("freeze_verts.ice", "Freeze")
				colrow.operator("thaw_frozen_verts.ice", "Thaw")
				colrow.operator("show_freeze_verts.ice", "Show")

			if ob.name == scn.link_edit:
				row = pie.column(True)
			else:
				row = pie.row(True)

			row.prop(context.object, "show_wire", toggle = False, emboss = True)
			row.prop(context.object, "show_x_ray", toggle = False, emboss = True)
			row.prop(context.space_data, "show_occlude_wire", toggle = False, emboss = True)

			if ob.name != target and ob.name != extract_mesh:
				col = pie.column()
				colrow = col.row(True)
				colrow.operator("create_link.ice", "Create Link Mesh")
				colrow.prop(scn, "link_use_mouse_depth", "", icon="CURSOR")
				colrow.prop(scn, "link_use_surface_snap", "", icon="SNAP_SURFACE")
				col.operator("set_target.ice", "Set Link Mesh As Target", icon = "CONSTRAINT")

			if ob.name == target:
				row = pie.row()
				row.operator("set_target.ice", "Unset As Target Mesh", icon = "CONSTRAINT")

class ChangeColumn(Operator):
	'''See next linklist column'''
	bl_idname = "change_col.ice"
	bl_label = "Change Link List Column"
	
	this_col = StringProperty("")

	@classmethod
	def poll(cls, context):
		return context.active_object is not None
	
	def execute(self, context):
		scn = context.scene
		ob = context.object
		div = 10
		
		if self.this_col == "NEXT":
			bcount = [b for b in ob.modifiers if b.type == "BOOLEAN"]

			if scn.link_col < (len(bcount)-div):
				scn.link_col += div
		else:
			scn.link_col -= div
			if scn.link_col < 0: scn.link_col = 0            

		return {"FINISHED"}
    
class IceTools_Menu_Mod(Menu):
	bl_label = 'Ice Tool Operators'
	bl_idname = 'IceTools_View_Sub'

	def draw(self, context):
		scn = context.scene
		ob = context.object
		layout = self.layout
		pie = layout.menu_pie()

		if ob:
			if ob.name != scn.link_target:
				col = pie.column()
				viewIcon = "ZOOMOUT"
				viewText = "Minimum View"

				if scn.minView:
					viewIcon = "ZOOMIN"
					viewText = "Maximum View"
				col.prop(scn, "minView", text=viewText, icon=viewIcon)
				col.operator("copy_mod_settings.ice", "Copy Modifier Settings", icon="SETTINGS")
				applyMod = col.operator("object.convert", "Apply All Modifiers", icon="FILE_TICK")
				applyMod.target = "MESH"    
	
				col = pie.column()
				mod = ob.modifiers
				modnam = ["Mirror","Bevel Flat","Solidify","Bevel Solid"]
				for m in mod:
    
					if m.name in modnam:
						colbox = col.box().column()
						boxrow = colbox.row()

						EnableIcon = "RESTRICT_VIEW_ON"
						if (m.show_viewport):
							EnableIcon = "RESTRICT_VIEW_OFF"
						Enable = boxrow.operator("enable_mod.ice", text=m.name, icon=EnableIcon, emboss=False)
						Enable.objMod = m.name

						if m.name == "Mirror":
							if m.show_viewport:
								boxrow = colbox.row()
								boxrow.prop(mod["Mirror"], "use_x", "X", emboss=False)
								boxrow.prop(mod["Mirror"], "use_y", "Y", emboss=False)
								boxrow.prop(mod["Mirror"], "use_z", "Z", emboss=False)

						if m.name == "Bevel Flat":
							if m.show_viewport:
								colbox.prop(mod["Bevel Flat"], "width", "Width")
								colbox.prop(mod["Bevel Flat"], "segments", "Segments")

								if scn.minView == False:
									colbox.prop(mod["Bevel Flat"], "profile", "Profile")

								colrow = colbox.row(True)
								colrow.operator("assign_to_vgroup.ice", "Assign Verts")
								colrow.operator("object.vertex_group_remove_from", "Remove Verts")

						if m.name == "Solidify":
							if m.show_viewport:
								colbox.prop(mod["Solidify"], "thickness", "Thickness")
								colbox.prop(mod["Solidify"], "offset", "Offset")

								if scn.minView == False:
									colbox.prop(mod["Solidify"], "use_rim_only", "Only Rim", emboss=False)

						if m.name == "Bevel Solid":
							if m.show_viewport:
								colbox.prop(mod["Bevel Solid"], "width", "Width")
								colbox.prop(mod["Bevel Solid"], "segments", "Segments")

								if scn.minView == False:
									colbox.prop(mod["Bevel Solid"], "profile", "Profile")
									colbox.prop(mod["Bevel Solid"], "angle_limit", "Angle")
			else:
				col = pie.column()
				bcount = [b for b in ob.modifiers if b.type == "BOOLEAN"]

				if len(bcount) > 0:
					row = col.row(True)

					if scn.link_order == True:
						pushicon = "TRIA_DOWN"
						ordinfo = "Newest To Oldest"
						order = reversed(ob.modifiers)
					else:
						pushicon = "TRIA_UP"
						ordinfo = "Oldest To Newest"
						order = ob.modifiers

					nextCol = row.operator("change_col.ice", "Previous Column", icon="BACK")
					nextCol.this_col = "PREVIOUS"
					prevCol = row.operator("change_col.ice", "Next Column", icon="FORWARD")
					prevCol.this_col = "NEXT"
					row = col.row(True)                    
					row.prop(scn, "link_order", ordinfo, icon = "SORTTIME")
					row.operator("bool_hide.ice", "Hide/Unhide", icon = "RESTRICT_VIEW_OFF")

					col = pie.column()
					div = 10
					colnum = ceil(scn.link_col/div) + 1
					coldiv = str(ceil(len(bcount)/div))
					col.box().label("COLUMN " + str(colnum) + "/" + coldiv, icon = "ARROW_LEFTRIGHT")
					i = 0
					for mod in order:
						if mod.type == "BOOLEAN":
							if mod.object == None:
								try:
									ob.modifiers.remove(mod)
								except: pass
							else:
								i += 1
								if i > scn.link_col:
									if (mod.operation == "UNION"):
										icon = "ROTATECOLLECTION"
									if (mod.operation == "DIFFERENCE"):
										icon = "ROTATECENTER"

									row = col.box().row(True)
									pushOp = row.operator("push_to_top.ice", "", icon=pushicon, emboss=False)
									pushOp.pushMod = mod.name
									split = row.split(align=True, percentage=.6)
									objSelect = split.operator("find_link.ice", text=mod.object.name, emboss=False)
									objSelect.obj = mod.object.name

									try:
										mat = bpy.data.objects[mod.object.name].material_slots[0].material
										split.prop(mat, "diffuse_color", text="")
									except: pass

									EnableIcon = "RESTRICT_VIEW_ON"
									if (mod.show_viewport):
										EnableIcon = "RESTRICT_VIEW_OFF"
									Enable = split.operator("enable_link.ice", icon=EnableIcon, emboss=False)
									Enable.thisObj = mod.object.name

									changeOp = split.operator("change_op.ice", icon=icon, emboss=False)
									changeOp.linkObj = mod.object.name

									clearOp = split.operator("clear_op.ice", icon="CANCEL", emboss=False)
									clearOp.remObj = mod.object.name
									if i == (scn.link_col + div): break
									print(scn.link_col, "")

addon_keymaps = []

def register():
	bpy.utils.register_module(__name__)

	wm = bpy.context.window_manager
	km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D', region_type='WINDOW')
	kmi = km.keymap_items.new('wm.call_menu_pie', 'X', 'PRESS', ctrl=True, shift=True)
	kmi.properties.name = 'IceTools_View_Main'

	kmi = km.keymap_items.new('wm.call_menu_pie', 'X', 'PRESS', alt=True, shift=True)
	kmi.properties.name = 'IceTools_View_Sub'

	addon_keymaps.append(km)

	bpy.types.Scene.link_target = StringProperty()
	bpy.types.Scene.link_edit = StringProperty()
	bpy.types.Scene.link_use_surface_snap = BoolProperty(default=True)
	bpy.types.Scene.link_use_mouse_depth = BoolProperty(default=True)
	bpy.types.Scene.add_mirror = BoolProperty(default=True)
	bpy.types.Scene.add_solid = BoolProperty(default=True)
	bpy.types.Scene.add_bevel_flat = BoolProperty(default=True)
	bpy.types.Scene.add_bevel_sol = BoolProperty(default=True)

	bpy.types.Scene.symm_x = BoolProperty(default=True)
	bpy.types.Scene.symm_y = BoolProperty(default=False)
	bpy.types.Scene.symm_z = BoolProperty(default=False)
	
	bpy.types.Scene.bevel_width_flat = FloatProperty(default=.01)
	bpy.types.Scene.bevel_segment_flat = IntProperty(default=1)
	bpy.types.Scene.bevel_profile_flat= FloatProperty(default=.5)
	
	bpy.types.Scene.solid_thick = FloatProperty(default=.01)
	bpy.types.Scene.solid_offset = FloatProperty(default=0)
	bpy.types.Scene.solid_rim_only = BoolProperty(default=False)
	
	bpy.types.Scene.bevel_width_solid = FloatProperty(default=.01)
	bpy.types.Scene.bevel_segment_solid = IntProperty(default=1)
	bpy.types.Scene.bevel_profile_solid= FloatProperty(default=.5)
	bpy.types.Scene.bevel_angle_solid= FloatProperty(default=30)

	bpy.types.Scene.link_order = BoolProperty(default=True)
	bpy.types.Scene.apply_perc = IntProperty(default=100, min=0, max=100, subtype='PERCENTAGE')
	bpy.types.Scene.mod_vis = StringProperty()
	bpy.types.Scene.minView = BoolProperty(False)
	bpy.types.Scene.link_col = IntProperty(default=0)

def unregister():
	bpy.utils.unregister_module(__name__)

	wm = bpy.context.window_manager
	for km in addon_keymaps:
		wm.keyconfigs.addon.keymaps.remove(km)

	addon_keymaps.clear()

	bpy.types.Scene.link_target = StringProperty()
	bpy.types.Scene.link_edit = StringProperty()
	bpy.types.Scene.link_use_surface_snap = BoolProperty(default=True)
	bpy.types.Scene.link_use_mouse_depth = BoolProperty(default=True)
	bpy.types.Scene.add_mirror = BoolProperty(default=True)
	bpy.types.Scene.add_solid = BoolProperty(default=True)
	bpy.types.Scene.add_bevel_flat = BoolProperty(default=True)
	bpy.types.Scene.add_bevel_sol = BoolProperty(default=True)

	bpy.types.Scene.symm_x = BoolProperty(default=True)
	bpy.types.Scene.symm_y = BoolProperty(default=False)
	bpy.types.Scene.symm_z = BoolProperty(default=False)
	
	bpy.types.Scene.bevel_width_flat = FloatProperty(default=.01)
	bpy.types.Scene.bevel_segment_flat = IntProperty(default=1)
	bpy.types.Scene.bevel_profile_flat= FloatProperty(default=.5)
	
	bpy.types.Scene.solid_thick = FloatProperty(default=.01)
	bpy.types.Scene.solid_offset = FloatProperty(default=0)
	bpy.types.Scene.solid_rim_only = BoolProperty(default=False)
	
	bpy.types.Scene.bevel_width_solid = FloatProperty(default=.01)
	bpy.types.Scene.bevel_segment_solid = IntProperty(default=1)
	bpy.types.Scene.bevel_profile_solid= FloatProperty(default=.5)
	bpy.types.Scene.bevel_angle_solid= FloatProperty(default=30)

	bpy.types.Scene.link_order = BoolProperty(default=True)
	bpy.types.Scene.apply_perc = IntProperty(default=100, min=0, max=100, subtype='PERCENTAGE')
	bpy.types.Scene.mod_vis = StringProperty()
	bpy.types.Scene.minView = BoolProperty(False)	

if __name__ == '__main__':
	register()