import bpy

from bpy.types import Panel

from ... utility import addon, names


class BC_PT_shape_settings(Panel):
    bl_label = 'Shape'
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

                self.label_row(layout.row(), preference.shape, 'offset')
                self.label_row(layout.row(), preference.shape, 'lazorcut_limit')

                layout.separator()

                self.label_row(layout.row(), preference.shape, 'circle_vertices')
                self.label_row(layout.row(), preference.shape, 'inset_thickness')

                layout.separator()

                self.label_row(layout.row(), preference.shape, 'array_count')
                self.label_row(layout.row(), preference.shape, 'solidify_thickness')
                self.label_row(layout.row(), preference.shape, 'bevel_width')
                self.label_row(layout.row(), preference.shape, 'bevel_segments')
                self.label_row(layout.row(), preference.shape, 'quad_bevel')
                self.label_row(layout.row(), preference.shape, 'straight_edges')

                break


    def label_row(self, row, path, prop, label=''):
        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')
