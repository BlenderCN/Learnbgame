import bpy
from ... utils.objects import get_current_selected_status


class HOPS_OT_CurveBevelOperator(bpy.types.Operator):
    bl_idname = "hops.curve_bevel"
    bl_label = "Sets 2nd Curve To Bevel"
    bl_description = "Set's 2nd Curve to 1st Curve Bevel Object"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        active_object, other_objects, other_object = get_current_selected_status()
        bpy.context.object.data.bevel_object = other_object
        return {"FINISHED"}
