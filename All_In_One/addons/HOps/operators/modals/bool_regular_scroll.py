import bpy
import gpu
from bgl import *
from gpu_extras.batch import batch_for_shader
from bpy.types import Operator
from bpy.props import BoolProperty
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi, draw_box
from ... preferences import Hops_text_color, Hops_text2_color, Hops_border_color, Hops_border2_color, get_preferences


class HOPS_OT_BoolScroll(Operator):
    bl_idname = "hops.bool_scroll"
    bl_label = "Scroll Booleans"
    bl_description = "Use the scroll wheel to scroll through boolean modifiers on the selected object."

    additive : BoolProperty()

    def modal(self, context, event):

        if event.type == "WHEELUPMOUSE" or event.type == "NUMPAD_PLUS" and event.value == "PRESS":
            self.bool_index += 1

        if event.type == "WHEELDOWNMOUSE" or event.type == "NUMPAD_MINUS" and event.value == "PRESS":
            self.bool_index -= 1

        if self.loop:
            if self.bool_index >= len(self.bools):
                self.bool_index = 0
            if self.bool_index < 0:
                self.bool_index = len(self.bools) - 1

        else:
            self.bool_index = max(min(self.bool_index, len(self.bools) - 1), 0)

        if event.type == 'L' and event.value == 'PRESS':
            self.loop = not self.loop

        if event.type == 'A' and event.value == 'RELEASE':
            if self.bools[list(self.bools.keys())[self.bool_index]] is not None:
                # if list(self.bools.keys())[self.bool_index] is not None:
                override_value = self.bools[list(self.bools.keys())[self.bool_index]]["override"]
                self.bools[list(self.bools.keys())[self.bool_index]]["override"] = not override_value

        self.original_obj.select_set(True)
        context.view_layer.objects.active = self.original_obj

        if event.type == 'M' and event.value == 'PRESS':
            self.all_mods = not self.all_mods
            self.bools = {None: None}
            self.bool_index = 0

            for mod in self.bools:
                if mod is not None:
                    mod.show_viewport = self.bools[mod]["original_show_viewport"]

            for mod in context.object.modifiers:
                if self.all_mods:
                    self.bools.update({mod: {"original_show_viewport": mod.show_viewport, "override": False}})

        if self.additive:
            for count, mod in enumerate(self.bools):
                if mod is not None:
                    if count <= self.bool_index:
                        mod.show_viewport = True
                    else:
                        mod.show_viewport = False
                    if self.bools[mod]["override"] or self.bools[list(self.bools.keys())[self.bool_index]] is None:
                        mod.show_viewport = False

        else:
            for mod in self.bools:
                if mod is not None and hasattr(mod, "object"):
                    mod.show_viewport = self.bools[mod]["override"]  # hide all mods except for those pressed A on.
                    mod.object.select_set(False)

                    mod.object.hide_viewport = True
                    if mod.show_viewport:  # show and select objects that have modifier being shown in viewport.
                        mod.object.hide_viewport = False

                        mod.object.select_set(True)

            if self.bools[list(self.bools.keys())[self.bool_index]] is not None:
                current_bool = list(self.bools.keys())[self.bool_index]
                current_bool.show_viewport = True  # show viewport on the current mod.
                if hasattr(current_bool, "object"):

                    current_bool.object.hide_viewport = False

                    current_bool.object.select_set(True)

        if event.type == "H" and event.value == "PRESS":
            get_preferences().hops_modal_help = not get_preferences().hops_modal_help

        if event.type in {'LEFTMOUSE', 'RET', 'NUMPAD_ENTER'}:
            self.finish()
            for mod in self.bools:
                if mod is not None and hasattr(mod, "object"):
                    if not mod.show_viewport:
                        mod.object.hide_viewport = True
                    else:

                        mod.object.hide_viewport = False
                        mod.object.select_set(True)

            if not self.additive:
                if hasattr(current_bool, "object") and current_bool.object is not None:
                    context.active_object.select_set(False)
                    current_bool.object.select_set(True)
                    context.view_layer.objects.active = current_bool.object
            return {"FINISHED"}

        if event.type in {'RIGHTMOUSE', 'ESC', 'BACK_SPACE'}:
            self.finish()
            for mod in self.bools:
                if mod is not None:
                    mod.show_viewport = self.bools[mod]["original_show_viewport"]
            return {'CANCELLED'}

        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        self.start_mouse_position = [event.mouse_region_x, event.mouse_region_y]
        self.modifiers = [mod for mod in context.object.modifiers if mod.type == "BOOLEAN"]
        self.bools = {None: None}
        self.bool_index = 0
        self.all_mods = False
        self.loop = False
        self.original_obj = context.object

        for mod in self.modifiers:
            if mod.object is not None:
                self.bools.update({mod: {"original_show_viewport": mod.show_viewport, "override": False, "hide": mod.object.hide_viewport}})

        if len(self.bools) == 1:
            return {'CANCELLED'}

        args = (context, )
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_ui, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def finish(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
        return {"FINISHED"}

    def draw_ui(self, context):
        x, y = self.start_mouse_position
        object = context.active_object

        set_drawing_dpi(get_dpi())
        factor = get_dpi_factor()

        color_text1 = Hops_text_color()
        color_text2 = get_preferences().Hops_hud_help_color
        color_border = Hops_border_color()
        color_border2 = Hops_border2_color()

        offset = 5

        l1 = (-1, 23, 4, 44)
        l2 = (46, 23, 4, 220)
        l4 = (46, 42, 26, 220)
        vertices = (
            (x + (l1[0] - offset) * factor, y + l1[1] * factor), (x + l1[0] * factor, y + l1[2] * factor), (x + (l1[3] - offset) * factor, y + l1[1] * factor), (x + l1[3] * factor, y + l1[2] * factor),
            (x + (l2[0] - offset) * factor, y + l2[1] * factor), (x + l2[0] * factor, y + l2[2] * factor), (x + (l2[3] - offset) * factor, y + l2[1] * factor), (x + l2[3] * factor, y + l2[2] * factor),
            (x + (l4[0] - offset) * factor, y + l4[1] * factor), (x + l4[0] * factor, y + l4[2] * factor), (x + (l4[3] - offset) * factor, y + l4[1] * factor), (x + l4[3] * factor, y + l4[2] * factor))

        l1 = (l1[0] - 15, l1[1], l1[2], l1[0] - 6)

        vertices2 = (
            (x + (l1[0] - offset) * factor, y + l1[1] * factor), (x + l1[0] * factor, y + l1[2] * factor), (x + (l1[3] - offset) * factor, y + l1[1] * factor), (x + l1[3] * factor, y + l1[2] * factor))

        indices = (
            (0, 1, 2), (1, 2, 3), (4, 5, 6), (5, 6, 7), (8, 9, 10), (9, 10, 11))

        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)

        shader.bind()
        shader.uniform_float("color", get_preferences().Hops_hud_color)
        glEnable(GL_BLEND)
        batch.draw(shader)
        glDisable(GL_BLEND)

        shader2 = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch2 = batch_for_shader(shader2, 'TRIS', {"pos": vertices2}, indices=indices)
        shader2.bind()
        shader2.uniform_float("color", get_preferences().Hops_hud_help_color)

        glEnable(GL_BLEND)
        batch2.draw(shader2)
        glDisable(GL_BLEND)

        red = [1, 0.15, 0.15, 0.9]

        draw_text("{}".format(self.bool_index),
                  x + 25 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        if list(self.bools.keys())[self.bool_index] is not None:
            mod = list(self.bools.keys())[self.bool_index]
            name_color = color_text2
            if not mod.show_viewport and self.additive:
                name_color = red

            if hasattr(mod, "object"):
                draw_text("{}".format(mod.object.name),
                          x + 50 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

            draw_text("{}".format(mod.name),
                      x + 50 * factor, y + 28 * factor, size=12, color=(name_color))

        self.draw_help(context, x, y, factor)

    def draw(self, context):
        x, y = self.start_mouse_position

        set_drawing_dpi(get_dpi())
        factor = get_dpi_factor()
        color_text1 = Hops_text_color()
        color_text2 = get_preferences().Hops_hud_help_color
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

        if self.bool_index >= 10:
            draw_text(str(self.bool_index), x - 8 * factor, y, size=23, color=color_text1)
        else:
            draw_text(str(self.bool_index), x + 3 * factor, y, size=23, color=color_text1)

        if list(self.bools.keys())[self.bool_index] is not None:
            mod = list(self.bools.keys())[self.bool_index]
            name_color = color_text2
            if not mod.show_viewport and self.additive:
                name_color = red

            if hasattr(mod, "object"):
                draw_text("{}".format(mod.object.name),
                          x + 27 * factor, y + 9 * factor, size=12, color=color_text2)

            draw_text("{}".format(mod.name),
                      x + 27 * factor, y - 4 * factor, size=12, color=name_color)

        else:
            draw_text("Off", x + 27 * factor, y - 2 * factor, size=20, color=color_text2)

        if get_preferences().hops_modal_help:
            self.draw_help(context, x, y, factor)

    def draw_help(self, context, x, y, factor):

        color_text2 = get_preferences().Hops_hud_help_color

        if get_preferences().hops_modal_help:

            draw_text(" scroll - change boolean visibility",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)

            draw_text(" a - toggle current visibility",
                      x + 45 * factor, y - 26 * factor, size=11, color=color_text2)

            draw_text(" m - use only booleans / all modifiers",
                      x + 45 * factor, y - 38 * factor, size=11, color=color_text2)

            draw_text(" l - toggle looping",
                      x + 45 * factor, y - 50 * factor, size=11, color=color_text2)

        else:
            draw_text(" H - Show/Hide Help",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)
