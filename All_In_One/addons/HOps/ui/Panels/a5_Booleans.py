import bpy
from bpy.props import *
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )
import os
from ... icons import get_icon_id
from ... utils.addons import addon_exists
from ... preferences import pro_mode_enabled

class HOPS_PT_BooleansPanel(bpy.types.Panel):
    bl_label = "Booleans"
    # bl_category = "HardOps"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)

        col.operator("hops.bool_intersect", text="Intersection", icon="ROTATECENTER")
        col.operator("hops.bool_union", text="Union", icon="ROTATECOLLECTION")
        col.operator("hops.bool_difference", text="Difference", icon="ROTACTIVE")
