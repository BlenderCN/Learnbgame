import bpy
import gpu
from bgl import *
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi, draw_box
from ... preferences import Hops_text_color, Hops_text2_color, Hops_border_color, Hops_border2_color, get_preferences


class HOPS_OT_TwoDBevelOperator(bpy.types.Operator):
    bl_idname = "hops.2d_bevel"
    bl_label = "2 Dimensional Bevel"
    bl_description = """Interactively and non destructively adds BEVEL modifier to single flat FACES
Press H for help"""
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def invoke(self, context, event):
        self.modal_scale = get_preferences().Hops_modal_scale
        self.object = context.active_object
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.view3d.clean_mesh()
        self.bevel = self.get_bevel_modifier()
        self.start_mouse_position = Vector((event.mouse_region_x, event.mouse_region_y))
        self.start_bevel_width = self.bevel.width
        self.start_bevel_profile = self.bevel.profile
        self.start_bevel_segments = self.bevel.segments
        self.bevel_offset = 0
        self.profile_offset = 0
        self.last_mouse_x = event.mouse_region_x

        args = (context, )
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_ui, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def get_bevel_modifier(self):
        object = bpy.context.active_object
        bevel_modifier = None
        for modifier in object.modifiers:
            if modifier.type == "BEVEL":
                bevel_modifier = modifier
                self.created_bevel_modifier = False
        if bevel_modifier is None:
            bevel_modifier = object.modifiers.new("Bevel", "BEVEL")
            bevel_modifier.limit_method = "NONE"
            bevel_modifier.width = 0.200
            bevel_modifier.profile = 0.70
            bevel_modifier.segments = 6
            bevel_modifier.use_only_vertices = True
            bevel_modifier.use_clamp_overlap = False
            self.created_bevel_modifier = True
        return bevel_modifier

    def modal(self, context, event):
        divisor = 10000 * self.modal_scale if event.shift else 10000000 if event.ctrl else 1000 * self.modal_scale
        divisor_profile = 500 * self.modal_scale if event.ctrl else 100000000000
        offset_x = event.mouse_region_x - self.last_mouse_x
        self.bevel_offset += offset_x / divisor / get_dpi_factor()
        self.bevel.width = self.start_bevel_width - self.bevel_offset
        self.profile_offset += offset_x / divisor_profile / get_dpi_factor()

        if event.ctrl:
            self.bevel.profile = self.start_bevel_profile - self.profile_offset

        if event.type == "WHEELUPMOUSE" or event.type == 'NUMPAD_PLUS' and event.value == 'PRESS':
            self.bevel.segments += 1
        if event.type == "WHEELDOWNMOUSE" or event.type == 'NUMPAD_MINUS' and event.value == 'PRESS':
            self.bevel.segments -= 1

        if event.type == "H" and event.value == "PRESS":
            get_preferences().hops_modal_help = not get_preferences().hops_modal_help

        if event.type in ("ESC", "RIGHTMOUSE"):
            self.reset_object()
            return self.finish()

        if event.type in ("SPACE", "LEFTMOUSE"):
            return self.finish()

        if event.type == 'W' and event.value == 'PRESS':
            offset_types = ["OFFSET", "WIDTH", "DEPTH", "PERCENT"]
            modifier.offset_type = offset_types[(offset_types.index(modifier.offset_type) + 1) % len(offset_types)]

        self.last_mouse_x = event.mouse_region_x
        context.area.tag_redraw()
        return {"RUNNING_MODAL"}

    def reset_object(self):
        self.bevel.width = self.start_bevel_width
        self.bevel.segments = self.start_bevel_segments
        self.bevel.profile = self.start_bevel_profile
        if self.created_bevel_modifier:
            self.object.modifiers.remove(self.bevel)

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

        l1 = (3, 23, 4, 44)
        l2 = (46, 23, 4, 146)
        l3 = (149, 23, 4, 220)
        l4 = (223, 23, 4, 280)
        vertices = (
            (x + (l1[0] - offset) * factor, y + l1[1] * factor), (x + l1[0] * factor, y + l1[2] * factor), (x + (l1[3] - offset) * factor, y + l1[1] * factor), (x + l1[3] * factor, y + l1[2] * factor),
            (x + (l2[0] - offset) * factor, y + l2[1] * factor), (x + l2[0] * factor, y + l2[2] * factor), (x + (l2[3] - offset) * factor, y + l2[1] * factor), (x + l2[3] * factor, y + l2[2] * factor),
            (x + (l3[0] - offset) * factor, y + l3[1] * factor), (x + l3[0] * factor, y + l3[2] * factor), (x + (l3[3] - offset) * factor, y + l3[1] * factor), (x + l3[3] * factor, y + l3[2] * factor),
            (x + (l4[0] - offset) * factor, y + l4[1] * factor), (x + l4[0] * factor, y + l4[2] * factor), (x + (l4[3] - offset) * factor, y + l4[1] * factor), (x + l4[3] * factor, y + l4[2] * factor))

        l1 = (l1[0] - 15, l1[1], l1[2], l1[0] - 6)
        vertices2 = (
            (x + (l1[0] - offset) * factor, y + l1[1] * factor), (x + l1[0] * factor, y + l1[2] * factor), (x + (l1[3] - offset) * factor, y + l1[1] * factor), (x + l1[3] * factor, y + l1[2] * factor))

        indices = (
            (0, 1, 2), (1, 2, 3), (4, 5, 6), (5, 6, 7), (8, 9, 10), (9, 10, 11), (12, 13, 14), (13, 14, 15))

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

        draw_text("{}".format(self.bevel.segments),
                  x + 27 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text(" B-Width: {:.3f}".format(self.bevel.width),
                  x + 50 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text("Profile:{:.2f}".format(self.bevel.profile),
                  x + 154 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text("{}".format(self.bevel.offset_type),
                  x + 227 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        self.draw_help(context, x, y, factor)

    def draw(self, context):
        x, y = self.start_mouse_position
        bevel = self.bevel

        set_drawing_dpi(get_dpi())
        factor = get_dpi_factor()
        color_text1 = Hops_text_color()
        color_text2 = get_preferences().Hops_hud_help_color
        color_border = Hops_border_color()
        color_border2 = Hops_border2_color()

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

        if bevel.segments >= 10:
            draw_text(str(bevel.segments), x - 8 * factor, y, size=23, color=color_text1)
        else:
            draw_text(str(bevel.segments), x + 3 * factor, y, size=23, color=color_text1)

        draw_text("2d Bevel - {:.3f} // (W) - {}".format(bevel.width, bevel.offset_type),
                  x + 27 * factor, y + 9 * factor, size=12, color=color_text2)

        draw_text("Profile- {:.2f} ".format(bevel.profile),
                  x + 27 * factor, y - 4 * factor, size=12, color=color_text2)

        # this never worked anyway, do we need it ?
        '''draw_text(self.get_description_text(), x + 24 * factor, y - 28 * factor,
                                          size = 12, color = color)'''
        if get_preferences().hops_modal_help:
            self.draw_help(context, x, y, factor)

    def draw_help(self, context, x, y, factor):

        color_text1 = Hops_text_color()
        color_text2 = get_preferences().Hops_hud_help_color
        color_border = Hops_border_color()
        color_border2 = Hops_border2_color()

        if get_preferences().hops_modal_help:

            draw_text(" scroll - set segment",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)

            draw_text(" ctrl - set profile",
                      x + 45 * factor, y - 26 * factor, size=11, color=color_text2)

            draw_text(" W - choose offset type",
                      x + 45 * factor, y - 38 * factor, size=11, color=color_text2)

        else:
            draw_text(" H - Show/Hide Help",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)
