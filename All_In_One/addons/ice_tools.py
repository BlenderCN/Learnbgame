bl_info = {
	"name": "Ice Tools",
	"author": "Ian Lloyd Dela Cruz, Bookyakuno (2.8Update)",
	"version": (2, 0, 2),
	"blender": (2, 80, 0),
	"location": "3d View > property shelf > Retopology > Ice Tools",
	"description": "Retopology support",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Learnbgame",
	}

import bpy
import math
import bmesh
from bpy.props import *

def add_mod(mod, link, meth, offset):
	md = bpy.context.active_object.modifiers.new(mod, 'SHRINKWRAP')
	md.target = bpy.data.objects[link]
	md.wrap_method = meth
	if md.wrap_method == "PROJECT":
		md.use_negative_direction = True
	if md.wrap_method == "NEAREST_SURFACEPOINT":
		md.use_keep_above_surface = True
	md.offset = offset
	if "retopo_suppo_frozen" in bpy.context.active_object.vertex_groups:
		md.vertex_group = "retopo_suppo_thawed"
	md.show_on_cage = False
	md.show_expanded = False

def sw_clipping(obj, autoclip, clipcenter):
	if "Mirror" in bpy.data.objects[obj].modifiers:
		pre_cursor_location = bpy.context.scene.cursor_location.copy()
		bpy.ops.object.editmode_toggle()
		bpy.ops.view3d.snap_cursor_to_selected()
		bpy.ops.object.editmode_toggle()

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
				bpy.ops.mesh.select_all(action='DESELECT')
				for v in bm.verts:
					if -EPSILON <= v.co.x <= EPSILON:
						v.select = True
						bm.select_history.add(v)
						v1 = v
						vcount += 1
					if vcount > 1:

						bpy.ops.mesh.select_axis(orientation='CURSOR', sign='NEG')
						bpy.context.scene.cursor_location = pre_cursor_location

						# bpy.ops.mesh.select_axis(mode='ALIGNED')
						# bpy.ops.mesh.select_axis()
						bpy.ops.mesh.loop_multi_select()
						# for vert in bpy.context.active_object.data.vertices:
						# 	co = [vert.co.x, vert.co.y, vert.co.z][int(self.axis)]
						# 	direct = int(self.direction)
						# 	if (self.offset * direct <= co * direct + self.threshold):
						# 		vert.select = True

						for v in bm.verts:
							if v.select == True: v.co.x = 0
						break

def sw_Update(meshlink, wrap_offset, wrap_meth, autoclip, clipcenter):
	activeObj = bpy.context.active_object
	scn = bpy.context.scene
	oldmod = activeObj.mode
	selmod = bpy.context.tool_settings.mesh_select_mode
	modnam = "shrinkwrap_apply"
	modlist = bpy.context.object.modifiers
	modops = bpy.ops.object.modifier_move_up

	if selmod[0] == True:
		oldSel = 'VERT'
	if selmod[1] == True:
		oldSel = 'EDGE'
	if selmod[2] == True:
		oldSel = 'FACE'

	bpy.context.view_layer.objects.active = activeObj

	# bpy.context.scene.objects.active = activeObj
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_mode(type='VERT')

	sw_clipping(activeObj.name, autoclip, clipcenter)

	if "shrinkwrap_apply" in bpy.context.active_object.modifiers:
		bpy.ops.object.modifier_remove(modifier= "shrinkwrap_apply")

	if "retopo_suppo_thawed" in bpy.context.active_object.vertex_groups:
		tv = bpy.data.objects[activeObj.name].vertex_groups["retopo_suppo_thawed"].index
		activeObj.vertex_groups.active_index = tv
		bpy.ops.object.vertex_group_remove(all=False)

	if "retopo_suppo_frozen" in bpy.context.active_object.vertex_groups:
		fv = bpy.data.objects[activeObj.name].vertex_groups["retopo_suppo_frozen"].index
		activeObj.vertex_groups.active_index = fv
		bpy.ops.mesh.select_all(action="SELECT")
		bpy.ops.object.vertex_group_deselect()
		bpy.ops.object.vertex_group_add()
		bpy.data.objects[activeObj.name].vertex_groups.active.name = "retopo_suppo_thawed"
		bpy.ops.object.vertex_group_assign()

	#add sw mod
	add_mod(modnam, meshlink, wrap_meth, wrap_offset)

	#move sw mod up the stack
	for i in modlist:
		if modlist.find(modnam) == 0: break
		modops(modifier=modnam)

	#apply modifier
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modnam)
	bpy.ops.object.mode_set(mode='EDIT')

	if scn.sw_autoapply == False:
	#move the sw mod below the mirror or multires mod assuming this is your first
		add_mod(modnam, meshlink, wrap_meth, wrap_offset)
		for i in modlist:
			if modlist.find(modnam) == 0: break
			if modlist.find(modnam) == 1:
				if modlist.find("Mirror") == 0: break
				if modlist.find("Multires") == 0: break
			modops(modifier=modnam)

	sw_clipping(activeObj.name, autoclip, False)

	bpy.ops.mesh.select_all(action='DESELECT')
	bpy.ops.mesh.select_mode(type=oldSel)

	if "retopo_suppo_vgroup" in bpy.context.active_object.vertex_groups:
		vg = bpy.data.objects[activeObj.name].vertex_groups["retopo_suppo_vgroup"].index
		activeObj.vertex_groups.active_index = vg
		bpy.ops.object.vertex_group_select()
		bpy.ops.object.vertex_group_remove(all=False)

	bpy.ops.object.mode_set(mode=oldmod)

class SetUpRetopoMesh(bpy.types.Operator):
	'''Set up Retopology Mesh on Active Object'''
	bl_idname = "setup.retopo"
	bl_label = "Set Up Retopo Mesh"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == 'OBJECT' or context.active_object.mode == 'SCULPT'

	def execute(self, context):
		scn = context.scene
		oldObj = bpy.context.view_layer.objects.active.name

		bpy.ops.view3d.snap_cursor_to_active()
		bpy.ops.mesh.primitive_plane_add(enter_editmode = True)

		bpy.ops.mesh.delete(type='VERT')
		bpy.ops.object.editmode_toggle()
		context.object.name = oldObj + "_retopo_mesh"
		activeObj = context.active_object

		#place mirror mod
		md = activeObj.modifiers.new("Mirror", 'MIRROR')
		md.show_on_cage = False
		md.use_clip = True

		#generate grease pencil surface draw mode on retopo mesh
		# bpy.context.tool_settings.grease_pencil_source = 'OBJECT'
		# if context.object.grease_pencil is None: bpy.ops.gpencil.data_add()
		# if context.object.grease_pencil.layers.active is None: bpy.ops.gpencil.layer_add()
		# bpy.data.objects[oldObj].select = True

		#further mesh toggles
		bpy.ops.object.editmode_toggle()
		context.tool_settings.use_snap = True
		# context.tool_settings.snap_element = 'FACE'
		bpy.context.scene.tool_settings.snap_elements = {'FACE'}
		# context.tool_settings.snap_target = 'CLOSEST'
		bpy.context.scene.tool_settings.snap_target = 'CLOSEST'
		context.tool_settings.use_snap_project = True
		context.object.show_all_edges = True
		bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')

		#establish link for shrinkwrap update function
		scn.sw_target = oldObj
		scn.sw_mesh = activeObj.name

		for SelectedObject in context.selected_objects :
			if SelectedObject != activeObj :
				SelectedObject.select = False
		activeObj.select_set(state = True)
		return {'FINISHED'}

class ShrinkUpdate(bpy.types.Operator):
	'''Applies Shrinkwrap Mod on Retopo Mesh'''
	bl_idname = "shrink.update"
	bl_label = "Shrinkwrap Update"
	bl_options = {'REGISTER', 'UNDO'}

	apply_mod = bpy.props.BoolProperty(name = "Auto-apply Shrinkwrap", default = True)
	sw_autoclip = bpy.props.BoolProperty(name = "Auto-Clip (X)", default = True)
	sw_clipcenter = bpy.props.BoolProperty(name = "Clip Selected Verts (X)", default = False)
	sw_offset = bpy.props.FloatProperty(name = "Offset:", min = -0.5, max = 0.5, step = 0.1, precision = 3, default = 0)
	sw_wrapmethod = bpy.props.EnumProperty(
		name = 'Wrap Method',
		items = (
			('NEAREST_VERTEX', 'Nearest Vertex',""),
			('PROJECT', 'Project',""),
			('NEAREST_SURFACEPOINT', 'Nearest Surface Point',"")),
		default = 'PROJECT')

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		activeObj = context.active_object
		scn = context.scene

		#establish link
		if len(bpy.context.selected_objects) == 2:
			for SelectedObject in bpy.context.selected_objects:
				if SelectedObject != activeObj:
					scn.sw_target = SelectedObject.name
				else:
					scn.sw_mesh = activeObj.name
				if SelectedObject != activeObj :
					SelectedObject.select_set(state = False)

		if scn.sw_mesh != activeObj.name:
			self.report({'WARNING'}, "Establish Link First!")
			return {'FINISHED'}
		else:
			if self.apply_mod == True:
			   scn.sw_autoapply = True
			else:
			   scn.sw_autoapply = False

			if activeObj.mode == 'EDIT':
				bpy.ops.object.vertex_group_add()
				bpy.data.objects[activeObj.name].vertex_groups.active.name = "retopo_suppo_vgroup"
				bpy.ops.object.vertex_group_assign()

			sw_Update(scn.sw_target, self.sw_offset, self.sw_wrapmethod, self.sw_autoclip, self.sw_clipcenter)
			activeObj.select_set(state = True)

		return {'FINISHED'}

class FreezeVerts(bpy.types.Operator):
	'''Immunize verts from shrinkwrap update'''
	bl_idname = "freeze_verts.retopo"
	bl_label = "Freeze Vertices"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == 'EDIT'

	def execute(self, context):
		activeObj = bpy.context.active_object

		if "retopo_suppo_frozen" in bpy.context.active_object.vertex_groups:
			fv = bpy.data.objects[activeObj.name].vertex_groups["retopo_suppo_frozen"].index
			activeObj.vertex_groups.active_index = fv
			bpy.ops.object.vertex_group_assign()
		else:
			bpy.ops.object.vertex_group_add()
			bpy.data.objects[activeObj.name].vertex_groups.active.name = "retopo_suppo_frozen"
			bpy.ops.object.vertex_group_assign()

		return {'FINISHED'}

class ThawFrozenVerts(bpy.types.Operator):
	'''Remove frozen verts'''
	bl_idname = "thaw_freeze_verts.retopo"
	bl_label = "Thaw Frozen Vertices"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == 'EDIT'

	def execute(self, context):
		activeObj = bpy.context.active_object

		if "retopo_suppo_frozen" in bpy.context.active_object.vertex_groups:
			tv = bpy.data.objects[activeObj.name].vertex_groups["retopo_suppo_frozen"].index
			activeObj.vertex_groups.active_index = tv
			bpy.ops.object.vertex_group_remove_from()

		return {'FINISHED'}

class ShowFrozenVerts(bpy.types.Operator):
	'''Show frozen verts'''
	bl_idname = "show_freeze_verts.retopo"
	bl_label = "Show Frozen Vertices"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.active_object.mode == 'EDIT'

	def execute(self, context):
		activeObj = bpy.context.active_object

		if "retopo_suppo_frozen" in bpy.context.active_object.vertex_groups:
			bpy.ops.mesh.select_mode(type='VERT')
			fv = bpy.data.objects[activeObj.name].vertex_groups["retopo_suppo_frozen"].index
			activeObj.vertex_groups.active_index = fv
			bpy.ops.mesh.select_all(action='DESELECT')
			bpy.ops.object.vertex_group_select()

		return {'FINISHED'}

class RetopoSupport(bpy.types.Panel):
	"""Retopology Support Functions"""
	bl_label = "Ice Tools"
	bl_idname = "OBJECT_PT_retosuppo"
	bl_space_type = 'VIEW_3D'
	# bl_region_type = 'TOOLS'
	# bl_category = 'Retopology'
	bl_region_type = 'UI'
	bl_category = 'Retopology'




	def draw(self, context):
		layout = self.layout
		scn = context.scene

		row = layout.row(align=True)
		# row.alignment = 'EXPAND'
		row.operator("setup.retopo", text="Set Up Retopo Mesh")
		row = layout.row(align=True)
		# row.alignment = 'EXPAND'
		row.operator("shrink.update", text="Shrinkwrap Update")

		row = layout.row(align=True)
		row.alignment = 'EXPAND'
		row.operator("freeze_verts.retopo", text="Freeze")
		row.operator("thaw_freeze_verts.retopo", text="Thaw")
		row.operator("show_freeze_verts.retopo", text="Show")

		# if context.active_object is not None:
		# 	row = layout.row(align=True)
		# 	row.alignment = 'EXPAND'
			# row.prop(bpy.context.space_data,"overlay.show_wireframes")
			# row.prop(context.object, text="show_x_ray", toggle =False)
			# row.prop(context.space_data, text="show_occlude_wire", toggle =False)






classes = {
SetUpRetopoMesh,
ShrinkUpdate,
FreezeVerts,
ThawFrozenVerts,
ShowFrozenVerts,
RetopoSupport,
}

def register():
	# bpy.utils.register_module(__name__)
	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.Scene.sw_mesh= StringProperty()
	bpy.types.Scene.sw_target= StringProperty()
	bpy.types.Scene.sw_autoapply = BoolProperty(default=True)

def unregister():
	# bpy.utils.unregister_module(__name__)
	for cls in classes:
		bpy.utils.unregister_class(cls)

if __name__ == "__main__":
	register()
