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

bl_info = {
	"name": "Isolate Select",
	"author": "bookyakuno",
	"version": (1, 1, 0),
	"blender": (2, 79),
	"location": "3D View Q key",
	"description": "Repeat local view as long as there are selected objects & Non zoom",
	"category": "3D View",
}


import bpy, mathutils
import os, csv
import collections




class isolate_select(bpy.types.Operator):
	bl_idname = "view3d.isolate_select"
	bl_label = "Isolate Select"
	bl_description = "Repeat local view as long as there are selected objects & Non zoom"
	bl_options = {'REGISTER'}

	def execute(self, context):



		if (context.space_data.local_view):
			# ローカルビューの場合

			# ======  ====== Srt オブジェクト数を見る Srt ======  ======
			# ======  ====== Srt オブジェクト数を見る Srt ======  ======
			# ======  ====== Srt オブジェクト数を見る Srt ======  ======
			# 一度オブジェクトモードに戻って、
			# 選択状態の保存、
			# 全選択、
			# オブジェクト数の情報を得る
			# 元の選択状態に戻す
			#
			#
			#


			if context.mode =='OBJECT': # オブジェクトモードモードの場合
				# self.report(type={'INFO'}, message="OB")


				ff = bpy.context.selected_objects
				bpy.ops.object.select_all(action='SELECT')
				ww = len (context.selected_objects )
				bpy.ops.object.select_all(action='DESELECT')
				for obj in ff:
					obj.select = True

			elif context.mode =='SCULPT': # スカルプトモードの場合

				bpy.ops.sculpt.sculptmode_toggle()

				ff = bpy.context.selected_objects
				bpy.ops.object.select_all(action='SELECT')
				ww = len (context.selected_objects )

				bpy.ops.object.select_all(action='DESELECT')
				for obj in ff:
					obj.select = True

				# スカルプトモードに戻る
				bpy.ops.sculpt.sculptmode_toggle()

			elif context.mode =='PAINT_WEIGHT': # ウェイトペイントモードの場合

				bpy.ops.paint.weight_paint_toggle()

				ff = bpy.context.selected_objects
				bpy.ops.object.select_all(action='SELECT')
				ww = len (context.selected_objects )

				bpy.ops.object.select_all(action='DESELECT')
				for obj in ff:
					obj.select = True

				# ウェイトペイントモードに戻る
				bpy.ops.paint.weight_paint_toggle()

			elif context.mode =='POSE': # ポーズモードの場合

				bpy.ops.object.posemode_toggle()

				ff = bpy.context.selected_objects
				bpy.ops.object.select_all(action='SELECT')
				ww = len (context.selected_objects )

				bpy.ops.object.select_all(action='DESELECT')
				for obj in ff:
					obj.select = True

				# ポーズモードに戻る
				bpy.ops.object.posemode_toggle()

			elif context.mode =='PAINT_TEXTURE': # テクスチャペイントモードの場合

				bpy.ops.paint.texture_paint_toggle()

				ff = bpy.context.selected_objects
				bpy.ops.object.select_all(action='SELECT')
				ww = len (context.selected_objects )

				bpy.ops.object.select_all(action='DESELECT')
				for obj in ff:
					obj.select = True

				# テクスチャペイントモードに戻る
				bpy.ops.paint.texture_paint_toggle()

			elif context.mode =='PAINT_VERTEX': # 頂点ペイントモードの場合

				bpy.ops.paint.vertex_paint_toggle()

				ff = bpy.context.selected_objects
				bpy.ops.object.select_all(action='SELECT')
				ww = len (context.selected_objects )

				bpy.ops.object.select_all(action='DESELECT')
				for obj in ff:
					obj.select = True

				# 頂点ペイントモードに戻る
				bpy.ops.paint.vertex_paint_toggle()


			elif context.mode == 'EDIT_MESH' or 'EDIT_CURVE' or 'EDIT_SURFACE' or 'EDIT_METABALL' or 'EDIT_ARMATURE':
				# 各種編集モードの場合
				# self.report(type={'INFO'}, message="misc_Edit")

				# 編集モードを抜ける
				bpy.ops.object.editmode_toggle()

				ff = bpy.context.selected_objects
				bpy.ops.object.select_all(action='SELECT')

				ww = len (context.selected_objects )
				bpy.ops.object.select_all(action='DESELECT')

				for obj in ff:
					obj.select = True

				# 編集モードに戻す
				bpy.ops.object.editmode_toggle()



			else:				# それ以外の場合

				ff = bpy.context.selected_objects
				bpy.ops.object.select_all(action='SELECT')
				ww = len (context.selected_objects )

				bpy.ops.object.select_all(action='DESELECT')
				for obj in ff:
					obj.select = True


				aax = len (context.selected_objects )


			# ======  ====== End オブジェクト数を見る End ======  ======
			# ======  ====== End オブジェクト数を見る End ======  ======
			# ======  ====== End オブジェクト数を見る End ======  ======




			# ======  ====== Srt オブジェクト数を測る Srt ======  ======
			# ======  ====== Srt オブジェクト数を測る Srt ======  ======
			# ======  ====== Srt オブジェクト数を測る Srt ======  ======



			if  len (context.selected_objects ) == 0:
				# 選択物が  なにもない場合、ローカルビューを終了する
				bpy.ops.view3d.local_view_ex_ops()
				# self.report(type={'INFO'}, message="0")

			elif  ww == 1:
				# 選択物が  1つしかない場合、ローカルビューを終了する

				# self.report(type={'INFO'}, message="1")
				bpy.ops.view3d.local_view_ex_ops()

			elif  len (context.selected_objects ) == ww:
				# 選択物が  同じ  の場合、ローカルビューを終了する

				# self.report(type={'INFO'}, message="1")
				bpy.ops.view3d.local_view_ex_ops()




			# else:
			elif  len (context.selected_objects ) < ww:
				# 選択物が  少ない  場合、ローカルビューを実行する


				if context.mode =='EDIT_MESH':
					# self.report(type={'INFO'}, message="EDIT")

					bpy.ops.object.editmode_toggle()
					bpy.ops.view3d.local_view_ex_ops()
					bpy.ops.object.editmode_toggle()

				else:
					# self.report(type={'INFO'}, message="Repeat")

					aa = bpy.context.selected_objects

					bpy.ops.view3d.local_view_ex_ops()
					bpy.ops.object.select_all(action='DESELECT')
					for obj in aa:
						obj.select = True
					bpy.ops.view3d.local_view_ex_ops()

		else:

			# if context.mode =='EDIT_MESH':

			if context.mode =='OBJECT': # オブジェクトモードモードの場合
				# self.report(type={'INFO'}, message="OB")
				bpy.ops.view3d.local_view_ex_ops()

			elif context.mode == 'EDIT_MESH' or 'EDIT_CURVE' or 'EDIT_SURFACE' or 'EDIT_METABALL' or 'EDIT_ARMATURE':
				# self.report(type={'INFO'}, message="elsezzz")
				bpy.ops.object.editmode_toggle()

				bpy.ops.view3d.local_view_ex_ops()
				bpy.ops.object.editmode_toggle()

			else:
				bpy.ops.view3d.local_view_ex_ops()


		return {'FINISHED'}


	# =====================================================

	# =====================================================




class LocalViewEx_ops(bpy.types.Operator): #ローカルビューを非ズームで実行する
	bl_idname = "view3d.local_view_ex_ops"
	bl_label = "Global / local view (non-zoom)"
	bl_description = "Displays only selected objects and centered point of view doesn\'t (zoom)"
	# bl_options = {'REGISTER'}

	def execute(self, context):


		pre_smooth_view = context.user_preferences.view.smooth_view
		context.user_preferences.view.smooth_view = 0
		pre_view_distance = context.region_data.view_distance
		pre_view_location = context.region_data.view_location.copy()
		pre_view_rotation = context.region_data.view_rotation.copy()
		pre_cursor_location = context.space_data.cursor_location.copy()
		bpy.ops.view3d.localview()
		# if (context.space_data.local_view):
		# 	# self.report(type={'INFO'}, message="Local")
		# else:
			# self.report(type={'INFO'}, message="Global")
		context.space_data.cursor_location = pre_cursor_location
		context.region_data.view_distance = pre_view_distance
		context.region_data.view_location = pre_view_location
		context.region_data.view_rotation = pre_view_rotation
		context.user_preferences.view.smooth_view = pre_smooth_view
		return {'FINISHED'}

	# =====================================================

	# =====================================================




addon_keymaps = []
def register():
	bpy.utils.register_module(__name__)
	wm = bpy.context.window_manager

	km = wm.keyconfigs.addon.keymaps.new(name = '3D View Generic', space_type = 'VIEW_3D')
	kmi = km.keymap_items.new(isolate_select.bl_idname, 'Q', 'PRESS')
	addon_keymaps.append((km, kmi))


def unregister():
	bpy.utils.unregister_module(__name__)
	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()
