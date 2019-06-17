import bpy


class HOPS_OT_Shrinkwrap(bpy.types.Operator):
    bl_idname = "hops.shrinkwrap2"
    bl_label = "Hops Shrinkwrap2"
    bl_description = "Shrinkwrap selected mesh"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        object = context.active_object
        if object is None: return False
        if object.mode == "OBJECT" and object.type == "MESH":
            return True

    def execute(self, context):
        object = context.active_object
        objects = context.selected_objects

        for obj in objects:
            if obj.name != object.name:

                mod = obj.modifiers.new("Shrinkwrap", "SHRINKWRAP")
                mod.target = object

        return {"FINISHED"}
