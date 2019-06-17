import bpy
from bpy.props import BoolProperty


class HOPS_OT_BoolToggle(bpy.types.Operator):
    bl_idname = "hops.bool_toggle_viewport"
    bl_label = "Modifier Toggle"
    bl_description = "Toggles viewport visibility of all modifiers on selected object."
    bl_options = {"REGISTER", "UNDO"}

    all_modifiers: BoolProperty(
        name="Hide All Modifiers",
        description="Hide all Modifiers",
        default=False)

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col = layout.column(align=True)
        colrow = col.row(align=True).split(factor=0.6, align=True)
        colrow.prop(self, "all_modifiers", toggle=True)

    def execute(self, context):
        if context.object is not None:
            for mod in context.active_object.modifiers:
                mod.show_viewport = not mod.show_viewport

        return {"FINISHED"}
