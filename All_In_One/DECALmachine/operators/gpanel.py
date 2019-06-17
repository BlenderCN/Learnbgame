import bpy
from bpy.props import BoolProperty, IntProperty
import bmesh
import math
import mathutils
from .. utils.raycast import find_nearest_normals
from .. utils.decal import get_panel_width, create_float_slice_geometry, create_panel_uvs, finish_panel_decal
from .. utils.collection import sort_into_collections
from .. utils.addon import gp_add_to_edit_mode_group
from .. utils.object import update_local_view
from .. utils.math import get_midpoint
from .. utils.object import flatten
from .. utils.raycast import find_nearest
from .. utils.debug import draw_vector, draw_point


# TODO: stoke order independend panel creation? you'd need to sort the strokes youself, using a proximity check to find the start of the next stroke


class GPanel(bpy.types.Operator):
    bl_idname = "machin3.gpanel"
    bl_label = "MACHIN3: Grease Panel"
    bl_description = "Turns Grease Pencil Strokes into a Panel Decal.\nSHIFT: Connected Panels\nCTRL: Connected Cyclic Panel"
    bl_options = {'REGISTER', 'UNDO'}

    connect: BoolProperty(name="Connect Strokes", default=False)
    segments: IntProperty(name="Segments", default=4, min=0)
    make_cyclic: BoolProperty(name="Make Cyclic", default=False)

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        row = column.row(align=True)
        row.prop(self, "connect", toggle=True)
        if self.connect:
            row.prop(self, "segments")
            row.prop(self, "make_cyclic", toggle=True)

    @classmethod
    def poll(cls, context):
        active = context.active_object
        return (active and active.type == "GPENCIL") or (active and active.DM.decaltype == "PANEL" and not active.DM.decalbackup)

    def invoke(self, context, event):
        gp = context.active_object
        layer = gp.data.layers.active

        if layer and not layer.hide:
            target = gp.parent if gp.parent else self.find_nearest_surface(context, gp, layer)

            if target:
                # initialize
                self.connect = True if event.shift else True if event.ctrl else False
                # self.segments = 4
                self.make_cyclic = True if event.ctrl else False

                self.gpanel(context, gp, layer, target, self.connect, self.segments, self.make_cyclic)

        return {'FINISHED'}

    def execute(self, context):
        gp = context.active_object
        layer = gp.data.layers.active

        if layer and not layer.hide:
            target = gp.parent if gp.parent else self.find_nearest_surface(context, gp, layer)

            if target:
                self.gpanel(context, gp, layer, target, self.connect, self.segments, self.make_cyclic)

        return {'FINISHED'}

    def gpanel(self, context, gp, layer, target, connect=False, segments=4, make_cyclic=True, debug=False):
        mcol = context.collection

        # debug = True
        # debug = False

        if target and layer and not layer.hide:
            layer.hide = True

            frame = layer.active_frame

            # create per stroke sequence lists of point coords
            psequences = []

            for stroke in frame.strokes:
                pseq = []

                for point in stroke.points:
                    pseq.append(point.co)

                psequences.append(pseq)

            # create empty panel decal model, with an empty mesh
            panel = bpy.data.objects.new("Panel Decal", bpy.data.meshes.new("Panel Decal"))

            # panel.matrix_world = gp.matrix_world
            panel.matrix_world = target.matrix_world

            mcol.objects.link(panel)
            mx = panel.matrix_world
            mxi = panel.matrix_world.inverted() @ gp.matrix_world

            # create verts sequences
            bm, sequences, intersection = self.create_vert_sequences(panel.data, psequences, mxi)

            if connect and len(sequences) > 1:
                if make_cyclic:
                    sequences.append(sequences[0])

                connected_sequence = []

                for idx, (verts, _) in enumerate(sequences):
                    if idx < len(sequences) - 1:

                        # end of stroke
                        v_end = verts[-1]
                        v_end_remote = verts[-2]
                        end_dir = v_end_remote.co - v_end.co

                        # start of next stroke
                        v_start = sequences[idx + 1][0][0]
                        v_start_remote = sequences[idx + 1][0][1]
                        start_dir = v_start_remote.co - v_start.co

                        connection_angle = math.degrees(end_dir.angle(start_dir))

                        # create handle using end of previous storke and start of current, skip this at the very first run
                        ico = mathutils.geometry.intersect_line_line(v_start.co, v_start_remote.co, v_end.co, v_end_remote.co)

                        # if the start and end dirs are parallel or close to it, avoid line intersections
                        # if ico is None or 178 <= connection_angle <= 182:  # if the edge and both loop egdes are on the same line or are parallel: _._._ or  _./'¯¯
                            # ico1 = mathutils.geometry.intersect_point_line(v_start.co, v_end.co, v_end_remote.co)[0]
                            # ico2 = mathutils.geometry.intersect_point_line(v_end.co, v_start.co, v_start_remote.co)[0]
                            # ico = (ico1, ico2)

                        # if the start and end dirs are parallel simply connect with a single polygon
                        if ico is None or 178 <= connection_angle <= 182:  # if the edge and both loop egdes are on the same line or are parallel: _._._ or  _./'¯¯
                            # print("single polygon connection")

                            connected_sequence.extend(verts)

                        else:
                            # print("bezier connection")

                            # hco = get_center_between_points(ico[0], ico[1])

                            if debug:
                                draw_point(mx @ ico[0], color=(1, 0, 0))
                                draw_point(mx @ ico[1], color=(0, 1, 0))
                                # draw_point(mx @ hco, color=(1, 1, 0))

                            # add tension
                            handle_end = v_end.co + (ico[0] - v_end.co) * 0.7
                            handle_start = v_start.co + (ico[1] - v_start.co) * 0.7

                            # create bezier locations
                            # beziercos = mathutils.geometry.interpolate_bezier(v_end.co, ico[0], ico[1], v_start.co, 6)
                            beziercos = mathutils.geometry.interpolate_bezier(v_end.co, handle_end, handle_start, v_start.co, segments + 2)
                            # beziercos = mathutils.geometry.interpolate_bezier(v_end.co, hco, hco, v_start.co, 6)

                            connected_sequence.extend(verts)

                            # created vertices at those bezier locations
                            for co in beziercos[1:-1]:
                                if debug:
                                    draw_point(mx @ co, color=(1, 1, 1))

                                v = bm.verts.new()
                                v.co = co

                                connected_sequence.append(v)
                                intersection.append(v)

                    # for the last sequence, just extend with the stroke's verts, but only make_cyclic is False
                    elif not make_cyclic:
                        connected_sequence.extend(verts)


                # if connect is used, the nex sequnces list will contain a single vert list
                sequences = [(connected_sequence, make_cyclic)]


            # get normals
            normals, bmt = find_nearest_normals(bm, target.evaluated_get(context.evaluated_depsgraph_get()).to_mesh(), debug=False)


            # connect the verts for each stroke for each stroke
            self.create_edges_from_strokes(bm, sequences)

            # determine panel width, enfore global width, independent of object scaling
            width = get_panel_width(panel, context.scene)

            # create panel faces
            geo = create_float_slice_geometry(bm, panel.matrix_world, sequences, normals, width=width)

            # blast the intersection edge loop
            bmesh.ops.delete(bm, geom=intersection, context="VERTS")

            bmt.free()

            # create UVs and finish bmesh
            create_panel_uvs(bm, geo, panel, width=width)

            # finsh the panel
            finish_panel_decal(context, panel, target, None)

            # sort panel into collections
            sort_into_collections(context.scene, panel)

            # deselect, select and make active
            gp.select_set(False)
            panel.select_set(True)
            context.view_layer.objects.active = panel

            # add edit mode group
            gp_add_to_edit_mode_group(context, panel)

            # local view update
            update_local_view(context.space_data, [(panel, True)])


    def create_edges_from_strokes(self, bm, sequences):
        for verts, _ in sequences:
            for idx, v in enumerate(verts):
                if idx < len(verts) - 1:
                    bm.edges.new([v, verts[idx +1]])

    def create_vert_sequences(self, mesh, psequences, mx):
        bm = bmesh.new()
        bm.from_mesh(mesh)

        sequences = []
        intersection = []

        for pseq in psequences:
            seq = []

            for co in pseq:
                v = bm.verts.new()
                v.co = mx @ co
                seq.append(v)
                intersection.append(v)

            # (verts, cyclic) tuple - all of the strokes are non-cyclic of course
            sequences.append((seq, False))

        bm.verts.index_update()

        return bm, sequences, intersection

    def find_nearest_surface(self, context, gp, layer, debug=False):
        if debug:
            print("GP is not parented, finding target by surface proximity to first point in first stroke.")

        frame = layer.active_frame

        try:
            point = frame.strokes[0].points[0]
        except:
            point = None

            if debug:
                print("Active GP layer has no strokes or stroke has no points.")

        if point:
            origin = gp.matrix_world @ point.co

            if debug:
                draw_point(origin, color=(1, 0, 0))

            visible = [obj for obj in context.visible_objects if obj.type == "MESH" and not obj.DM.isdecal]

            target, _, _, _, _ = find_nearest(visible, origin, debug=debug)

            return target
