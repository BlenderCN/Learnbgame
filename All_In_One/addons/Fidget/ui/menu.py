import bpy
from bpy.props import *


class FidgetCustomMenu(bpy.types.Menu):
    bl_idname = "fidget.custom_menu"
    bl_label = "Operators Library"

    def draw(self, context):
        layout = self.layout
        layout.menu("fidget.custom_object_menu", text="Object Mode")
        layout.menu("fidget.custom_edit_menu", text="Edit Mode")
        layout.separator()
        layout.menu("fidget.custom_bc_menu", text="BoxCutter")
        layout.menu("fidget.custom_hops_menu", text="Hardops")
        layout.separator()
        layout.menu("fidget.custom_menus_menu", text="Menus")
        layout.separator()
        layout.menu("fidget.custom_modifiers_menu", text="Modifiers")

        # TO DO
        # layout.menu("fidget.custom_logic_menu", text="Logic")
