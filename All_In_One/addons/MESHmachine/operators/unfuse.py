import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, EnumProperty
import bmesh
from ..utils.graph import build_mesh_graph
from ..utils.core import get_2_rails
from ..utils.ui import popup_message, step_enum, draw_init, draw_end, draw_title, draw_prop
from ..utils.debug import debug_sweeps, vert_debug_print
from ..utils.developer import output_traceback
from ..utils import MACHIN3 as m3



class OperatorSettings:
    # see https://blender.stackexchange.com/questions/6520/should-an-operator-remember-its-last-used-settings-when-invoked
    _settings = {}

    def save_settings(self):
        for d in dir(self.properties):
            if d in ['bl_rna', 'rna_type', 'reverse']:
                continue
            try:
                self.__class__._settings[d] = self.properties[d]
            except KeyError:
                # catches __doc__ etc.
                continue

    def load_settings(self):
        # what exception could occur here??
        for d in self.__class__._settings:
            self.properties[d] = self.__class__._settings[d]


class Unfuse(bpy.types.Operator, OperatorSettings):
    bl_idname = "machin3.unfuse"
    bl_label = "MACHIN3: Unfuse"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Reconstruct chamfer from Rounded Bevel"

    sharps = BoolProperty(name="Set Sharps", default=True)
    bweights = BoolProperty(name="Set Bevel Weights", default=False)
    bweight = FloatProperty(name="Weight", default=1, min=0, max=1)

    # hiddden
    cyclic = BoolProperty(name="Cyclic", default=False)

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        column = layout.column()

        column.prop(self, "sharps")

        row = column.row()
        row.prop(self, "bweights")
        row.prop(self, "bweight")

    @classmethod
    def poll(cls, context):
        bm = bmesh.from_edit_mesh(context.active_object.data)
        return len([f for f in bm.faces if f.select]) >= 1

    def draw_HUD(self, args):
        draw_init(self, args)

        draw_title(self, "Unfuse")

        draw_prop(self, "Set Sharps", self.sharps, key="toggle S")
        draw_prop(self, "Set BWeights", self.bweights, offset=18, key="toggle B")
        if self.bweights:
            draw_prop(self, "BWeight", self.bweight, offset=18, key="ALT scroll UP/DOWN")
        self.offset += 10

        draw_end()

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        events = ['WHEELUPMOUSE', 'UP_ARROW', 'ONE', 'WHEELDOWNMOUSE', 'DOWN_ARROW', 'TWO', 'S', 'B']

        if event.type in events:

            # CONTROL segments, method, handlemethod and capdissolveangle

            if event.type in {'WHEELUPMOUSE', 'UP_ARROW', 'ONE'} and event.value == 'PRESS':
                if event.alt:
                    self.bweight += 0.1

            elif event.type in {'WHEELDOWNMOUSE', 'DOWN_ARROW', 'TWO'} and event.value == 'PRESS':
                if event.alt:
                    self.bweight -= 0.1

            # TOGGLE sharps, bweights and reverse

            elif event.type == 'S' and event.value == "PRESS":
                self.sharps = not self.sharps

            elif event.type == 'B' and event.value == "PRESS":
                self.bweights = not self.bweights

            # modal unfuse
            try:
                self.ret = self.main(self.active, modal=True)

                # success
                if self.ret:
                    self.save_settings()
                # caught an error
                else:
                    bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
                    return {'FINISHED'}
            # unexpected error
            except:
                output_traceback(self)
                bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
                mode = m3.get_mode()
                if mode == "OBJECT":
                    m3.set_mode("EDIT")
                return {'FINISHED'}

        # VIEWPORT control

        elif event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}

        # FINISH

        elif event.type in {'LEFTMOUSE', 'SPACE'}:
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
            return {'FINISHED'}

        # CANCEL

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel_modal()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def cancel_modal(self, removeHUD=True):
        if removeHUD:
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')

        m3.set_mode("OBJECT")
        self.initbm.to_mesh(self.active.data)
        m3.set_mode("EDIT")

    def invoke(self, context, event):
        self.load_settings()

        self.active = m3.get_active()

        # make sure the current edit mode state is saved to obj.data
        self.active.update_from_editmode()

        # save this initial mesh state, this will be used when canceling the modal and to reset it for each mousemove event
        self.initbm = bmesh.new()
        self.initbm.from_mesh(self.active.data)

        # mouse positions
        self.mouse_x = self.init_mouse_x = self.fixed_mouse_x = event.mouse_region_x
        self.mouse_y = self.init_mouse_y = self.fixed_mouse_y = event.mouse_region_y

        # first run, this is necessary if there's no mouse movement event
        try:
            self.ret = self.main(self.active, modal=True)
            if self.ret:
                self.save_settings()
            else:
                self.cancel_modal(removeHUD=False)
                return {'FINISHED'}
        except:
            output_traceback(self)
            mode = m3.get_mode()
            if mode == "OBJECT":
                m3.set_mode("EDIT")
            return {'FINISHED'}

        args = (self, context)
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (args, ), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        active = m3.get_active()

        try:
            self.main(active)
        except:
            output_traceback(self)

        return {'FINISHED'}

    def main(self, active, modal=False):
        debug = True
        debug = False

        if debug:
            m3.clear()
            m3.debug_idx()

        m3.set_mode("OBJECT")

        if modal:
            self.initbm.to_mesh(active.data)

        # create bmesh
        bm = bmesh.new()
        bm.from_mesh(active.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        bw = bm.edges.layers.bevel_weight.verify()

        mg = build_mesh_graph(bm, debug=debug)
        verts = [v for v in bm.verts if v.select]
        faces = [f for f in bm.faces if f.select]

        sweeps = get_sweeps(bm, mg, verts, faces, debug=debug)

        if sweeps:
            chamfer_faces = unfuse(bm, faces, sweeps, debug=debug)

            if chamfer_faces:
                # set boundary rail sharps
                chamfer_verts = [v for v in bm.verts if v.select]
                chamfer_mg = build_mesh_graph(bm, debug=debug)

                ret = get_2_rails(bm, chamfer_mg, chamfer_verts, chamfer_faces, False, debug=debug)

                if ret:
                    chamfer_rails, self.cyclic = ret

                    if any([self.sharps, self.bweights]):
                        if self.sharps:
                            bpy.context.object.data.show_edge_sharp = True
                        if self.bweights:
                            bpy.context.object.data.show_edge_bevel_weight = True

                        if self.cyclic:
                            chamfer_rails[0].append(chamfer_rails[0][0])
                            chamfer_rails[1].append(chamfer_rails[1][0])

                        for rail in chamfer_rails:
                            for idx, rv in enumerate(rail):
                                if idx == len(rail) - 1:
                                    break
                                else:
                                    re = bm.edges.get([rv, rail[idx + 1]])
                                    if self.sharps:
                                        re.smooth = False
                                    if self.bweights:
                                        re[bw] = self.bweight

                # returning and wether ret is True or not, because we want to at least push back the unfused state
                # if we dont do that, any error messages, like ngon warings in get_2_rails, doesnt make sense, as its not clear what ngon is meant
                # see 065_unfuse_fail for an example scenario
                bm.to_mesh(active.data)

                m3.set_mode("EDIT")
                # m3.set_mode("VERT")
                # m3.set_mode("EDGE")
                return True

        m3.set_mode("EDIT")

        return False


def unfuse(bm, faces, sweeps, debug=False):
    edgeloops = []
    edgeloopverts = []

    for sweep in sweeps[1:-1]:
        e = bm.edges.get(sweep)
        edgeloops.append(e)
        edgeloopverts.extend([v for v in sweep])

        # if debug:
            # e.select = True

        # get BMLoop that points to the right direction
        for loop in e.link_loops:
            # stop when reach the end of the edge loop
            while len(loop.vert.link_edges) == 4:
                # jump between BMLoops to the next BMLoop we need
                loop = loop.link_loop_prev.link_loop_radial_prev.link_loop_prev

                next_e = loop.edge
                if next_e in edgeloops:  # cyclicity
                    break
                else:
                    # following edge in the edge loop
                    edgeloops.append(next_e)
                    edgeloopverts.extend([v for v in next_e.verts if v not in edgeloopverts])
                    # if debug:
                        # next_e.select = True

    # get all the faces and select them, this way the chamfer will be selected after the edges and verts are removed
    removedgeloops = []
    edgeloopfaces = []
    for e in edgeloops:
        for f in e.link_faces:
            if f not in edgeloopfaces:
                if len(f.verts) == 4:  # some edges may go further than desired, see 065_unfuse_fail, this is just aimple check to only include quads, it may still contain undesired polys however
                    edgeloopfaces.append(f)
                    f.select = True
                else:
                    removedgeloops.append(e)

    # remove the undesired edges and verts
    for e in removedgeloops:
        if e in edgeloops:
            edgeloops.remove(e)
        for v in e.verts:
            if v in edgeloopverts:
                edgeloopverts.remove(v)

    # get all th other faces
    otherfaces = [f for f in bm.faces if f not in edgeloopfaces]

    try:
        bmesh.ops.dissolve_edges(bm, edges=edgeloops)
        bmesh.ops.dissolve_verts(bm, verts=edgeloopverts)
        bm.verts.ensure_lookup_table()

        # without the flushing, there will only be edges selected, not faces
        bm.select_flush(True)

        # the flusing may select faces not part of the chamfer, due to all a face's verts being selected. this is undesired behavior, so deselect the other faces.
        for f in otherfaces:
            if f.is_valid:
                f.select = False

        return [f for f in bm.faces if f.select]
    except:
        # print("You can't Unfuse bevels with triangular coners")
        popup_message(["You can't unfuse bevels with triangular coners", "Turn them into Quad Corners first!"], title="Illegal Selection")
        return


def get_sweeps(bm, mg, verts, faces, debug=False):
    # ngons and tris
    ngons = [f for f in faces if len(f.verts) > 4]
    tris = [f for f in faces if len(f.verts) < 4]

    if ngons:
        # print("Selection includes ngons, aborting")
        popup_message("Selection includes ngons, aborting", title="Illegal Selection")
        return
    elif tris:
        # print("Selection includes tris, aborting")
        popup_message("Selection includes tris, aborting", title="Illegal Selection")
        return

    if len(faces) < 2:
        # print("Selection has less than 2 faces, aborting")
        popup_message("Selection has less than 2 faces, aborting", title="Illegal Selection")
        return
    elif len(verts) < 6:
        # print("Selection has less than 6 vertices selected, aborting")
        popup_message("Selection has less than 6 verts, aborting", title="Illegal Selection")
        return
    else:
        if debug:
            print("Determining rail direction via vert hops")

    corners = [bm.verts[idx] for idx in mg if bm.verts[idx].select and sum([vselect for _, vselect, eselect in mg[idx] if eselect]) == 2]

    # if no corners are found, its a cyclic selection! this shouldn't happen
    if len(corners) == 0:  # < 0 ?
        # print("Cyclic selections not supported")
        popup_message("Cyclic selections are not supported, aborting", title="Illegal Selection")
        return

    # get the short sides, the sides where its one hop to the next corner
    # c1 - o - o - c3
    # |    |   |   |  X sweeps
    # c2 - o - o - c4
    #    2  rails

    # pick one corner
    c1 = corners[0]
    corners.remove(c1)

    c2 = [c for c in corners if c.index in [idx for idx, _, eselect in mg[c1.index] if eselect]]

    # if nothing can be found for c2, its because c1 and c2 arent seperated by one hop, it's not a chamfer selection
    if not c2:
        # print("Selection is not a poly strip aborting")
        popup_message("Selection is not a polysrip, aborting", title="Illegal Selection")
        return
    else:
        c2 = c2[0]
        corners.remove(c2)

        # walk the polygons, this will establish the sequence of sweeps (of the poly strip)

        rail1 = [c1]
        rail2 = [c2]

        sweeps = [(c1, c2)]

        # TODO: check if all polygons in the selection are quads? abort if not? correct if not?
        if debug:
            print("rail1 start:", rail1[-1].index)
            print("rail2 start:", rail2[-1].index)

        not_yet_walked = [f for f in faces]
        while not_yet_walked:
            v1 = rail1[-1]
            v2 = rail2[-1]
            sweep = bm.edges.get([v1, v2])

            if debug:
                print("sweep:", sweep.index)

            current_face = [f for f in sweep.link_faces if f.select and f in not_yet_walked]

            if current_face:
                cf = current_face[0]
                if debug:
                    print("current face:", cf.index)
                not_yet_walked.remove(cf)

                next_verts = [v for v in cf.verts if v not in rail1 + rail2]
                if debug:
                    print("next verts:", [v.index for v in next_verts])

                # TODO: i dont think you need to iterate over all verts here???
                # rail1_next_vert = [bm.verts[idx] for idx, _, _ in mg[v1.index] if bm.verts[idx] in next_verts][0]
                rail1_next_vert = [e.other_vert(v1) for e in v1.link_edges if e.other_vert(v1) in next_verts][0]
                if debug:
                    print("next vert 1:", rail1_next_vert.index)

                # rail2_next_vert = [bm.verts[idx] for idx, _, _ in mg[v2.index] if bm.verts[idx] in next_verts][0]
                rail2_next_vert = [e.other_vert(v2) for e in v2.link_edges if e.other_vert(v2) in next_verts][0]
                if debug:
                    print("next vert 2:", rail2_next_vert.index)
                    print()

                rail1.append(rail1_next_vert)
                rail2.append(rail2_next_vert)
                sweeps.append((rail1_next_vert, rail2_next_vert))
            else:
                break

    #TODO: check if any rail edges are non-manifold
    if debug:
        print("rails:")
        rail1ids = [str(v.index) for v in rail1]
        rail2ids = [str(v.index) for v in rail2]
        print(" » ".join(rail1ids))
        print(" » ".join(rail2ids))

        print()
        print("sweeps:")
        sweepids = [(str(v1.index), str(v2.index)) for v1, v2 in sweeps]
        print(sweepids)

    return sweeps
