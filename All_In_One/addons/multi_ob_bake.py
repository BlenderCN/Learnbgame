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
	"name": "multi_ob_bake",
	"author": "bookyakuno",
	"version": (1,0),
	"blender": (2, 78, 0),
	'location': 'Properties > Render > Bake',
	"warning": "Required 2 add-ons",
	"description": "multi object bake Macro. Create target object & bake object , bake texture",
	"category": "Render",
}


import bpy
import bmesh
from bpy.types import Menu
from bpy.props import IntProperty, FloatProperty, BoolProperty


# AddonPreferences
class Wazou_fast_skin_x(bpy.types.AddonPreferences):
	bl_idname = __name__


	# bpy.types.Scene.Enable_Tab_FK_01 = bpy.props.BoolProperty(default=False)

	def draw(self, context):
		layout = self.layout


		# layout.prop(context.scene, "Enable_Tab_FK_01", text="URL's", icon="URL")
		# if context.scene.Enable_Tab_FK_01:
		layout.label(text="Required add-ons", icon="ERROR")
		row = layout.row()

		row.operator("wm.url_open", text="Scramble Addon Ghitub").url = "https://github.com/saidenka/Blender-Scramble-Addon"
		row.operator("wm.url_open", text="AddAsImageTexture  Ghitub").url = "https://github.com/chichige-bobo/BlenderPython/blob/master/AddAsImageTexture.py"
		# row.operator("wm.url_open", text="BlenderLounge Forum ").url = "http://blenderlounge.fr/forum/"








# operator
class multi_ob_bake(bpy.types.Operator):
	bl_idname = "object.multi_ob_bake"
	bl_label = "multi_ob_bake"
	bl_options = {'REGISTER', 'UNDO'}
	def execute(self, context):


		#ターゲット用オブジェクト複製
		bpy.ops.object.duplicate_move()
		#名前を取得
		active = bpy.context.active_object
		name = active.name

		#モディファイア適用・結合
		bpy.ops.object.convert(target='MESH')
		bpy.ops.object.join()
		bpy.context.object.name = name + "_target"

		#ベイク用オブジェクト作成
		bpy.ops.object.duplicate_move()
		bpy.context.object.name = name + "_bake"

		#ターゲットオブジェクト選択
		target = bpy.data.objects[name + "_target"]
		target.select = True

		#マテリアル全削除
		bpy.ops.material.remove_all_material_slot()

		#UV パッキング
		bpy.ops.object.view_menu(variable="VIEW_3D")
		bpy.ops.object.editmode_toggle()
		bpy.ops.mesh.select_all(action='SELECT')
		bpy.ops.object.view_menu(variable="IMAGE_EDITOR")
		bpy.ops.uv.select_all(action='SELECT')
		bpy.ops.uv.average_islands_scale()
		bpy.ops.uv.pack_islands(rotate=False, margin=0.0)
		bpy.ops.object.editmode_toggle()

		#Scramble Addon 新規画像作成
		bpy.ops.image.new_bake_image(name=name + "_iBake", alpha=False)

		#AddAsImageTexture 画像を元にマテリアル作成
		bpy.ops.object.add_as_image_texture()

		#ベイク設定c
		bpy.context.scene.cycles.bake_type = 'COMBINED'
		bpy.context.scene.use_selected_to_active = True
		bpy.context.scene.cage_extrusion = 0.01

		#ベイク
		#bpy.ops.object.bake(type='COMBINED')
		return {'FINISHED'}




# Menu
def multi_ob_bake_ui(self, context):

	layout = self.layout

	scene = context.scene
	cscene = scene.cycles
	rd = context.scene.render


	scene = context.scene
	cscene = scene.cycles
	device_type = context.user_preferences.system.compute_device_type


	col = layout.column(align=True)
	row = col.row(align=True)


	row.operator("object.multi_ob_bake", icon="RENDER_REGION")




def register():
	bpy.utils.register_module(__name__)

	# bpy.utils.register_class(multi_ob_bake)
	bpy.types.CyclesRender_PT_bake.append(multi_ob_bake_ui)


def unregister():
	bpy.utils.unregister_module(__name__)

	# bpy.utils.unregister_class(multi_ob_bake)
	bpy.types.CyclesRender_PT_bake.remove(multi_ob_bake_ui)


if __name__ == "__main__":
	register()
