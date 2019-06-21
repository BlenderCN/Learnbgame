import bpy

from bpy.types import Panel

from .. utility import addon, active_tool


class BC_PT_snap(Panel):
    bl_label = 'Snap'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BoxCutter'

    @classmethod
    def poll(cls, context):
        return active_tool().idname == 'BoxCutter'

    def draw(self, context):
        layout = self.layout
        preference = addon.preference()
        bc = context.window_manager.bc

        snap = layout.row(align=True)
        snap.scale_x = 1.5
        snap.scale_y = 1.5
        row = snap.row(align=True)
        row.active = preference.behavior.snap
        row.prop(preference.behavior, 'snap_increment', text='', icon='SNAP_INCREMENT')

        sub = row.row(align=True)
        if preference.behavior.snap_increment:
            sub.prop(preference.behavior, 'increment_amount', text='')
            sub.prop(preference.behavior, 'increment_lock', text='', icon=F'{"" if preference.behavior.increment_lock else "UN"}LOCKED')

            row = layout.row(align=True)
            row.alignment = 'RIGHT'
            row.scale_x = 1.22
            row.scale_y = 1.5
            row.active = preference.behavior.snap

            row.prop(preference.keymap, 'alt_draw', text='', icon='EVENT_ALT')
            row.prop(preference.keymap, 'shift_draw', text='', icon='EVENT_SHIFT')

            row.separator()

            sub.prop(preference.behavior, 'snap_grid', text='', icon='SNAP_GRID')
            row.prop(preference.behavior, 'snap_vert', text='', icon='VERTEXSEL')
            row.prop(preference.behavior, 'snap_edge', text='', icon='EDGESEL')
            row.prop(preference.behavior, 'snap_face', text='', icon='FACESEL')

        else:

            sub.separator()
            sub.separator()

            sub.prop(preference.keymap, 'alt_draw', text='', icon='EVENT_ALT')
            sub.prop(preference.keymap, 'shift_draw', text='', icon='EVENT_SHIFT')

            sub.separator()

            sub.prop(preference.behavior, 'snap_grid', text='', icon='SNAP_GRID')
            sub.prop(preference.behavior, 'snap_vert', text='', icon='VERTEXSEL')
            sub.prop(preference.behavior, 'snap_edge', text='', icon='EDGESEL')
            sub.prop(preference.behavior, 'snap_face', text='', icon='FACESEL')
