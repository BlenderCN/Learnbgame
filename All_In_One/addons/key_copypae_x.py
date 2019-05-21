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
    "name": "key_copypae_x",
    "author": "bookyakuno",
    "version": (1,4),
    "location": "timeline shift + ctrl/cmd + X/C/V, key_del = BACK_SPACE(Other Anime Editor Window), , Property Shelf > Display > PLAY & HIDE",
    "description": "current key frame CUT, COPY, PASTE, DELETE in Timeline",
    "warning": "",
    "category": "Learnbgame"
}
# import the basic library
import bpy
class key_copypae_xPrefs(bpy.types.AddonPreferences):
    bl_idname = __name__
    bpy.types.Scene.Enable_Tab_01 = bpy.props.BoolProperty(default=False)
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "Enable_Tab_01", text="Info", icon="QUESTION")
        if context.scene.Enable_Tab_01:
            row = layout.row()
            layout.label(text="timeline")
            layout.label(text="Cut     > shift + ctrl/cmd + X")
            layout.label(text="Copy    > shift + ctrl/cmd + C")
            layout.label(text="Paste   > shift + ctrl/cmd + V")
            layout.label(text="key_del > BACK_SPACE")
            layout.label(text="")
            layout.label(text="PLAY & HIDE")
            layout.label(text="(Animation play & Rendering Only)")
            layout.label(text="3D View > ")
            layout.label(text="Property Shelf > ")
            layout.label(text="Display > ")
            layout.label(text="PLAY & HIDE")
###########################################
#
###########################################

class origin_set_cursor_x(bpy.types.Operator):
    bl_idname = "object.origin_set_cursor_x"
    bl_label = "origin_set_cursor_x"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):

        if context.mode == 'EDIT_MESH':
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            bpy.ops.object.editmode_toggle()

        else:
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        return {'FINISHED'}





###########################################
#
###########################################
class dope_frame_set_end(bpy.types.Operator):
    bl_idname = "object.dope_frame_set_end"
    bl_label = "dope_frame_set_end"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        bpy.ops.object.view_menu(variable="TIMELINE")
        bpy.ops.time.end_frame_set()
        bpy.ops.object.view_menu(variable="DOPESHEET_EDITOR")
        return {'FINISHED'}
class dope_frame_set_start(bpy.types.Operator):
    bl_idname = "object.dope_frame_set_start"
    bl_label = "dope_frame_set_start"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        bpy.ops.object.view_menu(variable="TIMELINE")
        bpy.ops.time.start_frame_set()
        bpy.ops.object.view_menu(variable="DOPESHEET_EDITOR")
        return {'FINISHED'}
class play_hide(bpy.types.Operator):
    bl_idname = "object.play_hide"
    bl_label = "PLAY & HIDE"
    def execute(self, context):
        if (bpy.context.screen.is_animation_playing == False):
            	bpy.context.space_data.show_only_render = True
            	bpy.ops.screen.animation_play(reverse=False, sync=False)
        else:
            	bpy.context.space_data.show_only_render = False
            	bpy.ops.screen.animation_play(reverse=False, sync=False)
        return {'FINISHED'}
# ヘッダーに項目追加
def play_hide_menu(self, context):
	layout = self.layout
	col = layout.column()
	if (bpy.context.screen.is_animation_playing == False):
            col.operator("object.play_hide", icon="PLAY")
	else:
            col.operator("object.play_hide", icon="PAUSE")
class key_constant_col(bpy.types.Operator):
    bl_idname = "object.key_constant_col"
    bl_label = "key_constant_col"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Message
        if (context.active_object):
            self.report(type={"INFO"}, message="CONSTANT")
        bpy.ops.action.interpolation_type(type='CONSTANT')
        bpy.ops.action.keyframe_type(type='EXTREME')
        return {'FINISHED'}
class key_linear_col(bpy.types.Operator):
    bl_idname = "object.key_linear_col"
    bl_label = "key_linear_col"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Message
        if (context.active_object):
            self.report(type={"INFO"}, message="LINEAR")
        bpy.ops.action.interpolation_type(type='LINEAR')
        bpy.ops.action.keyframe_type(type='BREAKDOWN')
        return {'FINISHED'}
class key_bezier_col(bpy.types.Operator):
    bl_idname = "object.key_bezier_col"
    bl_label = "key_bezier_col"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Message
        if (context.active_object):
            self.report(type={"INFO"}, message="BEZIER")
        bpy.ops.action.interpolation_type(type='BEZIER')
        bpy.ops.action.keyframe_type(type='KEYFRAME')
        return {'FINISHED'}
        # bpy.ops.action.keyframe_type(type='EXTREME')
        # bpy.ops.action.keyframe_type(type='JITTER')
        # bpy.ops.action.interpolation_type(type='LINEAR')
        # bpy.ops.action.interpolation_type(type='CONSTANT')
        # bpy.ops.action.interpolation_type(type='CONSTANT')
# 実際の内容
class DeleteUnmassage_xxx(bpy.types.Operator):
	bl_idname = "object.delete_xxx"
	bl_label = "Silent_Key_Del"
	bl_options = {'REGISTER', 'UNDO'}
	def execute(self, context):
		if (context.active_object):
		    self.report(type={"INFO"}, message="Silent_Key_Del")			# Message
		bpy.ops.anim.keyframe_delete_v3d()
		return {'FINISHED'}
class DeleteUnmassage_graph_silent_del(bpy.types.Operator):
	bl_idname = "graph.silent_del"
	bl_label = "silent_graph_Key_Del"
	bl_options = {'REGISTER', 'UNDO'}
	def execute(self, context):
		if (context.active_object):
		    self.report(type={"INFO"}, message="Silent_Key_Del")			# Message
		bpy.ops.graph.delete()
		return {'FINISHED'}
class bone_roll_0(bpy.types.Operator):
    bl_idname = "object.bone_roll_0"
    bl_label = "bone_roll_0"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        bpy.context.object.data.roll = 0
        return {'FINISHED'}
class curve_add_point(bpy.types.Operator):
    bl_idname = "object.curve_add_point"
    bl_label = "curve_add_point"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        bpy.ops.curve.select_next()
        bpy.ops.curve.subdivide()
        return {'FINISHED'}
class key_dope_cut_x(bpy.types.Operator):
    bl_idname = "object.key_dope_cut_x"
    bl_label = "key_dope_cut_x"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Message
        if (context.active_object):
            self.report(type={"INFO"}, message="key_dope_cut_x")
        bpy.ops.action.copy()
        bpy.ops.action.delete()
        return {'FINISHED'}
class key_cut_x(bpy.types.Operator):
    bl_idname = "object.key_cut_x"
    bl_label = "key_cut_x"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Message
        if (context.active_object):
            self.report(type={"INFO"}, message="key_cut_x")
        bpy.ops.object.view_menu(variable="DOPESHEET_EDITOR")	    # ドープシートへ移動
        # 選択を確実に解除
        bpy.ops.action.select_leftright(mode='RIGHT', extend=False)	 # 右側を選択
        bpy.ops.action.select_all_toggle(invert=False)				# 選択解除
        bpy.ops.action.select_column(mode='CFRA')				    # 現在のフレームのキーをすべて選択
        bpy.ops.action.copy()									    # キーフレームをコピー
        bpy.ops.action.delete()                                     # キーフレームをカット
        bpy.ops.object.view_menu(variable="TIMELINE")				# タイムラインへ戻る
        return {'FINISHED'}
class key_copy_x(bpy.types.Operator):
    bl_idname = "object.key_copy_x"
    bl_label = "key_copy_x"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Message
        if (context.active_object):
            self.report(type={"INFO"}, message="key_copy_x")
        bpy.ops.object.view_menu(variable="DOPESHEET_EDITOR")	#ドープシートへ移動
        # 選択を確実に解除
        bpy.ops.action.select_leftright(mode='RIGHT', extend=False)	 # 右側を選択
        bpy.ops.action.select_all_toggle(invert=False)				# 選択解除
        bpy.ops.action.select_column(mode='CFRA')				# 現在のフレームのキーをすべて選択
        bpy.ops.action.copy()									# キーフレームをコピー
        bpy.ops.object.view_menu(variable="TIMELINE")				# タイムラインへ戻る
        return {'FINISHED'}
class key_paste_x(bpy.types.Operator):
    bl_idname = "object.key_paste_x"
    bl_label = "key_paste_x"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        if (context.active_object):
            self.report(type={"INFO"}, message="key_paste_x")			# Message
        bpy.ops.object.view_menu(variable="DOPESHEET_EDITOR")
        bpy.ops.action.paste()
        bpy.ops.object.view_menu(variable="TIMELINE")
        return {'FINISHED'}
class key_move_current_x(bpy.types.Operator):
    bl_idname = "object.key_move_current_x"
    bl_label = "key_move_current_x"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # if (context.active_object):
        self.report(type={"INFO"}, message="key_move_current_x")			# Message
        bpy.ops.action.copy()
        bpy.ops.action.delete()
        bpy.ops.action.paste()
        return {'FINISHED'}
class key_del_x(bpy.types.Operator):
	bl_idname = "object.key_del_x"
	bl_label = "key_del_x"
	bl_options = {'REGISTER', 'UNDO'}
	def execute(self, context):
		if (context.active_object):
		    self.report(type={"INFO"}, message="key_del_x")			# Message
		bpy.ops.anim.keyframe_delete_v3d() #これが実際に削除するやつ。普通にAlt + Iから実行する方は、『警告 + この文』を実行しているので、この文だけを実行させる
		return {'FINISHED'}
class key_del_graph_x(bpy.types.Operator):
	bl_idname = "graph.key_del_graph_x"
	bl_label = "silent_graph_Key_Del"
	bl_options = {'REGISTER', 'UNDO'}
	def execute(self, context):
		if (context.active_object):
		    self.report(type={"INFO"}, message="key_del_graph_x")			# Message
		bpy.ops.graph.delete()
		 #これが実際に削除するやつ。普通にAlt + Iから実行する方は、『警告 + この文』を実行しているので、この文だけを実行させる
		return {'FINISHED'}
class only_select(bpy.types.Operator):
	bl_idname = "object.only_select"
	bl_label = "only_select"
	bl_options = {'REGISTER', 'UNDO'}
	def execute(self, context):
		bpy.ops.object.editmode_toggle()
		bpy.ops.view3d.local_view_ex()
		bpy.ops.object.editmode_toggle()
		bpy.ops.mesh.hide(unselected=True)
		return {'FINISHED'}
        # store keymaps here to access after registration
addon_keymaps = []
def register():
    bpy.utils.register_module(__name__)
    # ヘッダーメニューに項目追加
    bpy.types.VIEW3D_PT_view3d_display.prepend(play_hide_menu)
    # handle the keymap
#addon_keymaps = [] #put on out of register()
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name = 'Timeline', space_type = 'TIMELINE')
    # key_cut_x
    # kmi = km.keymap_items.new(key_dope_cut_x.bl_idname, 'X', 'PRESS', oskey=True)
    # addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(key_cut_x.bl_idname, 'X', 'PRESS', shift=True, ctrl=True)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(key_cut_x.bl_idname, 'X', 'PRESS', shift=True, oskey=True)
    addon_keymaps.append((km, kmi))
    # key_copy_x
    kmi = km.keymap_items.new(key_copy_x.bl_idname, 'C', 'PRESS', shift=True, ctrl=True)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(key_copy_x.bl_idname, 'C', 'PRESS', shift=True, oskey=True)
    addon_keymaps.append((km, kmi))
    # key_paste_x
    kmi = km.keymap_items.new(key_paste_x.bl_idname, 'V', 'PRESS', shift=True, ctrl=True)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(key_paste_x.bl_idname, 'V', 'PRESS', shift=True, oskey=True)
    addon_keymaps.append((km, kmi))
    # key_move_current_x
    kmi = km.keymap_items.new(key_move_current_x.bl_idname, 'X', 'PRESS',  oskey=True)
    addon_keymaps.append((km, kmi))
    # key_del_x
    kmi = km.keymap_items.new(key_del_x.bl_idname, 'BACK_SPACE', 'PRESS')
    addon_keymaps.append((km, kmi))
    km = wm.keyconfigs.addon.keymaps.new(name = 'Graph Editor Generic', space_type = 'GRAPH_EDITOR')
    kmi = km.keymap_items.new(key_del_graph_x.bl_idname, 'BACK_SPACE', 'PRESS')
    addon_keymaps.append((km, kmi))
    # km = wm.keyconfigs.addon.keymaps.new(name = 'Dopesheet', space_type = 'DOPESHEET_EDITOR')
    # kmi = km.keymap_items.new(key_del_x.bl_idname, 'BACK_SPACE', 'PRESS')
    # addon_keymaps.append((km, kmi))
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new(key_del_x.bl_idname, 'BACK_SPACE', 'PRESS',  alt=True)
    addon_keymaps.append((km, kmi))
    km = wm.keyconfigs.addon.keymaps.new(name='Pose Mode', space_type='EMPTY')
    kmi = km.keymap_items.new(key_del_x.bl_idname, 'BACK_SPACE', 'PRESS',  alt=True)
    addon_keymaps.append((km, kmi))
    km = wm.keyconfigs.addon.keymaps.new(name = 'Dopesheet', space_type = 'DOPESHEET_EDITOR')
    kmi = km.keymap_items.new(dope_frame_set_end.bl_idname, 'E', 'PRESS',  alt=True)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(dope_frame_set_start.bl_idname, 'S', 'PRESS',  alt=True)
    addon_keymaps.append((km, kmi))

def unregister():
    bpy.utils.unregister_module(__name__)
    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    # ヘッダーメニューの項目解除
    bpy.types.VIEW3D_PT_view3d_display.remove(play_hide_menu)
#
#
#
# # register the class
# def register():
#     bpy.utils.register_module(__name__)
#
#     pass
#
# def unregister():
#     bpy.utils.unregister_module(__name__)
#
#     pass
#
# if __name__ == "__main__":
#     register()
