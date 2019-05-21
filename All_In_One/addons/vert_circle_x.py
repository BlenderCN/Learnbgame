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
	"name": "vert_circle_x",
	"author": "bookyakuno",
	"version": (1,2),
	"location": "alt + Y or object.vert_circle_x",
	"description": "need loop tool addon circle",
	"warning": "",
	"category": "Learnbgame"
}

import bpy


class vert_circle_x(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "object.vert_circle_x"
	bl_label = "vert_circle_x"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):

#		before_Apivot = bpy.context.space_data.pivot_point
		automerge_setting = bpy.context.scene.tool_settings.use_mesh_automerge
		bpy.context.scene.tool_settings.use_mesh_automerge = False
		# bpy.data.scenes['Scene'].tool_settings.use_mesh_automerge = False

		bpy.ops.mesh.select_more()
		bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, 0)})
		bpy.ops.mesh.looptools_circle(custom_radius=False, fit='best', flatten=True, influence=100, lock_x=False, lock_y=False, lock_z=False, radius=1, regular=True)

		bpy.context.space_data.pivot_point = 'INDIVIDUAL_ORIGINS' # あとで複数の作った円を一括してスケール調整できるよう、ピボットを「それぞれの原点」に変更

		bpy.ops.transform.resize(value=(0.5, 0.5, 0.5),release_confirm=False)

		# bpy.ops.transform.resize("INVOKE_DEFAULT") # 実行したあとすぐにスケール調整ジェスチャーが始まる。自分としては使わないのでオフ。使いたい場合は「行頭の「# 」を取る

		bpy.context.user_preferences.edit.use_global_undo = True # 使っているLoop Toolsアドオンのcircleが、グローバルアンドゥをオフにするようになっているので、最後にグローバルアンドゥがオンになるように修正

#		bpy.context.space_data.pivot_point = before_pivot
		bpy.context.scene.tool_settings.use_mesh_automerge = automerge_setting


		return {'FINISHED'}



addon_keymaps = []
def register():
	bpy.utils.register_module(__name__)
	wm = bpy.context.window_manager

	km = wm.keyconfigs.addon.keymaps.new(name = 'Mesh')
	kmi = km.keymap_items.new(vert_circle_x.bl_idname, 'Y', 'PRESS', alt=True)
	addon_keymaps.append((km, kmi))

def unregister():
	bpy.utils.unregister_module(__name__)
	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()
