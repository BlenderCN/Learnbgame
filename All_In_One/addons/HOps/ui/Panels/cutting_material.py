import bpy
from bpy.types import Panel

from ... preferences import get_preferences


class HOPS_PT_material_hops(Panel):
    bl_label = 'Cutting Material'
    bl_space_type = 'VIEW_3D'
    bl_category = 'HardOps'
    bl_region_type = 'UI'


    def draw(self, context):
        layout = self.layout
        option = context.window_manager.Hard_Ops_material_options

        row = layout.row(align=True)
        row.alignment = 'LEFT'

        column = layout.column(align=True)

        row = column.row(align=True)
        row.prop(option, 'material_mode', expand=True)

        row = column.row(align=True)

        if option.material_mode == 'ALL':
            row.prop_search(option, 'active_material', bpy.data, 'materials', text='')

        else:
            row.prop_search(option, 'active_material', context.active_object, 'material_slots', text='')

        row.prop(option, 'force', text='', icon='FORCE_FORCE')
