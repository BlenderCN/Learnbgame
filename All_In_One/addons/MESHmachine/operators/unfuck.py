import bpy
from bpy.props import FloatProperty, IntProperty, BoolProperty, EnumProperty
import bmesh
import math
import mathutils
from . fuse import tensionpresetitems
from .. utils.graph import build_mesh_graph
from .. utils.ui import popup_message, draw_init, draw_end, draw_title, draw_prop, wrap_mouse
from .. utils.developer import output_traceback
from .. utils import MACHIN3 as m3



class OperatorSettings:
    # see https://blender.stackexchange.com/questions/6520/should-an-operator-remember-its-last-used-settings-when-invoked
    _settings = {}

    def save_settings(self):
        for d in dir(self.properties):
            if d in ['bl_rna', 'rna_type', 'allowmodalwidth', 'allowmodaltension', 'width', 'propagate', 'fade', 'widthlinked', 'tensionlinked']:
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


class Unfuck(bpy.types.Operator, OperatorSettings):
    bl_idname = "machin3.unfuck"
    bl_label = "MACHIN3: Unf*ck"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Realign messed up verts and edges."

    width = FloatProperty(name="Width", default=0, step=0.1)
    width2 = FloatProperty(name="Width 2", default=0, step=0.1)
    widthlinked = BoolProperty(name="Width Linked", default=True)

    tension = FloatProperty(name="Tension", default=0.7, min=0.01, max=10, step=0.1)
    tension_preset = EnumProperty(name="Tension Presets", items=tensionpresetitems, default="CUSTOM")
    tension2 = FloatProperty(name="Tension 2", default=0.7, min=0.01, max=10, step=0.1)
    tension2_preset = EnumProperty(name="Tension Presets", items=tensionpresetitems, default="CUSTOM")
    tensionlinked = BoolProperty(name="Tension Linked", default=True)

    propagate = IntProperty(name="Propagate", default=0, min=0)
    fade = FloatProperty(name="Fade", default=1, min=0, max=1, step=0.1)

    merge = BoolProperty(name="Merge", default=False)

    advanced = BoolProperty(name="Advanced Mode", default=False)

    # modal
    allowmodalwidth = BoolProperty(default=True)
    allowmodaltension = BoolProperty(default=False)

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        column = layout.column()

        column.prop(self, "merge", toggle=True)

        if not self.merge:
            if self.advanced:
                row = column.row().split(percentage=0.2)
                row.prop(self, "widthlinked", icon="CONSTRAINT", text="Linked")
                row.prop(self, "width")
                row.prop(self, "width2")

                row = column.row().split(percentage=0.2)
                row.prop(self, "tensionlinked", icon="CONSTRAINT", text="Linked")
                row.prop(self, "tension")
                row.prop(self, "tension2")
                row = column.row()
                row.prop(self, "tension_preset", expand=True)
                row.prop(self, "tension2_preset", expand=True)
            else:
                column.prop(self, "width")
                column.prop(self, "tension")
                row = column.row()
                row.prop(self, "tension_preset", expand=True)

        column.separator()
        row = column.row().split(percentage=0.6)
        row.prop(self, "propagate")

        if not self.merge:
            row.prop(self, "fade")

            column.separator()
            column.prop(self, "advanced")

    @classmethod
    def poll(cls, context):
        mode = m3.get_mode()
        bm = bmesh.from_edit_mesh(context.active_object.data)
        return len([e for e in bm.edges if e.select]) >= 2 and mode in ['VERT', 'EDGE']

    def draw_HUD(self, args):
        draw_init(self, args)

        draw_title(self, "Unf*ck")

        draw_prop(self, "Merge", self.merge, key="toggle M")
        self.offset += 10

        if not self.merge:
            draw_prop(self, "Width", self.width, offset=18, decimal=3, active=self.allowmodalwidth, key="move LEFT/RIGHT, toggle W, reset ALT + W")
            draw_prop(self, "Tension", self.tension, offset=18, decimal=2, active=self.allowmodaltension, key="move UP/DOWN, toggle T, presets %s, X, C, V" % ("Z" if m3.MM_prefs().keyboard_layout == "QWERTY" else "Y"))
            self.offset += 10

        draw_prop(self, "Propagate", self.propagate, offset=18, key="scroll UP/DOWN")
        if self.propagate > 0 and not self.merge:
            draw_prop(self, "Fade", self.fade, offset=18, decimal=1, key="ALT scroll  UP/DOWN")

        draw_end()

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        events = ['WHEELUPMOUSE', 'UP_ARROW', 'ONE', 'WHEELDOWNMOUSE', 'DOWN_ARROW', 'TWO', 'Y', 'Z', 'X', 'C', 'V', 'W', 'T', 'M']

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

                    if event.shift:
                        self.width = delta_x * 0.0001
                    elif event.ctrl:
                        self.width = delta_x * 0.01
                    else:
                        self.width = delta_x * 0.001

                if self.allowmodaltension:
                    wrap_mouse(self, context, event, y=True)

                    self.tension_preset = "CUSTOM"

                    if event.shift:
                        self.tension = self.init_tension + delta_y * 0.0001
                    elif event.ctrl:
                        self.width = self.init_tension + delta_y * 0.01

                    self.tension = self.init_tension + delta_y * 0.001

            # TOGGLE merge
            elif event.type == 'M' and event.value == "PRESS":
                self.merge = not self.merge

            # CONTROL propagate

            elif event.type in {'WHEELUPMOUSE', 'UP_ARROW', 'ONE'} and event.value == 'PRESS':
                if event.alt:
                    self.fade += 0.1
                else:
                    self.propagate += 1

            elif event.type in {'WHEELDOWNMOUSE', 'DOWN_ARROW', 'TWO'} and event.value == 'PRESS':
                if event.alt:
                    self.fade -= 0.1
                else:
                    self.propagate -= 1

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

            # modal Unf*ck
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
                # reset merge prop, just in case
                self.merge = False
                self.save_settings()
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

        # initial tension, necessary because its a non-zero value and so has to be added to the mouse movementse
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

        if self.tension2_preset != "CUSTOM":
            self.tension2 = float(self.tension2_preset)

        debug = False
        # debug = True

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

        verts = [v for v in bm.verts if v.select]
        mg = build_mesh_graph(bm)

        # create vert sequence, starting at one of the ends
        seq = self.get_vert_sequence(bm, mg, verts, debug=debug)

        if seq:
            if len(seq) > 3:
                self.merge_verts = []

                self.align_seq_to_bezier(bm, seq, self.tension, self.tension2, debug=debug)

                if self.propagate:
                    self.propagate_edge_loops(bm, seq, self.propagate, self.tension, self.tension2, fade=self.fade, debug=debug)

                if self.merge:
                    for mvs in self.merge_verts:
                        bmesh.ops.remove_doubles(bm, verts=mvs, dist=0.00001)

        bm.to_mesh(active.data)
        m3.set_mode("EDIT")
        # m3.set_mode("VERT")

        if seq:
            return True
        else:
            return False

    def propagate_edge_loops(self, bm, seq, propagate, tension, tension2, fade=0, debug=False):
        for p in range(propagate):
            if debug:
                print("propagation:", p)

            new_seq = []

            # on the first iteration get the loop from the face neighboring the edge, that isnt an ngon
            if p == 0:
                e1 = bm.edges.get([seq[0], seq[1]])
                bmloop_start = [l for l in e1.link_loops if len(l.face.verts) == 4][0]
                flipped = False

                # depending on what end of the sequence you start, you need to loop in different directions
                # if we are just taking the first edge on the other end of the sequence, we can simply reuse the same code for both
                if bmloop_start.vert != seq[0]:
                    if debug:
                        print("Taking start edge from the end of the sequence!")
                    flipped = True
                    e1 = bm.edges.get([seq[-1], seq[-2]])
                    bmloop_start = [l for l in e1.link_loops if len(l.face.verts) == 4][0]

            # on the next iterations, base the start loop on the previous start loop
            else:
                bmloop_start = bmloop_start.link_loop_next.link_loop_next.link_loop_radial_next

            if debug:
                for e in bm.edges:
                    e.select = False
                e1.select = True
                print("first edge of old sequence:", e1.index)

            # walk around it two times, we need to go around it radially as well, because this way, we can properly access the first vert of the edge
            bmloop = bmloop_start.link_loop_next.link_loop_next.link_loop_radial_next

            v = bmloop.vert
            new_seq.append(v)

            if debug:
                v.select = True
                print("vertex:", v.index)

            # now just loop forwards for the length of the previous sequence
            for i in range(len(seq) - 1):
                bmloop = bmloop.link_loop_next.link_loop_radial_next.link_loop_next
                v = bmloop.vert
                new_seq.append(v)

                if debug:
                    v.select = True
                    # print("vertex:", v.index)

            if debug:
                print(" » ".join([str(v.index) for v in seq]))

            fade_propagate = (p + 1) / (propagate + 1) * fade
            if debug:
                # print(p, propagate, (p + 1) / (propagate + 1) * fade)
                print("fade_propagate: ", fade_propagate)

            self.align_seq_to_bezier(bm, new_seq, tension, tension2, fade=fade_propagate, flipped=flipped, debug=debug)

            seq = new_seq

    def align_seq_to_bezier(self, bm, seq, tension, tension2, fade=0, merge=False, flipped=False, debug=False):
        if self.merge:
            tension = tension2 = 1

        remote1 = seq[0]
        end1 = seq[1]

        remote2 = seq[-1]
        end2 = seq[-2]

        if debug:
            print("remote 1:", remote1.index, "end 1:", end1.index)
            print("remote 2:", remote2.index, "end 2:", end2.index)

        # loop1_dir = end1.co - remote1.co
        # loop2_dir = end2.co - remote2.co

        loop1_dir = remote1.co - end1.co
        loop2_dir = remote2.co - end2.co

        # create starting point of bezier, this is an offset of the end points in essence and is controlled by the width prop
        if self.widthlinked:
            self.width2 = self.width

        # if the start edge of the sequence has been flipped when propagating, these values also need to change
        # TODO: investigate why this happens at all
        if flipped:
            start1co = end1.co + (remote1.co - end1.co).normalized() * self.width2
            start2co = end2.co + (remote2.co - end2.co).normalized() * self.width
        else:
            start1co = end1.co + (remote1.co - end1.co).normalized() * self.width
            start2co = end2.co + (remote2.co - end2.co).normalized() * self.width2

        if debug:
            s1 = bm.verts.new()
            s1.co = start1co

            s2 = bm.verts.new()
            s2.co = start2co

        # create handle for bezier
        h = mathutils.geometry.intersect_line_line(end1.co, remote1.co, end2.co, remote2.co)

        loop_angle = math.degrees(loop1_dir.angle(loop2_dir))
        if debug:
            print("loop angle:", loop_angle)

        if h is None or 178 <= loop_angle <= 182:  # if the edge and both loop egdes are on the same line or are parallel: _._._ or  _./'¯¯
            if debug:
                print(" » handles could not be determined via line-line instersection")
                print(" » falling back to closest point to handle vector")

            h1_full = mathutils.geometry.intersect_point_line(end2.co, end1.co, remote1.co)[0]
            h2_full = mathutils.geometry.intersect_point_line(end1.co, end2.co, remote2.co)[0]

            h1 = end1.co + (h1_full - end1.co)
            h2 = end2.co + (h2_full - end2.co)

            h = (h1, h2)

        if not self.advanced or self.tensionlinked:
            self.tension2 = self.tension

        if flipped:
            handle1co = start1co + (h[0] - start1co) * tension2
            handle2co = start2co + (h[1] - start2co) * tension

        else:
            handle1co = start1co + (h[0] - start1co) * tension
            handle2co = start2co + (h[1] - start2co) * tension2

        if debug:
            h1 = bm.verts.new()
            h1.co = handle1co

            h2 = bm.verts.new()
            h2.co = handle2co

        if self.merge:
            for idx, vert in enumerate(seq[1:-1]):
                vert.co = handle1co

            self.merge_verts.append(seq[1:-1])
        else:
            bezierverts = mathutils.geometry.interpolate_bezier(start1co, handle1co, handle2co, start2co, len(seq) - 2)

            for idx, vert in enumerate(seq[1:-1]):
                # vert.co = vert.co + (bezierverts[idx] - vert.co) * fade
                vert.co = bezierverts[idx] + (vert.co - bezierverts[idx]) * fade

    def get_vert_sequence(self, bm, mg, verts, debug=False):
        seq = []
        if len(verts) > 3:
            # find the endpoints
            ends = [bm.verts[idx] for idx in mg if bm.verts[idx].select and sum([vselect for _, vselect, eselect in mg[bm.verts[idx].index] if eselect]) == 1]

            if not ends:  # cyclic selection
                # print("Selection is cyclic, aborting")
                popup_message("Selection is cyclic, aborting", title="Illegal Selection")
                return
            else:
                # the sequence starts at one of the ends
                end1 = ends[0]
                seq.append(end1)
                ends.remove(end1)

                while ends:
                    nextvs = [bm.verts[idx] for idx, vselect, eselect in mg[seq[-1].index] if vselect and eselect and bm.verts[idx] not in seq]
                    if nextvs:
                        nextv = nextvs[0]

                        seq.append(nextv)
                        if nextv in ends:
                            ends.remove(nextv)
                    else:
                        popup_message("Selection need to be at least 3 loop edges, aborting", title="Illegal Selection")
                        return

        if debug:
            print(" » ".join([str(v.index) for v in seq]))

        return seq
