import bpy
import gpu
from bgl import *
from gpu_extras.batch import batch_for_shader
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi, draw_box
from ... preferences import Hops_text_color, Hops_text2_color, Hops_border_color, Hops_border2_color, get_preferences


class HOPS_OT_ModifierScroll(Operator):
    bl_idname = "hops.modifier_scroll"
    bl_label = "Scroll Modifiers"
    bl_description = "Use the scroll wheel to scroll through modifiers on the selected object"

    running: bool = False

    all: BoolProperty()
    type: StringProperty(default='BOOLEAN')
    additive : BoolProperty()


    def modal(self, context, event):

        self.mouse = [event.mouse_region_x, event.mouse_region_y]

        current_bool = None

        if event.type == "WHEELUPMOUSE" or event.type == "NUMPAD_PLUS" and event.value == "PRESS":
            self.index += 1

        if event.type == "WHEELDOWNMOUSE" or event.type == "NUMPAD_MINUS" and event.value == "PRESS":
            self.index -= 1

        if self.loop:
            if self.index >= len(self.mods):
                self.index = 0
            if self.index < 0:
                self.index = len(self.mods) - 1

        else:
            self.index = max(min(self.index, len(self.mods) - 1), 0)

        if event.type == 'L' and event.value == 'PRESS':
            self.loop = not self.loop

        if event.type == 'A' and event.value == 'RELEASE':
            if self.mods[list(self.mods.keys())[self.index]] is not None:
                # if list(self.mods.keys())[self.index] is not None:
                override_value = self.mods[list(self.mods.keys())[self.index]]["override"]
                self.mods[list(self.mods.keys())[self.index]]["override"] = not override_value

        self.original_obj.select_set(True)
        context.view_layer.objects.active = self.original_obj

        if event.type == 'M' and event.value == 'PRESS':
            self.all_mods = not self.all_mods
            self.mods = {None: None}
            self.index = 0

            for mod in self.mods:
                if mod is not None:
                    mod.show_viewport = self.mods[mod]["original_show_viewport"]

            for mod in context.object.modifiers:
                if self.all_mods:
                    self.mods.update({mod: {"original_show_viewport": mod.show_viewport, "override": False}})

        if self.additive or event.shift:
            for count, mod in enumerate(self.mods):
                if mod is not None:
                    if count <= self.index:
                        mod.show_viewport = True
                    else:
                        mod.show_viewport = False
                    if self.mods[mod]["override"] or self.mods[list(self.mods.keys())[self.index]] is None:
                        mod.show_viewport = False

        else:
            for mod in self.mods:
                if mod is not None and hasattr(mod, "object"):
                    mod.show_viewport = self.mods[mod]["override"]  # hide all mods except for those pressed A on.
                    if not self.all or self.type == 'BOOLEAN':
                        mod.object.select_set(False)

                        mod.object.hide_viewport = True

                    if mod.show_viewport:  # show and select objects that have modifier being shown in viewport.
                        mod.object.hide_viewport = False

                        if not self.all or self.type == 'BOOLEAN':
                            mod.object.select_set(True)

            if self.mods[list(self.mods.keys())[self.index]] is not None:
                current_bool = list(self.mods.keys())[self.index]
                current_bool.show_viewport = True  # show viewport on the current mod.
                if hasattr(current_bool, "object"):

                    current_bool.object.hide_viewport = False

                    current_bool.object.select_set(True)

        if event.type == "H" and event.value == "PRESS":
            get_preferences().hops_modal_help = not get_preferences().hops_modal_help

        if event.type in {'LEFTMOUSE', 'RET', 'NUMPAD_ENTER'}:
            self.finish()
            for mod in self.mods:
                if mod is not None and hasattr(mod, "object"):
                    if not mod.show_viewport:
                        if not self.all or self.type == 'BOOLEAN':
                            mod.object.hide_viewport = True

                    elif not self.all or self.type == 'BOOLEAN':
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
            for mod in self.mods:
                if mod is not None:
                    mod.show_viewport = self.mods[mod]["original_show_viewport"]
            return {'CANCELLED'}

        context.area.tag_redraw()
        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        self.running = True

        self.mouse = [event.mouse_region_x, event.mouse_region_y]

        if event.shift:
            self.all = True

        if not self.all:
            self.modifiers = [mod for mod in context.active_object.modifiers if mod.type == self.type]
        else:
            self.modifiers = [mod for mod in context.active_object.modifiers]

        self.mods = {None: None}
        self.index = 0
        self.all_mods = False
        self.loop = False
        self.original_obj = context.active_object

        for mod in self.modifiers:
            if self.type == 'BOOLEAN' and not self.all and mod.show_render:
                self.mods.update({
                    mod: {
                        "original_show_viewport": mod.show_viewport,
                        "override": False,
                        "hide": mod.object.hide_viewport}})
            elif mod.show_render:
                self.mods.update({
                    mod: {
                        "original_show_viewport": mod.show_viewport,
                        "override": False,
                        "hide": False}})

        if len(self.mods) == 1:
            return {'CANCELLED'}

        args = (context, )
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_ui, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


    def finish(self):
        self.running = False
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
        return {"FINISHED"}


    def draw_ui(self, context):
        if self.running:
            x, y = self.mouse
            object = context.active_object

            set_drawing_dpi(get_dpi())
            factor = get_dpi_factor()

            color_text1 = Hops_text_color()
            color_text2 = get_preferences().Hops_hud_help_color
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
            shader.uniform_float("color", get_preferences().Hops_hud_color)
            glEnable(GL_BLEND)
            batch.draw(shader)
            glDisable(GL_BLEND)
            red = [1, 0.15, 0.15, 0.9]

            draw_text("{}".format(self.index),
                      x + 25 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)


            if list(self.mods.keys())[self.index] is not None:
                mod = list(self.mods.keys())[self.index]
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
        if self.running:
            x, y = self.mouse

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

            if self.index >= 10:
                draw_text(str(self.index), x - 8 * factor, y, size=23, color=color_text1)
            else:
                draw_text(str(self.index), x + 3 * factor, y, size=23, color=color_text1)

            if list(self.mods.keys())[self.index] is not None:
                mod = list(self.mods.keys())[self.index]
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
        if self.running:
            color_text2 = get_preferences().Hops_hud_help_color

            if get_preferences().hops_modal_help:

                draw_text(" Scroll - change boolean visibility",
                          x + 45 * factor, y - 14 * factor, size=11, color=color_text2)

                draw_text(" A - toggle current visibility",
                          x + 45 * factor, y - 26 * factor, size=11, color=color_text2)

                draw_text(" M - use only booleans / all modifiers",
                          x + 45 * factor, y - 38 * factor, size=11, color=color_text2)

                draw_text(" L - toggle looping",
                          x + 45 * factor, y - 50 * factor, size=11, color=color_text2)

            else:
                draw_text(" H - Show/Hide Help",
                          x + 45 * factor, y - 14 * factor, size=11, color=color_text2)
