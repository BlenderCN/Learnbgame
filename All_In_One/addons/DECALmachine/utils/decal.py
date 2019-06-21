import bpy
from mathutils import Vector, Matrix
import os
import re
from . material import get_decal_textures, get_decalgroup_from_decalmat, get_parallaxgroup_from_decalmat, get_heightgroup_from_parallaxgroup, get_decal_texture_nodes, auto_match_material, remove_decalmat, get_panel_material
from . raycast import cast_bvh_ray_from_object, get_origin_from_object, find_nearest, get_origin_from_face, get_origin_from_object_boundingbox, cast_bvh_ray_from_mouse, get_grid_intersection, cast_obj_ray_from_mouse, cast_obj_ray_from_object
from . object import parent, lock
from . modifier import get_nrmtransfer, get_displace, add_nrmtransfer, add_displace, get_shrinkwrap
from . registration import get_prefs, get_path
from . math import create_rotation_matrix_from_normal, flatten_matrix, get_sca_matrix
from . append import append_scene
from . collection import unlink_object
from .. utils.debug import draw_vector


def get_target(context, decal):
    target = context.active_object if context.active_object and context.active_object in context.selected_objects and not context.active_object.DM.isdecal else None

    if target:
        return target

    else:
        target, _, _, _, _ = cast_bvh_ray_from_object(decal, (0, 0, -1), backtrack=0.01)

        return target if target else decal.parent if decal.parent else None


# PROPERTIES & NAMING

def set_props_and_node_names_of_library_decal(library, name, decalobj=None, decalmat=None, decaltextures=None, decaltype=None, uuid=None, creator=None):
    if any([decalobj, decalmat, decaltextures]):
        decalname = "%s_%s" % (library, name)

        # find out what elements are provided and determine the others if possible
        if decalobj:
            if not decalmat:
                decalmat = decalobj.active_material

        if decalmat:
            decalmat.name = decalname

            if not decaltextures:
                textures = get_decal_textures(decalmat)

                if textures:
                    decaltextures = list(textures.values())

        # create list of all components to receive DM props and set them
        complist = [comp for comp in [decalobj, decalmat] + decaltextures if comp]

        for component in complist:
            component.DM.decallibrary = library
            component.DM.decalname = decalname
            component.DM.decalmatname = decalname

            # set decaltype if is passed in (as in UpdateLegacyDecals())
            if decaltype:
                component.DM.decaltype = decaltype

            # set uuid if is passed in
            if uuid:
                component.DM.uuid = uuid

            # set creator if is passed in
            if creator:
                component.DM.creator = creator


        # set decalobj props from material, if they aren't set already set (like or sliced panels) or when the panel material is changed (like with the adjusttool)
        if decalobj and decalmat:
            decalobj.DM.uuid = decalmat.DM.uuid
            decalobj.DM.creator = decalmat.DM.creator


        # set node and tree names, as well as image names
        if decalmat:
            decalgroup = get_decalgroup_from_decalmat(decalmat)

            decalgroup.name = "%s.%s" % (decalmat.DM.decaltype.lower(), decalname)
            decalgroup.node_tree.name = decalgroup.name

            parallaxgroup = get_parallaxgroup_from_decalmat(decalmat)

            if parallaxgroup:
                parallaxgroup.name = "parallax.%s" % (decalname)
                parallaxgroup.node_tree.name = parallaxgroup.name
                decalmat.DM.parallaxnodename = parallaxgroup.name

                heightgroups = get_heightgroup_from_parallaxgroup(parallaxgroup, getall=True)

                if heightgroups:
                    for idx, hg in enumerate(heightgroups):
                        hg.name = "height.%s" % (decalname)

                        if idx == 0:
                            hg.node_tree.name = hg.name
            else:
                decalmat.DM.parallaxnodename = ""


            # set image node names and image names
            imgnodes = get_decal_texture_nodes(decalmat, height=True)

            for textype, node in imgnodes.items():
                node.name = "%s.%s" % (textype.lower(), decalname)

                if textype != "HEIGHT":
                    node.image.name = ".%s.%s" % (textype.lower(), decalname)


def set_decalobj_props_from_material(obj, decalmat):
    obj.DM.decallibrary = decalmat.DM.decallibrary
    obj.DM.decalname = decalmat.DM.decalname
    obj.DM.decalmatname = decalmat.DM.decalmatname
    obj.DM.uuid = decalmat.DM.uuid
    obj.DM.creator = decalmat.DM.creator


def set_decalobj_name(decalobj, decalname=None, uuid=None):
    """
    determine the object name, specifically the counter. it should count up, instead of just setting it to the decalname
    """

    decalname = decalname if decalname else decalobj.DM.decalname
    uuid = uuid if uuid else decalobj.DM.uuid

    if uuid:
        decals = [obj for obj in bpy.data.objects if obj != decalobj and obj.DM.uuid == uuid]

        if decals:
            counters = []
            countRegex = re.compile(r".+\.([\d]{3,})")

            for obj in decals:
                mo = countRegex.match(obj.name)

                # collect the counters
                if mo:
                    count = mo.group(1)
                    counters.append(int(count))

            if counters:
                decalobj.name = "%s.%s" % (decalname, str(max(counters) + 1).zfill(3))

            # set the first count manually
            else:
                decalobj.name = decalname + ".001"


        # the very first panel decal of its kind gets no counter, just the decalname
        else:
            decalobj.name = decalname

        # name the mesh as well
        decalobj.data.name = decalobj.name


# ALL TYPES

def align_decal(decalobj, scene, depsgraph, force_cursor_align=False):
    """
    1. scale the decal according to the individualscales prop or the globalscale prop
    2. set the default decal height
    3. align the decal location and rotation to the cursor
    """

    dm = scene.DM
    wm = bpy.context.window_manager
    view = bpy.context.space_data

    # set scale according to stored scale in individualscales scene prop
    if decalobj.DM.uuid in dm.individualscales:
        decalobj.scale = dm.individualscales[decalobj.DM.uuid].scale

    # set scale based on globalscale scene prop
    elif dm.globalscale != 1:
        decalobj.scale *= scene.DM.globalscale

    depsgraph.update()

    # set decal height
    displace = get_displace(decalobj)

    if displace:
        displace.mid_level = scene.DM.height


    # set location and rotation according to the cursor
    if dm.align_mode == "CURSOR" or force_cursor_align or (view.region_3d.view_perspective == 'CAMERA' and scene.camera.data.type == 'ORTHO'):
        decalobj.location = bpy.context.scene.cursor.location
        bpy.context.scene.cursor.rotation_mode = "QUATERNION"
        decalobj.rotation_mode = "QUATERNION"
        decalobj.rotation_quaternion = bpy.context.scene.cursor.rotation_quaternion

    # set location and rotation via raycast from the mouse
    elif dm.align_mode == "RAYCAST":
        mousepos = wm.decal_mousepos

        # for performance, do it in 2 passes, first all visible objects, original meshes
        # hitobj, loc, normal, _, _ = cast_bvh_ray_from_mouse(mousepos, exclude_decals=True, debug=True)

        # # then a second ray to the evaluated mesh of the best previus
        # if hitobj:
            # hitobj, loc, normal, _, _ = cast_bvh_ray_from_mouse(mousepos, candidates=[hitobj], depsgraph=depsgraph, exclude_decals=False, debug=True)

        # obj raycast seems faster and is on evaluated objects
        hitobj, loc, normal, _, _ = cast_obj_ray_from_mouse(mousepos, exclude_decals=False, debug=False)

        _, _, sca = decalobj.matrix_world.decompose()

        scamx = get_sca_matrix(sca)

        # object was hit, align to normal and intersection point
        if hitobj:
            rotmx = create_rotation_matrix_from_normal(hitobj, normal, loc, debug=False)
            decalobj.matrix_world = Matrix.Translation(loc) @ rotmx @ scamx

        # nothing was hit, align to grid intersection point
        else:
            loc, rotmx = get_grid_intersection(mousepos)
            decalobj.matrix_world = Matrix.Translation(loc) @ rotmx @ scamx


def apply_decal(decalobj, target=None, raycast=False, force_automatch=False):
    """
    1. Make sure decalobj has displace and normal transfer mods
    2. raycast/find_nearest from the decal to find a target object, unless one is explicitely passed in
    3. if one is found, set the hit obj as the decal's normal source
    4. also, parent the decal to the hit obj
    5. and finally, auto match the decal to the material at the hit location
    """

    # add modifiers
    displace = get_displace(decalobj)
    nrmtransfer = get_nrmtransfer(decalobj)

    if not displace:
        displace = add_displace(decalobj)

    if not nrmtransfer:
        nrmtransfer = add_nrmtransfer(decalobj)

    dm = bpy.context.scene.DM

    # find nearest from the bounding box center of the projected decal geo
    if decalobj.DM.isprojected:
        origin = get_origin_from_object_boundingbox(decalobj)

        if target:
            targets = [target]

        else:
            targets = [decalobj.DM.projectedon] if decalobj.DM.projectedon else [decalobj.parent] if decalobj.parent else [obj for obj in bpy.context.visisble_objects if obj.type == "MESH" and not obj.DM.isdecal]

        # then find the nearest polygon on the target and match its material
        target, _, _, faceidx, _ = find_nearest(targets, origin)

    # find nearest from the first face of the sliced decal
    elif decalobj.DM.issliced:
        origin, direction = get_origin_from_face(decalobj)

        if target:
            targets = [target]

        else:
            targets = [decalobj.DM.slicedon] if decalobj.DM.slicedon else [decalobj.parent] if decalobj.parent else [obj for obj in bpy.context.visisble_objects if obj.type == "MESH" and not obj.DM.isdecal]

        # then find the nearest polygon on the target and match its material
        target, _, _, faceidx, _ = find_nearest(targets, origin)

    # cast ray from the decal obj to find target object and faceidx
    else:
        # for InsertDecal() we want to use a raycast, this is to prevent auto matching to near objects, when decals aren't inserted on top an object
        if raycast:
            target, _, _, faceidx, _ = cast_bvh_ray_from_object(decalobj, (0, 0, -1), backtrack=0.01)

        # for other cases, find nearest is better suited and a safer choice
        else:
            origin, _ = get_origin_from_object(decalobj)

            if target:
                targets = [target]

            else:
                targets = [obj for obj in bpy.context.visible_objects if obj.type == "MESH" and not obj.DM.isdecal]

            target, _, _, faceidx, _ = find_nearest(targets, origin)


    if target and faceidx is not None:

        # set the normal transfer source obj
        if nrmtransfer.object != target:
            nrmtransfer.object = target

        # set the shrinkwrap target
        shrinkwrap = get_shrinkwrap(decalobj)
        if shrinkwrap:
            if shrinkwrap.target != target:
                shrinkwrap.target = target

        # parent
        if decalobj.parent != target:
            parent(decalobj, target)

        # update projectedon and slicedon properties if necessary
        if decalobj.DM.isprojected:
            if decalobj.DM.projectedon != target:
                decalobj.DM.projectedon = target

        if decalobj.DM.issliced:
            if decalobj.DM.slicedon != target:
                decalobj.DM.slicedon = target

        # auto match material
        if (dm.auto_match == "AUTO" or force_automatch) and decalobj.active_material and decalobj.DM.decaltype in ["SIMPLE", "SUBSET", "PANEL"]:
            auto_match_material(decalobj, decalobj.active_material, matchobj=target, face_idx=faceidx)

        elif dm.auto_match == "MATERIAL" and decalobj.DM.decaltype in ["SIMPLE", "SUBSET", "PANEL"]:
            auto_match_material(decalobj, decalobj.active_material, matchmatname=bpy.context.window_manager.matchmaterial)

        return True

    elif dm.auto_match == "MATERIAL" and decalobj.DM.decaltype in ["SIMPLE", "SUBSET", "PANEL"]:
        auto_match_material(decalobj, decalobj.active_material, matchmatname=bpy.context.window_manager.matchmaterial)


def set_defaults(decalobj=None, decalmat=None):
    dm = bpy.context.scene.DM

    if decalobj:

        # SHADOWS and DIFFUSE RAYS

        decalobj.cycles_visibility.shadow = False
        decalobj.cycles_visibility.diffuse = False


        # GLOSSY RAYS

        glossyrays = dm.glossyrays

        if decalobj.cycles_visibility.glossy != glossyrays:
            decalobj.cycles_visibility.glossy = glossyrays


        # NORMAL TRANSFER

        mod = get_nrmtransfer(decalobj)

        if mod:
            render = dm.normaltransfer_render
            viewport = dm.normaltransfer_viewport

            if mod.show_render != render:
                mod.show_render = render

            if mod.show_viewport != viewport:
                mod.show_viewport = viewport


    if decalmat:

        decalgroup = get_decalgroup_from_decalmat(decalmat)
        parallaxgroup = get_parallaxgroup_from_decalmat(decalmat)
        nrmnode = get_decal_texture_nodes(decalmat).get("NRM_ALPHA")
        colornode = get_decal_texture_nodes(decalmat).get("COLOR_ALPHA")
        textures = get_decal_textures(decalmat)


        # PARALLAX

        parallax = dm.parallax

        if parallaxgroup and parallaxgroup.mute == parallax:
            parallaxgroup.mute = not parallax


        # NORMAL INTERPOLATION

        interpolation = dm.normalinterpolation

        if nrmnode and nrmnode.interpolation != interpolation:
            nrmnode.interpolation = interpolation


        # COLOR INTERPOLATION

        interpolation = dm.colorinterpolation

        if colornode and colornode.interpolation != interpolation:
            colornode.interpolation = interpolation

        # ALPHA BLEND MODE

        blendmode = dm.alpha_blendmode

        if decalmat.blend_method != blendmode:
            decalmat.blend_method = blendmode


        # AO STRENGTH

        ao = dm.ao_strength

        if decalgroup:
            i = decalgroup.inputs.get("AO Strength")

            if i and i.default_value != ao:
                i.default_value = ao


        # INVERT

        invert = dm.invert_infodecals

        if decalgroup:
            i = decalgroup.inputs.get("Invert")

            if i and i.default_value != invert:
                i.default_value = invert


        # EDGE HIGHLIGHTS

        highlights = float(dm.edge_highlights)

        if decalgroup:
            i = decalgroup.inputs.get("Edge Highlights")

            if i and i.default_value != highlights:
                i.default_value = highlights


        # HIDE/SHOW MATERIAL

        hide = dm.hide_materials

        if hide:
            if not decalmat.name.startswith("."):
                decalmat.name = ".%s" % decalmat.name

        else:
            if decalmat.name.startswith("."):
                decalmat.name = decalmat.name[1:]


        # HIDE/SHOW MATERIAL

        hide = dm.hide_materials

        if hide:
            if not decalmat.name.startswith("."):
                decalmat.name = ".%s" % decalmat.name

        else:
            if decalmat.name.startswith("."):
                decalmat.name = decalmat.name[1:]


        # HIDE/SHOW TEXTURES

        if textures:
            hide = dm.hide_textures

            for img in textures.values():
                if hide:
                    if not img.name.startswith("."):
                        img.name = ".%s" % decalmat.name

                else:
                    if img.name.startswith("."):
                        img.name = decalmat.name[1:]


# PANEL

def get_panel_width(obj, scene):
    """
    returns panel width in obj's local space, from the panelwidth scene prop
    """
    dm = scene.DM

    mxi = obj.matrix_world.inverted()

    return (Vector((0, 0, dm.panelwidth * dm.globalscale)) @ mxi).length


def get_panel_width_from_edge(obj, edge):
    """
    returns panel width in world space, from an bmesh edge
    """
    mx = obj.matrix_world
    # return (mx.to_3x3() @ (edge.verts[1].co - edge.verts[0].co)).length
    return (mx.to_3x3() @ (edge.verts[1].co - edge.verts[0].co)).length * bpy.context.scene.DM.globalscale


def sort_panel_geometry(bm, debug=False):
    """
    sorts quad panel geometry into sequences/islands, and each sequence into a (face, edge) list
    used by Topo Slice and Panel Unwrap. Float Sliced creates the same output natively.
    """
    geo_sequences = []

    faces = [f for f in bm.faces]
    boundary_edges = [e for e in bm.edges if not e.is_manifold]

    # check if the panel is one or multiple single faces, we need to fallback to using edge length to determine the ends in that case
    if len(boundary_edges) == 4 * len(faces):

        ends = []

        for f in faces:
            edge_lengths = sorted([(e, e.calc_length()) for e in f.edges], key=lambda x: x[1])
            for e, _ in edge_lengths[0:2]:
                ends.append(e)

        rail_edges = ends

    # multi face quad panels
    else:
        ends = [e for e in boundary_edges if all(len(v.link_edges) == 2 for v in e.verts)]
        rail_edges = [e for e in bm.edges if e not in boundary_edges] + ends


    # non-cyclic panel, pick end edge as starting edge, cyclic panel, pick any rail edge
    edge = ends[0] if ends else rail_edges[0]
    loop = edge.link_loops[0]
    face = loop.face

    geo = [(face, edge)]

    while faces:
        if debug:
            print("face:", face.index, "edge:", edge.index, "loop:", loop)

        # smooth face, while iterating over all of them
        face.smooth = True

        # remove face and current rail edge from lists, to track what has been iterated over
        faces.remove(face)
        rail_edges.remove(edge)
        if edge in ends:
            ends.remove(edge)

        # get next loop, and from it the next rail edge and face
        while True:
            loop = loop.link_loop_next

            # we've reached the end of a sequence, it's either cyclic or not
            if loop.edge in ends or loop.edge == geo[0][1]:

                # it's the current edge, meaning we've looped around the entire face and so reached the end of a non-cyclic panel
                if loop.edge in ends:
                    cyclic = False
                    ends.remove(loop.edge)

                # it's the first edge of the current sequence, meaning we've completetly iterated over a cyclic panel
                elif loop.edge == geo[0][1]:
                    cyclic = True

                if debug:
                    print("cyclic:", cyclic)

                geo_sequences.append((geo, cyclic))

                # check if there are faces (of other sequences) left and if so, start over
                # TODO: this should fail for multiple non-cyclic sequences, repeat what you did above instead
                if faces:
                    edge = ends[0] if ends else rail_edges[0]
                    loop = edge.link_loops[0]
                    face = loop.face

                    geo = [(face, edge)]

                break

            # it's a new rail edge, repeat the process
            elif loop.edge.is_manifold:

                loop = loop.link_loop_radial_next
                face = loop.face
                edge = loop.edge

                geo.append((face, edge))

                break

    return geo_sequences


def create_panel_uvs(bm, geo_sequences, panel, width=None):
    """
    create panel uvs from quad panel geometry
    """
    uvs = bm.loops.layers.uv.verify()

    for geo, cyclic in geo_sequences:
        u_start = 0
        u_end = 0

        # get width from second rail edge, unless it is passed in directly, as in the case of Slice
        if not width:
            # NOTE: passing in second edge, because the the first one may be tapered!
            # there is no second face to take an edge from, however in cases of single quad panels
            width_edge = geo[1][1] if len(geo) > 1 else geo[0][1]
            width = get_panel_width_from_edge(panel, width_edge)

        for gidx, (face, edge) in enumerate(geo):
            # next edge in cyclic panels
            if cyclic:
                edge_next = geo[0][1] if gidx == len(geo) - 1 else geo[gidx + 1][1]

            # next edges of non-cyclic panels need to be determined differently
            else:
                # only one face
                if len(geo) == 1:
                    edge_next = [e for e in face.edges if not any(v in edge.verts for v in e.verts)][0]

                # last face
                elif gidx == len(geo) - 1:
                    edge_next = [e for e in face.edges if all(len(v.link_edges) == 2 for v in e.verts)][0]

                # any other is the same as for cyclic panels
                else:
                    edge_next = geo[0][1] if gidx == len(geo) - 1 else geo[gidx + 1][1]


            # determine distance between rail edge midpoints
            midpoint = (edge.verts[0].co + edge.verts[1].co) / 2
            midpoint_next = (edge_next.verts[0].co + edge_next.verts[1].co) / 2

            # the bigger the width, the shorter the distance(and with it total length) should be, proportionally
            distance_local = (midpoint - midpoint_next).length * 1 / width

            # make sure it's in world space
            distance_world = (panel.matrix_world.to_3x3() @ Vector((distance_local, 0, 0))).length

            u_end += distance_world

            # find a common starting point, independent of the vertex order of a face, so it will work for float and slice panels alike
            loop = [l for l in edge.link_loops if l.face == face][0]

            maxvstart = maxvend = 1
            minvstart = minvend = 0

            # check for tapered ends in non-cyclic panels, and adjust vmin and vmax accordingly
            if not cyclic:
                # fist edge is tapered
                if gidx == 0:
                    ratio = edge.calc_length() / edge_next.calc_length()
                    if ratio < 1 / 3:
                        maxvstart = 0.5 + ratio / 2
                        minvstart = 0.5 - ratio / 2

                # last edge is tapered
                elif gidx == len(geo) - 1:
                    ratio = edge_next.calc_length() / edge.calc_length()
                    if ratio < 1 / 3:
                        maxvend = 0.5 + ratio / 2
                        minvend = 0.5 - ratio / 2

            for i in range(4):
                if i == 0:
                    loop[uvs].uv = (u_start, maxvstart)
                elif i == 1:
                    loop[uvs].uv = (u_start, minvstart)
                elif i == 2:
                    loop[uvs].uv = (u_end, minvend)
                elif i == 3:
                    loop[uvs].uv = (u_end, maxvend)

                loop = loop.link_loop_next

            u_start = u_end


    bm.to_mesh(panel.data)
    bm.clear()


def change_panel_width(bm, amount, panel=None, scene=None, set_props=False):
    """
    change quand panel width by scaling the rall edges, an amount of 1 means no change
    also sets the panelwidth scene prop if desired
    """
    boundary_edges = [e for e in bm.edges if not e.is_manifold]


    # check if the panel is one or multiple single faces, we need to fallback to using edge length to determine the ends in that case
    if len(boundary_edges) == 4 * len(bm.faces):
        ends = []

        for f in bm.faces:
            edge_lengths = sorted([(e, e.calc_length()) for e in f.edges], key=lambda x: x[1])
            for e, _ in edge_lengths[0:2]:
                ends.append(e)

    # multi face quad panels
    else:
        ends = [e for e in boundary_edges if all(len(v.link_edges) == 2 for v in e.verts)]

    rail_edges = [e for e in bm.edges if e.is_manifold] + ends

    for idx, e in enumerate(rail_edges):
        avg = (e.verts[0].co + e.verts[1].co) / 2

        for v in e.verts:
            v.co = avg + (v.co - avg) * amount

        # use rail edge to calculate panel width in world space and independent of object scale, set the panelwidth scene prop accordlingly
        if idx == 0 and panel and scene and set_props:
            scene.DM.panelwidth = get_panel_width_from_edge(panel, e)


def create_float_slice_geometry(bm, mx, sequences, normals, width, debug=False):
    geo_sequences = []

    for seq, cyclic in sequences:
        geo = []

        for idx, v in enumerate(seq):
            # get prev and next verts to determine the direction vector
            prevv = seq[-1] if idx == 0 else seq[idx -1]
            nextv = seq[0] if idx == len(seq) - 1 else seq[idx + 1]

            normal = normals[v].normalized()

            # cyclic direction vector based on previous and next verts
            if cyclic:
                direction = (prevv.co - nextv.co).normalized()

            # for non-cyclic sequences, the first and last vertices need to be treated differently
            else:
                # first vert
                if idx == 0:
                    direction = (v.co - nextv.co).normalized()

                # last vert
                elif idx == len(seq) - 1:
                    direction = (prevv.co - v.co).normalized()

                # inbetween verts are the same as for cyclic
                else:
                    direction = (prevv.co - nextv.co).normalized()

            # the cross product of normal and direction is the panel rail edge direction
            cross = direction.cross(normal).normalized()

            if debug:
                draw_vector(normal * 0.1, origin=mx @ v.co, color=(1, 0, 0))
                draw_vector(direction * 0.05, origin=mx @ v.co, color=(0, 0, 1))
                draw_vector(cross * 0.05, origin=mx @ v.co, color=(0, 1, 0))

            # panel rail verts
            v1 = bm.verts.new()
            v1.co = v.co + cross * width / 2

            v2 = bm.verts.new()
            v2.co = v.co - cross * width / 2


            # skip face creation on the very first vert
            if idx == 0:
                prevv1 = firstv1 = v1
                prevv2 = firstv2 = v2
                continue

            # build faces
            f = bm.faces.new((v1, prevv1, prevv2, v2))
            f.smooth = True

            geo.append((f, bm.edges.get((prevv1, prevv2))))

            # at the very end of a cyclic sequence, build a second face to close the loop
            if cyclic and idx == len(seq) - 1:
                f = bm.faces.new((firstv1, v1, v2, firstv2))
                f.smooth = True

                geo.append((f, bm.edges.get((v1, v2))))

            # otherwise prepare the prev verts for the next iteration
            else:
                prevv1 = v1
                prevv2 = v2

        geo_sequences.append((geo, cyclic))

    return geo_sequences


def finish_panel_decal(context, panel, target, cutter):
    dm = context.scene.DM

    # parent panel to target
    parent(panel, target)

    # set basic panel obj props
    panel.DM.isdecal = True
    panel.DM.issliced = True
    panel.DM.slicedon = target
    panel.DM.decalbackup = cutter
    panel.DM.decaltype = "PANEL"

    # turn off shadow casting and diffuse rays
    panel.cycles_visibility.shadow = False
    panel.cycles_visibility.diffuse = False

    # determine "current panel decal" by checking the window_manager enum
    uuid = context.window_manager.paneldecals

    # get matet from blend file or append if necessary, if appended deduplicate
    mat, appended, library, name = get_panel_material(uuid)

    if mat:
        # set node names and props of the panel obj, the appended material and textures
        if appended:
            set_props_and_node_names_of_library_decal(library, name, decalobj=panel, decalmat=mat)

            # set material defaults
            set_defaults(decalmat=mat)

        # set additional panel obj props, based on the existing material
        else:
            set_decalobj_props_from_material(panel, mat)

        # apply the material
        panel.data.materials.append(mat)

        # and set the panel obj name
        set_decalobj_name(panel, decalname=mat.DM.decalname, uuid=mat.DM.uuid)

        # auto match the material
        if mat.DM.decaltype != 'INFO':
            automatch = dm.auto_match

            if automatch == "AUTO":
                # auto match material, by taking the first face of the panel strip as the origin
                origin, direction = get_origin_from_face(panel)

                # then find the nearest polygon on the target and match its material
                _, _, _, index, _ = find_nearest([target], origin)

                if index is not None:
                    auto_match_material(panel, mat, matchobj=target, face_idx=index)

            elif automatch == "MATERIAL":
                auto_match_material(panel, mat, matchmatname=context.window_manager.matchmaterial)

    # displace
    add_displace(panel)

    # normal tranfer
    add_nrmtransfer(panel, target)

    # set object defaults
    set_defaults(decalobj=panel)

    # lock transforms
    lock(panel)

    if cutter:
        # turn the cutter into a decal backup
        cutter.use_fake_user = True
        cutter.DM.isbackup = True

        unlink_object(cutter)

        # store the backup's matrix in target's local space
        cutter.DM.backupmx = flatten_matrix(target.matrix_world.inverted() @ cutter.matrix_world)


# DECAL ASSETS


def save_uuid(path, uuid, legacy=False):
    if legacy:
        path = os.path.join(os.path.splitext(path)[0] + ".uuid")

    else:
        path = os.path.join(path, "uuid")

    with open(path, "w") as f:
        f.write(uuid)


def save_blend(obj, path, scene):
    # make sure the decal is not parented
    obj.parent = None

    # disable shadow casting and diffuse rays
    obj.cycles_visibility.shadow = False
    obj.cycles_visibility.diffuse = False

    # put the decal into the origin and scale and rotate it properly
    obj.matrix_world = Matrix.Identity(4)

    # reset the displace height
    displace = get_displace(obj)
    if displace:
        displace.mid_level = 0.9999

    # write decal blend file
    bpy.data.libraries.write(filepath=os.path.join(path, "decal.blend"), datablocks={scene}, relative_remap=True)

    # remove decal asset scene
    bpy.data.scenes.remove(scene, do_unlink=True)


def render_thumbnail(context, decalpath, decal, decalmat, tint=(0.14, 0.15, 0.16, 1), size=None, removeall=True):
    templatepath = os.path.join(get_path(), "resources", "Templates.blend")

    thumbscene = append_scene(templatepath, "Thumbnail")
    context.window.scene = thumbscene

    bg = thumbscene.world.node_tree.nodes.get('Background')

    if bg:
        bg.inputs[0].default_value = tint

    thumbscene.collection.objects.link(decal)

    context.view_layer.objects.active = decal
    decal.select_set(True)

    if size:
        res = max(size)
        width = (128 / res) * size[0] / 1000

    else:
        size = [int(d * 1000) for d in decal.dimensions[:2]]

        # need to get the width, after the decal is resized
        width = None

    factor = 1 / (max(s for s in size) / 128)

    bpy.ops.transform.resize(value=[factor] * 3)

    # force scene update
    bpy.ops.transform.translate()


    # for panel decals, duplicate the decal two times to each side
    paneldups = []

    if decalmat.DM.decaltype == "PANEL":
        if not width:
            width = decal.dimensions[0]

        for i in [-2, -1, 1, 2]:
            dup = decal.copy()
            dup.data = decal.data.copy()
            paneldups.append(dup)

            dup.matrix_world.translation.x += width * i
            thumbscene.collection.objects.link(dup)


    # change the camera and dim one light for info decals
    if decalmat.DM.decaltype == "INFO":
        thumbscene.camera = bpy.data.objects['Camera_INFO']

        dim = bpy.data.objects.get('Dim')
        dim.data.energy = 0.5

    else:
        thumbscene.camera = bpy.data.objects['Camera_NORMAL']


    # set render output filename
    thumbscene.render.filepath = os.path.join(decalpath, "decal.png")

    # render thumbnail
    bpy.ops.render.render(write_still=True)

    # allways remove panel duplicates
    for dup in paneldups:
        bpy.data.meshes.remove(dup.data, do_unlink=True)

    # optionally remove everything else
    if removeall:
        bgmat = bpy.data.materials.get('THUMBNAILBG')
        if bgmat:
            bpy.data.materials.remove(bgmat, do_unlink=True)

        remove_decalmat(decalmat, remove_textures=True)

        for obj in thumbscene.objects:
            if obj.type == "MESH":
                bpy.data.meshes.remove(obj.data, do_unlink=True)

            elif obj.type == "CAMERA":
                bpy.data.cameras.remove(obj.data, do_unlink=True)

            elif obj.type == "LIGHT":
                bpy.data.lights.remove(obj.data, do_unlink=True)

    # remove the render scene and world
    bpy.data.worlds.remove(thumbscene.world, do_unlink=True)
    bpy.data.scenes.remove(thumbscene, do_unlink=True)
