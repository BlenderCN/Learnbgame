import bpy
import gpu
import math
from bgl import *
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi
from ... preferences import Hops_text_color, Hops_border_color, Hops_border2_color, get_preferences


class HOPS_OT_MOD_Wireframe(bpy.types.Operator):
    bl_idname = "hops.mod_wireframe"
    bl_label = "Adjust Simple Deform Modifier"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """LMB - Adjust Wireframe Modifier
LMB + CTRL - Add new Wireframe Modifier

Press H for help."""

    wireframe_objects = {}

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        for obj in selected:
            return getattr(obj, "type", "") == "MESH"

    def invoke(self, context, event):
        self.modal_scale = get_preferences().Hops_modal_scale
        self.wireframe_objects = {}

        for object in context.selected_objects:
            self.get_deform_modifier(object, event)

        self.active_wireframe_modifier = context.object.modifiers[self.wireframe_objects[context.object.name]["modifier"]]
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
            try: self.wireframe_objects.setdefault(object.name, {})["modifier"] = self.wireframe_modifiers(object)[-1].name
            except: self.add_deform_modifier(object)

    def add_deform_modifier(self, object):
        wireframe_modifier = object.modifiers.new(name="Wireframe", type="WIREFRAME")
        wireframe_modifier.thickness = 0.2
        wireframe_modifier.use_even_offset = True
        wireframe_modifier.use_relative_offset = False
        wireframe_modifier.use_replace = True
        wireframe_modifier.use_boundary = True

        self.wireframe_objects.setdefault(object.name, {})["modifier"] = wireframe_modifier.name
        self.wireframe_objects[object.name]["added_modifier"] = True

    @staticmethod
    def wireframe_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "WIREFRAME"]

    def store_values(self):
        for object_name in self.wireframe_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.wireframe_objects[object_name]["modifier"]]
            self.wireframe_objects[object_name]["show_viewport"] = modifier.show_viewport
            self.wireframe_objects[object_name]["thickness"] = modifier.thickness
            self.wireframe_objects[object_name]["offset"] = modifier.offset
            self.wireframe_objects[object_name]["use_even_offset"] = modifier.use_even_offset
            self.wireframe_objects[object_name]["use_relative_offset"] = modifier.use_relative_offset
            self.wireframe_objects[object_name]["use_replace"] = modifier.use_replace
            self.wireframe_objects[object_name]["use_boundary"] = modifier.use_boundary
            self.wireframe_objects[object_name]["use_crease"] = modifier.use_crease

    def modal(self, context, event):
        divisor = 10000 * self.modal_scale if event.shift else 100000000000 if event.ctrl else 1000 * self.modal_scale
        divisor_profile = 500 * self.modal_scale if event.ctrl else 100000000000
        offset_x = event.mouse_region_x - self.last_mouse_x
        thickness_offset = offset_x / divisor / get_dpi_factor()
        offset = offset_x / divisor_profile / get_dpi_factor()

        context.area.header_text_set("Hardops Wireframe:      B : use_boundary - {}      C : use_crease - {}      Q : use_even_offset - {}      W : use_relative_offset - {}".format(self.active_wireframe_modifier.use_boundary, self.active_wireframe_modifier.use_crease, self.active_wireframe_modifier.use_even_offset, self.active_wireframe_modifier.use_relative_offset))

        for object_name in self.wireframe_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.wireframe_objects[object_name]["modifier"]]

            modifier.thickness = modifier.thickness - thickness_offset

            if event.ctrl:
                modifier.offset = modifier.offset - offset

            if event.type == "Q" and event.value == "PRESS":
                modifier.use_even_offset = not modifier.use_even_offset
            if event.type == "W" and event.value == "PRESS":
                modifier.use_relative_offset = not modifier.use_relative_offset
            if event.type == "E" and event.value == "PRESS":
                modifier.use_replace = not modifier.use_replace
            if event.type == "B" and event.value == "PRESS":
                modifier.use_boundary = not modifier.use_boundary
            if event.type == "C" and event.value == "PRESS":
                modifier.use_crease = not modifier.use_crease

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
        for object_name in self.wireframe_objects:
            object = bpy.data.objects[object_name]
            if "added_modifier" in self.wireframe_objects[object_name]:
                object.modifiers.remove(object.modifiers[self.wireframe_objects[object_name]["modifier"]])
            else:
                modifier = object.modifiers[self.wireframe_objects[object_name]["modifier"]]
                modifier.show_viewport = self.wireframe_objects[object_name]["show_viewport"]
                modifier.thickness = self.wireframe_objects[object_name]["thickness"]
                modifier.offset = self.wireframe_objects[object_name]["offset"]
                modifier.use_even_offset = self.wireframe_objects[object_name]["use_even_offset"]
                modifier.use_relative_offset = self.wireframe_objects[object_name]["use_relative_offset"]
                modifier.use_replace = self.wireframe_objects[object_name]["use_replace"]
                modifier.use_boundary = self.wireframe_objects[object_name]["use_boundary"]
                modifier.use_crease = self.wireframe_objects[object_name]["use_crease"]

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

        draw_text("Thick: {:.3f}".format(self.active_wireframe_modifier.thickness),
                  x + 15 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text("Offset: {:.3f}".format(math.degrees(self.active_wireframe_modifier.offset)),
                  x + 100 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text("Replace: {}".format(self.active_wireframe_modifier.use_replace),
                  x + 190 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        self.draw_help(context, x, y, factor)

    def draw_help(self, context, x, y, factor):

        # color_text1 = Hops_text_color()
        color_text2 = get_preferences().Hops_hud_help_color
        # color_border = Hops_border_color()
        # color_border2 = Hops_border2_color()

        if get_preferences().hops_modal_help:

            draw_text(" move - set thickness",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)

            draw_text(" ctrl - set offset",
                      x + 45 * factor, y - 26 * factor, size=11, color=color_text2)

            draw_text(" Q - use_even_offset",
                      x + 45 * factor, y - 38 * factor, size=11, color=color_text2)

            draw_text(" W - use_relative_offset",
                      x + 45 * factor, y - 50 * factor, size=11, color=color_text2)

            draw_text(" E - use_replace",
                      x + 45 * factor, y - 62 * factor, size=11, color=color_text2)

            draw_text(" C - use_crease",
                      x + 45 * factor, y - 74 * factor, size=11, color=color_text2)

            draw_text(" B - use_boundary",
                      x + 45 * factor, y - 86 * factor, size=11, color=color_text2)

            draw_text(" H - Show/Hide Help",
                      x + 45 * factor, y - 98 * factor, size=11, color=color_text2)

        else:
            draw_text(" H - Show/Hide Help",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)
