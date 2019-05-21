import os
import bpy
import rna_keymap_ui
from math import radians
from mathutils import Vector
from bpy.props import EnumProperty, StringProperty, FloatProperty, BoolProperty, FloatVectorProperty
from . utils.addons import addon_exists
from . ui.addon_checker import draw_addon_diagnostics
from . utils.blender_ui import write_text, get_dpi_factor
from . utils.registers import get_hotkey_entry_item


def get_preferences():
    name = get_addon_name()
    return bpy.context.preferences.addons[name].preferences


def get_addon_name():
    return os.path.basename(os.path.dirname(os.path.realpath(__file__)))


# Specific preference settings

def experimental_ssharp():
    return get_preferences().experimental_ssharp


def tool_overlays_enabled():
    return get_preferences().enable_tool_overlays


def pie_F6_enabled():
    return get_preferences().pie_F6


def pie_bool_options_enabled():
    return get_preferences().pie_bool_options


def use_asset_manager():
    return get_preferences().Asset_Manager_Preview and addon_exists("asset_management")


def right_handed_enabled():
    return get_preferences().right_handed


def pro_mode_enabled():
    return get_preferences().pro_mode


def extra_options_enabled():
    return get_preferences().extra_options
    

def BC_unlock_enabled():
    return get_preferences().BC_unlock


def mira_handler_enabled():
    return get_preferences().mira_handler_enabled


# colors


def get_hops_preferences_colors_with_transparency(transparency):
    color_text1 = [Hops_text_color()[0], Hops_text_color()[1], Hops_text_color()[2], Hops_text_color()[3] * transparency]
    color_text2 = [Hops_text2_color()[0], Hops_text2_color()[1], Hops_text2_color()[2], Hops_text2_color()[3] * transparency]
    color_border = [Hops_border_color()[0], Hops_border_color()[1], Hops_border_color()[2], Hops_border_color()[3] * transparency]
    color_border2 = [Hops_border2_color()[0], Hops_border2_color()[1], Hops_border2_color()[2], Hops_border2_color()[3] * transparency]
    return color_text1, color_text2, color_border, color_border2


def Hops_text_color():
    return get_preferences().Hops_text_color


def Hops_text2_color():
    return get_preferences().Hops_text2_color


def Hops_border_color():
    return get_preferences().Hops_border_color


def Hops_border2_color():
    return get_preferences().Hops_border2_color

# Display Parameter Time


def Hops_display_time():
    return get_preferences().display_time


def Hops_fadeout_time():
    return get_preferences().fadeout_time

# logo


def Hops_logo_color():
    return get_preferences().Hops_logo_color


def Hops_logo_color_boolshape():
    return get_preferences().Hops_logo_color_boolshape


def Hops_logo_color_boolshape2():
    return get_preferences().Hops_logo_color_boolshape2


def Hops_logo_color_cstep():
    return get_preferences().Hops_logo_color_cstep


def Hops_logo_color_csharp():
    return get_preferences().Hops_logo_color_csharp


def Hops_logo_size():
    return get_preferences().Hops_logo_size


def Hops_logo_x_position():
    return get_preferences().Hops_logo_x_position


def Hops_logo_y_position():
    return get_preferences().Hops_logo_y_position


def Hops_display_logo():
    return get_preferences().Hops_display_logo


def Hops_display_undefined_status():
    return get_preferences().Hops_display_undefined_status


def Hops_display_text_status():
    return get_preferences().Hops_display_text_status


def Hops_hud_text_color():
    return get_preferences().Hops_hud_text_color


def get_color_for_drawing():

    bg2R = 0.692
    bg2G = 0.298
    bg2B = 0.137
    bg2A = 0.718

    bgR = 0.235
    bgG = 0.235
    bgB = 0.235
    bgA = 0.8

    txR = 0.6
    txG = 0.6
    txB = 0.6
    txA = 0.9

    return bg2R, bg2G, bg2B, bg2A, bgR, bgG, bgB, bgA, txR, txG, txB, txA

# Tool Panel for update category and hide panel


def update_HardOps_Panel_Tools(self, context):
    panel = getattr(bpy.types, "hops_main_panel", None)
    if panel is not None:
        bpy.utils.unregister_class(panel)
        panel.bl_category = get_preferences().toolbar_category_name
        bpy.utils.register_class(panel)


def category_name_changed(self, context):
    category = get_preferences().toolbar_category_name
    change_hard_ops_category(category)

# edit mode properties


def Hops_circle_size():
    return get_preferences().Hops_circle_size


booleans_modes = [
    ("BMESH", "Bmesh", ""),
    ("CARVE", "Carve", "")]

settings_tabs_items = [
    ("UI", "UI", ""),
    ("DRAWING", "Drawing", ""),
    ("INFO", "Info", ""),
    ("KEYMAP", "Keymap", ""),
    ("LINKS", "Links / Help", ""),
    ("ADDONS", "Addons", "")]

mirror_modes = [
    ("MODIFIER", "Mod", ""),
    ("BISECT", "Bisect", ""),
    ("SYMMETRY", "Symmetry", "")]

mirror_modes_multi = [
    ("VIA_ACTIVE", "Mod", ""),
    ("BISECT", "Bisect", ""),
    ("SYMMETRY", "Symmetry", "")]

mirror_direction = [
    ("-", "-", ""),
    ("+", "+", "")]

symmetrize_type = [
    ("DEFAULT", "Default", ""),
    ("Machin3", "Machin3", "")]


class HardOpsPreferences(bpy.types.AddonPreferences):

    debug: BoolProperty(name="debug", default=False)

    decalmachine_fix: BoolProperty(name="Use Setup For DECALmachine", default=False)

    adaptivemode: BoolProperty("Adaptive Segments", default=False)
    adaptiveoffset: FloatProperty("Adaptive Offset", default=10, min=0)
    adaptivewidth: BoolProperty("Adaptive Segments", default=False)

    auto_bweight: BoolProperty("auto bweight", default=False)

    keep_cutin_bevel: BoolProperty(name="Keep Cut In Bevel", default=True)
    force_array_reset_on_init: BoolProperty(name="Force Array Reset", default=False)
    force_array_apply_scale_on_init: BoolProperty(name="Force Array Apply Scale", default=False)
    force_thick_reset_solidify_init: BoolProperty(name="Force Reset Solidify", default=False)

    meshclean_mode: EnumProperty(name="Mode",
                                 description="",
                                 items=[('ACTIVE', "Active", "Effect all the active object geometry"),
                                        ('SELECTED', "Selected", "Effect only selected geometry or selected objects geometry"),
                                        ('VISIBLE', "Visible", "Effect only visible geometry")],
                                 default='ACTIVE')

    meshclean_dissolve_angle: FloatProperty(name="Limited Dissolve Angle",
                                            default=radians(0.5),
                                            min=radians(0),
                                            max=radians(30),
                                            subtype="ANGLE")
    meshclean_remove_threshold: FloatProperty(name="Remove Threshold Amount",
                                              description="Remove Double Amount",
                                              default=0.001,
                                              min=0.0001,
                                              max=1.00)
    meshclean_unhide_behavior: BoolProperty(default=True)
    meshclean_delete_interior: BoolProperty(default=False)

    experimental_ssharp: BoolProperty(name="Use Experimental Ssharp method", default=True)

    sharp_use_crease: BoolProperty(name="Allow Sharpening To Use Crease", default=False)
    sharp_use_bweight: BoolProperty(name="Allow Sharpening To Use Bevel Weight", default=True)
    sharp_use_seam: BoolProperty(name="Allow Sharpening To Use Seams", default=False)
    sharp_use_sharp: BoolProperty(name="Allow Sharpening To Use Sharp Edges", default=True)

    bl_idname = get_addon_name()

    workflow: EnumProperty(name="Mode",
                           description="",
                           items=[('DESTRUCTIVE', "Destructive", ""),
                                  ('NONDESTRUCTIVE', "NonDestructive", "")],
                           default='NONDESTRUCTIVE')

    workflow_mode: EnumProperty(name="Mode",
                                description="",
                                items=[('ANGLE', "Angle", ""),
                                       ('WEIGHT', "Weight", "")],
                                default='ANGLE')

    add_weighten_normals_mod: BoolProperty(name="Add weighten normals mod", default=True)

    helper_tab: StringProperty(name="Helper Set Category", default="MODIFIERS")

    tab: EnumProperty(name="Tab", items=settings_tabs_items)

    toolbar_category_name: StringProperty(
        name="Toolbar Category",
        default="HardOps",
        description="Name of the tab in the toolshelf in the 3d view",
        update=category_name_changed)

    enable_tool_overlays: BoolProperty(name="Enable Tool Overlays", default=True)

    mira_handler_enabled: BoolProperty(name="Hard Ops Mira Handler", default=False)

    Asset_Manager_Preview: BoolProperty(name="Asset Manager Preview", default=False)

    bevel_loop_slide: BoolProperty(
        name="Bweight loop slide",
        default=True,
        description="loop slide")

    pie_F6: BoolProperty(
        name="Pie F6",
        default=True,
        description="add F6 button to pie menu")

    pie_bool_options: BoolProperty(
        name="Pie Bool Options",
        default=True,
        description="add bool button to pie menu")

    right_handed: BoolProperty(
        name="Right Handed",
        default=True,
        description="Reverse The X Mirror For Right Handed People")

    pro_mode: BoolProperty(
        name="Pro Mode",
        default=False,
        description="Enables Pro Level Hard Ops Options")

    extra_options: BoolProperty(
        name="Extra Options",
        default=False,
        description="Enables Extra Options Hidden")

    BC_unlock: BoolProperty(
        name="BC",
        default=False,
        description="BC Support")

    hops_modal_help: BoolProperty(
        name="Modal Help",
        default=False,
        description="Enables help for modal operators")

    sharpness: FloatProperty(name="angle edge marks are applied to", default=radians(30), min=radians(1), max=radians(180), precision=3, unit='ROTATION')
    auto_smooth_angle: FloatProperty(name="angle edge marks are applied to", default=radians(60), min=radians(1), max=radians(180), precision=3, unit='ROTATION')

    # Display Parameter Time
    display_time: FloatProperty(name="Display Time", default=1, min=1, max=5)
    fadeout_time: FloatProperty(name="Fadeout Time", default=0.8, min=0, max=5)

    # ogo size

    Hops_logo_size: FloatProperty(
        name="HardOps Indicator Size",
        description="BoxCutter indicator size",
        default=2, min=0, max=100)

    Hops_logo_x_position: FloatProperty(
        name="HardOps Indicator X Position",
        description="BoxCutter Indicator X Position",
        default=-52)

    Hops_logo_y_position: FloatProperty(
        name="HardOps Indicator Y Position",
        description="BoxCutter Indicator Y Position",
        default=15)

    Hops_display_logo: BoolProperty(name="Dispalay Logo", default=True)
    Hops_display_undefined_status: BoolProperty(name="Dispalay Undefined Status", default=True)
    Hops_display_text_status: BoolProperty(name="Dispalay Undefined Status", default=False)

    # getimg theme colors

    bg2R, bg2G, bg2B, bg2A, bgR, bgG, bgB, bgA, txR, txG, txB, txA = get_color_for_drawing()

    Hops_text_color: FloatVectorProperty(
        name="",
        default=Vector((txR, txG, txB, txA)),
        size=4,
        min=0, max=1,
        subtype='COLOR')

    Hops_text2_color: FloatVectorProperty(
        name="",
        default=Vector((txR, txG, txB, txA)),
        size=4,
        min=0, max=1,
        subtype='COLOR')

    Hops_border_color: FloatVectorProperty(
        name="",
        default=Vector((bgR, bgG, bgB, bgA)),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_border2_color: FloatVectorProperty(
        name="",
        default=Vector((bg2R, bg2G, bg2B, bg2A)),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_logo_color: FloatVectorProperty(
        name="",
        default=(0.448, 0.448, 0.448, 0.1),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_logo_color_csharp: FloatVectorProperty(
        name="",
        default=(1, 0.597, 0.133, 0.9),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_logo_color_cstep: FloatVectorProperty(
        name="",
        default=(0.29, 0.52, 1.0, 0.9),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_logo_color_boolshape2: FloatVectorProperty(
        name="",
        default=(1, 0.133, 0.133, 0.53),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_logo_color_boolshape: FloatVectorProperty(
        name="",
        default=(0.35, 1, 0.29, 0.53),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    Hops_hud_text_color: FloatVectorProperty(
        name="",
        default=(1, 1, 1, 1),
        size=4,
        min=0, max=1,
        subtype='COLOR'
        )

    # operators
    Hops_mirror_modes: EnumProperty(name="Mirror Modes", items=mirror_modes, default='BISECT')
    Hops_mirror_modes_multi: EnumProperty(name="Mirror Modes Multi", items=mirror_modes_multi, default='VIA_ACTIVE')
    Hops_mirror_direction: EnumProperty(name="Mirror Direction", items=mirror_direction, default='+')
    Hops_Mir2_symmetrize_type: EnumProperty(name="Mir2 Symmetry Type", items=symmetrize_type, default='DEFAULT')

    Hops_mirror_modal_use_cursor: BoolProperty(
        name="Modal Mirror Uess Cursor",
        default=False,
        description="uses cursor for modal mirror")

    Hops_mirror_modal_revert: BoolProperty(
        name="Modal Mirror Revert",
        default=True,
        description="reverts modal mirror")

    Hops_mirror_modal_Interface_scale: FloatProperty(
        name="Modal Mirror Interface Scale",
        description="Modal Mirror Interface Scale",
        default=0.7, min=0.1, max=50)

    Hops_gizmo_array: FloatProperty(
        name="Array gizmo",
        description="Array gizmo",
        default=0
        )

    Hops_mirror_modal_scale: FloatProperty(
        name="Modal Mirror Operators Scale",
        description="Modal Mirror Operators Scale",
        default=5, min=0.1, max=100
        )

    Hops_mirror_modal_sides_scale: FloatProperty(
        name="Modal Mirror Operators Sides Scale",
        description="Modal Mirror Operators Sides Scale",
        default=0.20, min=0.01, max=0.99)

    Hops_modal_scale: FloatProperty(
        name="Modal Operators Scale",
        description="Modal Operators Scale",
        default=1, min=0.001, max=100)

    Hops_modal_percent_scale: FloatProperty(
        name="Modal Operators Scale",
        description="Modal Operators Scale",
        default=1, min=0.001, max=100)

    # edit mode properties
    Hops_circle_size: FloatProperty(
        name="Bevel offset step",
        description="Bevel offset step",
        default=0.0001, min=0.0001)

    Hops_gizmo_mirror_on: BoolProperty(
        name="Display Mirror Gizmo",
        default=True,
        description="Display Mirror Gizmo")

    Hops_gizmo_mirror: BoolProperty(
        name="Display Mirror Gizmo",
        default=False,
        description="Display Mirror Gizmo")

    Hops_gizmo_qarray: BoolProperty(
        name="Display Array Gizmo",
        default=False,
        description="Display Array Gizmo")

    # menu
    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        row = col.row()
        row.prop(self, "tab", expand=True)

        box = col.box()

        if self.tab == "UI":
            self.draw_ui_tab(box)
        elif self.tab == "ADDONS":
            self.draw_addons_tab(box)
        elif self.tab == "DRAWING":
            self.draw_drawing_tab(box)
        elif self.tab == "INFO":
            self.draw_info_tab(box)
        elif self.tab == "LINKS":
            self.draw_links_tab(box)
        elif self.tab == "KEYMAP":
            self.draw_keymap_tab(box)

    def draw_drawing_tab(self, layout):
        box = layout.box()

        row = box.row(align=True)
        row.prop(self, "enable_tool_overlays")

        box = layout.box()
        row = box.row(align=True)
        row.operator("hops.color_to_default", text='Hard Ops')
        row.operator("hops.color_to_theme", text='AR')
        row.operator("hops.color_to_theme2", text='ThemeGrabber')

        box = layout.box()
        row = box.row(align=True)
        row.prop(self, "Hops_text_color", text="Main Text Color ")

        row = box.row(align=True)
        row.prop(self, "Hops_text2_color", text="Secoundary Text Color ")

        row = box.row(align=True)
        row.prop(self, "Hops_border_color", text="Border Color")

        row = box.row(align=True)
        row.prop(self, "Hops_border2_color", text="Secondary Border Color")

        box = layout.box()

        if self.pro_mode:
            if self.extra_options:
                row = box.row(align=True)
                row.prop(self, "Hops_display_logo", text="Display Logo")

        row = box.row(align=True)
        row.prop(self, "Hops_logo_color", text="Logo Color")
        row = box.row(align=True)
        row.prop(self, "Hops_logo_color_csharp", text="Csharp Color")
        row = box.row(align=True)
        row.prop(self, "Hops_logo_color_cstep", text="Cstep Color")
        row = box.row(align=True)
        row.prop(self, "Hops_logo_color_boolshape", text="Boolshape Color")
        row = box.row(align=True)
        row.prop(self, "Hops_logo_color_boolshape2", text="Boolshape2 Color")

        row = box.row(align=True)
        row.prop(self, "Hops_logo_size", text="Logo Size")
        row.prop(self, "Hops_logo_x_position", text="Logo X Position")
        row.prop(self, "Hops_logo_y_position", text="Logo Y Position")

        box = layout.box()
        row = box.row(align=True)
        row.prop(self, "Hops_display_text_status", text="Display Text Status")
        row.prop(self, "Hops_display_undefined_status", text="Display Undefined Status")
        row = box.row(align=True)
        row.prop(self, "Hops_hud_text_color", text="Hud Text Color")

        box = layout.box()
        row = box.row(align=True)
        row.prop(self, "display_time", text="HUD Display Time (seconds)")

        row = box.row(align=True)
        row.prop(self, "fadeout_time", text="HUD Fadeout Time (seconds)")

        box = layout.box()
        row = box.row(align=True)
        row.prop(self, "Hops_mirror_modal_scale", text="modal mirror scale")

        row = box.row(align=True)
        row.prop(self, "Hops_mirror_modal_sides_scale", text="modal mirror sides scale")

    def draw_ui_tab(self, layout):
        # layout.prop(self, "toolbar_category_name")
        row = layout.row()
        row.prop(self, "Hops_modal_scale")

        row = layout.row()

        row.prop(self, "pro_mode")

        row = layout.row()

        row.prop(self, "extra_options", text="Extra Options")

        if pro_mode_enabled():
            if addon_exists("MESHmachine"):
                row = layout.row()
                row.label(text="Mir2 Symmetrize type:")
                row.prop(self, "Hops_Mir2_symmetrize_type", expand=True)

        row = layout.row()

        if self.extra_options:
            row = layout.row()
            row.prop(self, "pie_F6", text="Pie: F6 Option At Top")

            row = layout.row()
            row.prop(self, "pie_bool_options", text="Pie: Add Boolean Options")

        row = layout.row()

        if self.extra_options:
            row = layout.row()
            row.label(text="Dev Options")
            row = layout.row()
            row.prop(self, "experimental_ssharp", text="Use experimental ssharp")

        if addon_exists("asset_management"):
            row = layout.row()
            row.label(text="Asset Manager Expansion:")
            row.prop(self, "Asset_Manager_Preview", text="Asset Manager: Add To HOps")

        if addon_exists("mira_tools"):
            row = layout.row()
            row.label(text="Mira Tools Expansion:")
            row.prop(self, "mira_handler_enabled", text="Mira Tools: Enable Hops Handler")

    def draw_info_tab(self, layout):
        write_text(layout, info_text, width=bpy.context.region.width / get_dpi_factor() / 8)

    def draw_keymap_tab(self, layout):
        box = layout.box()
        split = box.split()
        col = split.column()
        col.label(text='Do not remove hotkeys, disable them instead.')
        col.separator()
        col.label(text='Hotkeys')

        col.separator()

        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user

        col.label(text='menus:')

        col.separator()
        km = kc.keymaps['3D View']
        kmi = get_hotkey_entry_item(km, 'wm.call_menu_pie', 'hops_main_pie', 'name')
        if kmi:
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text="No hotkey entry found")
            col.label(text="restore hotkeys from interface tab")

        col.separator()
        km = kc.keymaps['3D View']
        kmi = get_hotkey_entry_item(km, 'wm.call_menu', 'hops_main_menu', 'name')
        if kmi:
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text="No hotkey entry found")
            col.label(text="restore hotkeys from interface tab")

        col.separator()
        km = kc.keymaps['3D View']
        kmi = get_hotkey_entry_item(km, 'view3d.hops_helper_popup', 'MODIFIERS', 'tab')
        if kmi:
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text="No hotkey entry found")
            col.label(text="restore hotkeys from interface tab")

        col.separator()
        km = kc.keymaps['3D View']
        kmi = get_hotkey_entry_item(km, 'wm.call_menu', 'hops.material_list_menu', 'name')
        if kmi:
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text="No hotkey entry found")
            col.label(text="restore hotkeys from interface tab")

        col.separator()
        km = kc.keymaps['3D View']
        kmi = get_hotkey_entry_item(km, 'wm.call_menu', 'hops.vieport_submenu', 'name')
        if kmi:
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text="No hotkey entry found")
            col.label(text="restore hotkeys from interface tab")

        col.separator()
        col.label(text='operators:')

        col.separator()
        km = kc.keymaps['3D View']
        kmi = get_hotkey_entry_item(km, 'hops.mirror_gizmo', 'none', 'none')
        if kmi:
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text="No hotkey entry found")
            col.label(text="restore hotkeys from interface tab")

        col.separator()
        km = kc.keymaps['3D View']
        kmi = get_hotkey_entry_item(km, 'hops.mirror_mirror_x', 'none', 'none')
        if kmi:
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text="No hotkey entry found")
            col.label(text="restore hotkeys from interface tab")

        col.separator()
        km = kc.keymaps['3D View']
        kmi = get_hotkey_entry_item(km, 'hops.mirror_mirror_y', 'none', 'none')
        if kmi:
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text="No hotkey entry found")
            col.label(text="restore hotkeys from interface tab")

        col.separator()
        km = kc.keymaps['3D View']
        kmi = get_hotkey_entry_item(km, 'hops.mirror_mirror_z', 'none', 'none')
        if kmi:
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text="No hotkey entry found")
            col.label(text="restore hotkeys from interface tab")

        col.separator()
        col.label(text='booleans:')
        col.separator()
        km = kc.keymaps['Object Mode']
        kmi = get_hotkey_entry_item(km, 'hops.bool_union', 'none', 'none')
        if kmi:
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text="No hotkey entry found")
            col.label(text="restore hotkeys from interface tab")

        col.separator()
        km = kc.keymaps['Object Mode']
        kmi = get_hotkey_entry_item(km, 'hops.bool_difference', 'none', 'none')
        if kmi:
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text="No hotkey entry found")
            col.label(text="restore hotkeys from interface tab")

        col.separator()
        km = kc.keymaps['Object Mode']
        kmi = get_hotkey_entry_item(km, 'hops.slash', 'none', 'none')
        if kmi:
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text="No hotkey entry found")
            col.label(text="restore hotkeys from interface tab")

        col.separator()
        km = kc.keymaps['Mesh']
        kmi = get_hotkey_entry_item(km, 'hops.edit_bool_union', 'none', 'none')
        if kmi:
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text="No hotkey entry found")
            col.label(text="restore hotkeys from interface tab")

        col.separator()
        km = kc.keymaps['Mesh']
        kmi = get_hotkey_entry_item(km, 'hops.edit_bool_difference', 'none', 'none')
        if kmi:
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text="No hotkey entry found")
            col.label(text="restore hotkeys from interface tab")

    def draw_links_tab(self, layout):
        col = layout.column()
        for name, url in weblinks:
            col.operator("wm.url_open", text=name).url = url

    def draw_addons_tab(self, layout):
        draw_addon_diagnostics(layout, columns=4)


info_text = """HardOps is a toolset to maximize hard surface efficiency. This tool began back in
2015 and still continues. Thanks to everyone's continued support and usage the tool continues to live. 2.8 might start off rocky but we plan to continue the same plan of creating the best out of box modelling experience for users possible. As Blender improves so will we. I thank you all for even making it as far as this text. The legend of Hard Ops continue. With the same teams and same service. Cheers and heres to another round of Blending! 

License Code: 29468741xxxx4x5  haha just kidding! This.... is... Blender!
""".replace("\n", " ")

weblinks = [
    ("Documentation",           "http://hardops-manual.readthedocs.io/en/latest/"),
    ("Youtube",                 "https://www.youtube.com/user/masterxeon1001/"),
    ("Gumroad",                 "https://gumroad.com/l/hardops/"),
    ("Hard Ops 9 Videos",       "https://www.youtube.com/playlist?list=PL0RqAjByAphEUuI2JDxIjjCQtfTRQlRh0"),
    ("Hard Ops 8 Videos",       "https://www.youtube.com/playlist?list=PL0RqAjByAphGEVeGn9QdPdjk3BLJXu0ho"),
    ("Version 9 Notes",         "https://masterxeon1001.com/2018/06/04/boxcutter-6-8-8-ghostscythe/"),
    ("Version 8 Notes",         "https://masterxeon1001.com/2017/02/10/hard-ops-0087-hassium-update/")
]
