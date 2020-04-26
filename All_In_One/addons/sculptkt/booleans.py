import bpy
from .multifile import register_class

@register_class
class Boolean(bpy.types.Operator):
    bl_idname = "sculpt_tool_kit.boolean"
    bl_label = "Boolean"
    bl_description = "Boolean operation"
    bl_options = {"REGISTER", "UNDO"}

    operation: bpy.props.EnumProperty(
        items = (
            ("UNION", "Union", "Union"),
            ("INTERSECT", "Intersect", "Union"),
            ("DIFFERENCE", "Difference", "Difference"),
        ),
        name="Operation"
    )

    remove_objects: bpy.props.BoolProperty(
        name="Remove Objects",
        default=True
    )

    @classmethod
    def poll(cls, context):
        if context.active_object and context.active_object.type == "MESH":
            return len(context.view_layer.objects.selected) > 1

    def execute(self, context):
        objects = list(context.view_layer.objects.selected)
        active = context.view_layer.objects.active
        objects.remove(active)
        for obj in objects:
            if not obj.type == "MESH":
                continue
            md = active.modifiers.new(type="BOOLEAN", name="BOOL")
            md.object = obj
            md.operation = self.operation
            bpy.ops.object.modifier_apply(modifier=md.name)

        if self.remove_objects:
            for obj in objects:
                if not obj.type == "MESH":
                    continue
                bpy.data.meshes.remove(obj.data)

        return {"FINISHED"}

@register_class
class Slice(bpy.types.Operator):
    bl_idname = "sculpt_tool_kit.slice_boolean"
    bl_label = "Slice Boolean"
    bl_description = "Cut selected objects using active object as a knife"
    bl_options = {"REGISTER", "UNDO"}

    thickness: bpy.props.FloatProperty(
        name="Thickness",
        default = 0.0001
    )

    remove_objects: bpy.props.BoolProperty(
        name="Remove Objects",
        default=False
    )

    @classmethod
    def poll(cls, context):
        if context.active_object and context.active_object.type == "MESH":
            return len(context.view_layer.objects.selected) > 1

    def execute(self, context):
        objects = list(context.view_layer.objects.selected)
        active = context.view_layer.objects.active
        objects.remove(active)

        for obj in objects:
            if not obj.type == "MESH":
                continue
            md = obj.modifiers.new(type="SOLIDIFY", name="Thickness")
            md.thickness = self.thickness
            md_bool = active.modifiers.new(type="BOOLEAN", name="Bool")
            md_bool.operation = "DIFFERENCE"
            md_bool.object = obj
            context.scene.update()
            bpy.ops.object.modifier_apply(modifier=md_bool.name)
            obj.modifiers.remove(md)

        if self.remove_objects:
            for obj in objects:
                if not obj.type == "MESH":
                    continue
                bpy.data.meshes.remove(obj.data)
        else:
            for obj in objects:
                obj.select_set(False)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.separate(type="LOOSE")
        bpy.ops.object.mode_set(mode="OBJECT")

        return {"FINISHED"}
