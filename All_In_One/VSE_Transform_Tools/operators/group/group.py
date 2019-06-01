import bpy

from ..utils.geometry import get_group_box
from ..utils.selection import get_input_tree

class PREV_OT_group(bpy.types.Operator):
    bl_idname = "vse_transform_tools.group"
    bl_label = "Group"
    bl_description = "Group VSE Strips together"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if (scene.sequence_editor and len(context.selected_sequences) > 0):
            return True
        return False

    def invoke(self, context, event):
        if event.alt:
            bpy.ops.sequencer.meta_separate()
            return {"FINISHED"}

        selected = context.selected_sequences

        for strip in selected:
            tree = get_input_tree(strip)
            for child in tree:
                child.select = True
                if not child in selected:
                    selected.append(child)

        left, right, bottom, top = get_group_box(selected)

        res_x = context.scene.render.resolution_x
        res_y = context.scene.render.resolution_y

        bpy.ops.sequencer.meta_make()

        active = context.scene.sequence_editor.active_strip
        active.use_translation = True
        active.blend_type = "ALPHA_OVER"

        if not (left == right == bottom == top == 0):
            active.use_crop = True
            active.crop.min_x = left
            active.crop.max_x = res_x - right

            active.crop.min_y = bottom
            active.crop.max_y = res_y - top

            active.transform.offset_x = left
            active.transform.offset_y = bottom


        return {"FINISHED"}
