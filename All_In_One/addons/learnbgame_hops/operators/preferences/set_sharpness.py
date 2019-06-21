import bpy
from math import radians
from bpy.props import FloatProperty
from ... preferences import get_preferences


class HOPS_OT_SetSharpness30(bpy.types.Operator):
    bl_idname = "hops.set_sharpness_30"
    bl_label = "Set Hops Global Sharpness Angle 30"
    bl_options = {"REGISTER", "INTERNAL"}
    bl_description = "Sets hops global sharpness angle"

    sharpness: FloatProperty(name="angle edge marks are applied to", default=radians(30), min=radians(1), max=radians(180), subtype="ANGLE")

    def execute(self, context):

        get_preferences().sharpness = self.sharpness

        return {"FINISHED"}


class HOPS_OT_SetSharpness45(bpy.types.Operator):
    bl_idname = "hops.set_sharpness_45"
    bl_label = "Set Hops Global Sharpness Angle 45"
    bl_options = {"REGISTER", "INTERNAL"}
    bl_description = "Sets hops global sharpness angle"

    sharpness: FloatProperty(name="angle edge marks are applied to", default=radians(45), min=radians(1), max=radians(180), subtype="ANGLE")

    def execute(self, context):

        get_preferences().sharpness = self.sharpness

        return {"FINISHED"}


class HOPS_OT_SetSharpness60(bpy.types.Operator):
    bl_idname = "hops.set_sharpness_60"
    bl_label = "Set Hops Global Sharpness Angle 60"
    bl_options = {"REGISTER", "INTERNAL"}
    bl_description = "Sets hops global sharpness angle"

    sharpness: FloatProperty(name="angle edge marks are applied to", default=radians(60), min=radians(1), max=radians(180), subtype="ANGLE")

    def execute(self, context):

        get_preferences().sharpness = self.sharpness

        return {"FINISHED"}
