import bpy
import bmesh


class MaskDecimate(bpy.types.Operator):
    bl_idname = "f_tools_2.decimate"
    bl_label = "Mask Decimate"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    ratio = bpy.props.FloatProperty(
        name="Ratio",
        description="How much to recuce",
        default=0.7,
        min = 0.0000001,
        max = 1.0
    )

    @classmethod
    def poll(cls, context):
        if context.active_object:
            if not context.active_object.mode == "EDIT":
                return context.active_object.type == "MESH"

    def execute(self, context):
        ob = context.active_object
        md = ob.modifiers.new(type="DECIMATE", name="Decmater")
        md.ratio = self.ratio
        bpy.ops.object.modifier_apply(modifier=md.name)
        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "ratio", slider = True)
