import bpy
from bpy.props import *
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )
import os

class HOPS_PT_InsertsPanel(bpy.types.Panel):
    bl_label = "Inserts"
    # bl_category = "HardOps"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout.column(1)           
        row = layout.row(1)

        wm = context.window_manager
        row.template_icon_view(wm, "Hard_Ops_previews")
        row.template_icon_view(wm, "sup_preview")

        layout = self.layout
        layout.separator()

        if len(context.selected_objects) > 1:
          layout.operator("object.to_selection", text="Obj to selection", icon="MOD_MULTIRES")
          layout.operator("make.link", text="Link Objects", icon='CONSTRAINT' )
          layout.operator("unlink.objects", text="Unlink Objects", icon='UNLINKED' )
        else:
          layout.label(text="Select 2 obj or more for more options")

