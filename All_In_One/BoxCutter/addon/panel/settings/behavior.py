import bpy

from bpy.types import Panel

from ... utility import addon, names


class BC_PT_behavior_settings(Panel):
    bl_label = 'Behavior'
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

                row = layout.row(align=True)
                self.label_row(layout.row(), option, 'active_only', label='Active only')
                self.label_row(layout.row(), preference.behavior, 'quick_execute')
                self.label_row(layout.row(), preference.behavior, 'apply_slices')
                self.label_row(layout.row(), preference.behavior, 'make_active')
                self.label_row(layout.row(), preference.behavior, 'auto_smooth')
                self.label_row(layout.row(), preference.behavior, 'parent_shape')
                self.label_row(layout.row(), preference.behavior, 'autohide_shapes', label='Auto Hide')
                self.label_row(layout.row(), preference.behavior, 'use_multi_edit')
                self.label_row(layout.row(), preference.behavior, 'simple_trace')
                self.label_row(layout.row(), preference.behavior, 'sort_modifiers')

                if preference.behavior.sort_modifiers:
                    row = layout.row(align=True)
                    row.alignment = 'RIGHT'

                    if preference.behavior.sort_bevel:
                        row.prop(preference.behavior, 'sort_bevel_last', text='', icon='SORT_ASC')
                        row.separator()

                    row.prop(preference.behavior, 'sort_bevel', text='', icon='MOD_BEVEL')
                    row.prop(preference.behavior, 'sort_weighted_normal', text='', icon='MOD_NORMALEDIT')
                    row.prop(preference.behavior, 'sort_array', text='', icon='MOD_ARRAY')
                    row.prop(preference.behavior, 'sort_mirror', text='', icon='MOD_MIRROR')
                    row.prop(preference.behavior, 'sort_solidify', text='', icon='MOD_SOLIDIFY')
                    row.prop(preference.behavior, 'sort_simple_deform', text='', icon='MOD_SIMPLEDEFORM')
                    row.prop(preference.behavior, 'sort_triangulate', text='', icon='MOD_TRIANGULATE')

                self.label_row(layout.row(), preference.behavior, 'keep_modifiers')

                if preference.behavior.keep_modifiers:
                    row = layout.row(align=True)
                    row.alignment = 'RIGHT'
                    row.prop(preference.behavior, 'keep_bevel', text='', icon='MOD_BEVEL')
                    row.prop(preference.behavior, 'keep_solidify', text='', icon='MOD_SOLIDIFY')
                    row.prop(preference.behavior, 'keep_array', text='', icon='MOD_ARRAY')
                    row.prop(preference.behavior, 'keep_mirror', text='', icon='MOD_MIRROR')
                    row.prop(preference.behavior, 'keep_screw', text='', icon='MOD_SCREW')
                    row.prop(preference.behavior, 'keep_lattice', text='', icon='MOD_LATTICE')

                break


    def label_row(self, row, path, prop, label=''):
        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')
