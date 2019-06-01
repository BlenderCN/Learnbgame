import bpy


class HOPS_OT_BoolToggle(bpy.types.Operator):
    bl_idname = "hops.bool_toggle_viewport"
    bl_label = "Boolean Modifier Toggle"
    bl_description = "Toggles viewport visibility of all boolean modifiers on selected object."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if context.object is not None:
            bools = [mod for mod in context.object.modifiers if mod.type == "BOOLEAN"]
            if bools:
                first_bool = bools[0].show_viewport
                for mod in context.object.modifiers:
                    mod.show_viewport = not first_bool

        return {"FINISHED"}
