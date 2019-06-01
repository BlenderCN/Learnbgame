import bpy
from ..common import *

class MenuAnimModes(bpy.types.Menu):
    bl_idname = "texanim.modemenu"
    bl_label = "Animation Mode"

    def draw(self, context):
        layout = self.layout

        layout.operator("texanim.transform", icon="ARROW_LEFTRIGHT")
        layout.operator("texanim.grid", icon="MESH_GRID")


class RevoltAnimationPanel(bpy.types.Panel):
    bl_label = "Texture Animation (.w)"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "mesh_edit"
    bl_category = "Re-Volt"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(self, context):
        # Only shows up in NPC mode
        props = context.scene.revolt
        return props.face_edit_mode == "prm"

    def draw_header(self, context):
        self.layout.label("", icon="CAMERA_DATA")

    def draw(self, context):
        obj = context.object
        props = context.scene.revolt

        # Total slots
        row = self.layout.row(align=True)
        row.prop(props, "ta_max_slots", text="Total Slots")

        # Current slot
        row = self.layout.row(align=True)
        row.active = (props.ta_max_slots > 0)
        column = row.column(align=True)
        column.label("Animation Slot:")
        column.prop(props, "ta_current_slot", text="Slot")
        column.prop(props, "ta_max_frames")

        # Current frame
        framecol = self.layout.column(align=True)
        framecol.active = (props.ta_max_slots > 0)
        framecol.label("Animation Frame:")
        framecol.prop(props, "ta_current_frame")

        # Texture animation preview
        row = framecol.row(align=True)
        row.active = (props.ta_max_slots > 0)
        column = row.column(align=True)
        column.scale_x = 2.4
        column.operator("texanim.prev_prev", text="", icon="FRAME_PREV")
        column = row.column(align=True)
        column.operator("texanim.copy_frame_to_uv", text="Preview", icon="VIEWZOOM")
        column = row.column(align=True)
        column.scale_x = 2.4
        column.operator("texanim.prev_next", text="", icon="FRAME_NEXT")

        row = framecol.row(align=True)
        row.prop(props, "ta_current_frame_tex", icon="TEXTURE")
        row.prop(props, "ta_current_frame_delay", icon="PREVIEW_RANGE")

        # Texture animation operators
        row = self.layout.row()
        row.active = (props.ta_max_slots > 0)
        row.menu("texanim.modemenu", text="Animate...", icon="ANIM")


        # UV Coords
        row = self.layout.row()
        row.active = (props.ta_max_slots > 0)
        row.label("UV Coordinates:")

        row = self.layout.row(align=True)
        row.active = (props.ta_max_slots > 0)
        row.operator("texanim.copy_uv_to_frame", icon="COPYDOWN")

        row = self.layout.row()
        row.active = (props.ta_max_slots > 0)
        column = row.column()
        column.prop(props, "ta_current_frame_uv0")
        column.prop(props, "ta_current_frame_uv1")

        column = row.column()
        column.prop(props, "ta_current_frame_uv2")
        column.prop(props, "ta_current_frame_uv3")

