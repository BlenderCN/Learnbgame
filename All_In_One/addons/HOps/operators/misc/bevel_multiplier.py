import bpy
from bpy.props import BoolProperty, FloatProperty


class HOPS_OT_BevelMultiplier(bpy.types.Operator):
    bl_idname = "view3d.bevel_multiplier"
    bl_label = "Hops Bevel Multiplier"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Multiplies / Divides bevel width of selected objects"

    multiply: BoolProperty(name="Multiply/Divide",
                           description="multiply or devide bevel value for modifier",
                           default=True)

    multiply_amount: FloatProperty(name="Multiply by", description="Multiply by", default=2.0, min=0.0)
    divide_amount: FloatProperty(name="Divide by", description="Divide by", default=2.0, min=0.1)

    use_active: BoolProperty(name="Unify Bevel To Active",
                             description="Unify bevel value for modifiers To Active",
                             default=False)

    active_value: FloatProperty(name="Active Bevel Value", description="active object bevel value", default=0,)

    @classmethod
    def poll(cls, context):
        object = context.active_object
        if object is None: return False
        return object.type == "MESH" and object.mode == "OBJECT"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(self, "multiply")
        box = layout.box()
        box.prop(self, "multiply_amount")
        box.prop(self, "divide_amount")
        box = layout.box()
        box.prop(self, "use_active")

    def execute(self, context):

        object = bpy.context.active_object
        for modifieractive in object.modifiers:
            if modifieractive.type == "BEVEL":
                self.active_value = modifieractive.width

        for obj in bpy.context.selected_objects:
            for modifier in obj.modifiers:
                if modifier.type == "BEVEL":
                    if self.use_active:
                        if self.multiply:
                            modifier.width = self.active_value * self.multiply_amount
                        else:
                            modifier.width = self.active_value / self.divide_amount
                    else:
                        if self.multiply:
                            modifier.width = modifier.width * self.multiply_amount
                        else:
                            modifier.width = modifier.width / self.divide_amount
        return {'FINISHED'}
