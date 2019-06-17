import bpy
from bpy.props import *
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )
from ... icons import get_icon_id


class HOPS_PT_HelpPanel(bpy.types.Panel):
    bl_label = "Help"
    # bl_category = "HardOps"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    #bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        layout.operator("hops.learning_popup", text="Hard Ops Learning", icon_value=get_icon_id("Noicon"))
        #layout.operator("hops.viewport_buttons", text="Viewport Buttons", icon_value=get_icon_id("Noicon"))
          