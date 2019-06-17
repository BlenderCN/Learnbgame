import bpy
from bpy.types import Panel

from ... preferences import get_preferences


class HOPS_PT_operator_options(Panel):
    bl_label = 'Operator Options'
    bl_space_type = 'VIEW_3D'
    bl_category = 'HardOps'
    bl_region_type = 'UI'


    def draw(self, context):
        layout = self.layout
        preference = get_preferences()

        column = layout.column(align=True)

        row = column.row(align=True)
        row.label(text='Modals:')

        column.separator()

        row = column.row(align=True)
        row.prop(preference, 'Hops_modal_scale', text='Modal Scale')
        row.prop(preference, 'adaptivewidth', text='Adapitve')

        column.separator()

        row = column.row(align=True)
        row.label(text='CSharpen:')

        column.separator()

        row = column.row(align=True)
        row.prop(preference, 'bevel_loop_slide', text='use Loop slide')
        row.prop(preference, 'auto_bweight', text='jump to (B)Width')

        column.separator()

        row = column.row(align=True)
        row.label(text='Mirror:')

        row = column.row(align=True)
        row.prop(preference, 'Hops_mirror_modal_scale', text='Mirror Scale')
        row.prop(preference, 'Hops_mirror_modal_sides_scale', text='Mirror Size')

        row = column.row(align=True)
        row.prop(preference, 'Hops_mirror_modal_Interface_scale', text='Mirror Interface Scale')
        row.prop(preference, 'Hops_mirror_modal_revert', text='Revert')

        column.separator()
        column.separator()

        row = column.row(align=True)
        row.label(text='Cut In:')
        row.prop(preference, 'keep_cutin_bevel', expand=True)

        column.separator()

        row = column.row(align=True)
        row.label(text='Array:')
        row.prop(preference, 'force_array_reset_on_init', expand=True)

        row = column.row(align=True)
        row.label(text='')
        row.prop(preference, 'force_array_apply_scale_on_init', expand=True)

        column.separator()
        column.separator()

        row = column.row(align=True)
        row.label(text='Thick:')
        row.prop(preference, 'force_thick_reset_solidify_init', expand=True)

        column.separator()
