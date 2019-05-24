# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
	"name": "Keymap_Set",
	"author": "bookyakuno",
	"version": (1, 2),
	"blender": (2, 79, 0),
	"description": "Rational Keymap Set",
	"location": "This addon Setting",
	"warning": "",
	"category": "Learnbgame",
}

#
import bpy, os
from bpy.types import Menu, Header
from bpy.props import IntProperty, FloatProperty, BoolProperty
import bmesh
from mathutils import *
import math
import rna_keymap_ui



import bpy
from bpy.app.translations import pgettext_iface as iface_
from bpy.app.translations import contexts as i18n_contexts




# 翻訳辞書
translation_dict_keymap_set = {
	"en_US": {
		("*", "Delete Face By Right Click"):
			"Delete Face By Right Click",
		("*", "Sample3-7: Out of range"):
			"Sample3-7: Out of range",
		("*", "Sample3-7: No face is selected"):
			"Sample3-7: No face is selected",
		("*", "Sample3-7: Deleted Face"):
			"Sample3-7: Deleted Face",
		("*", "Sample3-7: Start deleting faces"):
			"Sample3-7: Start deleting faces",
		("*", "Sample3-7: %d face(s) are deleted"):
			"Sample3-7: %d face(s) are deleted",
		("*", "Start"):
			"Start",
		("*", "End"):
			"End",
		("*", "Sample3-7: Enabled add-on 'Sample3-7'"):
			"Sample3-7: Enabled add-on 'Sample3-7'",
		("*", "Sample3-7: Disabled add-on 'Sample3-7'"):
			"Sample3-7: Disabled add-on 'Sample3-7'"
	},
	"ja_JP": {
		("*", "It will not be saved if you change it with keymap list of this addon."):
		"このアドオンのキーマップリストによってキー変更しても保存されません。",
		("*", "Please search and change at the 'input' tab. "):
		"「入力」タブの所で検索して変更してください。",
		("*", "A checkbox enables you to enable / disable keymap."):
			"チェックボックスによってキーマップのグループを有功/無効にできます。",
		("*", "Restart Blender to checkbox apply."):
			"チェックボックスの反映には再起動が必要です。",
		# ("*", "To reflect the check box, press the button below to 'Update all addons'."):
		# "チェックボックスが反映には、下のボタンを押して'全てのアドオンを更新させます'。",
	}
}


# モジュール名をキー、ファイルパスと更新時間で構成される辞書を値とする辞書
module_mtimes = None

# 更新されたモジュール名を入れる
module_updated = set()







def reload_addon(context, module_name):
	addons = context.user_preferences.addons
	if module_name not in addons:
		return False

	addon = addons[module_name]
	module_name = addon.module
	if module_name in sys.modules:
		mod = sys.modules[module_name]
		try:
			mod.unregister()
		except:
			traceback.print_exc()
		del mod
	ccc = []

	for km, kmi in ccc:
		km.keymap_items.remove(kmi)
	# ccc.clear()


	for key in list(sys.modules):
		if key == module_name or key.startswith(module_name + '.'):
			del sys.modules[key]

	bpy.ops.wm.addon_refresh()
	try:
		mod = importlib.import_module(module_name)
		mod.register()
	except:
		# for key in list(sys.modules):
		#     if key == module_name or key.startswith(module_name + '.'):
		#         del sys.modules[key]
		# bpy.ops.wm.addon_disable(module=module_name)
		traceback.print_exc()
		return False

	mtimes = get_module_mtimes(module_name)
	module_mtimes[module_name] = mtimes[module_name]
	if module_name in module_updated:
		module_updated.remove(module_name)
	print("Reload '{}'".format(module_name))
	return True






class reveal_no_select(bpy.types.Operator):
	bl_idname = "mesh.reveal_no_select"
	bl_label = "reveal_no_select"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		obj = context.object
		bm = bmesh.from_edit_mesh(obj.data)


		# 現在の選択を頂点グループにバックアップ
		bpy.ops.object.vertex_group_assign_new()
		bpy.context.object.vertex_groups.active.name = "reveal_no_select_vgroups"

		# 表示
		bpy.ops.mesh.reveal()
		bpy.ops.mesh.select_all(action='DESELECT') #選択解除

		# 保持した頂点グループを選択
		bpy.ops.object.vertex_group_set_active(group='reveal_no_select_vgroups')
		bpy.ops.object.vertex_group_select()

		# reveal_vgroupsを除去
		bpy.ops.object.vertex_group_remove()

		return {'FINISHED'}


class reveal_no_select_object(bpy.types.Operator):
	bl_idname = "object.reveal_no_select_object"
	bl_label = "reveal_no_select_object"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):


		obj = context.object

		if len(bpy.context.selected_objects) == 0:
			bpy.ops.object.hide_view_clear()
		else:
			#  アクティブオブジェクトの定義
			# selob = bpy.context.selected_objects
			bpy.ops.group.create(name="reveal_no_select_object_gp")

			# 表示
			bpy.ops.object.hide_view_clear()
			bpy.ops.object.select_all(action='DESELECT') #選択解除
			bpy.ops.object.select_same_group(group="reveal_no_select_object_gp")
			bpy.ops.group.objects_remove(group='reveal_no_select_object_gp')


		return {'FINISHED'}





class view_selected_or_all(bpy.types.Operator):
	bl_idname = 'view3d.view_selected_or_all'
	bl_label = 'view_selected_or_all'
	bl_description = 'view_selected_or_all'
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		if context.mode =='EDIT_MESH':
			bpy.ops.object.vertex_group_assign_new()
			bpy.context.object.vertex_groups.active.name = "vgroups"
			bpy.ops.mesh.select_all(action='SELECT')
			bpy.ops.view3d.view_selected()
			bpy.ops.mesh.select_all(action='DESELECT')

			bpy.ops.object.vertex_group_set_active(group='vgroups')
			bpy.ops.object.vertex_group_select()
			bpy.ops.object.vertex_group_remove()
			bpy.ops.view3d.view_selected()

		else:
			if  len (context.selected_objects ) == 0:
				bpy.ops.view3d.view_all()
			else:
				bpy.ops.view3d.view_selected()

		return {'FINISHED'}


class WM_OT_addon_reload_all_x(bpy.types.Operator):
	bl_idname = 'wm.addon_reload_all_x'
	bl_label = 'Reload Add-ons'
	bl_description = 'Reload updated add-ons'

	def execute(self, context):
		addons = context.user_preferences.addons
		check_update()
		result = False
		for addon in addons:
			if addon.module in module_updated:
				result |= reload_addon(context, addon.module)
		if not result:
			return {'CANCELLED'}

		redraw_userprefs(context)
		return {'FINISHED'}


class ViewSelected_smart(bpy.types.Operator):
	bl_idname = "view3d.view_selected_smart"
	bl_label = "view Selected (non-zoom)"
	bl_description = "Selected ones over center of 3D perspective not (zoom)"
	bl_options = {'REGISTER'}

	def execute(self, context):
		pre_view_location = context.region_data.view_location[:]
		smooth_view = context.user_preferences.view.smooth_view
		context.user_preferences.view.smooth_view = 0
		view_distance = context.region_data.view_distance
		bpy.ops.view3d.view_selected()
		context.region_data.view_distance = view_distance
		context.user_preferences.view.smooth_view = smooth_view
		context.region_data.update()
		new_view_location = context.region_data.view_location[:]
		context.region_data.view_location = pre_view_location[:]
		pre_cursor_location = bpy.context.space_data.cursor_location[:]
		bpy.context.space_data.cursor_location = new_view_location[:]
		bpy.ops.view3d.view_center_cursor()
		bpy.context.space_data.cursor_location = pre_cursor_location[:]
		return {'FINISHED'}



class object_delete_silent(bpy.types.Operator):
	bl_idname = "object.object_delete_silent"
	bl_label = "object_delete_silent"
	bl_description = "Delete without checking all selected object"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		bpy.ops.object.delete()
		return {'FINISHED'}

class graph_delete_silent(bpy.types.Operator):
	bl_idname = "graph.graph_delete_silent"
	bl_label = "graph_delete_silent"
	bl_description = "Delete without checking all selected object"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		bpy.ops.graph.delete()
		return {'FINISHED'}

class action_delete_silent(bpy.types.Operator):
	bl_idname = "action.action_delete_silent"
	bl_label = "action_delete_silent"
	bl_description = "Delete without checking all selected object"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		bpy.ops.action.delete()
		return {'FINISHED'}


class DeleteBySelectMode_x(bpy.types.Operator):
	bl_idname = "mesh.delete_by_select_mode_x"
	bl_label = "delete by mode"
	bl_description = "delete by select mode"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		mode = context.tool_settings.mesh_select_mode[:]
		if (mode[0]):
			bpy.ops.mesh.delete(type="VERT")
		elif (mode[1]):
			bpy.ops.mesh.delete(type="EDGE")
		elif (mode[2]):
			bpy.ops.mesh.delete(type="FACE")
		return {'FINISHED'}


class KeymapSetMenuPrefs(bpy.types.AddonPreferences):
	bl_idname = __name__


	# boolean = BoolProperty(
	# 		name="Example Boolean",
	# 		default=False,
	# 		)
	select_border = BoolProperty(
			name="Border Select",
			default=True,
			)

	select_link = BoolProperty(
			name="Select Link",
			default=True,
			)

	mode_set_keymap = BoolProperty(
			name="Mode Set",
			default=True,
			)

	view_numpad = BoolProperty(
			name="Navigation",
			default=True,
			)

	etc_keymap = BoolProperty(
			name="Etc",
			default=True,
			)

	delete_keymap = BoolProperty(
			name="Delete",
			default=True,
			)
	mesh_tool_keymap = BoolProperty(
			name="Mesh Tool",
			default=True,
			)

	view_control_keymap = BoolProperty(
			name="View Control",
			default=True,
			)



	modifier_keymap = BoolProperty(
			name="Modifier",
			default=True,
			)


	transform_keymap = BoolProperty(
			name="Transform",
			default=False,
			)




######################################################
######################################################

	bpy.types.Scene.select_border_tab = bpy.props.BoolProperty(default=False)
	bpy.types.Scene.select_linked_tab = bpy.props.BoolProperty(default=False)
	bpy.types.Scene.view_numpad_tab =   bpy.props.BoolProperty(default=False)
	bpy.types.Scene.mode_set_tab =      bpy.props.BoolProperty(default=False)
	bpy.types.Scene.etc_keymap          = bpy.props.BoolProperty(default=False)
	bpy.types.Scene.delete_keymap   = bpy.props.BoolProperty(default=False)
	bpy.types.Scene.mesh_tool_keymap    = bpy.props.BoolProperty(default=False)
	bpy.types.Scene.view_control_keymap = bpy.props.BoolProperty(default=False)
	bpy.types.Scene.modifier_keymap = bpy.props.BoolProperty(default=False)
	bpy.types.Scene.transform_keymap = bpy.props.BoolProperty(default=False)




	def draw(self, context):
		layout = self.layout
		user_preferences = context.user_preferences
		addon_prefs = user_preferences.addons[__name__].preferences

#######################################################
#######################################################
# UI


		layout.label(
		text="It will not be saved if you change it with keymap list of this addon."
		)
		layout.label(
		text="Please search and change at the 'input' tab. "
		)
		layout.label(
		text=		"A checkbox enables you to enable / disable keymap.")
		layout.label(
		text=		"Restart Blender to checkbox apply.", icon='FILE_REFRESH')
		# text=		"To reflect the check box, press the button below to 'Update all addons'.", icon='FILE_REFRESH')
		# layout.operator('wm.addon_reload_all_x', text='Reload',icon='FILE_REFRESH')



		# 	このアドオンのkeymapリストによって変更しても保存されません。 "入力"タブの所で検索して変更してください。
		# チェックボックスによってkeymap を有功/無効にできます。それには再起動が必要です。


#######################################################
#######################################################
#  Select Border
		col = layout.column(align=True)
		row = col.row(align=True)
		row.prop(self, "select_border")
		row.prop(context.scene, "select_border_tab", text="Select Border >> Mouse Drag", icon="URL")


		if context.scene.select_border_tab:
			col = layout.column()
			kc = bpy.context.window_manager.keyconfigs.addon
			for km, kmi in select_border_keymap:
				km = km.active()
				col.context_pointer_set("keymap", km)
				rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)


#######################################################
#######################################################
#  Select Linked
		col = layout.column(align=True)
		row = col.row(align=True)
		row.prop(self, "select_link")
		row.prop(context.scene, "select_linked_tab", text="Select Linked >> Double Click", icon="URL")

		if context.scene.select_linked_tab:
			col = layout.column()
			kc = bpy.context.window_manager.keyconfigs.addon
			for km, kmi in select_linked_keymap:
				km = km.active()
				col.context_pointer_set("keymap", km)
				rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)




#######################################################
#######################################################
#  delete_keymap
		col = layout.column(align=True)
		row = col.row(align=True)
		row.prop(self, "delete_keymap")
		row.prop(context.scene, "delete_keymap", text="Delete >> BACK SPACE", icon="URL")


		if context.scene.delete_keymap:
			col = layout.column()
			kc = bpy.context.window_manager.keyconfigs.addon
			for km, kmi in delete_keymap:
				km = km.active()
				col.context_pointer_set("keymap", km)
				rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)


#######################################################
#######################################################
#  view numpad
		col = layout.column(align=True)
		row = col.row(align=True)
		row.prop(self, "view_numpad")
		row.prop(context.scene, "view_numpad_tab", text="View Numpad  >> 1,2,3,4,5", icon="URL")



		if context.scene.view_numpad_tab:
			col = layout.column()
			kc = bpy.context.window_manager.keyconfigs.addon
			for km, kmi in view_numpad_keymap:
				km = km.active()
				col.context_pointer_set("keymap", km)
				rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)


#######################################################
#######################################################
#  Mode Set
		col = layout.column(align=True)
		row = col.row(align=True)
		row.prop(self, "mode_set_keymap")
		row.prop(context.scene, "mode_set_tab", text="Mode Set >> Tab", icon="URL")


		if context.scene.mode_set_tab:
			col = layout.column()
			kc = bpy.context.window_manager.keyconfigs.addon
			for km, kmi in mode_set_keymap:
				km = km.active()
				col.context_pointer_set("keymap", km)
				rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)

#######################################################
#######################################################
#  view_control_keymap
		col = layout.column(align=True)
		row = col.row(align=True)
		row.prop(self, "view_control_keymap")
		row.prop(context.scene, "view_control_keymap", text="View Control  >> ", icon="URL")



		if context.scene.view_control_keymap:
			col = layout.column()
			kc = bpy.context.window_manager.keyconfigs.addon
			for km, kmi in view_control_keymap:
				km = km.active()
				col.context_pointer_set("keymap", km)
				rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)


#######################################################
#######################################################
#  transform_keymap
		col = layout.column(align=True)
		row = col.row(align=True)
		row.prop(self, "transform_keymap")
		row.prop(context.scene, "transform_keymap", text="translate,rotate >> A,D", icon="URL")


		if context.scene.transform_keymap:
			col = layout.column()
			kc = bpy.context.window_manager.keyconfigs.addon
			for km, kmi in transform_keymap:
				km = km.active()
				col.context_pointer_set("keymap", km)
				rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)



#######################################################
#######################################################
#  etc_keymap
		col = layout.column(align=True)
		row = col.row(align=True)
		row.prop(self, "etc_keymap")
		row.prop(context.scene, "etc_keymap", text="etc_keymap...", icon="URL")


		if context.scene.etc_keymap:
			col = layout.column()
			kc = bpy.context.window_manager.keyconfigs.addon
			for km, kmi in etc_keymap:
				km = km.active()
				col.context_pointer_set("keymap", km)
				rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)




#######################################################
#######################################################

select_border_keymap = []

select_linked_keymap = []

view_numpad_keymap = []

view_control_keymap = []

mode_set_keymap = []

etc_keymap = []

delete_keymap = []

mesh_tool_keymap = []

view_control_keymap = []

modifier_keymap = []

transform_keymap = []

#######################################################
#######################################################







################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
# # # # # # # # プロパティの指定に必要なもの
def kmi_props_setattr(kmi_props, attr, value):
	try:
		setattr(kmi_props, attr, value)
	except AttributeError:
		print("Warning: property '%s' not found in keymap item '%s'" %
			  (attr, kmi_props.__class__.__name__))
	except Exception as e:
		print("Warning: %r" % e)

# # # # # # # #
################################################################
#------------------- REGISTER ------------------------------

def register():
	bpy.utils.register_module(__name__)
	wm = bpy.context.window_manager
	if wm.keyconfigs.addon:
#
#  ################################################################
#
		user_preferences = bpy.context.user_preferences
		addon_prefs = user_preferences.addons[__name__].preferences

######################################################
######################################################
#boader select
		# 矩形選択
		if addon_prefs.select_border == True:


			######################################################
			######################################################
			# select mouse Drag
			#

			################################################################
			km = wm.keyconfigs.addon.keymaps.new('Info',space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('--  --', 'MINUS', 'PRESS')
			kmi.active = False
			select_border_keymap.append((km, kmi))
			################################################################
			km = wm.keyconfigs.addon.keymaps.new('Info',space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('-- select mouse Drag --', 'MINUS', 'PRESS')
			kmi.active = False
			select_border_keymap.append((km, kmi))
			################################################################



			# Map Gesture Border
			# km = wm.keyconfigs.addon.keymaps.new('Gesture Border', space_type='EMPTY', region_type='WINDOW', modal=True)
			#
			# kmi = km.keymap_items.new_modal('DESELECT', 'RIGHTMOUSE', 'PRESS', alt=True)
			# kmi.active = True
			# select_border_keymap.append((km, kmi))


			# km = wm.keyconfigs.addon.keymaps.new('Gesture Border', space_type='EMPTY', region_type='WINDOW', modal=True)
			# kmi = km.keymap_items.new_modal('DESELECT', 'H', 'RELEASE')
			# kmi.active = True
			# select_border_keymap.append((km, kmi))


			# km = wm.keyconfigs.addon.keymaps.new('Gesture Border', space_type='EMPTY', region_type='WINDOW', modal=True)
			# kmi = km.keymap_items.new_modal('DESELECT', 'RIGHTMOUSE', 'RELEASE', alt=True)
			# kmi.active = True
			# select_border_keymap.append((km, kmi))



			# km = wm.keyconfigs.addon.keymaps.new('3D View', space_type='VIEW_3D', region_type='WINDOW', modal=False)
			# kmi = km.keymap_items.new('view3d.select_border', 'EVT_TWEAK_R', 'ANY', alt=True)
			# kmi.active = True
			# select_border_keymap.append((km, kmi))


			km = wm.keyconfigs.addon.keymaps.new('3D View', space_type='VIEW_3D', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('view3d.select_border', 'EVT_TWEAK_L', 'ANY')
			kmi_props_setattr(kmi.properties, 'extend', False)
			kmi.active = True
			select_border_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Animation Channels', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('anim.channels_select_border', 'EVT_TWEAK_L', 'ANY')
			kmi_props_setattr(kmi.properties, 'extend', False)
			kmi.active = True
			select_border_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Grease Pencil Stroke Edit Mode', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('gpencil.select_border', 'EVT_TWEAK_L', 'ANY')
			kmi_props_setattr(kmi.properties, 'extend', False)
			kmi.active = True
			select_border_keymap.append((km, kmi))


			km = wm.keyconfigs.addon.keymaps.new('Weight Paint Vertex Selection', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('view3d.select_border', 'EVT_TWEAK_L', 'ANY')
			kmi_props_setattr(kmi.properties, 'extend', False)
			kmi.active = True
			select_border_keymap.append((km, kmi))


			km = wm.keyconfigs.addon.keymaps.new('UV Editor', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('uv.select_border', 'EVT_TWEAK_L', 'ANY')
			kmi_props_setattr(kmi.properties, 'extend', False)
			kmi.active = True
			select_border_keymap.append((km, kmi))


			km = wm.keyconfigs.addon.keymaps.new('Graph Editor', space_type='GRAPH_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('graph.select_border', 'EVT_TWEAK_L', 'ANY')
			kmi_props_setattr(kmi.properties, 'extend', False)
			kmi.active = True
			select_border_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Node Editor', space_type='NODE_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('node.select_border', 'EVT_TWEAK_L', 'ANY')
			kmi_props_setattr(kmi.properties, 'extend', False)
			kmi.active = True
			select_border_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Dopesheet', space_type='DOPESHEET_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('action.select_border', 'EVT_TWEAK_L', 'ANY')
			kmi_props_setattr(kmi.properties, 'extend', False)
			kmi.active = True
			select_border_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('NLA Editor', space_type='NLA_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('nla.select_border', 'EVT_TWEAK_L', 'ANY')
			kmi_props_setattr(kmi.properties, 'extend', False)
			kmi.active = True
			select_border_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Sequencer', space_type='SEQUENCE_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('sequencer.select_border', 'EVT_TWEAK_L', 'ANY')
			kmi_props_setattr(kmi.properties, 'extend', False)
			kmi.active = True
			select_border_keymap.append((km, kmi))


			km = wm.keyconfigs.addon.keymaps.new('Clip Editor', space_type='CLIP_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('clip.select_border', 'EVT_TWEAK_L', 'ANY')
			kmi_props_setattr(kmi.properties, 'extend', False)
			kmi.active = True
			select_border_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Clip Graph Editor', space_type='CLIP_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('clip.select_border', 'EVT_TWEAK_L', 'ANY')
			kmi_props_setattr(kmi.properties, 'extend', False)
			kmi.active = True
			select_border_keymap.append((km, kmi))


			######################################################
			######################################################
			# select mouse Drag + shift
			#


			################################################################
			km = wm.keyconfigs.addon.keymaps.new('Info',space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('--  --', 'MINUS', 'PRESS')
			kmi.active = False
			select_border_keymap.append((km, kmi))
			################################################################
			km = wm.keyconfigs.addon.keymaps.new('Info',space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('-- select mouse Drag + shift --', 'MINUS', 'PRESS')
			kmi.active = False
			select_border_keymap.append((km, kmi))
			################################################################



			km = wm.keyconfigs.addon.keymaps.new('3D View', space_type='VIEW_3D', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('view3d.select_border', 'EVT_TWEAK_L', 'ANY', shift=True)
			kmi.active = True
			select_border_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Animation Channels', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('anim.channels_select_border', 'EVT_TWEAK_L', 'ANY', shift=True)
			kmi.active = True
			select_border_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Grease Pencil Stroke Edit Mode', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('gpencil.select_border', 'EVT_TWEAK_L', 'ANY', shift=True)
			kmi.active = True
			select_border_keymap.append((km, kmi))


			km = wm.keyconfigs.addon.keymaps.new('Weight Paint Vertex Selection', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('view3d.select_border', 'EVT_TWEAK_L', 'ANY', shift=True)
			kmi.active = True
			select_border_keymap.append((km, kmi))



			km = wm.keyconfigs.addon.keymaps.new('UV Editor', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('uv.select_border', 'EVT_TWEAK_L', 'ANY', shift=True)
			kmi.active = True
			select_border_keymap.append((km, kmi))


			km = wm.keyconfigs.addon.keymaps.new('Graph Editor', space_type='GRAPH_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('graph.select_border', 'EVT_TWEAK_L', 'ANY', shift=True)
			kmi.active = True
			select_border_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Node Editor', space_type='NODE_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('node.select_border', 'EVT_TWEAK_L', 'ANY', shift=True)
			kmi.active = True
			select_border_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Dopesheet', space_type='DOPESHEET_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('action.select_border', 'EVT_TWEAK_L', 'ANY', shift=True)
			kmi.active = True
			select_border_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('NLA Editor', space_type='NLA_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('nla.select_border', 'EVT_TWEAK_L', 'ANY', shift=True)
			kmi.active = True
			select_border_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Sequencer', space_type='SEQUENCE_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('sequencer.select_border', 'EVT_TWEAK_L', 'ANY', shift=True)
			kmi.active = True
			select_border_keymap.append((km, kmi))


			km = wm.keyconfigs.addon.keymaps.new('Clip Editor', space_type='CLIP_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('clip.select_border', 'EVT_TWEAK_L', 'ANY', shift=True)
			kmi.active = True
			select_border_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Clip Graph Editor', space_type='CLIP_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('clip.select_border', 'EVT_TWEAK_L', 'ANY', shift=True)
			kmi.active = True
			select_border_keymap.append((km, kmi))











######################################################

			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('view3d.manipulator', 'SELECTMOUSE', 'PRESS', any=True)
			kmi_props_setattr(kmi.properties, 'release_confirm', True)
			kmi.active = True
			select_border_keymap.append((km, kmi))

######################################################







		######################################################
		######################################################
		#Select Linked
		if addon_prefs.select_link == True:

			km = wm.keyconfigs.addon.keymaps.new('Mesh', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('mesh.select_linked_pick', 'SELECTMOUSE', 'DOUBLE_CLICK')
			kmi_props_setattr(kmi.properties, 'limit', True)
			kmi_props_setattr(kmi.properties, 'deselect', False)
			kmi.active = True
			select_linked_keymap.append((km, kmi))


			km = wm.keyconfigs.addon.keymaps.new('Mesh', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('mesh.select_linked_pick', 'SELECTMOUSE', 'DOUBLE_CLICK', shift=True)
			kmi_props_setattr(kmi.properties, 'limit', True)
			kmi_props_setattr(kmi.properties, 'deselect', False)
			kmi.active = True
			select_linked_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Mesh', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('mesh.select_linked_pick', 'SELECTMOUSE', 'DOUBLE_CLICK', ctrl=True)
			kmi_props_setattr(kmi.properties, 'limit', True)
			kmi_props_setattr(kmi.properties, 'deselect', True)
			kmi.active = False
			select_linked_keymap.append((km, kmi))




			#UV Select Linked
			km = wm.keyconfigs.addon.keymaps.new('UV Editor', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('uv.select_linked', 'SELECTMOUSE', 'DOUBLE_CLICK')
			kmi.active = True
			select_linked_keymap.append((km, kmi))


			km = wm.keyconfigs.addon.keymaps.new('UV Editor', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('uv.select_linked', 'SELECTMOUSE', 'DOUBLE_CLICK', shift=True)
			kmi_props_setattr(kmi.properties, 'extend', True)
			kmi.active = True
			select_linked_keymap.append((km, kmi))







 #
 #
 # # # # # # # # #
 # ################################################################
	# 	km = wm.keyconfigs.addon.keymaps.new('Info',space_type='EMPTY', region_type='WINDOW', modal=False)
	# 	kmi = km.keymap_items.new('--  --', 'MINUS', 'PRESS')
	# 	kmi.active = False
	# 	etc_keymap.append((km, kmi))
 # ################################################################



		if addon_prefs.etc_keymap == True:
			################################################################
			km = wm.keyconfigs.addon.keymaps.new('Info',space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('-- Delete object (Nomessage) --', 'MINUS', 'PRESS')
			kmi.active = False
			delete_keymap.append((km, kmi))
			################################################################

			km = wm.keyconfigs.addon.keymaps.new('Object Mode', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('object.object_delete_silent', 'BACK_SPACE', 'PRESS')
			kmi.active = True
			delete_keymap.append((km, kmi))

			################################################################
			km = wm.keyconfigs.addon.keymaps.new('Info',space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('-- Delete Graph key (Nomessage) --', 'MINUS', 'PRESS')
			kmi.active = False
			delete_keymap.append((km, kmi))
			################################################################

			km = wm.keyconfigs.addon.keymaps.new('Graph Editor', space_type='GRAPH_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('graph.graph_delete_silent', 'BACK_SPACE', 'PRESS')
			kmi.active = True
			delete_keymap.append((km, kmi))
			################################################################
			km = wm.keyconfigs.addon.keymaps.new('Info',space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('-- Delete Dopesheet key (Nomessage) --', 'MINUS', 'PRESS')
			kmi.active = False
			delete_keymap.append((km, kmi))
			################################################################

			km = wm.keyconfigs.addon.keymaps.new('Dopesheet', space_type='DOPESHEET_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('action.action_delete_silent', 'BACK_SPACE', 'PRESS')
			kmi.active = True
			delete_keymap.append((km, kmi))

			################################################################
			km = wm.keyconfigs.addon.keymaps.new('Info',space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('-- Delete Mesh(Auto mesh type Delete) --', 'MINUS', 'PRESS')
			kmi.active = False
			delete_keymap.append((km, kmi))
			################################################################


			km = wm.keyconfigs.addon.keymaps.new('Mesh', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('mesh.delete_by_select_mode_x', 'BACK_SPACE', 'PRESS')
			kmi.active = True
			delete_keymap.append((km, kmi))



			km = wm.keyconfigs.addon.keymaps.new('Mesh', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('mesh.dissolve_mode', 'BACK_SPACE', 'PRESS', alt=True)
			kmi.active = True
			delete_keymap.append((km, kmi))



			km = wm.keyconfigs.addon.keymaps.new('Mesh', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('mesh.merge', 'BACK_SPACE', 'PRESS', shift=True)
			kmi_props_setattr(kmi.properties, 'type', 'CENTER')
			kmi.active = True
			delete_keymap.append((km, kmi))








		######################################################
		######################################################
		# 視点変更
		#------------3d View
		# 1,2,3
		if addon_prefs.view_numpad == True:

			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('view3d.viewnumpad', 'ONE', 'PRESS')
			kmi_props_setattr(kmi.properties, 'type', 'FRONT')
			kmi.active = True
			view_numpad_keymap.append((km, kmi))


			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('view3d.viewnumpad', 'TWO', 'PRESS')
			kmi_props_setattr(kmi.properties, 'type', 'RIGHT')
			kmi.active = True
			view_numpad_keymap.append((km, kmi))


			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('view3d.viewnumpad', 'THREE', 'PRESS')
			kmi_props_setattr(kmi.properties, 'type', 'TOP')
			kmi.active = True
			view_numpad_keymap.append((km, kmi))


			# 1,2,3 + Ctrl
			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('view3d.viewnumpad', 'ONE', 'PRESS', ctrl=True)
			kmi_props_setattr(kmi.properties, 'type', 'BACK')
			kmi.active = True
			view_numpad_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('view3d.viewnumpad', 'TWO', 'PRESS', ctrl=True)
			kmi_props_setattr(kmi.properties, 'type', 'LEFT')
			kmi.active = True
			view_numpad_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('view3d.viewnumpad', 'THREE', 'PRESS', ctrl=True)
			kmi_props_setattr(kmi.properties, 'type', 'BOTTOM')
			kmi.active = True
			view_numpad_keymap.append((km, kmi))


#Object
			km = wm.keyconfigs.addon.keymaps.new('Object Mode', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('view3d.viewnumpad', 'ONE', 'PRESS', ctrl=True)
			kmi_props_setattr(kmi.properties, 'type', 'BACK')
			kmi.active = True
			view_numpad_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Object Mode', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('view3d.viewnumpad', 'TWO', 'PRESS', ctrl=True)
			kmi_props_setattr(kmi.properties, 'type', 'LEFT')
			kmi.active = True
			view_numpad_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Object Mode', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('view3d.viewnumpad', 'THREE', 'PRESS', ctrl=True)
			kmi_props_setattr(kmi.properties, 'type', 'BOTTOM')
			kmi.active = True
			view_numpad_keymap.append((km, kmi))
#Mesh
			km = wm.keyconfigs.addon.keymaps.new('Mesh', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('view3d.viewnumpad', 'ONE', 'PRESS', ctrl=True)
			kmi_props_setattr(kmi.properties, 'type', 'BACK')
			kmi.active = True
			view_numpad_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Mesh', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('view3d.viewnumpad', 'TWO', 'PRESS', ctrl=True)
			kmi_props_setattr(kmi.properties, 'type', 'LEFT')
			kmi.active = True
			view_numpad_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Mesh', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('view3d.viewnumpad', 'THREE', 'PRESS', ctrl=True)
			kmi_props_setattr(kmi.properties, 'type', 'BOTTOM')
			kmi.active = True
			view_numpad_keymap.append((km, kmi))
#Sculpt
			km = wm.keyconfigs.addon.keymaps.new('Sculpt', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('view3d.viewnumpad', 'ONE', 'PRESS', ctrl=True)
			kmi_props_setattr(kmi.properties, 'type', 'BACK')
			kmi.active = True
			view_numpad_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Sculpt', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('view3d.viewnumpad', 'TWO', 'PRESS', ctrl=True)
			kmi_props_setattr(kmi.properties, 'type', 'LEFT')
			kmi.active = True
			view_numpad_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Sculpt', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('view3d.viewnumpad', 'THREE', 'PRESS', ctrl=True)
			kmi_props_setattr(kmi.properties, 'type', 'BOTTOM')
			kmi.active = True
			view_numpad_keymap.append((km, kmi))

			# align_active …… 1,2,3 + Alt
			#
			# km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			#
			# kmi = km.keymap_items.new('view3d.viewnumpad', 'ONE', 'PRESS', alt=True)
			# kmi_props_setattr(kmi.properties, 'type', 'TOP')
			# kmi.active = True
			# view_numpad_keymap.append((km, kmi))
			# km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			#
			# kmi = km.keymap_items.new('view3d.viewnumpad', 'TWO', 'PRESS', alt=True)
			# kmi_props_setattr(kmi.properties, 'type', 'RIGHT')
			# kmi_props_setattr(kmi.properties, 'align_active', True)
			# kmi.active = True
			# view_numpad_keymap.append((km, kmi))
			#
			#
			# km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			#
			# kmi = km.keymap_items.new('view3d.viewnumpad', 'THREE', 'PRESS', alt=True)
			# kmi_props_setattr(kmi.properties, 'type', 'FRONT')
			# kmi_props_setattr(kmi.properties, 'align_active', True)
			# kmi.active = True
			# view_numpad_keymap.append((km, kmi))
			#


# Camera

			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('view3d.viewnumpad', 'FOUR', 'PRESS')
			kmi_props_setattr(kmi.properties, 'type', 'CAMERA')
			kmi.active = True
			view_numpad_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('view3d.object_as_camera', 'FOUR', 'PRESS',shift=True, ctrl=True,)
			kmi_props_setattr(kmi.properties, 'type', 'CAMERA')
			kmi.active = True
			view_numpad_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('view3d.view_persportho', 'FOUR', 'PRESS',shift=True)
			kmi.active = True
			view_numpad_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('view3d.camera_to_view', 'FOUR', 'PRESS',ctrl=True,alt=True)
			kmi.active = True
			view_numpad_keymap.append((km, kmi))




			# km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			# kmi = km.keymap_items.new('wm.context_toggle', 'FOUR', 'PRESS', ctrl=True)
			# kmi_props_setattr(kmi.properties, 'data_path', 'space_data.lock_camera')
			# kmi.active = True
			# view_numpad_keymap.append((km, kmi))



			km = wm.keyconfigs.addon.keymaps.new('Sculpt', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('wm.context_toggle', 'FOUR', 'PRESS', ctrl=True)
			kmi_props_setattr(kmi.properties, 'data_path', 'space_data.lock_camera')
			kmi.active = True
			view_numpad_keymap.append((km, kmi))




			km = wm.keyconfigs.addon.keymaps.new('Object Mode', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('wm.context_toggle', 'FOUR', 'PRESS', ctrl=True)
			kmi_props_setattr(kmi.properties, 'data_path', 'space_data.lock_camera')
			kmi.active = True
			view_numpad_keymap.append((km, kmi))




			km = wm.keyconfigs.addon.keymaps.new('Mesh', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('wm.context_toggle', 'FOUR', 'PRESS', ctrl=True)
			kmi_props_setattr(kmi.properties, 'data_path', 'space_data.lock_camera')
			kmi.active = True
			view_numpad_keymap.append((km, kmi))








# Render

			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('render.render', 'FIVE', 'PRESS')
			kmi_props_setattr(kmi.properties, 'animation', False)
			kmi_props_setattr(kmi.properties, 'use_viewport', True)
			kmi.active = True
			view_numpad_keymap.append((km, kmi))



			# # # # # # # #
			################################################################
			km = wm.keyconfigs.addon.keymaps.new('Info',space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('-- Modifier --', 'MINUS', 'PRESS')
			kmi.active = False
			view_numpad_keymap.append((km, kmi))
			 ################################################################
			 # # # # # # # #


			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('object.subdivision_set', 'ONE', 'PRESS', oskey=True)
			kmi_props_setattr(kmi.properties, 'level', 0)
			kmi.active = True
			view_numpad_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('object.subdivision_set', 'THREE', 'PRESS', oskey=True)
			kmi_props_setattr(kmi.properties, 'level', 2)
			kmi.active = True
			view_numpad_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('object.subdivision_set', 'ONE', 'PRESS', alt=True)
			kmi_props_setattr(kmi.properties, 'level', 0)
			kmi.active = True
			view_numpad_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('object.subdivision_set', 'THREE', 'PRESS', alt=True)
			kmi_props_setattr(kmi.properties, 'level', 2)
			kmi.active = True
			view_numpad_keymap.append((km, kmi))








 #
 # # # # # # # # #
 # ################################################################
	# 	km = wm.keyconfigs.addon.keymaps.new('Info',space_type='EMPTY', region_type='WINDOW', modal=False)
	# 	kmi = km.keymap_items.new('--  --', 'MINUS', 'PRESS')
	# 	kmi.active = False
	# 	etc_keymap.append((km, kmi))
 # ################################################################
 # ################################################################
	# 	km = wm.keyconfigs.addon.keymaps.new('Info',space_type='EMPTY', region_type='WINDOW', modal=False)
	# 	kmi = km.keymap_items.new('-- Transform AXIS-Y >> C --', 'MINUS', 'PRESS')
	# 	kmi.active = False
	# 	etc_keymap.append((km, kmi))
 # ################################################################
 # # # # # # # # #





		# #
		# km = bpy.context.window_manager.keyconfigs.addon.keymaps.new('Transform Modal Map', space_type='EMPTY', region_type='WINDOW', modal=True)
		# kmi = km.keymap_items.new_modal('PLANE_Y', 'C', 'PRESS', shift=True)
		# kmi.active = True
		# etc_keymap.append((km, kmi))
		#
		# km = bpy.context.window_manager.keyconfigs.addon.keymaps.new('Transform Modal Map', space_type='EMPTY', region_type='WINDOW', modal=True)
		# kmi = km.keymap_items.new_modal('AXIS_Y', 'C', 'PRESS', any=True)
		# kmi.active = True
		# etc_keymap.append((km, kmi))
		#










		if addon_prefs.view_control_keymap == True:



			# # # # # # # #
			################################################################
			# km = wm.keyconfigs.addon.keymaps.new('Info',space_type='EMPTY', region_type='WINDOW', modal=False)
			# kmi = km.keymap_items.new('--  --', 'MINUS', 'PRESS')
			# kmi.active = False
			# view_control_keymap.append((km, kmi))
			################################################################
			################################################################
			km = wm.keyconfigs.addon.keymaps.new('Info',space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('-- View Rotate/move --', 'MINUS', 'PRESS')
			kmi.active = False
			view_control_keymap.append((km, kmi))
			################################################################
			# # # # # # # #

			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('view3d.rotate', 'SELECTMOUSE', 'PRESS', oskey=True)
			kmi.active = True
			view_control_keymap.append((km, kmi))


			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('view3d.zoom', 'ACTIONMOUSE', 'PRESS', oskey=True, ctrl=True)
			kmi.active = True
			view_control_keymap.append((km, kmi))
			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('view3d.zoom', 'MIDDLEMOUSE', 'PRESS', oskey=True, ctrl=True)
			kmi.active = True
			view_control_keymap.append((km, kmi))


			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('view3d.move', 'RIGHTMOUSE', 'PRESS', oskey=True)
			kmi.active = True
			view_control_keymap.append((km, kmi))
			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('view3d.move', 'MIDDLEMOUSE', 'PRESS', oskey=True)
			kmi.active = True
			view_control_keymap.append((km, kmi))

			################################################################
			km = wm.keyconfigs.addon.keymaps.new('Info',space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('--  --', 'MINUS', 'PRESS')
			kmi.active = False
			view_control_keymap.append((km, kmi))
			################################################################
			km = wm.keyconfigs.addon.keymaps.new('Info',space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('-- show only render  >>   shift + alt Z', 'MINUS', 'PRESS')
			kmi.active = False
			view_control_keymap.append((km, kmi))
			################################################################
			################################################################
			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('wm.context_toggle', 'Z', 'PRESS', shift=True,alt=True)
			kmi_props_setattr(kmi.properties, 'data_path', 'space_data.show_only_render')
			kmi.active = True
			view_control_keymap.append((km, kmi))



			################################################################
			km = wm.keyconfigs.addon.keymaps.new('Info',space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('--  --', 'MINUS', 'PRESS')
			kmi.active = False
			view_control_keymap.append((km, kmi))
			################################################################
			km = wm.keyconfigs.addon.keymaps.new('Info',space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('-- view all / selected  >>  Z --', 'MINUS', 'PRESS')
			kmi.active = False
			view_control_keymap.append((km, kmi))
			################################################################





			######################################################
			######################################################
			# view select

			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('view3d.view_all', 'A', 'PRESS', ctrl=True, oskey=True)
			kmi.active = True
			view_control_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('view3d.view_all', 'Z', 'PRESS', shift=True)
			kmi.active = True
			view_control_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('view3d.view_selected_or_all', 'A', 'PRESS', shift=True, oskey=True)
			kmi.active = True
			view_control_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('view3d.view_selected_or_all', 'Z', 'PRESS')
			kmi.active = True
			view_control_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Graph Editor', space_type='GRAPH_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('graph.view_selected', 'Z', 'PRESS')
			kmi.active = True
			view_control_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Image', space_type='IMAGE_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('image.view_all', 'Z', 'PRESS')
			kmi_props_setattr(kmi.properties, 'fit_view', True)
			kmi.active = True
			view_control_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Node Editor', space_type='NODE_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('node.view_selected', 'Z', 'PRESS')
			kmi.active = True
			view_control_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Dopesheet', space_type='DOPESHEET_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('action.view_selected', 'Z', 'PRESS')
			kmi.active = True
			view_control_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('NLA Editor', space_type='NLA_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('nla.view_selected', 'Z', 'PRESS')
			kmi.active = True
			view_control_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Sequencer', space_type='SEQUENCE_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('sequencer.view_selected', 'Z', 'PRESS')
			kmi.active = True
			view_control_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Clip Editor', space_type='CLIP_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('clip.view_selected', 'Z', 'PRESS')
			kmi.active = True
			view_control_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Timeline', space_type='TIMELINE', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('time.view_all', 'Z', 'PRESS')
			kmi.active = True
			view_control_keymap.append((km, kmi))





######################################################
######################################################
# mose set
		if addon_prefs.mode_set_keymap == True:


			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('object.mode_set', 'TAB', 'PRESS', shift=True)
			kmi_props_setattr(kmi.properties, 'mode', 'POSE')
			kmi.active = True
			mode_set_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Pose', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('object.mode_set', 'TAB', 'PRESS', shift=True)
			kmi_props_setattr(kmi.properties, 'mode', 'OBJECT')
			kmi.active = True
			mode_set_keymap.append((km, kmi))



	#Sculpt mode
			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('object.mode_set', 'TAB', 'PRESS', shift=True)
			kmi_props_setattr(kmi.properties, 'mode', 'SCULPT')
			kmi.active = True
			mode_set_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Sculpt', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('object.mode_set', 'TAB', 'PRESS', shift=True)
			kmi_props_setattr(kmi.properties, 'mode', 'OBJECT')
			kmi.active = True
			mode_set_keymap.append((km, kmi))



	#Weight paint
			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('object.mode_set', 'TAB', 'PRESS', alt=True)
			kmi_props_setattr(kmi.properties, 'mode', 'WEIGHT_PAINT')
			kmi.active = True
			mode_set_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Weight Paint', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('object.mode_set', 'TAB', 'PRESS', alt=True)
			kmi_props_setattr(kmi.properties, 'mode', 'OBJECT')
			kmi.active = True
			mode_set_keymap.append((km, kmi))





	 #Texture paint
			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('object.mode_set', 'TAB', 'PRESS', ctrl=True,oskey=True)
			kmi_props_setattr(kmi.properties, 'mode', 'TEXTURE_PAINT')
			kmi.active = True
			mode_set_keymap.append((km, kmi))
			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('object.mode_set', 'TAB', 'PRESS', ctrl=True, shift=True)
			kmi_props_setattr(kmi.properties, 'mode', 'TEXTURE_PAINT')
			kmi.active = True
			mode_set_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Image Paint', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('object.mode_set', 'TAB', 'PRESS', ctrl=True)
			kmi_props_setattr(kmi.properties, 'mode', 'OBJECT')
			kmi.active = True
			mode_set_keymap.append((km, kmi))


	#Vertex paint
			km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
			kmi = km.keymap_items.new('object.mode_set', 'TAB', 'PRESS', ctrl=True, alt=True)
			kmi_props_setattr(kmi.properties, 'mode', 'VERTEX_PAINT')
			kmi.active = True
			mode_set_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Vertex Paint', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('object.mode_set', 'TAB', 'PRESS', ctrl=True, alt=True)
			kmi_props_setattr(kmi.properties, 'mode', 'OBJECT')
			kmi.active = True
			mode_set_keymap.append((km, kmi))






		if addon_prefs.etc_keymap == True:

		 # # # # # # # #
		 ################################################################
				# km = wm.keyconfigs.addon.keymaps.new('Info',space_type='EMPTY', region_type='WINDOW', modal=False)
				# kmi = km.keymap_items.new('--  --', 'MINUS', 'PRESS')
				# kmi.active = False
				# etc_keymap.append((km, kmi))
		 ################################################################

				km = wm.keyconfigs.addon.keymaps.new(name = '3D View', space_type = 'VIEW_3D')
				kmi = km.keymap_items.new('object.modifier_add', 'FOUR', 'PRESS', ctrl=True, oskey=True)
				kmi_props_setattr(kmi.properties, 'type', 'MIRROR')
				kmi.active = True
				etc_keymap.append((km, kmi))




				# # # # # # # # #
				# ################################################################
				# km = wm.keyconfigs.addon.keymaps.new('Info',space_type='EMPTY', region_type='WINDOW', modal=False)
				# kmi = km.keymap_items.new('--  --', 'MINUS', 'PRESS')
				# kmi.active = False
				# etc_keymap.append((km, kmi))
				# ################################################################
				# ################################################################
				# km = wm.keyconfigs.addon.keymaps.new('Info',space_type='EMPTY', region_type='WINDOW', modal=False)
				# kmi = km.keymap_items.new('-- Mesh Tool --', 'MINUS', 'PRESS')
				# kmi.active = False
				# etc_keymap.append((km, kmi))
				# ################################################################
				# # # # # # # # #


				km = wm.keyconfigs.addon.keymaps.new('Mesh', space_type='EMPTY', region_type='WINDOW', modal=False)
				kmi = km.keymap_items.new('mesh.knife_tool', 'Z', 'PRESS', alt=True)
				kmi.active = True
				etc_keymap.append((km, kmi))



				# km = wm.keyconfigs.addon.keymaps.new('Mesh', space_type='EMPTY', region_type='WINDOW', modal=False)
				# kmi = km.keymap_items.new('mesh.inset', 'S', 'PRESS', shift=True,alt=True)
				# kmi.active = True
				# etc_keymap.append((km, kmi))



				km = wm.keyconfigs.addon.keymaps.new('Window', space_type='EMPTY', region_type='WINDOW', modal=False)
				kmi = km.keymap_items.new('wm.search_menu', 'SPACE', 'PRESS', shift=True,alt=True)
				kmi.active = True
				etc_keymap.append((km, kmi))

				km = wm.keyconfigs.addon.keymaps.new('Window', space_type='EMPTY', region_type='WINDOW', modal=False)
				kmi = km.keymap_items.new('screen.animation_play', 'SPACE', 'PRESS')
				kmi_props_setattr(kmi.properties, 'sync', True)
				kmi.active = True
				etc_keymap.append((km, kmi))


				km = wm.keyconfigs.addon.keymaps.new('Frames', space_type='EMPTY', region_type='WINDOW', modal=False)
				kmi = km.keymap_items.new('screen.frame_jump', 'RET', 'PRESS')
				kmi.active = True
				etc_keymap.append((km, kmi))


				km = wm.keyconfigs.addon.keymaps.new('Screen', space_type='EMPTY', region_type='WINDOW', modal=False)
				kmi = km.keymap_items.new('screen.userpref_show', 'COMMA', 'PRESS', ctrl=True)
				kmi.active = True
				etc_keymap.append((km, kmi))


				# # # # # # # # #
				# ################################################################
				# km = wm.keyconfigs.addon.keymaps.new('Info',space_type='EMPTY', region_type='WINDOW', modal=False)
				# kmi = km.keymap_items.new('-- release "C" key, the circle selection mode is canceled --', 'MINUS', 'PRESS')
				# kmi.active = False
				# etc_keymap.append((km, kmi))
				#  ################################################################
				#  # # # # # # # #
				#
				# km = wm.keyconfigs.addon.keymaps.new('View3D Gesture Circle', space_type='EMPTY', region_type='WINDOW', modal=True)
				# kmi = km.keymap_items.new_modal('CONFIRM', 'C', 'RELEASE')
				# kmi.active = True
				# etc_keymap.append((km, kmi))


				km = wm.keyconfigs.addon.keymaps.new('Mesh', space_type='EMPTY', region_type='WINDOW', modal=False)
				kmi = km.keymap_items.new('mesh.separate', 'J', 'PRESS', ctrl=True)
				kmi_props_setattr(kmi.properties, 'type', 'SELECTED')
				kmi.active = True
				etc_keymap.append((km, kmi))

				km = wm.keyconfigs.addon.keymaps.new('Mesh', space_type='EMPTY', region_type='WINDOW', modal=False)
				kmi = km.keymap_items.new('mesh.reveal_no_select', 'W', 'PRESS', alt=True)
				kmi_props_setattr(kmi.properties, 'type', 'SELECTED')
				kmi.active = True
				etc_keymap.append((km, kmi))


				km = wm.keyconfigs.addon.keymaps.new('Object Mode', space_type='EMPTY', region_type='WINDOW', modal=False)
				kmi = km.keymap_items.new('object.reveal_no_select_object', 'W', 'PRESS', alt=True)
				kmi.active = True
				etc_keymap.append((km, kmi))







################################################################
################################################################

################################################################
################################################################


		if addon_prefs.transform_keymap == True:



	# # # # # # # #
	################################################################

	#Translate >> A

	################################################################
	# # # # # # # #
			km = wm.keyconfigs.addon.keymaps.new('3D View Generic', space_type='VIEW_3D', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.translate', 'A', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Grease Pencil', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.translate', 'A', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Grease Pencil Stroke Edit Mode', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.translate', 'A', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Pose', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.translate', 'A', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Object Mode', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.translate', 'A', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Curve', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.translate', 'A', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Mesh', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.translate', 'A', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Armature', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.translate', 'A', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Metaball', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.translate', 'A', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Lattice', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.translate', 'A', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Object Non-modal', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.translate', 'A', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('3D View', space_type='VIEW_3D', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.translate', 'A', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('UV Editor', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.translate', 'A', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			# km = wm.keyconfigs.addon.keymaps.new('Transform Modal Map', space_type='EMPTY', region_type='WINDOW', modal=False)
			# kmi = km.keymap_items.new_modal('ROTATE', 'A', 'PRESS')
			# kmi.active = True
			# transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Graph Editor', space_type='GRAPH_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.translate', 'A', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Node Editor', space_type='NODE_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.translate', 'A', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Dopesheet', space_type='DOPESHEET_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.transform', 'A', 'PRESS')
			kmi_props_setattr(kmi.properties, 'mode', 'TIME_TRANSLATE')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('NLA Editor', space_type='NLA_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.translate', 'A', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Sequencer', space_type='SEQUENCE_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.translate', 'A', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Logic Editor', space_type='LOGIC_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.translate', 'A', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Clip Editor', space_type='CLIP_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.translate', 'A', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Clip Graph Editor', space_type='CLIP_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.translate', 'A', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Clip Dopesheet Editor', space_type='CLIP_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.translate', 'A', 'PRESS')
			kmi_props_setattr(kmi.properties, 'mode', 'TIME_TRANSLATE')
			kmi.active = True
			transform_keymap.append((km, kmi))






	# # # # # # # #
	################################################################

	#Rotate >> D

	################################################################
	# # # # # # # #
			km = wm.keyconfigs.addon.keymaps.new('3D View Generic', space_type='VIEW_3D', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Grease Pencil', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Grease Pencil Stroke Edit Mode', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			# km = wm.keyconfigs.addon.keymaps.new('Pose', space_type='EMPTY', region_type='WINDOW', modal=False)
			# kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			# kmi.active = True
			# transform_keymap.append((km, kmi))

			# km = wm.keyconfigs.addon.keymaps.new('Object Mode', space_type='EMPTY', region_type='WINDOW', modal=False)
			# kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			# kmi.active = True
			# transform_keymap.append((km, kmi))

			# km = wm.keyconfigs.addon.keymaps.new('Curve', space_type='EMPTY', region_type='WINDOW', modal=False)
			# kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			# kmi.active = True
			# transform_keymap.append((km, kmi))

			# km = wm.keyconfigs.addon.keymaps.new('Mesh', space_type='EMPTY', region_type='WINDOW', modal=False)
			# kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			# kmi.active = True
			# transform_keymap.append((km, kmi))
			#
			# km = wm.keyconfigs.addon.keymaps.new('Armature', space_type='EMPTY', region_type='WINDOW', modal=False)
			# kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			# kmi.active = True
			# transform_keymap.append((km, kmi))

			# km = wm.keyconfigs.addon.keymaps.new('Metaball', space_type='EMPTY', region_type='WINDOW', modal=False)
			# kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			# kmi.active = True
			# transform_keymap.append((km, kmi))

			# km = wm.keyconfigs.addon.keymaps.new('Lattice', space_type='EMPTY', region_type='WINDOW', modal=False)
			# kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			# kmi.active = True
			# transform_keymap.append((km, kmi))

			# km = wm.keyconfigs.addon.keymaps.new('Object Non-modal', space_type='EMPTY', region_type='WINDOW', modal=False)
			# kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			# kmi.active = True
			# transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('3D View', space_type='VIEW_3D', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('UV Editor', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			# km = wm.keyconfigs.addon.keymaps.new('Transform Modal Map', space_type='EMPTY', region_type='WINDOW', modal=True)
			# kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			# kmi.active = True
			# transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Graph Editor', space_type='GRAPH_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Node Editor', space_type='NODE_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			# km = wm.keyconfigs.addon.keymaps.new('Dopesheet', space_type='DOPESHEET_EDITOR', region_type='WINDOW', modal=False)
			# kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			# kmi.active = True
			# transform_keymap.append((km, kmi))

			# km = wm.keyconfigs.addon.keymaps.new('NLA Editor', space_type='NLA_EDITOR', region_type='WINDOW', modal=False)
			# kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			# kmi.active = True
			# transform_keymap.append((km, kmi))

			# km = wm.keyconfigs.addon.keymaps.new('Sequencer', space_type='SEQUENCE_EDITOR', region_type='WINDOW', modal=False)
			# kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			# kmi.active = True
			# transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Logic Editor', space_type='LOGIC_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			# km = wm.keyconfigs.addon.keymaps.new('Clip Editor', space_type='CLIP_EDITOR', region_type='WINDOW', modal=False)
			# kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			# kmi.active = True
			# transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Clip Graph Editor', space_type='CLIP_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			kmi.active = True
			transform_keymap.append((km, kmi))

			# km = wm.keyconfigs.addon.keymaps.new('Clip Dopesheet Editor', space_type='CLIP_EDITOR', region_type='WINDOW', modal=False)
			# kmi = km.keymap_items.new('transform.rotate', 'D', 'PRESS')
			# kmi.active = True
			# transform_keymap.append((km, kmi))



###################################

# select ndof_all

###################################


			km = wm.keyconfigs.addon.keymaps.new('Animation Channels', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('anim.channels_select_all_toggle', 'A', 'PRESS', oskey=True)
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Grease Pencil', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('object.select_all', 'A', 'PRESS', oskey=True)
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Grease Pencil Stroke Edit Mode', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('gpencil.select_all', 'A', 'PRESS', oskey=True)
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Pose', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('object.select_all', 'A', 'PRESS', oskey=True)
			kmi.active = True
			transform_keymap.append((km, kmi))
			km = wm.keyconfigs.addon.keymaps.new('Particle', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('particle.select_all', 'A', 'PRESS', oskey=True)
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Object Mode', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('object.select_all', 'A', 'PRESS', oskey=True)
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Curve', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('curve.select_all', 'A', 'PRESS', oskey=True)
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Mesh', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('mesh.select_all', 'A', 'PRESS', oskey=True)
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Armature', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('armature.select_all', 'A', 'PRESS', oskey=True)
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Metaball', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('mball.select_all', 'A', 'PRESS', oskey=True)
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Weight Paint Vertex Selection', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('paint.vert_select_all', 'A', 'PRESS', oskey=True)
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Lattice', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('lattice.select_all', 'A', 'PRESS', oskey=True)
			kmi.active = True
			transform_keymap.append((km, kmi))

			# km = wm.keyconfigs.addon.keymaps.new('Object Non-modal', space_type='EMPTY', region_type='WINDOW', modal=False)
			# kmi = km.keymap_items.new('object.select_all', 'A', 'PRESS', oskey=True)
			# kmi.active = True
			# transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('3D View', space_type='VIEW_3D', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('object.select_all', 'A', 'PRESS', oskey=True)
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('UV Editor', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('uv.select_all', 'A', 'PRESS', oskey=True)
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Font', space_type='EMPTY', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('font.select_all', 'A', 'PRESS', oskey=True)
			kmi.active = True
			transform_keymap.append((km, kmi))

			# km = wm.keyconfigs.addon.keymaps.new('Transform Modal Map', space_type='EMPTY', region_type='WINDOW', modal=True)
			# kmi = km.keymap_items.new('object.select_all', 'A', 'PRESS', oskey=True)
			# kmi.active = True
			# transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Graph Editor', space_type='GRAPH_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('graph.select_all_toggle', 'A', 'PRESS', oskey=True)
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Node Editor', space_type='NODE_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('node.select_all', 'A', 'PRESS', oskey=True)
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Dopesheet', space_type='DOPESHEET_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('action.select_all_toggle', 'A', 'PRESS', oskey=True)
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('NLA Editor', space_type='NLA_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('nla.select_all_toggle', 'A', 'PRESS', oskey=True)
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Sequencer', space_type='SEQUENCE_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('object.select_all', 'A', 'PRESS', oskey=True)
			kmi.active = True
			transform_keymap.append((km, kmi))

			# km = wm.keyconfigs.addon.keymaps.new('Logic Editor', space_type='LOGIC_EDITOR', region_type='WINDOW', modal=False)
			# kmi = km.keymap_items.new('object.select_all', 'A', 'PRESS', oskey=True)
			# kmi.active = True
			# transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Clip Editor', space_type='CLIP_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('clip.select_all', 'A', 'PRESS', oskey=True)
			kmi.active = True
			transform_keymap.append((km, kmi))

			km = wm.keyconfigs.addon.keymaps.new('Clip Graph Editor', space_type='CLIP_EDITOR', region_type='WINDOW', modal=False)
			kmi = km.keymap_items.new('clip.graph_select_all_markers', 'A', 'PRESS', oskey=True)
			kmi.active = True
			transform_keymap.append((km, kmi))





 # # # # # # # #
 ################################################################


 ################################################################
 # # # # # # # #

		bpy.app.translations.register(__name__, translation_dict_keymap_set)   # 辞書の登録




def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.app.translations.unregister(__name__)   # 辞書の削除


	# handle the keymap
	for km, kmi in select_border_keymap:
		km.keymap_items.remove(kmi)
	for km, kmi in select_linked_keymap:
		km.keymap_items.remove(kmi)
	for km, kmi in view_numpad_keymap:
		km.keymap_items.remove(kmi)
	for km, kmi in mode_set_keymap:
		km.keymap_items.remove(kmi)
	for km, kmi in etc_keymap:
		km.keymap_items.remove(kmi)
	for km, kmi in delete_keymap:
		km.keymap_items.remove(kmi)
	for km, kmi in mesh_tool_keymap:
		km.keymap_items.remove(kmi)
	for km, kmi in view_control_keymap:
		km.keymap_items.remove(kmi)
	for km, kmi in modifier_keymap:
		km.keymap_items.remove(kmi)
	for km, kmi in transform_keymap:
		km.keymap_items.remove(kmi)

	select_border_keymap.clear()
	select_linked_keymap.clear()
	view_numpad_keymap.clear()
	mode_set_keymap.clear()
	etc_keymap.clear()
	delete_keymap.clear()
	mesh_tool_keymap.clear()
	view_control_keymap.clear()
	modifier_keymap.clear()
	transform_keymap.clear()




	# clear the list
	del select_border_keymap[:]
	del select_linked_keymap[:]
	del view_numpad_keymap[:]
	del mode_set_keymap[:]
	del etc_keymap[:]
	del delete_keymap[:]
	del mesh_tool_keymap[:]
	del view_control_keymap[:]
	del modifier_keymap[:]
	del transform_keymap[:]

	if __name__ == "__main__":
		register()
