import bpy
from bpy.props import EnumProperty, BoolProperty

origin = [
    ("ACTIVE", "Active Object", ""),
    ("CENTER", "Center", "")]


class HOPS_OT_ResetAxis(bpy.types.Operator):
    bl_idname = "hops.reset_axis"
    bl_label = "Hops Reset Axis"
    bl_description = """Reset object on selected axis.
Location only"""
    bl_options = {"REGISTER", "UNDO"}

    x: BoolProperty(name="X", default=True)
    y: BoolProperty(name="Y", default=False)
    z: BoolProperty(name="Z", default=False)

    origin: EnumProperty(name="Modifier Types", default='ACTIVE', items=origin)

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.label(text="Origin Point")
        col.prop(self, "origin", expand=True)
        col.separator()
        col.label(text="Axis To Reset")
        layout.column(align=True)
        col.prop(self, "x", text="X", toggle=True)
        col.prop(self, "y", text="Y", toggle=True)
        col.prop(self, "z", text="Z", toggle=True)

    def execute(self, context):
        if getattr(context.active_object, "mode", "") == "OBJECT":

            object = context.active_object

            if self.origin == "ACTIVE":

                for obj in bpy.context.selected_objects:
                    if self.x is True:
                        obj.location[0] = object.location[0]
                    if self.y is True:
                        obj.location[1] = object.location[1]
                    if self.z is True:
                        obj.location[2] = object.location[2]

            elif self.origin == "CENTER":
                for obj in bpy.context.selected_objects:
                    if self.x is True:
                        obj.location[0] = 0
                    if self.y is True:
                        obj.location[1] = 0
                    if self.z is True:
                        obj.location[2] = 0

        elif getattr(context.active_object, "mode", "") == "EDIT":

            if self.x is True:
                bpy.ops.transform.resize(value=(0, 1, 1))
            if self.y is True:
                bpy.ops.transform.resize(value=(1, 0, 1))
            if self.z is True:
                bpy.ops.transform.resize(value=(1, 1, 0))

        return {"FINISHED"}
