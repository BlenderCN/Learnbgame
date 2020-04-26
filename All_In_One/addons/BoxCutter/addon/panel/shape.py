import bpy

from bpy.types import Panel

from .. utility import addon, active_tool, names, vertice_presets, angle_presets


class BC_PT_shape(Panel):
    bl_label = 'Shape'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BoxCutter'

    @classmethod
    def poll(cls, context):
        return active_tool().idname == 'BoxCutter'

    def draw(self, context):
        preference = addon.preference()

        layout = self.layout
        bc = context.window_manager.bc

        option = None
        for tool in context.workspace.tools:
            if tool.idname == 'BoxCutter' and tool.mode == context.workspace.tools_mode:
                option = tool.operator_properties('bc.draw_shape')

                column = layout.column()

                row = column.row()
                row.scale_x = 2.0
                row.scale_y = 1.5

                sub = row.row()
                sub.enabled = not bc.running
                sub.prop(option, 'shape_type', expand=True, text='')

                sub = row.row()
                sub.enabled = option.shape_type != 'NGON'
                sub.prop(option, 'origin', expand=True, text='')

                if option.shape_type == 'CIRCLE':
                    self.label_row(layout.row(), preference.shape, 'circle_vertices', label='Vertices')

                elif option.shape_type == 'NGON':
                    self.label_row(layout.row(), preference.behavior, 'ngon_snap_angle', label='Snap Angle')

                elif option.shape_type == 'CUSTOM':
                    self.label_row(layout.row(), bc, 'collection', label='Collection')

                    if not bc.collection:
                        self.label_row(layout.row(), bc, 'shape', label='Shape')

                    else:
                        row = layout.row()
                        split = row.split(factor=0.5)
                        split.label(text='Shape')
                        split.prop_search(bc, 'shape', bc.collection, 'objects', text='')


    def label_row(self, row, path, prop, label=''):
        if prop in {'circle_vertices', 'ngon_snap_angle'}:
            column = self.layout.column(align=True)
            row = column.row(align=True)

        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')

        values = {
            'Vertices': vertice_presets,
            'Snap Angle': angle_presets}

        if prop in {'circle_vertices', 'ngon_snap_angle'}:
            row = column.row(align=True)
            split = row.split(factor=0.48, align=True)
            sub = split.row(align=True)
            sub = split.row(align=True)

            pointer = '.' if prop == 'ngon_snap_angle' else '.shape.'
            for value in values[label]:
                ot = sub.operator('wm.context_set_int', text=str(value))
                ot.data_path = F'preferences.addons[\"{__name__.partition(".")[0]}\"].preferences{pointer}{prop}'
                ot.value = value
