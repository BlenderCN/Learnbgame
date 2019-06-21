import bpy
import gpu
from bgl import *
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from bpy.props import IntProperty, FloatProperty
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi, draw_box
from ... preferences import Hops_text_color, Hops_text2_color, Hops_border_color, Hops_border2_color, get_preferences


class HOPS_OT_AdjustCurveOperator(bpy.types.Operator):
    bl_idname = "hops.adjust_curve"
    bl_label = "Adjust Curve"
    bl_description = "Interactive Curve adjustment. 1/2/3 provides presets for curves"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}

    first_mouse_x: IntProperty()
    first_value: FloatProperty()
    second_value: IntProperty()

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "CURVE"

    def modal(self, context, event):

        bpy.context.object.show_wire = True

        divisor = 10000 * self.modal_scale if event.shift else 10000000 if event.ctrl else 1000 * self.modal_scale
        offset_x = event.mouse_region_x - self.last_mouse_x

        self.depth_offset += offset_x / divisor / get_dpi_factor()
        context.object.data.bevel_depth = self.start_depth_offset - self.depth_offset

        if event.ctrl:
            if event.type == "WHEELUPMOUSE" or event.type == 'NUMPAD_PLUS' and event.value == 'PRESS':
                context.object.data.resolution_u += 1
                context.object.data.render_resolution_u += 1

            if event.type == "WHEELDOWNMOUSE" or event.type == 'NUMPAD_MINUS' and event.value == 'PRESS':
                context.object.data.resolution_u -= 1
                context.object.data.render_resolution_u -= 1

        else:
            if event.type == "WHEELUPMOUSE" or event.type == 'NUMPAD_PLUS' and event.value == 'PRESS':
                context.object.data.bevel_resolution += 1

            if event.type == "WHEELDOWNMOUSE" or event.type == 'NUMPAD_MINUS' and event.value == 'PRESS':
                context.object.data.bevel_resolution -= 1

        if event.type == 'S' and event.value == 'PRESS':
            bpy.ops.object.shade_smooth()

        if event.type == 'ONE' and event.value == 'PRESS':
            bpy.context.object.data.resolution_u = 6
            bpy.context.object.data.render_resolution_u = 12
            bpy.context.object.data.bevel_resolution = 6
            bpy.context.object.data.fill_mode = 'FULL'

        if event.type == 'TWO' and event.value == 'PRESS':
            bpy.context.object.data.resolution_u = 64
            bpy.context.object.data.render_resolution_u = 64
            bpy.context.object.data.bevel_resolution = 16
            bpy.context.object.data.fill_mode = 'FULL'

        if event.type == "H" and event.value == "PRESS":
            get_preferences().hops_modal_help = not get_preferences().hops_modal_help

        if event.type == 'LEFTMOUSE':
            return self.finish()

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.reset_object()
            bpy.context.object.show_wire = False
            context.object.data.fill_mode = 'HALF'
            context.object.data.bevel_depth = 0
            return self.finish()

        self.last_mouse_x = event.mouse_region_x
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def reset_object(self):
        self.depth_offset = self.start_depth_offset

    def invoke(self, context, event):
        self.modal_scale = get_preferences().Hops_modal_scale
        self.start_depth_offset = context.object.data.bevel_depth
        self.last_mouse_x = event.mouse_region_x
        self.depth_offset = 0
        self.profile_offset = 0

        if context.object:
            context.object.data.fill_mode = 'FULL'
            self.start_mouse_position = Vector((event.mouse_region_x, event.mouse_region_y))
            self.curve = bpy.ops

            self.first_mouse_x = event.mouse_x
            self.first_value = context.object.data.bevel_depth

            args = (context, )
            self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_ui, args, "WINDOW", "POST_PIXEL")
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}

    # def reset_object(self):
        # self.bevel.width = self.start_bevel_width
        # self.bevel.segments = self.start_bevel_segments
        # self.bevel.profile = self.start_bevel_profile
        # if self.created_bevel_modifier:
        #    self.object.modifiers.remove(self.bevel)
        # self.curve = bpy.context
        # self.curve.object.data.bevel_depth = 0
        # self.curve.object.data.resolution_u = 6
        # self.curve.object.data.render_resolution_u = 12
        # self.curve.object.data.bevel_resolution = 6
        # self.curve.object.data.fill_mode = 'FULL'

    def finish(self):
        bpy.context.object.show_wire = False
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

        l1 = (-1, 23, 4, 72)
        l2 = (75, 23, 4, 197)
        l3 = (200, 23, 4, 270)
        vertices = (
            (x + (l1[0] - offset) * factor, y + l1[1] * factor), (x + l1[0] * factor, y + l1[2] * factor), (x + (l1[3] - offset) * factor, y + l1[1] * factor), (x + l1[3] * factor, y + l1[2] * factor),
            (x + (l2[0] - offset) * factor, y + l2[1] * factor), (x + l2[0] * factor, y + l2[2] * factor), (x + (l2[3] - offset) * factor, y + l2[1] * factor), (x + l2[3] * factor, y + l2[2] * factor),
            (x + (l3[0] - offset) * factor, y + l3[1] * factor), (x + l3[0] * factor, y + l3[2] * factor), (x + (l3[3] - offset) * factor, y + l3[1] * factor), (x + l3[3] * factor, y + l3[2] * factor))
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

        draw_text("{:.3f}".format(context.object.data.bevel_depth),
                  x + 27 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text("Segments (ctrl) - {:.0f}".format(context.object.data.render_resolution_u),
                  x + 85 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text("Profile:{:.0f}".format(context.object.data.bevel_resolution),
                  x + 210 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        self.draw_help(context, x, y, factor)

    def draw(self, context):
        x, y = self.start_mouse_position

        set_drawing_dpi(get_dpi())
        factor = get_dpi_factor()
        color_text1 = Hops_text_color()
        color_text2 = get_preferences().Hops_hud_help_color
        color_border = Hops_border_color()
        color_border2 = Hops_border2_color()

        # front
        draw_box(x - 14 * factor, y + 8 * factor, 82 * factor, 34 * factor, color=color_border2)
        # back
        draw_box(x + 208 * factor, y + 8 * factor, 2 * factor, 34 * factor, color=color_border2)
        # top
        draw_box(x + 68 * factor, y + 24 * factor, 140 * factor, 2 * factor, color=color_border2)
        # bot
        draw_box(x + 68 * factor, y - 8 * factor, 140 * factor, 2 * factor, color=color_border2)
        # middle
        # raw_box(x -14 * factor, y + 8 * factor, 224 * factor, 34* factor, color=color_border2)
        draw_box(x + 68 * factor, y + 8 * factor, 140 * factor, 30 * factor, color=color_border)

        draw_text("{:.3f}".format(context.object.data.bevel_depth), x - 12 * factor, y, size=23, color=color_text1)

        draw_text("Segments (ctrl) -  {:.0f}".format(context.object.data.render_resolution_u),
                  x + 70 * factor, y + 11 * factor, size=12, color=color_text2)

        draw_text("Resolution          -  {:.0f}".format(context.object.data.bevel_resolution),
                  x + 70 * factor, y - 4 * factor, size=12, color=color_text2)

        if get_preferences().hops_modal_help:
            self.draw_help(context, x, y, factor)

    def draw_help(self, context, x, y, factor):

        # color_text1 = Hops_text_color()
        color_text2 = get_preferences().Hops_hud_help_color
        # color_border = Hops_border_color()
        # color_border2 = Hops_border2_color()

        if get_preferences().hops_modal_help:

            draw_text(" scroll - set resolution",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)

            draw_text(" ctrl + scroll - set segments",
                      x + 45 * factor, y - 26 * factor, size=11, color=color_text2)

            draw_text(" S - set smooth shading",
                      x + 45 * factor, y - 38 * factor, size=11, color=color_text2)

            draw_text(" 1 - set profile 12 x 6",
                      x + 45 * factor, y - 50 * factor, size=11, color=color_text2)

            draw_text(" 2 - set profile 64 x 16",
                      x + 45 * factor, y - 62 * factor, size=11, color=color_text2)

        else:
            draw_text(" H - Show/Hide Help",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)
