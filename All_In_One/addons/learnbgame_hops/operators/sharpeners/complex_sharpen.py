import bpy
from math import radians
from bpy.props import EnumProperty, IntProperty, FloatProperty, BoolProperty
from .. utils import update_bevel_modifier_if_necessary, update_Weight_modifier_if_necessary
from ... utils.context import ExecutionContext
from . soft_sharpen import soft_sharpen_object
from ... preferences import get_preferences
from ... utils.objects import apply_modifiers
from ... utils.objects import get_modifier_with_type
from ... utility import modifier

mod_types = [
    ("BOOLEAN", "Boolean", ""),
    ("MIRROR", "Mirror", ""),
    ("BEVEL", "Bevel", ""),
    ("SOLIDIFY", "Solidify", ""),
    ("ARRAY", "Array", "")]


class HOPS_OT_ComplexSharpenOperator(bpy.types.Operator):
    bl_idname = "hops.complex_sharpen"
    bl_label = "Hops Csharpen"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """Adds Bevel Modifier / Shade Smooth / Enable Autosmooth
Mark Sharp Edges / Destructively Bakes - Ignores Modifiers via F6 """

    items: [(x.identifier, x.name, x.description, x.icon)
            for x in bpy.types.Modifier.bl_rna.properties['type'].enum_items]

    modifier_types: EnumProperty(name="Modifier Types", default={'BOOLEAN', 'SOLIDIFY'},
                                 options={"ENUM_FLAG"}, items=mod_types)

    segment_amount: IntProperty(name="Segments", description="Segments For Bevel", default=3, min=1, max=12)

    bevelwidth: FloatProperty(name="Bevel Width Amount",
                              description="Set Bevel Width",
                              default=0.0200,
                              precision=3,
                              min=0.000,
                              max=100)

    segment_modal: IntProperty(name="Segments", description="Segments For Bevel", default=3, min=1, max=12)

    bevelwidth_modal: FloatProperty(name="Bevel Width Amount",
                                    description="Set Bevel Width",
                                    default=0.0200,
                                    precision=3,
                                    min=0.000,
                                    max=100)

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

    profile_value = 0.70
    reveal_mesh = True

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        object = context.active_object
        if object is None: return False
        if object.mode == "OBJECT" and all(obj.type == "MESH" for obj in selected):
            return True

    def draw(self, context):
        layout = self.layout

        col = layout.column()

        col.label(text="Modifiers Applied By Csharp")
        colrow = col.row(align=True)

        colrow.prop(self, "modifier_types", expand=True)
        col.separator()
        col.label(text="General Parameters")
        col = layout.column(align=True)
        colrow = col.row(align=True).split(factor=0.3, align=True)
        colrow.prop(self, "segment_modal", text='')
        colrow.prop(self, "segment_amount")
        colrow = col.row(align=True).split(factor=0.3, align=True)
        colrow.prop(self, "bevelwidth_modal", text='')
        colrow.prop(self, "bevelwidth")
        col.separator()

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
        selected = context.selected_objects
        object = bpy.context.active_object

        self.is_global = context.active_object.hops.is_global
        self.auto_smooth_angle = context.active_object.data.auto_smooth_angle

        for obj in selected:
            bevel = get_modifier_with_type(object, "BEVEL")
            if bevel is not None:
                self.segment_amount = bevel.segments
                self.bevelwidth = bevel.width
            else:
                self.segment_amount = self.segment_modal
                self.bevelwidth = self.bevelwidth_modal

        self.execute(context)
        if get_preferences().auto_bweight:
            bpy.ops.hops.adjust_bevel("INVOKE_DEFAULT")

        return {"FINISHED"}

    def execute(self, context):

        selected = context.selected_objects
        object = bpy.context.active_object

        for obj in selected:

            if object.hops.status == "CSTEP":
                self.reveal_mesh = False

            complex_sharpen_active_object(
                obj,
                get_preferences().sharpness,
                get_preferences().auto_smooth_angle,
                self.additive_mode,
                self.modifier_types,
                self.segment_amount,
                self.bevelwidth,
                self.reveal_mesh)

            update_bevel_modifier_if_necessary(
                obj,
                self.segment_amount,
                self.bevelwidth,
                self.profile_value)

            if get_preferences().add_weighten_normals_mod:
                update_Weight_modifier_if_necessary(obj)

            obj.hops.is_global = self.is_global
            obj.data.auto_smooth_angle = get_preferences().auto_smooth_angle if self.is_global else self.auto_smooth_angle

        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected:
            obj.select_set(state=True)
        bpy.context.view_layer.objects.active = object

        return {"FINISHED"}


def complex_sharpen_active_object(object, sharpness, auto_smooth_angle, additive_mode, modifier_types, segment_amount, bevelwidth, reveal_mesh):
    modifier.apply(object, type=modifier_types)
    soft_sharpen_object(object, sharpness, auto_smooth_angle, additive_mode, reveal_mesh)

    object = bpy.context.active_object

    if object.hops.status != "CSTEP":
        object.hops.status = "CSHARP"
