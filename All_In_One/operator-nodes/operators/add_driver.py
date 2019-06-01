import bpy

class AddDriverOperator(bpy.types.Operator):
    bl_idname = "en.add_driver"
    bl_label = "Add Driver"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        context.active_object.node_drivers.add()
        return {"FINISHED"}