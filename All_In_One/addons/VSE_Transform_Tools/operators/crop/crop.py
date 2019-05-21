import bpy
import copy

import math
from mathutils import Vector
from mathutils.geometry import intersect_point_quad_2d

from ..utils.geometry import get_preview_offset
from ..utils.geometry import rotate_point

from ..utils.selection import get_highest_transform

from .draw_crop import draw_crop
from .crop_scale import crop_scale


class PREV_OT_crop(bpy.types.Operator):
    """
    Crop the active strip
    """
    bl_idname = "vse_transform_tools.crop"
    bl_label = "Crop"
    bl_description = "Crop a strip in the Image Preview"
    bl_options = {'REGISTER', 'UNDO'}

    init_pos_x = 0
    init_pos_y = 0

    mouse_pos = Vector([-1, -1])
    current_mouse = Vector([-1, -1])

    corners = [Vector([-1, -1]), Vector([-1, -1]), Vector([-1, -1]),
               Vector([-1, -1])]
    max_corners = [Vector([-1, -1]), Vector([-1, -1]), Vector([-1, -1]),
                   Vector([-1, -1])]
    corner_quads = []

    clicked_quad = None

    handle_crop = None

    crop_left = 0
    crop_right = 0
    crop_bottom = 0
    crop_top = 0

    scale_factor_x = 1.0
    scale_factor_y = 1.0

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if (scene.sequence_editor and
           scene.sequence_editor.active_strip and
           scene.sequence_editor.active_strip.select):
            return True
        return False


    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            mouse_x = event.mouse_region_x
            mouse_y = event.mouse_region_y

            self.mouse_pos = Vector([mouse_x, mouse_y])
            self.current_mouse = Vector([mouse_x, mouse_y])

            for i in range(len(self.corner_quads)):
                quad = self.corner_quads[i]

                bl = quad[0]
                tl = quad[1]
                tr = quad[2]
                br = quad[3]

                intersects = intersect_point_quad_2d(
                    self.mouse_pos, bl, tl, tr, br)

                if intersects:
                    self.clicked_quad = i

        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            offset_x, offset_y, fac, preview_zoom = get_preview_offset()

            active_strip = context.scene.sequence_editor.active_strip
            if active_strip.type == "TRANSFORM":
                angle = math.radians(active_strip.rotation_start)
            else:
                angle = 0

            origin = self.max_corners[2] - self.max_corners[0]

            bl = rotate_point(self.max_corners[0], -angle, origin)
            tl = rotate_point(self.max_corners[1], -angle, origin)
            tr = rotate_point(self.max_corners[2], -angle, origin)
            br = rotate_point(self.max_corners[3], -angle, origin)

            bl_current = rotate_point(self.corners[0], -angle, origin)
            tl_current = rotate_point(self.corners[1], -angle, origin)
            tr_current = rotate_point(self.corners[2], -angle, origin)
            br_current = rotate_point(self.corners[3], -angle, origin)

            if self.clicked_quad is not None:
                for i in range(len(self.corners)):
                    if i == 0:
                        self.crop_left = bl_current.x - bl.x
                        self.crop_left /= preview_zoom * fac

                        self.crop_bottom = bl_current.y - bl.y
                        self.crop_bottom /= preview_zoom * fac
                    elif i == 1:
                        self.crop_left = tl_current.x - tl.x
                        self.crop_left /= preview_zoom * fac

                        self.crop_top = tl.y - tl_current.y
                        self.crop_top /= preview_zoom * fac

                    elif i == 2:
                        self.crop_right = tr.x - tr_current.x
                        self.crop_right /= preview_zoom * fac

                        self.crop_top = tr.y - tr_current.y
                        self.crop_top /= preview_zoom * fac

                    elif i == 3:
                        self.crop_right = br.x - br_current.x
                        self.crop_right /= preview_zoom * fac

                        self.crop_bottom = br_current.y - br.y
                        self.crop_bottom /= preview_zoom * fac

            self.clicked_quad = None
            self.mouse_pos = Vector([-1, -1])

        elif event.type == 'MOUSEMOVE' and self.clicked_quad is not None:
            mouse_x = event.mouse_region_x
            mouse_y = event.mouse_region_y
            self.current_mouse = Vector([mouse_x, mouse_y])

        elif event.type in ['MIDDLEMOUSE', 'WHEELDOWNMOUSE',
                            'WHEELUPMOUSE', 'RIGHT_ARROW', 'LEFT_ARROW']:
            return {'PASS_THROUGH'}

        elif event.type in ['C', 'RET', 'NUMPAD_ENTER'] and event.value == 'PRESS':
            offset_x, offset_y, fac, preview_zoom = get_preview_offset()

            active_strip = context.scene.sequence_editor.active_strip
            crops = [self.crop_left / self.scale_factor_x,
                     self.crop_right / self.scale_factor_x,
                     self.crop_bottom / self.scale_factor_y,
                     self.crop_top / self.scale_factor_y,
                     ]

            scene = context.scene

            if active_strip.type == "TRANSFORM":
                crop_scale(self, active_strip, crops)

                strip_in = active_strip.input_1

                if scene.tool_settings.use_keyframe_insert_auto:
                    cf = context.scene.frame_current
                    active_strip.keyframe_insert(data_path='translate_start_x')
                    active_strip.keyframe_insert(data_path='translate_start_y')
                    active_strip.keyframe_insert(data_path='scale_start_x')
                    active_strip.keyframe_insert(data_path='scale_start_y')

                    strip_in.crop.keyframe_insert(data_path='min_x')
                    strip_in.crop.keyframe_insert(data_path='max_x')
                    strip_in.crop.keyframe_insert(data_path='min_y')
                    strip_in.crop.keyframe_insert(data_path='max_y')

            else:
                active_strip.use_crop = True
                active_strip.crop.min_x = crops[0]
                active_strip.crop.max_x = crops[1]
                active_strip.crop.min_y = crops[2]
                active_strip.crop.max_y = crops[3]

                active_strip.transform.offset_x = self.init_pos_x - self.init_crop_left + crops[0]
                active_strip.transform.offset_y = self.init_pos_y - self.init_crop_bottom + crops[2]

                if scene.tool_settings.use_keyframe_insert_auto:
                    active_strip.crop.keyframe_insert(data_path='min_x')
                    active_strip.crop.keyframe_insert(data_path='max_x')
                    active_strip.crop.keyframe_insert(data_path='min_y')
                    active_strip.crop.keyframe_insert(data_path='max_y')

                    active_strip.transform.keyframe_insert(data_path="offset_x")
                    active_strip.transform.keyframe_insert(data_path="offset_y")

            bpy.types.SpaceSequenceEditor.draw_handler_remove(
                self.handle_crop, 'PREVIEW')
            return {'FINISHED'}

        elif (event.alt and event.type == 'C') or event.type == 'ESC':
            active_strip = context.scene.sequence_editor.active_strip
            crops = [self.init_crop_left, self.init_crop_right,
                     self.init_crop_bottom, self.init_crop_top]

            if active_strip.type == "TRANSFORM":
                crop_scale(self, active_strip, crops)

            else:
                active_strip.use_crop = True
                active_strip.crop.min_x = crops[0]
                active_strip.crop.max_x = crops[1]
                active_strip.crop.min_y = crops[2]
                active_strip.crop.max_y = crops[3]

                active_strip.transform.offset_x = crops[0]
                active_strip.transform.offset_y = crops[2]

            bpy.types.SpaceSequenceEditor.draw_handler_remove(
                self.handle_crop, 'PREVIEW')
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        scene = context.scene

        res_x = scene.render.resolution_x
        res_y = scene.render.resolution_y

        strip = get_highest_transform(scene.sequence_editor.active_strip)
        scene.sequence_editor.active_strip = strip

        if not strip.type == "TRANSFORM" and not strip.use_translation:
            bpy.ops.vse_transform_tools.add_transform()
            strip.select = False
            strip = scene.sequence_editor.active_strip

        elif not strip.type == "TRANSFORM" and strip.use_translation:

            strip.use_translation = True
            strip.use_crop = True

            self.init_crop_left = strip.crop.min_x
            self.init_crop_right = strip.crop.max_x
            self.init_crop_bottom = strip.crop.min_y
            self.init_crop_top = strip.crop.max_y

            self.init_pos_x = strip.transform.offset_x
            self.init_pos_y = strip.transform.offset_y

            self.crop_left = strip.crop.min_x
            self.crop_right = strip.crop.max_x
            self.crop_bottom = strip.crop.min_y
            self.crop_top = strip.crop.max_y

            strip.crop.min_x = 0
            strip.crop.max_x = 0
            strip.crop.min_y = 0
            strip.crop.max_y = 0

            strip.transform.offset_x -= self.init_crop_left
            strip.transform.offset_y -= self.init_crop_bottom

            if event.alt:
                return {'FINISHED'}

        if strip.type == "TRANSFORM":
            strip_in = strip.input_1

            if not strip_in.use_crop:
                strip_in.use_crop = True

                strip_in.crop.min_x = 0
                strip_in.crop.max_x = 0
                strip_in.crop.min_y = 0
                strip_in.crop.max_y = 0

            if event.alt:
                crop_scale(self, strip, [0, 0, 0, 0])
                return {'FINISHED'}

            crop_scale(self, strip, [0, 0, 0, 0])

        args = (self, context)
        self.handle_crop = bpy.types.SpaceSequenceEditor.draw_handler_add(
            draw_crop, args, 'PREVIEW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}
