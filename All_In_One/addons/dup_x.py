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
	"name": "dup_x",
	"author": "bookyakuno",
	"version": (1,1),
	"location": "like a zbrush add parts",
	"description": "Shift + cmd + T",
	"warning": "",
	"category": "Learnbgame"
}

import bpy
from bpy.props import IntProperty, FloatProperty


class dup_x_modal(bpy.types.Operator):
    bl_idname = "object.dup_x_modal"
    bl_label = "dup_x_modal"

    first_mouse_y = IntProperty()
    first_value = FloatProperty()

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            delta = self.first_mouse_y - event.mouse_y
            context.object.scale.x = self.first_value + delta * 0.001
            context.object.scale.y = self.first_value + delta * 0.001
            context.object.scale.z = self.first_value + delta * 0.001

        elif event.type == 'LEFTMOUSE':
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.object.scale.x = self.first_value
            context.object.scale.y = self.first_value
            context.object.scale.z = self.first_value

            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.object:
            self.first_mouse_y = event.mouse_y
            self.first_value = context.object.scale.x
            self.first_value = context.object.scale.y
            self.first_value = context.object.scale.z

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}


class dup_x(bpy.types.Macro):
	bl_idname = "object.dup_x"
	bl_label = "dup_x"
	bl_options = {'REGISTER','UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None


class dup_x_01(bpy.types.Operator):
	bl_idname = "object.dup_x_01"
	bl_label = "dup_x_01"

	def execute(self, context):
		snap_dx = bpy.context.scene.tool_settings.use_snap
		snape_dx = bpy.context.scene.tool_settings.snap_element
		snapt_dx = bpy.context.scene.tool_settings.snap_target
		snapr_dx = bpy.context.scene.tool_settings.use_snap_align_rotation

		bpy.ops.object.duplicate_move_linked()

		bpy.context.scene.tool_settings.use_snap = True
		bpy.context.scene.tool_settings.use_snap_align_rotation = True
		bpy.context.scene.tool_settings.snap_element = 'FACE'
		bpy.context.scene.tool_settings.snap_target = 'MEDIAN'
		bpy.context.scene.tool_settings.use_snap_project = False


		return {'FINISHED'}


class dup_x_02(bpy.types.Operator):
	bl_idname = "object.dup_x_02"
	bl_label = "dup_x_02"

	def execute(self, context):
		bpy.context.scene.tool_settings.use_snap = False

		return {'FINISHED'}

class dup_x_03(bpy.types.Operator):
	bl_idname = "object.dup_x_03"
	bl_label = "dup_x_03"

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):

		return {'FINISHED'}







class dup_x_04(bpy.types.Operator):
	bl_idname = "object.dup_x_04"
	bl_label = "dup_x_04"

	def execute(self, context):
		bpy.ops.transform.resize("INVOKE_DEFAULT")

		return {'FINISHED'}




class dup_x_05(bpy.types.Operator):
	bl_idname = "object.dup_x_05"
	bl_label = "dup_x_05"

	def execute(self, context):
		bpy.ops.transform.rotate("INVOKE_DEFAULT",constraint_orientation='NORMAL',constraint_axis=(False, False, True))

		return {'FINISHED'}


class dup_x_06(bpy.types.Operator):
	bl_idname = "object.dup_x_06"
	bl_label = "dup_x_06"

	def execute(self, context):
		bpy.ops.transform.translate(value=(0.1, 0, 0), constraint_axis=(True, False, False), constraint_orientation='GLOBAL',)

		return {'FINISHED'}

class dup_x_reset(bpy.types.Operator):
	bl_idname = "object.dup_x_reset"
	bl_label = "dup_x_reset"

	def execute(self, context):
		bpy.context.scene.tool_settings.use_snap = snap_dx
		bpy.context.scene.tool_settings.snap_element = snape_dx
		bpy.context.scene.tool_settings.snap_target = snapt_dx
		bpy.context.scene.tool_settings.use_snap_align_rotation = snapr_dx

		return {'FINISHED'}














#
# addon_keymaps = []
# def register():
# 	bpy.utils.register_class(dup_x_modal)
# 	bpy.utils.register_class(dup_x)
# 	bpy.utils.register_class(dup_x_01)
# 	bpy.utils.register_class(dup_x_02)
# 	bpy.utils.register_class(dup_x_03)
# 	bpy.utils.register_class(dup_x_04)
# 	bpy.utils.register_class(dup_x_05)
# 	bpy.utils.register_class(dup_x_06)
# 	bpy.utils.register_class(dup_x_reset)
#
# 	bpy.utils.register_module(__name__)
# 	wm = bpy.context.window_manager




		# store keymaps here to access after registration
addon_keymaps = []
def register():
	bpy.utils.register_module(__name__)
	# ヘッダーメニューに項目追加


	wm = bpy.context.window_manager

	km = wm.keyconfigs.addon.keymaps.new(name = 'Object Mode', space_type = 'EMPTY')
	kmi = km.keymap_items.new(dup_x.bl_idname, 'T', 'PRESS', shift=True, oskey=True)
	addon_keymaps.append((km, kmi))


	# マクロ登録
	dup_x.define('OBJECT_OT_dup_x_01')
	dup_x.define('TRANSFORM_OT_translate')
	dup_x.define('OBJECT_OT_dup_x_02')
	# dup_x.define('OBJECT_OT_modal_operator')
	# dup_x.define('OBJECT_OT_dup_x_02')
	dup_x.define('OBJECT_OT_dup_x_03')
	dup_x.define('OBJECT_OT_dup_x_modal')
	dup_x.define('OBJECT_OT_dup_x_05')
	# dup_x.define('OBJECT_OT_dup_x_06')
	# dup_x.define('OBJECT_OT_dup_x_04')
	# dup_x.define('OBJECT_OT_dup_x_reset')


def unregister():
	bpy.utils.unregister_class(dup_x_modal)
	bpy.utils.unregister_class(dup_x)
	bpy.utils.unregister_class(dup_x_01)
	bpy.utils.unregister_class(dup_x_02)
	bpy.utils.unregister_class(dup_x_03)
	bpy.utils.unregister_class(dup_x_04)
	bpy.utils.unregister_class(dup_x_05)
	bpy.utils.unregister_class(dup_x_06)
	bpy.utils.unregister_class(dup_x_reset)

	bpy.utils.unregister_module(__name__)
	# handle the keymap
	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()

if __name__ == "__main__":
	register()
