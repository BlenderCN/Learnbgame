import bpy
from mathutils import Vector
import math

from ..utils.geometry import  mouse_to_res

class PREV_OT_mouse_track(bpy.types.Operator):
    """
    Track mouse position and apply as keyframes to a transform modifier
    """
    bl_idname = "vse_transform_tools.mouse_track"
    bl_label = "Mouse Track"
    bl_description = "Track mouse position and apply as keyframes to a transform modifier"
    bl_options = {'REGISTER', 'UNDO', 'GRAB_CURSOR', 'BLOCKING'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        strip = scene.sequence_editor.active_strip
        if (scene.sequence_editor and strip):
            if strip.type == "TRANSFORM":
                return True
            elif strip.use_translation:
                return True
        return False

    def modal(self, context, event):
        scene = context.scene
        fps = scene.render.fps / scene.render.fps_base
        fc = scene.frame_current
        cushion = fc + math.ceil(fps / 2)

        strip = scene.sequence_editor.active_strip

        res_x = scene.render.resolution_x
        res_y = scene.render.resolution_y

        mouse_x = event.mouse_region_x
        mouse_y = event.mouse_region_y

        mouse_vec = Vector([mouse_x, mouse_y])
        mouse_pos = mouse_to_res(mouse_vec)

        if strip.type == "TRANSFORM":
            x = mouse_pos.x - (res_x / 2)
            y = mouse_pos.y - (res_y / 2)

            if strip.translation_unit == 'PERCENT':
                x = ((mouse_pos.x * 100) / res_x) - 50
                y = ((mouse_pos.y * 100) / res_y) - 50

            strip.translate_start_x = x
            strip.translate_start_y = y

            for i in range(fc, cushion):
                try:
                    strip.keyframe_delete('translate_start_x', frame=i)
                    strip.keyframe_delete('translate_start_y', frame=i)
                except RuntimeError:
                    pass

            strip.keyframe_insert(
                data_path="translate_start_x")
            strip.keyframe_insert(
                data_path="translate_start_y")

        else:
            strip.transform.offset_x = mouse_pos.x
            strip.transform.offset_y = mouse_pos.y

            for i in range(fc, cushion):
                try:
                    strip.transform.keyframe_delete('offset_x', frame=i)
                    strip.transform.keyframe_delete('offset_y', frame=i)
                except RuntimeError:
                    pass

            strip.transform.keyframe_insert(
                data_path="offset_x")
            strip.transform.keyframe_insert(
                data_path="offset_y")

        if event.type == 'M' and event.value == 'RELEASE':
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.initial_frame = context.scene.frame_current
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
