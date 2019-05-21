import bpy
import math

from bpy.props import FloatProperty


class SmoothShading(bpy.types.Operator):
    """Activate the Auto Smooth with an 45° angle"""
    bl_idname = "object.smooth_shading"
    bl_label = "Advanced Smooth Shading"
    bl_options = {'REGISTER', 'UNDO'}

    angle = FloatProperty(name="Angle Value", min=0, max=180, subtype='ANGLE')

    @staticmethod
    def execute(self, context):
        sltd_obj = context.selected_objects
        data = bpy.data


        for obj in sltd_obj:
            if obj.type == "MESH":
                bpy.ops.object.shade_smooth()
                data.objects[obj.name].data.use_auto_smooth = True
                mesh_name = data.objects[obj.name].data.name
                angle = self.angle
                bpy.data.meshes[mesh_name].auto_smooth_angle = angle

        return {'FINISHED'}

    def invoke(self, context, event):
        self.angle = math.radians(15)

        return self.execute(self, context)


def register():
    bpy.utils.register_class(SmoothShading)


def unregister():
    bpy.utils.unregister_class(SmoothShading)
