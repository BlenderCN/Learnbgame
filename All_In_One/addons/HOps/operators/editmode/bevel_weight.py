import bpy
import bmesh
import gpu
from bgl import *
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi, draw_box
from ... preferences import Hops_text_color, Hops_text2_color, Hops_border_color, Hops_border2_color, get_preferences


class HOPS_OT_AdjustBevelWeightOperator(bpy.types.Operator):
    bl_idname = "hops.bevel_weight"
    bl_label = "Adjust Bevel Weight"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """Adjust the bevel weight of selected edges
Press H for help"""

    @classmethod
    def poll(cls, context):
        object = context.active_object
        return(object.type == 'MESH' and context.mode == 'EDIT_MESH')

    def invoke(self, context, event):
        self.value = 0
        self.start_value = self.detect(context)
        self.offset = 0
        self.start_mouse_position = Vector((event.mouse_region_x, event.mouse_region_y))
        self.last_mouse_x = event.mouse_region_x

        args = (context, )
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_ui, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        divisor = 5000 if event.shift else 230
        offset_x = event.mouse_region_x - self.last_mouse_x
        self.offset += offset_x / divisor / get_dpi_factor()
        self.value_base = float("{:.2f}".format(self.start_value - self.offset))
        self.value = max(self.value_base, 0) and min(self.value_base, 1)

        if not event.ctrl and not event.shift:
            self.value = round(self.value, 1)

        obj = bpy.context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        bw = bm.edges.layers.bevel_weight.verify()

        selected = [e for e in bm.edges if e.select]
        for e in selected:
            e[bw] = self.value

        bmesh.update_edit_mesh(me)

        if event.type == "H" and event.value == "PRESS":
            get_preferences().hops_modal_help = not get_preferences().hops_modal_help

        if event.type in ("ESC", "RIGHTMOUSE"):
            for e in selected:
                e[bw] = self.start_value
            bmesh.update_edit_mesh(me)
            return self.finish()

        if event.type in ("SPACE", "LEFTMOUSE"):
            return self.finish()

        if event.type == 'A' and event.value == 'PRESS' and event.ctrl:
            selectedbw = [e for e in bm.edges if e[bw] > 0]
            for e in selectedbw:
                e.select_set(True)

        elif event.type == 'A' and event.value == 'PRESS' and not event.ctrl:
            bpy.ops.mesh.select_linked(delimit=set())
            selectedbw = [e for e in bm.edges if e[bw] == 0]

            for e in selectedbw:
                e.select_set(False)
                for elem in reversed(bm.select_history):
                    if isinstance(elem, bmesh.types.BMEdge):
                        elem.select_set(True)

        self.last_mouse_x = event.mouse_region_x
        context.area.tag_redraw()
        return {"RUNNING_MODAL"}

    def finish(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
        return {"FINISHED"}

    def detect(self, context):

        obj = bpy.context.object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        bw = bm.edges.layers.bevel_weight.verify()

        selected = [e for e in bm.edges if e.select]

        bmesh.update_edit_mesh(me)

        if len(selected) > 0:
            return selected[-1][bw]
        else:
            return 0


    def draw_ui(self, context):
        x, y = self.start_mouse_position
        object = context.active_object

        set_drawing_dpi(get_dpi())
        factor = get_dpi_factor()

        color_text1 = Hops_text_color()
        color_text2 = get_preferences().Hops_hud_help_color
        color_border = Hops_border_color()
        color_border2 = Hops_border2_color()

        vertices = (
            (x - 1 * factor, y + 23 * factor), (x - 1 * factor, y + 4 * factor), (x + 140 * factor, y + 23 * factor), (x + 140 * factor, y + 4 * factor))

        indices = (
            (0, 1, 2), (1, 2, 3))

        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)

        shader.bind()
        shader.uniform_float("color", get_preferences().Hops_hud_color)
        glEnable(GL_BLEND)
        batch.draw(shader)
        glDisable(GL_BLEND)

        draw_text(" {:.2f} - B-Weight".format(self.value),
                  x + 27 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        self.draw_help(context, x, y, factor)

    def draw(self, context):
        x, y = self.start_mouse_position
        value = self.value

        set_drawing_dpi(get_dpi())
        factor = get_dpi_factor()
        color_text1 = Hops_text_color()
        color_text2 = get_preferences().Hops_hud_help_color
        color_border = Hops_border_color()
        color_border2 = Hops_border2_color()

        # front
        draw_box(x - 8 * factor, y + 8 * factor, 53 * factor, 34 * factor, color=color_border2)
        # back
        draw_box(x + 195 * factor, y + 8 * factor, 2 * factor, 34 * factor, color=color_border2)
        # top
        draw_box(x + 45 * factor, y + 24 * factor, 150 * factor, 2 * factor, color=color_border2)
        # bot
        draw_box(x + 45 * factor, y - 8 * factor, 150 * factor, 2 * factor, color=color_border2)
        # middle
        # draw_box(x -8 * factor, y + 8 * factor, 204 * factor , 34* factor, color = color_border2)
        draw_box(x + 45 * factor, y + 8 * factor, 150 * factor, 30 * factor, color=color_border)

        draw_text(" {:.2f} - B-Weight".format(value),
                  x - 8 * factor, y, size=20, color=color_text2)

        if get_preferences().hops_modal_help:
            self.draw_help(context, x, y, factor)

    def draw_help(self, context, x, y, factor):

        color_text1 = Hops_text_color()
        color_text2 = get_preferences().Hops_hud_help_color
        color_border = Hops_border_color()
        color_border2 = Hops_border2_color()

        if get_preferences().hops_modal_help:

            draw_text(" A - select all weights in mesh",
                      x + 45 * factor, y - 24 * factor, size=11, color=color_text2)

            draw_text(" ctrl + A - select all weights",
                      x + 45 * factor, y - 36 * factor, size=11, color=color_text2)

        else:
            draw_text(" H - Show/Hide Help",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)
