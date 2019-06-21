import bpy
import gpu
import math
from bgl import *
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi
from ... preferences import Hops_text_color, Hops_border_color, Hops_border2_color, get_preferences


class HOPS_OT_MOD_Cast(bpy.types.Operator):
    bl_idname = "hops.mod_cast"
    bl_label = "Adjust Cast Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """LMB - Adjust Cast Modifier
LMB + CTRL - Add New cast Modifier

Press H for help."""

    cast_objects = {}

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        for obj in selected:
            return getattr(obj, "type", "") == "MESH"

    def invoke(self, context, event):
        self.factor_mode = True
        self.stop_position = event.mouse_region_x
        self.size_mode = False
        self.radius_mode = False
        self.modal_scale = get_preferences().Hops_modal_scale
        self.cast_objects = {}

        for object in context.selected_objects:
            self.get_deform_modifier(object, event)

        self.active_cast_modifier = context.object.modifiers[self.cast_objects[context.object.name]["modifier"]]
        self.store_values()

        self.start_mouse_position = Vector((event.mouse_region_x, event.mouse_region_y))
        self.last_mouse_x = event.mouse_region_x

        self.stop_factor = self.active_cast_modifier.factor

        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_ui, (context, ), "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}

    def get_deform_modifier(self, object, event):
        if event.ctrl:
            self.add_deform_modifier(object)
        else:
            try: self.cast_objects.setdefault(object.name, {})["modifier"] = self.cast_modifiers(object)[-1].name
            except: self.add_deform_modifier(object)

    def add_deform_modifier(self, object):
        cast_modifier = object.modifiers.new(name="cast", type="CAST")
        cast_modifier.factor = 1.0
        cast_modifier.radius = 0
        cast_modifier.size = 0
        cast_modifier.cast_type = "SPHERE"
        cast_modifier.use_y = True
        cast_modifier.use_x = True
        cast_modifier.use_z = True
        cast_modifier.use_radius_as_size = True

        self.cast_objects.setdefault(object.name, {})["modifier"] = cast_modifier.name
        self.cast_objects[object.name]["added_modifier"] = True

    @staticmethod
    def cast_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "CAST"]

    def store_values(self):
        for object_name in self.cast_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.cast_objects[object_name]["modifier"]]
            self.cast_objects[object_name]["show_viewport"] = modifier.show_viewport
            self.cast_objects[object_name]["factor"] = modifier.factor
            self.cast_objects[object_name]["radius"] = modifier.radius
            self.cast_objects[object_name]["size"] = modifier.size
            self.cast_objects[object_name]["cast_type"] = modifier.cast_type
            self.cast_objects[object_name]["use_y"] = modifier.use_y
            self.cast_objects[object_name]["use_z"] = modifier.use_z
            self.cast_objects[object_name]["use_x"] = modifier.use_x
            self.cast_objects[object_name]["use_radius_as_size"] = modifier.use_radius_as_size

    def modal(self, context, event):
        context.area.header_text_set("Hardops Cast:     X : Use x - {}    Y : Usey - {}     Z : Use z - {}     Q : radius as size - {}".format(self.active_cast_modifier.use_x, self.active_cast_modifier.use_y, self.active_cast_modifier.use_z, self.active_cast_modifier.use_radius_as_size))

        for object_name in self.cast_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.cast_objects[object_name]["modifier"]]

            if self.radius_mode:
                radius_offset = self.stop_position - event.mouse_region_x
                modifier.radius = int(self.stop_radius) + int(radius_offset / 60 / get_dpi_factor())

            if self.size_mode:
                size_offset = self.stop_position - event.mouse_region_x
                modifier.size = int(self.stop_size) + int(size_offset / 60 / get_dpi_factor())

            if self.factor_mode:
                factor_offset = self.stop_position - event.mouse_region_x
                modifier.factor = int(self.stop_factor) + int(factor_offset / 60 / get_dpi_factor())

            if event.type == "R" and event.value == "PRESS":
                self.stop_position = event.mouse_region_x
                self.stop_radius = modifier.radius
                if self.size_mode:
                    self.size_mode = False
                if self.factor_mode:
                    self.factor_mode = False
                if self.radius_mode:
                    self.factor_mode = True
                self.radius_mode = not self.radius_mode

            if event.type == "S" and event.value == "PRESS":
                self.stop_position = event.mouse_region_x
                self.stop_size = modifier.size
                if self.factor_mode:
                    self.factor_mode = False
                if self.radius_mode:
                    self.radius_mode = False
                if self.size_mode:
                    self.factor_mode = True
                self.size_mode = not self.size_mode

            if event.type == "WHEELUPMOUSE" or event.type == "NUMPAD_PLUS" and event.value == "PRESS":
                cast_type = ["SPHERE", "CUBOID", "CYLINDER"]
                modifier.cast_type = cast_type[(cast_type.index(modifier.cast_type) + 1) % len(cast_type)]
            if event.type == "WHEELDOWNMOUSE" or event.type == "NUMPAD_MINUS" and event.value == "PRESS":
                cast_type = ["SPHERE", "CUBOID", "CYLINDER"]
                modifier.cast_type = cast_type[(cast_type.index(modifier.cast_type) - 1) % len(cast_type)]

            if event.type == "X" and event.value == "PRESS":
                modifier.use_x = not modifier.use_x

            if event.type == "Y" and event.value == "PRESS":
                modifier.use_y = not modifier.use_y

            if event.type == "Z" and event.value == "PRESS":
                modifier.use_z = not modifier.use_z

            if event.type == "Q" and event.value == "PRESS":
                modifier.use_radius_as_size = not modifier.use_radius_as_size

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
        for object_name in self.cast_objects:
            object = bpy.data.objects[object_name]
            if "added_modifier" in self.cast_objects[object_name]:
                object.modifiers.remove(object.modifiers[self.cast_objects[object_name]["modifier"]])
            else:
                modifier = object.modifiers[self.cast_objects[object_name]["modifier"]]
                modifier.show_viewport = self.cast_objects[object_name]["show_viewport"]
                modifier.factor = self.cast_objects[object_name]["factor"]
                modifier.radius = self.cast_objects[object_name]["radius"]
                modifier.size = self.cast_objects[object_name]["size"]
                modifier.cast_type = self.cast_objects[object_name]["cast_type"]
                modifier.use_y = self.cast_objects[object_name]["use_y"]
                modifier.use_z = self.cast_objects[object_name]["use_z"]
                modifier.use_x = self.cast_objects[object_name]["use_x"]
                modifier.use_radius_as_size = self.cast_objects[object_name]["use_radius_as_size"]

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
        l4 = (262, 23, 4, 370)
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

        draw_text("Factor: {}".format(self.active_cast_modifier.factor),
                  x + 15 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text("Radius: {:.1f}".format(self.active_cast_modifier.radius),
                  x + 100 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text("Size: {}".format(self.active_cast_modifier.size),
                  x + 190 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text("Cast: {}".format(self.active_cast_modifier.cast_type),
                  x + 270 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        self.draw_help(context, x, y, factor)

    def draw_help(self, context, x, y, factor):

        # color_text1 = Hops_text_color()
        color_text2 = get_preferences().Hops_hud_help_color
        # color_border = Hops_border_color()
        # color_border2 = Hops_border2_color()

        if get_preferences().hops_modal_help:

            draw_text(" move - Factor",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)

            draw_text(" R - Radius",
                      x + 45 * factor, y - 26 * factor, size=11, color=color_text2)

            draw_text(" S - Size",
                      x + 45 * factor, y - 38 * factor, size=11, color=color_text2)

            draw_text(" WHEEL - Cast type",
                      x + 45 * factor, y - 50 * factor, size=11, color=color_text2)

            draw_text(" X - use x",
                      x + 45 * factor, y - 62 * factor, size=11, color=color_text2)

            draw_text(" Y - use y",
                      x + 45 * factor, y - 74 * factor, size=11, color=color_text2)

            draw_text(" Z - use z",
                      x + 45 * factor, y - 86 * factor, size=11, color=color_text2)

            draw_text(" Q - use_radius_as_size",
                      x + 45 * factor, y - 98 * factor, size=11, color=color_text2)

            draw_text(" H - Show/Hide Help",
                      x + 45 * factor, y - 110 * factor, size=11, color=color_text2)

        else:
            draw_text(" H - Show/Hide Help",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)
