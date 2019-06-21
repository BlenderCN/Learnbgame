import bpy
from bpy.props import *
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )
from math import radians, degrees
from ... icons import get_icon_id
from ... preferences import get_preferences


class HOPS_PT_SharpPanel(bpy.types.Panel):
    bl_label = "Sharp"
    # bl_category = "HardOps"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        col.prop(get_preferences(), "sharp_use_crease", text="Apply crease")
        col.prop(get_preferences(), "sharp_use_bweight", text="Apply bweight")
        col.prop(get_preferences(), "sharp_use_seam", text="Apply seam")
        col.prop(get_preferences(), "sharp_use_sharp", text="Apply sharp")

        colrow = col.row(align=True)
        colrow.operator("hops.set_sharpness_30", text="30")
        colrow.operator("hops.set_sharpness_45", text="45")
        colrow.operator("hops.set_sharpness_60", text="60")

        col.prop(get_preferences(), "sharpness", text="Sharpness")

        col.separator()
        col.operator("hops.sharp_manager", text="Sharps Manager")