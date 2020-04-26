import bpy
import gpu
import math
from math import radians
from bgl import *
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... utils.objects import apply_scale
from ... graphics.drawing2d import draw_text, set_drawing_dpi, draw_box
from ... preferences import Hops_text_color, Hops_border_color, Hops_border2_color, get_preferences


class HOPS_OT_AdjustBevelOperator(bpy.types.Operator):
    bl_idname = "hops.adjust_bevel"
    bl_label = "Adjust Bevel"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = """LMB - Adjust Bevel Modifier
LMB + CTRL - Add new Bevel Modifier
LMB + Shift + CTRL - Add new Bevel Modifier with 60 angle

Press H for help."""

    mods: list = []
    bevel_objects = {}

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        for obj in selected:
            return getattr(obj, "type", "") == "MESH"

    def invoke(self, context, event):
        self.segments_mode = False
        self.adaptivemode = get_preferences().adaptivemode
        self.modal_scale = get_preferences().Hops_modal_scale
        self.modal_percent_scale = get_preferences().Hops_modal_percent_scale
        self.mods = []
        self.bevel_objects = {}

        if get_preferences().adaptivewidth:
            object = context.active_object
            dimensions = [abs(object.dimensions[0]), abs(object.dimensions[1]), abs(object.dimensions[2])]
            smallest_dimension = min(dimensions)
            # self.adaptive_scale = get_preferences().adaptiveoffset * (smallest_dimension*smallest_dimension*60)
            self.modal_scale = get_preferences().Hops_modal_scale / smallest_dimension

        for object in context.selected_objects:
            self.get_bevel_modifier(context, object, event)

        self.active_bevel_modifier = context.object.modifiers[self.bevel_objects[context.object.name]["modifier"]]
        self.store_values()

        self.percent_mode = False

        for object_name in self.bevel_objects:
            self.bevel_objects[object_name]["start_width"] = self.bevel_objects[object_name]["width"]

        # apply the scale, keep child transformations and bevel width as well as fix DECALmachine backup matrices
        if context.mode == 'OBJECT': #doesnt work in object mode
            apply_scale([bpy.data.objects[name] for name in self.bevel_objects if self.bevel_objects[name].get("scaled")])

        self.start_mouse_position = Vector((event.mouse_region_x, event.mouse_region_y))
        self.mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        self.last_mouse_x = event.mouse_region_x

        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_ui, (context, ), "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}

    def get_bevel_modifier(self, context, object, event):
        if event.ctrl:
            self.add_bevel_modifier(context, object, math.radians(60 if event.shift else 30))
        else:
            try: self.bevel_objects.setdefault(object.name, {})["modifier"] = self.bevel_modifiers(object)[-1].name
            except: self.add_bevel_modifier(context, object, math.radians(30))

    def add_bevel_modifier(self, context, object, angle):
        bevel_modifier = object.modifiers.new(name="Bevel", type="BEVEL")
        bevel_modifier.limit_method = "ANGLE"
        bevel_modifier.angle_limit = angle
        #bevel_modifier.angle_limit = 1.0472
        bevel_modifier.miter_outer = 'MITER_ARC'
        bevel_modifier.width = 0.02
        bevel_modifier.profile = 0.70
        bevel_modifier.segments = 3
        bevel_modifier.loop_slide = get_preferences().bevel_loop_slide
        bevel_modifier.use_clamp_overlap = False
        object.show_all_edges = True
        bpy.context.object.data.use_auto_smooth = True
        bpy.context.object.data.auto_smooth_angle = 1.0472
        if context.mode == 'EDIT_MESH':
            vg = object.vertex_groups.new(name='HardOps')
            bpy.ops.object.vertex_group_assign()
            bevel_modifier.limit_method = 'VGROUP'
            bevel_modifier.vertex_group = vg.name
            bpy.ops.mesh.faces_shade_smooth()
        else:
            bpy.ops.object.shade_smooth()

        self.bevel_objects.setdefault(object.name, {})["modifier"] = bevel_modifier.name
        self.bevel_objects[object.name]["added_modifier"] = True

    @staticmethod
    def bevel_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "BEVEL"]

    def store_values(self, obj=None, mod=None):
        if not obj:
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
                self.bevel_objects[object_name]["start_width"] = modifier.width

            return

        # self.bevel_objects[obj.name]["show_wire"] = obj.show_wire

        # if object.scale != Vector((1.0, 1.0, 1.0)):
        #     self.bevel_objects[obj.name]["scaled"] = obj.scale[:]

        modifier = obj.modifiers[mod.name]
        self.bevel_objects[obj.name]["modifier"] = modifier.name
        self.bevel_objects[obj.name]["show_viewport"] = modifier.show_viewport
        self.bevel_objects[obj.name]["width"] = modifier.width
        self.bevel_objects[obj.name]["profile"] = modifier.profile
        self.bevel_objects[obj.name]["segments"] = modifier.segments
        self.bevel_objects[obj.name]["limit_method"] = modifier.limit_method
        self.bevel_objects[obj.name]["use_only_vertices"] = modifier.use_only_vertices
        self.bevel_objects[obj.name]["use_clamp_overlap"] = modifier.use_clamp_overlap
        self.bevel_objects[obj.name]["offset_type"] = modifier.offset_type
        self.bevel_objects[obj.name]["loop_slide"] = modifier.loop_slide
        self.bevel_objects[obj.name]["start_width"] = modifier.width
        self.last_mouse_x = self.mouse_x


    def change_bevel(self, object, modifier, neg=False):
        bevels = [mod for mod in object.modifiers if mod.type == 'BEVEL']
        if neg:
            index = [mod.name for mod in bevels].index(modifier.name)
            self.store_values(obj=object, mod=bevels[index-1])

            return object.modifiers[self.bevel_objects[object.name]["modifier"]]

        else:
            index = [mod.name for mod in bevels].index(modifier.name)
            if index + 1 < len(bevels):
                self.store_values(obj=object, mod=bevels[index+1])
            else:
                self.store_values(obj=object, mod=bevels[0])

            return object.modifiers[self.bevel_objects[object.name]["modifier"]]


    def modal(self, context, event):
        self.mouse_x = event.mouse_region_x

        divisor = 10000 * self.modal_scale if event.shift else 1000 * self.modal_scale if event.ctrl else 1000 * self.modal_scale
        divisor_profile = 500 * self.modal_scale if event.ctrl else 100000000000
        offset_x = self.mouse_x - self.last_mouse_x
        profile_offset = offset_x / divisor_profile / get_dpi_factor()


        context.area.header_text_set("Hardops Adjust Bevel,                Current modifier: - {}".format(self.active_bevel_modifier.name,))

        for object_name in self.bevel_objects:
            object = bpy.data.objects[object_name]
            modifier = object.modifiers[self.bevel_objects[object_name]["modifier"]]

            # modifier.width -= offset_x / divisor / get_dpi_factor()

            if self.segments_mode:
                # self.bevel_objects[object_name]["start_width"] = modifier.width
                segments_offset = self.stop_position - self.mouse_x
                # bevel_offset = offset_x / 100000000000 / get_dpi_factor()
                if segments_offset != 0:
                    modifier.segments = self.stop_segments + int(segments_offset / 60 / get_dpi_factor())

                self.bevel_objects[object_name]["start_width"] = modifier.width
                self.last_mouse_x = self.mouse_x

            else:
                bevel_offset = offset_x / divisor / get_dpi_factor()
                if event.ctrl:
                    modifier.width = round(self.bevel_objects[object_name]["start_width"] - bevel_offset, 1)
                else:
                    modifier.width = self.bevel_objects[object_name]["start_width"] - bevel_offset
                    self.bevel_objects[object_name]["start_width"] = modifier.width
                    self.last_mouse_x = self.mouse_x

            if self.adaptivemode:
                self.adaptivesegments = int(modifier.width * get_preferences().adaptiveoffset) + object.hops.adaptivesegments
                modifier.segments = self.adaptivesegments

            if event.type == "WHEELUPMOUSE" or event.type == "NUMPAD_PLUS" and event.value == "PRESS":
                if self.adaptivemode:
                    if event.ctrl:
                        get_preferences().adaptiveoffset += 0.5
                    elif event.shift:
                        modifier = self.change_bevel(object, modifier)
                    else:
                        object.hops.adaptivesegments += 1

                elif event.shift:
                    modifier = self.change_bevel(object, modifier)

                else:
                    modifier.segments += 1

            if event.type == "WHEELDOWNMOUSE" or event.type == "NUMPAD_MINUS" and event.value == "PRESS":
                if self.adaptivemode:
                    if event.ctrl:
                        get_preferences().adaptiveoffset -= 0.5
                    elif event.shift:
                        modifier = self.change_bevel(object, modifier, neg=True)
                    else:
                        object.hops.adaptivesegments -= 1

                elif event.shift:
                    modifier = self.change_bevel(object, modifier, neg=True)

                else:
                    modifier.segments -= 1

            if event.type == "ONE" and event.value == "PRESS":
                if object.data.auto_smooth_angle == radians(60):
                    object.data.auto_smooth_angle = radians(30)
                elif object.data.auto_smooth_angle == radians(30):
                    object.data.auto_smooth_angle = radians(60)
                else:
                    object.data.auto_smooth_angle = radians(30)

            if event.type == "TWO" and event.value == "PRESS":
                # modifier.limit_method = "NONE"
                modifier.segments = 6
                modifier.use_only_vertices = True
                modifier.use_clamp_overlap = False
            if event.type == "A" and event.value == "PRESS":
                self.adaptivemode = not self.adaptivemode
                get_preferences().adaptivemode = not get_preferences().adaptivemode
            if event.type == "Q" and event.value == "PRESS":
                modifier = self.change_bevel(object, modifier, neg=True)
                self.bevel_objects[object_name]["start_width"] = modifier.width
            if event.type == "E" and event.value == "PRESS":
                modifier = self.change_bevel(object, modifier)
                self.bevel_objects[object_name]["start_width"] = modifier.width
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
                self.stop_position = self.mouse_x
                self.stop_segments = modifier.segments
                self.segments_mode = not self.segments_mode
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

        self.active_bevel_modifier = context.object.modifiers[self.bevel_objects[context.object.name]["modifier"]]
        #self.last_mouse_x = event.mouse_region_x
        return {'RUNNING_MODAL'}

    def restore(self):
        scale_vectors = []
        for object_name in self.bevel_objects:
            object = bpy.data.objects[object_name]
            object.show_wire = self.bevel_objects[object_name]["show_wire"]
            if "scaled" in self.bevel_objects[object_name]:
                scale_vector = self.bevel_objects[object_name]["scaled"]
                scale_vectors.append(scale_vector)
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

        # reversed scale application, by passing in the scale_vectors
        apply_scale([bpy.data.objects[name] for name in self.bevel_objects if self.bevel_objects[name].get("scaled")], scale_vectors=scale_vectors)

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
            (0, 1, 2), (1, 2, 3), (4, 5, 6), (5, 6, 7), (8, 9, 10), (9, 10, 11), (12, 13, 14), (13, 14, 15), (16, 15, 17), (15, 16, 17))

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

        draw_text("{}".format(self.active_bevel_modifier.segments),
                  x + 23 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text(" B-Width: {:.3f}".format(self.active_bevel_modifier.width),
                  x + 50 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text("Profile:{:.2f}".format(self.active_bevel_modifier.profile),
                  x + 154 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text("{}".format(self.active_bevel_modifier.offset_type),
                  x + 227 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        if self.adaptivemode:
            draw_text("A",
                      x + 1 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        self.draw_help(context, x, y, factor)

    def draw2(self, context):
        x, y = self.start_mouse_position
        object = context.active_object

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
        draw_box(x + 24 * factor, y + 8 * factor, 180 * factor, 30 * factor, color=color_border)

    def draw_help(self, context, x, y, factor):

        # color_text1 = Hops_text_color()
        color_text2 = get_preferences().Hops_hud_help_color
        # color_border = Hops_border_color()
        # color_border2 = Hops_border2_color()

        if get_preferences().hops_modal_help:

            draw_text(" scroll - set segment",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)

            draw_text(" ctrl - set width(snap)",
                      x + 45 * factor, y - 26 * factor, size=11, color=color_text2)

            draw_text(" W - choose offset type",
                      x + 45 * factor, y - 38 * factor, size=11, color=color_text2)

            draw_text(" V - show/hide mod in vieport",
                      x + 45 * factor, y - 50 * factor, size=11, color=color_text2)

            draw_text(" Z -  show/hide wire",
                      x + 45 * factor, y - 62 * factor, size=11, color=color_text2)

            draw_text(" 1 - autosmooth toggle",
                      x + 45 * factor, y - 74 * factor, size=11, color=color_text2)

            draw_text(" 2 - use bevel verts",
                      x + 45 * factor, y - 86 * factor, size=11, color=color_text2)

            draw_text(" A - use adaptive mode",
                      x + 45 * factor, y - 98 * factor, size=11, color=color_text2)

            draw_text(" ctrl + scroll - adaptive offset",
                      x + 45 * factor, y - 110 * factor, size=11, color=color_text2)

            draw_text(" C - Loop Slide",
                      x + 45 * factor, y - 122 * factor, size=11, color=color_text2)

            draw_text(" S - modal segments",
                      x + 45 * factor, y - 134 * factor, size=11, color=color_text2)

            draw_text(" E /Shift+ wheelUP - change modifier UP",
                      x + 45 * factor, y - 146 * factor, size=11, color=color_text2)

            draw_text(" Q /Shift+ wheelDOWN - change modifier DOWN",
                      x + 45 * factor, y - 158 * factor, size=11, color=color_text2)

            draw_text(" H - Show/Hide Help",
                      x + 45 * factor, y - 170 * factor, size=11, color=color_text2)

        else:
            draw_text(" H - Show/Hide Help",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)
