import bpy
import gpu
import math
from bgl import *
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from ... utility import modifier
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi
from ... preferences import Hops_text_color, Hops_border_color, Hops_border2_color, get_preferences


class HOPS_OT_MOD_Simple_deform(bpy.types.Operator):
    bl_idname = "hops.mod_simple_deform"
    bl_label = "Adjust Simple Deform Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """LMB - Adjust Deform Modifier
LMB + Ctrl - Add new Deform Modifier
LMB + Ctrl + Shift - Apply Deform Modifiers

Press H for help."""

    deform_objects = {}

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        for obj in selected:
            return getattr(obj, "type", "") == "MESH"

    def invoke(self, context, event):
        self.fisnish = False
        self.stop_position = event.mouse_region_x
        self.modal_scale = get_preferences().Hops_modal_scale
        self.deform_objects = {}

        for object in context.selected_objects:
            self.get_deform_modifier(object, event)

        if self.fisnish:
            return {'FINISHED'}

        self.active_deform_modifier = context.object.modifiers[self.deform_objects[context.object.name]["modifier"]]
        self.store_values()

        self.start_mouse_position = Vector((event.mouse_region_x, event.mouse_region_y))
        self.last_mouse_x = event.mouse_region_x

        self.stop_angle = math.degrees(self.active_deform_modifier.angle)

        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_ui, (context, ), "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}

    def get_deform_modifier(self, object, event):
        if event.ctrl:
            if event.shift:
                modifier.apply(object, type=["SIMPLE_DEFORM"])
                self.fisnish = True
            else:
                self.add_deform_modifier(object)
        else:
            try: self.deform_objects.setdefault(object.name, {})["modifier"] = self.deform_modifiers(object)[-1].name
            except: self.add_deform_modifier(object)

    def add_deform_modifier(self, object):
        deform_modifier = object.modifiers.new(name="SimpleDeform", type="SIMPLE_DEFORM")
        deform_modifier.angle = math.radians(45)
        deform_modifier.deform_method = "TWIST"
        deform_modifier.deform_axis = "X"
        deform_modifier.lock_x = False
        deform_modifier.lock_y = False
        deform_modifier.lock_z = False

        self.deform_objects.setdefault(object.name, {})["modifier"] = deform_modifier.name
        self.deform_objects[object.name]["added_modifier"] = True

    @staticmethod
    def deform_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "SIMPLE_DEFORM"]

    def store_values(self):
        for object_name in self.deform_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.deform_objects[object_name]["modifier"]]
            self.deform_objects[object_name]["show_viewport"] = modifier.show_viewport
            self.deform_objects[object_name]["angle"] = modifier.angle
            self.deform_objects[object_name]["deform_method"] = modifier.deform_method
            self.deform_objects[object_name]["deform_axis"] = modifier.deform_axis
            self.deform_objects[object_name]["lock_x"] = modifier.lock_x
            self.deform_objects[object_name]["lock_y"] = modifier.lock_y
            self.deform_objects[object_name]["lock_z"] = modifier.lock_z

    def modal(self, context, event):
        context.area.header_text_set("Hardops Simple Deform:        X/Y/Z : axis - {}      ctrl+X : Lock x - {}       ctrl+Y : Lock y: {}      ctrl+Z : Lock Z: {}".format(self.active_deform_modifier.deform_axis, self.active_deform_modifier.lock_x, self.active_deform_modifier.lock_y, self.active_deform_modifier.lock_z))

        for object_name in self.deform_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.deform_objects[object_name]["modifier"]]

            segments_offset = self.stop_position - event.mouse_region_x
            if event.ctrl:
                modifier.angle = math.radians(int(self.stop_angle) + int(segments_offset / 60 / get_dpi_factor()) * 15)
            else:
                modifier.angle = math.radians(int(self.stop_angle) + int(segments_offset / 60 / get_dpi_factor()))

            if event.type == "WHEELUPMOUSE" or event.type == "NUMPAD_PLUS" and event.value == "PRESS":
                deform_method_types = ["TWIST", "BEND", "TAPER", "STRETCH"]
                modifier.deform_method = deform_method_types[(deform_method_types.index(modifier.deform_method) + 1) % len(deform_method_types)]
            if event.type == "WHEELDOWNMOUSE" or event.type == "NUMPAD_MINUS" and event.value == "PRESS":
                deform_method_types = ["TWIST", "BEND", "TAPER", "STRETCH"]
                modifier.deform_method = deform_method_types[(deform_method_types.index(modifier.deform_method) - 1) % len(deform_method_types)]

            if event.type == "X" and event.value == "PRESS":
                if event.ctrl:
                    modifier.lock_x = not modifier.lock_x
                else:
                    modifier.deform_axis = "X"
            if event.type == "Y" and event.value == "PRESS":
                if event.ctrl:
                    modifier.lock_y = not modifier.lock_y
                else:
                    modifier.deform_axis = "Y"
            if event.type == "Z" and event.value == "PRESS":
                if event.ctrl:
                    modifier.lock_z = not modifier.lock_z
                else:
                    modifier.deform_axis = "Z"

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
        for object_name in self.deform_objects:
            object = bpy.data.objects[object_name]
            if "added_modifier" in self.deform_objects[object_name]:
                object.modifiers.remove(object.modifiers[self.deform_objects[object_name]["modifier"]])
            else:
                modifier = object.modifiers[self.deform_objects[object_name]["modifier"]]
                modifier.show_viewport = self.deform_objects[object_name]["show_viewport"]
                modifier.angle = self.deform_objects[object_name]["angle"]
                modifier.deform_method = self.deform_objects[object_name]["deform_method"]
                modifier.deform_axis = self.deform_objects[object_name]["deform_axis"]
                modifier.lock_x = self.deform_objects[object_name]["lock_x"]
                modifier.lock_y = self.deform_objects[object_name]["lock_y"]
                modifier.lock_z = self.deform_objects[object_name]["lock_z"]

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
        l2 = (46, 23, 4, 146)
        l3 = (149, 23, 4, 260)

        vertices = (
            (x + (l1[0] - offset) * factor, y + l1[1] * factor), (x + l1[0] * factor, y + l1[2] * factor), (x + (l1[3] - offset) * factor, y + l1[1] * factor), (x + l1[3] * factor, y + l1[2] * factor),
            (x + (l2[0] - offset) * factor, y + l2[1] * factor), (x + l2[0] * factor, y + l2[2] * factor), (x + (l2[3] - offset) * factor, y + l2[1] * factor), (x + l2[3] * factor, y + l2[2] * factor),
            (x + (l3[0] - offset) * factor, y + l3[1] * factor), (x + l3[0] * factor, y + l3[2] * factor), (x + (l3[3] - offset) * factor, y + l3[1] * factor), (x + l3[3] * factor, y + l3[2] * factor))

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

        draw_text("{}".format(self.active_deform_modifier.deform_axis),
                  x + 27 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text("Angle: {:.3f}".format(math.degrees(self.active_deform_modifier.angle)),
                  x + 50 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text("Method: {}".format(self.active_deform_modifier.deform_method),
                  x + 154 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        self.draw_help(context, x, y, factor)

    def draw_help(self, context, x, y, factor):

        # color_text1 = Hops_text_color()
        color_text2 = get_preferences().Hops_hud_help_color
        # color_border = Hops_border_color()
        # color_border2 = Hops_border2_color()

        if get_preferences().hops_modal_help:

            draw_text(" scroll - set deform method",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)

            draw_text(" ctrl - snap to 5*",
                      x + 45 * factor, y - 26 * factor, size=11, color=color_text2)

            draw_text(" X - set axis/ ctrl - lock axis",
                      x + 45 * factor, y - 38 * factor, size=11, color=color_text2)

            draw_text(" Y - set axis/ ctrl - lock axis",
                      x + 45 * factor, y - 50 * factor, size=11, color=color_text2)

            draw_text(" Z - set axis/ ctrl - lock axis",
                      x + 45 * factor, y - 62 * factor, size=11, color=color_text2)

            draw_text(" H - Show/Hide Help",
                      x + 45 * factor, y - 74 * factor, size=11, color=color_text2)

        else:
            draw_text(" H - Show/Hide Help",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)
