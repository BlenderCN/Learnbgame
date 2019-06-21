import bpy

from bpy.types import Panel

from .. utility import addon, active_tool


class BC_PT_surface(Panel):
    bl_label = 'Surface'
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

        option = None
        for tool in context.workspace.tools:
            if tool.idname == 'BoxCutter' and tool.mode == context.workspace.tools_mode:
                option = tool.operator_properties('bc.draw_shape')

        row = layout.row(align=True)
        row.scale_x = 1.5
        row.scale_y = 1.5
        if not self.is_popover:
            flow = row.column()
            row = flow.row()
        row.prop(preference, 'surface', expand=True, icon_only=not self.is_popover)

        if preference.surface == 'OBJECT':
            row = layout.row(align=True)
            row.scale_y = 1.25
            row.prop(option, 'align_to_view', icon='VIEW_ORTHO' if option.align_to_view else 'VIEW_PERSPECTIVE')

        else:
            row = layout.row(align=True)
            row.scale_y = 1.25
            row.prop(preference, 'cursor_axis', expand=True)

        row = layout.row(align=True)
        row.scale_x = 1.25
        row.scale_y = 1.25
        row.label(text='Gizmo')
        if preference.cursor:
            row.operator('bc.remove_cursor', text='', icon='CANCEL')
        else:
            row.operator('bc.add_cursor', text='', icon='PIVOT_CURSOR')

        if preference.transform_gizmo:
            row.operator('bc.remove_transform', text='', icon='CANCEL')
        else:
            row.operator('bc.add_transform', text='', icon='ORIENTATION_GLOBAL')
