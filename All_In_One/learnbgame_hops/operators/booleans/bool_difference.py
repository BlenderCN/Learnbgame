import bpy
from . import operator
from ... preferences import get_preferences


class HOPS_OT_BoolDifference(bpy.types.Operator):
    bl_idname = "hops.bool_difference"
    bl_label = "Hops Difference Boolean"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Cuts mesh using Difference Boolean"

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        if all(obj.type == "MESH" for obj in selected):
            return True

    def execute(self, context):
        if len(bpy.context.selected_objects) < 2:
            return {'CANCELLED'}
        else:
            operator.boolean(context, 'DIFFERENCE')

        return {'FINISHED'}
