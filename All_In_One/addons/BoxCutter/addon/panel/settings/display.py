import bpy

from bpy.types import Panel

from ... utility import addon, names


class BC_PT_display_settings(Panel):
    bl_label = 'Display'
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

        self.label_row(layout.row(), preference.display, 'fade_distance', label='Fade Distance')
        self.label_row(layout.row(), preference.display, 'wire_only')
        if preference.display.wire_only:
            self.label_row(layout.row(), preference.display, 'thick_wire')
            self.label_row(layout.row(), preference.display, 'wire_size_factor', 'Wire Multiplier')


    def label_row(self, row, path, prop, label=''):
        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')
