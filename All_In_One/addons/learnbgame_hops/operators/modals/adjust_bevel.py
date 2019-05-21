import bpy
import gpu
from bgl import *
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi, draw_box
from ... preferences import Hops_text_color, Hops_text2_color, Hops_border_color, Hops_border2_color, get_preferences


class HOPS_OT_AdjustBevelOperator(bpy.types.Operator):
    bl_idname = "hops.adjust_bevel"
    bl_label = "Adjust Bevel"
    bl_description = """Interactively and non destructively adds BEVEL modifier Press H for help"""
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}

    bevel_objects = {}

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        for obj in selected:
            return getattr(obj, "type", "") == "MESH"

    def invoke(self, context, event):
        self.adaptivemode = get_preferences().adaptivemode
        self.modal_scale = get_preferences().Hops_modal_scale
        self.modal_percent_scale = get_preferences().Hops_modal_percent_scale
        self.bevel_objects = {}

        if get_preferences().adaptivewidth:
            object = context.active_object
            dimensions = [abs(object.dimensions[0]), abs(object.dimensions[1]), abs(object.dimensions[2])]
            smallest_dimension = min(dimensions)
            # self.adaptive_scale = get_preferences().adaptiveoffset * (smallest_dimension*smallest_dimension*60)
            self.modal_scale = get_preferences().Hops_modal_scale / smallest_dimension

        for object in context.selected_objects:
            self.get_bevel_modifier(object)

        self.active_bevel_modifier = context.object.modifiers[self.bevel_objects[context.object.name]["modifier"]]
        self.store_values()

        self.percent_mode = False

        if not get_preferences().decalmachine_fix:
            if not self.adaptivemode:
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        self.start_mouse_position = Vector((event.mouse_region_x, event.mouse_region_y))
        self.last_mouse_x = event.mouse_region_x

        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_ui, (context, ), "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}

    def get_bevel_modifier(self, object):

        try: self.bevel_objects.setdefault(object.name, {})["modifier"] = self.bevel_modifiers(object)[-1].name
        except: self.add_bevel_modifier(object)

    def add_bevel_modifier(self, object):

        bevel_modifier = object.modifiers.new(name="Bevel", type="BEVEL")
        bevel_modifier.limit_method = "ANGLE"
        bevel_modifier.width = 0.200
        bevel_modifier.profile = 0.70
        bevel_modifier.segments = 3
        bevel_modifier.loop_slide = get_preferences().bevel_loop_slide
        bevel_modifier.use_clamp_overlap = False
        object.show_all_edges = True
        bpy.ops.object.shade_smooth()

        self.bevel_objects.setdefault(object.name, {})["modifier"] = bevel_modifier.name
        self.bevel_objects[object.name]["added_modifier"] = True

    @staticmethod
    def bevel_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "BEVEL"]

    def store_values(self):
        for object_name in self.bevel_objects:
            object = bpy.data.objects[object_name]
            self.bevel_objects[object_name]["show_wire"] = object.show_wire
            if object.scale != Vector((1.0, 1.0, 1.0)):
                self.bevel_objects[object_name]["scaled"] = object.scale[:]
            modifier = object.modifiers[self.bevel_objects[object_name]["modifier"]]
            self.bevel_objects[object_name]["show_viewport"] = modifier.show_viewport
            self.bevel_objects[object_name]["width"] = modifier.width
            self.bevel_objects[object_name]["profile"] = modifier.profile
            self.bevel_objects[object_name]["segments"] = modifier.segments
            self.bevel_objects[object_name]["limit_method"] = modifier.limit_method
            self.bevel_objects[object_name]["use_only_vertices"] = modifier.use_only_vertices
            self.bevel_objects[object_name]["use_clamp_overlap"] = modifier.use_clamp_overlap
            self.bevel_objects[object_name]["offset_type"] = modifier.offset_type
            self.bevel_objects[object_name]["loop_slide"] = modifier.loop_slide

    def modal(self, context, event):
        divisor = 10000 * self.modal_scale if event.shift else 100000000000 if event.ctrl else 1000 * self.modal_scale
        divisor_profile = 500 * self.modal_scale if event.ctrl else 100000000000
        offset_x = event.mouse_region_x - self.last_mouse_x
        bevel_offset = offset_x / divisor / get_dpi_factor()
        profile_offset = offset_x / divisor_profile / get_dpi_factor()

        for object_name in self.bevel_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.bevel_objects[object_name]["modifier"]]
            modifier.width = modifier.width - bevel_offset

            if self.adaptivemode:
                self.adaptivesegments = int(modifier.width * get_preferences().adaptiveoffset) + object.hops.adaptivesegments
                modifier.segments = self.adaptivesegments

            if event.ctrl:
                modifier.profile = modifier.profile - profile_offset
            if event.type == "WHEELUPMOUSE" or event.type == "NUMPAD_PLUS" and event.value == "PRESS":
                if self.adaptivemode:
                    if event.ctrl:
                        get_preferences().adaptiveoffset += 0.5
                    else:
                        object.hops.adaptivesegments += 1
                else:
                    modifier.segments += 1
            if event.type == "WHEELDOWNMOUSE" or event.type == "NUMPAD_MINUS" and event.value == "PRESS":
                if self.adaptivemode:
                    if event.ctrl:
                        get_preferences().adaptiveoffset -= 0.5
                    else:
                        object.hops.adaptivesegments -= 1
                else:
                    modifier.segments -= 1
            if event.type == "TWO" and event.value == "PRESS":
                modifier.limit_method = "NONE"
                modifier.segments = 6
                modifier.use_only_vertices = True
                modifier.use_clamp_overlap = False
            if event.type == "A" and event.value == "PRESS":
                self.adaptivemode = not self.adaptivemode
                get_preferences().adaptivemode = not get_preferences().adaptivemode
            if event.type == "C" and event.value == "PRESS":
                modifier.loop_slide = not modifier.loop_slide
            if event.type == "W" and event.value == "PRESS":
                offset_types = ["OFFSET", "WIDTH", "DEPTH", "PERCENT"]
                modifier.offset_type = offset_types[(offset_types.index(modifier.offset_type) + 1) % len(offset_types)]
            if event.type == "V" and event.value == "PRESS":
                modifier.show_viewport = False if modifier.show_viewport else True
            if event.type == "Z" and event.value == "PRESS":
                object.show_wire = False if object.show_wire else True
                object.show_all_edges = True if object.show_wire else False
            if event.type == "S" and event.value == "PRESS":
                limit_method = ["WEIGHT", "ANGLE"]
                modifier.limit_method = limit_method[(limit_method.index(modifier.limit_method) + 1) % len(limit_method)]
            if event.type == "H" and event.value == "PRESS":
                bpy.context.space_data.show_gizmo_navigate = True
                get_preferences().hops_modal_help = not get_preferences().hops_modal_help
            if event.type in ("ESC", "RIGHTMOUSE"):
                self.restore()
                bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
                return {'CANCELLED'}
            if event.type in ("SPACE", "LEFTMOUSE"):
                bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
                return {'FINISHED'}

        self.last_mouse_x = event.mouse_region_x
        return {'RUNNING_MODAL'}

    def restore(self):
        for object_name in self.bevel_objects:
            object = bpy.data.objects[object_name]
            object.show_wire = self.bevel_objects[object_name]["show_wire"]
            if "scaled" in self.bevel_objects[object_name]:
                scale_vector = self.bevel_objects[object_name]["scaled"]
                object.scale[0] /= scale_vector[0]
                object.scale[1] /= scale_vector[1]
                object.scale[2] /= scale_vector[2]
            if "added_modifier" in self.bevel_objects[object_name]:
                object.modifiers.remove(object.modifiers[self.bevel_objects[object_name]["modifier"]])
            else:
                modifier = object.modifiers[self.bevel_objects[object_name]["modifier"]]
                modifier.show_viewport = self.bevel_objects[object_name]["show_viewport"]
                modifier.width = self.bevel_objects[object_name]["width"]
                modifier.profile = self.bevel_objects[object_name]["profile"]
                modifier.segments = self.bevel_objects[object_name]["segments"]
                modifier.limit_method = self.bevel_objects[object_name]["limit_method"]
                modifier.use_only_vertices = self.bevel_objects[object_name]["use_only_vertices"]
                modifier.use_clamp_overlap = self.bevel_objects[object_name]["use_clamp_overlap"]
                modifier.offset_type = self.bevel_objects[object_name]["offset_type"]
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        for object_name in self.bevel_objects:
            if "scaled" in self.bevel_objects[object_name]:
                object = bpy.data.objects[object_name]
                object.scale = self.bevel_objects[object_name]["scaled"]

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
            (x + 46 * factor, y + 23 * factor), (x + 46 * factor, y + 4 * factor), (x + 146 * factor, y + 23 * factor), (x + 146 * factor, y + 4 * factor),
            (x + 149 * factor, y + 23 * factor), (x + 149 * factor, y + 4 * factor), (x + 220 * factor, y + 23 * factor), (x + 220 * factor, y + 4 * factor),
            (x + 223 * factor, y + 23 * factor), (x + 223 * factor, y + 4 * factor), (x + 280 * factor, y + 23 * factor), (x + 280 * factor, y + 4 * factor))

        indices = (
            (0, 1, 2), (1, 2, 3), (4, 5, 6), (5, 6, 7), (8, 9, 10), (9, 10, 11), (12, 13, 14), (13, 14, 15))

        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)

        shader.bind()
        shader.uniform_float("color", (0.17, 0.17, 0.17, 1))
        glEnable(GL_BLEND)
        batch.draw(shader)
        glDisable(GL_BLEND)

        draw_text("{}".format(self.active_bevel_modifier.segments),
                  x + 27 * factor, y + 9 * factor, size=12, color=(0.831, 0.831, 0.831, 1))

        draw_text(" B-Width: {:.3f}".format(self.active_bevel_modifier.width),
                  x + 50 * factor, y + 9 * factor, size=12, color=(0.831, 0.831, 0.831, 1))

        draw_text("Profile:{:.2f}".format(self.active_bevel_modifier.profile),
                  x + 154 * factor, y + 9 * factor, size=12, color=(0.831, 0.831, 0.831, 1))

        draw_text("{}".format(self.active_bevel_modifier.offset_type),
                  x + 227 * factor, y + 9 * factor, size=12, color=(0.831, 0.831, 0.831, 1))

        if self.adaptivemode:
            draw_text("A",
                  x + 1 * factor, y + 9 * factor, size=12, color=(0.831, 0.831, 0.831, 1))

        self.draw_help(context, x, y, factor)

    def draw2(self, context):
        x, y = self.start_mouse_position
        object = context.active_object

        set_drawing_dpi(get_dpi())
        factor = get_dpi_factor()
        color_text1 = Hops_text_color()
        color_text2 = Hops_text2_color()
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
        draw_box(x + 24 * factor, y + 8 * factor, 180 * factor, 30 * factor, color=color_border)

    def draw_help(self, context, x, y, factor):

        # color_text1 = Hops_text_color()
        color_text2 = Hops_text2_color()
        # color_border = Hops_border_color()
        # color_border2 = Hops_border2_color()

        if get_preferences().hops_modal_help:

            draw_text(" scroll - set segment",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)

            draw_text(" ctrl - set profile",
                      x + 45 * factor, y - 26 * factor, size=11, color=color_text2)

            draw_text(" W - choose offset type",
                      x + 45 * factor, y - 38 * factor, size=11, color=color_text2)

            draw_text(" V - show/hide mod in vieport",
                      x + 45 * factor, y - 50 * factor, size=11, color=color_text2)

            draw_text(" Z -  show/hide wire",
                      x + 45 * factor, y - 62 * factor, size=11, color=color_text2)

            draw_text(" 2 - use bevel verts",
                      x + 45 * factor, y - 74 * factor, size=11, color=color_text2)

            draw_text(" A - use adaptive mode",
                      x + 45 * factor, y - 86 * factor, size=11, color=color_text2)

            draw_text(" ctrl + scroll - adaptive offset",
                      x + 45 * factor, y - 98 * factor, size=11, color=color_text2)

            draw_text(" C - Loop Slide",
                      x + 45 * factor, y - 110 * factor, size=11, color=color_text2)

            draw_text(" S - Limit Method",
                      x + 45 * factor, y - 122 * factor, size=11, color=color_text2)

            draw_text(" H - Show/Hide Help",
                      x + 45 * factor, y - 142 * factor, size=11, color=color_text2)

        else:
            draw_text(" H - Show/Hide Help",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)
