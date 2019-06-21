import bpy


class KenBurnsEffectPreferences:
    ken_burns_transformation_x_value = bpy.props.FloatProperty(
        name="Transformation X",
        description="Ken Burns effect horizontal transformation value",
        default=8.0,
        min=0,
        max=50
    )

    ken_burns_transformation_x_value_max_deviation = bpy.props.FloatProperty(
        name="Transformation X max deviation",
        description="Ken Burns effect horizontal transformation max value deviation",
        default=2.0,
        min=0,
        max=50
    )

    ken_burns_transformation_y_value = bpy.props.FloatProperty(
        name="Transformation Y",
        description="Ken Burns effect vertical transformation value",
        default=8.0,
        min=0,
        max=50
    )

    ken_burns_transformation_y_value_max_deviation = bpy.props.FloatProperty(
        name="Transformation Y max deviation",
        description="Ken Burns effect vertical transformation max value deviation",
        default=2.0,
        min=0,
        max=50
    )

    ken_burns_transformation_scale_value = bpy.props.FloatProperty(
        name="Scale max",
        description="Ken Burns effect scale value",
        default=0.08,
        max=0.2,
        min=0.0
    )

    ken_burns_transformation_scale_value_max_deviation = bpy.props.FloatProperty(
        name="Scale max deviation",
        description="Ken Burns effect scale max deviation",
        default=0.009,
        max=0.3,
        min=0.0
    )

    ken_burns_transformation_rotation_enabled = bpy.props.BoolProperty(
        name="Use rotation",
        description="Use rotation in KenBurns generated effect",
        default=False,
    )

    ken_burns_transformation_rotation_value = bpy.props.FloatProperty(
        name="Rotation",
        description="Ken Burns effect rotation value",
        default=3.0,
        max=5.0,
        min=0.0
    )

    ken_burns_transformation_rotation_value_max_deviation = bpy.props.FloatProperty(
        name="Rotation max deviation",
        description="Ken Burns effect rotation value max deviation",
        default=1.0,
        max=3.0,
        min=0.0
    )

    ken_burns_combined_effect_probability = bpy.props.IntProperty(
        name="Combined effect probability (%)",
        description="Probability of applying multiple effects on one image",
        default=10,
        min=0,
        max=100
    )


class StripsCreatorPreferences:
    image_strip_frames = bpy.props.IntProperty(
        name="Image strip frames",
        description="Number of frames each imported image strip will last",
        default=90,
        min=5
    )

    strips_cross_frames = bpy.props.IntProperty(
        name="Strips cross effect frames",
        description="Number of frames the cross effect between two strips will last",
        default=20,
        min=5
    )

    generate_ken_burns_effect = bpy.props.BoolProperty(
        name="Ken Burns effect",
        description="Generates Ken Burns effect on imported images",
        default=True
    )

    movie_strips_scale = bpy.props.FloatProperty(
        name="Movie strips scale",
        description="Scale factor applied to every imported movie",
        default=1.15,
        min=1.0
    )


class SlideshowComposerPreferences(bpy.types.AddonPreferences, KenBurnsEffectPreferences, StripsCreatorPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        layout.label(text="Slideshow Composer preferences")
        layout.prop(self, "image_strip_frames")
        layout.prop(self, "strips_cross_frames")
        box = layout.box()
        box.label(text="Ken Burns effect for images")
        box.prop(self, "ken_burns_transformation_x_max")
        box.prop(self, "ken_burns_transformation_y_max")
        box.prop(self, "ken_burns_transformation_scale_max")
        box.prop(self, "ken_burns_transformation_rotation_max")
        box.prop(self, "ken_burns_combined_effect_probability")
