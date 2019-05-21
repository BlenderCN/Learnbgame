import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, EnumProperty
import bmesh
import math
from ..utils.graph import build_mesh_graph
from ..utils.core import get_2_rails, init_sweeps, create_loop_intersection_handles, create_splines, get_loops, create_face_intersection_handles
from . change_width import change_width
from ..utils.debug import debug_sweeps
from ..utils.ui import step_enum, draw_title, draw_prop, draw_init, draw_end, wrap_mouse
from ..utils.developer import output_traceback
from ..utils.support import loop_index_update
from ..utils import MACHIN3 as m3


# TODO: if there are flat facs detected, don't fuse them, unless its specificlly enabled?


tensionpresetitems = [("CUSTOM", "Custom", ""),
                      ("0.55", "0.55", ""),
                      ("0.7", "0.7", ""),
                      ("1", "1", ""),
                      ("1.33", "1.33", "")]

methoditems = [("FUSE", "Fuse", ""),
               ("BRIDGE", "Bridge", "")]

handlemethoditems=[("FACE", "Face", ""),
                   ("LOOP", "Loop", "")]


class FuseSettings:
    # see https://blender.stackexchange.com/questions/6520/should-an-operator-remember-its-last-used-settings-when-invoked
    _settings = {}

    def save_settings(self):
        for d in dir(self.properties):
            if d in ['bl_rna', 'rna_type', 'width', 'average', 'reverse', 'allowmodalwidth', 'allowmodaltension']:
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


class Fuse(bpy.types.Operator, FuseSettings):
    bl_idname = "machin3.fuse"
    bl_label = "MACHIN3: Fuse"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Create rounded Bevels from Chamfers"

    method = EnumProperty(name="Method", items=methoditems, default="FUSE")

    handlemethod = EnumProperty(name="Unchamfer Method", items=handlemethoditems, default="FACE")

    segments = IntProperty(name="Segments", default=6, min=0, max=30)
    tension = FloatProperty(name="Tension", default=0.7, min=0.01, max=4, step=0.1)
    tension_preset = EnumProperty(name="Tension Presets", items=tensionpresetitems, default="CUSTOM")
    average = BoolProperty(name="Average Tension", default=False)
    force_projected_loop = BoolProperty(name="Force Projected Loop", default=False)

    width = FloatProperty(name="Width (experimental)", default=0.0, step=0.1)

    capholes = BoolProperty(name="Cap", default=True)
    capdissolveangle = IntProperty(name="Dissolve Angle", min=0, max=180, default=10)

    smooth = BoolProperty(name="Shade Smooth", default=False)

    reverse = BoolProperty(name="Reverse", default=False)

    # hidden
    cyclic = BoolProperty(name="Cyclic", default=False)
    single = BoolProperty(name="Single", default=False)

    # modal
    allowmodalwidth = BoolProperty(default=False)
    allowmodaltension = BoolProperty(default=False)

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        column = layout.column()

        row = column.row()
        row.prop(self, "method", expand=True)
        column.separator()

        if self.method == "FUSE":
            row = column.row()
            row.prop(self, "handlemethod", expand=True)
            column.separator()

        column.prop(self, "segments")
        column.prop(self, "tension")
        row = column.row()
        row.prop(self, "tension_preset", expand=True)

        if self.method == "FUSE":
            if self.handlemethod == "FACE":
                column.prop(self, "average")
            column.prop(self, "force_projected_loop")

            column.separator()
            column.prop(self, "width")
            if not self.cyclic:
                column.separator()
                row = column.row().split(percentage=0.3)
                row.prop(self, "capholes")
                row.prop(self, "capdissolveangle")

            column.prop(self, "smooth")

        if self.single:
            column.separator()
            column.prop(self, "reverse")

    @classmethod
    def poll(cls, context):
        bm = bmesh.from_edit_mesh(context.active_object.data)
        return len([f for f in bm.faces if f.select]) >= 1

    def draw_HUD(self, args):
        draw_init(self, args)

        draw_title(self, "Fuse")

        draw_prop(self, "Method", self.method, offset=0, key="SHIFT scroll UP/DOWN,")
        if self.method == "FUSE":
            draw_prop(self, "Handles", self.handlemethod, offset=18, key="CTRL scroll UP/DOWN")
        self.offset += 10

        draw_prop(self, "Segments", self.segments, offset=18, key="scroll UP/DOWN")
        draw_prop(self, "Tension", self.tension, offset=18, decimal=2, active=self.allowmodaltension, key="move UP/DOWN, toggle T, presets %s, X, C, V" % ("Z" if m3.MM_prefs().keyboard_layout == "QWERTY" else "Y"))

        if self.method == "FUSE":
            if self.handlemethod == "FACE":
                draw_prop(self, "Average Tension", self.average, offset=18, key="toggle A")
            draw_prop(self, "Projected Loops", self.force_projected_loop, offset=18, key="toggle P")

            self.offset += 10

            draw_prop(self, "Width", self.width, offset=18, decimal=3, active=self.allowmodalwidth, key="move LEFT/RIGHT, toggle W, reset ALT + W")
            self.offset += 10

            if not self.cyclic:
                draw_prop(self, "Cap Holes", self.capholes, offset=18, key="toggle F")
                # if self.capholes:
                draw_prop(self, "Dissolve Angle", self.capdissolveangle, offset=18, key="ALT scroll UP/DOWN")
                self.offset += 10

            draw_prop(self, "Smooth", self.smooth, offset=18, key="toggle S")

        if self.single:
            self.offset += 10
            draw_prop(self, "Reverse", self.reverse, offset=18, key="toggle R")

        draw_end()

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        events = ['WHEELUPMOUSE', 'UP_ARROW', 'ONE', 'WHEELDOWNMOUSE', 'DOWN_ARROW', 'TWO', 'R', 'S', 'F', 'Y', 'Z', 'X', 'C', 'V', 'W', 'T', 'A', 'P']

        # only consider MOUSEMOVE as a trigger for main(), when modalwidth or modaltension are actually active
        if any([self.allowmodalwidth, self.allowmodaltension]):
            events.append('MOUSEMOVE')

        if event.type in events:

            # CONTROL width and tension

            if event.type == 'MOUSEMOVE':
                delta_x = self.mouse_x - self.init_mouse_x  # bigger if going to the right
                delta_y = self.mouse_y - self.init_mouse_y  # bigger if going to the up

                if self.allowmodalwidth:
                    wrap_mouse(self, context, event, x=True)

                    self.width = delta_x * 0.001

                if self.allowmodaltension:
                    wrap_mouse(self, context, event, y=True)

                    self.tension_preset = "CUSTOM"
                    self.tension = delta_y * 0.001 + self.init_tension

            # CONTROL segments, method, handlemethod and capdissolveangle

            elif event.type in {'WHEELUPMOUSE', 'UP_ARROW', 'ONE'} and event.value == 'PRESS':
                if event.shift:
                    self.method = step_enum(self.method, methoditems, 1)
                elif event.ctrl:
                    self.handlemethod = step_enum(self.handlemethod, handlemethoditems, 1)
                elif event.alt:
                    self.capdissolveangle += 5
                else:
                    self.segments += 1

            elif event.type in {'WHEELDOWNMOUSE', 'DOWN_ARROW', 'TWO'} and event.value == 'PRESS':
                if event.shift:
                    self.method = step_enum(self.method, methoditems, -1)
                elif event.ctrl:
                    self.handlemethod = step_enum(self.handlemethod, handlemethoditems, -1)
                elif event.alt:
                    self.capdissolveangle -= 5
                else:
                    self.segments -= 1

            # TOGGLE reverse, shade smooth and caps

            elif event.type == 'R' and event.value == "PRESS":
                self.reverse = not self.reverse

            elif event.type == 'S' and event.value == "PRESS":
                self.smooth = not self.smooth

            elif event.type == 'F' and event.value == "PRESS":
                self.capholes = not self.capholes

            # SET tension presets

            elif (event.type == 'Y' and event.value == "PRESS") or (event.type == 'Z' and event.value == "PRESS"):
                self.tension_preset = "0.55"

            elif event.type == 'X' and event.value == "PRESS":
                self.tension_preset = "0.7"

            elif event.type == 'C' and event.value == "PRESS":
                self.tension_preset = "1"

            elif event.type == 'V' and event.value == "PRESS":
                self.tension_preset = "1.33"

            # TOGGLE modal width and tension

            elif event.type == 'W' and event.value == "PRESS":
                if event.alt:
                    self.allowmodalwidth = False
                    self.width = 0
                else:
                    self.allowmodalwidth = not self.allowmodalwidth

            elif event.type == 'T' and event.value == "PRESS":
                self.allowmodaltension = not self.allowmodaltension

            # TOGGLE average tension and force projected loops

            elif event.type == 'A' and event.value == "PRESS":
                self.average = not self.average

            elif event.type == 'P' and event.value == "PRESS":
                self.force_projected_loop = not self.force_projected_loop

            # modal fuse
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

        self.init_tension = self.tension

        # first run, this is necessary if there's no mouse movement event
        # which would trigger the first run automatically (even without any movement)
        # note that for some reason, returning FINISHED or CANCELLED here or in main() will crash blender
        # but doing it in modal() is fine
        # maybe related to the info/error popup?
        # hmm, doesnt seem to be true anymore
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
        if self.segments > 0 or modal is True:

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
                if self.segments == 0:
                    m3.set_mode("EDIT")
                    return True

            # create bmesh
            bm = bmesh.new()
            bm.from_mesh(active.data)
            bm.normal_update()
            bm.verts.ensure_lookup_table()
            # bm.faces.ensure_lookup_table()
            # bm.edges.ensure_lookup_table()

            bw = bm.edges.layers.bevel_weight.verify()

            mg = build_mesh_graph(bm, debug=debug)
            verts = [v for v in bm.verts if v.select]
            faces = [f for f in bm.faces if f.select]

            if len(faces) == 1:
                self.single = True
            else:
                self.single = False

            ret = get_2_rails(bm, mg, verts, faces, self.reverse, debug=debug)

            if ret:
                rails, self.cyclic = ret

                if self.method == "FUSE":
                    sweeps = init_sweeps(bm, active, rails, debug=debug)
                    # debug_sweeps(sweeps, self.cyclic)
                    get_loops(bm, faces, sweeps, force_projected=self.force_projected_loop, debug=debug)
                    # debug_sweeps(sweeps, self.cyclic)

                    # change width, but only if it's actually non zero
                    if self.width != 0:
                        change_width(bm, sweeps, self.width, debug=debug)

                    if self.handlemethod == "FACE":
                        create_face_intersection_handles(bm, sweeps, tension=self.tension, average=self.average, debug=debug)
                    elif self.handlemethod == "LOOP":
                        create_loop_intersection_handles(bm, sweeps, self.tension, debug=debug)

                    # """
                    spline_sweeps = create_splines(bm, sweeps, self.segments, debug=debug)
                    # debug_sweeps(sweeps, self.cyclic)


                    self.clean_up(bm, sweeps, faces, magicloop=True, initialfaces=False, debug=debug)

                    # remove edges created by magic loop and the originally selected faces
                    self.clean_up(bm, sweeps, faces, magicloop=False, initialfaces=True, debug=debug)

                    fuse_faces, _ = fuse_surface(bm, spline_sweeps, self.smooth, self.capholes, self.capdissolveangle, self.cyclic, debug=debug)

                    # get the loop edges, and set the sweep edge sharps and bweights accordingly
                    loop_edges = [(idx, [le for le in sweep["loops"] if le.is_valid]) for idx, sweep in enumerate(sweeps)]

                    for idx, les in loop_edges:
                        for i, v in enumerate(spline_sweeps[idx]):
                            if i == len(spline_sweeps[idx]) - 1:
                                break
                            se = bm.edges.get([v, spline_sweeps[idx][i + 1]])

                            if any([not le.smooth for le in les]):
                                se.smooth = False

                            if any([le[bw] > 0 for le in les]):
                                se[bw] = 1

                    # extend the rails
                    if self.cyclic:
                        rails[0].append(rails[0][0])
                        rails[1].append(rails[1][0])

                    rail_edges = []  # collect the rail edges for the normal flattening of the border faces

                    # remove boundary sharps and bweights
                    for rail in rails:
                        for idx, rv in enumerate(rail):
                            if idx == len(rail) - 1:
                                break
                            else:
                                re = bm.edges.get([rv, rail[idx + 1]])
                                re.smooth = True
                                re[bw] = 0

                                rail_edges.append(re)

                    # """

                elif self.method == "BRIDGE":
                    for f in bm.faces:
                        f.select = False

                    bmesh.ops.delete(bm, geom=faces, context=5)

                    if self.cyclic:
                        rails[0].append(rails[0][0])
                        rails[1].append(rails[1][0])

                    for rail in rails:
                        for idx, v in enumerate(rail):
                            if idx == len(rail) - 1:
                                break
                            else:
                                edge = bm.edges.get([v, rail[idx + 1]])
                                edge.select = True

                bm.to_mesh(active.data)

                m3.set_mode("EDIT")

                # NOTE: the bmesh bridge op seems very limited for some reason(no segments, not continuity), so the bpy op it is
                if self.method == "BRIDGE":
                    bpy.ops.mesh.bridge_edge_loops(number_cuts=self.segments, smoothness=self.tension, interpolation='SURFACE')

                # m3.set_mode("VERT")

                return True

            else:
                m3.set_mode("EDIT")

        return False

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


def fuse_surface(bm, spline_sweeps, smooth, capholes=True, capdissolveangle=10, cyclic=False, select=True, debug=False):
    faces = []

    # rail[4]   o - o - o - o - o - o - o - o - o
    #           |   |   |   |   |   |   |   |   |
    # rail[3]   o - o - o - o - o - o - o - o - o
    #           |   |   |   |   |   |   |   |   |
    # rail[2]   o - o - o - o - o - o - o - o - o
    #           |   |   |   |   |   |   |   |   |
    # rail[1]   o 🡲 o - o - o - o - o - o - o - o
    #           🡱   🡳   |   |   |   |   |   |   |
    # rail[0]   o 🡰 o - o - o - o - o - o - o - o
    #
    #           0   1   2   3   4   5   6   7   8
    #                 sweeps

    for sweepidx, sweep in enumerate(spline_sweeps):
        for railidx, vert in enumerate(sweep):
            fc1 = vert  # sweep[railidx]
            fc2 = sweep[railidx + 1]

            fc3 = spline_sweeps[sweepidx + 1][railidx + 1]
            fc4 = spline_sweeps[sweepidx + 1][railidx]

            face_corners = [fc1, fc2, fc3, fc4]
            face = bm.faces.new(face_corners)
            if smooth:
                face.smooth = True
            faces.append(face)

            if debug:
                bm.faces.index_update()
                print("face:", face.index, "verts:", [fc.index for fc in face_corners])

            if railidx + 2 == len(sweep):
                break

        if sweepidx + 2 == len(spline_sweeps):
            break

    bmesh.ops.recalc_face_normals(bm, faces=faces)

    no_caps_selected = True
    caps = []
    # we dont't cap holes for a cyclic selection, but we can use the border verts!
    if capholes or cyclic:
        # separate them in two lists
        border1 = spline_sweeps[0]
        border2 = spline_sweeps[-1]

        if debug:
            border1_ids = [v.index for v in border1]
            border2_ids = [v.index for v in border2]

            print("border1:", border1_ids)
            print("border2:", border2_ids)

        if cyclic:
            cyclic_faces = []
            for idx, (sweep1_vert, sweep2_vert) in enumerate(zip(border1, border2)):
                fc1 = sweep1_vert  # border1[idx]
                fc2 = border1[idx + 1]
                fc3 = border2[idx + 1]
                fc4 = sweep2_vert  # border2[idx]

                face_corners = [fc1, fc2, fc3, fc4]
                face = bm.faces.new(face_corners)
                if smooth:
                    face.smooth = True
                cyclic_faces.append(face)

                if idx + 2 == len(border1):
                    bmesh.ops.recalc_face_normals(bm, faces=cyclic_faces)
                    break

            if select:
                for f in faces + cyclic_faces:
                    f.select = True

            return faces + cyclic_faces, None

        # cap the openings
        caps.extend([bm.faces.new(b) for b in [border1, border2]])
        bmesh.ops.recalc_face_normals(bm, faces=caps)

        # get the remote edges
        cap1_edge = bm.edges.get([border1[0], border1[-1]])
        cap2_edge = bm.edges.get([border2[0], border2[-1]])

        # get the face angle of these edges
        # NOTE; that the originally selected faces have to have been deleted at this point
        # otherwise the edges will have 3 faces and an angle cant be calculated!
        if cap1_edge.is_manifold:
            cap1_angle = math.degrees(cap1_edge.calc_face_angle())

            if debug:
                print("cap1 angle:", cap1_angle)

            if cap1_angle < capdissolveangle or cap1_angle > 181 - capdissolveangle:
                bmesh.ops.dissolve_edges(bm, edges=[cap1_edge])

                # now that the cap edge has been dissolved, we need to get the cap face from one of the border verts
                if smooth:
                    border1vert = border1[1]
                    cap1face = [f for f in border1vert.link_faces if f not in faces][0]
                    cap1face.smooth = True


        if cap2_edge.is_manifold:
            cap2_angle = math.degrees(cap2_edge.calc_face_angle())

            if debug:
                print("cap2 angle:", cap2_angle)

            if cap2_angle < capdissolveangle or cap2_angle > 181 - capdissolveangle:
                bmesh.ops.dissolve_edges(bm, edges=[cap2_edge])

                # now that the cap edge has been dissolved, we need to get the cap face from one of the border verts
                if smooth:
                    border2vert = border2[1]
                    cap2face = [f for f in border2vert.link_faces if f not in faces][0]
                    cap2face.smooth = True


        if cap1_edge.is_valid:
            caps[0].select = True
            no_caps_selected = False
            # adding it to the history, so it can be easily flattend by adding to the selection
            bm.select_history.add(caps[0])


        if cap2_edge.is_valid:
            caps[1].select = True
            no_caps_selected = False
            bm.select_history.add(caps[1])
            # adding it to the history, so it can be easily flattend by adding to the selection


    # select all new faces, if no caps have been selected,
    # this is to ensure the poll returns True and so the redo panel works
    if select:
        if no_caps_selected or not caps or cyclic:
            for f in faces:
                f.select = True

    return faces, caps
