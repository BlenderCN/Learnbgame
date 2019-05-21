import bpy
import bmesh
from .. utils.context import ExecutionContext
from .. utils.objects import get_modifier_with_type
from .. preferences import get_preferences


def update_Weight_modifier_if_necessary(object):
    W_mod = get_modifier_with_type(object, "WEIGHTED_NORMAL")
    if W_mod is None:
        w_mod = object.modifiers.new("Weighted Normal", "WEIGHTED_NORMAL")
        w_mod.show_expanded = False


def update_bevel_modifier_if_necessary(object, segment_amount, bevelwidth, profile_value):
    bevel = get_modifier_with_type(object, "BEVEL")
    if bevel is None:
        bevel = object.modifiers.new("Bevel", "BEVEL")
        bevel.use_clamp_overlap = False
        bevel.show_in_editmode = False
        bevel.width = bevelwidth
        bevel.profile = profile_value
        bevel.limit_method = get_preferences().workflow_mode
        bevel.show_in_editmode = True
        bevel.segments = segment_amount
        bevel.loop_slide = get_preferences().bevel_loop_slide
    else:
        bevel.segments = segment_amount
        bevel.width = bevelwidth


def clear_ssharps(object):
    with ExecutionContext(mode="EDIT", active_object=object):
        bpy.ops.mesh.select_mode(type="EDGE", action="ENABLE")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.transform.edge_bevelweight(value=-1)
        bpy.ops.mesh.mark_sharp(clear=True)
        bpy.ops.transform.edge_crease(value=-1)


def convert_to_sharps(object):
    with ExecutionContext(mode="EDIT", active_object=object):
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_mode(type="EDGE", action="ENABLE")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.transform.edge_bevelweight(value=-1)
        bpy.ops.transform.edge_crease(value=-1)
        bpy.ops.mesh.mark_sharp(clear=False)


def mark_ssharps(object, sharpness):
    with ExecutionContext(mode="EDIT", active_object=object):
        bpy.context.scene.tool_settings.use_mesh_automerge = False
        only_select_sharp_edges(sharpness)

        if get_preferences().sharp_use_crease:
            bpy.ops.transform.edge_crease(value=1)

        if get_preferences().sharp_use_sharp:
            bpy.ops.mesh.mark_sharp(clear=False, use_verts=False)

        if get_preferences().sharp_use_seam:
            bpy.ops.mesh.mark_seam(clear=False)

        if get_preferences().sharp_use_bweight:
            obj = bpy.context.object
            me = obj.data
            bm = bmesh.from_edit_mesh(me)
            cr = bm.edges.layers.bevel_weight.verify()

            for e in bm.edges:
                if (e[cr] > 0):
                    e.select_set(state=False)

            bmesh.update_edit_mesh(me, False, False)
            bpy.ops.transform.edge_bevelweight(value=1)


def mark_ssharps_bmesh(object, sharpness, reveal_mesh, additive_mode):

    me = object.data

    bm = bmesh.new()
    bm.from_mesh(me)

    if get_preferences().sharp_use_crease:
        cr = bm.edges.layers.crease.verify()
    if get_preferences().sharp_use_bweight:
        bw = bm.edges.layers.bevel_weight.verify()

    if reveal_mesh:
        alledges = [e for e in bm.edges if len(e.link_faces) == 2]
    else:
        alledges = [e for e in bm.edges if not e.hide and (len(e.link_faces) == 2)]

    for e in alledges:
        if not additive_mode:
            if get_preferences().sharp_use_crease:
                e[cr] = 0
            if get_preferences().sharp_use_sharp:
                e.smooth = True
            if get_preferences().sharp_use_seam:
                e.seam = False
            if get_preferences().sharp_use_bweight:
                e[bw] = 0
        if e.calc_face_angle() >= sharpness:
            if get_preferences().sharp_use_crease:
                e[cr] = 1
            if get_preferences().sharp_use_sharp:
                e.smooth = False
            if get_preferences().sharp_use_seam:
                e.seam = True
            if get_preferences().sharp_use_bweight:
                if e[bw] == 0:
                    e[bw] = 1

    bm.to_mesh(me)
    bm.free()


def set_smoothing(object, auto_smooth_angle):
    bpy.ops.object.shade_smooth()
    object.data.use_auto_smooth = True
    object.data.auto_smooth_angle = auto_smooth_angle


def only_select_sharp_edges(sharpness):
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.edges_select_sharp(sharpness=sharpness)
