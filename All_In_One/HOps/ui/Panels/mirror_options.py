import bpy
from bpy.types import Panel

from ... preferences import get_preferences


class HOPS_PT_mirror_options(Panel):
    bl_label = 'Mirror Options'
    bl_space_type = 'VIEW_3D'
    bl_category = 'HardOps'
    bl_region_type = 'UI'


    def draw(self, context):
        layout = self.layout
        preference = get_preferences()

        column = layout.column(align=True)

        row = column.row(align=True)
        row.prop(preference, 'Hops_mirror_modes', expand=True)

        if preference.Hops_mirror_modes in {'BISECT', 'SYMMETRY'}:
            row = column.row(align=True)
            row.prop(preference, 'Hops_mirror_direction', expand=True)
