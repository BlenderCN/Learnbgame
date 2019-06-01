import bpy
from . import operator
from ... preferences import get_preferences


class HOPS_OT_BoolUnion(bpy.types.Operator):
    bl_idname = "hops.bool_union"
    bl_label = "Hops Union Boolean"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Merges mesh using Union Boolean"

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        if all(obj.type == "MESH" for obj in selected):
            return True

    def execute(self, context):
        if len(bpy.context.selected_objects) < 2:
            return {'CANCELLED'}
        else:
            operator.boolean(context, 'UNION')

        return {'FINISHED'}
