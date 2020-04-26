import bpy

class ElaraLightPanel(bpy.types.Panel):
    bl_label = "Lamp"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    COMPAT_ENGINES = {'elara_renderer'}
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        lamp = context.lamp
        return (lamp and (lamp.type == 'AREA' or lamp.type == 'POINT'))

    def draw(self, context):
        layout = self.layout
        lamp = context.lamp
        layout.prop(lamp, "color")
        layout.prop(lamp, "energy")

        if lamp.type == 'AREA':
            col = layout.column()
            col.row().prop(lamp, "shape", expand=True)
            sub = col.row(align=True)

            if lamp.shape == 'SQUARE':
                sub.prop(lamp, "size")
            elif lamp.shape == 'RECTANGLE':
                sub.prop(lamp, "size", text="Size X")
                sub.prop(lamp, "size_y", text="Size Y")

def register():
    bpy.utils.register_class(ElaraLightPanel)

def unregister():
    bpy.utils.unregister_class(ElaraLightPanel)