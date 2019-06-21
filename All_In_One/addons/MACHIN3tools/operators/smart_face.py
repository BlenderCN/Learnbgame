import bpy
from bpy.props import FloatProperty, BoolProperty
import bmesh
from .. utils import MACHIN3 as m3


class SmartFace(bpy.types.Operator):
    bl_idname = "machin3.smart_face"
    bl_label = "MACHIN3: Smart Face"
    bl_options = {'REGISTER', 'UNDO'}

    automerge: BoolProperty(name="Merge to close-by Vert", default=True)

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        if len(self.selverts) == 1:
            column.prop(self, "automerge")


    @classmethod
    def poll(cls, context):
        return m3.get_mode() in ["VERT", "EDGE", "FACE"]

    def execute(self, context):
        mode = m3.get_mode()
        active = m3.get_active()

        if mode in ["VERT", "EDGE"]:
            self.selverts = m3.get_selection("VERT")

            if self.selverts:

                # F3

                if 1 <= len(self.selverts) <= 2:
                    self.f3(active, self.automerge)

                # Blender's face creation

                elif len(self.selverts) > 2:
                    bpy.ops.mesh.edge_face_add()

        elif mode == "FACE":
            selfaces = m3.get_selection("FACE")

            # DUPLICATE and SEPARATE

            if selfaces:
                bpy.ops.mesh.duplicate()
                bpy.ops.mesh.separate(type='SELECTED')

                m3.set_mode("OBJECT")
                sel = context.selected_objects
                sel.remove(active)
                active.select_set(False)
                m3.make_active(sel[0])
                m3.set_mode("EDIT")

        return {'FINISHED'}

    def f3(self, active, automerge):
        bm = bmesh.from_edit_mesh(active.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        verts = [v for v in bm.verts if v.select]

        if len(verts) == 1:
            vs = verts[0]

            faces = vs.link_faces
            open_edges = [e for e in vs.link_edges if not e.is_manifold]

            if faces and len(open_edges) == 2:

                # calculate the location of the new vert
                e1 = open_edges[0]
                e2 = open_edges[1]

                v1_other = e1.other_vert(vs)
                v2_other = e2.other_vert(vs)

                v1_dir = v1_other.co - vs.co
                v2_dir = v2_other.co - vs.co

                # create new vert
                v_new = bm.verts.new()
                v_new.co = vs.co + v1_dir + v2_dir

                # create new face
                f = bm.faces.new([vs, v2_other, v_new, v1_other])
                f.smooth = any([f.smooth for f in faces])

                # recalc the face normal
                bmesh.ops.recalc_face_normals(bm, faces=[f])

                # automatically merge the newly created vert to the closest non manifold vert if it's closer than the 2 other verts are
                if automerge:
                    nonmanifoldverts = [v for v in bm.verts if any([not e.is_manifold for e in v.link_edges]) and v not in [vs, v_new, v1_other, v2_other]]

                    if nonmanifoldverts:
                        distance = min([((v_new.co - v.co).length, v) for v in nonmanifoldverts], key=lambda x: x[0])
                        threshold = min([(v_new.co - v.co).length * 0.5 for v in [v1_other, v2_other]])

                        if distance[0] < threshold:
                            v_closest = distance[1]

                            # merge new to closest, NOTE: in this verts order, the v_new vert stays alive, which is perfect
                            bmesh.ops.pointmerge(bm, verts=[v_new, v_closest], merge_co=v_closest.co)


                # if any of the other two verts has 4 edges, at least one of them non-manifold, select it. first come first serve.
                if any([len(v1_other.link_edges) == 4, len(v2_other.link_edges) == 4]):
                    if len(v1_other.link_edges) == 4 and any([not e.is_manifold for e in v1_other.link_edges]):
                        vs.select = False
                        v1_other.select = True
                        vs = v1_other

                    elif len(v2_other.link_edges) == 4 and any([not e.is_manifold for e in v2_other.link_edges]):
                        vs.select = False
                        v2_other.select = True
                        vs = v2_other
                    else:
                        vs.select = False
                        bm.select_flush(False)

                    bm.select_flush(False)

                    # for the newly selected vert, check if there is an other vert with 4 edges, select it if so
                    # plus, with the automerge, you need to also chekc if of those 4 edegs, two are non manifold, this avoids selecting verts with 4 non manifolds
                    second_vs = [e.other_vert(vs) for e in vs.link_edges if not e.is_manifold and len(e.other_vert(vs).link_edges) == 4 and sum([not e.is_manifold for e in e.other_vert(vs).link_edges]) == 2]

                    if second_vs:
                        second_v = second_vs[0]
                        second_v.select = True

                        bm.select_flush(True)

                else:
                    vs.select = False
                    # v_new.select = True  # it's better to not have anything selected, than select a vert that's only useful in some circumstances

                    bm.select_flush(False)


        if len(verts) == 2:
            v1 = verts[0]
            v2 = verts[1]
            e12 = bm.edges.get([v1, v2])

            faces = [f for v in [v1, v2] for f in v.link_faces]

            v1_edges = [e for e in v1.link_edges if e != e12 and not e.is_manifold]
            v2_edges = [e for e in v2.link_edges if e != e12 and not e.is_manifold]

            if v1_edges and v2_edges:
                v1_other = v1_edges[0].other_vert(v1)
                v2_other = v2_edges[0].other_vert(v2)

                # create new face
                if v1_other == v2_other:
                    f = bm.faces.new([v1, v1_other, v2])
                else:
                    f = bm.faces.new([v1, v1_other, v2_other, v2])

                f.smooth = any([f.smooth for f in faces])

                # recalc the face normal
                bmesh.ops.recalc_face_normals(bm, faces=[f])

                v1.select = False
                v2.select = False

                # only select the new verts if they have 4 edges and at least one of them non manifold
                if len(v1_other.link_edges) == 4 and any([not e.is_manifold for e in v1_other.link_edges]):
                    v1_other.select = True

                if len(v2_other.link_edges) == 4 and any([not e.is_manifold for e in v2_other.link_edges]):
                    v2_other.select = True

                bm.select_flush(False)

                # if there is one vert left, check if it has an other vert with 4 edges
                if v1_other.select and not v2_other.select:
                    v1 = v1_other
                    v2 = v2_other

                    second_vs = [e.other_vert(v1) for e in v1.link_edges if not e.is_manifold and e.other_vert(v1) != v2 and len(e.other_vert(v1).link_edges) == 4]
                    if second_vs:
                        second_v = second_vs[0]
                        second_v.select = True

                elif v2_other.select and not v1_other.select:
                    v1 = v1_other
                    v2 = v2_other

                    second_vs = [e.other_vert(v2) for e in v2.link_edges if not e.is_manifold and e.other_vert(v2) != v1 and len(e.other_vert(v2).link_edges) == 4]
                    if second_vs:
                        second_v = second_vs[0]
                        second_v.select = True

                bm.select_flush(True)


        bmesh.update_edit_mesh(active.data)
