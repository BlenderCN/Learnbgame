import bpy
import math
from .addon import ADDON_ID, prefs
from .hotkeys import hotkeys, Hotkey
from .overlay import Overlay
from .uv_align_by_edge import *
from .uv_rotate import *
from .uv_snap import *
from .ui_pie_menus import *


class RL_Preferences(bpy.types.AddonPreferences):
    bl_idname = ADDON_ID

    def update_hotkeys(self, context):
        pr = prefs()
        for kmi in hotkeys.keymap_items():
            if kmi.idname == SUV_OT_uv_align_by_edge.bl_idname:
                kmi.active = pr.uv_align
            elif kmi.idname == SUV_OT_uv_snap.bl_idname:
                kmi.active = pr.uv_snap
            elif kmi.idname == SUV_OT_uv_rotate.bl_idname:
                kmi.active = pr.uv_rotate

    overlay = bpy.props.PointerProperty(type=Overlay)
    uv_align = bpy.props.BoolProperty(
        name="Align Island by Edge",
        description=(
            "This script allows you to align and rotate an island "
            "based on an edge selection.\n"
            "Just select an edge press shift "
            "and scroll your middle mouse wheel."),
        update=update_hotkeys)
    rotate_again = bpy.props.BoolProperty(
        name="Rotate UVs again",
        description="Rotate UVs 90 degrees each time you click align")
    uv_snap = bpy.props.BoolProperty(
        name="Snap UV",
        description=(
            "This script will snap your current selection "
            "to the closest unselected ones.\n"
            "Pressing down ctrl and scroll your mouse wheel "
            "to increase/decrease the value."),
        update=update_hotkeys)
    uv_snap_default = bpy.props.FloatProperty(
        name="Defalut Threshold",
        description="Default threshold for Snap UV tool",
        default=0.05)
    uv_snap_step = bpy.props.FloatProperty(
        name="Threshold Step", description="Threshold step for Snap UV tool",
        default=0.05)
    uv_rotate = bpy.props.BoolProperty(
        name="Rotate UV Islands",
        description=(
            "This script allows you to rotate UV islands CW & CCW "
            "by pressing down shift and scrolling your mouse wheel."),
        update=update_hotkeys)
    uv_rotate_step = bpy.props.FloatProperty(
        name="Rotation Step", description="Rotation step",
        default=math.pi / 4, subtype='ANGLE')

    use_uv_bounds = bpy.props.BoolProperty(
        name="Use Bounds", description="Use bounds")

    hk_small_pie = bpy.props.PointerProperty(type=Hotkey)
    hk_big_pie = bpy.props.PointerProperty(type=Hotkey)

    def draw(self, context):
        layout = self.layout
        row = layout.split(0.5)
        row.prop(self, "uv_snap")
        if self.uv_snap:
            row = row.row(True)
            row.prop(self, "uv_snap_default")
            row.prop(self, "uv_snap_step")

        row = layout.row()
        row.prop(self, "uv_rotate")
        if self.uv_rotate:
            row.prop(self, "uv_rotate_step")

        row = layout.row()
        row.prop(self, "uv_align")
        if self.uv_align:
            row.prop(self, "rotate_again")
        self.overlay.draw(layout)

        row = layout.row()
        self.hk_small_pie.draw(row, context, label="Small Pie Menu:")
        self.hk_big_pie.draw(row, context, label="Big Pie Menu:")


def register():
    hotkeys.keymap("UV Editor")
    hotkeys.add(
        SUV_OT_uv_align_by_edge.bl_idname, 'WHEELUPMOUSE', shift=True,
        delta=1)
    hotkeys.add(
        SUV_OT_uv_align_by_edge.bl_idname, 'WHEELDOWNMOUSE', shift=True,
        delta=-1)

    hotkeys.add(
        SUV_OT_uv_rotate.bl_idname, 'WHEELUPMOUSE', shift=True,
        delta=1)
    hotkeys.add(
        SUV_OT_uv_rotate.bl_idname, 'WHEELDOWNMOUSE', shift=True,
        delta=-1)

    hotkeys.add(
        SUV_OT_uv_snap.bl_idname, 'WHEELUPMOUSE', ctrl=True,
        delta=1)
    hotkeys.add(
        SUV_OT_uv_snap.bl_idname, 'WHEELDOWNMOUSE', ctrl=True,
        delta=-1)

    hk = prefs().hk_small_pie
    if hk.key == 'NONE':
        hk.key = 'SELECTMOUSE'
        hk.value = 'PRESS'
    hotkeys.add("wm.call_menu_pie", name="SUV_MT_small_pie", hotkey=hk)

    hk = prefs().hk_big_pie
    if hk.key == 'NONE':
        hk.key = 'SELECTMOUSE'
        hk.ctrl = True
        hk.value = 'PRESS'
    hotkeys.add("wm.call_menu_pie", name="SUV_MT_big_pie", hotkey=hk)

    prefs().update_hotkeys(bpy.context)


def unregister():
    pass

