import os
import bpy
import rna_keymap_ui
from bpy.props import *
from . utils.registers import get_hotkey_entry_item


def get_preferences():
    name = get_addon_name()
    return bpy.context.user_preferences.addons[name].preferences


def get_addon_name():
    return os.path.basename(os.path.dirname(os.path.realpath(__file__)))

manipulator_modes = [
    ("MODE1", "mode1", ""),
    ("MODE2", "mode2", ""),
    ("MODE3", "mode3", "")]

settings_tabs_items = [
    ("UI", "UI", ""),
    ("INFO", "Info", ""),
    ("KEYMAP", "Keymap", "")]


class FidgetPreferences(bpy.types.AddonPreferences):
    bl_idname = get_addon_name()

    tab = EnumProperty(name="Tab", items=settings_tabs_items)
    pref_mode = EnumProperty(name="Tab", items=manipulator_modes)
    mode = EnumProperty(name="", options={"SKIP_SAVE"}, items=manipulator_modes)

    fidget_manimulator_scale = FloatProperty(
        name="Fidget Manipulator Scale",
        description="Fidget manipulator Scale",
        default=0.7, min=0, max=10)

    fidget_manimulator_dots_scale = FloatProperty(
        name="Fidget Manipulator Dots Scale",
        description="Fidget manipulator Dots Scale",
        default=0.34, min=0, max=10)

    fidget_manimulator_radius = FloatProperty(
        name="Fidget Manipulator Radius",
        description="Fidget manipulator Radius",
        default=7, min=0, max=100)

    fidget_manimulator_rotation = IntProperty(
        name="Fidget Manipulator Rotation",
        description="Fidget manipulator Rotation",
        default=0, min=0, max=360)

    fidget_manimulator_rotation_angle = IntProperty(
        name="Fidget Manipulator Rotation Angle",
        description="Fidget manipulator Rotation Angle",
        default=30, min=1, max=360)

    fidget_outline_width = FloatProperty(
        name="Fidget Manipulator Outline Width",
        description="Fidget manipulator outline width",
        default=1, min=0, max=10)

    fidget_info_pos_x = FloatProperty(
        name="Fidget Manipulator Info Posx",
        description="Fidget Manipulator Info Posx",
        default=52)

    fidget_info_pos_y = FloatProperty(
        name="Fidget Manipulator Info Posy",
        description="Fidget Manipulator Info Posy",
        default=-21)

    fidget_info_font_size = IntProperty(
        name="Fidget Manipulator Info Font Size",
        description="Fidget Manipulator Info Font Size",
        default=11, min=1, max=100)

    fidget_enable_info = BoolProperty(
        name="Enable Info",
        description="Enable Info",
        default=True)

    fidget_enable_outline = BoolProperty(
        name="Enable Outline",
        description="Enable Outline",
        default=True)

    # colors

    fidget_mode1_color = FloatVectorProperty(
            name="",
            default=(0.7, 0.7, 0.7, 0.1),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_mode2_color = FloatVectorProperty(
            name="",
            default=(0.7, 0.7, 0.7, 0.1),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_mode3_color = FloatVectorProperty(
            name="",
            default=(0.7, 0.7, 0.7, 0.1),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_mode1_color_hover = FloatVectorProperty(
            name="",
            default=(0.29, 0.52, 1.0, 0.9),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_mode2_color_hover = FloatVectorProperty(
            name="",
            default=(0.29, 0.52, 1.0, 0.9),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_mode3_color_hover = FloatVectorProperty(
            name="",
            default=(0.29, 0.52, 1.0, 0.9),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_button1_color = FloatVectorProperty(
            name="",
            default=(0.3, 0.3, 0.3, 0.5),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_button2_color = FloatVectorProperty(
            name="",
            default=(0.5, 0.5, 0.5, 0.5),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_button3_color = FloatVectorProperty(
            name="",
            default=(0.448, 0.448, 0.448, 0.5),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_button1_color_hover = FloatVectorProperty(
            name="",
            default=(0.29, 0.52, 1.0, 0.9),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_button2_color_hover = FloatVectorProperty(
            name="",
            default=(0.29, 0.52, 1.0, 0.9),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_button3_color_hover = FloatVectorProperty(
            name="",
            default=(0.29, 0.52, 1.0, 0.9),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    # mode2
    fidget_button1_color_mode2 = FloatVectorProperty(
            name="",
            default=(0.3, 0.3, 0.3, 0.5),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_button2_color_mode2 = FloatVectorProperty(
            name="",
            default=(0.5, 0.5, 0.5, 0.5),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_button3_color_mode2 = FloatVectorProperty(
            name="",
            default=(0.448, 0.448, 0.448, 0.5),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_button1_color_mode2_hover = FloatVectorProperty(
            name="",
            default=(0.29, 0.52, 1.0, 0.9),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_button2_color_mode2_hover = FloatVectorProperty(
            name="",
            default=(0.29, 0.52, 1.0, 0.9),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_button3_color_mode2_hover = FloatVectorProperty(
            name="",
            default=(0.29, 0.52, 1.0, 0.9),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    # mode3
    fidget_button1_color_mode3 = FloatVectorProperty(
            name="",
            default=(0.3, 0.3, 0.3, 0.5),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_button2_color_mode3 = FloatVectorProperty(
            name="",
            default=(0.5, 0.5, 0.5, 0.5),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_button3_color_mode3 = FloatVectorProperty(
            name="",
            default=(0.448, 0.448, 0.448, 0.5),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_button1_color_mode3_hover = FloatVectorProperty(
            name="",
            default=(0.29, 0.52, 1.0, 0.9),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_button2_color_mode3_hover = FloatVectorProperty(
            name="",
            default=(0.29, 0.52, 1.0, 0.9),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_button3_color_mode3_hover = FloatVectorProperty(
            name="",
            default=(0.29, 0.52, 1.0, 0.9),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_outline = FloatVectorProperty(
            name="",
            default=(0.1, 0.1, 0.1, 0.4),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    fidget_info_color = FloatVectorProperty(
            name="",
            default=(0.7, 0.7, 0.7, 0.7),
            size=4,
            min=0, max=1,
            subtype='COLOR'
            )

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        row = col.row()
        row.prop(self, "tab", expand=True)

        box = col.box()

        if self.tab == "UI":
            self.draw_ui_tab(box)
        # elif self.tab == "PROPERTIES":
        #     self.draw_properties_tab(box)
        elif self.tab == "INFO":
            self.draw_info_tab(box)
        elif self.tab == "KEYMAP":
            self.draw_keymap_tab(box)

    def draw_ui_tab(self, layout):
        box = layout.box()
        row = box.row(align=True)
        row.label("Size")
        row = box.row(align=True)
        row.prop(self, "fidget_manimulator_scale", text="Manipualtor Scale")
        row = box.row(align=True)
        row.prop(self, "fidget_manimulator_dots_scale", text="Manipulator dots scale")
        row.prop(self, "fidget_manimulator_radius", text="Manipulator dots radius")
        row = box.row(align=True)
        row.prop(self, "fidget_manimulator_rotation", text="Manipulator rotation")
        row = box.row(align=True)
        row.prop(self, "fidget_manimulator_rotation_angle", text="Manipulator rotation angle")
        row = box.row(align=True)
        row.prop(self, "fidget_enable_info", text="Show info")
        row.prop(self, "fidget_info_pos_x", text="Info x position")
        row.prop(self, "fidget_info_pos_y", text="Info y position")
        row.prop(self, "fidget_info_font_size", text="Info font size")
        row = box.row(align=True)
        row.prop(self, "fidget_info_color", text="Info text color")

        box = layout.box()
        row = box.row(align=True)
        row.label("Modes Colors")
        row = box.row(align=True)
        row.prop(self, "fidget_mode1_color", text="Mode 1 color")
        row.prop(self, "fidget_mode1_color_hover", text="Mode 1 hover")
        row = box.row(align=True)
        row.prop(self, "fidget_mode2_color", text="Mode 2 color")
        row.prop(self, "fidget_mode2_color_hover", text="Mode 2 hover")
        row = box.row(align=True)
        row.prop(self, "fidget_mode3_color", text="Mode 3 color")
        row.prop(self, "fidget_mode3_color_hover", text="Mode 3 hover")

        box = layout.box()
        row = box.row(align=True)
        row.label("Manipulator Colors")
        row.prop(self, "pref_mode", expand=True)

        if self.pref_mode == "MODE1":
            row = box.row(align=True)
            row.prop(self, "fidget_button1_color", text="Button 1 color")
            row.prop(self, "fidget_button1_color_hover", text="Button 1 hover")
            row = box.row(align=True)
            row.prop(self, "fidget_button2_color", text="Button 2 color")
            row.prop(self, "fidget_button2_color_hover", text="Button 2 hover")
            row = box.row(align=True)
            row.prop(self, "fidget_button3_color", text="Button 3 color")
            row.prop(self, "fidget_button3_color_hover", text="Button 3 hover")
        elif self.pref_mode == "MODE2":
            row = box.row(align=True)
            row.prop(self, "fidget_button1_color_mode2", text="Button 1 color")
            row.prop(self, "fidget_button1_color_mode2_hover", text="Button 1 hover")
            row = box.row(align=True)
            row.prop(self, "fidget_button2_color_mode2", text="Button 2 color")
            row.prop(self, "fidget_button2_color_mode2_hover", text="Button 2 hover")
            row = box.row(align=True)
            row.prop(self, "fidget_button3_color_mode2", text="Button 3 color")
            row.prop(self, "fidget_button3_color_mode2_hover", text="Button 3 hover")
        elif self.pref_mode == "MODE3":
            row = box.row(align=True)
            row.prop(self, "fidget_button1_color_mode3", text="Button 1 color")
            row.prop(self, "fidget_button1_color_mode3_hover", text="Button 1 hover")
            row = box.row(align=True)
            row.prop(self, "fidget_button2_color_mode3", text="Button 2 color")
            row.prop(self, "fidget_button2_color_mode3_hover", text="Button 2 hover")
            row = box.row(align=True)
            row.prop(self, "fidget_button3_color_mode3", text="Button 3 color")
            row.prop(self, "fidget_button3_color_mode3_hover", text="Button 3 hover")

        box = layout.box()
        row = box.row(align=True)
        row.label("Manipulator outline")
        row = box.row(align=True)
        row.prop(self, "fidget_enable_outline", text="Enable outline")
        row.prop(self, "fidget_outline_width", text="Outline width")
        row.prop(self, "fidget_outline")

    def draw_properties_tab(self, layout):
        box = layout.box()

    def draw_info_tab(self, layout):
        layout.label('Info')

    def draw_keymap_tab(self, layout):
        box = layout.box()
        split = box.split()
        col = split.column()
        col.label('Do not remove hotkeys, disable them instead.')
        col.separator()
        col.label('Hotkeys')

        col.separator()

        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user

        col.label('Open:')

        col.separator()
        km = kc.keymaps['3D View']
        kmi = get_hotkey_entry_item(km, 'fidget.viewport_buttons', 'none', 'none')
        if kmi:
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label("No hotkey entry found")
            col.label("restore hotkeys from interface tab")
