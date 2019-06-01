import bpy


class BarnDoors(bpy.types.Panel):
    bl_idname = "panel.BarnDoors"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_label = "Barndoors"
    bl_options = {'DEFAULT_CLOSED'}

    use_bd = bpy.props.BoolProperty(name="Use Barndoors", default=False)

    @classmethod
    def poll(cls, context):
        lamp = context.lamp
        return (lamp and lamp.type == 'SPOT')

    def draw_header(self, context):
        lamp = context.lamp
        self.layout.prop(lamp, "use_bd", text="")

    def draw(self, context):
        layout = self.layout
        ob = context.object
        col = layout.column()
        split = layout.split()

        col.label(text="Barndoors:")

        col = split.column(align=True)
        col.label(text="Right Panel:")
        col.label(text="Bottom Panel:")
        col.label(text="Left Panel:")
        col.label(text="Top Panel:")

        col = split.column(align=True)
        col.prop(ob, "rotation_euler", text="Angle")
        col.prop(ob, "rotation_euler", text="Angle")
        col.prop(ob, "rotation_euler", text="Angle")
        col.prop(ob, "rotation_euler", text="Angle")


class Cookie(bpy.types.Panel):

    bl_idname = "panel.Cookie"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_label = "Cookie"
    bl_options = {'DEFAULT_CLOSED'}

    use_ck = bpy.props.BoolProperty(name="Use Cookie", default=False)

    @classmethod
    def poll(cls, context):
        return context.lamp

    def draw_header(self, context):
        lamp = context.lamp
        self.layout.prop(lamp, "use_ck", text="")

    def draw(self, context):
        layout = self.layout


class SelectResetView(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_label = "Look Through Selected"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        lamp = context.lamp
        return (lamp)

    def draw(self, context):
        layout = self.layout

        row = layout.row()

        row.operator("view3d.object_as_camera", text='Look Through Selected')
        row.operator("reset.camera_as_active", text='Reset Camera')
