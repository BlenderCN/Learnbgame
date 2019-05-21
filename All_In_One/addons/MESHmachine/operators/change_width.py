import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty
import bmesh
import mathutils
from ..utils.graph import build_mesh_graph
from ..utils.core import get_2_rails, init_sweeps, debug_sweeps, get_loops
from ..utils.ui import popup_message, draw_title, draw_prop, draw_init, draw_end, wrap_mouse
from ..utils.developer import output_traceback
from ..utils import MACHIN3 as m3



# TODO: optional independent controlls for each rail
# NOTE: look into bmesh.ops.offset_edgeloops(bm, edges, use_cap_endpoint)
# TODO: instead of the separate tension and width controls, do a single value, a ratio that determines the influence of both and goes from -1 to 1

# TODO: add force projected loop method, and maybe also the offset loop method from the chamfer tool

# TODO: projected loop

class ChangeWidth(bpy.types.Operator):
    bl_idname = "machin3.change_width"
    bl_label = "MACHIN3: Change Width"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Change Chamfer Width"

    width = FloatProperty(name="Width", default=0.0, step=0.1)

    reverse = BoolProperty(name="Reverse", default=False)

    # hidden
    single = BoolProperty(name="Single", default=False)
    cyclic = BoolProperty(name="Cyclic", default=False)

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        column = layout.column()

        column.prop(self, "width")

        if self.single:
            column.prop(self, "reverse")

    @classmethod
    def poll(cls, context):
        bm = bmesh.from_edit_mesh(context.active_object.data)
        return len([f for f in bm.faces if f.select]) >= 1


    def draw_HUD(self, args):
        draw_init(self, args)

        draw_title(self, "Change Width")

        draw_prop(self, "Width", self.width, decimal=3, key="move LEFT/RIGHT")
        if self.single:
            draw_prop(self, "Reverse", self.reverse, offset=18, key="toggle R")

        draw_end()

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        if event.type in ['MOUSEMOVE', 'R']:

            # CONTROL width

            if event.type == 'MOUSEMOVE':
                wrap_mouse(self, context, event, x=True)

                delta = self.mouse_x - self.init_mouse_x  # bigger if going to the right

                if event.shift:
                    self.width = delta * 0.0001
                elif event.ctrl:
                    self.width = delta * 0.01
                else:
                    self.width = delta * 0.001

            # TOGGLE reverse

            elif event.type == 'R' and event.value == "PRESS":
                self.reverse = not self.reverse

            # modal change width
            try:
                ret = self.main(self.active, modal=True)

                # caught and error
                if ret is False:
                    bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
                    return {'FINISHED'}
            # unexpected error
            except:
                output_traceback(self)
                bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
                return {'FINISHED'}

        # VIEWPORT control

        elif event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}

        # FINISH

        elif event.type in ['LEFTMOUSE', 'SPACE']:
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
        self.active = m3.get_active()

        # make sure the current edit mode state is saved to obj.data
        self.active.update_from_editmode()

        # save this initial mesh state, this will be used when canceling the modal and to reset it for each mousemove event
        self.initbm = bmesh.new()
        self.initbm.from_mesh(self.active.data)

        # mouse positions
        self.mouse_x = self.init_mouse_x = self.fixed_mouse_x = event.mouse_region_x
        self.mouse_y = self.init_mouse_y = self.fixed_mouse_y = event.mouse_region_y

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

        # reset the mesh the initial state
        if modal:
            self.initbm.to_mesh(active.data)

        # create new bmesh
        bm = bmesh.new()
        bm.from_mesh(active.data)

        bm.normal_update()
        bm.verts.ensure_lookup_table()

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

            sweeps = init_sweeps(bm, active, rails, debug=debug)
            # debug_sweeps(sweeps)
            get_loops(bm, faces, sweeps, debug=debug)

            changed_width = change_width(bm, sweeps, self.width, debug=debug)

            self.clean_up(bm, sweeps, magicloop=True, debug=debug)

            if changed_width:
                bm.to_mesh(active.data)
            else:
                popup_message("Something went wrong, likely not a valid chamfer selection.", title="Chamfer Width")

        m3.set_mode("EDIT")
        # m3.set_mode("VERT")

        if ret:
            if changed_width:
                return True

        return False

    def clean_up(self, bm, sweeps, magicloop=True, debug=False):
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
                print("Removed magic loops:", ", ".join(magic_loop_ids))


def change_width(bm, sweeps, width, debug=False):
    # NOTE; as the sweeps are vertex pairs, we are gonna iterate over both sides of the chamfer(both rails) at the same time

    # get the first and second verts and their loop edges
    v1 = sweeps[0]["verts"][0]
    v1_next = sweeps[1]["verts"][0]

    v2 = sweeps[0]["verts"][1]
    v2_next = sweeps[1]["verts"][1]

    loop1 = sweeps[0]["loops"][0]
    loop1_next = sweeps[1]["loops"][0]

    loop2 = sweeps[0]["loops"][1]
    loop2_next = sweeps[1]["loops"][1]

    # get the end verts on the loop edges, to build the direction vectors
    loop1_end = loop1.other_vert(v1)
    loop1_end_next = loop1_next.other_vert(v1_next)
    loop1_dir = v1.co + (loop1_end.co - v1.co).normalized() * width

    loop2_end = loop2.other_vert(v2)
    loop2_end_next = loop2_next.other_vert(v2_next)
    loop2_dir = v2.co + (loop2_end.co - v2.co).normalized() * width

    # the direction of the rails, from one vert to the next one on the same rail
    rail1_dir = v1_next.co - v1.co
    rail2_dir = v2_next.co - v2.co

    # find the endpoint on the next loop edge, not by checkin the other vert, but by drawing a vector parallel to the rail and interecting it with the direction of the (next) loop
    h1 = mathutils.geometry.intersect_line_line(loop1_dir, loop1_dir + rail1_dir, v1_next.co, loop1_end_next.co)
    h2 = mathutils.geometry.intersect_line_line(loop2_dir, loop2_dir + rail2_dir, v2_next.co, loop2_end_next.co)

    if h1 and h2:
        v1.co = loop1_dir
        v2.co = loop2_dir

        # we did all of this to get the first loop end, which will be the starting point for all the other offsets
        loop1_ends = []
        loop1_ends.append(h1[0])  # maybe average h[0] and h[1] instead of taking just the first?, they should be the same, but you never know?

        loop2_ends = []
        loop2_ends.append(h2[0])

        # repeat the above for all other verts
        # TODO: put it all in the for loop, if possible
        for idx, sweep in enumerate(sweeps):
            if idx == 0:  # skip first index, its done above
                continue
            if idx == len(sweeps) - 1:
                v1_next.co = h1[0]
                v2_next.co = h2[0]
                break

            v1 = sweep["verts"][0]
            v1_next = sweeps[idx + 1]["verts"][0]

            v2 = sweep["verts"][1]
            v2_next = sweeps[idx + 1]["verts"][1]

            loop1 = sweep["loops"][0]
            loop1_next = sweeps[idx + 1]["loops"][0]

            loop2 = sweep["loops"][1]
            loop2_next = sweeps[idx + 1]["loops"][1]

            # here we take the loop ends from the list initialized above
            loop1_end = loop1_ends[-1]
            loop1_end_next = loop1_next.other_vert(v1_next)

            loop2_end = loop2_ends[-1]
            loop2_end_next = loop2_next.other_vert(v2_next)

            loop1_dir = v1.co + (loop1_end - v1.co)
            sweep1_dir = v1_next.co - v1.co

            loop2_dir = v2.co + (loop2_end - v2.co)
            sweep2_dir = v2_next.co - v2.co

            v1.co = loop1_dir
            v2.co = loop2_dir

            h1 = mathutils.geometry.intersect_line_line(loop1_dir, loop1_dir + sweep1_dir, v1_next.co, loop1_end_next.co)
            h2 = mathutils.geometry.intersect_line_line(loop2_dir, loop2_dir + sweep2_dir, v2_next.co, loop2_end_next.co)

            if h1 and h2:
                loop1_ends.append(h1[0])
                loop2_ends.append(h2[0])
            else:
                return False
    else:
        return False

    return True
