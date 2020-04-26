import bpy
from .multifile import register_class


@register_class
class Symmetrize(bpy.types.Operator):
    bl_idname = "sculpt_tool_kit.symmetrize"
    bl_label = "Symmetrize"
    bl_description = "Mirror mesh around an axis"
    bl_options = {"REGISTER", "UNDO"}

    axis: bpy.props.EnumProperty(
        name="Axis",
        description="Which axis to symmetrize",
        items=(
            ("POSITIVE_X", "+x to -x", "+x to -x"),
            ("POSITIVE_Y", "+y to -y", "+y to -y"),
            ("POSITIVE_Z", "+z to -z", "+z to -z"),
            ("NEGATIVE_X", "-x to +x", "-x to +x"),
            ("NEGATIVE_Y", "-y to +y", "-y to +y"),
            ("NEGATIVE_Z", "-z to +z", "-z to +z")
        )
    )

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == "MESH"

    def execute(self, context):
        bpy.ops.ed.undo_push()
        context.scene.update()
        ob = context.active_object
        if ob.mode == "SCULPT" and ob.use_dynamic_topology_sculpting:
            context.scene.tool_settings.sculpt.symmetrize_direction = self.axis
            bpy.ops.sculpt.symmetrize()
        else:
            last_mode = ob.mode
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.mesh.symmetrize(direction=self.axis)
            bpy.ops.object.mode_set(mode=last_mode)

        return {"FINISHED"}
