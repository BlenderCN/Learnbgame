import bpy
import bmesh
import gpu
from bgl import *
from gpu_extras.batch import batch_for_shader
from bpy.props import *
from mathutils import Vector
from collections import OrderedDict
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi, draw_box
from ... preferences import Hops_text_color, Hops_text2_color, Hops_border_color, Hops_border2_color, get_preferences

class HOPS_OT_ResetAxisModal(bpy.types.Operator):
    bl_idname = "hops.reset_axis_modal"
    bl_label = "Hops Reset Axis"
    bl_description = "Reset object on selected axis. MODAL"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        self.start_mouse_position = Vector((event.mouse_region_x, event.mouse_region_y))
        if context.active_object.mode == "EDIT":
            self.bm = bmesh.from_edit_mesh(context.active_object.data)
            self.original_verts = [[i for i in vert.co] for vert in self.bm.verts]
        self.active_obj_original_location = [i for i in context.active_object.location]
        self.original_locations = [[i for i in obj.location] for obj in context.selected_objects]
        self.axises = []
        self.set_axis = ""
        self.xyz = ["X", "Y", "Z"]
        self.xyz_index = -1
        args = (context, )
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_ui, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type in ["WHEELUPMOUSE", "WHEELDOWNMOUSE", "NUMPAD_PLUS", "NUMPAD_MINUS"] and event.value == "PRESS":
            self.reset_object()
            if event.type in ["WHEELUPMOUSE", "NUMPAD_PLUS"]:
                self.xyz_index += 1
            if event.type in ["WHEELDOWNMOUSE", "NUMPAD_MINUS"]:
                self.xyz_index -= 1
            self.xyz_index = min(max(-1, self.xyz_index), 2)
            if self.xyz_index == -1:
                self.set_axis = "RESET"
            else:
                self.set_axis = self.xyz[self.xyz_index]

        if not event.shift and event.type == "C" and event.value == "PRESS":
            if self.set_axis == "C":
                self.set_axis = "RESET"
            else:
                self.set_axis = "C"
                context.view_layer.objects.active.select_set(False)
                bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
                context.view_layer.objects.active.select_set(True)

        if event.shift and event.type == "C" and event.value == "PRESS":
            if self.set_axis == "CO":
                self.set_axis = "RESET"
            else:
                self.set_axis = "CO"
                context.view_layer.objects.active.select_set(False)
                bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
                context.view_layer.objects.active.select_set(True)

        if event.type == "X" and event.value == "PRESS":
            if self.set_axis == "X":
                self.set_axis = "RESET"
            else:
                self.set_axis = "X"
            self.axises.append("X")

        if event.type == "Y" and event.value == "PRESS":
            if self.set_axis == "Y":
                self.set_axis = "RESET"
            else:
                self.set_axis = "Y"
            self.axises.append("Y")

        if event.type == "Z" and event.value == "PRESS":
            if self.set_axis == "Z":
                self.set_axis = "RESET"
            else:
                self.set_axis = "Z"
            self.axises.append("Z")

        if context.active_object.mode == "OBJECT":

            for obj in context.selected_objects:

                reset_to = [0, 0, 0]
                if len(context.selected_objects) > 1:
                    reset_to = self.active_obj_original_location
##                if obj.name == context.active_object.name:
##                    reset_to = context.space_data.cursor.location

                if self.set_axis == "X":
                    obj.location[0] = reset_to[0]
                elif self.set_axis == "Y":
                    obj.location[1] = reset_to[1]
                elif self.set_axis == "Z":
                    obj.location[2] = reset_to[2]

        elif context.active_object.mode == "EDIT":
            if self.set_axis == "X":
                bpy.ops.transform.resize(value=(0, 1, 1))
            elif self.set_axis == "Y":
                bpy.ops.transform.resize(value=(1, 0, 1))
            elif self.set_axis == "Z":
                bpy.ops.transform.resize(value=(1, 1, 0))

        if self.set_axis == "RESET":
            self.reset_object()

        if event.type == "H" and event.value == "PRESS":
            get_preferences().hops_modal_help = not get_preferences().hops_modal_help

        if event.type in ("ESC", "RIGHTMOUSE"):
            self.reset_object()
            return self.finish()

        if event.type in ("SPACE", "LEFTMOUSE"):
            return self.finish()

        self.last_mouse_x = event.mouse_region_x
        context.area.tag_redraw()
        return {"RUNNING_MODAL"}

    def reset_object(self):
        if bpy.context.active_object.mode == "EDIT":
            for count, vert in enumerate(self.bm.verts):
                vert.co = self.original_verts[count]
            bpy.ops.mesh.normals_make_consistent(inside=False)
        else:
            for count, obj in enumerate(bpy.context.selected_objects):
                obj.location = self.original_locations[count]

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

        l1 = (-1, 23, 4, 44)
        l2 = (46, 23, 4, 146)

        vertices = (
            (x + (l1[0] - offset) * factor, y + l1[1] * factor), (x + l1[0] * factor, y + l1[2] * factor), (x + (l1[3] - offset) * factor, y + l1[1] * factor), (x + l1[3] * factor, y + l1[2] * factor),
            (x + (l2[0] - offset) * factor, y + l2[1] * factor), (x + l2[0] * factor, y + l2[2] * factor), (x + (l2[3] - offset) * factor, y + l2[1] * factor), (x + l2[3] * factor, y + l2[2] * factor))

        l1 = (l1[0] - 15, l1[1], l1[2], l1[0] - 6)
        vertices2 = (
            (x + (l1[0] - offset) * factor, y + l1[1] * factor), (x + l1[0] * factor, y + l1[2] * factor), (x + (l1[3] - offset) * factor, y + l1[1] * factor), (x + l1[3] * factor, y + l1[2] * factor))

        indices = (
            (0, 1, 2), (1, 2, 3), (4, 5, 6), (5, 6, 7))

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

        axis = self.set_axis
        if axis == "RESET":
            axis = ""
            self.axises = []
        if len(axis) > 1:
            axis = axis[0]

        draw_text(axis,
                  x + 27 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        draw_text("Axis - {}".format(", ".join(list(OrderedDict.fromkeys(self.axises)))),
                  x + 50 * factor, y + 9 * factor, size=12, color=get_preferences().Hops_hud_text_color)

        self.draw_help(context, x, y, factor)


    def draw_help(self, context, x, y, factor):

        color_text1 = Hops_text_color()
        color_text2 = get_preferences().Hops_hud_help_color
        color_border = Hops_border_color()
        color_border2 = Hops_border2_color()

        if get_preferences().hops_modal_help:

            draw_text(" x - reset x axis",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)

            draw_text(" y - reset y axis",
                      x + 45 * factor, y - 26 * factor, size=11, color=color_text2)

            draw_text(" z - reset z axis",
                      x + 45 * factor, y - 38 * factor, size=11, color=color_text2)

            draw_text(" c - snap to cursor",
                      x + 45 * factor, y - 50 * factor, size=11, color=color_text2)

            draw_text(" shift+c - snap to cursor offset",
                      x + 45 * factor, y - 62 * factor, size=11, color=color_text2)

            draw_text(" press these consecutively to undo",
                      x + 45 * factor, y - 74 * factor, size=11, color=color_text2)

            draw_text(" scroll - change axis",
                      x + 45 * factor, y - 86 * factor, size=11, color=color_text2)

            draw_text(" H - Show/Hide Help",
                      x + 45 * factor, y - 98 * factor, size=11, color=color_text2)

        else:
            draw_text(" H - Show/Hide Help",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)