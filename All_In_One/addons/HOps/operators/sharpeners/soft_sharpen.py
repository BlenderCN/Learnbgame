import bpy
from math import radians
from bpy.props import BoolProperty, FloatProperty
from ... utils.context import ExecutionContext
from ... preferences import get_preferences
from .. utils import clear_ssharps, mark_ssharps, set_smoothing, mark_ssharps_bmesh
from ... utility import modifier


class HOPS_OT_SoftSharpenOperator(bpy.types.Operator):
    bl_idname = "hops.soft_sharpen"
    bl_label = "Hops Ssharpen"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Shade Smooth / Enable Autosmooth / Mark Sharp Edges"

    additive_mode: BoolProperty(name="Additive Mode",
                                description="Don't clear existing edge properties",
                                default=True)

    auto_smooth_angle: FloatProperty(name="angle edge marks are applied to",
                                     default=radians(60),
                                     min=radians(1),
                                     max=radians(180),
                                     precision=3,
                                     unit='ROTATION')

    is_global: BoolProperty(name="Is Global", default=True)

    reveal_mesh = True

    message = "NO!"

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        object = context.active_object
        if object is None: return False
        if object.mode in {"OBJECT", "EDIT"} and all(obj.type == "MESH" for obj in selected):
            return True

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.label(text="Sharpening Parameters")
        col = layout.column(align=True)
        colrow = col.row(align=True).split(factor=0.3, align=True)
        colrow.prop(self, "additive_mode", toggle=True)
        colrow.prop(get_preferences(), "sharpness", text="Sharpness")
        colrow = col.row(align=True).split(factor=0.3, align=True)
        colrow.prop(self, "is_global", text="Global", toggle=True)
        if self.is_global:
            colrow.prop(get_preferences(), "auto_smooth_angle", text="Auto Smooth Angle")
        else:
            colrow.prop(self, "auto_smooth_angle", text="Auto Smooth Angle")
        col.separator()

    def invoke(self, context, event):
        self.is_global = context.active_object.hops.is_global
        self.auto_smooth_angle = context.active_object.data.auto_smooth_angle

        self.execute(context)

        return {"FINISHED"}

    def execute(self, context):

        # Vitaliy!
        selected = context.selected_objects

        for obj in selected:

            if obj.hops.status == "CSTEP":
                self.reveal_mesh = False

            soft_sharpen_object(
                obj,
                get_preferences().sharpness,
                get_preferences().auto_smooth_angle,
                self.additive_mode,
                self.reveal_mesh)

            obj.hops.is_global = self.is_global
            obj.data.auto_smooth_angle = get_preferences().auto_smooth_angle if self.is_global else self.auto_smooth_angle

        return {"FINISHED"}


def soft_sharpen_object(object, sharpness, auto_smooth_angle, additive_mode, reveal_mesh):

    mark_ssharps_bmesh(object, sharpness, reveal_mesh, additive_mode)
    set_smoothing(object, auto_smooth_angle)
    # modifier.bevel_method(object)
