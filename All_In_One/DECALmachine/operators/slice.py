import bpy
import bmesh
from mathutils.bvhtree import BVHTree as BVH
from .. utils.mesh import hide, unhide
from .. utils.object import intersect, flatten, parent, update_local_view, lock
from .. utils.decal import set_props_and_node_names_of_library_decal, set_decalobj_props_from_material, set_decalobj_name, set_defaults
from .. utils.decal import get_panel_width, create_panel_uvs, change_panel_width, sort_panel_geometry, create_float_slice_geometry, finish_panel_decal
from .. utils.raycast import find_nearest_normals
from .. utils.modifier import add_displace, add_nrmtransfer
from .. utils.material import get_panel_material, auto_match_material
from .. utils.raycast import get_origin_from_face, find_nearest, shrinkwrap
from .. utils.ui import popup_message
from .. utils.collection import unlink_object, get_decaltype_collection, sort_into_collections
from .. utils.addon import gp_add_to_edit_mode_group


# TODO: multi object slicing?
# TODO: separate panels if there are multiple seqiemces?
# TODO: deal with mirrors like in project?


class Slice(bpy.types.Operator):
    bl_idname = "machin3.slice_decal"
    bl_label = "MACHIN3: Slice Decal"
    bl_description = "Create Panel Decal at Intersection of Two Objects.\nALT: Topo Slice, use target object's topology\nSHIFT: Create Smoothed Panel Decal\nCTRL: Create Subdivided and Smoothed Panel Decal"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        col = layout.column()

    @classmethod
    def poll(cls, context):
        nondecals = [obj for obj in context.selected_objects if not obj.DM.isdecal]
        return len(nondecals) == 2 and context.active_object in nondecals

    def invoke(self, context, event):
        nondecals = [obj for obj in context.selected_objects if not obj.DM.isdecal]

        target = context.active_object
        nondecals.remove(target)
        cutter = nondecals[0]

        sliced = self.slice(context, event, target, cutter)

        if not sliced:
            msg = ["Slicing failed!"]

            msg.append("Try re-positioning the cutter, make sure it intersects the object you want to slice.")
            msg.append("Also, make sure you aren't using Topo-Slice (ALT pressed) on geometry that's unsuited for it.")

            popup_message(msg)

        return {'FINISHED'}

    def slice(self, context, event, target, cutter):
        """
        create panel decal
        """

        # parent the cutter to the target, so it will keep its relative position when brought back as a backup
        parent(cutter, target)

        # duplicate target mesh, which will become the projected decal after boolean
        panel = target.copy()
        panel.data = target.data.copy()
        panel.data.materials.clear()

        # link panel decal to master collection
        mcol = context.scene.collection
        mcol.objects.link(panel)

        dg = context.evaluated_depsgraph_get()

        # flatten it
        flatten(panel, dg)

        # hide panel and unhide cutter geo
        hide(panel.data)
        unhide(cutter.data)

        # create panel decal, either float (default) or topo (ALT pressed)
        panel = self.topo_slice(context, mcol, panel, cutter) if event.alt else self.float_slice(context, dg, event, panel, cutter)

        """
        cutter.hide_set(True)
        target.hide_set(True)
        panel.select_set(True)
        context.view_layer.objects.active = panel
        # """

        # """
        # set decal props, get or append material and apply it, add modes, parent, etc
        if panel:
            # finsh the panel
            finish_panel_decal(context, panel, target, cutter)

            # sort panel into collections
            sort_into_collections(context.scene, panel)

            # deselect, select and make active
            target.select_set(False)
            panel.select_set(True)
            context.view_layer.objects.active = panel

            # add edit mode group
            gp_add_to_edit_mode_group(context, panel)

            # local view update
            update_local_view(context.space_data, [(panel, True)])

            return True

        return
        # """

    def topo_slice(self, context, collection, panel, cutter):
        """
        create topological panel decal
        """

        def create_topo_slice_geometry(count, obj, flat_target):
            def get_dirty_panel_ends(bm):
                """
                get end edges in non-cyclic geometry
                """

                # check if the panel is one or multiple single faces, we need to fallback to using edge length to determine the ends in that case
                boundary_edges = [e for e in bm.edges if not e.is_manifold]

                if len(boundary_edges) == 4 * len(bm.faces) and all(len(f.verts) == 4 for f in bm.faces):
                    ends = []

                    for f in bm.faces:
                        edge_lengths = sorted([(e, e.calc_length()) for e in f.edges], key=lambda x: x[1])
                        for e, _ in edge_lengths[0:2]:
                            ends.append(e)

                # otherwise, use triangulation to determine ends
                else:

                    # triangulate the mesh, to get rid of all ngons
                    bmesh.ops.triangulate(bm, faces=bm.faces, quad_method='BEAUTY', ngon_method='BEAUTY')

                    # only one vert on each end of a non-cylclic panel will now have 2 connecting (non-manofild) edges
                    end_verts = [v for v in bm.verts if len(v.link_edges) == 2 and sum(not e.is_manifold for e in v.link_edges) == 2]

                    ends = []
                    for v in end_verts:
                        for e in v.link_edges:
                            otherv = e.other_vert(v)

                            # find the other vert of the end edge
                            if len(otherv.link_edges) == 3 and sum(not e.is_manifold for e in otherv.link_edges) == 2:
                                ends.append(e)

                return ends

            def create_quad_panel_geometry(bm, ends):
                sequences = []
                ends_seen = ends.copy()

                faces = [f for f in bm.faces]
                # NOTE: these aren't real rail edges, they are inside edges + ends
                rail_edges = [e for e in bm.edges if e.is_manifold] + ends

                edge = ends[0] if ends else rail_edges[0]
                loop = edge.link_loops[0]
                face = loop.face

                seq = [(face, edge, [e for e in face.edges if not e.is_manifold and e not in rail_edges])]

                # print("ends:", [e.index for e in ends])
                # print("left over faces:", [f.index for f in faces])

                while faces:
                    # print("face:", face.index, "edge:", edge.index, "loop:", loop)

                    # this avoids the rare issue in 114_slice_fail.blend
                    if face in faces and edge in rail_edges:
                        faces.remove(face)
                        rail_edges.remove(edge)

                    else:
                        return []

                    if edge in ends_seen:
                        ends_seen.remove(edge)

                    while True:
                        loop = loop.link_loop_next

                        # reached end of seqeuence
                        if loop.edge in ends_seen or loop.edge == seq[0][1]:

                            # non-cyclic panel
                            if loop.edge in ends_seen:
                                cyclic = False
                                # print("found end edge:", loop.edge)
                                ends_seen.remove(loop.edge)

                            # cyclic sequence
                            elif loop.edge == seq[0][1]:
                                cyclic = True
                                # print("found start edge:", loop.edge)

                            # never reaching this point for non-cyclic panels
                            # print("cyclic:", cyclic)

                            sequences.append((seq, cyclic))

                            if faces:
                                # print("ends:", [e.index for e in ends])
                                # print("left over faces:", [f.index for f in faces])
                                # print("rail edges:", rail_edges)
                                edge = ends_seen[0] if ends_seen else rail_edges[0]
                                loop = edge.link_loops[0]
                                face = loop.face

                                seq = [(face, edge, [e for e in face.edges if not e.is_manifold and e not in rail_edges])]

                            break


                        # jump to the next face
                        elif loop.edge.is_manifold:
                            loop = loop.link_loop_radial_next
                            edge = loop.edge
                            face = loop.face

                            seq.append((face, edge, [e for e in face.edges if not e.is_manifold and e not in rail_edges]))
                            break

                # up to this point, we've found individual seqeunces of panel faces, panel rail edges and boundary edges(exlucing ends)
                # we are now blasing away what is not needed and bridge the boundary edges per sequences, which creates quad panel geometry

                # blast faces
                bmesh.ops.delete(bm, geom=bm.faces, context="FACES_KEEP_BOUNDARY")

                # blast ends
                bmesh.ops.delete(bm, geom=ends, context="EDGES")

                geo_sequences = []

                for seq, cyclic in sequences:
                    bounds = [edge for _, _, bounds in seq for edge in bounds]

                    # in rare cases, see 111_decal_slice_fail, the bright will fail, so just return an empty geo sequences, leading to a new iteration with smaller panel width
                    try:
                        geo = bmesh.ops.bridge_loops(bm, edges=bounds)
                    except:
                        return []

                    geo_sequences.append(geo)

                return geo_sequences

            bm = bmesh.new()
            bm.from_mesh(obj.data)

            # blast away visible faces(resulting from the boolean, not part of the panel)
            blastfaces = [f for f in bm.faces if not f.hide]
            bmesh.ops.delete(bm, geom=blastfaces, context="FACES_KEEP_BOUNDARY")

            # sometimes something with the boolean can go wrong and there will be no (hidden) panel faces, even though there were (visible) faces to blast away
            if not bm.faces:
                return

            # check for verts with more than one manifold edge. they are verts on the inside of the panel geo and need to be avoided
            v3s = [v for v in bm.verts if sum(e.is_manifold for e in v.link_edges) > 1]

            # check for tris
            if not v3s:
                f3s = [f for f in bm.faces if len(f.verts) == 3]

                if not f3s:
                    # get end edges in non-cyclic geometry
                    ends = get_dirty_panel_ends(bm)

                    # build clean quad panel geo
                    geo_sequences = create_quad_panel_geometry(bm, ends)

                    # check the resulting face normals against the target and flip them, if normal directions don't match
                    for geo in geo_sequences:
                        mxw = obj.matrix_world
                        face = geo['faces'][0]
                        origin = mxw @ face.calc_center_median()
                        normal = mxw.to_3x3() @ face.normal

                        _, _, target_normal, _, _ = find_nearest([flat_target], origin)

                        if normal.dot(target_normal) < 0:
                            bmesh.ops.reverse_faces(bm, faces=geo['faces'])

                    # check if triangles are found, which can sometimes happen with bridge
                    # if not then this is a sucessful panel decal
                    if not any(len(f.verts) == 3 for f in bm.faces):

                        # increase the panel width, unless this is the first run
                        if count > 0:
                            change_panel_width(bm, pow(2, count))

                        return bm

            # return None, try again with smaller panel width
            bm.clear()

        # to compare panel normals created via bridge, we need a flattened copy of the target, or just a copy of the panel decal before the intersection
        flat_target = panel.copy()
        flat_target.data = panel.data.copy()

        # determine panel width, enfore global width, independent of object scaling
        width = get_panel_width(cutter, context.scene)

        # you need to repeatedly solidify and boolean, until you have no triangels in the mesh anymore
        solidify = cutter.modifiers.new(name="Solidify", type="SOLIDIFY")
        solidify.offset = 0
        solidify.use_even_offset = True
        solidify.thickness = width

        # intersect
        intersect(panel, cutter)

        # """

        # try to create an all quad panel decal by repeatedly decreasing the panel width
        c = 0
        while True:

            candidate = panel.copy()
            candidate.data = panel.data.copy()
            collection.objects.link(candidate)
            flatten(candidate)

            # blast redundant geometry, check the rest for verts with 3 manifold edges and for faces with 3 verts, also bridge to create panel faces with proper rail edges
            bm = create_topo_slice_geometry(c, candidate, flat_target)

            # remove panel, the candidate becomes the new panel, continue below
            if bm:
                bpy.data.meshes.remove(panel.data, do_unlink=True)
                panel = candidate

                # remove the solidify mod from the cutter again
                cutter.modifiers.remove(solidify)
                break

            # failed to find a proper panel, reseting to pre slice state and exit slice()
            elif bm is False or c > 10:
                bpy.data.meshes.remove(candidate.data, do_unlink=True)
                bpy.data.meshes.remove(panel.data, do_unlink=True)

                # remove the solidify mod again
                cutter.modifiers.remove(solidify)
                return

            # do another iteration with half panel width
            else:
                bpy.data.meshes.remove(candidate.data, do_unlink=True)

                c += 1
                solidify.thickness /= 2


        # remove the flattened obj again
        bpy.data.meshes.remove(flat_target.data, do_unlink=True)

        # """
        # sort the faces in the panel so they can be uved
        geo = sort_panel_geometry(bm)

        # create uvs and finsish bmesh
        create_panel_uvs(bm, geo, panel, width)
        # """
        return panel

    def float_slice(self, context, depsgraph, event, panel, cutter):
        """
        create floating panel decal
        """

        def check_cutter(cutter):
            bm = bmesh.new()
            bm.from_mesh(cutter.data)

            ismanifold = True
            for e in bm.edges:
                if not e.is_manifold:
                    ismanifold = False
                    break

            if not ismanifold:
                # select all the original faces, this will be used to blast everythign else on the panel and cutter
                for f in bm.faces:
                    f.select = True

                bmesh.ops.solidify(bm, geom=bm.faces, thickness=0.0001)
                bm.to_mesh(cutter.data)

            bm.free()
            return ismanifold

        def recreate_cutter(cutter):
            bm = bmesh.new()
            bm.from_mesh(cutter.data)

            faces = [f for f in bm.faces if not f.select]
            bmesh.ops.delete(bm, geom=faces, context="FACES")

            bm.to_mesh(cutter.data)
            bm.clear()

        def get_intersection_edge_loop(obj, ismanifold):
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bm.normal_update()
            bm.verts.ensure_lookup_table()

            if ismanifold:
                # blast all visible faces
                faces = [f for f in bm.faces if not f.hide]
                bmesh.ops.delete(bm, geom=faces, context="FACES_KEEP_BOUNDARY")

                # blast remaining hidden faces
                faces = [f for f in bm.faces if f.hide]
                bmesh.ops.delete(bm, geom=faces, context="FACES_KEEP_BOUNDARY")

            else:
                # blast the visible and selected faces
                faces = [f for f in bm.faces if not f.hide or f.select]
                bmesh.ops.delete(bm, geom=faces, context="FACES")

                # blast everything but the selected verts
                verts = [v for v in bm.verts if not v.select]
                bmesh.ops.delete(bm, geom=verts, context="VERTS")


            if len(bm.edges) == 0:
                return False

            # bm.to_mesh(obj.data)
            # bm.clear()

            return bm

        def sort_vertex_sequences(bm):
            verts = [v for v in bm.verts]
            intersection = verts.copy()
            sequences = []

            # if edge loops are non-cyclic, it matters at what vert you start the sorting
            noncyclicstartverts = [v for v in verts if len(v.link_edges) == 1]

            if noncyclicstartverts:
                v = noncyclicstartverts[0]

            # in cyclic edge loops, any vert works
            else:
                v = verts[0]

            seq = []

            while verts:
                seq.append(v)

                verts.remove(v)
                if v in noncyclicstartverts:
                    noncyclicstartverts.remove(v)

                nextv = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) not in seq]

                # next vert in sequence
                if nextv:
                    v = nextv[0]

                # finished a sequence
                else:
                    # determine cyclicity
                    cyclic = True if len(v.link_edges) == 2 else False

                    # store sequence and cyclicity
                    sequences.append((seq, cyclic))

                    # start a new sequence, if there are still verts left
                    if verts:
                        if noncyclicstartverts:
                            v = noncyclicstartverts[0]
                        else:
                            v = verts[0]

                        seq = []

            return sequences, intersection

        # to find the normals below, we need a flattened copy of the target, or just a copy of the panel decal before the intersection
        flat_target = panel.copy()
        flat_target.data = panel.data.copy()

        # check if cutter is manifold and if not, thicken it it, allowing for partially intersecting cuts by non-manifold geometry
        ismanifold = check_cutter(cutter)

        # intersect
        intersect(panel, cutter)

        # apply the boolean mod
        depsgraph.update()
        flatten(panel, depsgraph)

        # if the cutter was non-manifold, recreate the original again, by blasting everything but the original faces
        if not ismanifold:
            recreate_cutter(cutter)

        # remove everything but the intersection edge loop
        bm = get_intersection_edge_loop(panel, ismanifold)

        if not bm:
            bpy.data.meshes.remove(panel.data, do_unlink=True)
            return False

        # """
        # smooth or subdive and smooth the edge loop
        if len(bm.verts) > 2:

            # smooth once
            if event.shift:
                bmesh.ops.smooth_vert(bm, verts=bm.verts, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)

            # subdivide once + smooth 4 times
            elif event.ctrl:
                bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=1)

                for i in range(4):
                    bmesh.ops.smooth_vert(bm, verts=bm.verts, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)

        # """

        # """

        # TODO: remove 2 edge verts with angles of 180° ?
        # TODO: merge close by verts? determine distance by averaging all distances and dividing by 10 or similar?


        # build dictionary using panel decal vert ids as keys and normals on the flattened target mesh as values
        normals, bmt = find_nearest_normals(bm, flat_target.data)

        # remove the flattened obj again
        bpy.data.meshes.remove(flat_target.data, do_unlink=True)

        # we need to sort the vertices in the sequence they are connected to each other and determine cyclicity
        # there could be multiple loops, so we are going to create a list of sequences
        sequences, intersection = sort_vertex_sequences(bm)

        # determine panel width, enfore global width, independent of object scaling
        width = get_panel_width(panel, context.scene)

        # create panel faces
        geo = create_float_slice_geometry(bm, panel.matrix_world, sequences, normals, width=width)

        # blast the intersection edge loop
        bmesh.ops.delete(bm, geom=intersection, context="VERTS")

        # shrinkwrap
        shrinkwrap(bm, bmt)

        # create UVs and finish bmesh
        create_panel_uvs(bm, geo, panel, width=width)
        # """

        return panel
