import bpy
from mathutils import Vector
from ... import M3utils as m3
from ... utils.blender_ui import get_dpi_factor
from ... utils.drawing_2d import draw_text


class AdjustHeight(bpy.types.Operator):
    bl_idname = "machin3.decal_adjust_height"
    bl_label = "Adjust Decal Height"
    bl_options = {"REGISTER", "UNDO", "GRAB_CURSOR", "BLOCKING"}
    bl_description = "Change Height values for decals"

    @classmethod
    def poll(cls, context):
        return getattr(context.active_object, "type", "") == "MESH"

    def invoke(self, context, event):
        self.object = context.active_object
        self.displace = self.get_displace_mod()
        self.start_mouse_position = Vector((event.mouse_region_x, event.mouse_region_y))
        self.start_displace_mid_level = self.displace.mid_level
        self.offset = 0
        self.last_mouse_x = event.mouse_region_x

        if m3.DM_prefs().consistantscale:
            self.scene_scale = m3.get_scene_scale()
        else:
            self.scene_scale = 1

        self.midlevel = 1 - (0.0001 / self.scene_scale)  # 0.9999 for scene scale of 1.0

        args = (context, )
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw, args, "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def get_displace_mod(self):
        active = bpy.context.active_object

        for mod in active.modifiers:
            if "displace" in mod.name.lower():
                displace_modifier = mod

        return displace_modifier

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            if event.shift:
                divisor = 1000000 * self.scene_scale
            elif event.ctrl:
                divisor = 1000 * self.scene_scale
            else:
                divisor = 100000 * self.scene_scale
            offset_x = event.mouse_region_x - self.last_mouse_x
            self.offset -= offset_x / divisor / get_dpi_factor()
            self.displace.mid_level = self.start_displace_mid_level - self.offset

        elif event.type is ("C"):
            if event.value == 'PRESS':
                # self.displace.mid_level = 0.9989
                self.displace.mid_level = self.midlevel - (0.001 / self.scene_scale)
                self.offset = 0

        elif event.type is ("X"):
            if event.value == 'PRESS':
                # self.displace.mid_level = 0.9999
                self.displace.mid_level = self.midlevel
                self.offset = 0

        elif event.type is ("Y"):
            if event.value == 'PRESS':
                self.displace.mid_level = self.start_displace_mid_level
                self.offset = 0

        elif event.type in ("ESC", "RIGHTMOUSE"):
            self.reset_object()
            return self.finish(context)

        elif event.type in ("SPACE", "LEFTMOUSE"):
            return self.finish(context)

        self.last_mouse_x = event.mouse_region_x
        context.area.tag_redraw()
        return {"RUNNING_MODAL"}

    def reset_object(self):
        self.displace.mid_level = self.start_displace_mid_level

    def finish(self, context):
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
        context.area.tag_redraw()
        return {"FINISHED"}

    def draw(self, context):
        x, y = self.start_mouse_position

        # draw_text("Decal Height:   {:.4f}".format(-(self.displace.mid_level - 0.9999) * 1000), x, y, size=16, color=(1, 1, 1, 1))
        draw_text("Decal Height:   {:.4f}".format(-(self.displace.mid_level - self.midlevel) * 1000 * self.scene_scale), x, y, size=16, color=(1, 1, 1, 1))
        draw_text("Press Y to reset to start value, press X to reset to 0, press C to reset to 1", x, y - 20, size=11, color=(1, 1, 1, 1))
        draw_text("Hold SHIFT for finer control, hold CTRL for bigger steps ", x, y - 33, size=11, color=(1, 1, 1, 1))
