import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, EnumProperty
import bmesh
import mathutils
from . fuse import fuse_surface, tensionpresetitems
from ..utils.graph import build_mesh_graph
from ..utils.core import init_sweeps, create_splines
from ..utils.loop import topo_loop
from ..utils.debug import debug_sweeps, vert_debug_print
from ..utils.ui import popup_message, step_enum, draw_init, draw_end, draw_title, draw_prop, wrap_mouse
from ..utils.developer import output_traceback
from ..utils import MACHIN3 as m3



class OperatorSettings:
    # see https://blender.stackexchange.com/questions/6520/should-an-operator-remember-its-last-used-settings-when-invoked
    _settings = {}

    def save_settings(self):
        for d in dir(self.properties):
            if d in ['bl_rna', 'rna_type', 'turn', 'allowmodalwidth', 'allowmodaltension']:
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


turnitems = [("1", "1", ""),
             ("2", "2", ""),
             ("3", "3", "")]


class QuadCorner(bpy.types.Operator, OperatorSettings):
    bl_idname = "machin3.quad_corner"
    bl_label = "MACHIN3: Quad Corner"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Convert a triangular Bevel Corner into Quad Corner"

    width = FloatProperty(name="Width", default=0.01, min=0.0001, max=1, precision=2, step=0.1)
    tension = FloatProperty(name="Tension", default=0.55, min=0.01, max=2, step=0.1)
    tension_preset = EnumProperty(name="Tension Presets", items=tensionpresetitems, default="CUSTOM")

    turn = EnumProperty(name="Turn", items=turnitems, default="1")

    # hidden
    single = BoolProperty(name="Single", default=False)

    # modal
    allowmodalwidth = BoolProperty(default=True)
    allowmodaltension = BoolProperty(default=False)

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        column = layout.column()

        column.prop(self, "width")

        if not self.single:
            column.prop(self, "tension")
            row = column.row()
            row.prop(self, "tension_preset", expand=True)

        column.separator()

        row = column.row()
        row.label("Corner")
        row.prop(self, "turn", expand=True)

    @classmethod
    def poll(cls, context):
        bm = bmesh.from_edit_mesh(context.active_object.data)
        return len([f for f in bm.faces if f.select]) >=1

    def draw_HUD(self, args):
        draw_init(self, args)

        draw_title(self, "Quad Corner")

        draw_prop(self, "Width", self.width, active=self.allowmodalwidth, key="move LEFT/RIGHT, toggle W")

        if not self.single:
            draw_prop(self, "Tension", self.tension, offset=18, decimal=2, active=self.allowmodaltension, key="move UP/DOWN, toggle T, presets %s, X, C, V" % ("Z" if m3.MM_prefs().keyboard_layout == "QWERTY" else "Y"))

        self.offset += 10

        draw_prop(self, "Turn", self.turn, offset=18, key="scroll UP/DOwn")

        draw_end()


    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        events = ['MOUSEMOVE', 'WHEELUPMOUSE', 'UP_ARROW', 'ONE', 'WHEELDOWNMOUSE', 'DOWN_ARROW', 'TWO', 'Y', 'Z', 'X', 'C', 'V']

        # only consider MOUSEMOVE as a trigger, when modalwidth or modaltension are actually active
        if any([self.allowmodalwidth, self.allowmodaltension]):
            events.append('MOUSEMOVE')

        if event.type in events:

            # CONTROL width and tension

            if event.type == 'MOUSEMOVE':
                delta_x = self.mouse_x - self.init_mouse_x  # bigger if going to the right
                delta_y = self.mouse_y - self.init_mouse_y  # bigger if going to the up

                if self.allowmodalwidth:
                    wrap_mouse(self, context, event, x=True)

                    self.width = self.init_width + delta_x * 0.001

                if self.allowmodaltension:
                    wrap_mouse(self, context, event, y=True)

                    self.tension_preset = "CUSTOM"
                    self.tension = delta_y * 0.001 + self.init_tension

            # CONTROL turn/corner

            elif event.type in {'WHEELUPMOUSE', 'UP_ARROW', 'ONE'} and event.value == 'PRESS':
                self.turn = step_enum(self.turn, turnitems, 1)

            elif event.type in {'WHEELDOWNMOUSE', 'DOWN_ARROW', 'TWO'} and event.value == 'PRESS':
                self.turn = step_enum(self.turn, turnitems, -1)

            # SET tension presets

            elif (event.type == 'Y' and event.value == "PRESS") or (event.type == 'Z' and event.value == "PRESS"):
                self.tension_preset = "0.55"

            elif event.type == 'X' and event.value == "PRESS":
                self.tension_preset = "0.7"

            elif event.type == 'C' and event.value == "PRESS":
                self.tension_preset = "1"

            elif event.type == 'V' and event.value == "PRESS":
                self.tension_preset = "1.33"

            # modal quad corner
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
                return {'FINISHED'}

        # TOGGLE modal width and tension

        elif event.type == 'W' and event.value == "PRESS":
            self.allowmodalwidth = not self.allowmodalwidth

        elif event.type == 'T' and event.value == "PRESS":
            self.allowmodaltension = not self.allowmodaltension

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

    def cancel_modal(self):
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

        # initial witdth and tension, necessary because they are non-zero values and so have to be added to the mouse movementse
        self.init_width = self.width
        self.init_tension = self.tension

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
        if self.tension_preset != "CUSTOM":
            self.tension = float(self.tension_preset)

        debug = True
        debug = False

        if debug:
            m3.clear()
            m3.debug_idx()

        m3.set_mode("OBJECT")

        # reset the mesh the initial state
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
        edges = [e for e in bm.edges if e.select]
        faces = [f for f in bm.faces if f.select]

        if len(faces) == 1:
            self.single = True
        else:
            self.single = False

        ret = get_3_sides(bm, mg, verts, edges, faces, self.turn, debug=debug)

        if ret:
            sides, corners = ret

            smooth, sidesharps, cornersharps, sidebweights, cornerbweights = self.check_smooth_sharps_bweights(bm, bw, faces, sides, corners, debug=debug)

            rails, other_vs = get_rails(bm, faces, sides, self.width, debug=debug)

            # disabling freestyle, becuase get_rails creates 2 new edges, which can't be access via active.data yet and bmesh cant access  the freestyle layer either
            sweeps = init_sweeps(bm, active, rails, edges=False, freestyle=False, avg_face_normals=False, debug=debug)

            # debug_sweeps(sweeps, edges=False)

            self.get_loops(bm, faces, sweeps, debug=debug)
            # debug_sweeps(sweeps, edges=False)

            adjust_width(sweeps, self.width)
            create_handles(bm, sweeps, tension=self.tension, debug=debug)

            spline_sweeps = create_splines(bm, sweeps, segments=len(sides[2]) - 1, debug=debug)
            self.clean_up(bm, sweeps, faces, magicloop=False, initialfaces=True, debug=debug)

            # add the verts of the second side to the sweeps(+ the first of the third side, the third corner)
            # this is needed for the final row of faces, which connects to existing geo
            spline_sweeps.append(sides[1])
            spline_sweeps[-1].append(sides[2][0])

            fuse_faces, _ = fuse_surface(bm, spline_sweeps, smooth=smooth, capholes=False, select=False, debug=debug)

            self.set_sharps_bweights(bm, bw, spline_sweeps, sidesharps, cornersharps, sidebweights, cornerbweights, fuse_faces)

            rebuild_corner_faces(bm, sides, rails, spline_sweeps, self.single, smooth, debug=debug)
            # debug_sweeps(sweeps, edges=False)

        bm.to_mesh(active.data)

        m3.set_mode("EDIT")
        # m3.set_mode("VERT")

        if ret:
            return True
        else:
            return False

    def set_sharps_bweights(self, bm, bw, spline_sweeps, sidesharps, cornersharps, sidebweights, cornerbweights, fuse_faces):
        if any([sidesharps, cornersharps, sidebweights, cornerbweights]):
            for sweep in spline_sweeps:
                sweep[0].select = True
                sweep[-1].select = True

            for v in spline_sweeps[0]:
                v.select = True

            for v in spline_sweeps[-1]:
                v.select = True

            bm.select_flush(True)

            sideedges = [e for e in bm.edges if e.select]
            corneredges = [e for v in [spline_sweeps[0][0], spline_sweeps[0][-1]] for e in v.link_edges if e not in sideedges]

            # we need to add the edges of spline_sweeps[0] to the corner edges, otherwiese there's a gap
            for ssidx, v in enumerate(spline_sweeps[0]):
                if ssidx == len(spline_sweeps[0]) - 1:
                    break
                corneredges.append(bm.edges.get([v, spline_sweeps[0][ssidx + 1]]))

            for e in sideedges:
                if sidesharps:
                    e.smooth = False
                if sidebweights:
                    e[bw] = 1

            for e in corneredges:
                if cornersharps:
                    e.smooth = False
                if cornerbweights:
                    e[bw] = 1

        # select the fuse faces
        for f in fuse_faces:
            f.select = True

    def check_smooth_sharps_bweights(self, bm, bw, faces, sides, corners, debug=False):
        smooth = any([f.smooth for f in faces])

        sideedges = []
        for sidx, side in enumerate(sides):
            for vidx, v in enumerate(side):
                if vidx == len(side) - 1:
                    if sidx == 0:
                        sideedges.append(bm.edges.get([v, sides[1][0]]))
                    elif sidx == 1:
                        sideedges.append(bm.edges.get([v, sides[2][0]]))
                    else:
                        sideedges.append(bm.edges.get([v, sides[0][0]]))
                    break
                sideedges.append(bm.edges.get([v, side[vidx + 1]]))

        corneredges = []
        for v in corners:
            corneredges += [e for e in v.link_edges if e not in sideedges]


        sidesharps = False if all([e.smooth for e in sideedges]) else True
        cornersharps = False if all([e.smooth for e in corneredges]) else True

        sidebweights = True if any([e[bw] > 0 for e in sideedges]) else False
        cornerbweights = True if any([e[bw] > 0 for e in corneredges]) else False

        if debug:
            print("side sharps:", sidesharps)
            print("corner sharps:", cornersharps)

            print("side bweights:", sidebweights)
            print("corner bweights:", cornerbweights)

        return smooth, sidesharps, cornersharps, sidebweights, cornerbweights


    def get_loops(self, bm, faces, sweeps, debug=False):
        if debug:
            print()
        # debug = [4]
        # debug = [42, 73]

        for sweep in sweeps:
            for idx, v in enumerate(sweep["verts"]):
                vert_debug_print(debug, v, "\n" + str(v.index), end=" » ")

                ccount = len(sweep["loop_candidates"][idx])
                vert_debug_print(debug, v, "\nloop count: " + str(ccount))

                sweep["loops"].append(topo_loop(v, sweep["loop_candidates"][idx], debug=debug))
                sweep["loop_types"].append("TOPO")

    def clean_up(self, bm, sweeps, faces, magicloop=True, initialfaces=True, debug=False):
        # remove the magic loops
        if magicloop:
            magic_loops = []

            for sweep in sweeps:
                for idx, lt in enumerate(sweep["loop_types"]):
                    if lt in ["MAGIC", "PROJECTED"]:
                        magic_loops.append(sweep["loops"][idx])

            magic_loop_ids = [str(l.index) for l in magic_loops]

            # 1: DEL_VERTS, 2: DEL_EDGES, 3: DEL_ONLYFACES, 4: DEL_EDGESFACES, 5: DEL_FACES, 6: DEL_ALL, 7: DEL_ONLYTAGGED};
            # see https://blender.stackexchange.com/a/1542/33919 for context enum details
            bmesh.ops.delete(bm, geom=magic_loops, context=2)

            if debug:
                print()
                print("Removed magic and projected loops:", ", ".join(magic_loop_ids))

        # remove originally selected faces
        if initialfaces:
            face_ids = [str(f.index) for f in faces]

            bmesh.ops.delete(bm, geom=faces, context=5)

            if debug:
                print()
                print("Removed faces:", ", ".join(face_ids))


        # unselect everything
        if not debug:
            for v in bm.verts:
                v.select = False

            bm.select_flush(False)


def rebuild_corner_faces(bm, sides, rails, spline_sweeps, single, smooth, debug=False):
    # rebuild the 3 faces around the c1 vert, the short end of the corner quad(if unfused)
    c1 = sides[0][0]
    if debug:
        print("c1 vert:", c1.index)
        # c1.select = True

    c1_faces = [f for f in c1.link_faces]

    if single:   # if the selection is a single face, it has to be the following for the A edge
        c1_edge_A = bm.edges.get([c1, sides[1][0]])
    else:
        c1_edge_A = bm.edges.get([c1, sides[0][1]])

    c1_edge_B = bm.edges.get([c1, sides[2][-1]])

    # the A face, is the one down the first rail, the B face is the one down the second rail, and the N face is what's going to be the n-gon
    c1_face_A = [f for f in c1_edge_A.link_faces if not f.select][0]
    c1_face_B = [f for f in c1_edge_B.link_faces if not f.select][0]

    c1_faces.remove(c1_face_A)
    c1_faces.remove(c1_face_B)
    c1_face_N = c1_faces[0]

    if debug:
        print("c1_face A:", c1_face_A.index)
        print("c1_face B:", c1_face_B.index)
        print("c1_face N:", c1_face_N.index)

    c1_face_A_verts = [v for v in c1_face_A.verts]
    c1_face_B_verts = [v for v in c1_face_B.verts]
    c1_face_N_verts = [v for v in c1_face_N.verts]

    if debug:
        print("old c1_face_A_verts:", [v.index for v in c1_face_A_verts])
        print("old c1_face_B_verts:", [v.index for v in c1_face_B_verts])
        print("old c1_face_N_verts:", [v.index for v in c1_face_N_verts])

    A_vert_idx = c1_face_A_verts.index(c1)
    B_vert_idx = c1_face_B_verts.index(c1)
    N_vert_idx = c1_face_N_verts.index(c1)

    if debug:
        print("A_vert index:", A_vert_idx)
        print("B_vert index:", B_vert_idx)
        print("N_vert index:", N_vert_idx)

    # replace c1 in the A and B face verts
    c1_face_A_verts.insert(A_vert_idx, rails[0][0])
    c1_face_A_verts.remove(c1)

    c1_face_B_verts.insert(B_vert_idx, rails[1][0])
    c1_face_B_verts.remove(c1)

    # in the N face verts, replace c1 with the verts of the first sweep
    c1_face_N_verts[N_vert_idx:N_vert_idx] = spline_sweeps[0]
    c1_face_N_verts.remove(c1)

    if debug:
        print("new c1_face_A_verts:", [v.index for v in c1_face_A_verts])
        print("new c1_face_B_verts:", [v.index for v in c1_face_B_verts])
        print("new c1_face_N_verts:", [v.index for v in c1_face_N_verts])

    # create the new faces
    new_faces = []

    new_faces.append(bm.faces.new(c1_face_A_verts))
    new_faces.append(bm.faces.new(c1_face_B_verts))
    new_faces.append(bm.faces.new(c1_face_N_verts))

    # delete the old ones
    # 1: DEL_VERTS, 2: DEL_EDGES, 3: DEL_ONLYFACES, 4: DEL_EDGESFACES, 5: DEL_FACES, 6: DEL_ALL, 7: DEL_ONLYTAGGED};
    bmesh.ops.delete(bm, geom=[c1_face_A, c1_face_B, c1_face_N], context=6)
    bmesh.ops.delete(bm, geom=[c1_edge_A, c1_edge_B], context=2)

    bmesh.ops.recalc_face_normals(bm, faces=new_faces)

    if smooth:
        for f in new_faces:
            f.smooth = True


def create_handles(bm, sweeps, tension, debug=False):
    for sweep in sweeps:
        v1 = sweep["verts"][0]
        v2 = sweep["verts"][1]

        loop1 = sweep["loops"][0]
        loop1_end = loop1.other_vert(v1)
        loop1_dir = v1.co - loop1_end.co

        loop2 = sweep["loops"][1]
        loop2_end = loop2.other_vert(v2)
        loop2_dir = v2.co - loop2_end.co

        if debug:
            print(" » vert 1:", v1.index)
            print("   » loop", loop1.index)
            print("     » loop end", loop1_end.index)
            print("     » direction", loop1_dir)
            print()
            print(" » vert 2:", v2.index)
            print("   » loop", loop2.index)
            print("     » loop end", loop2_end.index)
            print("     » direction", loop2_dir)
            print()

        # tuple, the first item is the handle location for the first edge, the second for the other
        h = mathutils.geometry.intersect_line_line(v1.co, loop1_end.co, v2.co, loop2_end.co)

        # take the handles and add in the tension
        handle1co = v1.co + ((h[0] - v1.co) * tension)
        handle2co = v2.co + ((h[1] - v2.co) * tension)

        sweep["handles"] = [handle1co, handle2co]

        if debug:
            handle1 = bm.verts.new()
            handle1.co = handle1co

            handle2 = bm.verts.new()
            handle2.co = handle2co

            bm.edges.new((v1, handle1))
            bm.edges.new((v2, handle2))


def adjust_width(sweeps, width):
    sweeplen = len(sweeps)

    # adjust the width accordingly to fade it out increasingly
    for idx, sweep in enumerate(sweeps):
        v1 = sweep["verts"][0]
        loop1 = sweep["loops"][0]
        v1_other = loop1.other_vert(v1)

        dir1 = v1.co + (v1_other.co - v1.co).normalized() * width * (sweeplen - idx) / sweeplen
        v1.co = dir1

        v2 = sweep["verts"][1]
        loop2 = sweep["loops"][1]
        v2_other = loop2.other_vert(v2)

        dir2 = v2.co + (v2_other.co - v2.co).normalized() * width * (sweeplen - idx) / sweeplen
        v2.co = dir2


def get_rails(bm, faces, sides, width, debug=False):
    # we need to "split" one of the corner verts, the edge connecting the two new verts, will be the short side of the corner quad
    # the A vert is the one leading down the verts first side, the B one is leading down the inverted last side
    c1 = sides[0][0]
    # c1.select = True

    c1_loop = [l for l in c1.link_loops if l.face.select][0]
    # c1_loop.edge.select = True

    edge_A = c1_loop.link_loop_radial_next.link_loop_next.edge
    # edge_A.select = True

    edge_B = c1_loop.link_loop_prev.link_loop_radial_prev.link_loop_prev.edge
    # edge_B.select = True

    edge_A_other_v = edge_A.other_vert(c1)
    edge_B_other_v = edge_B.other_vert(c1)

    # c1_Aco = c1.co + (edge_A_other_v.co - c1.co).normalized() * width
    # c1_Bco = c1.co + (edge_B_other_v.co - c1.co).normalized() * width
    # NOTE: we are no longer spacing out the c1 A and B verts here by the width amount, we are setting all width amounts propagated through the sweeps later

    c1_A = bm.verts.new()
    # c1_A.co = c1_Aco
    c1_A.co = c1.co

    c1_B = bm.verts.new()
    # c1_B.co = c1_Bco
    c1_B.co = c1.co

    bm.verts.index_update()

    # we are also creating an edge, this is so the sweep function can find a loop candidate
    # which it wouldnt be able to do on a loose vert
    bm.edges.new([c1_A, edge_A_other_v])
    bm.edges.new([c1_B, edge_B_other_v])
    bm.edges.index_update()

    # NOTE: deselecting the faces, as well as hiding them at the bottom is gonna break the following steps, its only here for when this very code is being worked on
    # if debug:
        # for f in faces:
            # f.select = False

    # setup the rails
    rail1 = [c1_A]
    rail2 = [c1_B]

    for v in sides[0][1:]:
        rail1.append(v)

    for v in reversed(sides[2][1:]):
        rail2.append(v)

    if debug:
        for v in rail1:
            v.select = True

        for v in rail2:
            v.select = True

        # for f in faces:
            # f.hide_set(True)

    if debug:
        print("\nrails:")
        rail1ids = [str(v.index) for v in rail1]
        rail2ids = [str(v.index) for v in rail2]
        print(" » ".join(rail1ids))
        print(" » ".join(rail2ids))


    return (rail1, rail2), (edge_A_other_v, edge_B_other_v)


def get_3_sides(bm, mg, verts, edges, faces, turn, debug=False):
    if len(faces) == 0:
        # print("Selection does not include faces, aborting")
        popup_message("Selection does not include faces, aborting", title="Illegal Selection")
        return
    elif len(verts) < 3:
        # print("Selection has less than 3 vertices selected, aborting")
        popup_message("Selection has less than 3 verts selected, aborting", title="Illegal Selection")
        return

    corners = [bm.verts[idx] for idx in mg if bm.verts[idx].select and sum([vselect for _, vselect, eselect in mg[idx] if eselect]) == 2]

    if len(corners) != 3:
        # print("Selection does not have 3 corners, it's not a triangular corner, aborting")
        popup_message("Selection does not have 3 corners, it's not a triangular corner, aborting", title="Illegal Selection")
        return


    # turn the corner(the entire surface thats going to be built will be turned as a consequence)
    if turn == "2":
        first = corners.pop(0)
        corners.append(first)
    elif turn == "3":
        third = corners.pop(2)
        corners.insert(0, third)

    sides = [[corners[0]], [corners[1]], [corners[2]]]

    if debug:
        print("sides:", sides)

    # for each corner, walk forwards until you meet the next corner
    for idx, c in enumerate(corners):
        if debug:
            print("corner:", c.index)

        loop = [l for l in c.link_loops if l.face.select][0]

        v = c
        side = [side for side in sides if side[0] == v][0]
        while loop.edge.other_vert(v) not in corners:
            # sides[idx].append(loop.edge.other_vert(v))
            side.append(loop.edge.other_vert(v))

            loop = loop.link_loop_next.link_loop_radial_next.link_loop_next
            v = loop.vert

            if debug:
                # v.select = True
                # loop.edge.select = True
                print("edge:", loop.edge.index, "vert:", v.index)

        # if you are on your first walk, you need to check if the vert you ran into, actually is the one of the next walk in sides
        # switch side 1 and 2 otherwise, this is to ensure sides are in proper order
        if idx == 0:
            if loop.edge.other_vert(v) != sides[1][0]:
                if debug:
                    print("switched side 1 and 2")
                second = sides.pop(1)
                sides.append(second)

    if debug:
        for side in sides:
            print(" » ".join([str(v.index) for v in side]))

    return sides, corners
