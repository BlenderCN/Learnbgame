import bpy


from bl_ui.properties_data_lamp import DataButtonsPanel
from .properties_material import color_template


from bl_ui import properties_data_lamp
properties_data_lamp.DATA_PT_preview.COMPAT_ENGINES.add('PEARRAY_RENDER')
del properties_data_lamp


class DATA_PT_pr_lamp(DataButtonsPanel, bpy.types.Panel):
    bl_label = "Lamp"
    COMPAT_ENGINES = {'PEARRAY_RENDER'}

    def draw(self, context):
        layout = self.layout

        lamp = context.lamp

        layout.prop(lamp, "type", expand=True)
        if lamp.type == 'SPOT':
            layout.label('Spot light will be converted to point light!', icon='INFO')
        elif lamp.type == 'HEMI':
            layout.label('Hemi light will be converted to area light!', icon='INFO')

        split = layout.split()

        col = split.column(align=True)
        col.separator()
        color_template(lamp, col, "color")

        if lamp.type == 'POINT' or lamp.type == 'SPOT':
            col.separator()
            col.prop(lamp.pearray, 'point_radius')
        elif lamp.type == 'HEMI' or lamp.type == 'AREA':
            col.separator()
            col2 = col.column(align=True)
            col2.row().prop(lamp, "shape", expand=True)
            sub = col2.row(align=True)

            if lamp.shape == 'SQUARE':
                sub.prop(lamp, "size")
            elif lamp.shape == 'RECTANGLE':
                sub.prop(lamp, "size", text="Size X")
                sub.prop(lamp, "size_y", text="Size Y")
    
        if lamp.type == 'POINT' or lamp.type == 'SPOT' or lamp.type == 'HEMI' or lamp.type == 'AREA':
            col.separator()
            col.prop(lamp.pearray, 'camera_visible')