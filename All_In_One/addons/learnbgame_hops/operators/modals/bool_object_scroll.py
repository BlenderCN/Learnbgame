import bpy
import gpu
from bgl import *
from gpu_extras.batch import batch_for_shader
from bpy.types import Operator
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi, draw_box
from ... preferences import Hops_text_color, Hops_text2_color, Hops_border_color, Hops_border2_color, get_preferences


class HOPS_OT_BoolObjectScroll(Operator):
    bl_idname = "hops.bool_scroll_objects"
    bl_label = "Scroll Booleans"
    bl_description = "Use the scroll wheel to scroll through boolean modifiers on the selected object."

    def modal(self, context, event):

        if event.type == 'WHEELUPMOUSE':
            self.obj_index += 1

        if event.type == 'WHEELDOWNMOUSE':
            self.obj_index -= 1

        if self.obj_index >= len(self.obj_list):
            self.obj_index = 0
        if self.obj_index < 0:
            self.obj_index = len(self.obj_list)-1

        obj = self.obj_list[self.obj_index]["object"]

        for data in self.obj_list:
            data["object"].hide_viewport = data["override"]

        override_value = self.obj_list[self.obj_index]["override"]

        if self.show_current:
            obj.hide_viewport = False

        self.obj_name = obj.name

        if event.type == 'A' and event.value == 'PRESS':
            self.obj_list[self.obj_index]["override"] = not override_value
            obj.hide_viewport = override_value

#         if event.type == 'O' and event.value == 'PRESS':
#             self.show_current = not self.show_current

        if event.type == 'T' and event.value == 'PRESS':
            self.modifiers[self.obj_index].show_viewport = not self.modifiers[self.obj_index].show_viewport

        if event.ctrl: # ctrl+a to toggle object visibility
            if event.type == 'A' and event.value == 'PRESS':
                self.ctrl_a = not self.ctrl_a
                for data in self.obj_list:
                    data["override"] = self.ctrl_a

        if event.type == "H" and event.value == "PRESS":
            get_preferences().hops_modal_help = not get_preferences().hops_modal_help

        if event.type in {'LEFTMOUSE', 'RET', 'NUMPAD_ENTER'}:
            self.finish()
            context.active_object.select_set(state=False)
            obj.select_set(state=True)
            context.view_layer.objects.active = obj
            return {"FINISHED"}

        if event.type in {'RIGHTMOUSE', 'ESC', 'BACK_SPACE'}:
            self.finish()
            for data in self.obj_list:
                data["object"].hide_viewport = data["hide"]
            return {'CANCELLED'}

        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        self.start_mouse_position = [event.mouse_region_x, event.mouse_region_y]
        self.modifiers = [i for i in context.object.modifiers if i.type == "BOOLEAN"]
        self.obj_list = [{"object": mod.object, "hide": mod.object.hide_viewport, "override": True} for mod in self.modifiers if mod.object is not None]
        self.obj_index = 0
        self.obj_name = ""
        self.ctrl_a = True
        self.show_current = True

        if not self.obj_list:
            return{'CANCELLED'}

        args = (context, )
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_ui, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def finish(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
        return {'FINISHED'}

    def draw_ui(self, context):
        x, y = self.start_mouse_position
        object = context.active_object

        set_drawing_dpi(get_dpi())
        factor = get_dpi_factor()

        color_text1 = Hops_text_color()
        color_text2 = Hops_text2_color()
        color_border = Hops_border_color()
        color_border2 = Hops_border2_color()

        vertices = (
            (x - 1 * factor, y + 23 * factor), (x - 1 * factor, y + 4 * factor), (x + 44 * factor, y + 23 * factor), (x + 44 * factor, y + 4 * factor),
            (x + 46 * factor, y + 23 * factor), (x + 46 * factor, y + 4 * factor), (x + 220 * factor, y + 23 * factor), (x + 220 * factor, y + 4 * factor),
            (x + 46 * factor, y + 42 * factor), (x + 46 * factor, y + 26 * factor), (x + 220 * factor, y + 42 * factor), (x + 220 * factor, y + 26 * factor))

        indices = (
            (0, 1, 2), (1, 2, 3), (4, 5, 6), (5, 6, 7), (8, 9, 10), (9, 10, 11))

        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)

        shader.bind()
        shader.uniform_float("color", (0.17, 0.17, 0.17, 1))
        glEnable(GL_BLEND)
        batch.draw(shader)
        glDisable(GL_BLEND)
        red = [1, 0.15, 0.15, 0.9]

        draw_text("{}".format(self.obj_index + 1),
                  x + 25 * factor, y + 9 * factor, size=12, color=(0.831, 0.831, 0.831, 1))

        name_color = color_text2
        if not self.modifiers[self.obj_index].show_viewport:
            name_color = red

        draw_text("{}".format(self.obj_name),
                  x + 50 * factor, y + 9 * factor, size=12, color=(0.831, 0.831, 0.831, 1))

        draw_text("{}".format(self.modifiers[self.obj_index].name),
                  x + 50 * factor, y + 28 * factor, size=12, color=(name_color))

        self.draw_help(context, x, y, factor)

    def draw(self, context):

        try:
            x, y = self.start_mouse_position
        except:
            x, y = 0, 0

        set_drawing_dpi(get_dpi())
        factor = get_dpi_factor()
        color_text1 = Hops_text_color()
        color_text2 = Hops_text2_color()
        color_border = Hops_border_color()
        color_border2 = Hops_border2_color()
        red = [1, 0.15, 0.15, 0.9]

        # front
        draw_box(x - 8 * factor, y + 8 * factor, 32 * factor, 34 * factor, color=color_border2)
        # back
        draw_box(x + 204 * factor, y + 8 * factor, 2 * factor, 34 * factor, color=color_border2)
        # top
        draw_box(x + 24 * factor, y + 24 * factor, 180 * factor, 2 * factor, color=color_border2)
        # bot
        draw_box(x + 24 * factor, y - 8 * factor, 180 * factor, 2 * factor, color=color_border2)
        # middle
        # draw_box(x -8 * factor, y + 8 * factor, 214 * factor , 34* factor, color = color_border2)
        draw_box(x + 24 * factor, y + 8 * factor, 180 * factor, 30 * factor, color=color_border)

        if self.obj_index + 1 >= 10:
            draw_text(str(self.obj_index + 1), x - 8 * factor, y - 2, size=23, color=color_text1)
        else:
            draw_text(str(self.obj_index + 1), x + 2 * factor, y - 2, size=23, color=color_text1)

        name_color = color_text2
        if not self.modifiers[self.obj_index].show_viewport:
            name_color = red

        draw_text("{}".format(self.obj_name), x + 27 * factor, y + 9 * factor, size=12, color=color_text2)

        draw_text("{}".format(self.modifiers[self.obj_index].name), x + 27 * factor, y - 4 * factor, size=12, color=name_color)

        if get_preferences().hops_modal_help:
            self.draw_help(context, x, y, factor)

    def draw_help(self, context, x, y, factor):

        color_text2 = Hops_text2_color()

        if get_preferences().hops_modal_help:

            draw_text(" scroll - change boolean visibility",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)

            draw_text(" a - toggle current visibility",
                      x + 45 * factor, y - 26 * factor, size=11, color=color_text2)

            draw_text(" ctrl+a - toggle all visibility",
                      x + 45 * factor, y - 38 * factor, size=11, color=color_text2)

    #       draw_text(" o - toggle show current object",
    #                  x + 45 * factor, y - 60* factor, size=11, color=color_text2)

            draw_text(" t - toggle modifier visibility",
                      x + 45 * factor, y - 50 * factor, size=11, color=color_text2)

        else:
            draw_text(" H - Show/Hide Help",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)
