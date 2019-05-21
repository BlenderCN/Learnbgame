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


import bpy, codecs, os.path

import bpy
import mathutils
import os.path
import os, sys
import subprocess
import fnmatch
from bpy.props import IntProperty, FloatProperty, EnumProperty
from bpy.props import FloatVectorProperty, StringProperty


# アドオン情報
bl_info = {
	"name" : "info_header_useful",
	"author" : "Bookyakuno",
	"version" : (0, 4),
	"blender" : (2, 79),
	"location" : "info > header > left, 3D view > header > left",
	"description" : "check the important stator with the header.",
	"warning" : "",
	"wiki_url" : "",
	"tracker_url" : "",
	"category" : "UI"
}


from bpy.types import Operator, AddonPreferences


###
import struct





# 翻訳辞書
translation_dict = {
	"en_US": {
	},
	"ja_JP": {
		("*", "check the important stator with the header."):
		"重要なステータスをヘッダーで確認できます",
		("*", "- current frame"):
		"・カレントフレーム",
		("*", "- Auto Keyframe mode"):
		"・自動キーフレームモード",
		("*", "- Recently opened file list, latest automatic backup"):
		"・最近開いたファイル一覧、最新の自動バックアップ",
		("*", "- Change object name"):
		"・オブジェクト名の変更",
		("*", "- Mirror in various modes"):
		"・各種モードでのミラー",
		("*", "- If global undo is turned off, a warning indication"):
		"・グローバルアンドゥがオフになっていると警告表示",
		("*", "- When Automatic keyframe insertion is ON, the header BG color becomes Red"):
		"・自動キーフレームモードがオンだとヘッダー背景色を「赤」に変更",
		("*", "- When Dyntopo is ON, the header BG color becomes Yellow"):
		"・Dyntopoがオンだとヘッダー背景色を「黄色」に変更",
		("*", "- Dyntopo"):
		"・Dyntopo",
	}
}



class info_header_useful_MenuPrefs(bpy.types.AddonPreferences):
	bl_idname = __name__

	# def_header_col = bpy.props.FloatVectorProperty(name="Default", default=(0.2, 0.2, 0.2, 1), size=4, subtype="COLOR", min=0, max=1)
	# header_color = bpy.props.BoolProperty(
    #         name="header_color",
    #         description="header_color",
    #         default=False)
	def draw(self, context):


		layout = self.layout
		split = layout.split()
		col = split.column()
		# col.prop(self, "def_header_col")
		# col.prop(self, "header_color")


		layout.label(
		text="- current frame")
		layout.label(
		text="- Auto Keyframe mode")
		layout.label(
		text="- Recently opened file list, latest automatic backup")
		layout.label(
		text="- Change object name")
		layout.label(
		text="- Mirror in various modes")
		layout.label(
		text="- When Automatic keyframe insertion is ON, the header BG color becomes Red")
		layout.label(
		text="- When Dyntopo is ON, the header BG color becomes Yellow")
		layout.label(
		text="- Dyntopo")

		# row.operator("wm.url_open", text="Download : github").url = "https://github.com/bookyakuno/-Blender-/blob/master/angle_select_click.py"
		# row.operator("wm.url_open", text="Donation $3 : gumroad").url = "https://gumroad.com/l/LXbX"





class RecoverLatestAutoSave_x(bpy.types.Operator):
	bl_idname = "wm.recover_latest_auto_save_x"
	bl_label = "最新の自動保存の読み込み"
	bl_description = "復元するために自動的に保存したファイルの最新ファイルを開きます"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		tempPath = context.user_preferences.filepaths.temporary_directory
		lastFile = None
		for fileName in fnmatch.filter(os.listdir(tempPath), "*.blend"):
			path = os.path.join(tempPath, fileName)
			if (lastFile):
				mtime = os.stat(path).st_mtime
				if (lastTime < mtime and fileName != "quit.blend"):
					lastFile = path
					lastTime = mtime
			else:
				lastFile = path
				lastTime = os.stat(path).st_mtime
		bpy.ops.wm.recover_auto_save(filepath=lastFile)
		self.report(type={"INFO"}, message="最新の自動保存ファイルを読み込みました")
		return {'FINISHED'}








class INFO_HT_header_recent_files_x(bpy.types.Menu):
	bl_idname = 'yyyt'
	bl_label = "Recent Files"

	def draw(self, context):

		recent_files = os.path.join(bpy.utils.user_resource('CONFIG'), "recent-files.txt")
		file = codecs.open(recent_files, 'r', 'utf-8-sig')

		for index, blend_path in enumerate(file.readlines()):
			if not blend_path: continue
			blend_path = blend_path.rstrip("\r\n")
			base_name = os.path.splitext( os.path.basename(blend_path) )[0]
			row = self.layout.row()
			row.operator_context = 'EXEC_DEFAULT'
			row.operator('wm.open_mainfile', icon='FILE_BLEND', text=base_name).filepath = blend_path

			if index == 0:
				self.layout.separator()
		self.layout.separator()
		row = self.layout.row()
		row.operator('wm.recover_latest_auto_save_x' , icon='PREVIEW_RANGE')

		file.close()



# ヘッダーに項目追加
def veiw3d_header_menu_x(self, context):
	layout = self.layout

	window = context.window
	scene = context.scene
	rd = scene.render

	userpref = context.user_preferences
	system = userpref.system
	edit = userpref.edit
	row = layout.row()
	col = row.column()

	# # # ヘッダーカラー



	current_theme = bpy.context.user_preferences.themes.items()[0][0]
	texed = bpy.context.user_preferences.themes[current_theme].view_3d

	def hex_to_rgb_dyn(rgb_str):
	    int_tuple = struct.unpack('BBB', bytes.fromhex(rgb_str))
	    return tuple([val/255 for val in int_tuple])
	if context.mode == 'SCULPT':
		if bpy.context.sculpt_object.use_dynamic_topology_sculpting == True:
			texed.space.header = hex_to_rgb_dyn('654600')
		else:
			texed.space.header = hex_to_rgb_dyn('333333')
	else:
		texed.space.header = hex_to_rgb_dyn('333333')
	# # # ヘッダーカラー


	# =====================================================
	# グローバルアンドゥを有功
	# =====================================================
	if bpy.context.user_preferences.edit.use_global_undo== False:
		col.prop(edit, "use_global_undo", icon="ERROR",text="")



	# =====================================================
	# テクスチャペイント
	# =====================================================
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



	# =====================================================
	# ウェイトペイント
	# =====================================================
	mode_string = context.mode

	if mode_string in {'PAINT_WEIGHT'}:
		obj = context.weight_paint_object
		mesh = obj.data
		self.layout.prop(mesh, "use_mirror_x",text="",icon="MOD_MIRROR")



	# =====================================================
	# アーマチュアミラー
	# =====================================================
	obj = context.active_object
	mode_string = context.mode
	edit_object = context.edit_object
	gp_edit = context.gpencil_data and context.gpencil_data.use_stroke_edit_mode
	mode = obj.mode
	if (mode == 'EDIT' and obj.type == 'MESH' or mode == 'EDIT' and 'ARMATURE'):

		arm = context.active_object.data
		self.layout.prop(arm, "use_mirror_x",text="",icon="MOD_MIRROR")



	# =====================================================
	# スカルプト
	# =====================================================
	if context.sculpt_object:

		col = layout.column(align=True)
		row = col.row(align=True)
		# =====================================================
		# シンメトリー
		# =====================================================
		sculpt = context.tool_settings.sculpt
		row.scale_x = 0.5
		row.prop(sculpt, "use_symmetry_x", text="X", toggle=True)
		row.prop(sculpt, "use_symmetry_y", text="Y", toggle=True)
		row.prop(sculpt, "use_symmetry_z", text="Z", toggle=True)

		# =====================================================
		# ダイナトポ
		# =====================================================
		WM = context.window_manager
		toolsettings = context.tool_settings
		sculpt = toolsettings.sculpt

		if len(context.selected_objects) >= 1 :





			# if bpy.context.scene.tool_settings.use_keyframe_insert_auto == True:
			#     texed.space.header = hex_to_rgb('670000')

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




		if (sculpt.detail_type_method == 'CONSTANT'):
			layout.prop(sculpt, "constant_detail_resolution", text="")
			# layout.operator("sculpt.sample_detail_size", text="", icon='EYEDROPPER')
		elif (sculpt.detail_type_method == 'BRUSH'):
			layout.prop(sculpt, "detail_percent", text="")
		else:
			layout.prop(sculpt, "detail_size", text="")



		userpref = context.user_preferences
		view = userpref.view
		layout.prop(view, "use_auto_perspective", text="", icon="CAMERA_DATA")








# ヘッダーに項目追加
def info_header_menu_x(self, context):

	layout = self.layout

	window = context.window
	scene = context.scene
	rd = scene.render


	layout.prop(scene, "frame_current", text="")










	toolsettings = context.tool_settings
	screen = context.screen
	userprefs = context.user_preferences

	row = layout.row(align=True)
	row.prop(toolsettings, "use_keyframe_insert_auto", text="", toggle=True)
	if toolsettings.use_keyframe_insert_auto:

		current_theme = bpy.context.user_preferences.themes.items()[0][0]
		texed = bpy.context.user_preferences.themes[current_theme].view_3d

		def hex_to_rgb_auto_key(rgb_str):
		    int_tuple = struct.unpack('BBB', bytes.fromhex(rgb_str))
		    return tuple([val/255 for val in int_tuple])

		if bpy.context.scene.tool_settings.use_keyframe_insert_auto == True:
			texed.space.header = hex_to_rgb_auto_key('670000')
		else:
			texed.space.header = hex_to_rgb_auto_key('333333')

		# if bpy.context.sculpt_object.use_dynamic_topology_sculpting == True:
		#     texed.space.header = hex_to_rgb('654600')


		row.prop(toolsettings, "use_keyframe_insert_keyingset", text="", toggle=True)

	if screen.is_animation_playing and not userprefs.edit.use_keyframe_insert_available:

		subsub = row.row(align=True)
		subsub.prop(toolsettings, "use_record_with_nla", toggle=True)





	# 最近使ったファイル
#    self.layout.menu('INFO_MT_file_open_recent', icon='OPEN_RECENT', text="")
#                 layout.menu("INFO_MT_file_open_recent", icon='OPEN_RECENT', text="")


	self.layout.menu('yyyt', icon='OPEN_RECENT', text="")

	### アイテム








	layout = self.layout
	col = layout.column(align=True)
	view = context.space_data
	scene = context.scene
	obj = context.object
	#                obj_type = obj.type

	ob = context.active_object

	row = layout.row()
	row.template_ID(context.scene.objects, "active")
#     row.label(text="", icon='OBJECT_DATA')
#     row.prop(ob, "name", text="")

	if ob.type == 'ARMATURE' and ob.mode in {'EDIT', 'POSE'}:
		bone = context.active_bone
		row = layout.row()
		row.label(text="", icon='BONE_DATA')
		row.prop(bone, "name", text="")


#    cam = bpy.context.scene.camera

#    col = split.column()
#    row = col.row()
#    row.prop(cam, "lens")

#    camx = bpy.context.scene.camera
#    xxz = bpy.data.cameras["camx"]

	layout.prop(context.object.data, "lens", text="lens")




	# 連番リネーム
	#                row.prop(context.scene,"rno_str_new_name",text="")
	#                layout.operator("object.rno_setname",text="",icon='GREASEPENCIL')


	st = context.space_data
	toolsettings = context.tool_settings

	row = layout.row(align=True)
	row.template_header()

	DOPESHEET_MT_editor_menus.draw_collapsible(context, layout)

	layout.prop(st, "mode", text="")

	if st.mode in {'ACTION', 'SHAPEKEY'}:
		row = layout.row(align=True)
		row.operator("action.layer_prev", text="", icon='TRIA_DOWN')
		row.operator("action.layer_next", text="", icon='TRIA_UP')

		layout.template_ID(st, "action", new="action.new", unlink="action.unlink")

		row = layout.row(align=True)
		row.operator("action.push_down", text="Push Down", icon='NLA_PUSHDOWN')
		row.operator("action.stash", text="Stash", icon='FREEZE')

	layout.prop(st.dopesheet, "show_summary", text="Summary")

	if st.mode == 'DOPESHEET':
		dopesheet_filter(layout, context)
	elif st.mode == 'ACTION':
		# 'genericFiltersOnly' limits the options to only the relevant 'generic' subset of
		# filters which will work here and are useful (especially for character animation)
		dopesheet_filter(layout, context, genericFiltersOnly=True)
	elif st.mode == 'GPENCIL':
		row = layout.row(align=True)
		row.prop(st.dopesheet, "show_gpencil_3d_only", text="Active Only")

		if st.dopesheet.show_gpencil_3d_only:
			row = layout.row(align=True)
			row.prop(st.dopesheet, "show_only_selected", text="")
			row.prop(st.dopesheet, "show_hidden", text="")

		row = layout.row(align=True)
		row.prop(st.dopesheet, "use_filter_text", text="")
		if st.dopesheet.use_filter_text:
			row.prop(st.dopesheet, "filter_text", text="")
			row.prop(st.dopesheet, "use_multi_word_filter", text="")

	row = layout.row(align=True)
	row.prop(toolsettings, "use_proportional_action",
			 text="", icon_only=True)
	if toolsettings.use_proportional_action:
		row.prop(toolsettings, "proportional_edit_falloff",
				 text="", icon_only=True)

	# Grease Pencil mode doesn't need snapping, as it's frame-aligned only
	if st.mode != 'GPENCIL':
		layout.prop(st, "auto_snap", text="")

	row = layout.row(align=True)
	row.operator("action.copy", text="", icon='COPYDOWN')
	row.operator("action.paste", text="", icon='PASTEDOWN')
	if st.mode not in ('GPENCIL', 'MASK'):
		row.operator("action.paste", text="", icon='PASTEFLIPDOWN').flipped = True




	obj = context.object

	obj_name = obj.name
	for group in bpy.data.groups:
			group_objects = group.objects
			if obj_name in group.objects and obj in group_objects[:]:
					col = layout.column(align=True)

					col.context_pointer_set("group", group)


					row.menu("GROUP_MT_specials_x", icon='META_CUBE', text="")
#                    row.prop(group, "name", text="")

#                    row.operator("object.group_remove", text="", icon='X', emboss=False)



class GROUP_MT_specials_x(bpy.types.Menu):
	bl_label = "Group Specials"

	def draw(self, context):
		layout = self.layout

#        row.prop(group, "name", text="")


		obj = context.object

		obj_name = obj.name
		for group in bpy.data.groups:
				group_objects = group.objects
				if obj_name in group.objects and obj in group_objects[:]:
						col = layout.column(align=True)

						layout.prop(group, "name", text="")
#                        layout.operator("object.group_remove", icon='X', emboss=False)


#        layout.operator("object.group_unlink", icon='X')
#        layout.operator("object.grouped_select")
#        layout.operator("object.dupli_offset_from_cursor")
#        layout.operator("object.group_remove", icon='X', emboss=False)






def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_HT_header.prepend(info_header_menu_x)
	bpy.types.VIEW3D_MT_editor_menus.prepend(veiw3d_header_menu_x)
	# bpy.types.VIEW3D_MT_editor_menus.prepend(header_color_change)
	bpy.types.VIEW3D_HT_header.prepend(veiw3d_header_menu_x)
	bpy.app.translations.register(__name__, translation_dict)   # 辞書の登録

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_HT_header.remove(info_header_menu_x)
	# bpy.types.INFO_HT_header.remove(header_color_change)
	bpy.types.VIEW3D_MT_editor_menus.remove(veiw3d_header_menu_x)
	bpy.types.VIEW3D_HT_header.remove(veiw3d_header_menu_x)
	bpy.app.translations.unregister(__name__)   # 辞書の削除


if __name__ == '__main__':
	register()
