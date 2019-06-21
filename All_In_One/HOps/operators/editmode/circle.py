import bpy
from bpy.props import *
from mathutils import Vector
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi, draw_box
from ... preferences import Hops_text_color, Hops_text2_color, Hops_border_color, Hops_border2_color, Hops_circle_size, get_preferences


class HOPS_OT_ModalCircle(bpy.types.Operator):
    bl_idname = "hops.circle"
    bl_label = "Hops Circle"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = "Make Circle form selected points"

    @classmethod
    def poll(cls, context):
        object = context.active_object
        return(object.type == 'MESH' and context.mode == 'EDIT_MESH')

    def invoke(self, context, event):

        self.subdivide = 1
        self.start_value = Hops_circle_size()
        self.offset = 0
        self.start_mouse_position = Vector((event.mouse_region_x, event.mouse_region_y))
        self.last_mouse_x = event.mouse_region_x

        if bpy.context.tool_settings.mesh_select_mode[2] and not bpy.context.tool_settings.mesh_select_mode[0]:
            bpy.ops.mesh.inset(thickness=0.01)
            bpy.ops.mesh.edge_face_add()
        else:
            bpy.ops.mesh.bevel(offset=0.29861, vertex_only=True)

        args = (context, )
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        divisor = 1000 if event.shift else 40 if event.ctrl else 230
        offset_x = event.mouse_region_x - self.last_mouse_x
        self.offset += offset_x / divisor / get_dpi_factor()
        self.radius = max((self.start_value - self.offset), 0.001)

        if event.type == "WHEELUPMOUSE" or event.type == 'NUMPAD_PLUS' and event.value == 'PRESS':
            if self.subdivide < 4:
                bpy.ops.mesh.subdivide(number_cuts=1, smoothness=0)
                bpy.ops.mesh.edge_face_add()
                self.subdivide += 1
        if event.type == "WHEELDOWNMOUSE" or event.type == 'NUMPAD_MINUS' and event.value == 'PRESS':
            pass

        # bpy.ops.mesh.looptools_circle(custom_radius=True, fit='best', flatten=True, influence=100, lock_x=False, lock_y=False, lock_z=False, radius=self.radius, regular=True)
        bpy.ops.mesh.looptools_circle(custom_radius=False, fit='inside', flatten=False, influence=100, lock_x=False, lock_y=False, lock_z=False, radius=self.radius, regular=True)

        if event.type in ("ESC", "RIGHTMOUSE"):
            bpy.ops.mesh.looptools_circle(custom_radius=True, fit='best', flatten=True, influence=100, lock_x=False, lock_y=False, lock_z=False, radius=Hops_circle_size(), regular=True)
            return self.finish()

        if event.type in ("SPACE", "LEFTMOUSE"):
            get_preferences().Hops_circle_size = self.radius
            return self.finish()

        self.last_mouse_x = event.mouse_region_x
        context.area.tag_redraw()
        return {"RUNNING_MODAL"}

    def finish(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
        return {"FINISHED"}

    def draw(self, context):
        x, y = self.start_mouse_position
        value = self.radius
        subdivide = self.subdivide - 1

        set_drawing_dpi(get_dpi())
        factor = get_dpi_factor()
        color_text1 = Hops_text_color()
        color_text2 = Hops_text2_color()
        color_border = Hops_border_color()
        color_border2 = Hops_border2_color()

        draw_box(x - 8 * factor, y + 8 * factor, 204 * factor, 34 * factor, color=color_border2)

        draw_box(x + 45 * factor, y + 8 * factor, 150 * factor, 30 * factor, color=color_border)

        draw_text(" {:.0f} subd ".format(subdivide), x + 50 * factor, y, size=16, color=color_text1)
        # else:
        # draw_text(str(bevel.segments), x + 3 * factor, y, size = 23, color = color_text1)

        draw_text(" {:.2f}  ".format(value),
                  x - 8 * factor, y, size=20, color=color_text2)

        # this never worked anyway, do we need it ?
        '''draw_text(self.get_description_text(), x + 24 * factor, y - 28 * factor,
                                          size = 12, color = color)'''
