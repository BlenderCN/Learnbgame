import bpy
from bpy.props import BoolProperty, IntProperty, FloatProperty, EnumProperty, StringProperty
import bmesh
import math
import mathutils
import os
from .. utils.developer import Benchmark
from .. utils.ui import popup_message
from .. utils.support import unparent, parent, add_vgroup
from .. utils.registration import set_new_plug_index, reload_plug_libraries
from .. utils.append import append_group, append_world, append_scene
from .. utils.normal import normal_clear, normal_transfer_from_obj, normal_clear_across_sharps
from .. utils import MACHIN3 as m3
from . stashes import create_stash
from uuid import uuid4


# TODO: can you do the knife intersection using bmesh? or atleast the solidify part

# TODO: transformations: scale x,y, move x,y
# TODO: draw the precision value by drawing the border verts of the handle?
# TODO: do custon normals on subsets?

# TODO: create group for subsets? for each plug(type)?

# TODO: update plug assets op -> take the blend files and set the group names

# TODO: if a plug has stashes, should they be cleared when addeing to library? tagged as isplugstash and clear tag isplug, then stashed for the plug receiver?

# TODO: ease up on plugging other plugs, it should probably be allowed
# ####: doing that removes any exising conform groups!

# TODO: boolean plugs?, dont deform, but can cut away across an edge

# TODO: you could add the ability to bevel the hard edges after the plug has been integrated.

# TODO: can you change the width of a panel cut using modifiers?



filletoredgeitems = [("FILLET", "Fillet", ""),
                     ("EDGE", "Edge", "")]


draw_edges = []


class Plug(bpy.types.Operator):
    bl_idname = "machin3.plug"
    bl_label = "MACHIN3: Plug"
    bl_options = {'REGISTER', 'UNDO'}

    contain = BoolProperty(name="Contain", default=False)
    contain_amnt = FloatProperty(name="Amount", default=0.07, min=0.001)

    filletoredge = EnumProperty(name="Fillet or Edge", items=filletoredgeitems, default="FILLET")

    # transformation
    offset = FloatProperty(name="Offset", default=0, min=-0.9, max=4, step=20)
    offset_dist = None

    rotation = FloatProperty(name="Rotation", default=0, step=100)

    # deformation
    deformation = BoolProperty(name="Deformation", default=True)
    deform_plug = BoolProperty(name="Deform Plug", default=False)
    deform_subsets = BoolProperty(name="Deform Subsets", default=False)
    deform_interpolation_falloff = FloatProperty(name="Interpolation Falloff (Surface Deform)", default=16, min=0)

    use_mesh_deform = BoolProperty(name="Mesh Deform", default=True)
    deformer_plug_precision = IntProperty(name="Plug Precision", default=4, min=0)
    deformer_subset_precision = IntProperty(name="Subset Precision", default=4, min=0)

    # face matching
    precision = IntProperty(name="Precision", default=2, min=0, max=5)

    # cleanup and polish
    dissolve_angle = FloatProperty(name="Dissolve Angle", default=1, min=0, step=50)
    normal_transfer = BoolProperty(name="Normal Transfer", default=False)

    show_wire = BoolProperty(name="Show Wire", default=False)
    fading_wire = BoolProperty(name="Fading Wire", default=True)

    # hidden
    init = BoolProperty(name="Initial Run", default=False)


    @classmethod
    def poll(cls, context):
        active = context.active_object
        if active:
            return not active.MM.isplughandle

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        # integration
        box = layout.box()
        box.label("Integration")

        # row = box.row()
        # row.prop(self, "filletoredge", expand=True)

        row = box.row()
        row.prop(self, "contain")

        # if self.contain:
            # row.prop(self, "contain_amnt")

        row = box.row()
        row.prop(self, "precision")
        if not self.contain:
            row.prop(self, "dissolve_angle")

        # transformation
        box = layout.box()
        box.label("Transformation")

        row = box.row()
        row.prop(self, "offset")
        row.prop(self, "rotation")

        # deformation
        box = layout.box()
        box.prop(self, "deformation")

        if self.deformation:
            if any([self.subsets, self.filletoredge == "EDGE", self.deformer]):

                # subset deformation
                row = box.split(percentage=0.4)
                if self.deformer:
                    row.prop(self, "use_mesh_deform", text="Use Deformer")

                # plug deformation
                if self.filletoredge == "EDGE":
                    row.prop(self, "deform_plug", text="Plug")

                # subset deformation
                if self.subsets:
                    row.prop(self, "deform_subsets", text="Subsets")

                # use mesh deform
                if self.deformer and self.use_mesh_deform:
                    if self.deformer_plug_precision > 4 or self.deformer_subset_precision > 4:
                        box.label("Careful, values above 4 are increasingly slow", icon="ERROR")

                    row = box.row()
                    row.prop(self, "deformer_plug_precision")
                    if self.subsets and self.deform_subsets:
                        row.prop(self, "deformer_subset_precision")

        # appeareance
        box = layout.box()
        box.label("Appereance")

        column = box.column()

        column.prop(self, "normal_transfer")

        row = column.row()
        row.prop(self, "show_wire")
        if m3.MM_prefs().plugfadingwire:
            if not self.show_wire:
                row.prop(self, "fading_wire")

    def execute(self, context):
        debug = False
        # debug = True

        T = Benchmark(True)

        if debug:
            m3.clear()

        # get the target, plug handle, plug, and subsets
        target, handle, plug, subsets, deformer, modifiers, others, err = self.get_plug(m3.selected_objects(), debug=debug)
        T.measure("get_plug")

        if err:
            popup_message(err[0], err[1])
            return {'FINISHED'}
        else:
            # create MM.plugscales scene prop entry to remember scale, NOTE: you can't run this in the init part, has to be run every redo, or it will be undone
            self.get_and_save_plug_scale(context.scene, handle, [o for o in others if o.type == "EMPTY"])

            # set the vertex group tool weight to 1, without it the normal transfer may not work as expected
            bpy.context.scene.tool_settings.vertex_group_weight = 1

            # create normal source
            nrmsrc = False
            if self.normal_transfer:
                nrmsrc = target.copy()
                nrmsrc.data = target.data.copy()

            # on the initial run set a few operator props for the current plug
            if self.init:
                self.set_operator_props(plug, subsets, deformer)

            T.measure("initialize props")

            # make sure xray is turned off for the subsets
            for sub in subsets:
                sub.show_x_ray = False

            # check mods for hooks and arrays and apply them
            self.apply_hooks_and_arrays(handle, plug, subsets, deformer, modifiers)
            T.measure("apply hooks")

            # remove others (empties, array caps, occluder)
            for obj in others:
                bpy.data.objects.remove(obj, do_unlink=True)
            T.measure("delete others")

            # rotate, offset
            self.transform(handle, plug, subsets, deformer, self.rotation, self.offset, debug=debug)
            T.measure("transform")

            # unparent plug and subsets, but only get the subs that are parented to the handle or plug mesh, this way any hierarchy among the subsets remains intact
            subs = [sub for sub in subsets if sub.parent == plug or sub.parent == handle]

            unparent([plug] + subs, debug=debug)
            T.measure("unparent")

            # parent subsets to target
            parent(subs, target, debug=debug)
            T.measure("parent")

            # create stash if necessary
            # if self.normal_transfer and not target.MM.stashes:
            if not target.MM.stashes:
                create_stash(active=target, source=target)
            T.measure("create_stash")

            # deform the plug to fit the surface perfectly, this is helpful to maintain a constant chamfer width
            # and also allows you to plug fully beveled/fused plugs IF the origin is at the very top of the bevel
            if self.deformation:
                self.deform(target, handle, deformer, plug, subsets, debug=debug)
            T.measure("deformation")

            # """
            if self.contain:
                self.contain_handle(target, handle, self.contain_amnt, self.precision, debug=debug)
            T.measure("contain_handle")

            # project border verts onto target surface
            if self.deformation:
                self.conform_verts_to_target_surface(plug, target, debug=debug)
            else:
                self.create_plug_vgroups(plug, push_back=True)
            T.measure("conform_verts_to_target_surface")

            # get target face ids
            face_ids = self.get_target_face_ids(handle, target, precision=self.precision, debug=debug)
            T.measure("get_target_face_ids")

            # join plug and target objs
            target.select = True
            plug.select = True
            m3.make_active(target)

            bpy.ops.object.join()
            T.measure("join")

            # merge plug and target meshes
            conform_vgroup, border_vgroup, container_vgroup, boundary_vgroup = self.merge_plug_into_target(target, face_ids, debug=debug)
            T.measure("merge_plug_into_target")

            # cleanup using limited dissolve and tris to quad
            nrm_vgroup = self.cleanup(target, deformer, conform_vgroup, border_vgroup, container_vgroup, boundary_vgroup, self.dissolve_angle, nrmsrc)
            T.measure("cleanup")

            # basic wire display
            target.show_wire = self.show_wire
            target.show_all_edges = self.show_wire
            T.measure("show_wire")

            # custom, modal, facding wire display, if show_wire is turned off
            if m3.MM_prefs().plugfadingwire:
                if not self.show_wire and self.fading_wire:
                    global draw_edges
                    draw_edges = self.modal_wire_display(target, nrm_vgroup)
                    # T.measure("drawing edges prep")

                    # draw the edges
                    try:
                        bpy.ops.machin3.draw_plug(countdown=3)
                    except:
                        pass

                draw_edges = []
            T.measure("modal_wire")

            T.total()
            # """

        return {'FINISHED'}

    def modal_wire_display(self, target, vgroup):
        bm = bmesh.new()
        bm.from_mesh(target.data)

        groups = bm.verts.layers.deform.verify()

        edges = []

        for e in bm.edges:
            for v in e.verts:
                if vgroup.index in v[groups]:
                    edges.append((v.index, e.other_vert(v).index))
                    break
        bm.clear()

        return edges

    def cleanup(self, target, deformer, conform_vgroup, border_vgroup, container_vgroup, boundary_vgroup, dissolve_angle, nrmsrc, debug=False):
        plug_vgroup = target.vertex_groups.get("plug")

        m3.set_mode("EDIT")

        if not container_vgroup:
            # its essential to run dissolve_lmited from face mode! otherwisee it may dissolve beyond the selection border
            m3.set_mode("FACE")
            target.vertex_groups.active_index = boundary_vgroup.index
            bpy.ops.object.vertex_group_select()
            bpy.ops.mesh.dissolve_limited(angle_limit=math.radians(self.dissolve_angle))
            bpy.ops.mesh.tris_convert_to_quads()


        # select conform verts
        target.vertex_groups.active_index = conform_vgroup.index
        bpy.ops.object.vertex_group_select()

        # when contain is True, the selection needs to go beyond the conform polygons
        if container_vgroup:
            # increase selection
            bpy.ops.mesh.select_more()

            # deselect the plug
            target.vertex_groups.active_index = plug_vgroup.index
            bpy.ops.object.vertex_group_deselect()

        normal_vgroup = add_vgroup(target, name="normal_transfer", debug=debug)

        # only do the actual normal transfer when self.normal_transfer is enabled
        if self.normal_transfer:
            normal_transfer_from_obj(target, nrmsrc, vgroup=normal_vgroup)
            m3.set_mode("OBJECT")

            if self.filletoredge == "EDGE":
                normal_clear_across_sharps(target)

        else:
            m3.set_mode("OBJECT")

        # remove the vertex groups
        target.vertex_groups.remove(conform_vgroup)
        target.vertex_groups.remove(border_vgroup)
        target.vertex_groups.remove(boundary_vgroup)
        target.vertex_groups.remove(plug_vgroup)

        if container_vgroup:
            target.vertex_groups.remove(container_vgroup)

        # remove leftovers
        if deformer:
            bpy.data.objects.remove(deformer, do_unlink=True)

        if self.normal_transfer:
            bpy.data.objects.remove(nrmsrc, do_unlink=True)

        return normal_vgroup

    def merge_plug_into_target(self, target, face_ids, debug=False):
        boundary_vgroup = target.vertex_groups.new("boundary")

        conform_vgroup = target.vertex_groups.get("conform")
        border_vgroup = target.vertex_groups.get("border")
        container_vgroup = target.vertex_groups.get("container")


        # create final target bmesh
        bm = bmesh.new()
        bm.from_mesh(target.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        groups = bm.verts.layers.deform.verify()

        # get faces from handle projectton
        faces = [f for f in bm.faces if f.index in face_ids]

        # when containing, you may have missed some small faces at the container cut, add these via selection flushing
        if container_vgroup:
            # iterating over all the faces, because its exrtremely important that nothign is selected that shouldnt
            for f in bm.faces:
                if f in faces:
                    f.select = True
                else:
                    f.select = False

            for v in bm.verts:
                if container_vgroup.index in v[groups]:
                    v.select = True

            bm.select_flush(True)

            faces = [f for f in bm.faces if f.select]

        # for f in faces:
            # f.select = False


        # get target face boundary edges
        boundary_edges = []
        for f in faces:
            # f.select = True
            for e in f.edges:
                if not all([f in faces for f in e.link_faces]):
                    boundary_edges.append(e)
                    # e.select = True

        # sort them
        # boundary_edges = self.sort_edges(boundary_edges, debug=True)

        # get plug border edges

        # get the verts from the vertex group
        border_verts = [v for v in bm.verts if border_vgroup.index in v[groups]]

        # then get the border edges from those verts
        border_edges = []
        for v in border_verts:
            for e in v.link_edges:
                if all([v in border_verts for v in e.verts]):
                    if e not in border_edges:
                        border_edges.append(e)
                        # e.select = True

        # sort them
        # border_edges = self.sort_edges(border_edges, debug=True)

        # delete the original faces
        # NOTE: the bridge tool below will mess up on single faces, if the origianl face is not deleted in advance
        bmesh.ops.delete(bm, geom=faces, context=5)

        # in some rare cases edges can be in the border and boundary lists, this needs to be avoided or the bridge ops will complain
        # the set method is ~ 5x as fast as the same done via a for loop btw
        if container_vgroup:
            bridge_edges = [e for e in list(set(boundary_edges + border_edges)) if e.is_valid]
        else:
            bridge_edges = [e for e in boundary_edges + border_edges if e.is_valid]

        # bridge the opening
        # interestingly depite deleting the faces, the bridging still works with the edges
        geo = bmesh.ops.bridge_loops(bm, edges=bridge_edges)

        # create the boundary vertex group and unsellect everything
        for f in bm.faces:
            if f in geo["faces"]:
                for v in f.verts:
                    v[groups][boundary_vgroup.index] = 1
            f.select = False

        bm.select_flush(False)

        if container_vgroup:
            self.remove_container_boundary(bm, groups, target, container_vgroup, conform_vgroup, border_vgroup, boundary_vgroup, debug=debug)

        bm.to_mesh(target.data)
        bm.clear()

        m3.set_mode("EDIT")

        return conform_vgroup, border_vgroup, container_vgroup, boundary_vgroup

    def remove_container_boundary(self, bm, groups, target, container_vgroup, conform_vgroup, border_vgroup, boundary_vgroup, debug=False):
        border_verts = []
        conform_verts = []
        container_verts = []
        boundary_verts = []

        for v in bm.verts:
            if border_vgroup.index in v[groups]:
                border_verts.append(v)

            if conform_vgroup.index in v[groups]:
                conform_verts.append(v)

            if container_vgroup.index in v[groups]:
                container_verts.append(v)

            if boundary_vgroup.index in v[groups]:
                boundary_verts.append(v)

        # there may be some verts that are part of the boundary but neither container nor border verts, the will have to be dissolved
        dissolve_verts = []
        for v in boundary_verts:
            if v not in border_verts and v not in container_verts:
                dissolve_verts.append(v)


        # from the container verts, find the shortest edge leading to a border vert and move the container vert to its location
        for v in container_verts:
            edges = [(e.calc_length(), e.other_vert(v)) for e in v.link_edges if e.other_vert(v) in border_verts]

            if edges:
                shortest = sorted(edges, key=lambda e: e[0])[0]
                v.co = shortest[1].co
            else:
                dissolve_verts.append(v)

        # merge the verts and so remove the gap between plug border and container cut
        bmesh.ops.remove_doubles(bm, verts=container_verts + border_verts, dist=0.00001)

        # dissolve the trouble makers
        bmesh.ops.dissolve_verts(bm, verts=dissolve_verts)


        # remove_doubles scrumbles the border and cointainer verts groups
        # the boundary vgroup now is the a perfect border vrgroup however

        # update the border vert list
        border_verts = [v for v in boundary_verts if v.is_valid]

        # update the border and conform vgroups as well
        for v in border_verts:
            # v.select = True
            v[groups][border_vgroup.index] = 1
            v[groups][conform_vgroup.index] = 1


        # moving and merging the cointainer verts to the border verts, may have produced edges slipping under some verts
        slipping_edges = []

        for v in border_verts:
            offset_edge = None

            # this list will be filled with edges of border verts, some of these edges are slipping edges, that need to be removed
            border_edges = []

            for e in v.link_edges:
                if e.other_vert(v) in border_verts:
                    border_edges.append(e)
                elif e.other_vert(v) in conform_verts:
                    offset_edge = e

            if offset_edge and len(border_edges) > 2:
                # print("vert:", v.index)
                # v.select = True

                # print("offset edge:", offset_edge.index)
                # offset_edge.select = True

                for l in offset_edge.link_loops:
                    if l.vert == v:
                        border_edge = l.link_loop_prev.edge
                    else:
                        border_edge = l.link_loop_next.edge

                    # border_edge.select = TrueA

                    # thie is a true border edge, remove it from the list
                    border_edges.remove(border_edge)

                # the remaining are sliping edges
                for e in border_edges:
                    # e.select = True
                    if e not in slipping_edges:
                        slipping_edges.append(e)

        # for e in slipping_edges:
            # e.select = True

        # remove the slipping edges
        bmesh.ops.dissolve_edges(bm, edges=slipping_edges)

    def sort_edges(self, edges, debug=False):
        unsorted_edges = [e for e in edges]

        if debug:
            print("unsorted edges:", [e.index for e in unsorted_edges])

        edge = unsorted_edges[0]
        vert = edge.verts[0]

        sorted_edges = [edge]
        unsorted_edges.remove(edge)

        # print("vert:", vert.index)
        # print("edge:", edge.index)
        # print("----")

        while unsorted_edges:
            next_vert = edge.other_vert(vert)
            # print("next vert:", next_vert.index)

            next_edges = [e for e in next_vert.link_edges if e in edges and e not in sorted_edges]
            # print(next_edges)
            next_edge = next_edges[0]
            # print("next edge:", next_edge.index)

            sorted_edges.append(next_edge)

            # print("sorted_edges:", [e.index for e in sorted_edges])

            vert = next_vert
            edge = next_edge

            # print("vert:", vert.index)
            # print("edge:", edge.index)

            # print("--")

            unsorted_edges.remove(edge)

        if debug:
            print("sorted edges:", [e.index for e in sorted_edges])

        return sorted_edges

    def get_target_face_ids(self, obj, target, precision, debug=False):
        if debug:
            print("\nGetting target obj's faces to be replaced by the plug")

        if precision:
            m3.make_active(obj)
            subd = obj.modifiers.new(name="Subsurf", type="SUBSURF")
            subd.levels = precision
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier=subd.name)

        # create bmesh
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        # for every vert of the obj, get the closest face of the surface of the target
        objmx = obj.matrix_world
        targetmx = target.matrix_world

        face_ids = []
        for v in bm.verts:
            vert_world_co = objmx * v.co  # vertex location in world space
            vert_target_local_co = targetmx.inverted() * vert_world_co   # vertex location in the targets local space

            hit, co, nrm, face_idx = target.closest_point_on_mesh(vert_target_local_co)

            if hit:
                if debug:
                    print(" » idx:", v.index, "normal:", nrm, "target face index:", face_idx)

                if face_idx not in face_ids:
                    face_ids.append(face_idx)
        if debug:
            print(" » sampled %d verts" % (len(bm.verts)))

        bm.clear()

        # remove the handle
        if not debug:
            bpy.data.objects.remove(obj, do_unlink=True)

        return face_ids

    def conform_verts_to_target_surface(self, obj, target, debug=False):
        if debug:
            print("\nConforming plug obj's verts to the target's surface")

        # get bmesh and vertex groups
        bm, conform_verts, border_verts = self.create_plug_vgroups(obj)

        if debug:
            print(" » border verts:", [v.index for v in border_verts])
            print(" » conform verts:", [v.index for v in conform_verts])

        # for each border vert and conform vert, get the closest point on the surface of the target
        # and reposition the vert accordingly, https://blender.stackexchange.com/a/58432/33919

        # the modifier based deformation makes the vertex proximity offset unnecessary
        # in fact the vertex proximity offset damages small bevels(at least if run after the modifier based deform)
        # however, the vertex proximity offset is fantastic when the modiifier based deformation is turned off
        # NOTE, turning it off only really works for hard edges

        if self.filletoredge == "EDGE":
            objmx = obj.matrix_world
            targetmx = target.matrix_world

            distances = []
            for v in border_verts + conform_verts:
                vert_origin_world_co = obj.matrix_world * v.co  # vertex location in world space
                vert_origin_target_local_co = targetmx.inverted() * vert_origin_world_co   # vertex location in the targets local space

                hit, co, nrm, face_idx = target.closest_point_on_mesh(vert_origin_target_local_co)

                if hit:
                    if debug:
                        print(" » idx:", v.index, "normal:", nrm, "target face index:", face_idx)

                    # on target surface projected vert location in world space
                    vert_destination_world_co = targetmx * co

                    dist = (vert_destination_world_co - vert_origin_world_co).length
                    distances.append(dist)
                    if debug:
                        print("  » projection distance:", dist)

                    vert_destination_obj_local_co = objmx.inverted() * vert_destination_world_co

                    v.co = vert_destination_obj_local_co

            if debug:
                print(" » moved %d verts" % (len(border_verts + conform_verts)))

            # move all of the non-border and non-conform verts according to the avg distance verts have been moved
            avg_dist = sum(distances) / len(distances)

            if debug:
                print(" » average distance:", avg_dist)

            for v in bm.verts:
                if v not in border_verts + conform_verts:
                    v.co = v.co + mathutils.Vector((0, 0, -1)) * avg_dist

        bm.to_mesh(obj.data)
        obj.data.update()
        bm.clear()

    def create_plug_vgroups(self, plug, push_back=False):
        conform_vgroup = plug.vertex_groups.get("conform")
        plug_vgroup = plug.vertex_groups.new("plug")
        border_vgroup = plug.vertex_groups.new("border")

        # create bmesh
        bm = bmesh.new()
        bm.from_mesh(plug.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        groups = bm.verts.layers.deform.verify()

        # create plug vgroup by inverting the conform vgroup
        conform_verts = []

        for v in bm.verts:
            if conform_vgroup.index in v[groups]:
                conform_verts.append(v)
            else:
                v[groups][plug_vgroup.index] = 1


        # create border vgroup from non-manifold edges
        border_edges = [e for e in bm.edges if not e.is_manifold]
        border_verts = []

        for e in border_edges:
            for v in e.verts:
                v[groups][border_vgroup.index] = 1
                border_verts.append(v)

        # if the main self.deformation toggle is off, we push back here, else, we do it in self.conform_verts_to_target_surface()
        if push_back:
            bm.to_mesh(plug.data)
            bm.clear()

        return bm, conform_verts, border_verts

    def contain_handle(self, target, handle, amount, precision, debug=False):
        handlescale = (handle.scale.x + handle.scale.y) / 2
        targetscale = (target.scale.x + target.scale.y + target.scale.z) / 3

        # the cointain amount needs to adjust relative to the handle scale, and since the handle dup is joined with the target, the target scale needs to be taken into account as well.
        containamount = handlescale / targetscale * amount
        # containamount = amount

        handle.select = False

        container = handle.copy()
        container.data = handle.data.copy()
        container.name = "container"
        bpy.context.scene.objects.link(container)

        add_vgroup(container, [v.index for v in container.data.vertices], "container", debug=debug)

        container.select = True
        m3.make_active(container)

        # subdivide the container a bit, because if you subdivice the handle later and dont subd the cointainer, the face match may hit faces outside of the container cut at negative corners
        if precision > 1:
            subd = container.modifiers.new(name="Subsurf", type="SUBSURF")
            subd.levels = 1
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier=subd.name)

        m3.set_mode("EDIT")
        m3.set_mode("FACE")
        m3.select_all("MESH")

        bpy.ops.transform.translate(value=(0, 0, -containamount), constraint_axis=(False, False, True), constraint_orientation='LOCAL')
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, containamount * 2), "constraint_axis": (False, False, True), "constraint_orientation": 'LOCAL'})
        m3.select_all("MESH")
        m3.set_mode("OBJECT")

        # unhide and unselect target geo
        m3.make_active(target)
        target.select = True
        m3.set_mode("EDIT")
        m3.unhide_all("MESH")
        m3.unselect_all("MESH")
        m3.set_mode("OBJECT")

        # mesh intersect
        bpy.ops.object.join()
        m3.set_mode("EDIT")
        bpy.ops.transform.shrink_fatten(value=-containamount)
        bpy.ops.mesh.intersect(separate_mode='NONE')

        # remove container mesh parts and vgroup
        container_vgroup = target.vertex_groups.get("container")
        target.vertex_groups.active_index = container_vgroup.index
        bpy.ops.object.vertex_group_select()
        # bpy.ops.mesh.delete(type='VERT')

        bpy.ops.mesh.select_more()
        bpy.ops.object.vertex_group_assign()
        bpy.ops.mesh.delete(type='FACE')

        m3.set_mode("OBJECT")
        handle.select = True

    def deform(self, target, handle, deformer, plug, subsets, debug=False):
        # add surface deform mod to plug, if deform is True or if FILLET is selected
        if self.deform_plug or self.filletoredge == "FILLET":
            if deformer and self.use_mesh_deform:
                # use a surface deform on the deformer mesh
                m3.make_active(deformer)
                surface_deform = deformer.modifiers.new(name="Deformer Deform", type="SURFACE_DEFORM")
                surface_deform.target = handle
                surface_deform.falloff = self.deform_interpolation_falloff  # by default this value is 4, but it might not be enough

                bpy.ops.object.surfacedeform_bind(modifier="Deformer Deform")

                # and a mesh deform on the plug mesh
                m3.make_active(plug)
                mesh_deform = plug.modifiers.new(name="Plug Deform", type="MESH_DEFORM")
                mesh_deform.object = deformer
                mesh_deform.precision = self.deformer_plug_precision

                bpy.ops.object.meshdeform_bind(modifier="Plug Deform")
            else:
                # use a surface deform on the plug mesh
                m3.make_active(plug)
                surface_deform = plug.modifiers.new(name="Plug Deform", type="SURFACE_DEFORM")
                surface_deform.target = handle
                surface_deform.falloff = self.deform_interpolation_falloff  # by default this value is 4, but it might not be enough

                bpy.ops.object.surfacedeform_bind(modifier="Plug Deform")

        # add surface deform mod to subsets, if deform subsets is True or forcesubsetdeform is True on a per subsets level
        if subsets:
            subs = subsets if self.deform_subsets else [sub for sub in subsets if sub.MM.forcesubsetdeform]

            for sub in subs:
                m3.make_active(sub)

                if deformer and self.use_mesh_deform:
                    mesh_deform = sub.modifiers.new(name="Plug Deform", type="MESH_DEFORM")
                    mesh_deform.object = deformer
                    mesh_deform.precision = self.deformer_subset_precision

                    bpy.ops.object.meshdeform_bind(modifier="Plug Deform")

                else:
                    surface_deform = sub.modifiers.new(name="Subset Deform", type="SURFACE_DEFORM")
                    surface_deform.target = handle
                    surface_deform.falloff = self.deform_interpolation_falloff  # by default this value is 4, but it might not be enough

                    bpy.ops.object.surfacedeform_bind(modifier="Subset Deform")

        # add shrink wrap mod to handle, always do that
        shrink_wrap = handle.modifiers.new(name="Shrink Wrap", type="SHRINKWRAP")
        shrink_wrap.target = target

        # """
        # apply mods
        # update the scene or surface deform isn't "seen"
        bpy.context.scene.update()

        # the order here is imporant, the handle needs to be last, or you'd need additional scene updates
        m3.apply_all_mods(plug)
        if subsets:
            for sub in subs:
                m3.apply_all_mods(sub)

        m3.apply_all_mods(handle)

        # """

    def transform(self, handle, plug, subsets, deformer, rotation, offset, debug=False):
        if self.rotation != 0:
            rotmx = mathutils.Matrix.Rotation(math.radians(rotation), 4, 'Z')

            # rotate the handle (and with it everything that is still parented to it)
            handle.matrix_world *= rotmx

            bpy.context.scene.update()

        if offset != 0:
            self.offset_border(plug, offset, debug=debug)
            self.offset_border(handle, offset, debug=debug)

            if deformer:
                self.offset_deformer(deformer, offset, debug=debug)

    def offset_deformer(self, obj, amount, debug=False):
        # create final target bmesh
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        # make sure everything is unhidden and unsellected
        for f in bm.faces:
            f.hide_set(False)
            f.select_set(False)

        # sort faces by normal by comparing their normals to an up vector
        top = []
        bottom = []
        side = []

        for f in bm.faces:
            dot = f.normal.dot(mathutils.Vector((0, 0, 1)))

            if dot > 0.9:
                top.append(f)
            elif dot < -0.9:
                bottom.append(f)
            else:
                side.append(f)

        # select the top faces
        for f in top:
            f.select = True

        # get the boundary edges and get the vert pairs
        border_edges = [e for e in bm.edges if (e.link_faces[0].select and not e.link_faces[1].select) or (not e.link_faces[0].select and e.link_faces[1].select)]


        verts = {}
        for e in border_edges:
            for v in e.verts:
                if v not in verts:
                    # get the offset vert, this is the inner vert in this case
                    offset_edge = [e for e in v.link_edges if e.select and e not in border_edges]
                    if offset_edge:
                        if not self.offset_dist:
                            self.offset_dist = offset_edge[0].calc_length()
                            if debug:
                                print("offset distance:", self.offset_dist)

                        offset_vert = offset_edge[0].other_vert(v)

                        verts[v] = offset_vert
                        if debug:
                            print("vert:", v.index, " » offset vert:", offset_vert.index)


        # repeat for the bottom faces, first select the bottom faces
        for f in bm.faces:
            f.select = True if f in bottom else False


        # get the boundary edges and get the vert pairs
        border_edges = [e for e in bm.edges if (e.link_faces[0].select and not e.link_faces[1].select) or (not e.link_faces[0].select and e.link_faces[1].select)]

        for e in border_edges:
            for v in e.verts:
                if v not in verts:
                    # get the offset vert, this is the inner vert in this case
                    offset_edge = [e for e in v.link_edges if e.select and e not in border_edges]
                    if offset_edge:
                        if not self.offset_dist:
                            self.offset_dist = offset_edge[0].calc_length()
                            if debug:
                                print("offset distance:", self.offset_dist)

                        offset_vert = offset_edge[0].other_vert(v)

                        verts[v] = offset_vert
                        if debug:
                            print("vert:", v.index, " » offset vert:", offset_vert.index)


        # move the verts according ot tthe offset amount and he self.offset_dist value
        for v in verts:
            # normalize the vector so the offset change is equal for the plug and the handle
            # multiply the length of the first offset edge, to geta baseline distance, that cant be overshot in the negative direction
            v_ov_dir = (verts[v].co - v.co).normalized() * self.offset_dist * amount
            v.co = v.co - v_ov_dir

        bm.to_mesh(obj.data)
        bm.clear()

    def offset_border(self, obj, amount, debug=False):
        # create final target bmesh
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        # get border
        border_edges = [e for e in bm.edges if not e.is_manifold]

        verts = {}
        for e in border_edges:
            for v in e.verts:
                if v not in verts:
                    # get the offset vert, this is the inner vert in this case
                    offset_edge = [e for e in v.link_edges if e not in border_edges]
                    if offset_edge:
                        if not self.offset_dist:
                            self.offset_dist = offset_edge[0].calc_length()
                            if debug:
                                print("offset distance:", self.offset_dist)

                        offset_vert = offset_edge[0].other_vert(v)

                        verts[v] = offset_vert
                        if debug:
                            print("vert:", v.index, " » offset vert:", offset_vert.index)

        for v in verts:
            # normalize the vector so the offset change is equal for the plug and the handle
            # multiply the length of the first offset edge, to geta baseline distance, that cant be overshot in the negative direction
            v_ov_dir = (verts[v].co - v.co).normalized() * self.offset_dist * amount
            v.co = v.co - v_ov_dir


        bm.to_mesh(obj.data)
        bm.clear()

    def apply_hooks_and_arrays(self, handle, plug, subsets, deformer, modifiers):
        if any(mod in modifiers for mod in ['HOOK', 'ARRAY']):
            bpy.context.scene.update()

            # if there are more than two array mods on the plug, you need to apply the arrow mods on the caps of the second array mod first
            # otherwise the caps' vertex groups won't be carried through
            arraymods = [m for m in plug.modifiers if m.type == "ARRAY"]

            if len(arraymods) > 1:
                array2 = arraymods[1]

                m3.apply_all_mods(array2.start_cap)
                m3.apply_all_mods(array2.end_cap)

                bpy.context.scene.update()

            # get the objects where you need to apply the mods
            applyobjs = [handle] + [plug] + subsets
            if deformer:
                applyobjs.append(deformer)

            # then apply the mods
            for obj in applyobjs:
                m3.apply_all_mods(obj)

    def set_operator_props(self, plug, subsets, deformer):
        self.init = False

        # check plug for its hasfillet prop and set the operator prop filletoredge accordingly
        if plug.MM.hasfillet:
            self.filletoredge = "FILLET"
        else:
            self.filletoredge = "EDGE"

        # also set the subsets operator prop for draw()
        self.subsets = True if subsets else False

        # and do the same for the deformer operator prop
        self.deformer = True if deformer else False

        # set rotation and offset values
        self.rotation = 0
        self.offset = 0

        # set the deformerprecision values
        self.deformer_plug_precision = plug.MM.deformerprecision
        if subsets:
            self.deformer_subset_precision = max([sub.MM.deformerprecision for sub in subsets])

        # set use_mesh_deform prop
        if deformer:
            self.use_mesh_deform = deformer.MM.usedeformer

    def get_and_save_plug_scale(self, scene, handle, empties):
        if handle.MM.uuid:
            plugscales = scene.MM.plugscales

            if handle.MM.uuid in plugscales:
                ps = plugscales[handle.MM.uuid]
            else:
                ps = plugscales.add()
                ps.name = handle.MM.uuid
            ps.scale = handle.scale

        for e in empties:
            if e.MM.uuid:
                if e.MM.uuid in ps.empties:
                    emp = ps.empties[e.MM.uuid]
                else:
                    emp = ps.empties.add()
                    emp.name = e.MM.uuid
                emp.location = e.location


    def get_plug(self, sel, debug=False):
        if len(sel) != 2:
            errmsg = "Select plug handle and a target object to plug into."
            errtitle = "Illegal Selection"
        else:
            active = m3.get_active()

            if active in sel:
                sel.remove(active)
                target = active

                if debug:
                    print("target:", target.name)

                if sel[0].MM.isplughandle:
                    handle = sel[0]

                    if debug:
                        print("plug handle:", handle.name)

                    plug = None
                    deformer = None
                    subsets = []
                    others = []  # other are either empties or array caps or an occluder, all of these can be deleted after mods have been applied
                    modifiers = list(set([mod.type for mod in handle.modifiers]))

                    if handle.children:
                        children = list(handle.children)

                        while children:
                            c = children[0]
                            children.extend(list(c.children))

                            if c.MM.isplug:
                                plug = c
                            elif c.MM.isplugsubset:
                                subsets.append(c)
                            elif c.MM.isplugdeformer:
                                deformer = c
                            else:
                                others.append(c)

                            modifiers.extend([mod.type for mod in c.modifiers if mod.type not in modifiers])

                            children.pop(0)

                        if plug:
                            if debug:
                                print("plug:", plug.name)

                            conform_vgroup = plug.vertex_groups.get("conform")

                            if conform_vgroup:
                                if debug:
                                    print("subsets:", [obj.name for obj in subsets])
                                    print("deformer:", deformer.name if deformer else None)
                                    print("others:", [obj.name for obj in others])
                                    print("modifiers:", modifiers)

                                return target, handle, plug, subsets, deformer, modifiers, others, None
                            else:
                                errmsg = "Plug is missing a 'conform' vertex group."
                                errtitle = "Invalid Plug"

                        else:
                            errmsg = "Plug handle does not seem to have a plug object as a child"
                            errtitle = "Invalid Plug"

                    else:
                        errmsg = "Plugs can't just consist of a handle, they need to have a plug mesh as well."
                        errtitle = "Invalid Plug"

                else:
                    errmsg = "The selected object is not a (valid) plug handle, aborting"
                    errtitle = "Illegal Selection"

            else:
                errmsg = "No active object in selection."
                errtitle = "Illegal Selection"

        return None, None, None, None, None, None, None, (errmsg, errtitle)


class CreatePlug(bpy.types.Operator):
    bl_idname = "machin3.create_plug"
    bl_label = "MACHIN3: Create Plug"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        active = context.active_object
        if active:
            sel = context.selected_objects
            return not any([obj.MM.isplug or obj.MM.isplughandle for obj in sel + [active]])

    def execute(self, context):
        plug = m3.get_active()
        others = m3.selected_objects()

        if plug in others:
            others.remove(plug)

        # find subsets and align the subset origins to the plug origin
        subsets = []
        for obj in others:
            # only mesh objects are substes, empties are not
            if obj.type == "MESH":
                subsets.append(obj)
                # submx = obj.matrix_world.copy()
                # obj.matrix_world = plug.matrix_world

                # for v in obj.data.vertices:
                    # v.co = plug.matrix_world.inverted() * submx * v.co
                # obj.data.update()

        # parent subset to the plug
        parent(subsets, plug, debug=True)

        # create conform vgroup
        conform_vgroup = plug.vertex_groups.new(name="conform")

        # clear all materials
        plug.data.materials.clear()

        # create (empty) handle mesh and name it after the plug mesh
        handle_mesh = bpy.data.meshes.new(name="%s_handle" % (plug.name))
        handle = bpy.data.objects.new(name=handle_mesh.name, object_data=handle_mesh)
        context.scene.objects.link(handle)

        # assign verts to conform vgroup, start the the handle mesh
        hasfillet = self.prepare_plug(plug, handle, conform_vgroup)

        # set the object props
        self.set_props(plug, handle, subsets, hasfillet)

        # move the handle to where the plug is
        handle.matrix_world = plug.matrix_world * handle.matrix_world

        # parent the plug to the handle
        parent([plug], handle)

        # set handle draw type and xray
        handle.draw_type = 'WIRE'
        handle.show_x_ray = True
        handle.hide_render = True

        # select only the handle and go into edit mode to finish the handle mesh
        m3.unselect_all("OBJECT")
        handle.select = True
        m3.make_active(handle)

        m3.set_mode("EDIT")

        return {'FINISHED'}

    def set_props(self, plug, handle, subsets, hasfillet):
        uuid = str(uuid4())
        creator = m3.MM_prefs().plugcreator

        plug.MM.isplug = True
        plug.MM.uuid = uuid
        plug.MM.hasfillet = hasfillet
        plug.MM.plugcreator = creator

        handle.MM.isplughandle = True
        handle.MM.uuid = uuid
        handle.MM.plugcreator = creator

        for sub in subsets:
            sub.MM.isplugsubset = True
            sub.MM.uuid = uuid
            sub.MM.plugcreator = creator

    def prepare_plug(self, plug, handle, conform_vgroup):
        # create bmesh
        bm = bmesh.new()
        bm.from_mesh(plug.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        groups = bm.verts.layers.deform.verify()

        # get border edges and make sure they aren't sharp
        border_edges = []
        border_verts = []
        for e in bm.edges:
            if not e.is_manifold:
                e.smooth = True
                border_edges.append(e)
                border_verts.extend(e.verts)

        # get conform verts
        conform_verts = []
        edge_verts = []
        for e in border_edges:
            for v in e.verts:
                # add the manifold edge verts to the list
                if v not in conform_verts:
                    conform_verts.append(v)
                    edge_verts.append(v)

                # append the vert on the inside
                for e in v.link_edges:
                    if e not in border_edges:
                        conform_verts.append(e.other_vert(v))

        # add verts to the conform vgroup
        for v in conform_verts:
            v[groups][conform_vgroup.index] = 1

        # check if the inner rail is made of sharp edges or a fillet
        inner_rail = []
        for e in bm.edges:
            if len([v for v in e.verts if v in conform_verts]) == 2:
                # e.select = True
                if len([v for v in e.verts if v in border_verts]) == 0:
                    # e.select = True
                    inner_rail.append(e)

        hasfillet = True if all([e.smooth for e in inner_rail]) else False

        # push back to the plug mesh
        bm.to_mesh(plug.data)

        # offset the border verts outside
        for v in edge_verts:
            for e in v.link_edges:
                if e not in border_edges:
                    other_v = e.other_vert(v)
                    offset_dir = other_v.co - v.co
                    v.co = v.co - offset_dir * 0.3

        # create the handle mesh, by dissolving everything but the conform verts
        bmesh.ops.dissolve_verts(bm, verts=[v for v in bm.verts if v not in conform_verts])

        bm.to_mesh(handle.data)
        bm.clear()

        return hasfillet


# TODO: keep subset materials?

addmodeitems = [("NEW", "New", ""),
                ("REPLACE", "Replace", "")]


class AddPlugToLibrary(bpy.types.Operator):
    bl_idname = "machin3.add_plug_to_library"
    bl_label = "MACHIN3: Add Plug To Library"

    addmode = EnumProperty(name="Add Mode", items=addmodeitems, default="NEW")

    plugname = StringProperty(name="Name (optional)")

    showindicatorHUD = BoolProperty(name="Show Indicators", default=True)
    showindicatorFILLETorEDGE = BoolProperty(name="FILLET or EDGE", default=True)
    showindicatorHOOKorARRAY = BoolProperty(name="HOOK or ARRAY", default=True)
    showindicatorDEFORMER = BoolProperty(name="DEFORMER", default=True)

    @classmethod
    def poll(cls, context):
        active = m3.get_active()
        if active:
            return active.MM.isplughandle

    def check(self, context):
        return True

    def draw(self, context):
        wm = context.window_manager
        library = context.scene.pluglibs
        scale = m3.DM_prefs().plugsinlibraryscale
        show_names = m3.DM_prefs().showplugnames

        layout = self.layout

        column = layout.column()

        # mode selection
        row = column.row()
        row.label("Add Mode")
        row.prop(self, "addmode", expand=True)

        # library selection
        column.prop(context.scene, "pluglibs", text="Library")

        # plug naming
        if self.addmode == "NEW":
            column.prop(self, "plugname")

            if self.plugname:
                pathstr = library + " / blends / " + context.scene.newplugidx + "_" + self.plugname.replace(" ", "_") + ".blend"
            else:
                pathstr = library + " / blends / " + context.scene.newplugidx + ".blend"

        # plug replacing
        else:
            # column.prop(wm, "pluglib_" + library, text="Replace Plug")
            column.template_icon_view(wm, "pluglib_" + library, show_labels=show_names, scale=scale)

            plugname = getattr(wm, "pluglib_" + library)
            pathstr = library + " / blends / " + plugname + ".blend"


        row = column.split(percentage=0.28)
        row.label("Path Preview")
        row.label(pathstr, icon="FILE_FOLDER")


        column.separator()
        column.prop(self, "showindicatorHUD")

        if self.showindicatorHUD:
            row = column.row()
            row.prop(self, "showindicatorFILLETorEDGE")
            row.prop(self, "showindicatorHOOKorARRAY")
            row.prop(self, "showindicatorDEFORMER")

    def invoke(self, context, event):
        set_new_plug_index(self, context)

        # make sure selecting a plug in replace mode, doesn't insert or remove the plug
        m3.MM_prefs().plugmode = "NONE"

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def execute(self, context):
        debug = False
        debug = True

        # depending on user priviledges, windows and mac may not like the script saving a previously unsaved scene
        try:
            bpy.ops.wm.save_mainfile()
        except:
            popup_message("Save your blender file first!")
            return {'FINISHED'}

        # get current blend file
        currentblend = bpy.data.filepath

        assetspath = m3.MM_prefs().assetspath
        library = context.scene.pluglibs
        index = context.scene.newplugidx
        plugiconrenderblendpath = os.path.join(m3.MM_prefs().MMpath, "resources", "plug_icon_render.blend")

        # create the blend and icon paths and the name of the plug itself
        if self.addmode == "NEW":
            if self.plugname:
                blendname = "%s_%s.blend" % (index, self.plugname.replace(" ", "_"))
                iconname = "%s_%s.png" % (index, self.plugname.replace(" ", "_"))
                plugname = "%s_%s" % (index, self.plugname.replace(" ", "_"))
            else:
                blendname = "%s.blend" % index
                iconname = "%s.png" % index
                plugname = "%s" % index
        else:
            wm = context.window_manager
            plugname = getattr(wm, "pluglib_" + library)
            blendname = "%s.blend" % plugname
            iconname = "%s.png" % plugname


        blendpath = os.path.join(assetspath, library, "blends", blendname)
        iconpath = os.path.join(assetspath, library, "icons", iconname)

        # get all the plug objects
        handle = m3.get_active()
        plugobjs, fillet, deformer, occluder, mods = self.get_plug_objs(handle, debug=debug)

        # render icon
        self.create_icon(plugobjs, plugiconrenderblendpath, iconpath, fillet, deformer, mods)

        # """
        # save the plug blend
        self.create_blend(plugobjs, plugname, blendpath)

        # update the library
        reload_plug_libraries(library=library, defaultplug=plugname)

        # open the original scene again
        bpy.ops.wm.open_mainfile(filepath=currentblend)
        # """

        return {'FINISHED'}

    def get_plug_objs(self, handle, debug=False):
        plugobjects = [handle]
        plugmods = []
        fillet = False
        deformer = False
        occluder = False
        mods = None

        if handle.children:
            children = list(handle.children)

            while children:
                child = children[0]

                plugobjects.append(child)
                children.extend(list(child.children))

                # check hasfillet
                if child.MM.isplug:
                    if child.MM.hasfillet:
                        fillet = True

                # check if there's a deformer
                if child.MM.isplugdeformer:
                    deformer = child

                # check if there's an occluder
                if child.MM.isplugoccluder:
                    occluder = child

                # collect mods
                plugmods.extend([mod.type for mod in child.modifiers])

                children.pop(0)

        if "ARRAY" in plugmods:
            mods = "ARRAY"
        elif "HOOK" in plugmods:
            mods = "HOOK"

        if debug:
            print("plug objs:", plugobjects)
            print("fillet:", fillet)
            print("deformer:", deformer)
            print("occluder:", occluder)
            print("mods:", mods)

        return plugobjects, fillet, deformer, occluder, mods

    def create_icon(self, plugobjs, iconrenderblendpath, iconpath, fillet, deformer, mods):
        # append the icon render scene
        scene = append_scene(iconrenderblendpath, "PlugIconScene")
        bpy.context.screen.scene = scene

        # remove the demo plug present in that scene
        for obj in bpy.data.objects:
            if "demo" in obj.name:
                bpy.data.objects.remove(obj, do_unlink=True)


        # link the plug we want to render an icon from
        handle = plugobjs[0]

        # we only want the plug objects on layer 1
        for obj in plugobjs:
            scene.objects.link(obj)
            obj.layers = (True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False)

        # position the plug at the origin
        handle.location = (0, 0, 0)
        handle.rotation_euler = (0, 0, 0)

        # it's weird, but only by translating and doing a data.update() witll some hook/empty plugs udpdate their dimensions properly
        bpy.ops.transform.translate(value=(0, 0, 0))
        handle.data.update()
        scene.update()

        # scale the plug to fit the camera space
        maxscale = 1.8
        handlemaxdim = max(handle.dimensions)

        mxworld = handle.matrix_world.copy()
        handle.matrix_world = mathutils.Matrix.Scale(maxscale / handlemaxdim, 4) * mxworld
        scene.update()

        # set the indicator HUDs
        if self.showindicatorHUD:
            if self.showindicatorFILLETorEDGE:
                hudfillet = bpy.data.objects.get("HUD_FILLET")
                hudedge = bpy.data.objects.get("HUD_EDGE")
                if hudfillet and hudedge:
                    if fillet:
                        hudfillet.hide_render = False
                        hudfillet.hide = False
                        hudedge.hide_render = True
                        hudedge.hide = True
                    else:
                        hudfillet.hide_render = True
                        hudfillet.hide = True
                        hudedge.hide_render = False
                        hudedge.hide = False

            if self.showindicatorHOOKorARRAY:
                hudarray = bpy.data.objects.get("HUD_ARRAY")
                hudhook = bpy.data.objects.get("HUD_HOOK")
                if hudarray and hudhook:
                    if mods == "ARRAY":
                        hudarray.hide_render = False
                        hudarray.hide = False
                        hudhook.hide_render = True
                        hudhook.hide = True
                    elif mods == "HOOK":
                        hudarray.hide_render = True
                        hudarray.hide = True
                        hudhook.hide_render = False
                        hudhook.hide = False

            if self.showindicatorDEFORMER:
                huddeformer = bpy.data.objects.get("HUD_DEFORMER")
                if huddeformer:
                    if deformer:
                        huddeformer.hide_render = False
                        huddeformer.hide = False

                        if deformer.MM.usedeformer:
                            mat = bpy.data.materials.get("HUD.white.transparent")
                            if mat:
                                huddeformer.material_slots[0].material = mat


        # set render output filename
        scene.render.filepath = iconpath

        # setting the tumbpath is not enough, the filetype needs to also be set to png!
        scene.render.image_settings.file_format = 'PNG'

        # focus the viewport on the handle, this is just in case the handle wasn't at the origin and to make it easy for when you open a plug blend manually
        handle.select = True
        bpy.ops.view3d.view_selected(use_all_regions=False)

        # """
        # render thumbnail
        bpy.ops.render.render(write_still=True)

        # remove the render scene
        bpy.data.scenes.remove(scene, do_unlink=True)

        # reset the handle/plug to its original size
        handle.matrix_world = mxworld

        print(" » Saved plug icon to '%s'" % (iconpath))
        # """

    def create_blend(self, plugobjs, plugname, blendpath):
        m3.delete_all(keepobjs=plugobjs)

        # create group
        group = bpy.data.groups.new(name=plugname)

        for obj in plugobjs:
            group.objects.link(obj)

        # prevent exception in case you append a plug, delete it from the lib and want to create a new plug in its place
        for lib in bpy.data.libraries:
            lib.filepath = ""

        # save the plug blend
        bpy.ops.wm.save_as_mainfile(filepath=blendpath)

        print(" » Saved plug blend to '%s'" % (blendpath))


propitems = [("NONE", "None", ""),
             ("PLUG", "Plug", ""),
             ("HANDLE", "Handle", ""),
             ("SUBSET", "Subset", ""),
             ("DEFORMER", "Deformer", ""),
             ("OCCLUDER", "Occluder", "")]


class SetPlugProps(bpy.types.Operator):
    bl_idname = "machin3.set_plug_props"
    bl_label = "MACHIN3: Set Plug Props"
    bl_options = {'REGISTER', 'UNDO'}

    prop = EnumProperty(name="Property", items=propitems, default="NONE")

    hasfillet = BoolProperty(name="Has Fillet", default=False)

    deformerprecision = IntProperty(name="Deformer Precision", default=4)

    usedeformer = BoolProperty(name="Use Deformer", default=False)
    forcesubsetdeform = BoolProperty(name="Force Subset Deform", default=False)

    # hidden
    init = BoolProperty(name="initial run", default=False)

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return len(context.selected_objects) == 1

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        row = column.row()
        row.prop(self, "prop", expand=True)
        if self.prop == "PLUG":
            column.prop(self, "hasfillet")

        if self.prop in ["PLUG", "SUBSET"]:
            if self.deformerprecision > 4:
                column.label("Careful, values above 4 are increasingly slow", icon="ERROR")

            column.prop(self, "deformerprecision")

        if self.prop == "SUBSET":
            column.prop(self, "forcesubsetdeform")

        if self.prop == "DEFORMER":
            column.prop(self, "usedeformer")

    def execute(self, context):
        active = m3.get_active()

        if self.init:
            if active.MM.isplug:
                self.set_props(active, plug=True)
            elif active.MM.isplughandle:
                self.set_props(active, handle=True)
            elif active.MM.isplugsubset:
                self.set_props(active, subset=True)
            elif active.MM.isplugdeformer:
                self.set_props(active, deformer=True)
            elif active.MM.isplugoccluder:
                self.set_props(active, occluder=True)
            else:
                self.set_props(active)

            self.init = False

        else:
            if self.prop == "NONE":
                self.set_props(active)
            elif self.prop == "PLUG":
                self.set_props(active, plug=True)
            elif self.prop == "HANDLE":
                self.set_props(active, handle=True)
            elif self.prop == "SUBSET":
                self.set_props(active, subset=True)
            elif self.prop == "DEFORMER":
                self.set_props(active, deformer=True)
            elif self.prop == "OCCLUDER":
                self.set_props(active, occluder=True)

        return {'FINISHED'}

    def set_props(self, obj, plug=False, handle=False, subset=False, deformer=False, occluder=False):
        if self.init:
            # on the initial run, set the operator props
            if plug:
                self.prop = "PLUG"
                self.hasfillet = obj.MM.hasfillet
                self.deformerprecision = obj.MM.deformerprecision
            elif handle:
                self.prop = "HANDLE"
            elif deformer:
                self.prop = "DEFORMER"
                self.usedeformer = obj.MM.usedeformer
            elif subset:
                self.prop = "SUBSET"
                self.deformerprecision = obj.MM.deformerprecision
                self.forcesubsetdeform = obj.MM.forcesubsetdeform
            else:
                self.prop = "NONE"

        # set the obj props and make sure the obj is only one of these (by the way this method is called)
        obj.MM.isplug = plug
        obj.MM.isplughandle = handle
        obj.MM.isplugsubset = subset
        obj.MM.isplugdeformer = deformer
        obj.MM.isplugoccluder = occluder

        if not self.init:
            if plug:
                obj.MM.hasfillet = self.hasfillet
                obj.MM.deformerprecision = self.deformerprecision

            if subset:
                obj.MM.deformerprecision = self.deformerprecision
                obj.MM.forcesubsetdeform = self.forcesubsetdeform

            if deformer:
                obj.name = obj.name.replace("handle", "deformer")
                obj.MM.usedeformer = self.usedeformer
                obj.show_x_ray = False

            if occluder:
                obj.name = obj.name.replace("handle", "occluder")
                obj.hide_render = False
                obj.show_all_edges = True
                obj.show_x_ray = False
                obj.cycles.is_shadow_catcher = True


class ClearPlugProps(bpy.types.Operator):
    bl_idname = "machin3.clear_plug_props"
    bl_label = "MACHIN3: Clear Plug Properties"
    bl_options = {'REGISTER', 'UNDO'}

    alsoclearvgroups = BoolProperty(name="Also Clear Vertex Groups", default=True)

    @classmethod
    def poll(cls, context):
        active = m3.get_active()
        return active

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        column.prop(self, "alsoclearvgroups")

    def execute(self, context):
        sel = m3.selected_objects()

        for obj in sel:
            print(obj.name)

            if obj.MM.isplug:
                obj.MM.isplug = False
                print(" » cleared 'isplug' property")

                if self.alsoclearvgroups:
                    obj.vertex_groups.clear()
                    print(" » cleared plug object's vertex groups")

            if obj.MM.isplughandle:
                obj.MM.isplughandle = False
                print(" » cleared 'isplughandle' property")

            if obj.MM.isplugsubset:
                obj.MM.isplugsubset = False
                print(" » cleared 'isplugsubset' property")

            if obj.MM.isplugdeformer:
                obj.MM.isplugdeformer = False
                print(" » cleared 'isplugdeformer' property")

            if obj.MM.isplugoccluder:
                obj.MM.isplugoccluder = False
                print(" » cleared 'isplugoccluder' property")

            if obj.MM.deformerprecision != 4:
                obj.MM.deformerprecision = 4
                print(" » reset 'deformerprecision' property to 4")

            if obj.MM.usedeformer:
                obj.MM.usedeformer = False
                print(" » cleared 'usedeformer' property")

            if obj.MM.forcesubsetdeform:
                obj.MM.forcesubsetdeform = False
                print(" » cleared 'forcesubsetdeform' property")

        return {'FINISHED'}


class ValidatePlug(bpy.types.Operator):
    bl_idname = "machin3.validate_plug"
    bl_label = "MACHIN3: Validate Plug"

    hidesupportobjs = BoolProperty(name="Hide Deformer and Occluder and Others", default=True)

    generateuuid = BoolProperty(name="Generate new UUID", default=False)


    @classmethod
    def poll(cls, context):
        active = m3.get_active()
        return active

    def draw(self, context):
        layout = self.layout

        # CHECKS

        box = layout.box()

        column = box.column()
        column.label("Basic")

        # check handles

        if len(self.handles) == 1:
            column.label("Handle: %s" % self.handles[0].name, icon="FILE_TICK")
            if self.ngon:
                column.label("Handle contains N-Gons!", icon="ERROR")
            if self.flipped:
                column.label("Handle polygons are flipped!", icon="ERROR")

        elif len(self.handles) == 0:
            column.label("No Handle found!", icon="ERROR")
        else:
            column.label("Multiple Handles found!", icon="ERROR")
            for handle in self.handles:
                column.label("  » %s" % handle.name)

        # check plugs

        if len(self.plugs) == 1:
            column.label("Plug: %s" % self.plugs[0].name, icon="FILE_TICK")
            filletoredge = "FILLET" if self.plugs[0].MM.hasfillet else "EDGE"
            column.label("  » Type: %s" % filletoredge)
        elif len(self.plugs) == 0:
            column.label("No Plug Mesh found!", icon="ERROR")
        else:
            column.label("Multiple Plug Meshes found!", icon="ERROR")
            for plug in self.plugs:
                column.label("  » %s" % plug.name)

        # check subsets

        if self.subsets:
            if len(self.subsets) == 1:
                column.label("Subset: %s" % self.subsets[0].name, icon="FILE_TICK")
                column.label("  » Force Deform: %s " % str(self.subsets[0].MM.forcesubsetdeform))
            else:
                # multiple subsets are fine when there arent any array mods, but could be a problem if the subset array caps have not had their props cleared
                icon = "FILE_TICK" if "ARRAY" not in self.modifiers else "INFO"
                if icon == "FILE_TICK":
                    column.label("Multiple Subsets:", icon=icon)
                else:
                    column.label("Multiple Subsets", icon=icon)
                    column.label("Make sure they aren't just ARRAY caps, that need to have their props cleared!")

                for sub in self.subsets:
                    column.label("  » %s" % sub.name)
                    column.label("    » Force Deform: %s " % str(sub.MM.forcesubsetdeform))

        # check deformers

        if self.deformers:
            if len(self.deformers) == 1:
                column.label("Deformer: %s" % self.deformers[0].name, icon="FILE_TICK")
                column.label("  » Use Deformer: %s" % str(self.deformers[0].MM.usedeformer))
            else:
                column.label("Multiple Deformers found!", icon="ERROR")
                for deformer in self.deformers:
                    column.label("  » %s" % deformer.name)

        # check occluders

        if self.occluders:
            if len(self.occluders) == 1:
                column.label("Occluder: %s" % self.occluders[0].name, icon="FILE_TICK")
            else:
                column.label("Multiple Occluders found!", icon="ERROR")
                for occluder in self.occluders:
                    column.label("  » %s" % occluder.name)


        if self.modifiers or self.empties or self.others:
            column.separator()
            column.label("Advanced")

            # check modifiers

            if self.modifiers:
                if len(self.modifiers) == 1:
                    column.label("Modifier: %s" % self.modifiers[0], icon="MODIFIER")
                else:
                    column.label("Multiple Modifiers:", icon="MODIFIER")
                    for mod in self.modifiers:
                        column.label("  » %s" % mod)

            # check empties

            if self.empties:
                if any([mod in self.modifiers for mod in ["ARRAY", "HOOK"]]):
                    if len(self.empties) == 1:
                        column.label("Empty: %s" % self.empties[0].name, icon="FILE_TICK")
                    else:
                        column.label("Multiple Empties:", icon="FILE_TICK")
                        for empty in self.empties:
                            column.label("  » %s" % empty.name)
                else:
                    if len(self.empties) == 1:
                        column.label("Empty: %s" % self.empties[0].name, icon="INFO")
                        column.label("Empty found, but no ARRAY or HOOK modifiers present!")
                    else:
                        column.label("Multiple Empties", icon="INFO")
                        column.label("Empties found, but no ARRAY or HOOK modifiers present!")
                        for empty in self.empties:
                            column.label("  » %s" % empty.name)

            # check others

            if self.others:
                if any([mod in self.modifiers for mod in ["ARRAY"]]):
                    if len(self.others) == 1:
                        column.label("Other: %s" % self.others[0].name, icon="FILE_TICK")
                    else:
                        column.label("Multiple Others:", icon="FILE_TICK")
                        for other in self.others:
                            column.label("  » %s" % other.name)
                else:
                    if len(self.others) == 1:
                        column.label("Other: %s" % self.others[0].name, icon="INFO")
                        column.label("Other object found, but no ARRAY modifiers present! What is it?")
                    else:
                        column.label("Multiple Others:", icon="INFO")
                        column.label("Other objects found, but no ARRAY modifiers present! What are they?")
                        for other in self.others:
                            column.label("  » %s" % other.name)


        if self.uuids or self.creators:
            column.separator()

            column.label("Extra")

            # check uuids

            if self.uuids:
                if len(self.uuids) == 1:
                    column.label("UUID: %s" % self.uuids[0], icon="FILE_TICK")
                else:
                    column.label("Multiple UUIDs", icon="INFO")
                    for uuid in self.uuids:
                        column.label("  » %s" % uuid)

            # check creators

            if self.creators:
                if len(self.creators) == 1:
                    column.label("Creator: %s" % self.creators[0], icon="SOLO_OFF")
                else:
                    column.label("Multiple Creators", icon="INFO")
                    for creator in self.creators:
                        column.label("  » %s" % creator)

        # ACTIONS

        if self.active.MM.isplughandle:
            box = layout.box()

            column = box.column()
            column.label("Actions")

            if self.deformers or self.occluders or self.others:
                column.prop(self, "hidesupportobjs")

            column.prop(self, "generateuuid")

    def invoke(self, context, event):
        # initialize
        self.generateuuid = False

        self.active = m3.get_active()

        self.uuids = []
        self.handles = []
        self.plugs = []
        self.subsets = []
        self.deformers = []
        self.occluders = []
        self.empties = []
        self.others = []
        self.modifiers = []
        self.creators = []

        print(20 * "-")
        print("PLUG OBJECTS")

        if self.active:
            self.get_props(self.active)

            self.uuids, self.handles, self.plugs, self.subsets, self.deformers, self.occluders, self.others, self.empties, self.modifiers, self.creators = self.append(self.active, self.uuids, self.handles, self.plugs, self.subsets, self.deformers, self.occluders, self.others, self.empties, self.modifiers, self.creators)

            if self.active.children:
                children = list(self.active.children)

                while children:
                    child = children[0]
                    self.get_props(child)
                    self.uuids, self.handles, self.plugs, self.subsets, self.deformers, self.occluders, self.others, self.empties, self.modifiers, self.creators = self.append(child, self.uuids, self.handles, self.plugs, self.subsets, self.deformers, self.occluders, self.others, self.empties, self.modifiers, self.creators)

                    children.extend(list(child.children))
                    children.pop(0)

            # force unique elements
            self.uuids = list(set(self.uuids))
            self.modifiers = list(set(self.modifiers))
            self.creators = list(set(self.creators))

            print(5 * "-")
            print("SUMMARY\n")

            print("uuids:", self.uuids)
            print("handles:", self.handles)

            # check handle for tris and ngons
            if len(self.handles) == 1:
                handle = self.handles[0]
                self.ngon, self.flipped, deselect = self.check_handle(handle)

                if self.ngon:
                    print(" ! Handle contains N-Gons!")

                if self.flipped:
                    print(" ! Handle polygons are flipped!")

                if deselect:
                    print(" ! Handle faces have been deselected!")

            print("plugs:", self.plugs)
            print("subsets:", self.subsets)
            print("deformers:", self.deformers)
            print("occluders:", self.occluders)
            print("others:", self.others)
            print("empties:", self.empties)

            # always generate unique UUIds for empties, if they don't have UUIds, these are used to set the empty locations when inserting, similar to how the plug handle scale is set
            for obj in self.empties:
                if not obj.MM.uuid:
                    uuid = str(uuid4())
                    obj.MM.uuid = uuid
                    print(" ! Empty ID has been set for %s!" % (obj.name))

            print("modifiers:", self.modifiers)
            print("creators:", self.creators)


            # increase the dialog width to make room for long labels providing hints
            wide = True if len(self.subsets) > 1 and "ARRAY" in self.modifiers else False

            if not wide:  # prevent a previous True from being overwritten
                wide = True if self.empties and not any([mod in self.modifiers for mod in ["ARRAY", "HOOK"]]) else False

            if not wide:  # prevent a previous True from being overwritten
                wide = True if self.others and not any([mod in self.modifiers for mod in ["ARRAY"]]) else False

            width = 400 if wide else 300

            wm = context.window_manager
            return wm.invoke_props_dialog(self, width=width)

        else:
            popup_message("No active object!")
            return {'CANCELLED'}

    def execute(self, context):
        if self.active.MM.isplughandle and (self.plugs or self.deformers or self.occluders or self.others or self.empties):

            # set deformer and others visibilty based on hide prop
            for obj in self.deformers + self.occluders + self.others:
                obj.hide = self.hidesupportobjs
                obj.hide_render = self.hidesupportobjs

            # always make sure the handle doesnt render, but is visible
            if len(self.handles) == 1:
                self.handles[0].hide = False
                self.handles[0].hide_render = True

            # always make sure the deformer doesnt render
            if len(self.deformers) == 1:
                self.deformers[0].hide_render = True

            # always make sure the occluder does render
            if len(self.occluders) == 1:
                self.occluders[0].hide_render = False

            # always make sure the plug does render and is visible
            if len(self.plugs) == 1:
                self.plugs[0].hide = False
                self.plugs[0].hide_render = False

        # toggle xray on for handle and empties
        if self.active.MM.isplughandle:
            if len(self.handles) == 1:
                for obj in self.handles + self.empties:
                    obj.show_x_ray = True

        # generate new plug UUIDs
        if self.generateuuid:
            if self.active.MM.isplughandle:
                if len(self.handles) == 1:
                    uuid = str(uuid4())

                    for obj in self.handles + self.plugs + self.subsets + self.deformers + self.occluders + self.others:
                        obj.MM.uuid = uuid

        return {'FINISHED'}

    def check_handle(self, handle):
        ngon = False
        flipped = False
        deselect = False

        # create bmesh
        bm = bmesh.new()
        bm.from_mesh(handle.data)

        for f in bm.faces:
            # get vert count
            if len(f.verts) > 4:
                ngon = True

            # dot product with up vector
            dot = f.normal.dot(mathutils.Vector((0, 0, 1)))

            if dot < 0:
                flipped = True

            # deselect handle faces
            if f.select:
                deselect = True

            f.select = False

        bm.select_flush(False)

        bm.to_mesh(handle.data)
        bm.clear()

        return ngon, flipped, deselect

    def append(self, obj, uuids, handles, plugs, subsets, deformers, occluders, others, empties, modifiers, creators):
        if obj.type == "MESH":  # only collect MESH uuds, not empty uuids, which are used differently
            if obj.MM.uuid:
                uuids.append(obj.MM.uuid)

        if obj.MM.isplughandle:
            handles.append(obj)

        if obj.MM.isplug:
            plugs.append(obj)

        if obj.MM.isplugsubset:
            subsets.append(obj)

        if obj.MM.isplugdeformer:
            deformers.append(obj)

        if obj.MM.isplugoccluder:
            occluders.append(obj)

        if not any([obj.MM.isplughandle, obj.MM.isplug, obj.MM.isplugsubset, obj.MM.isplugdeformer, obj.MM.isplugoccluder]):
            if obj.type == "EMPTY":
                empties.append(obj)
            else:
                others.append(obj)

        modifiers.extend([mod.type for mod in obj.modifiers])

        if obj.MM.plugcreator:
            creators.append(obj.MM.plugcreator)

        return uuids, handles, plugs, subsets, deformers, occluders, others, empties, modifiers, creators

    def get_props(self, obj):
        print()
        print("Object Properties of '%s'" % (obj.name))
        print(" » uuid:", obj.MM.uuid)
        print(" » isplughandle:", obj.MM.isplughandle)
        print(" » isplug:", obj.MM.isplug)
        print("  » hasfillet:", obj.MM.hasfillet)
        print(" » isplugdeformer:", obj.MM.isplugdeformer)
        print("  » usedeformer:", obj.MM.usedeformer)
        print(" » isplugsubset:", obj.MM.isplugsubset)
        print("  » forcesubsetdeform:", obj.MM.forcesubsetdeform)
        print(" » isplugoccluder:", obj.MM.isplugoccluder)
        print(" » deformerprecision:", obj.MM.deformerprecision)
        print(" » plugcreaetor:", obj.MM.plugcreator)
