import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, EnumProperty
import bmesh
from . unfuse import unfuse, get_sweeps
from . change_width import change_width
from . fuse import fuse_surface, tensionpresetitems, methoditems, handlemethoditems
from .. utils.graph import build_mesh_graph
from .. utils.core import get_2_rails, init_sweeps, get_loops, create_loop_intersection_handles, create_splines, create_face_intersection_handles
from .. utils.ui import step_enum, draw_init, draw_end, draw_title, draw_prop, wrap_mouse
from .. utils.debug import debug_sweeps, vert_debug_print
from .. utils.developer import output_traceback
from .. utils import MACHIN3 as m3



class OperatorSettings:
    # see https://blender.stackexchange.com/questions/6520/should-an-operator-remember-its-last-used-settings-when-invoked
    _settings = {}

    def save_settings(self):
        for d in dir(self.properties):
            if d in ['bl_rna', 'rna_type', 'init', 'width', 'average', 'reverse', 'allowmodalwidth', 'allowmodaltension']:
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


class Refuse(bpy.types.Operator, OperatorSettings):
    bl_idname = "machin3.refuse"
    bl_label = "MACHIN3: Refuse"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Unfuse + Fuse"

    method = EnumProperty(name="Method", items=methoditems, default="FUSE")

    handlemethod = EnumProperty(name="Unchamfer Method", items=handlemethoditems, default="FACE")

    segments = IntProperty(name="Segments", default=6, min=0, max=30)
    tension = FloatProperty(name="Tension", default=0.7, min=0.01, max=2, step=0.1)
    tension_preset = EnumProperty(name="Tension Presets", items=tensionpresetitems, default="CUSTOM")
    average = BoolProperty(name="Average Tension", default=False)
    force_projected_loop = BoolProperty(name="Force Projected Loop", default=False)

    width = FloatProperty(name="Width (experimental)", default=0.0, step=0.1)

    capholes = BoolProperty(name="Cap", default=True)
    capdissolveangle = IntProperty(name="Dissolve Angle", min=0, max=180, default=10)
    smooth = BoolProperty(name="Shade Smooth", default=False)
    reverse = BoolProperty(name="Reverse", default=False)

    # recognize the first time the  tool is run to fetch the existing number of segments
    init = BoolProperty(name="Initialize", default=True)

    # hiddden
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

        draw_title(self, "Refuse")

        draw_prop(self, "Method", self.method, offset=0, key="SHIFT scroll UP/DOWN")
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

            draw_prop(self, "Cap Holes", self.capholes, offset=18, key="toggle F")
            if self.capholes:
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


            # modal refuse
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
                mode =m3.get_mode()
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
        if self.tension_preset != "CUSTOM":
            self.tension = float(self.tension_preset)

        debug = True
        debug = False

        active = m3.get_active()

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
        faces = [f for f in bm.faces if f.select]

        sweeps = get_sweeps(bm, mg, verts, faces, debug=debug)

        if sweeps:
            chamfer_faces = unfuse(bm, faces, sweeps, debug=debug)

            # we need t push the current state back to active.data
            # otherwise potential freestyle loop edges won't be detected (freestyle doesn't work in bmesh, so is done via MeshEdge)
            bm.to_mesh(active.data)

            if chamfer_faces:
                # exit out when the segments are 0, this is the same as doing an Unfuse()
                if self.segments == 0:
                    bm.to_mesh(active.data)
                    m3.set_mode("EDIT")
                    return True

                if len(chamfer_faces) == 1:
                    self.single = True
                else:
                    self.single = False

                if self.init:
                    self.segments = len(sweeps) - 2
                    self.init = False

                mg = build_mesh_graph(bm, debug=debug)
                chamfer_verts = [v for v in bm.verts if v.select]

                ret = get_2_rails(bm, mg, chamfer_verts, chamfer_faces, reverse=self.reverse, debug=debug)

                if ret:
                    rails, self.cyclic = ret

                    if self.method == "FUSE":
                        chamfer_sweeps = init_sweeps(bm, active, rails, debug=debug)
                        get_loops(bm, chamfer_faces, chamfer_sweeps, force_projected=self.force_projected_loop, debug=debug)

                        # change width, but only if it's actually non zero
                        if self.width != 0:
                            change_width(bm, chamfer_sweeps, self.width, debug=debug)

                        if self.handlemethod == "FACE":
                            create_face_intersection_handles(bm, chamfer_sweeps, tension=self.tension, average=self.average, debug=debug)
                        elif self.handlemethod == "LOOP":
                            create_loop_intersection_handles(bm, chamfer_sweeps, self.tension, debug=debug)

                        spline_sweeps = create_splines(bm, chamfer_sweeps, self.segments, debug=debug)
                        self.clean_up(bm, chamfer_sweeps, chamfer_faces, magicloop=True, initialfaces=False, debug=debug)

                        self.clean_up(bm, chamfer_sweeps, chamfer_faces, magicloop=False, initialfaces=True, debug=debug)
                        fuse_surface(bm, spline_sweeps, self.smooth, self.capholes, self.capdissolveangle, self.cyclic, debug=debug)

                        # get the loop edges, and set the sweep edge sharps and bweights accordingly
                        loop_edges = [(idx, [le for le in sweep["loops"] if le.is_valid]) for idx, sweep in enumerate(chamfer_sweeps)]

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

                        # remove boundary sharps and bweights
                        for rail in rails:
                            for idx, rv in enumerate(rail):
                                if idx == len(rail) - 1:
                                    break
                                else:
                                    re = bm.edges.get([rv, rail[idx + 1]])
                                    re.smooth = True
                                    re[bw] = 0


                    elif self.method == "BRIDGE":
                        for f in bm.faces:
                            f.select = False

                        bmesh.ops.delete(bm, geom=chamfer_faces, context=5)

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

                # this is done as a bpy ops, instead of a bmesh.ops because the bmesh ops is much more limited for some reason
                if self.method == "BRIDGE":
                    bpy.ops.mesh.bridge_edge_loops(number_cuts=self.segments, smoothness=self.tension, interpolation='SURFACE')

                return True

        # bm.to_mesh(active.data)

        m3.set_mode("EDIT")
        # m3.set_mode("VERT")
        # m3.set_mode("EDGE")

        return False


    def clean_up(self, bm, sweeps, faces, double_verts=None, magicloop=True, initialfaces=True, deselect=False, debug=False):
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

        if double_verts:
            bmesh.ops.remove_doubles(bm, verts=double_verts, dist=0)

        # unselect everything
        if deselect:
            if not debug:
                for v in bm.verts:
                    v.select = False

                bm.select_flush(False)
