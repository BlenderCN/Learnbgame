import bpy
import random
from . import preferences
from . import keyframes

class KenBurnsEffect(bpy.types.Operator, preferences.KenBurnsEffectPreferences):
    bl_idname = "slideshow_composer.ken_burns_effect"
    bl_label = "Ken Burns Effect"
    bl_description = "Generate random Ken Burns effect on image transform strips"
    bl_options = {'REGISTER', 'UNDO'}

    replace = bpy.props.BoolProperty(
        name="Replace existing sequence effect",
        description="Remove previous sequence effect and generate new one",
        default=False
    )

    class Animator:
        def __init__(self, sequence, value, reverse=False):
            self.sequence = sequence
            self.value = value
            self.reverse = reverse

        def get_data_path(self):
            raise NotImplementedError("Override and return data_path")

        def set_up_first_keyframe(self):
            raise NotImplementedError("Override and set appropriate property's value before creating a keyframe")

        def set_up_second_keyframe(self):
            raise NotImplementedError("Override and set appropriate property's value before creating a keyframe")

        def get_required_scale(self):
            return 1.0

        def generate(self):
            data_path = self.get_data_path()

            if self.reverse:
                self.set_up_second_keyframe()
            else:
                self.set_up_first_keyframe()
            self.create_keyframe(data_path=data_path, frame=self.sequence.frame_start)

            if self.reverse:
                self.set_up_first_keyframe()
            else:
                self.set_up_second_keyframe()
            seq_last_frame = self.sequence.frame_start + self.sequence.frame_duration - 1
            self.create_keyframe(data_path=data_path, frame=seq_last_frame)

        def create_keyframe(self, data_path, frame):
            self.sequence.keyframe_insert(data_path=data_path, frame=frame, group=KenBurnsEffect.get_fcurves_group_name())
            # last added fcurve's keyframe_points interpolation
            bpy.context.scene.animation_data.action.fcurves[-1].keyframe_points[0].interpolation = "LINEAR"

    class ScaleAnimator(Animator):
        initial_scale = None

        def get_data_path(self):
            return 'scale_start_x'

        def set_up_first_keyframe(self):
            self.store_initial_scale()
            self.sequence.scale_start_x = self.initial_scale

        def store_initial_scale(self):
            # scale can also be modified by other animators, eg. translation
            # where some scale has to be applied to not let the image
            # go out of its bounds during move animation. That's why scale
            # animation cannot just set the scale value but has to take into
            # account the initial value set by other animators
            if self.initial_scale is None:
                self.initial_scale = self.sequence.scale_start_x

        def set_up_second_keyframe(self):
            self.store_initial_scale()
            self.sequence.scale_start_x = self.initial_scale + self.value

        @staticmethod
        def create_random(preferences, sequence):
            return KenBurnsEffect.ScaleAnimator(
                sequence,
                value = generate_random_float(
                    preferences.ken_burns_transformation_scale_value,
                    preferences.ken_burns_transformation_scale_value_max_deviation),
                reverse = generate_random_bool())

    class TranslateXAnimator(Animator):
        def get_data_path(self):
            return 'translate_start_x'

        def get_required_scale(self):
            return 1.0 + self.value / 100

        def set_up_first_keyframe(self):
            self.sequence.translate_start_x = -self.value / 2

        def set_up_second_keyframe(self):
            self.sequence.translate_start_x = self.value / 2

        @staticmethod
        def create_random(preferences, sequence):
            return KenBurnsEffect.TranslateXAnimator(
                sequence,
                value=generate_random_float(
                    preferences.ken_burns_transformation_x_value,
                    preferences.ken_burns_transformation_x_value_max_deviation),
                reverse=generate_random_bool())

    class TranslateYAnimator(Animator):
        def get_data_path(self):
            return 'translate_start_y'

        def get_required_scale(self):
            return 1.0 + self.value / 100

        def set_up_first_keyframe(self):
            self.sequence.translate_start_y = -self.value / 2

        def set_up_second_keyframe(self):
            self.sequence.translate_start_y = self.value / 2

        @staticmethod
        def create_random(preferences, sequence):
            return KenBurnsEffect.TranslateYAnimator(
                sequence,
                value=generate_random_float(
                    preferences.ken_burns_transformation_y_value,
                    preferences.ken_burns_transformation_y_value_max_deviation),
                reverse=generate_random_bool())

    class RotateAnimator(Animator):
        def get_data_path(self):
            return 'rotation_start'

        def get_required_scale(self):
            return 1.2

        def set_up_first_keyframe(self):
            self.sequence.rotation_start = -self.value / 2

        def set_up_second_keyframe(self):
            self.sequence.rotation_start = self.value / 2

        @staticmethod
        def create_random(preferences, sequence):
            return KenBurnsEffect.RotateAnimator(
                sequence,
                value=generate_random_float(
                    preferences.ken_burns_transformation_rotation_value,
                    preferences.ken_burns_transformation_rotation_value_max_deviation),
                reverse=generate_random_bool())

    @classmethod
    def poll(self, context):
        # Check if image transform strip is selected
        return len(bpy.context.selected_sequences) == 1 and \
               bpy.context.selected_sequences[0].type == 'TRANSFORM' and \
               bpy.context.selected_sequences[0].input_1.type == 'IMAGE'

    def execute(self, context):
        self.generate_effect()
        return {'FINISHED'}

    def generate_effect(self):
        """ Generate Ken Burns effect for selected transform strip """
        transform_strip = bpy.context.selected_sequences[0]
        transform_strip.use_uniform_scale = True
        group = KenBurnsEffect.get_fcurves_group_name()

        seq = bpy.context.selected_sequences[0]

        # remove previously generated effect keyframes
        if self.replace is True:
            keyframes.delete_keyframes(seq, group=group)

        # create random animators
        animators = self.create_animators(seq)
        print("Animators: {}".format(animators))

        # some transformations may require additional scale being applied to
        # the image initially. Go through chosen animators and set highest
        # requested scale
        start_scale = 1.0
        for animator in animators:
            start_scale = max(start_scale, animator.get_required_scale())
        print("Set start scale {}".format(start_scale))
        seq.scale_start_x = start_scale

        # generate animation
        for animator in animators:
            animator.generate()

    def create_animators(self, sequence=None):
        print("Creating animators for sequence: {}".format(sequence))
        animator_types = [
            KenBurnsEffect.ScaleAnimator,
            KenBurnsEffect.TranslateXAnimator,
            KenBurnsEffect.TranslateYAnimator]

        if self.ken_burns_transformation_rotation_enabled:
            animator_types.append(KenBurnsEffect.RotateAnimator)

        # by default there is only one animator per image strip, eg. only translation.
        # from time to time the number of combined animations can raise to 2
        num_of_selected_animators = 1
        if random.uniform(0, 100) < self.ken_burns_combined_effect_probability:
            num_of_selected_animators = num_of_selected_animators + 1

        # chose animator types for the given image strip
        selected_animator_types = []
        while len(selected_animator_types) < num_of_selected_animators:
            animator_index = random.randint(0, len(animator_types)-1)
            animator_type = animator_types.pop(animator_index)
            print("Selected animator type:{} index:{}".format(animator_type, len(selected_animator_types)))
            selected_animator_types.append(animator_type)

        # create animator instances with random values
        animators = []
        for animator_type in selected_animator_types:
            animators.append(animator_type.create_random(preferences=self, sequence=sequence))

        return animators

    @staticmethod
    def get_fcurves_group_name():
        return 'KenBurnsEffect'

# if __name__ == "__main__":
#    bpy.utils.register_class(ImportFiles)


def generate_random_float(value, deviation):
    return random.uniform(value - deviation, value + deviation)

def generate_random_bool():
    return bool(random.getrandbits(1))