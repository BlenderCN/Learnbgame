import bpy
from bpy.types import Panel


class HOPS_PT_status(Panel):
    bl_label = 'Status'
    bl_space_type = 'VIEW_3D'
    bl_category = 'HardOps'
    bl_region_type = 'UI'


    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        option = wm.Hard_Ops_helper_options

        column = layout.column(align=True)

        row = column.row(align=True)
        row.prop(option, 'status', expand=True)
