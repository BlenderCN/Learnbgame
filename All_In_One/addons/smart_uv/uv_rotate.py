import bpy
from .addon import prefs


class SUV_OT_uv_rotate(bpy.types.Operator):
    bl_idname = "suv.uv_rotate"
    bl_label = "Rotate UV Islands"

    delta = bpy.props.IntProperty(options={'SKIP_SAVE'}, default=1)

    @classmethod
    def poll(self, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and \
            context.scene.tool_settings.uv_select_mode not in {'EDGE'}

    def execute(self, context):
        if self.delta < 0:
            valor = -prefs().uv_rotate_step
        else:
            valor = prefs().uv_rotate_step
        bpy.ops.transform.rotate(
            value=valor,
            axis=(-0, -0, -1),
            constraint_axis=(False, False, False),
            constraint_orientation='GLOBAL',
            mirror=False,
            proportional='DISABLED',
            proportional_edit_falloff='SMOOTH',
            proportional_size=1)
        return {'FINISHED'}
