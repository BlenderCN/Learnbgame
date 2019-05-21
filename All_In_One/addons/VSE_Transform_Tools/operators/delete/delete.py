import bpy
from ..utils.selection import get_input_tree


class PREV_OT_delete(bpy.types.Operator):
    """
    Deletes all selected strips as well as any strips that are inputs
    of those strips.
    For example, deleting a transform strip with this operator will
    also delete the strip it was transforming.
    """
    bl_idname = "vse_transform_tools.delete"
    bl_label = "Delete"
    bl_description = "Delete selected and their inputs recursively"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if (scene.sequence_editor and
           scene.sequence_editor.active_strip):
            return True
        return False

    def invoke(self, context, event):
        scene = context.scene
        selected = []

        for strip in context.selected_sequences:
            if strip not in selected:
                selected.extend(get_input_tree(strip))
        for strip in selected:
            strip.select = True

        delete_count = len(selected)

        dead_scenes = []
        if event.shift:
            for strip in selected:
                if strip.type == "SCENE":
                    for s in scene.sequence_editor.sequences_all:
                        if s.type == "SCENE" and s.scene == strip.scene:
                            s.select = True
                            delete_count += 1
                    dead_scenes.append(strip.scene)
                elif hasattr(strip, 'filepath'):
                    for s in scene.sequence_editor.sequences_all:
                        if hasattr(s, 'filepath') and s.filepath == strip.filepath:
                            s.select = True
                            delete_count += 1

        bpy.ops.sequencer.delete()

        for sce in dead_scenes:
            for obj in sce.objects:
                bpy.data.objects.remove(obj, True)
            bpy.data.scenes.remove(sce, True)

        selection_length = len(selected)
        report_message = ' '.join(
            ['Deleted', str(selection_length), 'sequence'])

        if selection_length > 1:
            report_message += 's'

        self.report({'INFO'}, report_message)

        return {"FINISHED"}
