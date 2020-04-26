import bpy
import os.path
from . import preferences
from . import file_utils


class StripsCreator(preferences.StripsCreatorPreferences):
    def create_strips(self, files):
        """ Creates strips for given files """
        frame_current = bpy.context.scene.frame_current
        previous_strip = None
        previous_transform_strip = None

        print("Total files to import: {}".format(len(files)))
        for file in files:
            (directory, file_name) = os.path.split(file)
            file_list = [{'name': file_name}]

            frame_start = frame_current
            current_transform_strip = None

            if file_utils.is_image(file):
                # Add image strip
                frame_end = frame_current + self.image_strip_frames
                bpy.ops.sequencer.image_strip_add(
                    directory=directory,
                    files=file_list,
                    frame_start=frame_start,
                    frame_end=frame_end)
                current_strip = bpy.context.selected_sequences[0]
                current_strip.blend_type = 'ALPHA_OVER'
                # Add transform strip
                current_transform_strip = self.create_transform_strip(strip=current_strip)
                current_strip.mute = True
                # Generate KenBurns effect on added transform strip if enabled
                if self.generate_ken_burns_effect:
                    bpy.ops.slideshow_composer.ken_burns_effect('EXEC_DEFAULT')
            elif file_utils.is_movie(file):
                # Add movie strip
                bpy.ops.sequencer.movie_strip_add(
                    filepath=file,
                    files=file_list,
                    frame_start=frame_start)
                current_strip = bpy.context.selected_sequences[0]
                # Add transform strip
                current_transform_strip = self.create_transform_strip(strip=current_strip)
                current_strip.mute = True
                # Apply scale on movie transform strip
                current_transform_strip.use_uniform_scale = True
                current_transform_strip.scale_start_x = self.movie_strips_scale
                frame_end = current_strip.frame_final_end

            # Create cross effect
            cross_first_strip = previous_strip
            cross_second_strip = current_strip
            if previous_transform_strip is not None:
                cross_first_strip = previous_transform_strip
            if current_transform_strip is not None:
                cross_second_strip = current_transform_strip
            if cross_first_strip is not None and cross_second_strip is not None:
                self.create_cross(
                    first_strip=cross_first_strip,
                    second_strip=cross_second_strip)

            frame_current = frame_end + 1 - self.strips_cross_frames
            previous_strip = current_strip
            previous_transform_strip = current_transform_strip
        return bpy.context.selected_sequences[0]

    def create_transform_strip(self, strip):
        # deselect all strips before adding transform strip - this is especially needed when adding transform effect
        # to movie clip that, once imported, creates two selected strips, one for movie and one for sound
        bpy.ops.sequencer.select_all(action="DESELECT")
        strip.select = True
        bpy.ops.sequencer.effect_strip_add(type='TRANSFORM')
        return bpy.context.selected_sequences[0]

    def create_cross(self, first_strip, second_strip):
        bpy.ops.sequencer.select_all(action="DESELECT")
        first_strip.select = True
        second_strip.select = True

        bpy.ops.sequencer.effect_strip_add(
            frame_start=second_strip.frame_start,
            frame_end=second_strip.frame_start + self.strips_cross_frames,
            type='CROSS'
        )