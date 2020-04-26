import bpy

from bpy.types import Panel

from ... utility import addon, names


class BC_PT_input_settings(Panel):
    bl_label = 'Input'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BoxCutter'
    bl_parent_id = 'BC_PT_settings'
    bl_options = {'DEFAULT_CLOSED'}


    @classmethod
    def poll(cls, context):
        return context.region.type == 'UI'


    def draw(self, context):
        layout = self.layout

        preference = addon.preference()

        option = None
        for tool in context.workspace.tools:
            if tool.idname == 'BoxCutter' and tool.mode == context.workspace.tools_mode:
                option = tool.operator_properties('bc.draw_shape')

                self.label_row(layout.row(), context.preferences.inputs, 'drag_threshold', label='Drag threshold')

                self.label_row(layout.row(), preference.keymap, 'enable_surface_toggle')
                self.label_row(layout.row(), preference.keymap, 'alt_preserve', label='Preserve Alt')
                self.label_row(layout.row(), preference.keymap, 'rmb_cancel_ngon', label='RMB Cancel Ngon')

                if context.workspace.tools_mode == 'EDIT_MESH':
                    self.label_row(layout.row(), preference.keymap, 'edit_disable_modifiers', label='Disable Ctrl & Shift LMB')

                self.label_row(layout.row(), preference.keymap, 'alt_draw', label='Alt Center')
                self.label_row(layout.row(), preference.keymap, 'shift_draw', label='Shift Uniform')

                break


    def label_row(self, row, path, prop, label=''):
        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')
