import bpy
import math
from bpy.props import EnumProperty, IntProperty, FloatProperty, BoolProperty
import bpy.utils.previews
from ... operators.utils import update_bevel_modifier_if_necessary
from ... utils.context import ExecutionContext
from ... utils.objects import apply_modifiers, get_modifier_with_type
from ... preferences import get_preferences



mod_types = [
    ("BOOLEAN", "Boolean", ""),
    ("MIRROR", "Mirror", ""),
    ("BEVEL", "Bevel", ""),
    ("SOLIDIFY", "Solidify", ""),
    ("ARRAY", "Array", "")]


class HOPS_OT_StepOperator(bpy.types.Operator):
    bl_idname = "hops.step"
    bl_label = "Hops Step Operator"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = """Applies Csharp / Hides mesh in edit mode / Adds new BEVEL modifier
Typically used for booleans and should be used with smaller radius"""

    items = [(x.identifier, x.name, x.description, x.icon)
             for x in bpy.types.Modifier.bl_rna.properties['type'].enum_items]

    modifier_types: EnumProperty(name="Modifier Types", default={'BEVEL'},
                                 options={"ENUM_FLAG"}, items=mod_types)

    bevelwidth: FloatProperty(name="Bevel Width Amount", description="Set Bevel Width", default=0.01, min=0.002, max=0.25)

    segment_amount: IntProperty(name="Segments", description="Segments For Bevel", default=6, min=1, max=12)

    bevelwidth: FloatProperty(name="Bevel Width Amount",
                              description="Set Bevel Width",
                              default=0.0200,
                              min=0.002,
                              max=1.50)

    hide_mesh: BoolProperty(name="Hide Mesh",
                            description="Hide Mesh",
                            default=True)

    profile_value = 0.70

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        object = context.active_object
        if object is None: return False
        if object.mode == "OBJECT" and all(obj.type == "MESH" for obj in selected):
            return True

    def execute(self, context):
        selected = context.selected_objects
        object = context.active_object

        for obj in selected:
            bpy.context.view_layer.objects.active = obj

            if get_preferences().workflow_mode == "WEIGHT":
                self.step_active_object(
                    obj,
                    self.modifier_types)

                update_bevel_modifier_if_necessary(
                    context.active_object,
                    self.segment_amount,
                    self.bevelwidth,
                    self.profile_value)

            else:
                if obj.hops.is_pending_boolean:
                    self.bevel(
                        context.active_object,
                        self.segment_amount,
                        self.bevelwidth,
                        self.profile_value)

            obj.hops.status = "CSTEP"

        bpy.context.view_layer.objects.active = object

        return {"FINISHED"}

    def step_active_object(self, object, modifier_types):
        with ExecutionContext(mode="OBJECT", active_object=object):
            apply_modifiers(object, modifier_types)

        with ExecutionContext(mode="EDIT", active_object=object):
            bpy.ops.mesh.reveal()
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.transform.edge_bevelweight(value=-1)
            bpy.ops.transform.edge_crease(value=-1)
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_all(action='SELECT')

            if self.hide_mesh:
                bpy.ops.mesh.hide()

    def bevel(self, object, segment_amount, bevelwidth, profile_value):
        bevel = object.modifiers.new("Bevel", "BEVEL")
        bevel.use_clamp_overlap = False
        bevel.show_in_editmode = False
        bevel.width = bevelwidth
        bevel.profile = profile_value
        bevel.limit_method = get_preferences().workflow_mode
        bevel.show_in_editmode = True
        bevel.harden_normals = False
        bevel.miter_outer = 'MITER_ARC'
        bevel.segments = segment_amount
        bevel.loop_slide = get_preferences().bevel_loop_slide
        bevel.angle_limit = math.radians(60)
