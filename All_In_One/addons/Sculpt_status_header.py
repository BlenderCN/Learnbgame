# ##### BEGIN GPL LICENSE BLOCK #####
#
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version 2
#   of the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from random import random
import bpy
from bpy.types import Menu, Panel, UIList
#from bl_ui.properties_grease_pencil_common import (
#   	GreasePencilDrawingToolsPanel,
#   	GreasePencilStrokeEditPanel,
#   	GreasePencilStrokeSculptPanel,
#   	GreasePencilBrushPanel,
#   	GreasePencilBrushCurvesPanel
#   	)
#from bl_ui.properties_paint_common import (
#   	UnifiedPaintPanel,
#   	brush_texture_settings,
#   	brush_texpaint_common,
#   	brush_mask_texture_settings,
#   	)




# アドオン情報
bl_info = {
	"name" : "Sculpt status header",
	"author" : "bookyakuno",
	"version" : (0, 6),
	"blender" : (2, 78),
	"location" : "3DView > TOOL Shelf > Sculpt Tab > Sculpt_menu_x, duplicate/separate/mat/mat_select/cut_mat_group > shfit + alt + D/F/R/R+ctrl/V",
	"description" : "Sculpt smart status",
	"warning" : "",
	"wiki_url" : "",
	"tracker_url" : "",
	"category" : "UI"
}



#class View3DPaintPanel(UnifiedPaintPanel):
#   bl_space_type = 'VIEW_3D'
#   bl_region_type = 'TOOLS'



def prop_unified_size_x(self, context):
	ups = context.tool_settings.unified_paint_settings
	ptr = ups if ups.use_unified_size else brush
	parent.prop(ptr, prop_name, icon=icon, text=text, slider=slider)



# ヘッダーに項目追加
def sculpt_header(self, context):

	layout = self.layout


	if context.image_paint_object:

		col = layout.column(align=True)
		row = col.row(align=True)
		# シンメトリー

		toolsettings = context.tool_settings
		ipaint = toolsettings.image_paint
		row.prop(ipaint, "use_symmetry_x", text="X", toggle=True)
		row.prop(ipaint, "use_symmetry_y", text="Y", toggle=True)
		row.prop(ipaint, "use_symmetry_z", text="Z", toggle=True)



		settings = self.paint_settings(context)
		brush = settings.brush

		col = layout.column()

		col.label(text="Stroke Method:")

		col.prop(brush, "stroke_method", text="")








	obj = context.active_object
	mode_string = context.mode
	edit_object = context.edit_object
	gp_edit = context.gpencil_data and context.gpencil_data.use_stroke_edit_mode
	mode = obj.mode
	if (mode == 'EDIT' and obj.type == 'MESH' or mode == 'EDIT' and 'ARMATURE'):

		arm = context.active_object.data
		self.layout.prop(arm, "use_mirror_x",text="",icon="MOD_MIRROR")


#   obj = context.active_object
#   if obj:
#   		obj_type = obj.type

#   		if obj_type in {'ARMATURE'}:

#   			arm = context.active_object.data
#   			self.layout.prop(arm, "use_mirror_x",text="",icon="MOD_MIRROR")


#   if mode_string == 'EDIT_ARMATURE':
#
#   	arm = context.active_object.data
#   	self.layout.prop(arm, "use_mirror_x")

#   if ob.type == 'ARMATURE' and ob.mode in {'EDIT', 'POSE'}:

#   	arm = context.active_object.data
#   	self.layout.prop(arm, "use_mirror_x")


	if context.sculpt_object:

		col = layout.column(align=True)
		row = col.row(align=True)
		# シンメトリー
		sculpt = context.tool_settings.sculpt
		row.scale_x = 0.5
		row.prop(sculpt, "use_symmetry_x", text="X", toggle=True)
		row.prop(sculpt, "use_symmetry_y", text="Y", toggle=True)
		row.prop(sculpt, "use_symmetry_z", text="Z", toggle=True)


#   	toolsettings = context.tool_settings
#   	settings = self.paint_settings(context)
#   	brush = settings.brush


#   	col.template_ID_preview(settings, "brush", new="brush.add", rows=3, cols=8)



#   	 toolsettings = context.tool_settings
#   	 settings = self.paint_settings(context)
#   	 brush = settings.brush
#
#
#   	 col.template_ID_preview(settings, "brush", new="brush.add", rows=3, cols=8)



		# Dynatopo
# row.separator()
# if context.sculpt_object.use_dynamic_topology_sculpting:
#    row.operator("sculpt.dynamic_topology_toggle", icon='CANCEL', text="")
# else:
#    row.operator("sculpt.dynamic_topology_toggle", icon='MOD_REMESH', text="")
# row.prop(sculpt, "detail_size", text="")



		#booleans_sculpt_v_0_0_2.py

		WM = context.window_manager
		toolsettings = context.tool_settings
		sculpt = toolsettings.sculpt

		if len(context.selected_objects) >= 1 :
				#Detail Size
				row.separator()
				row = layout.row(align=True)
				row.operator("object.update_dyntopo", text=" ", icon='FILE_TICK')
				row.scale_x = 0.5
				row.prop(WM, "detail_size", text="")
#   			row.scale_x = 1.2
				row.separator()
				if context.sculpt_object.use_dynamic_topology_sculpting:
					row.operator("sculpt.dynamic_topology_toggle", icon='CANCEL', text="")
				else:
					row.operator("sculpt.dynamic_topology_toggle", icon='MOD_REMESH', text="")

				row.separator()

				if not bpy.context.object.mode == 'SCULPT':
						layout.prop(WM, "subdivide_mesh", text="Subdivide")
						if WM.subdivide_mesh:
								layout.prop(WM, "use_sharps", text="Sharp Edges")
				layout.prop(WM, "smooth_mesh", text="", icon='MOD_SMOOTH')
				layout.prop(WM, "update_detail_flood_fill", text="", icon='MOD_DECIM')

		userpref = context.user_preferences
		view = userpref.view
		row = layout.row()
		col = row.column()
		layout.prop(view, "use_auto_perspective", text="", icon="CAMERA_DATA")

#   def prop_unified_strength(parent, context, brush, prop_name, icon='NONE', text="", slider=False):
#   	ups = context.tool_settings.unified_paint_settings
#   	ptr = ups if ups.use_unified_strength else brush
#   	parent.prop(ptr, prop_name, icon=icon, text=text, slider=slider)





################################################################

#   	row.prop(brush, "stroke_method", text="")

		row.prop(sculpt, "detail_size", text="")


def texture_import(self, context):

	layout = self.layout


	layout.separator()
	layout.operator('texture.load_brushes')
	layout.operator('texture.load_single_brush')










# class sculptmode_off_persp(bpy.types.Operator):
#   bl_idname = "object.sculptmode_off_persp"
#   bl_label = "sculptmode_off_persp"
#
#
#   def execute(self, context):
#   	# v = bpy.context.user_preferences.view
#   	bpy.ops.sculpt.sculptmode_toggle()
#   	bpy.context.user_preferences.view.use_auto_perspective = False
#
#   	if bpy.context.object.mode == 'SCULPT':
#
#   		bpy.ops.sculpt.sculptmode_toggle()
#   		bpy.context.user_preferences.view.use_auto_perspective = True
#
#   	return {'FINISHED'}



class duplicate_mask(bpy.types.Operator):
	bl_idname = "object.duplicate_mask"
	bl_label = "duplicate_mask"



	def execute(self, context):
		bpy.ops.paint.hide_show(action='HIDE', area='MASKED') # マスク部分を非表示
		bpy.ops.sculpt.sculptmode_toggle() # オブジェクトモードに戻す
		bpy.ops.object.select_all(action='DESELECT') #全選択解除で最後に選択するものを複製したものだけにする
		bpy.ops.object.editmode_toggle() # 編集モード
		bpy.ops.mesh.select_all(action='DESELECT') #全選択解除
		bpy.ops.mesh.reveal() # 隠しているものを表示
#   	 bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, 0))
		bpy.context.scene.tool_settings.use_mesh_automerge = False

		bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}) # 選択部分を複製
#   	bpy.ops.mesh.edge_face_add() # 閉じたオブジェクトにする
#   	bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY') # 閉じた面を三角形化
		bpy.ops.mesh.separate(type='SELECTED') # 選択部分を分離
		bpy.ops.object.editmode_toggle() # オブジェクトモード
		bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY') #重心に原点を配置して、回転しやすいように
		bpy.context.scene.tool_settings.use_mesh_automerge = True

		return {'FINISHED'}



class separate_mask(bpy.types.Operator):
	bl_idname = "object.separate_mask"
	bl_label = "separate_mask"


	def execute(self, context):
		bpy.ops.paint.hide_show(action='HIDE', area='MASKED') # マスク部分を非表示
		bpy.ops.sculpt.sculptmode_toggle() # オブジェクトモードに戻す
		bpy.ops.object.select_all(action='DESELECT') #全選択解除で最後に選択するものを複製したものだけにする
		bpy.ops.object.editmode_toggle() # 編集モード
		bpy.ops.mesh.select_all(action='DESELECT') #全選択解除
		bpy.ops.mesh.reveal() # 隠しているものを表示
		# bpy.ops.mesh.duplicate_move() # 選択部分を複製
		bpy.ops.mesh.split()
#   	bpy.ops.mesh.edge_face_add() # 閉じたオブジェクトにする(F2)
#   	bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY') # 閉じた面を三角形化
		bpy.ops.mesh.separate(type='SELECTED') # 選択部分を分離
		bpy.ops.object.editmode_toggle() # オブジェクトモード
		bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY') #重心に原点を配置して、回転しやすいように

		return {'FINISHED'}


class mat_select_mask(bpy.types.Operator):
	bl_idname = "object.mat_select_mask"
	bl_label = "mat_select_mask"


	def execute(self, context):
		bpy.ops.paint.hide_show(action='HIDE', area='MASKED') # マスク部分を非表示
		bpy.ops.sculpt.sculptmode_toggle() # オブジェクトモードに戻す
		bpy.ops.object.editmode_toggle() # 編集モード
		bpy.ops.mesh.select_all(action='DESELECT') #全選択解除
		bpy.ops.mesh.reveal() # 隠しているものを表示
		bpy.ops.sculpt.sculptmode_toggle() # スカルプトモード
		bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)
		bpy.ops.object.editmode_toggle() # 編集モード
		# bpy.ops.mesh.duplicate_move() # 選択部分を複製
		bpy.ops.mesh.select_similar(type='MATERIAL', threshold=0.01)
		bpy.ops.mesh.hide(unselected=False)
		bpy.ops.sculpt.sculptmode_toggle() # スカルプトモード
		bpy.ops.paint.mask_flood_fill(mode='VALUE', value=1)
		bpy.ops.paint.hide_show(action='SHOW', area='ALL')
		bpy.ops.paint.mask_flood_fill(mode='INVERT')


		return {'FINISHED'}



class mat_mask(bpy.types.Operator):
	bl_idname = "object.mat_mask"
	bl_label = "mat_mask"


	def execute(self, context):
		bpy.ops.paint.hide_show(action='HIDE', area='MASKED') # マスク部分を非表示
		bpy.ops.object.editmode_toggle() # 編集モード
		bpy.ops.mesh.select_all(action='DESELECT') #全選択解除
		bpy.ops.mesh.reveal() # 隠しているものを表示

		ob = bpy.context.object
		me = ob.data

		mat_offset = len(me.materials)
		mat_count = 1

		mats = []
		for i in range(mat_count):
			mat = bpy.data.materials.new("Mat_%i" % i)
			mat.diffuse_color = random(), random(), random()
			me.materials.append(mat)

		# Can't assign materials in editmode
		bpy.ops.object.mode_set(mode='OBJECT')

		i = 0
		for poly in me.polygons:
			if poly.select:
				poly.material_index = i % mat_count + mat_offset
				i += 1


		bpy.ops.sculpt.sculptmode_toggle() # オブジェクトモード
		return {'FINISHED'}














class random_mat(bpy.types.Operator):
	bl_idname = "object.random_mat"
	bl_label = "random_mat"




	def execute(self, context):

		ob = bpy.context.object
		me = ob.data

		mat_offset = len(me.materials)
		mat_count = 1

		mats = []
		for i in range(mat_count):
			mat = bpy.data.materials.new("Mat_%i" % i)
			mat.diffuse_color = random(), random(), random()
			me.materials.append(mat)

		# Can't assign materials in editmode
		bpy.ops.object.mode_set(mode='OBJECT')

		i = 0
		for poly in me.polygons:
			if poly.select:
				poly.material_index = i % mat_count + mat_offset
				i += 1

		if bpy.context.scene.render.engine == 'CYCLES':
 			bpy.context.object.active_material.use_nodes = True


		bpy.ops.object.mode_set(mode='EDIT')

		return {'FINISHED'}





class cut_mat_group(bpy.types.Operator):
	bl_idname = "object.cut_mat_group"
	bl_label = "cut_mat_group"


	def execute(self, context):

		bpy.ops.sculpt.sculptmode_toggle() # オブジェクトモードへ
		active = bpy.context.active_object
		bpy.ops.object.select_all(action='DESELECT') #全選択解除して複数選択を回避
		active.select = True


		bpy.ops.gpencil.convert(type='CURVE', use_timing_data=True)
		bpy.ops.gpencil.layer_remove()
		bpy.ops.object.editmode_toggle()
		bpy.ops.mesh.select_all(action='DESELECT') #全選択解除
		bpy.ops.mesh.knife_project(cut_through=True)


		ob = bpy.context.object
		me = ob.data

		mat_offset = len(me.materials)
		mat_count = 1

		mats = []
		for i in range(mat_count):
			mat = bpy.data.materials.new("Mat_%i" % i)
			mat.diffuse_color = random(), random(), random()
			me.materials.append(mat)

		# Can't assign materials in editmode
		bpy.ops.object.mode_set(mode='OBJECT')

		i = 0
		for poly in me.polygons:
			if poly.select:
				poly.material_index = i % mat_count + mat_offset
				i += 1





		#  アクティブオブジェクトの定義
		active = bpy.context.active_object

		#  アクティブオブジェクトの名前を定義
		name = active.name

		#  "cv_" + アクティブオブジェクト名に定義
		objname = "cv_" + name


		#  一度、アクティブの選択を解除し、リネームする
		active.select = False
		for obj in bpy.context.selected_objects:
			obj.name = objname

		bpy.ops.object.delete(use_global=False)

		#  再度、アクティブを選択
		active.select = True


		bpy.ops.sculpt.sculptmode_toggle() # オブジェクトモード
		return {'FINISHED'}


class grease_pencil_cut(bpy.types.Operator):
	bl_idname = "object.grease_pencil_cut"
	bl_label = "grease_pencil_cut"


	def execute(self, context):

		bpy.ops.sculpt.sculptmode_toggle() # オブジェクトモードへ
		active = bpy.context.active_object
		bpy.ops.object.select_all(action='DESELECT') #全選択解除して複数選択を回避
		active.select = True


		bpy.ops.gpencil.convert(type='CURVE', use_timing_data=True)
		bpy.ops.gpencil.layer_remove()
		bpy.ops.object.editmode_toggle()
		bpy.ops.mesh.select_all(action='DESELECT') #全選択解除
		bpy.ops.mesh.knife_project(cut_through=True)
		bpy.ops.mesh.delete(type='FACE')




		# Can't assign materials in editmode
		bpy.ops.object.mode_set(mode='OBJECT')


		#  アクティブオブジェクトの定義
		active = bpy.context.active_object

		#  アクティブオブジェクトの名前を定義
		name = active.name

		#  "cv_" + アクティブオブジェクト名に定義
		objname = "cv_" + name


		#  一度、アクティブの選択を解除し、リネームする
		active.select = False
		for obj in bpy.context.selected_objects:
			obj.name = objname

		bpy.ops.object.delete(use_global=False)

		#  再度、アクティブを選択
		active.select = True


		bpy.ops.sculpt.sculptmode_toggle() # オブジェクトモード
		return {'FINISHED'}

class grease_pencil_cut_v2(bpy.types.Operator):
	bl_idname = "object.grease_pencil_cut_v2"
	bl_label = "grease_pencil_cut_v2"


	def execute(self, context):


		bpy.ops.gpencil.convert(type='CURVE', use_timing_data=True)
		bpy.ops.gpencil.layer_remove()
		bpy.ops.object.convert(target='MESH')


		# Can't assign materials in editmode
		bpy.ops.object.mode_set(mode='OBJECT')


		#  アクティブオブジェクトの定義
		active = bpy.context.active_object

		#  アクティブオブジェクトの名前を定義
		name = active.name

		#  "gpc_" + アクティブオブジェクト名に定義
		objname = "gpc_" + name


		#  一度、アクティブの選択を解除し、リネームする
		active.select = False
		for obj in bpy.context.selected_objects:
			obj.name = objname

		bpy.context.scene.objects.active = bpy.data.objects["gpc_" + name]
		bpy.ops.object.editmode_toggle()
		bpy.ops.mesh.select_all(action='SELECT')
		bpy.ops.mesh.edge_face_add() # 閉じたオブジェクトにする
		bpy.ops.transform.translate(value=(2.38419e-07, 0, -50), constraint_axis=(False, False, True), constraint_orientation='NORMAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=11.9182) # 移動
		bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(-9.53674e-07, -0.000114441, 271.401), "constraint_axis":(False, False, True), "constraint_orientation":'NORMAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":11.9182, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False}) # 押し出し
		bpy.ops.mesh.select_all(action='SELECT')
		bpy.ops.mesh.normals_make_consistent(inside=False) # ノーマルを直す
		# bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY') # 三角形化

		bpy.ops.object.editmode_toggle()
		#
		# #  再度、アクティブを選択
		bpy.ops.object.select_all(action='DESELECT') #全選択解除

		active.select = True
		scene = bpy.context.scene
		for ob in scene.objects:
			if ob.name.startswith("gpc_" + name):
				ob.select = True
		bpy.context.scene.objects.active = bpy.data.objects[name]


		# active.select = True
		# bpy.ops.object.modifier_apply(modifier="BTool_" + "gpc_" + name)
		bpy.ops.btool.boolean_diff_direct()
		return {'FINISHED'}



class convert_multireso(bpy.types.Operator):
	bl_idname = "object.convert_multireso"
	bl_label = "convert_multireso"


	def execute(self, context):




		#  アクティブオブジェクトの定義
		active = bpy.context.active_object

		#  アクティブオブジェクトの名前を定義
		name = active.name



		bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
		bpy.ops.object.modifier_add(type='DECIMATE')
		bpy.context.object.modifiers["Decimate"].use_symmetry = True
		bpy.context.object.modifiers["Decimate"].ratio = 0.05
		bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")


		bpy.ops.object.modifier_add(type='MULTIRES')
		bpy.ops.object.multires_subdivide(modifier="Multires")
		bpy.ops.object.multires_subdivide(modifier="Multires")





		bpy.ops.object.modifier_add(type='SHRINKWRAP')
		bpy.context.object.modifiers["Shrinkwrap"].wrap_method = 'PROJECT'
		bpy.context.object.modifiers["Shrinkwrap"].use_negative_direction = True
		bpy.context.object.modifiers["Shrinkwrap"].target = bpy.data.objects[name]
		bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Shrinkwrap")

		return {'FINISHED'}









class Sculpt_menu_x(bpy.types.Panel):
	"""UI panel for the Remesh and Boolean buttons"""
	bl_label = "Sculpt_menu_x"
	bl_idname = "Sculpt_menu_x"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = "Sculpt"


	def draw(self, context):
		layout = self.layout
		edit = context.user_preferences.edit
		wm = context.window_manager

		row = layout.row(align=True)
		row.operator("object.duplicate_mask", icon="UV_ISLANDSEL")
		row.operator("object.separate_mask", icon="MOD_UVPROJECT")
		row.operator("object.random_mat", icon="COLOR")
		row = layout.row(align=True)
		row.operator("object.mat_mask", icon="FACESEL_HLT")
		row.operator("object.mat_select_mask", icon="RESTRICT_SELECT_OFF")
		row.operator("object.cut_mat_group", icon="BORDER_LASSO")
		row = layout.row(align=True)
		row.operator("object.grease_pencil_cut", icon="IPO_ELASTIC")
		row.operator("object.grease_pencil_cut_v2", icon="RNDCURVE")
		row = layout.row(align=True)
		row.operator("object.convert_multireso", icon="MOD_MULTIRES")








class automirror_apply_mod(bpy.types.Operator):
	bl_idname = "object.automirror_apply_mod"
	bl_label = "automirror_apply_mod"


	def execute(self, context):
		layout = self.layout
		bpy.context.scene.AutoMirror_apply_mirror = True
		bpy.ops.object.automirror()

		bpy.context.scene.AutoMirror_apply_mirror = False
		return {'FINISHED'}








addon_keymaps = []
def register():
	bpy.utils.register_module(__name__)

	bpy.types.VIEW3D_HT_header.prepend(sculpt_header)
	bpy.types.VIEW3D_PT_tools_brush_texture.append(texture_import)

	# bpy.utils.register_class(separate_mask)



	wm = bpy.context.window_manager
	km = wm.keyconfigs.addon.keymaps.new(name='Sculpt', space_type='EMPTY')
	kmi = km.keymap_items.new(duplicate_mask.bl_idname, 'D', 'PRESS',  alt=True, shift=True)
	addon_keymaps.append((km, kmi))
	kmi = km.keymap_items.new(separate_mask.bl_idname, 'F', 'PRESS',  alt=True, shift=True)
	addon_keymaps.append((km, kmi))
	kmi = km.keymap_items.new(cut_mat_group.bl_idname, 'V', 'PRESS',  alt=True, shift=True)
	addon_keymaps.append((km, kmi))
	kmi = km.keymap_items.new(mat_mask.bl_idname, 'R', 'PRESS',  alt=True, shift=True)
	addon_keymaps.append((km, kmi))
	kmi = km.keymap_items.new(mat_select_mask.bl_idname, 'R', 'PRESS',  alt=True, shift=True, ctrl=True)
	addon_keymaps.append((km, kmi))


	kmi = km.keymap_items.new(grease_pencil_cut.bl_idname, 'R', 'PRESS',ctrl=True)
	addon_keymaps.append((km, kmi))

	kmi = km.keymap_items.new(grease_pencil_cut_v2.bl_idname, 'R', 'PRESS',shift=True)
	addon_keymaps.append((km, kmi))
	kmi = km.keymap_items.new(automirror_apply_mod.bl_idname, 'FOUR', 'PRESS',oskey=True)
	addon_keymaps.append((km, kmi))

	km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
	kmi = km.keymap_items.new(grease_pencil_cut_v2.bl_idname, 'R', 'PRESS',shift=True)
	addon_keymaps.append((km, kmi))

	km = wm.keyconfigs.addon.keymaps.new(name='Mesh', space_type='EMPTY')


	kmi = km.keymap_items.new(random_mat.bl_idname, 'TWO', 'PRESS',oskey=True)
	addon_keymaps.append((km, kmi))






def unregister():
	bpy.types.VIEW3D_HT_header.remove(sculpt_header)
	bpy.types.VIEW3D_PT_tools_brush_texture.remove(texture_import)

	# bpy.utils.unregister_class(separate_mask)



# このスクリプトを単独で実行した時に実行
if __name__ == '__main__':
	register()
