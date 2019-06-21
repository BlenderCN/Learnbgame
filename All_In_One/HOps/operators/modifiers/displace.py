import bpy
import gpu
import math
from bgl import *
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi
from ... preferences import Hops_text_color, Hops_border_color, Hops_border2_color, get_preferences


class HOPS_OT_MOD_Displace(bpy.types.Operator):
    bl_idname = "hops.mod_displace"
    bl_label = "Adjust Displace Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """LMB - Adjust Displace Modifier
LMB + CTRL - Add new Displace Modifier

Press H for help."""

    displace_objects = {}

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        for obj in selected:
            return getattr(obj, "type", "") == "MESH"

    def invoke(self, context, event):
        self.modal_scale = get_preferences().Hops_modal_scale
        self.displace_objects = {}

        for object in context.selected_objects:
            self.get_deform_modifier(object, event)

        self.active_displace_modifier = context.object.modifiers[self.displace_objects[context.object.name]["modifier"]]
        self.store_values()

        self.start_mouse_position = Vector((event.mouse_region_x, event.mouse_region_y))
        self.last_mouse_x = event.mouse_region_x

        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_ui, (context, ), "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}

    def get_deform_modifier(self, object, event):
        if event.ctrl:
            self.add_deform_modifier(object)
        else:
            try: self.displace_objects.setdefault(object.name, {})["modifier"] = self.displace_modifiers(object)[-1].name
            except: self.add_deform_modifier(object)

    def add_deform_modifier(self, object):
        displace_modifier = object.modifiers.new(name="Displace", type="DISPLACE")
        displace_modifier.direction = "X"
        displace_modifier.space = "LOCAL"
        displace_modifier.mid_level = 0
        displace_modifier.strength = 0

        self.displace_objects.setdefault(object.name, {})["modifier"] = displace_modifier.name
        self.displace_objects[object.name]["added_modifier"] = True

    @staticmethod
    def displace_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "DISPLACE"]

    def store_values(self):
        for object_name in self.displace_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.displace_objects[object_name]["modifier"]]
            self.displace_objects[object_name]["show_viewport"] = modifier.show_viewport
            self.displace_objects[object_name]["strength"] = modifier.strength
            self.displace_objects[object_name]["mid_level"] = modifier.mid_level
            self.displace_objects[object_name]["direction"] = modifier.direction
            self.displace_objects[object_name]["space"] = modifier.space

    def modal(self, context, event):
        divisor = 10000 * self.modal_scale if event.shift else 100000000000 if event.ctrl else 100 * self.modal_scale
        divisor_profile = 500 * self.modal_scale if event.ctrl else 100000000000
        offset_x = event.mouse_region_x - self.last_mouse_x
        strength_offset = offset_x / divisor / get_dpi_factor()
        offset = offset_x / divisor_profile / get_dpi_factor()

        context.area.header_text_set("Hardops Displace:     Space: {}".format(self.active_displace_modifier.space))

        for object_name in self.displace_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.displace_objects[object_name]["modifier"]]

            modifier.strength = modifier.strength - strength_offset

            if event.ctrl:
                modifier.mid_level = modifier.mid_level - offset

            if event.type == "WHEELUPMOUSE" or event.type == "NUMPAD_PLUS" and event.value == "PRESS":
                direction_types = ["X", "Y", "Z", "NORMAL", "CUSTOM_NORMAL", "RGB_TO_XYZ"]
                modifier.direction = direction_types[(direction_types.index(modifier.direction) + 1) % len(direction_types)]
            if event.type == "WHEELDOWNMOUSE" or event.type == "NUMPAD_MINUS" and event.value == "PRESS":
                direction_types = ["X", "Y", "Z", "NORMAL", "CUSTOM_NORMAL", "RGB_TO_XYZ"]
                modifier.direction = direction_types[(direction_types.index(modifier.direction) - 1) % len(direction_types)]

            if event.type == "Q" and event.value == "PRESS":
                space_types = ["GLOBAL", "LOCAL"]
                modifier.space = space_types[(space_types.index(modifier.space) + 1) % len(space_types)]

            if event.type == "X" and event.value == "PRESS":
                modifier.direction = "X"
            if event.type == "Y" and event.value == "PRESS":
                modifier.direction = "Y"
            if event.type == "Z" and event.value == "PRESS":
                modifier.direction = "Z"
            if event.type == "N" and event.value == "PRESS":
                modifier.direction = "NORMAL"

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
        for object_name in self.displace_objects:
            object = bpy.data.objects[object_name]
            if "added_modifier" in self.displace_objects[object_name]:
                object.modifiers.remove(object.modifiers[self.displace_objects[object_name]["modifier"]])
            else:
                modifier = object.modifiers[self.displace_objects[object_name]["modifier"]]
                modifier.show_viewport = self.displace_objects[object_name]["show_viewport"]
                modifier.strength = self.displace_objects[object_name]["strength"]
                modifier.mid_level = self.displace_objects[object_name]["mid_level"]
                modifier.direction = self.displace_objects[object_name]["direction"]
                modifier.space = self.displace_objects[object_name]["space"]

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

        l1 = (-1, 23, 4, 92)
        l2 = (94, 23, 4, 184)
        l3 = (186, 23, 4, 280)
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

        draw_text("Str: {:.3f}".format(self.active_displace_modifier.strength),
                  x + 15 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text("Mid: {:.3f}".format(math.degrees(self.active_displace_modifier.mid_level)),
                  x + 100 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text("Direction: {}".format(self.active_displace_modifier.direction),
                  x + 190 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)


        self.draw_help(context, x, y, factor)

    def draw_help(self, context, x, y, factor):

        # color_text1 = Hops_text_color()
        color_text2 = get_preferences().Hops_hud_help_color
        # color_border = Hops_border_color()
        # color_border2 = Hops_border2_color()

        if get_preferences().hops_modal_help:

            draw_text(" move - set strength",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)

            draw_text(" ctrl - set Offset",
                      x + 45 * factor, y - 26 * factor, size=11, color=color_text2)

            draw_text(" WHEEL - Direction",
                      x + 45 * factor, y - 38 * factor, size=11, color=color_text2)

            draw_text(" Q- Space",
                      x + 45 * factor, y - 50 * factor, size=11, color=color_text2)

            draw_text(" H - Show/Hide Help",
                      x + 45 * factor, y - 74 * factor, size=11, color=color_text2)

        else:
            draw_text(" H - Show/Hide Help",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)
