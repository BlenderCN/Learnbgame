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
    "name": "Angle select click",
    "author": "bookyakuno",
    "version": (1,3),
    "location": "Property panel > Mesh Display",
    "description": "Select face by angle.",
    "warning": "",
    "category": "Learnbgame"
}

import bpy
import bmesh

from bpy.types import Operator, AddonPreferences



# 翻訳辞書
translation_dict = {
    "en_US": {
        ("*", "Delete Face By Right Click"):
            "Delete Face By Right Click",
    },
    "ja_JP": {
		("*", "Select face by angle."):
		"面を角度によって選択します",
    }
}





class KeymapSetMenuPrefsz(bpy.types.AddonPreferences):

    bl_idname = __name__

    bpy.types.Scene.angle_select_click_threshold = bpy.props.FloatProperty(default= 30, min= 0.01, max= 180, description="Angle")

    def draw(self, context):
        layout = self.layout

        layout.label(
        text="- Keymap -")
        layout.label(
        text="( if LEFT select mouse, ACTIONMOUSE = RIGHTMOUSE)")
        layout.label(
        text="Ctrl + ACTIONMOUSE >> Angle select")
        layout.label(
        text="Ctrl + Shift + ACTIONMOUSE >> Angle select multiple")
        layout.label(
        text="alt + Y >> Angle select")
        layout.label(
        text="alt + shift + Y >> Angle select multiple")

        layout.label(
        text="")
        layout.label(
        text="- Link -")
        row = layout.row()

        row.operator("wm.url_open", text="Download : github").url = "https://github.com/bookyakuno/-Blender-/blob/master/angle_select_click.py"
        row.operator("wm.url_open", text="Donation $3 : gumroad").url = "https://gumroad.com/l/LXbX"






class angle_select_click(bpy.types.Operator):
    bl_idname = "object.angle_select_click"
    bl_label = "angle_select_click"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        bm = bmesh.from_edit_mesh(obj.data)


        angle_select_click_angle = bpy.context.scene.angle_select_click_threshold/180



        # 非表示を頂点グループにバックアップ
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.reveal()
        bpy.ops.object.vertex_group_assign_new()
        bpy.context.object.vertex_groups.active.name = "hide_vgroups"

        # 角度選択
        bpy.ops.view3d.select('INVOKE_DEFAULT')
        bpy.ops.mesh.select_similar(type='NORMAL', compare='EQUAL', threshold=angle_select_click_angle)

        # リンクするもののみ選択
        bpy.ops.mesh.hide(unselected=True) #選択以外非表示
        bpy.ops.mesh.select_all(action='DESELECT') #選択解除
        bpy.ops.view3d.select('INVOKE_DEFAULT') #マウス下選択
        bpy.ops.mesh.select_linked(delimit={'NORMAL'}) #リンク選択
        bpy.ops.object.vertex_group_assign_new()
        bpy.context.object.vertex_groups.active.name = "angle_vgroups"

        # bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT') #選択解除
        # bpy.ops.mesh.select_all(action='INVERT')

        bpy.ops.object.vertex_group_set_active(group='hide_vgroups')
        bpy.ops.object.vertex_group_select()


        bpy.ops.object.vertex_group_remove()
        bpy.ops.mesh.hide() #選択非表示

        bpy.ops.object.vertex_group_set_active(group='angle_vgroups')
        bpy.ops.object.vertex_group_select()
        bpy.ops.object.vertex_group_remove()
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')



        return {'FINISHED'}



class angle_select_click_extend(bpy.types.Operator):
    bl_idname = "object.angle_select_click_extend"
    bl_label = "angle_select_click_extend"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        obj = context.object
        bm = bmesh.from_edit_mesh(obj.data)


        angle_select_click_angle = bpy.context.scene.angle_select_click_threshold/180



        # 表示状態を保存
        bpy.ops.object.vertex_group_assign_new()
        bpy.context.object.vertex_groups.active.name = "old_select_vgroups"

        # 非表示を頂点グループにバックアップ
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.reveal()
        bpy.ops.object.vertex_group_assign_new()
        bpy.context.object.vertex_groups.active.name = "hide_vgroups"

        # 角度選択
        bpy.ops.view3d.select('INVOKE_DEFAULT')
        bpy.ops.mesh.select_similar(type='NORMAL', compare='EQUAL', threshold=angle_select_click_angle)

        # リンクするもののみ選択
        bpy.ops.mesh.hide(unselected=True) #選択以外非表示
        bpy.ops.mesh.select_all(action='DESELECT') #選択解除
        bpy.ops.view3d.select('INVOKE_DEFAULT') #マウス下選択
        bpy.ops.mesh.select_linked(delimit={'NORMAL'}) #リンク選択
        bpy.ops.object.vertex_group_assign_new()
        bpy.context.object.vertex_groups.active.name = "angle_vgroups"

        # bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT') #選択解除
        # bpy.ops.mesh.select_all(action='INVERT')

        bpy.ops.object.vertex_group_set_active(group='hide_vgroups')
        bpy.ops.object.vertex_group_select()
        bpy.ops.object.vertex_group_remove()
        # bpy.ops.object.vertex_group_remove()
        bpy.ops.mesh.hide() #選択非表示

        bpy.ops.object.vertex_group_set_active(group='angle_vgroups')
        bpy.ops.object.vertex_group_select()
        bpy.ops.object.vertex_group_remove()

        bpy.ops.object.vertex_group_set_active(group='old_select_vgroups')
        bpy.ops.object.vertex_group_select()
        bpy.ops.object.vertex_group_remove()
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')




        return {'FINISHED'}








#
# class angle_select_click_extend(bpy.types.Operator):
# 	bl_idname = "object.angle_select_click_extend"
# 	bl_label = "angle_select_click_extend"
# 	bl_options = {'REGISTER', 'UNDO'}
#
# 	def execute(self, context):
# 		obj = context.object
# 		bm = bmesh.from_edit_mesh(obj.data)
#
#
# 		angle_select_click_angle = bpy.context.scene.angle_select_click_threshold/180
# 		# print(angle_select_click_angle)
#
# 		bpy.ops.object.vertex_group_assign_new()
# 		bpy.ops.mesh.hide() #選択非表示
# 		bpy.ops.view3d.select('INVOKE_DEFAULT',extend=True)
# 		bpy.ops.mesh.select_similar(type='NORMAL', compare='EQUAL', threshold=angle_select_click_angle)
#
# 		bpy.ops.mesh.hide(unselected=True) #選択以外非表示
# 		bpy.ops.mesh.select_all(action='DESELECT') #選択解除
# 		bpy.ops.view3d.select('INVOKE_DEFAULT',extend=True) #マウス下選択
# 		bpy.ops.mesh.select_linked(delimit={'NORMAL'}) #リンク選択
# 		bpy.ops.mesh.select_all(action='INVERT')
# 		bpy.ops.mesh.reveal()
# 		bpy.ops.mesh.select_all(action='INVERT')
#
#
# 		selected_faces = [f for f in bm.faces if f.select]
#
# 		for f in selected_faces :
# 				if selected_faces:
# 					f.select=True
#
# 		del(selected_faces[:])
#
# 		# bpy.ops.object.vertex_group_deselect()
# 		bpy.ops.object.vertex_group_select()
# 		bpy.ops.object.vertex_group_remove()
#
# 		return {'FINISHED'}


# ヘッダーに項目追加
def angle_select_click_threshold_menu(self, context):

    layout = self.layout
    scene = context.scene

    # row = layout.row(align=True)
    layout.label(text="angle select click:", icon='LAMP_HEMI')
    layout.prop(context.scene, "angle_select_click_threshold", text="Angle")



addon_keymaps = []
def register():
    bpy.utils.register_module(__name__)
    wm = bpy.context.window_manager

    km = wm.keyconfigs.addon.keymaps.new(name = 'Mesh')
    kmi = km.keymap_items.new(angle_select_click.bl_idname, 'Y', 'PRESS', alt=True)
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new(angle_select_click_extend.bl_idname, 'Y', 'PRESS', alt=True,shift=True)
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new(angle_select_click.bl_idname, 'ACTIONMOUSE', 'PRESS', ctrl=True)
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new(angle_select_click_extend.bl_idname, 'ACTIONMOUSE', 'PRESS', ctrl=True,shift=True)
    addon_keymaps.append((km, kmi))



    # メニューに項目追加
    bpy.types.VIEW3D_PT_view3d_meshdisplay.append(angle_select_click_threshold_menu)
    bpy.app.translations.register(__name__, translation_dict)   # 辞書の登録


def unregister():
    bpy.utils.unregister_module(__name__)
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.app.translations.unregister(__name__)   # 辞書の削除

    bpy.types.VIEW3D_PT_view3d_meshdisplay.remove(angle_select_click_threshold_menu)


if __name__ == '__main__':
    register()
