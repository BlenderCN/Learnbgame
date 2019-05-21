import bpy
from bpy.props import *
import bpy.utils.previews

#############################
# FaceOps Start Here
#############################

# Sets Up Faces For Grating


class HOPS_OT_FacegrateOperator(bpy.types.Operator):
    """
    Convert Face To Grate Pattern

    """
    bl_idname = "fgrate.op"
    bl_label = "FaceGrate"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
        bpy.ops.mesh.poke()

        # Threshold is a tricky devil
        bpy.ops.mesh.tris_convert_to_quads(face_threshold=0.698132, shape_threshold=1.39626)
        bpy.ops.mesh.inset(thickness=0.004, use_individual=True)
        return {'FINISHED'}

# Sets Up Faces For Knurling


class HOPS_OT_FaceknurlOperator(bpy.types.Operator):
    """
    Convert Face To Knurl Pattern

    """
    bl_idname = "fknurl.op"
    bl_label = "FaceKnurl"
    bl_options = {'REGISTER', 'UNDO'}
    """
    knurlSubd = IntProperty(name="KnurlSubdivisions", description="Amount Of Divisions", default=0, min = 0, max = 5)"""

    def execute(self, context):
        # allows the knurl to be subdivided
        # knurlSubd = self.knurlSubd
        # bpy.ops.mesh.subdivide(0)
        bpy.ops.mesh.inset(thickness=0.024, use_individual=True)
        bpy.ops.mesh.poke()
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        bpy.ops.mesh.select_less()
        # bpy.ops.transform.shrink_fatten(value=0.2, use_even_offset=True, mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        return {'FINISHED'}

#############################
# Panelling Operators Start Here
#############################

# Panel From An Edge Ring Selection
# Scale Dependant for now.


class HOPS_OT_EntrenchOperatorA(bpy.types.Operator):
    """
    Prototype Edge cut in operator.

    """
    bl_idname = "entrench.selection"
    bl_label = "Entrench"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        bpy.ops.mesh.bevel(offset=0.0128461, vertex_only=False)
        bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
        bpy.ops.transform.shrink_fatten(value=0.04, use_even_offset=True, mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        bpy.ops.mesh.region_to_loop()
        bpy.ops.mesh.bevel(offset=0.00885385, vertex_only=False)
        bpy.ops.mesh.select_more()
        bpy.ops.mesh.region_to_loop()
        bpy.ops.transform.edge_bevelweight(value=1)
        bpy.ops.mesh.mark_sharp()
        bpy.ops.object.editmode_toggle()
        # its important to specify that its edge mode youre working from. Vert mode is a different game altogether for it.
        return {'FINISHED'}

# Make A Panel Loop From Face Selection
# Scale Dependant for now.
class HOPS_OT_PanelOperatorA(bpy.types.Operator):
    """
    Prototype Face to panel operator.

    """
    bl_idname = "quick.panel"
    bl_label = "Sharpen"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
        bpy.ops.mesh.region_to_loop()
        bpy.ops.mesh.bevel(offset=0.00841237, segments=2, vertex_only=False)
        bpy.ops.mesh.select_less()
        bpy.ops.transform.shrink_fatten(value=0.0211908, use_even_offset=False, mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        bpy.ops.mesh.bevel(offset=0.00683826, vertex_only=False)
        return {'FINISHED'}

#############################
# OrginAndApply Operators Start Here
#############################

# apply all 2 except Loc at once and be done


class HOPS_OT_StompObjectnoloc(bpy.types.Operator):
    """
    Apply rotation and scale.

    """
    bl_idname = "stomp2.object"
    bl_label = "stompObjectnoLoc"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        # bpy.ops.object.location_clear()
        return {'FINISHED'}
