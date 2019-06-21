import bpy
from bpy.types import Panel

from ... preferences import get_preferences


class HOPS_PT_mesh_clean_options(Panel):
    bl_label = 'Mesh Clean Options'
    bl_space_type = 'VIEW_3D'
    bl_category = 'HardOps'
    bl_region_type = 'UI'


    def draw(self, context):
        layout = self.layout
        preference = get_preferences()

        column = layout.column(align=True)

        row = column.row(align=True)
        row.prop(preference, 'meshclean_mode', expand=True)

        row = column.row(align=True)
        row.prop(preference, 'meshclean_dissolve_angle', text="Limited Dissolve Angle")

        row = column.row(align=True)
        row.prop(preference, 'meshclean_remove_threshold', text="Remove Threshold")

        row = column.row(align=True)
        row.prop(preference, 'meshclean_unhide_behavior', text="Unhide Mesh")

        row = column.row(align=True)
        row.prop(preference, 'meshclean_delete_interior', text="Delete Interior Faces")
