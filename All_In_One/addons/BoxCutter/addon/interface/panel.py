import bpy

from bpy.types import Panel
from bpy.utils import register_class, unregister_class

from .. preference import names
from .. utility import addon


class BC_PT_settings(Panel):
    bl_idname = 'bc.settings'
    bl_space_type = 'VIEW_3D'
    bl_label = 'Settings'
    bl_region_type = 'UI'
    bl_category = 'Box Cutter'

    def draw(self, context):
        layout = self.layout

        preference = addon.preference()

        for tool in context.workspace.tools:
            if tool.name == 'BoxCutter' and tool.mode == context.workspace.tools_mode:
                option = tool.operator_properties('bc.draw_shape')

                break

        if option.shape == 'CIRCLE':
            row = layout.row()
            row.label(text='Vertices:')
            row.prop(option, 'vertices', text='')

        row = layout.row()
        row.label(text='Array count:')
        row.prop(option, 'array_count', text='')

        row = layout.row()
        row.label(text='Segments:')
        row.prop(option, 'segments', text='')

        row = layout.row()
        row.label(text=names['auto_smooth'])
        row.prop(preference, 'auto_smooth', text='')

        row = layout.row()
        row.label(text=names['use_multi_edit'])
        row.prop(preference, 'use_multi_edit', text='')

        row = layout.row()
        row.label(text=names['display_wires'])
        row.prop(preference, 'display_wires', text='')       

        row = layout.row()
        row.label(text=names['sort_modifiers'])
        row.prop(preference, 'sort_modifiers', text='')

        if preference.sort_modifiers:
            row = layout.row(align=True)
            row.alignment = 'RIGHT'
            row.prop(preference, 'sort_bevel', text='', icon='MOD_BEVEL')
            row.prop(preference, 'sort_weighted_normal', text='', icon='MOD_NORMALEDIT')
            row.prop(preference, 'sort_array', text='', icon='MOD_ARRAY')
            row.prop(preference, 'sort_mirror', text='', icon='MOD_MIRROR')

classes = [
    BC_PT_settings]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)