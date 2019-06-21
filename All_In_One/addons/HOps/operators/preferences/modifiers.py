import bpy


class HOPS_OT_CollapseModifiers(bpy.types.Operator):
    """
    Collapse all modifiers

    """
    bl_idname = "hops.collapse_modifiers"
    bl_label = "Collapse Modifiers"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):

        scene = bpy.context.scene

        objects = [obj for obj in scene.objects if obj.type == "MESH"]

        for obj in objects:
            for mod in obj.modifiers:
                mod.show_expanded = False

        return {"FINISHED"}


class HOPS_OT_OpenModifiers(bpy.types.Operator):
    """
    Expand all modifiers

    """
    bl_idname = "hops.open_modifiers"
    bl_label = "Open Modifiers"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):

        scene = bpy.context.scene

        objects = [obj for obj in scene.objects if obj.type == "MESH"]

        for obj in objects:
            for mod in obj.modifiers:
                mod.show_expanded = True

        return {"FINISHED"}
