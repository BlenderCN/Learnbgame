import bpy
import os.path
from .step5_utils import apply_modifiers, clear_parent_transform, append, assign_subsurf, \
    apply_transform_constraints, set_decimate_geometry
from ... common_utils import apply_to_selected

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator

#Panel
class VIEW3D_PT_jet_step5(bpy.types.Panel):
    bl_label = "5. Model Preparation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Jet"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.scene.Jet.info, "model_preparation", text="", icon="INFO")

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(context.scene.Jet, "subdivisions", text="Subbdivisions")
        row.operator("jet_assign_subsurf.btn", text="", icon="RIGHTARROW").subdiv = context.scene.Jet.subdivisions

        col = layout.column(align=True)
        col.operator("jet_apply_modifiers.btn", text="Apply Modifiers").remove_subsurf = context.scene.Jet.remove_subsurf
        col.prop(context.scene.Jet, "remove_subsurf", text="Remove Subsurf if last modifier", toggle=True)

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(context.scene.Jet, "decimate_ratio", text="Decimate Ratio")
        row.operator("jet_set_decimate.btn", text="", icon="RIGHTARROW").ratio = context.scene.Jet.decimate_ratio

        col = layout.column(align=True)
        col.operator("jet_apply_transf_constraints.btn", text="Apply Visual Transform")
        col = layout.column(align=True)
        col.operator("jet_clear_parent_transf.btn", text="Clear Parent with Transform")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(context.scene.Jet, "optimized_res_file", text="Proxy")
        row.operator("load_blend.btn", text="", icon="FILESEL").attr = "optimized_res_file"
        row = col.row(align=True)
        row.prop(context.scene.Jet, "high_res_file", text="Hi-Res")
        row.operator("load_blend.btn", text="", icon="FILESEL").attr = "high_res_file"

        hi =    (context.scene.Jet.high_res_file != "") and os.path.isfile(context.scene.Jet.high_res_file)
        proxy = (context.scene.Jet.optimized_res_file != "") and os.path.isfile(context.scene.Jet.optimized_res_file)
        row = col.row()
        row.enabled = hi and proxy
        op = col.operator("jet_append_opt_high.btn", text="Bring models to scene")
        op.optimized = context.scene.Jet.optimized_res_file
        op.high = context.scene.Jet.high_res_file

        row = layout.row(align=True)
        row.enabled = hi and proxy
        row.prop(context.scene.Jet.swap, "model", expand=True)


#Operators
class VIEW3D_OT_jet_append_opt_high(bpy.types.Operator):
    bl_idname = "jet_append_opt_high.btn"
    bl_label = "Bring proxy and hi-res models to scene"
    bl_description = "Bring proxy and hi-res models to scene"

    optimized = bpy.props.StringProperty(default='')
    high = bpy.props.StringProperty(default='')

    @classmethod
    def poll(cls, context):
        hi = (context.scene.Jet.high_res_file != "") and os.path.isfile(context.scene.Jet.high_res_file)
        return hi and ((context.scene.Jet.optimized_res_file != "") and os.path.isfile(context.scene.Jet.optimized_res_file))

    def execute(self, context):
        append(context, self.optimized, self.high)
        context.scene.Jet.swap.model = 'proxy'
        return {'FINISHED'}


class VIEW3D_OT_jet_apply_modifiers(bpy.types.Operator):
    bl_idname = "jet_apply_modifiers.btn"
    bl_label = "Apply Modifiers"
    bl_description = "Apply modifiers to selected objects"

    remove_subsurf = bpy.props.BoolProperty(default=True)

    def execute(self, context):
        apply_to_selected(context, apply_modifiers, value=self.remove_subsurf)
        return {'FINISHED'}


class VIEW3D_OT_jet_clear_parent_transform(bpy.types.Operator):
    bl_idname = "jet_clear_parent_transf.btn"
    bl_label = "Clear parent with transform"
    bl_description = "Clear parent with transform in all selected objects"

    def execute(self, context):
        apply_to_selected(context, clear_parent_transform)
        return {'FINISHED'}

class VIEW3D_OT_jet_set_decimate(bpy.types.Operator):
    bl_idname = "jet_set_decimate.btn"
    bl_label = "Set Decimate Geometry"
    bl_description = "Set Decimate Geometry command with the customized ratio to all selected objects"

    ratio = bpy.props.IntProperty(default=10)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        apply_to_selected(context, set_decimate_geometry, value=self.ratio/100)
        return {'FINISHED'}


class VIEW3D_OT_jet_assign_subsurf(bpy.types.Operator):
    bl_idname = "jet_assign_subsurf.btn"
    bl_label = "Assign subsurf"
    bl_description = "Assign subsurf and set the subdivisions to all selected objects" \
                     "\nThe subdivisions will be applied to the last subsurf in the modifier stack"

    subdiv = bpy.props.IntProperty(default=2)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        apply_to_selected(context, assign_subsurf, value=self.subdiv)
        return {'FINISHED'}


class VIEW3D_OT_jet_apply_transf_constraints(bpy.types.Operator):
    bl_idname = "jet_apply_transf_constraints.btn"
    bl_label = "Apply Visual Transform and Constraints"
    bl_description = "Apply Visual Transform and remove constraints to all selected objects"

    def execute(self, context):
        apply_to_selected(context, apply_transform_constraints)
        return {'FINISHED'}


class VIEW3D_OT_jet_load_blend_file(Operator, ImportHelper):
    bl_idname = "load_blend.btn"
    bl_label = "Load blend dialog"

    filename_ext = ".blend"

    filter_glob = StringProperty(
            default="*.blend",
            options={'HIDDEN'},
            maxlen=255)

    attr = StringProperty(default="",
                          options={'HIDDEN'})

    def execute(self, context):
        setattr(context.scene.Jet, self.attr, self.filepath)
        return {'FINISHED'}
