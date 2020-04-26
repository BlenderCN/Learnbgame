import bpy

from bpy.types import Panel

from .. utility import addon, active_tool, names, array_presets, width_presets, segment_presets


class BC_PT_operation(Panel):
    bl_label = 'Operations'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BoxCutter'


    @classmethod
    def poll(cls, context):
        return active_tool().idname == 'BoxCutter'


    def draw(self, context):
        preference = addon.preference()
        bc = context.window_manager.bc

        layout = self.layout

        option = None
        for tool in context.workspace.tools:
            if tool.idname == 'BoxCutter' and tool.mode == context.workspace.tools_mode:
                option = tool.operator_properties('bc.draw_shape')

                column = layout.column()
                column.scale_x = 1.5
                column.scale_y = 1.5

                row = column.row(align=True)

                if self.is_popover:
                    row.prop(option, 'operation', expand=True)
                else:
                    row.prop(bc, 'start_operation', expand=True, icon_only=True)
                    row.prop(option, 'operation', text='', icon_only=True)

                if option.operation == 'ARRAY':
                    self.label_row(layout.row(align=True), preference.shape, 'array_count', label='Count')

                elif option.operation == 'BEVEL':
                    self.label_row(layout.row(align=True), preference.shape, 'bevel_width', label='Width')
                    self.label_row(layout.row(align=True), preference.shape, 'bevel_segments', label='Segments')
                    self.label_row(layout.row(align=True), preference.shape, 'quad_bevel')
                    if preference.shape.quad_bevel:
                        self.label_row(layout.row(align=True), preference.shape, 'straight_edges')

                elif option.operation == 'SOLIDIFY':
                    self.label_row(layout.row(align=True), preference.shape, 'solidify_thickness', label='Thickness')

                break


    def label_row(self, row, path, prop, label=''):
        if prop in {'array_count', 'bevel_width', 'bevel_segments'}:
            column = self.layout.column(align=True)
            row = column.row(align=True)
        else:
            row.scale_x = 1.2

        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')

        values = {
            'Count': array_presets,
            'Width': width_presets,
            'Segments': segment_presets}

        if prop in {'array_count', 'bevel_width', 'bevel_segments'}:
            row = column.row(align=True)
            split = row.split(factor=0.48, align=True)
            sub = split.row(align=True)
            sub = split.row(align=True)

            for value in values[label]:
                ot = sub.operator(F'wm.context_set_{"int" if prop != "bevel_width" else "float"}', text=str(value))
                ot.data_path = F'preferences.addons["{__name__.partition(".")[0]}"].preferences.shape.{prop}'
                ot.value = value

            column.separator()
