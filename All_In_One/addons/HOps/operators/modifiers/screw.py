import bpy
import gpu
import math
from bgl import *
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi
from ... preferences import Hops_text_color, Hops_border_color, Hops_border2_color, get_preferences


class HOPS_OT_MOD_Screw(bpy.types.Operator):
    bl_idname = "hops.mod_screw"
    bl_label = "Adjust Screw Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """LMB - Adjust Screw Modifier
LMB + CTRL - Add New Screw Modifier

Press H for help."""

    screw_objects = {}

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        for obj in selected:
            return getattr(obj, "type", "") == "MESH"

    def invoke(self, context, event):
        self.segments_mode = False
        self.stop_position = event.mouse_region_x
        self.angle_mode = False
        self.screw_mode = True
        self.iterations_mode = False
        self.modal_scale = get_preferences().Hops_modal_scale
        self.screw_objects = {}

        for object in context.selected_objects:
            self.get_deform_modifier(object, event)

        self.active_screw_modifier = context.object.modifiers[self.screw_objects[context.object.name]["modifier"]]
        self.store_values()

        self.start_mouse_position = Vector((event.mouse_region_x, event.mouse_region_y))
        self.last_mouse_x = event.mouse_region_x

        self.stop_screw = self.active_screw_modifier.screw_offset

        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_ui, (context, ), "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}

    def get_deform_modifier(self, object, event):
        if event.ctrl:
            self.add_deform_modifier(object)
        else:
            try: self.screw_objects.setdefault(object.name, {})["modifier"] = self.screw_modifiers(object)[-1].name
            except: self.add_deform_modifier(object)

    def add_deform_modifier(self, object):
        screw_modifier = object.modifiers.new(name="screw", type="SCREW")
        screw_modifier.angle = math.radians(360)
        screw_modifier.axis = 'Y'
        screw_modifier.steps = 36
        screw_modifier.render_steps = 36
        screw_modifier.screw_offset = 0
        screw_modifier.iterations = 1
        screw_modifier.use_smooth_shade = True
        screw_modifier.use_merge_vertices = True

        self.screw_objects.setdefault(object.name, {})["modifier"] = screw_modifier.name
        self.screw_objects[object.name]["added_modifier"] = True

    @staticmethod
    def screw_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "SCREW"]

    def store_values(self):
        for object_name in self.screw_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.screw_objects[object_name]["modifier"]]
            self.screw_objects[object_name]["show_viewport"] = modifier.show_viewport
            self.screw_objects[object_name]["axis"] = modifier.axis
            self.screw_objects[object_name]["steps"] = modifier.steps
            self.screw_objects[object_name]["render_steps"] = modifier.render_steps
            self.screw_objects[object_name]["angle"] = modifier.angle
            self.screw_objects[object_name]["screw_offset"] = modifier.screw_offset
            self.screw_objects[object_name]["iterations"] = modifier.iterations
            self.screw_objects[object_name]["use_normal_flip"] = modifier.use_normal_flip
            self.screw_objects[object_name]["use_normal_calculate"] = modifier.use_normal_calculate
            self.screw_objects[object_name]["use_merge_vertices"] = modifier.use_merge_vertices
            self.screw_objects[object_name]["use_smooth_shade"] = modifier.use_smooth_shade

    def modal(self, context, event):
        context.area.header_text_set("Hardops Screw:     N : Smooth - {}     M : Merge - {}     X/Y/Z : AxiS - {}     F : Flip - {}      C : Calculate - {}".format(self.active_screw_modifier.use_smooth_shade, self.active_screw_modifier.use_merge_vertices, self.active_screw_modifier.axis, self.active_screw_modifier.use_normal_flip, self.active_screw_modifier.use_normal_calculate))

        for object_name in self.screw_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.screw_objects[object_name]["modifier"]]

            if self.angle_mode:
                angle_offset = self.stop_position - event.mouse_region_x
                if event.shift:
                    modifier.angle = math.radians(int(self.stop_angle) + int(angle_offset / 60 / get_dpi_factor()))
                elif event.ctrl:
                    modifier.angle = math.radians(int(self.stop_angle) + int(angle_offset / 60 / get_dpi_factor()) * 5)
                else:
                    modifier.angle = math.radians(int(self.stop_angle) + int(angle_offset / 60 / get_dpi_factor()) * 45)

            if self.iterations_mode:
                iterations_offset = self.stop_position - event.mouse_region_x
                modifier.iterations = int(self.stop_iterations) + int(iterations_offset / 60 / get_dpi_factor())

            if self.screw_mode:
                screw_offset = self.stop_position - event.mouse_region_x
                modifier.screw_offset = int(self.stop_screw) + int(screw_offset / 60 / get_dpi_factor())

            if self.segments_mode:
                segments_offset = self.stop_position - event.mouse_region_x
                modifier.steps = int(self.stop_segments) + int(segments_offset / 60 / get_dpi_factor())

            if event.type == "ONE" and event.value == "PRESS":
                modifier.angle = math.radians(360)
                modifier.steps = 12
                modifier.render_steps = 12
                modifier.screw_offset = 0
                modifier.use_merge_vertices = True
                modifier.use_smooth_shade = True
                modifier.use_normal_calculate = True

            if event.type == "TWO" and event.value == "PRESS":
                modifier.angle = math.radians(360)
                modifier.steps = 36
                modifier.render_steps = 36
                modifier.screw_offset = 0
                modifier.use_merge_vertices = True
                modifier.use_smooth_shade = True
                modifier.use_normal_calculate = False

            if event.type == "THREE" and event.value == "PRESS":
                modifier.angle = math.radians(0)
                modifier.steps = 2
                modifier.render_steps = 2
                modifier.screw_offset = 2.3
                modifier.use_merge_vertices = True
                modifier.use_smooth_shade = True
                modifier.use_normal_calculate = False
                modifier.axis = 'Z'

            if event.type == "A" and event.value == "PRESS":
                self.stop_position = event.mouse_region_x
                self.stop_angle = math.degrees(modifier.angle)
                self.stop_screw = modifier.screw_offset
                if self.iterations_mode:
                    self.iterations_mode = False
                if self.screw_mode:
                    self.screw_mode = False
                if self.segments_mode:
                    self.segments_mode = False
                if self.angle_mode:
                    self.screw_mode = True
                self.angle_mode = not self.angle_mode

            if event.type == "E" and event.value == "PRESS":
                self.stop_position = event.mouse_region_x
                self.stop_iterations = modifier.iterations
                self.stop_screw = modifier.screw_offset
                if self.screw_mode:
                    self.screw_mode = False
                if self.segments_mode:
                    self.segments_mode = False
                if self.angle_mode:
                    self.angle_mode = False
                if self.iterations_mode:
                    self.screw_mode = True
                self.iterations_mode = not self.iterations_mode

            if event.type == "S" and event.value == "PRESS":
                self.stop_position = event.mouse_region_x
                self.stop_segments = modifier.steps
                self.stop_screw = modifier.screw_offset
                if self.screw_mode:
                    self.screw_mode = False
                if self.iterations_mode:
                    self.iterations_mode = False
                if self.angle_mode:
                    self.angle_mode = False
                if self.segments_mode:
                    self.screw_mode = True
                self.segments_mode = not self.segments_mode

            if event.type == "WHEELUPMOUSE" or event.type == "NUMPAD_PLUS" and event.value == "PRESS":
                modifier.iterations += 1
            if event.type == "WHEELDOWNMOUSE" or event.type == "NUMPAD_MINUS" and event.value == "PRESS":
                modifier.iterations -= 1

            if event.type == "F" and event.value == "PRESS":
                modifier.use_normal_flip = not modifier.use_normal_flip

            if event.type == "X" and event.value == "PRESS":
                modifier.axis = "X"

            if event.type == "Y" and event.value == "PRESS":
                modifier.axis = "Y"

            if event.type == "Z" and event.value == "PRESS":
                modifier.axis = "Z"

            if event.type == "M" and event.value == "PRESS":
                modifier.use_merge_vertices = not modifier.use_merge_vertices

            if event.type == "C" and event.value == "PRESS":
                modifier.use_normal_calculate = not modifier.use_normal_calculate

            if event.type == "N" and event.value == "PRESS":
                modifier.use_smooth_shade = not modifier.use_smooth_shade

            if event.type == "H" and event.value == "PRESS":
                bpy.context.space_data.show_gizmo_navigate = True
                get_preferences().hops_modal_help = not get_preferences().hops_modal_help

            if event.type in ("ESC", "RIGHTMOUSE"):
                self.restore()
                context.area.header_text_set(text=None)
                bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
                return {'CANCELLED'}
            if event.type in ("SPACE", "LEFTMOUSE"):
                context.area.header_text_set(text=None)
                bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
                return {'FINISHED'}

        self.last_mouse_x = event.mouse_region_x
        return {'RUNNING_MODAL'}

    def restore(self):
        for object_name in self.screw_objects:
            object = bpy.data.objects[object_name]
            if "added_modifier" in self.screw_objects[object_name]:
                object.modifiers.remove(object.modifiers[self.screw_objects[object_name]["modifier"]])
            else:
                modifier = object.modifiers[self.screw_objects[object_name]["modifier"]]
                modifier.show_viewport = self.screw_objects[object_name]["show_viewport"]
                modifier.axis = self.screw_objects[object_name]["axis"]
                modifier.steps = self.screw_objects[object_name]["steps"]
                modifier.render_steps = self.screw_objects[object_name]["render_steps"]
                modifier.angle = self.screw_objects[object_name]["angle"]
                modifier.screw_offset = self.screw_objects[object_name]["screw_offset"]
                modifier.iterations = self.screw_objects[object_name]["iterations"]
                modifier.use_normal_flip = self.screw_objects[object_name]["use_normal_flip"]
                modifier.use_normal_calculate = self.screw_objects[object_name]["use_normal_calculate"]
                modifier.use_merge_vertices = self.screw_objects[object_name]["use_merge_vertices"]
                modifier.use_smooth_shade = self.screw_objects[object_name]["use_smooth_shade"]

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

        l1 = (-1, 23, 4, 86)
        l2 = (88, 23, 4, 182)
        l3 = (184, 23, 4, 260)
        l4 = (262, 23, 4, 310)
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

        draw_text("Steps: {}".format(self.active_screw_modifier.steps),
                  x + 15 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text("Angle: {:.1f}".format(math.degrees(self.active_screw_modifier.angle)),
                  x + 100 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text("Screw: {}".format(self.active_screw_modifier.screw_offset),
                  x + 190 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text("It: {}".format(self.active_screw_modifier.iterations),
                  x + 270 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        self.draw_help(context, x, y, factor)

    def draw_help(self, context, x, y, factor):

        # color_text1 = Hops_text_color()
        color_text2 = get_preferences().Hops_hud_help_color
        # color_border = Hops_border_color()
        # color_border2 = Hops_border2_color()

        if get_preferences().hops_modal_help:

            draw_text(" move - steps",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)

            draw_text(" A - angle",
                      x + 45 * factor, y - 26 * factor, size=11, color=color_text2)

            draw_text(" S - Steps",
                      x + 45 * factor, y - 38 * factor, size=11, color=color_text2)

            draw_text(" E - iterations",
                      x + 45 * factor, y - 50 * factor, size=11, color=color_text2)

            draw_text(" F - use_normal_flip",
                      x + 45 * factor, y - 62 * factor, size=11, color=color_text2)

            draw_text(" C - use_normal_calculate",
                      x + 45 * factor, y - 74 * factor, size=11, color=color_text2)

            draw_text(" WHEEL - change axis",
                      x + 45 * factor, y - 86 * factor, size=11, color=color_text2)

            draw_text(" M - Merge vertices",
                      x + 45 * factor, y - 98 * factor, size=11, color=color_text2)

            draw_text(" N - smooth shading",
                      x + 45 * factor, y - 122 * factor, size=11, color=color_text2)

            draw_text(" 1 - preset 1",
                      x + 45 * factor, y - 134 * factor, size=11, color=color_text2)

            draw_text(" 2 - preset 2",
                      x + 45 * factor, y - 146 * factor, size=11, color=color_text2)

            draw_text(" 3 - preset 3",
                      x + 45 * factor, y - 158 * factor, size=11, color=color_text2)

            draw_text(" H - Show/Hide Help",
                      x + 45 * factor, y - 170 * factor, size=11, color=color_text2)

        else:
            draw_text(" H - Show/Hide Help",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)
