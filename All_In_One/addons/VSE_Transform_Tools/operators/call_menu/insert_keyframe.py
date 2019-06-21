import bpy


class PREV_OT_insert_keyframe(bpy.types.Operator):
    bl_idname = "vse_transform_tools.insert_keyframe"
    bl_label = "Transform Insert KeyFrame"
    bl_options = {'REGISTER', 'UNDO'}

    ch: bpy.props.IntVectorProperty(
        name="ch",
        default=(0, 0, 0, 0, 0),
        size=5
    )

    @classmethod
    def poll(cls, context):
        ret = False
        if context.scene.sequence_editor:
            ret = True
        return ret and context.space_data.type == 'SEQUENCE_EDITOR'

    def execute(self, context):
        for seq in context.scene.sequence_editor.sequences:
            if seq.select and seq.type == 'TRANSFORM':
                if self.ch[0] == 1:
                    seq.keyframe_insert(
                        data_path="translate_start_x")
                    seq.keyframe_insert(
                        data_path="translate_start_y")

                if self.ch[1] == 1:
                    seq.keyframe_insert(
                        data_path="rotation_start")

                if self.ch[2] == 1:
                    seq.keyframe_insert(
                        data_path="scale_start_x")
                    seq.keyframe_insert(
                        data_path="scale_start_y")

                if self.ch[3] == 1:
                    seq.keyframe_insert(
                        data_path="blend_alpha")

                if self.ch[4] == 1 and seq.input_1.use_crop:
                    seq.input_1.crop.keyframe_insert(
                        data_path="min_x")
                    seq.input_1.crop.keyframe_insert(
                        data_path="max_x")
                    seq.input_1.crop.keyframe_insert(
                        data_path="min_y")
                    seq.input_1.crop.keyframe_insert(
                        data_path="max_y")

            elif seq.select and not seq.type == "SOUND":
                if self.ch[0] == 1 and seq.use_translation:
                    seq.transform.keyframe_insert(data_path="offset_x")
                    seq.transform.keyframe_insert(data_path="offset_y")

                if self.ch[4] == 1 and seq.use_crop:
                    seq.transform.keyframe_insert(data_path="offset_x")
                    seq.transform.keyframe_insert(data_path="offset_y")

                    seq.crop.keyframe_insert(
                        data_path="min_x")
                    seq.crop.keyframe_insert(
                        data_path="max_x")
                    seq.crop.keyframe_insert(
                        data_path="min_y")
                    seq.crop.keyframe_insert(
                        data_path="max_y")

                if self.ch[3] == 1:
                    seq.keyframe_insert(
                        data_path="blend_alpha", frame=cf)

        # Apparently redrawing is bad...
        # bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        # https://docs.blender.org/api/blender_python_api_2_78_release/info_gotcha.html
        # So instead, we can update blender like this:
        scene = context.scene
        scrubbing = False
        if scene.use_audio_scrub:
            scrubbing = True
            scene.use_audio_scrub = False

        context.scene.frame_current += 1
        context.scene.frame_current -= 1

        if scrubbing:
            scene.use_audio_scrub = True

        return {'FINISHED'}
