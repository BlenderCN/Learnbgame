import bpy
import bgl
import blf
from bpy.props import IntProperty, FloatProperty, BoolProperty, EnumProperty
import bmesh
from . fuse import methoditems, handlemethoditems, tensionpresetitems
from .. utils.core import build_mesh_graph, get_2_rails, init_sweeps, get_loops, create_loop_intersection_handles, create_face_intersection_handles, get_sides
from .. utils.support import get_angle_between_edges
from .. utils.ui import step_enum, draw_init, draw_end, draw_title, draw_prop, wrap_mouse, step_collection, popup_message
from .. utils.developer import output_traceback
from .. utils.raycast import cast_ray
from .. utils import MACHIN3 as m3
import math


sideselctionitems = [("A", "A", ""),
                     ("B", "B", "")]


class GetSides(bpy.types.Operator):
    bl_idname = "machin3.get_sides"
    bl_label = "MACHIN3: Get Sides"
    bl_options = {'REGISTER', 'UNDO'}

    sideselection = EnumProperty(name="Side", items=sideselctionitems, default="A")

    # hidden
    sharp = BoolProperty(default=False)
    debuginit = BoolProperty(default=True)


    def draw(self, context):
        layout = self.layout

        column = layout.column()

        row = column.row()
        row.prop(self, "sideselection", expand=True)

    def execute(self, context):
        active = m3.get_active()

        try:
            self.main(active)
        except:
            output_traceback(self)

        return {'FINISHED'}

    def main(self, active, modal=False):
        debug = False
        # debug = True

        if debug:
            m3.clear()
            if self.debuginit:
                m3.debug_idx()
                self.debuginit = False

        mesh = active.data

        m3.set_mode("OBJECT")

        # reset the mesh the initial state
        if modal:
            self.initbm.to_mesh(active.data)

        # create bmesh
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        verts = [v for v in bm.verts if v.select]
        edges = [e for e in bm.edges if e.select]

        if any([not e.smooth for e in edges]):
            self.sharp = True

        sideA, sideB, cyclic, err = get_sides(bm, verts, edges, debug=debug)


        if sideA and sideB:
            print("cyclic:", cyclic)

            if self.sideselection == "A":
                for sA in sideA:
                    if sA["edges"]:
                        sA["edges"][0].select = True

            else:
                for sB in sideB:
                    if sB["edges"]:
                        sB["edges"][0].select = True

            bm.to_mesh(mesh)
            m3.set_mode("EDIT")

            return True
        else:
            popup_message(err[0], title=err[1])
            m3.set_mode("EDIT")

            return False

        bm.to_mesh(mesh)
        m3.set_mode("EDIT")

        return True


class DrawTimer(bpy.types.Operator):
    bl_idname = "machin3.draw_timer"
    bl_label = "Draw Timer"
    bl_options = {'REGISTER'}

    countdown = FloatProperty(name="Countdown (s)", default=2)

    def draw_HUD(self, args):
        draw_init(self, args)

        # alpha = 0.5
        alpha = self.countdown / self.time
        title = "Draw Timer"
        subtitle = "%.*fs" % (1, self.countdown)
        subtitleoffset = 200

        HUDcolor = m3.MM_prefs().modal_hud_color
        bgl.glColor4f(*HUDcolor, alpha)

        blf.position(self.font_id, self.HUDx - 7, self.HUDy, 0)
        blf.size(self.font_id, 20, 72)
        blf.draw(self.font_id, "» " + title)

        if subtitle:
            bgl.glColor4f(*HUDcolor, 0.25)
            blf.position(self.font_id, self.HUDx - 7 + subtitleoffset, self.HUDy, 0)
            blf.size(self.font_id, 15, 72)
            blf.draw(self.font_id, subtitle)

        draw_end()

    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y


        # FINISH when countdown is 0

        if self.countdown < 0:
            # print("Countdown of %d seconds finished" % (self.time))

            # remove time handler
            context.window_manager.event_timer_remove(self.TIMER)

            # remove draw handler
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
            return {'FINISHED'}


        # COUNT DOWN

        if event.type == 'TIMER':
            self.countdown -= 0.1

        return {'PASS_THROUGH'}


    def invoke(self, context, event):
        self.time = self.countdown

        # # mouse positions
        self.mouse_x = self.init_mouse_x = self.fixed_mouse_x = event.mouse_region_x
        self.mouse_y = self.init_mouse_y = self.fixed_mouse_y = event.mouse_region_y

        # draw handler
        args = (self, context)
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (args, ), 'WINDOW', 'POST_PIXEL')

        # time handler
        self.TIMER = context.window_manager.event_timer_add(0.1, context.window)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class DrawStash(bpy.types.Operator):
    bl_idname = "machin3.draw_stash"
    bl_label = "MACHIN3: Draw Stash"
    bl_options = {'REGISTER', 'UNDO'}

    xray = BoolProperty(name="X-Ray", default=False)

    def draw_VIEW3D(self, args):
        if self.stash.obj:
            mesh = self.stash.obj.data

            # NOTE you can also draw quads, perhaps even ngons:
            # https://blender.stackexchange.com/questions/71980/modal-operator-to-highlight

            # offset amount depends on size of active object
            offset = sum([d for d in self.active.dimensions]) / 3 * 0.001

            edgewidth = 2
            edgecolor = (1.0, 1.0, 1.0, 0.75)

            bgl.glEnable(bgl.GL_BLEND)

            if self.xray:
                bgl.glDisable(bgl.GL_DEPTH_TEST)

            for edge in mesh.edges:
                v1 = mesh.vertices[edge.vertices[0]]
                v2 = mesh.vertices[edge.vertices[1]]

                # bring the coordinates into world space
                # and push them out abit so they are drawn on top of the mesh
                v1co = v1.co + v1.normal * offset + self.active.location
                v2co = v2.co + v2.normal * offset + self.active.location

                bgl.glLineWidth(edgewidth)
                bgl.glColor4f(*edgecolor)

                bgl.glBegin(bgl.GL_LINES)

                bgl.glVertex3f(*v1co)
                bgl.glVertex3f(*v2co)

            draw_end()

    def draw_HUD(self, args):
        draw_init(self, args)

        draw_title(self, "Draw Stash")

        draw_prop(self, "Stash", self.stash.index, key="scroll UP/DOWN")
        self.offset += 10

        if self.stash.obj:
            draw_prop(self, "X-Ray", self.xray, offset=18, key="toggle X")
        else:
            draw_prop(self, "INVALID", "Stash Object Not Found", offset=18, HUDcolor=(1, 0, 0))

        draw_end()


    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        # if event.type == 'LEFTMOUSE':
            # to select on a stash, you need to link it to the scene
            # make it invisible by rendering it as bbox or maybe make it transparent somehow? didnt wazour do this??
            # you can then raycast on it by excluding the active mesh, which can even be in edit mode and raycast will still work!
            # pass

        if event.type in {'WHEELUPMOUSE', 'UP_ARROW', 'ONE'} and event.value == 'PRESS':
            self.stash = step_collection(self.active.MM, self.stash, "stashes", "active_stash_idx", 1)

        elif event.type in {'WHEELDOWNMOUSE', 'DOWN_ARROW', 'TWO'} and event.value == 'PRESS':
            self.stash = step_collection(self.active.MM, self.stash, "stashes", "active_stash_idx", -1)

        if self.stash.obj:
            if event.type == 'X' and event.value == 'PRESS':
                self.xray = not self.xray

        # VIEWPORT control

        if event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}

        # FINISH

        elif event.type in ['LEFTMOUSE', 'SPACE']:
            # do something with self.stash

            bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
            return {'FINISHED'}

        # CANCEL

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
            # self.cancel_modal()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.active = m3.get_active()

        if self.active.MM.stashes:
            self.stash = self.active.MM.stashes[self.active.MM.active_stash_idx]

            # mouse positions
            self.mouse_x = self.init_mouse_x = self.fixed_mouse_x = event.mouse_region_x
            self.mouse_y = self.init_mouse_y = self.fixed_mouse_y = event.mouse_region_y

            args = (self, context)
            self.VIEW3D = bpy.types.SpaceView3D.draw_handler_add(self.draw_VIEW3D, (args, ), 'WINDOW', 'POST_VIEW')
            self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (args, ), 'WINDOW', 'POST_PIXEL')

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            print("%s has no stashes" % (self.active.name))
            return {'CANCELLED'}


class VertexInfo(bpy.types.Operator):
    bl_idname = "machin3.vertex_info"
    bl_label = "MACHIN3: Vertex Info"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active = m3.get_active()

        # create bmesh
        bm = bmesh.new()
        bm.from_mesh(active.data)
        bm.verts.ensure_lookup_table()

        verts = [v for v in bm.verts if v.select]

        for v in verts:
            print("vert:", v)

            print("loops:")
            for l in v.link_loops:
                print(" »", l)

            print("edges:")
            for e in v.link_edges:
                print(" »", e)


        return {'FINISHED'}


class RayCast(bpy.types.Operator):
    bl_idname = "machin3.raycast"
    bl_label = "Raycast"
    bl_options = {'REGISTER', 'UNDO'}


    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        elif event.type == "LEFTMOUSE" and event.value == 'PRESS':
            m3.clear()

            print("mouse:", self.mouse_x, self.mouse_y)

            coord = (self.mouse_x, self.mouse_y)
            # obj, coords, normal, face_idx = cast_ray(context, coord)
            obj, coords, normal, face_idx = cast_ray(context, coord, exclude_objs=[context.active_object])

            print("object:", obj)
            print("coords:", coords)
            print("normal:", normal)
            print("face_idx:", face_idx)

        elif event.type == 'MIDDLEMOUSE':
            return {'PASS_THROUGH'}

        elif event.type in {'SPACE'}:
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            return {'CANCELLED'}

        # return {'PASS_THROUGH'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.mouse_x = event.mouse_region_x
        self.mouse_y = event.mouse_region_y

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class GetLoopsHandles(bpy.types.Operator):
    bl_idname = "machin3.loops_or_handles"
    bl_label = "MACHIN3: Loops or Handles"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Create rounded Bevels from Chamfers"

    loops_or_handles = EnumProperty(name="Get Loops or Handles", items=[('LOOPS', "Loops", ""),
                                                                        ('HANDLES', "Handles", "")], default="LOOPS")

    handlemethod = EnumProperty(name="Unchamfer Method", items=handlemethoditems, default="FACE")

    tension = FloatProperty(name="Tension", default=1, min=0.01, max=4, step=0.1)

    average = BoolProperty(name="Average Tension", default=False)

    force_projected = BoolProperty(name="Force Projected Loops", default=False)

    reverse = BoolProperty(name="Reverse", default=False)

    # hidden
    cyclic = BoolProperty(name="Cyclic", default=False)
    single = BoolProperty(name="Single", default=False)


    def draw(self, context):
        layout = self.layout
        column = layout.column()

        row = column.row()
        row.prop(self, "loops_or_handles", expand=True)
        column.separator()

        row = column.row()
        row.prop(self, "handlemethod", expand=True)
        column.separator()

        column.prop(self, "tension")

        if self.handlemethod == "FACE":
            column.prop(self, "average")

        column.separator()
        column.prop(self, "force_projected")

        if self.single:
            column.separator()
            column.prop(self, "reverse")


    def execute(self, context):
        active = m3.get_active()

        self.main(active)

        return {'FINISHED'}

    def main(self, active):
        debug = True
        # debug = False

        if debug:
            m3.clear()
            m3.debug_idx()

        m3.set_mode("OBJECT")

        # create bmesh
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

            # debug_sweeps(sweeps, self.cyclic)
            get_loops(bm, faces, sweeps, force_projected=self.force_projected, debug=debug)

            # debug_sweeps(sweeps, self.cyclic)

            for f in faces:
                f.select = False

            if self.loops_or_handles == "HANDLES":
                if self.handlemethod == "FACE":
                    create_face_intersection_handles(bm, sweeps, tension=self.tension, average=self.average, debug=debug)
                elif self.handlemethod == "LOOP":
                    create_loop_intersection_handles(bm, sweeps, self.tension, debug=debug)

        bm.to_mesh(active.data)

        m3.set_mode("EDIT")

        if self.loops_or_handles == "HANDLES":
            m3.set_mode("VERT")
            m3.unselect_all("MESH")

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


class DrawHUD(bpy.types.Operator):
    bl_idname = "machin3.draw_hud"
    bl_label = "Draw HUD"
    bl_options = {'REGISTER', 'UNDO'}

    segments = IntProperty(name="Segments", default=0, min=0)
    width = FloatProperty(name="Width", default=0)
    method = EnumProperty(name="Method", items=methoditems, default="FUSE")
    smooth = BoolProperty(name="Smooth", default=False)

    # modal
    allowmodalwidth = BoolProperty(default=False)

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        column.prop(self, "segments")
        column.prop(self, "width")
        column.prop(self, "method")


    def draw_HUD(self, args):
        draw_init(self, args)

        draw_title(self, "HUD Drawing")

        draw_prop(self, "Segments", self.segments, key="scroll UP/DOWN")
        draw_prop(self, "Width", self.width, offset=18, decimal=3, active=self.allowmodalwidth, key="move LEFT/RIGHT, toggle W")
        draw_prop(self, "Method", self.method, offset=18, key="ALT + scroll UP/DOWN")
        self.offset += 18

        draw_prop(self, "Smooth", self.smooth, offset=18, key="toggle S")

        draw_end()


    def modal(self, context, event):
        context.area.tag_redraw()

        # update mouse postion for HUD
        if event.type == "MOUSEMOVE":
            self.mouse_x = event.mouse_region_x
            self.mouse_y = event.mouse_region_y

        events = ['WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'S', 'W']

        # only consider MOUSEMOVE is allowmodalwith is actually turned on
        if self.allowmodalwidth:
            events.append('MOUSEMOVE')
            context.window.cursor_set("SCROLL_X")
        else:
            context.window.cursor_set("CROSSHAIR")

        if event.type in events:

            if event.type == 'MOUSEMOVE':
                wrap_mouse(self, context, event, x=True)
                delta_x = event.mouse_x - self.init_mouse_x  # bigger if going to the right

                if self.allowmodalwidth:
                    self.width = delta_x * 0.001

            elif event.type == 'WHEELUPMOUSE':
                if event.alt:
                    self.method = step_enum(self.method, methoditems, 1)
                else:
                    self.segments += 1

            elif event.type == 'WHEELDOWNMOUSE':
                if event.alt:
                    self.method = step_enum(self.method, methoditems, -1)
                else:
                    self.segments -= 1

            elif event.type == 'W' and event.value == "PRESS":
                if event.alt:
                    self.allowmodalwidth = False
                    self.width = 0
                else:
                    self.allowmodalwidth = not self.allowmodalwidth

            elif event.type == 'S' and event.value == "PRESS":
                self.smooth = not self.smooth

            # execute

            try:
                self.execute(context)
            except:
                output_traceback(self)
                bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
                return {'FINISHED'}

        elif event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}

        elif event.type in {'LEFTMOUSE', 'SPACE'}:
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')
            return {'CANCELLED'}

        # return {'PASS_THROUGH'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        # mouse positions
        self.mouse_x = self.init_mouse_x = self.fixed_mouse_x = event.mouse_region_x
        self.mouse_y = self.init_mouse_y = self.fixed_mouse_y = event.mouse_region_y

        # Add the region OpenGL drawing callback
        args = (self, context)
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (args, ), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if self.segments == 7:
            # raise Exception
            7 / 0
        return True


class GetFacesLinkedToVerts(bpy.types.Operator):
    bl_idname = "machin3.get_faces_linked_to_verts"
    bl_label = "MACHIN3: Get Faces Linked to Verts"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active = m3.get_active()
        m3.debug_idx()

        m3.set_mode("OBJECT")

        bm = bmesh.new()
        bm.from_mesh(active.data)
        bm.normal_update()

        verts = [v for v in bm.verts if v.select]

        for v in verts:
            print(v)
            for f in v.link_faces:
                print(f)
            print()

        bm.to_mesh(active.data)

        m3.set_mode("EDIT")

        return {'FINISHED'}


class GetLength(bpy.types.Operator):
    bl_idname = "machin3.get_length"
    bl_label = "MACHIN3: Get Length"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
            active = m3.get_active()
            mesh = active.data

            m3.set_mode("OBJECT")

            bm = bmesh.new()
            bm.from_mesh(mesh)
            bm.normal_update()

            edges = [e for e in bm.edges if e.select]

            for edge in edges:
                print("edge:", edge.index, "length:", edge.calc_length())


            bm.to_mesh(mesh)

            m3.set_mode("EDIT")

            return {'FINISHED'}


class GetAngle(bpy.types.Operator):
    bl_idname = "machin3.get_angle"
    bl_label = "MACHIN3: Get Angle"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active = m3.get_active()
        mesh = active.data

        m3.set_mode("OBJECT")

        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.normal_update()

        edges = [e for e in bm.edges if e.select]

        if len(edges) == 1:
            e = edges[0]

            angle = math.degrees(e.calc_face_angle())
            print(angle)


        elif len(edges) == 2:
            e1 = edges[0]
            e2 = edges[1]

            angle = get_angle_between_edges(e1, e2, radians=False)
            print(angle)

        bm.to_mesh(mesh)

        m3.set_mode("EDIT")

        return {'FINISHED'}


class DebugToggle(bpy.types.Operator):
    bl_idname = "machin3.meshmachine_debug"
    bl_label = "MACHIN3: Debug MESHmachine"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        m3.MM_prefs().debug = not m3.MM_prefs().debug

        return {'FINISHED'}
