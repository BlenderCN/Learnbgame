import bpy
import gpu
from bgl import *
from gpu_extras.batch import batch_for_shader
from bpy.props import BoolProperty
from mathutils import Vector
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi, draw_box
from ... preferences import Hops_text_color, Hops_text2_color, Hops_border_color, Hops_border2_color, get_preferences


class HOPS_OT_AdjustArrayOperator(bpy.types.Operator):
    bl_idname = "hops.adjust_array"
    bl_label = "Adjust Array"
    bl_description = "Adds an array on the mesh. Supports multiple modifiers. Press H for help"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}

    x: BoolProperty(name="X Axis",
                    description="X Axis",
                    default=True)
    y: BoolProperty(name="Y Axis",
                    description="Y Axis",
                    default=False)
    z: BoolProperty(name="Z Axis",
                    description="Z Axis",
                    default=False)

    is_relative: BoolProperty(name="Is relative",
                              description="Is relatives",
                              default=True)

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def invoke(self, context, event):
        self.modal_scale = get_preferences().Hops_modal_scale
        self.objects = [obj for obj in context.selected_objects if obj.type == "MESH"]

        if get_preferences().force_array_apply_scale_on_init:
            for obj in self.objects:
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        self.arrays = {}
        self.get_array_modifier("Array")
        self.start_mouse_position = Vector((event.mouse_region_x, event.mouse_region_y))
        self.using_array = "Array"
        self.new_dir = "X"

        for obj in self.arrays:
            mods = self.arrays[obj]["arrays"]
            for mod in mods:
                relative = self.arrays[obj]["start_array_relative_offset_displace"]
                constant = self.arrays[obj]["start_array_constant_offset_displace"]
                if not relative:
                    self.arrays[obj]["start_array_count"] = mod.count
                    relative.update({mod.name: [i for i in mod.relative_offset_displace]})
                    constant.update({mod.name: [i for i in mod.constant_offset_displace]})

        self.offset_x = 0
        self.offset_y = 0
        self.offset_z = 0
        self.last_mouse_x = event.mouse_region_x

        if get_preferences().force_array_reset_on_init:
            for obj in self.arrays:
                mods = self.arrays[obj]["arrays"]
                for mod in mods:
                    mod.relative_offset_displace = [0, 0, 0]
                    mod.constant_offset_displace = [0, 0, 0]

        self.set_init_constant = False
        if len(self.objects) > 1:
            self.set_init_constant = True

        args = (context, )
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_ui, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def get_array_modifier(self, name):  # create or get array modifier on all selected objects.
        objects = self.objects  # [obj for bpy.context.active_object
        for count, obj in enumerate(objects):
            if obj not in self.arrays:
                self.arrays.update({obj: {"arrays": [], "start_array_relative_offset_displace": {}, "start_array_constant_offset_displace": {}, "created_array_modifier": False, "start_array_count": 2}})
            mods = obj.modifiers
            if name in mods:
                if obj.modifiers[name] not in self.arrays[obj]["arrays"]:
                    self.arrays[obj]["arrays"].append(obj.modifiers[name])
            else:#if did not get one this iteration, create it
                array_modifier = obj.modifiers.new(name, "ARRAY")
                self.array = array_modifier
                self.arrays[obj]["arrays"].append(array_modifier)
                array_modifier.count = 2
                array_modifier.relative_offset_displace = [1, 0, 0]
                relative = self.arrays[obj]["start_array_relative_offset_displace"]
                relative.update({self.array.name: [i for i in self.array.relative_offset_displace]})
                constant = self.arrays[obj]["start_array_constant_offset_displace"]
                constant.update({self.array.name: [i for i in self.array.constant_offset_displace]})
                self.arrays[obj]["created_array_modifier"] = True

    def modal(self, context, event):
        divisor = 1200 * self.modal_scale if event.shift else 10000000 if event.ctrl else 150 * self.modal_scale
        offset_x = event.mouse_region_x - self.last_mouse_x
        self.offset_x -= offset_x / divisor / get_dpi_factor()
        offset_y = event.mouse_region_x - self.last_mouse_x
        self.offset_y -= offset_y / divisor / get_dpi_factor()
        offset_z = event.mouse_region_x - self.last_mouse_x
        self.offset_z -= offset_z / divisor / get_dpi_factor()

        for obj in self.arrays:
            mods = self.arrays[obj]["arrays"]
            for mod in mods:
                self.array = mod

                relative = self.arrays[obj]["start_array_relative_offset_displace"]
                constant = self.arrays[obj]["start_array_constant_offset_displace"]

                if self.array.name == self.using_array:

                    if self.is_relative:
                        if mod.name in relative:
                            if self.x:
                                self.array.relative_offset_displace[0] = float("{:.2f}".format(relative[mod.name][0] - self.offset_x))

                            if self.y:
                                self.array.relative_offset_displace[1] = float("{:.2f}".format(relative[mod.name][1] - self.offset_y))

                            if self.z:
                                self.array.relative_offset_displace[2] = float("{:.2f}".format(relative[mod.name][2] - self.offset_z))
                    else:
                        if mod.name in constant:
                            if self.x:
                                self.array.constant_offset_displace[0] = float("{:.2f}".format(constant[mod.name][0] - self.offset_x))

                            if self.y:
                                self.array.constant_offset_displace[1] = float("{:.2f}".format(constant[mod.name][1] - self.offset_y))

                            if self.z:
                                self.array.constant_offset_displace[2] = float("{:.2f}".format(constant[mod.name][2] - self.offset_z))


                    if event.type == "X" and event.value == "PRESS" or self.new_dir == "X":
                        if event.shift:
                            self.x = not self.x
                        else:
                            if self.is_relative:
                                self.array.relative_offset_displace = [1, 0, 0]
                                self.offset_x = 0
                            else:
                                self.array.constant_offset_displace = [0, 0, 0]
                                self.offset_x = 0
                            self.x = True
                            self.y = False
                            self.z = False

                    if event.type == "Y" and event.value == "PRESS" or self.new_dir == "Y":
                        if event.shift:
                            self.y = not self.y
                        else:
                            if self.is_relative:
                                self.array.relative_offset_displace = [0, 1, 0]
                                self.offset_y = -1
                            else:
                                self.array.constant_offset_displace = [0, 0, 0]
                                self.offset_y = 0
                            self.x = False
                            self.y = True
                            self.z = False

                    if event.type == "Z" and event.value == "PRESS" or self.new_dir == "Z":
                        if event.shift:
                            self.z = not self.z
                        else:
                            if self.is_relative:
                                self.array.relative_offset_displace = [0, 0, 1]
                                self.offset_z = -1
                            else:
                                self.array.constant_offset_displace = [0, 0, 0]
                                self.offset_z = 0
                            self.x = False
                            self.y = False
                            self.z = True

                    if event.type == "WHEELUPMOUSE" or event.type == "NUMPAD_PLUS" and event.value == "PRESS":
                        self.array.count += 1
                    if event.type == "WHEELDOWNMOUSE" or event.type == "NUMPAD_MINUS" and event.value == "PRESS":
                        self.array.count -= 1

                    if event.type == "C" and event.value == "PRESS" or self.set_init_constant:
                        self.array.use_constant_offset = True
                        self.array.use_relative_offset = False
                        self.is_relative = False
                        self.array.constant_offset_displace = [0, 0, 0]

                    if event.type == "R" and event.value == "PRESS":
                        self.array.use_constant_offset = False
                        self.array.use_relative_offset = True
                        self.is_relative = True
                        self.array.relative_offset_displace = [1, 0, 0]

        self.set_init_constant = False
        self.new_dir = ""

        if event.type == "ONE" and event.value == "PRESS":
            self.get_array_modifier("Array")
            self.offset_x = 0
            self.offset_y = 0
            self.offset_z = 0
            self.set_init_constant = True
            self.using_array = "Array"
            self.new_dir = "X"

        if event.type == "TWO" and event.value == "PRESS":
            self.get_array_modifier("Array1")
            self.offset_x = 0
            self.offset_y = 0
            self.offset_z = 0
            self.set_init_constant = True
            self.using_array = "Array1"
            self.new_dir = "Y"

        if event.type == "THREE" and event.value == "PRESS":
            self.get_array_modifier("Array2")
            self.offset_x = 0
            self.offset_y = 0
            self.offset_z = 0
            self.set_init_constant = True
            self.using_array = "Array2"
            self.new_dir = "Z"

        if event.type == "S" and event.value == "PRESS":
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

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
        for obj in self.arrays:
            mods = self.arrays[obj]["arrays"]
            for mod in mods:
                self.array = mod
                self.array.count = self.arrays[obj]["start_array_count"]
                self.array.relative_offset_displace = self.arrays[obj]["start_array_relative_offset_displace"][mod.name]
                self.array.constant_offset_displace = self.arrays[obj]["start_array_constant_offset_displace"][mod.name]
                if self.arrays[obj]["created_array_modifier"]:
                    if self.array.name in obj.modifiers:
                        obj.modifiers.remove(self.array)

    def finish(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
        return {"FINISHED"}

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
            (x + 46 * factor, y + 23 * factor), (x + 46 * factor, y + 4 * factor), (x + 220 * factor, y + 23 * factor), (x + 220 * factor, y + 4 * factor),
            (x + 46 * factor, y + 42 * factor), (x + 46 * factor, y + 26 * factor), (x + 220 * factor, y + 42 * factor), (x + 220 * factor, y + 26 * factor))

        indices = (
            (0, 1, 2), (1, 2, 3), (4, 5, 6), (5, 6, 7), (8, 9, 10), (9, 10, 11))

        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)

        shader.bind()
        shader.uniform_float("color", (0.17, 0.17, 0.17, 1))
        glEnable(GL_BLEND)
        batch.draw(shader)
        glDisable(GL_BLEND)

        self.array = self.objects[0].modifiers[self.using_array]
        relative = self.array.relative_offset_displace
        constant = self.array.constant_offset_displace

        draw_text(str(self.array.count),
                  x + 27 * factor, y + 9 * factor, size=12, color=(0.831, 0.831, 0.831, 1))

        draw_text("  X: {:.3f}  Y: {:.3f}  Z: {:.3f} ".format(relative[0], relative[1], relative[2]),
                  x + 50 * factor, y + 9 * factor, size=12, color=(0.831, 0.831, 0.831, 1))

        draw_text("  X: {:.3f}  Y: {:.3f}  Z: {:.3f} ".format(constant[0], constant[1], constant[2]),
                  x + 50 * factor, y + 28 * factor, size=12, color=(0.831, 0.831, 0.831, 1))

        self.draw_help(context, x, y, factor)

    def draw(self, context):
        x, y = self.start_mouse_position

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

        if self.array.count >= 10:
            draw_text(str(self.array.count), x - 8 * factor, y, size=23, color=color_text1)
        else:
            draw_text(str(self.array.count), x + 3 * factor, y, size=23, color=color_text1)

        self.array = self.objects[0].modifiers[self.using_array]
        relative = self.array.relative_offset_displace
        constant = self.array.constant_offset_displace

        draw_text("  X: {:.3f}  Y: {:.3f}  Z: {:.3f} ".format(relative[0], relative[1], relative[2]),
                  x + 22 * factor, y + 10 * factor, size=12, color=color_text2)

        draw_text("  X: {:.3f}  Y: {:.3f}  Z: {:.3f} ".format(constant[0], constant[1], constant[2]),
                  x + 22 * factor, y - 3 * factor, size=12, color=color_text2)

        if get_preferences().hops_modal_help:
            self.draw_help(context, x, y, factor)

    def draw_help(self, context, x, y, factor):

        # color_text1 = Hops_text_color()
        color_text2 = Hops_text2_color()
        # color_border = Hops_border_color()
        # color_border2 = Hops_border2_color()

        if get_preferences().hops_modal_help:

            draw_text(" x - set x axis",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)

            draw_text(" y - set y axis",
                      x + 45 * factor, y - 26 * factor, size=11, color=color_text2)

            draw_text(" z - set z axis",
                      x + 45 * factor, y - 38 * factor, size=11, color=color_text2)

            draw_text(" shift+x - on/off x axis",
                      x + 45 * factor, y - 50 * factor, size=11, color=color_text2)

            draw_text(" shift+y - on/off y axis",
                      x + 45 * factor, y - 62 * factor, size=11, color=color_text2)

            draw_text(" shift+z - on/off z axis",
                      x + 45 * factor, y - 74 * factor, size=11, color=color_text2)

            draw_text(" scroll - change array count",
                      x + 45 * factor, y - 86 * factor, size=11, color=color_text2)

            draw_text(" R - use relative offset",
                      x + 45 * factor, y - 98 * factor, size=11, color=color_text2)

            draw_text(" C - use constant offset",
                      x + 45 * factor, y - 110 * factor, size=11, color=color_text2)

            draw_text(" 1 - jump to 1st modifier",
                      x + 45 * factor, y - 122 * factor, size=11, color=color_text2)

            draw_text(" 2 - create/jump to 2nd modifier",
                      x + 45 * factor, y - 134 * factor, size=11, color=color_text2)

            draw_text(" 3 - create/jump to 3rd modifier",
                      x + 45 * factor, y - 146 * factor, size=11, color=color_text2)

            draw_text(" s - apply scale",
                      x + 45 * factor, y - 158 * factor, size=11, color=color_text2)

        else:
            draw_text(" H - Show/Hide Help",
                      x + 45 * factor, y - 14 * factor, size=11, color=color_text2)
