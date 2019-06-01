import bpy
from bpy.props import FloatProperty


class HOPS_OT_BrushToggle(bpy.types.Operator):
    bl_idname = "sculpt.toggle_brush"
    bl_label = "Sculpt Toggle_Brush"
    bl_description = "Toggles Brush between relative and brush along with sizes used often"
    bl_options = {"REGISTER", "UNDO"}

    amountpercent: FloatProperty(name="Detail Percent", description="Detail Brush", default=25.0, min=0.01, max=100.0)

    amountsize: FloatProperty(name="Detail Size", description="Detail Relative", default=8.0, min=0.50, max=40.0)

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def draw(self, context):
        layout = self.layout
        if bpy.context.scene.tool_settings.sculpt.detail_type_method == 'BRUSH':
            layout.prop(self, "amountpercent")
        if bpy.context.scene.tool_settings.sculpt.detail_type_method == 'RELATIVE':
            layout.prop(self, "amountsize")
        # else:
        #    layout.text("NO")

    def invoke(self, context, event):
        self.execute(context)
        return {"FINISHED"}

    def execute(self, context):
        if bpy.context.active_object.mode == 'SCULPT':
            type = bpy.context.scene.tool_settings.sculpt.detail_type_method
            toggle_brush(type, self.amountpercent, self.amountsize)
        return {"FINISHED"}


def toggle_brush(type, amountpercent, amountsize):
    if type == 'BRUSH':
        bpy.context.scene.tool_settings.sculpt.detail_refine_method = 'SUBDIVIDE'
        bpy.context.scene.tool_settings.sculpt.detail_type_method = 'RELATIVE'
        bpy.context.scene.tool_settings.sculpt.detail_size = amountsize
    if type == 'RELATIVE':
        bpy.context.scene.tool_settings.sculpt.detail_refine_method = 'SUBDIVIDE'
        bpy.context.scene.tool_settings.sculpt.detail_type_method = 'BRUSH'
        bpy.context.scene.tool_settings.sculpt.detail_percent = amountpercent
