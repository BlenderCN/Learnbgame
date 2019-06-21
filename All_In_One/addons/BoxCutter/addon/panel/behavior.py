import bpy

from bpy.types import Panel

from .. keymap import keys
from .. utility import addon, names, vertice_presets, array_presets, width_presets, segment_presets, angle_presets


class BC_PT_behavior(Panel):
    bl_label = 'Behavior'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BoxCutter'


    def draw(self, context):
        layout = self.layout
        preference = addon.preference()
        bc = context.window_manager.bc

        option = None
        for tool in context.workspace.tools:
            if tool.idname == 'BoxCutter' and tool.mode == context.workspace.tools_mode:
                option = tool.operator_properties('bc.draw_shape')

                row = layout.row(align=True)
                row.scale_x = 2
                row.scale_y = 1.5
                row.prop(option, 'mode', text='', expand=True)

                row = layout.row()
                row.scale_x = 2
                row.scale_y = 1.25

                sub = row.row()
                sub.enabled = not bc.running
                sub.prop(option, 'shape_type', expand=True, text='')

                sub = row.row()
                sub.enabled = option.shape_type != 'NGON'
                sub.prop(option, 'origin', expand=True, text='')

                layout.separator()

                if self.is_popover:
                    snap = layout.row(align=True)
                    snap.scale_x = 1.5
                    snap.scale_y = 1.5
                    row = snap.row(align=True)
                    row.prop(preference.behavior, 'snap', text='', icon='SNAP_OFF' if not preference.behavior.snap else 'SNAP_ON')

                    sub = row.row(align=True)
                    sub.active = preference.behavior.snap
                    sub.prop(preference.behavior, 'snap_increment', text='', icon='SNAP_INCREMENT')

                    if preference.behavior.snap_increment:
                        sub.prop(preference.behavior, 'increment_amount', text='')
                        sub.prop(preference.behavior, 'increment_lock', text='', icon=F'{"" if preference.behavior.increment_lock else "UN"}LOCKED')

                        row = layout.row(align=True)
                        row.alignment = 'RIGHT'
                        row.scale_x = 1.22
                        row.scale_y = 1.5
                        row.active = preference.behavior.snap

                        row.prop(preference.behavior, 'snap_grid', text='', icon='SNAP_GRID')
                        row.prop(preference.behavior, 'snap_vert', text='', icon='VERTEXSEL')
                        row.prop(preference.behavior, 'snap_edge', text='', icon='EDGESEL')
                        row.prop(preference.behavior, 'snap_face', text='', icon='FACESEL')

                    else:

                        for _ in range(6):
                            sub.separator()

                        sub.prop(preference.behavior, 'snap_grid', text='', icon='SNAP_GRID')
                        sub.prop(preference.behavior, 'snap_vert', text='', icon='VERTEXSEL')
                        sub.prop(preference.behavior, 'snap_edge', text='', icon='EDGESEL')
                        sub.prop(preference.behavior, 'snap_face', text='', icon='FACESEL')

                if option.mode == 'INSET':
                    layout.row().label(text='\u2022 Inset')
                    self.label_row(layout.row(align=True), preference.shape, 'inset_thickness', label='Thickness')

                if option.shape_type == 'NGON':
                    layout.row().label(text='\u2022 Ngon')
                    self.label_row(layout.row(align=True), preference.behavior, 'ngon_snap_angle', label='Snap Angle')

                elif option.shape_type == 'CIRCLE':
                    layout.row().label(text='\u2022 Circle')
                    self.label_row(layout.row(align=True), preference.shape, 'circle_vertices', label='Vertices')

                elif option.shape_type == 'CUSTOM':
                    layout.row().label(text='\u2022 Custom')
                    self.label_row(layout.row(align=True), bc, 'collection', label='Collection')

                    if not bc.collection:
                        self.label_row(layout.row(align=True), bc, 'shape', label='Shape')

                    else:
                        row = layout.row(align=True)
                        split = row.split(factor=0.5)
                        split.label(text='Shape')
                        split.prop_search(bc, 'shape', bc.collection, 'objects', text='')

                if bc.shape:
                    if bc.shape.bc.array:
                        layout.row().label(text='\u2022 Array')
                        self.label_row(layout.row(align=True), preference.shape, 'array_count', label='Count')

                    if bc.shape.bc.solidify:
                        layout.row().label(text='\u2022 Solidify')
                        self.label_row(layout.row(align=True), preference.shape, 'solidify_thickness', label='Thickness')

                    if bc.shape.bc.bevel:
                        layout.row().label(text='\u2022 Bevel')
                        self.label_row(layout.row(align=True), preference.shape, 'bevel_width', label='Width')
                        self.label_row(layout.row(align=True), preference.shape, 'bevel_segments', label='Segments')

                elif bc.start_operation == 'ARRAY':
                    layout.row().label(text='\u2022 Array')
                    self.label_row(layout.row(align=True), preference.shape, 'array_count', label='Count')

                elif bc.start_operation == 'SOLIDIFY':
                    layout.row().label(text='\u2022 Solidify')
                    self.label_row(layout.row(align=True), preference.shape, 'solidify_thickness', label='Thickness')

                elif bc.start_operation == 'BEVEL':
                    self.label_row(layout.row(align=True), preference.shape, 'bevel_width', label='Width')
                    self.label_row(layout.row(align=True), preference.shape, 'bevel_segments', label='Segments')

        if not option:
            hotkey = [kmi[1] for kmi in keys if kmi[1].idname == 'bc.topbar_activate'][0]

            shift = 'Shift' if hotkey.shift else ''
            ctrl = 'Ctrl' if hotkey.ctrl else ''
            alt = 'Alt' if hotkey.alt else ''
            cmd = 'Cmd+' if hotkey.oskey else '+'

            shift += '+' if hotkey.ctrl and hotkey.shift else ''
            ctrl += '+' if hotkey.alt and hotkey.ctrl else ''
            alt += '+' if hotkey.oskey and hotkey.alt else ''

            key = hotkey.type

            layout.label(text=F'Activate BoxCutter')
            layout.label(text=F'\u2022 {shift+ctrl+alt+cmd+key}')


    def label_row(self, row, path, prop, label=''):
        if prop in {'circle_vertices', 'ngon_snap_angle', 'array_count', 'bevel_width', 'bevel_segments'}:
            column = self.layout.column(align=True)
            row = column.row(align=True)

        row.label(text=label if label else names[prop])
        row.prop(path, prop, text='')

        values = {
            'Vertices': vertice_presets,
            'Count': array_presets,
            'Width': width_presets,
            'Segments': segment_presets,
            'Snap Angle': angle_presets}

        if prop in {'circle_vertices', 'ngon_snap_angle', 'array_count', 'bevel_width', 'bevel_segments'}:
            row = column.row(align=True)
            split = row.split(factor=0.48, align=True)
            sub = split.row(align=True)
            sub = split.row(align=True)

            pointer = '.' if prop == 'ngon_snap_angle' else '.shape.'
            for value in values[label]:
                ot = sub.operator(F'wm.context_set_{"int" if prop != "bevel_width" else "float"}', text=str(value))
                ot.data_path = F'preferences.addons["{__name__.partition(".")[0]}"].preferences{pointer}{prop}'
                ot.value = value

            column.separator()
