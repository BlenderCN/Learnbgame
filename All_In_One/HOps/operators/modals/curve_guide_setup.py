import bpy
from mathutils import Vector
from bpy.types import Operator
from bpy.props import IntProperty, FloatProperty
from ... utils.blender_ui import get_dpi, get_dpi_factor
from ... graphics.drawing2d import draw_text, set_drawing_dpi, draw_box
from ... preferences import Hops_text_color, Hops_text2_color, Hops_border_color, Hops_border2_color


deformtypes = ["Deform", "Twist", "Shear", "Scale", "Stretch"]


class HOPS_OT_CurveGuide(Operator):
    bl_idname = "mesh.curve_guide"
    bl_label = "Curve Guide"
    bl_description = "Preconfiguration for Mira Tools Curve Guide"
    bl_options = {"REGISTER", "GRAB_CURSOR", "BLOCKING"}

    first_mouse_x : IntProperty()
    first_value : FloatProperty()
    second_value : IntProperty()
    precision : IntProperty(default=50)

    def modal(self, context, event):
        curve = context.scene.mi_curguide_settings
        # offset_x = event.mouse_region_x - self.last_mouse_x

        if event.type == 'WHEELUPMOUSE':
            if curve.points_number < 12:
                curve.points_number += 1

        if event.type == 'WHEELDOWNMOUSE':
            if curve.points_number > 2:
                curve.points_number -= 1

        if event.mouse_region_x % self.precision == 0:
            if event.mouse_region_x > self.last_mouse_x:
                self.set_deformtype(curve)
            elif event.mouse_region_x < self.last_mouse_x:
                self.set_deformtype(curve, previous=True)

        if event.type in {'LEFTMOUSE', 'RET', 'NUMPAD_ENTER'}:
            bpy.ops.mira.curve_guide('INVOKE_DEFAULT')
            self.finish()
            return {"FINISHED"}

        if event.type in {'RIGHTMOUSE', 'ESC', 'BACK_SPACE'}:
            return {'CANCELLED'}

        self.last_mouse_x = event.mouse_region_x
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.last_mouse_x = event.mouse_region_x
        self.start_mouse_position = Vector((event.mouse_region_x, event.mouse_region_y))

        # args = (context, )
        # self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def finish(self):
        # bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
        return {"FINISHED"}

    def draw(self, context):
        x, y = self.start_mouse_position
        # first_value = self.first_value
        curve = context.scene.mi_curguide_settings

        set_drawing_dpi(get_dpi())
        factor = get_dpi_factor()
        color_text1 = Hops_text_color()
        color_text2 = Hops_text2_color()
        color_border = Hops_border_color()
        color_border2 = Hops_border2_color()

        draw_box(x - 14 * factor, y + 8 * factor, 34 * factor, 34 * factor, color=color_border2)

        draw_text("{:.0f}".format(curve.points_number), x - 6 * factor, y, size=23, color=color_text1)
        draw_text(bpy.context.scene.mi_curguide_settings.deform_type, x + 30 * factor, y, size=23, color=color_text1)

    def set_deformtype(self, curve, previous=False):
        currenttype = curve.deform_type
        currentidx = deformtypes.index(currenttype)

        if previous:
            if currenttype == deformtypes[0]:
                nexttype = deformtypes[-1]
            else:
                nexttype = deformtypes[currentidx + -1]
        else:
            if currenttype == deformtypes[-1]:
                nexttype = deformtypes[0]
            else:
                nexttype = deformtypes[currentidx + 1]

        curve.deform_type = nexttype
