import bpy
import mathutils
import math
import os
import cProfile
from .interface import *
from . import nla_script

class B4A_LodProperty(bpy.types.PropertyGroup):
    pass

class B4A_DetailBendingColors(bpy.types.PropertyGroup):

    leaves_stiffness_col = bpy.props.StringProperty(
        name = "B4A: leaves stiffness color",
        description = "Vertex color used for leaves stiffness",
        default = ""
    )
    leaves_phase_col = bpy.props.StringProperty(
        name = "B4A: leaves phase color",
        description = "Vertex color used for leaves stiffness",
        default = ""
    )

    overall_stiffness_col = bpy.props.StringProperty(
        name = "B4A: overall stiffness color",
        description = "Vertex color used for overall stiffness",
        default = ""
    )

class B4A_FloatingSettings(bpy.types.PropertyGroup):
    part = bpy.props.EnumProperty(
        name = "Floater part",
        description = "Floating object part",
        default = "MAIN_BODY",
        items = [
            ("MAIN_BODY", "Main body", "Floating object main body"),
            ("BOB", "Bob", "Floating object's bob")
        ]
    )
    floating_factor = bpy.props.FloatProperty(
        name = "Floating factor",
        description = "Factor of strength applied to the floating object",
        default = 3.0,
        min = 0.0,
        soft_max = 100,
        step = 1,
        precision = 3
    )
    water_lin_damp = bpy.props.FloatProperty(
        name = "Water Linear damping",
        description = "Linear damping applied to objects under water",
        default = 0.8,
        min = 0.0,
        soft_max = 1,
        step = 1,
        precision = 3
    )
    water_rot_damp = bpy.props.FloatProperty(
        name = "Water Rotation damping",
        description = "Rotation damping applied to objects under water",
        default = 0.8,
        min = 0.0,
        soft_max = 1,
        step = 1,
        precision = 3
    )
    synchronize_position = bpy.props.BoolProperty(
        name = "Synchronize position",
        description = "Synchronize bob position",
        default = False,
    )

class B4A_VehicleSettings(bpy.types.PropertyGroup):
    part = bpy.props.EnumProperty(
        name = "Vehicle part",
        description = "Vehicle part",
        default = "CHASSIS",
        items = [
            ("HULL", "Hull", "Vehicle hull"),
            ("CHASSIS", "Chassis", "Vehicle chassis"),
            ("STEERING_WHEEL", "Steering wheel", "Optional vehicle steering wheel"),
            ("WHEEL_FRONT_LEFT", "Front left wheel", "Vehicle front left wheel"),
            ("WHEEL_FRONT_RIGHT", "Front right wheel", "Vehicle front right wheel"),
            ("WHEEL_BACK_LEFT", "Back left wheel", "Vehicle rear left wheel"),
            ("WHEEL_BACK_RIGHT", "Back right wheel", "Vehicle rear right wheel"),
            ("TACHOMETER", "Tachometer", "Vehicle tachometer"),
            ("SPEEDOMETER", "Speedometer", "Vehicle speedometer"),
            ("BOB", "Bob", "Boat's bob")
        ]
    )
    suspension_rest_length = bpy.props.FloatProperty(
        name = "Rest length",
        description = "Suspension rest length, length from relaxed to strained wheel position",
        default = 0.1,
        min = 0.0,
        soft_max = 1.0,
        step = 1,
        precision = 3
    )
    suspension_compression = bpy.props.FloatProperty(
        name = "Suspension compression",
        description = "Suspension compression",
        default = 4.4,
        min = 0.0,
        soft_max = 10.0,
        step = 10,
        precision = 1
    )
    suspension_stiffness = bpy.props.FloatProperty(
        name = "Suspension stiffness",
        description = "Suspension stiffness",
        default = 20.0,
        min = 0.0,
        soft_max = 100.0,
        step = 10,
        precision = 1
    )
    suspension_damping = bpy.props.FloatProperty(
        name = "Suspension damping",
        description = "Suspension damping",
        default = 2.3,
        min = 0.0,
        soft_max = 10.0,
        step = 10,
        precision = 1
    )
    wheel_friction = bpy.props.FloatProperty(
        name = "Wheel friction",
        description = "Wheel friction",
        default = 1000.0,
        min = 0.0,
        soft_max = 10000.0,
        step = 100,
        precision = 1
    )
    roll_influence = bpy.props.FloatProperty(
        name = "Roll influence",
        description = "Roll influence",
        default = 0.1,
        min = 0.0,
        soft_max = 10.0,
        step = 1,
        precision = 3
    )
    force_max = bpy.props.FloatProperty(
        name = "Force max",
        description = "Acceleration value for the vehicle",
        default = 1500.0,
        min = 0.0,
        soft_max = 10000.0,
        step = 1,
        precision = 3
    )
    brake_max = bpy.props.FloatProperty(
        name = "Brake max",
        description = "Braking value for the vehicle",
        default = 100.0,
        min = 0.0,
        soft_max = 10000.0,
        step = 1,
        precision = 3
    )
    steering_ratio = bpy.props.FloatProperty(
        name = "Steering ratio",
        description = "Ratio between the turn of the steering wheel and the turn of the wheels",
        default = 10.0,
        min = 0.0,
        soft_max = 100.0,
        step = 1,
        precision = 3
    )
    steering_max = bpy.props.FloatProperty(
        name = "Steering max",
        description = "Maximum steering wheel angle",
        default = 1,
        min = 0.0,
        soft_max = 10,
        step = 1,
        precision = 3
    )
    inverse_control = bpy.props.BoolProperty(
        name = "Inverse control",
        description = "Inverse vehicle control",
        default = False,
    )
    delta_tach_angle = bpy.props.FloatProperty(
        name = "Tachometer delta angle",
        description = "Sets delta angle for the tachometer device",
        default = 4.43,
        min = 0.0,
        soft_max = 6.18,
        step = 1,
        precision = 1,
        subtype = 'ANGLE'
    )
    max_speed_angle = bpy.props.FloatProperty(
        name = "Speedometer max angle",
        description = "Sets max angle for the speedometer device",
        default = 3.14,
        min = 0.0,
        soft_max = 6.18,
        step = 1,
        precision = 1,
        subtype = 'ANGLE'
    )
    speed_ratio = bpy.props.FloatProperty(
        name = "Speedometer ratio",
        description = "Sets speedometer ratio",
        default = 0.027,
        min = 0.0,
        soft_max = 10,
        step = 1,
        precision = 3,
        subtype = 'ANGLE'
    )
    max_suspension_travel_cm = bpy.props.FloatProperty(
        name = "Max suspension travel cm",
        description = "Max suspension travel cm",
        default = 30,
        min = 0.0,
        soft_max = 100,
        step = 1,
        precision = 3
    )
    floating_factor = bpy.props.FloatProperty(
        name = "Floating factor",
        description = "Factor of strengh applied to the floating object",
        default = 3.0,
        min = 0.0,
        soft_max = 100,
        step = 1,
        precision = 3
    )
    water_lin_damp = bpy.props.FloatProperty(
        name = "Water Linear damping",
        description = "Linear damping applied to objects under water",
        default = 0.8,
        min = 0.0,
        soft_max = 1,
        step = 1,
        precision = 3
    )
    water_rot_damp = bpy.props.FloatProperty(
        name = "Water Rotation damping",
        description = "Rotation damping applied to objects under water",
        default = 0.8,
        min = 0.0,
        soft_max = 1,
        step = 1,
        precision = 3
    )
    synchronize_position = bpy.props.BoolProperty(
        name = "Synchronize position",
        description = "Synchronize bob position",
        default = False,
    )

class B4A_GlowSettings(bpy.types.PropertyGroup):
    glow_duration = bpy.props.FloatProperty(
        name = "Glow duration",
        description = "Glow duration",
        default = 1.0,
        min = 0.01,
        soft_max = 10.0,
        max = 1000.0,
        step = 1,
        precision = 2
    )
    glow_period = bpy.props.FloatProperty(
        name = "Glow peroid",
        description = "Glow period",
        default = 1.0,
        min = 0.01,
        soft_max = 10.0,
        max = 1000.0,
        step = 1,
        precision = 2
    )
    glow_relapses = bpy.props.IntProperty(
        name = "Glow relapses",
        description = "Glow relapses",
        default = 0,
        min = 0,
        soft_max = 10,
        max = 1000
    )

class B4A_CharacterSettings(bpy.types.PropertyGroup):
    walk_speed = bpy.props.FloatProperty(
        name = "B4A: character walk speed",
        description = "Character walk speed",
        default = 4,
        min = 0.0,
        max = 10.0,
        soft_min = 0,
        soft_max = 10,
        step = 0.1,
        precision = 2
    )
    run_speed = bpy.props.FloatProperty(
        name = "B4A: character run speed",
        description = "Character run speed",
        default = 8,
        min = 0.0,
        max = 20.0,
        soft_min = 0,
        soft_max = 20,
        step = 0.1,
        precision = 2
    )
    step_height = bpy.props.FloatProperty(
        name = "B4A: character step height",
        description = "Character step height",
        default = 0.25,
        min = 0.0,
        max = 1.0,
        soft_min = 0,
        soft_max = 1,
        step = 0.01,
        precision = 3
    )
    jump_strength = bpy.props.FloatProperty(
        name = "B4A: character jump strength",
        description = "Character jump strength",
        default = 5,
        min = 0.0,
        max = 100.0,
        soft_min = 0,
        soft_max = 50,
        step = 0.1,
        precision = 2
    )
    waterline = bpy.props.FloatProperty(
        name = "B4A: character waterline",
        description = "Waterline for character in vertical direction",
        default = 0.0,
        min = -5,
        max = 5,
        soft_min = -2,
        soft_max = 2,
        step = 0.01,
        precision = 3
    )

class B4A_ShadowSettings(bpy.types.PropertyGroup):

    csm_resolution = bpy.props.EnumProperty(
        name = "csm_resolution",
        description = "Shadow map resolution",
        default = "2048",
        items = [
            ("512",  "512",  "512x512"),
            ("1024", "1024", "1024x1024"),
            ("2048", "2048", "2048x2048"),
            ("4096", "4096", "4096x4096"),
            ("8192", "8192", "8192x8192")
        ]
    )

    self_shadow_polygon_offset = bpy.props.FloatProperty(
        name = "self_shadow_polygon_offset",
        description = "Polygon offset value to prevent shadow acne",
        default = 1,
        min = 0,
        soft_max = 50,
        step = 10,
        precision = 2
    )

    self_shadow_normal_offset = bpy.props.FloatProperty(
        name = "self_shadow_normal_offset",
        description = "Normal offset value to prevent shadow acne",
        default = 0.01,
        min = 0,
        soft_max = 1,
        step = 0.1,
        precision = 3
    )

    b4a_enable_csm  = bpy.props.BoolProperty(
        name = "b4a_enable_csm",
        description = "Enable cascaded shadow maps",
        default = False
    )

    csm_num = bpy.props.IntProperty(
        name = "csm_num",
        description = "Number of cascaded shadow maps",
        default = 1,
        min = 1,
        max = 4
    )

    csm_first_cascade_border = bpy.props.FloatProperty(
        name = "csm_first_cascade_border",
        description = "Shadow map first cascade border",
        default = 10,
        min = 0.01,
        soft_max = 100,
        step = 10,
        precision = 2
    )

    first_cascade_blur_radius = bpy.props.FloatProperty(
        name = "first_cascade_blur_radius",
        description = "PCF blur radius for the first cascade",
        default = 3,
        min = 0,
        soft_max = 10,
        step = 10,
        precision = 2
    )

    csm_last_cascade_border = bpy.props.FloatProperty(
        name = "csm_last_cascade_border",
        description = "Shadow map last cascade border",
        default = 100,
        min = 0.01,
        soft_max = 100,
        step = 10,
        precision = 2
    )

    last_cascade_blur_radius = bpy.props.FloatProperty(
        name = "last_cascade_blur_radius",
        description = "PCF blur radius for the last cascade",
        default = 1.5,
        min = 0,
        soft_max = 10,
        step = 10,
        precision = 2
    )

    fade_last_cascade = bpy.props.BoolProperty(
        name = "fade_last_cascade",
        description = "The last cascade will be faded out",
        default = True
    )

    blend_between_cascades = bpy.props.BoolProperty(
        name = "blend_between_cascades",
        description = "Neighbouring cascades will be blended with each other",
        default = True
    )

class B4A_ColorCorrectionSettings(bpy.types.PropertyGroup):

    brightness = bpy.props.FloatProperty(
        name = "brightness",
        description = "Final image brightness",
        default = 0.0,
        min = -1.0,
        max = 1.0,
        step = 0.01,
        precision = 2
    )

    contrast = bpy.props.FloatProperty(
        name = "contrast",
        description = "Final image contrast",
        default = 0.0,
        min = -1.0,
        max = 1.0,
        step = 0.01,
        precision = 2
    )

    exposure = bpy.props.FloatProperty(
        name = "exposure",
        description = "Final image exposure",
        default = 1.0,
        min = 0.0,
        max = 2.0,
        step = 0.01,
        precision = 2
    )

    saturation = bpy.props.FloatProperty(
        name = "saturation",
        description = "Final image saturation",
        default = 1.0,
        min = 0.0,
        max = 2.0,
        step = 0.01,
        precision = 2
    )

class B4A_SSAOSettings(bpy.types.PropertyGroup):

    radius = bpy.props.FloatProperty(
        name = "radius",
        description = "radius",
        default = 0.0,
        min = 0.0,
        max = 20.0,
        step = 0.01,
        precision = 2
    )

    intensity = bpy.props.FloatProperty(
        name = "intensity",
        description = "intensity",
        default = 0.0,
        min = 0.0,
        max = 20.0,
        step = 0.01,
        precision = 2
    )

    falloff = bpy.props.FloatProperty(
        name = "falloff",
        description = "falloff",
        default = 0.0,
        min = 0.0,
        max = 20.0,
        step = 0.01,
        precision = 2
    )


class B4A_GodRaysSettings(bpy.types.PropertyGroup):

    intensity = bpy.props.FloatProperty(
        name = "intensity",
        description = "Intensity multiplier",
        default = 0.7,
        min = 0.0,
        max = 5.0,
        step = 0.01,
        precision = 2
    )

    max_ray_length = bpy.props.FloatProperty(
        name = "max_ray_length",
        description = "Maximum length of rays in screen size units",
        default = 1.0,
        min = 0.0,
        max = 5.0,
        step = 0.01,
        precision = 2
    )

    steps_per_pass = bpy.props.FloatProperty(
        name = "steps_per_pass",
        description = "Number of steps per blur pass (3 passes in all)",
        default = 10.0,
        min = 0.0,
        max = 30.0,
        step = 1.0,
        precision = 1
    )

class B4A_BloomSettings(bpy.types.PropertyGroup):

    radius = bpy.props.FloatProperty(
        name = "radius",
        description = "radius",
        default = 0.0,
        min = 0.0,
        max = 20.0,
        step = 0.01,
        precision = 2
    )

    threshold = bpy.props.FloatProperty(
        name = "threshold",
        description = "threshold",
        default = 0.0,
        min = 0.0,
        max = 20.0,
        step = 0.01,
        precision = 2
    )

    intensity = bpy.props.FloatProperty(
        name = "intensity",
        description = "intensity",
        default = 0.0,
        min = 0.0,
        max = 20.0,
        step = 0.01,
        precision = 2
    )

class B4A_FogSettings(bpy.types.PropertyGroup):

    start = bpy.props.FloatProperty(
        name = "start",
        description = "start",
        default = 1.0,
        min = 0.0,
        max = 5.0,
        step = 0.01,
        precision = 2
    )

    end = bpy.props.FloatProperty(
        name = "end",
        description = "end",
        default = 4.0,
        min = 0.0,
        max = 20.0,
        step = 0.01,
        precision = 2
    )

    texture = bpy.props.StringProperty(
        name = "texture",
        description = "texture",
        default = ""
    )

    color = bpy.props.FloatVectorProperty(
        name = "B4A: fog color",
        description = "Fog color",
        default = (0.5, 0.5, 0.5),
        min = 0.0,
        soft_min = 0.0,
        max = 1.0,
        soft_max = 1.0,
        precision = 3,
        subtype = 'COLOR',
        size = 3
    )

class B4A_BackgroundSettings(bpy.types.PropertyGroup):
   
    mode = bpy.props.FloatProperty(
        name = "mode",
        description = "mode",
        default = 0,
        min = 0,
        max = 5,
        step = 1
    )

    texture = bpy.props.StringProperty(
        name = "texture",
        description = "texture",
        default = ""
    )

    color = bpy.props.FloatVectorProperty(
        name = "B4A: Background color",
        description = "Background color",
        default = (0.5, 0.5, 0.5),
        min = 0.0,
        soft_min = 0.0,
        max = 1.0,
        soft_max = 1.0,
        precision = 3,
        subtype = 'COLOR',
        size = 3
    )

class B4A_VignetteSettings(bpy.types.PropertyGroup):

    color = bpy.props.FloatVectorProperty(
        name = "B4A: coverage color",
        description = "coverage color",
        default = (0.5, 0.5, 0.5),
        min = 0.0,
        soft_min = 0.0,
        max = 1.0,
        soft_max = 1.0,
        precision = 3,
        subtype = 'COLOR',
        size = 3
    )

    coverage = bpy.props.FloatProperty(
        name = "coverage",
        description = "coverage",
        default = 1.0,
        min = 0.0,
        max = 5.0,
        step = 0.01,
        precision = 2
    )

    softness = bpy.props.FloatProperty(
        name = "softness",
        description = "softness",
        default = 4.0,
        min = 0.0,
        max = 20.0,
        step = 0.01,
        precision = 2
    )

class B4A_HdrSettings(bpy.types.PropertyGroup):

    key = bpy.props.FloatProperty(
        name = "key",
        description = "key",
        default = 1.0,
        min = 0.0,
        max = 5.0,
        step = 0.01,
        precision = 2
    )

class B4A_MotionBlurSettings(bpy.types.PropertyGroup):

    motion_blur_factor = bpy.props.FloatProperty(
        name = "motion_blur_factor",
        description = "Motion blur factor",
        default = 0.01,
        min = 0.001,
        soft_min = 0.001,
        max = 1.0,
        soft_max = 1.0,
        step = 0.1,
        precision = 3
    )

    motion_blur_decay_threshold = bpy.props.FloatProperty(
        name = "motion_blur_decay_threshold",
        description = "Motion blur decay threshold",
        default = 0.01,
        min = 0.0,
        soft_min = 0.0,
        max = 1.0,
        soft_max = 1.0,
        step = 0.1,
        precision = 3
    )

class B4A_SkySettings(bpy.types.PropertyGroup):

    reflexible = bpy.props.BoolProperty(
        name = "B4A: reflexible",
        description = "Sky will be rendered during the reflection pass",
        default = False
    )

    reflexible_only = bpy.props.BoolProperty(
        name = "B4A: reflexible only",
        description = "Sky will not be rendered, but will have a reflection",
        default = False
    )

    procedural_skydome = bpy.props.BoolProperty(
        name = "B4A: procedural skydome",
        description = "Sky will be generated procedurally",
        default = False
    )

    use_as_environment_lighting = bpy.props.BoolProperty(
        name = "B4A: use_as_environment_map",
        description = "Procedural sky will be used as environment lighting",
        default = False
    )

    color = bpy.props.FloatVectorProperty(
        name = "color",
        description = "Sky atmosphere color",
        default = (0.087, 0.255, 0.6),
        min = 0.0,
        soft_min = 0.0,
        max = 1.0,
        soft_max = 1.0,
        precision = 3,
        subtype = 'COLOR',
        size = 3
    )

    rayleigh_brightness = bpy.props.FloatProperty(
        name = "rayleigh_brightness",
        description = "Brightness of Rayleigh scattering",
        default = 3.3,
        min = 0.0,
        max = 5.0,
        step = 0.01,
        precision = 2
    )

    mie_brightness = bpy.props.FloatProperty(
        name = "mie_brightness",
        description = "Brightness of Mie scattering",
        default = 0.1,
        min = 0.0,
        max = 1.0,
        step = 0.01,
        precision = 2
    )

    spot_brightness = bpy.props.FloatProperty(
        name = "spot_brightness",
        description = "Brightness of sun spot",
        default = 20.0,
        min = 0.0,
        max = 1000.0,
        step = 1.0,
        precision = 1
    )

    scatter_strength = bpy.props.FloatProperty(
        name = "scatter_strength",
        description = "Strength of light scattering",
        default = 0.2,
        min = 0.0,
        max = 1.0,
        step = 0.01,
        precision = 2
    )

    rayleigh_strength = bpy.props.FloatProperty(
        name = "rayleigh_strength",
        description = "Strength of Rayleigh scattering",
        default = 0.2,
        min = 0.0,
        max = 1.0,
        step = 0.01,
        precision = 2
    )

    mie_strength = bpy.props.FloatProperty(
        name = "mie_strength",
        description = "Strength of Mie scattering",
        default = 0.006,
        min = 0.0,
        max = 0.1,
        step = 0.0001,
        precision = 4
    )

    rayleigh_collection_power = bpy.props.FloatProperty(
        name = "rayleigh_collection_power",
        description = "Rayleigh collection power",
        default = 0.35,
        min = 0.0,
        max = 2.0,
        step = 0.01,
        precision = 2
    )

    mie_collection_power = bpy.props.FloatProperty(
        name = "mie_collection_power",
        description = "Mie collection power",
        default = 0.5,
        min = 0.0,
        max = 2.0,
        step = 0.01,
        precision = 2
    )

    mie_distribution = bpy.props.FloatProperty(
        name = "mie_distribution",
        description = "Mie disturbtion",
        default = 0.4,
        min = 0.0,
        max = 2.0,
        step = 0.01,
        precision = 2
    )

class B4A_DynamicCompressorSettings(bpy.types.PropertyGroup):
    threshold = bpy.props.FloatProperty(
        name = "threshold",
        description = "The value above which the compression will start taking effect",
        default = -24,
        min = -100,
        max = 0,
        step = 10,
        precision = 1
    )
    knee = bpy.props.FloatProperty(
        name = "knee",
        description = "Range above the threshold where the curve transitions to the ratio portion",
        default = 30,
        min = 0,
        max = 40,
        step = 10,
        precision = 1
    )
    ratio = bpy.props.FloatProperty(
        name = "ratio",
        description = "dB input change for a 1 dB output change",
        default = 12,
        min = 1,
        max = 20,
        step = 10,
        precision = 1
    )
    attack = bpy.props.FloatProperty(
        name = "attack",
        description = "Amount of time to reduce gain by 10 dB",
        default = 0.003,
        min = 0,
        max = 1,
        step = 0.1,
        precision = 3
    )
    release = bpy.props.FloatProperty(
        name = "release",
        description = "Amount of time to increase gain by 10 dB",
        default = 0.250,
        min = 0,
        max = 1,
        step = 0.1,
        precision = 3
    )

class B4A_BoundingsSettings(bpy.types.PropertyGroup):
    min_x = bpy.props.FloatProperty(
        name = "min_x",
        description = "Boundings minimum x",
        default = -1.0,
        min = -1000,
        max = 1000,
        soft_min = -50,
        soft_max = 50,
        step = 1,
        precision = 3
    )
    max_x = bpy.props.FloatProperty(
        name = "max_x",
        description = "Boundings maximum x",
        default = 1.0,
        min = -1000,
        max = 1000,
        soft_min = -50,
        soft_max = 50,
        step = 1,
        precision = 3
    )
    min_y = bpy.props.FloatProperty(
        name = "min_y",
        description = "Boundings minimum y",
        default = -1.0,
        min = -1000,
        max = 1000,
        soft_min = -50,
        soft_max = 50,
        step = 1,
        precision = 3
    )
    max_y = bpy.props.FloatProperty(
        name = "max_y",
        description = "Boundings maximum y",
        default = 1.0,
        min = -1000,
        max = 1000,
        soft_min = -50,
        soft_max = 50,
        step = 1,
        precision = 3
    )
    min_z = bpy.props.FloatProperty(
        name = "min_z",
        description = "Boundings minimum z",
        default = -1.0,
        min = -1000,
        max = 1000,
        soft_min = -50,
        soft_max = 50,
        step = 1,
        precision = 3
    )
    max_z = bpy.props.FloatProperty(
        name = "max_z",
        description = "Boundings maximum z",
        default = 1.0,
        min = -1000,
        max = 1000,
        soft_min = -50,
        soft_max = 50,
        step = 1,
        precision = 3
    )

def add_b4a_props():

    b4a_do_not_export = bpy.props.BoolProperty(
        name = "B4A: do not export",
        description = "Check if you do NOT wish to export this component",
        default = False
    )

    # deprecated
    b4a_export_path = bpy.props.StringProperty(
        name = "B4A: component export path",
        description = "Exported file path relative to the blend file",
        default = ""
    )

    class_names = [
        'Action',
        'Armature',
        'Camera',
        'Curve',
        'Group',
        'Image',
        'Lamp',
        'Material',
        'Mesh',
        'Object',
        'ParticleSettings',
        'Texture',
        'Scene',
        'Speaker',
        'Sound',
        'World'
    ]

    class_names_for_export = [
        'Action',
        'Image',
        'Material',
        'Object',
        'ParticleSettings',
        'Scene',
        'Texture',
        'World'
    ]

    for class_name in class_names_for_export:
        cl = getattr(bpy.types, class_name)
        cl.b4a_do_not_export = b4a_do_not_export

    for class_name in class_names:
        cl = getattr(bpy.types, class_name)
        # deprecated
        cl.b4a_export_path   = b4a_export_path

    b4a_export_path_json = bpy.props.StringProperty(
        name = "B4A: export path json",
        description = "Exported json file path relative to the blend file",
        default = ""
    )
    b4a_export_path_html = bpy.props.StringProperty(
        name = "B4A: export path html",
        description = "Exported html file path relative to the blend file",
        default = ""
    )
    bpy.types.Scene.b4a_export_path_json = b4a_export_path_json
    bpy.types.Scene.b4a_export_path_html = b4a_export_path_html

    add_scene_properties()

    # for world panel
    b4a_glow_color = bpy.props.FloatVectorProperty(
        name = "B4A: glow color of the selection",
        description = "Default glow color of the selection",
        default = (1.0, 1.0, 1.0),
        min = 0.0,
        soft_min = 0.0,
        max = 1.0,
        soft_max = 1.0,
        precision = 3,
        subtype = 'COLOR',
        size = 3
    )
    bpy.types.World.b4a_glow_color = b4a_glow_color

    b4a_glow_factor = bpy.props.FloatProperty(
        name = "B4A: glow factor",
        description = "Glow strength factor",
        default = 1.0,
        min = 0.1,
        max = 1.0,
        step = 1,
        precision = 2
    )
    bpy.types.World.b4a_glow_factor = b4a_glow_factor

    b4a_fog_color = bpy.props.FloatVectorProperty(
        name = "B4A: fog color",
        description = "Fog color",
        default = (0.5, 0.5, 0.5),
        min = 0.0,
        soft_min = 0.0,
        max = 1.0,
        soft_max = 1.0,
        precision = 3,
        subtype = 'COLOR',
        size = 3
    )
    bpy.types.World.b4a_fog_color = b4a_fog_color

    b4a_fog_density = bpy.props.FloatProperty(
        name = "B4A: fog density",
        description = "Fog density",
        default = 0.0,
        min = 0.0,
        soft_min = 0.0,
        max = 1.0,
        soft_max = 0.1,
        step = 0.1,
        precision = 4
    )

    bpy.types.World.b4a_fog_density = b4a_fog_density


    bpy.types.World.b4a_god_rays_settings = bpy.props.PointerProperty(
        name = "B4A: god rays settings",
        type = B4A_GodRaysSettings
    )

    bpy.types.World.b4a_shadow_settings = bpy.props.PointerProperty(
        name = "B4A: shadow settings",
        type = B4A_ShadowSettings
    )

    bpy.types.World.b4a_color_correction_settings = bpy.props.PointerProperty(
        name = "B4A: color correction settings",
        type = B4A_ColorCorrectionSettings
    )

    bpy.types.World.b4a_ssao_settings = bpy.props.PointerProperty(
        name = "B4A: SSAO settings",
        type = B4A_SSAOSettings
    )

    bpy.types.World.b4a_sky_settings = bpy.props.PointerProperty(
        name = "B4A: sky settings",
        type = B4A_SkySettings
    )

    bpy.types.World.b4a_bloom_settings = bpy.props.PointerProperty(
        name = "B4A: bloom settings",
        type = B4A_BloomSettings
    )

    bpy.types.World.b4a_fog_settings = bpy.props.PointerProperty(
        name = "B4A: fog settings",
        type = B4A_FogSettings
    )

    bpy.types.World.b4a_background_settings = bpy.props.PointerProperty(
        name = "B4A: background settings",
        type = B4A_BackgroundSettings
    )

    bpy.types.World.b4a_vignette_settings = bpy.props.PointerProperty(
        name = "B4A: vignette settings",
        type = B4A_VignetteSettings
    )

    bpy.types.World.b4a_hdr_settings = bpy.props.PointerProperty(
        name = "B4A: hdr settings",
        type = B4A_HdrSettings
    )

    bpy.types.World.b4a_motion_blur_settings = bpy.props.PointerProperty(
        name = "B4A: motion blur settings",
        type = B4A_MotionBlurSettings
    )

    add_object_properties()
    
    bpy.types.Camera.b4a_ms_style = bpy.props.EnumProperty(
        name = "B4A: Mono/Sterio style",
        description = "Default camera mono/sterio style",
        default = "TARGET",
        items = [
            ("STATIC", "Mono", "Mono"),
            ("TARGET", "Sterio", "Sterio")
        ]
    )
    # for camera panel
    b4a_move_style = bpy.props.EnumProperty(
        name = "B4A: movement style",
        description = "Default camera movement style",
        default = "TARGET",
        items = [
            ("STATIC", "Static", "Static camera"),
            ("TARGET", "Target", "Move target"),
            ("EYE", "Eye", "Move eye")
        ]
    )
    bpy.types.Camera.b4a_move_style = b4a_move_style

    b4a_target = bpy.props.FloatVectorProperty(
        name = "B4A: target",
        description = "Camera target location for \"TARGET\" camera",
        default = (0.0, 0.0, 0.0),
        min = -1000000.0,
        soft_min = -100.0,
        max = 1000000.0,
        soft_max = 100.0,
        precision = 2,
        subtype = 'XYZ',
        size = 3
    )
    bpy.types.Camera.b4a_target = b4a_target

    b4a_use_distance_limits = bpy.props.BoolProperty(
        name = "B4A: use distance limits",
        description = "Check if you wish to set distance limits",
        default = False
    )
    bpy.types.Camera.b4a_use_distance_limits = b4a_use_distance_limits

    b4a_distance_min = bpy.props.FloatProperty(
           name = "B4A: Minimum distance to target",
           description = "Minimum distance to target",
           default = 1.0,
           min = -1000000.0,
           soft_min = 0.0,
           max = 1000000.0,
           soft_max = 1000.0,
           precision = 3,
       )
    bpy.types.Camera.b4a_distance_min = b4a_distance_min

    b4a_distance_max = bpy.props.FloatProperty(
           name = "B4A: Maximum distance to target",
           description = "Maximum distance to target",
           default = 100.0,
           min = -1000000.0,
           soft_min = 0.0,
           max = 1000000.0,
           soft_max = 1000.0,
           precision = 3,
       )
    bpy.types.Camera.b4a_distance_max = b4a_distance_max

    b4a_use_horizontal_clamping = bpy.props.BoolProperty(
        name = "B4A: use horizontal rotation clamping",
        description = "Check if you wish to set horizontal clamping angles",
        default = False
    )
    bpy.types.Camera.b4a_use_horizontal_clamping = b4a_use_horizontal_clamping

    b4a_rotation_left_limit = bpy.props.FloatProperty(
           name = "B4A: Rotation left limit",
           description = "Rotation left limit angle",
           default = -math.pi,
           min = -2 * math.pi,
           soft_min = -2 * math.pi,
           max = 2 * math.pi,
           soft_max = 2 * math.pi,
           precision = 1,
           subtype = "ANGLE",
       )
    bpy.types.Camera.b4a_rotation_left_limit = b4a_rotation_left_limit

    b4a_rotation_right_limit = bpy.props.FloatProperty(
           name = "B4A: Rotation right limit",
           description = "Rotation right limit angle",
           default = math.pi,
           min = -2 * math.pi,
           soft_min = -2 * math.pi,
           max = 2 * math.pi,
           soft_max = 2 * math.pi,
           precision = 1,
           subtype = "ANGLE",
       )
    bpy.types.Camera.b4a_rotation_right_limit = b4a_rotation_right_limit

    bpy.types.Camera.b4a_horizontal_clamping_type = bpy.props.EnumProperty(
        name = "B4A: horizontal clamping type",
        description = "Horizontal clamping type",
        default = "LOCAL",
        items = [
            ("LOCAL", "Camera space", "Clamp angles in camera space"),
            ("WORLD", "World space", "Clamp angles in world space")
        ]
    )

    b4a_use_vertical_clamping = bpy.props.BoolProperty(
        name = "B4A: use vertical rotation clamping",
        description = "Check if you wish to set vertical clamping angles",
        default = False
    )
    bpy.types.Camera.b4a_use_vertical_clamping = b4a_use_vertical_clamping


    def get_rotation_down_limit(self):
        value = self.b4a_rotation_down_limit_storage
        if getattr(self, "b4a_use_horizontal_clamping"):
            value = min(max(value, -math.pi / 2), math.pi / 2)
        return value

    def set_rotation_down_limit(self, value):
        if getattr(self, "b4a_use_horizontal_clamping"):
            value = min(max(value, -math.pi / 2), math.pi / 2)
        self.b4a_rotation_down_limit_storage = value

    b4a_rotation_down_limit = bpy.props.FloatProperty(
           name = "B4A: Rotation down limit",
           description = "Rotation down limit angle",
           default = -math.pi / 2,
           min = -2 * math.pi,
           soft_min = -2 * math.pi,
           max = 2 * math.pi,
           soft_max = 2 * math.pi,
           precision = 1,
           subtype = "ANGLE",
           set = set_rotation_down_limit,
           get = get_rotation_down_limit
       )
    bpy.types.Camera.b4a_rotation_down_limit = b4a_rotation_down_limit

    # NOTE: fiction property for storing dynamically changing property
    bpy.types.Camera.b4a_rotation_down_limit_storage = bpy.props.FloatProperty(
            default = -math.pi / 2)


    def get_rotation_up_limit(self):
        value = self.b4a_rotation_up_limit_storage
        if getattr(self, "b4a_use_horizontal_clamping"):
            value = min(max(value, -math.pi / 2), math.pi / 2)
        return value

    def set_rotation_up_limit(self, value):
        if getattr(self, "b4a_use_horizontal_clamping"):
            value = min(max(value, -math.pi / 2), math.pi / 2)
        self.b4a_rotation_up_limit_storage = value

    b4a_rotation_up_limit = bpy.props.FloatProperty(
           name = "B4A: Rotation up limit",
           description = "Rotation up limit angle",
           default = math.pi / 2,
           min = -2 * math.pi,
           soft_min = -2 * math.pi,
           max = 2 * math.pi,
           soft_max = 2 * math.pi,
           precision = 1,
           subtype = "ANGLE",
           set = set_rotation_up_limit,
           get = get_rotation_up_limit
       )
    bpy.types.Camera.b4a_rotation_up_limit = b4a_rotation_up_limit

    # NOTE: fiction property for storing dynamically changing property
    bpy.types.Camera.b4a_rotation_up_limit_storage = bpy.props.FloatProperty(
            default = math.pi / 2)

    bpy.types.Camera.b4a_vertical_clamping_type = bpy.props.EnumProperty(
        name = "B4A: vertical clamping type",
        description = "Vertical clamping type",
        default = "LOCAL",
        items = [
            ("LOCAL", "Camera space", "Clamp angles in camera space"),
            ("WORLD", "World space", "Clamp angles in world space")
        ]
    )


    b4a_dof_front = bpy.props.FloatProperty(
           name = "B4A: DOF front distance",
           description = "Distance to the front DOF plane",
           default = 1.0,
           min = 0.0,
           soft_min = 0.0,
           max = 100000.0,
           soft_max = 100.0,
           precision = 3,
       )
    bpy.types.Camera.b4a_dof_front = b4a_dof_front

    b4a_dof_rear = bpy.props.FloatProperty(
           name = "B4A: DOF rear distance",
           description = "Distance to the rear DOF plane",
           default = 1.0,
           min = 0.0,
           soft_min = 0.0,
           max = 100000.0,
           soft_max = 100.0,
           precision = 3,
       )
    bpy.types.Camera.b4a_dof_rear = b4a_dof_rear

    b4a_dof_power = bpy.props.FloatProperty(
           name = "B4A: DOF power",
           description = "Strength of DOF blur",
           default = 3.0,
           min = 0.1,
           soft_min = 0.1,
           max = 20.0,
           soft_max = 20.0,
           precision = 2,
       )
    bpy.types.Camera.b4a_dof_power = b4a_dof_power

    add_speaker_properties()

    # for lamp panel
    b4a_generate_shadows = bpy.props.BoolProperty(
        name = "B4A: generate shadows",
        description = "Whether the lamp generates shadows",
        default = False
    )
    bpy.types.Lamp.b4a_generate_shadows = b4a_generate_shadows

    b4a_dynamic_intensity = bpy.props.BoolProperty(
        name = "B4A: dynamic intensity",
        description = "Whether sun changes intensity regardless to it position",
        default = False
    )
    bpy.types.Lamp.b4a_dynamic_intensity = b4a_dynamic_intensity

    # for mesh panel
    b4a_override_boundings = bpy.props.BoolProperty(
        name = "B4A: override boundings",
        description = "Override mesh boundings with specified values",
        default = False
    )
    bpy.types.Mesh.b4a_override_boundings = b4a_override_boundings

    b4a_boundings = bpy.props.PointerProperty(
        name = "B4A: boundings",
        type = B4A_BoundingsSettings
    )
    bpy.types.Mesh.b4a_boundings = b4a_boundings

    add_material_properties()

    add_texture_properties()

    add_particle_settings_properties()

def add_scene_properties():

    scene_type = bpy.types.Scene

    scene_type.b4a_use_nla = bpy.props.BoolProperty(
        name = "B4A: use NLA",
        description = "Use NLA to control animation and sounds on the scene",
        default = False
    )
    scene_type.b4a_nla_cyclic = bpy.props.BoolProperty(
        name = "B4A: cyclic NLA",
        description = "Repeat NLA animation",
        default = False
    )
    scene_type.b4a_enable_audio = bpy.props.BoolProperty(
        name = "B4A: enable audio",
        description = "Enable audio on this scene",
        default = True
    )
    scene_type.b4a_enable_dynamic_compressor = bpy.props.BoolProperty(
        name = "B4A: enable dynamic compressor",
        description = "Enable dynamic compression effect on this scene",
        default = False
    )
    scene_type.b4a_dynamic_compressor_settings = bpy.props.PointerProperty(
        name = "B4A: Dynamic compressor settings",
        type = B4A_DynamicCompressorSettings
    )

    scene_type.b4a_enable_convolution_engine = bpy.props.BoolProperty(
        name = "B4A: enable convolution engine",
        description = "Enable the convolution engine to allow linear (spacial) effects on this scene",
        default = False
    )

    b4a_enable_physics = bpy.props.BoolProperty(
        name = "B4A: enable physics",
        description = "Enable physics simulation on this scene",
        default = True
    )
    scene_type.b4a_enable_physics = b4a_enable_physics

    b4a_render_shadows = bpy.props.BoolProperty(
        name = "B4A: render shadows",
        description = "Render shadows for the scene objects with the " +
                "\"B4A shadow cast\" and \"B4A shadow receive\" properties",
        default = True
    )
    scene_type.b4a_render_shadows = b4a_render_shadows

    b4a_render_reflections = bpy.props.BoolProperty(
        name = "B4A: render reflections",
        description = "Render reflections for the scene objects with the " +
                "\"B4A reflection cast\" and \"B4A reflection receive\" properties",
        default = False
    )
    scene_type.b4a_render_reflections = b4a_render_reflections

    b4a_render_refractions = bpy.props.BoolProperty(
        name = "B4A: render refractions",
        description = "Render refractions for the scene objects",
        default = False
    )
    scene_type.b4a_render_refractions = b4a_render_refractions

    b4a_enable_god_rays = bpy.props.BoolProperty(
        name = "B4A: enable god rays",
        description = "Enable god rays for the scene lights",
        default = False
    )
    scene_type.b4a_enable_god_rays = b4a_enable_god_rays

    b4a_enable_ssao = bpy.props.BoolProperty(
        name = "B4A: enable SSAO",
        description = "Enable screen space ambient occlusion",
        default = False
    )
    scene_type.b4a_enable_ssao = b4a_enable_ssao

    b4a_enable_preview_display = bpy.props.BoolProperty(
        name = "B4A: enable preview display",
        description = "enable preview display",
        default = False
    )
    scene_type.b4a_enable_preview_display = b4a_enable_preview_display

    b4a_enable_fps_display = bpy.props.BoolProperty(
        name = "B4A: enable fps display",
        description = "enable fps display",
        default = False
    )
    scene_type.b4a_enable_fps_display = b4a_enable_fps_display

    b4a_enable_ray_display = bpy.props.BoolProperty(
        name = "B4A: enable ray display",
        description = "enable ray display",
        default = False
    )
    scene_type.b4a_enable_ray_display = b4a_enable_ray_display

    b4a_enable_bbox_display = bpy.props.BoolProperty(
        name = "B4A: enable bbox display",
        description = "enable bbox display",
        default = False
    )
    scene_type.b4a_enable_bbox_display = b4a_enable_bbox_display

    b4a_enable_wire_frame = bpy.props.BoolProperty(
        name = "B4A: enable_wire_frame",
        description = "enable_wire_frame",
        default = False
    )
    scene_type.b4a_enable_wire_frame = b4a_enable_wire_frame 

    b4a_enable_fxaa = bpy.props.BoolProperty(
        name = "B4A: enable FXAA",
        description = "Enable FXAA",
        default = False
    )
    scene_type.b4a_enable_fxaa = b4a_enable_fxaa

    b4a_enable_frustum_culling = bpy.props.BoolProperty(
        name = "B4A: enable_frustum_culling",
        description = "enable_frustum_culling",
        default = False
    )
    scene_type.b4a_enable_frustum_culling = b4a_enable_frustum_culling

    b4a_enable_backface_culling = bpy.props.BoolProperty(
        name = "B4A: enable_backface_culling",
        description = "enable_backface_culling",
        default = False
    )
    scene_type.b4a_enable_backface_culling = b4a_enable_backface_culling

    b4a_near_clip = bpy.props.FloatProperty(
        name = "B4A: near clip",
        description = "near clip",
        default = 0.1,
        min = 0.0000001,
        soft_min = 0.01,
        max = 1000.0,
        soft_max = 100.0,
        step = 0.1,
        precision = 4
    )

    scene_type.b4a_near_clip = b4a_near_clip

    b4a_far_clip = bpy.props.FloatProperty(
        name = "B4A: far clip",
        description = "far clip",
        default = 1000.0,
        min = 0.0,
        soft_min = 0.0,
        max = 1000000000.0,
        soft_max = 0.1,
        step = 0.1,
        precision = 4
    )

    scene_type.b4a_far_clip = b4a_far_clip

    b4a_batch_grid_size = bpy.props.FloatProperty(
        name = "B4A: batch grid size",
        description = "Batch grid size in meters, pass zero value to " +
                "prevent grid use",
        default = 0.0,
        min = 0.0,
        soft_max = 1000.0,
        precision = 2
    )
    scene_type.b4a_batch_grid_size = b4a_batch_grid_size

    # see also b4a_anisotropic_filtering for texture
    b4a_anisotropic_filtering = bpy.props.EnumProperty(
        name = "B4A: anisotropic filtering",
        description = "Anisotropic filtering for all textures. May be overriden by individual textures",
        items = [
            ("OFF", "OFF", "0", 0),
            ("2x",  "2x",  "1", 1),
            ("4x",  "4x",  "2", 2),
            ("8x",  "8x",  "3", 3),
            ("16x", "16x", "4", 4)
        ]
    )
    scene_type.b4a_anisotropic_filtering = b4a_anisotropic_filtering

    b4a_enable_bloom = bpy.props.BoolProperty(
        name = "B4A: enable bloom",
        description = "Enable bloom",
        default = False
    )
    scene_type.b4a_enable_bloom = b4a_enable_bloom

    b4a_enable_fog = bpy.props.BoolProperty(
        name = "B4A: enable fog",
        description = "Enable fog",
        default = False
    )
    scene_type.b4a_enable_fog = b4a_enable_fog

    b4a_enable_vignette = bpy.props.BoolProperty(
        name = "B4A: enable vignette",
        description = "Enable vignette",
        default = False
    )
    scene_type.b4a_enable_vignette = b4a_enable_vignette

    b4a_enable_fog = bpy.props.BoolProperty(
        name = "B4A: enable fog",
        description = "Enable fog",
        default = False
    )
    scene_type.b4a_enable_fog = b4a_enable_fog

    b4a_enable_FXAA = bpy.props.BoolProperty(
        name = "B4A: enable fxaa",
        description = "Enable fxaa",
        default = False
    )
    scene_type.b4a_enable_FXAA = b4a_enable_FXAA

    b4a_enable_hdr = bpy.props.BoolProperty(
        name = "B4A: enable hdr",
        description = "Enable hdr",
        default = False
    )
    scene_type.b4a_enable_hdr = b4a_enable_hdr

    b4a_enable_motion_blur = bpy.props.BoolProperty(
        name = "B4A: enable motion blur",
        description = "Enable motion blur",
        default = False
    )
    scene_type.b4a_enable_motion_blur = b4a_enable_motion_blur

    b4a_enable_color_correction = bpy.props.BoolProperty(
        name = "B4A: enable color correction",
        description = "Enable color correction",
        default = False
    )
    scene_type.b4a_enable_color_correction = b4a_enable_color_correction

    b4a_enable_antialiasing = bpy.props.BoolProperty(
        name = "B4A: enable antialiasing",
        description = "Enable antialiasing",
        default = True
    )
    scene_type.b4a_enable_antialiasing = b4a_enable_antialiasing


def add_object_properties():
    """Add properties for the object panel"""

    obj_type = bpy.types.Object

    b4a_do_not_batch = bpy.props.BoolProperty(
        name = "B4A: do not batch",
        description = "Do not join this object with others having the same material",
        default = False
    )
    obj_type.b4a_do_not_batch = b4a_do_not_batch

    obj_type.b4a_dynamic_geometry = bpy.props.BoolProperty(
        name = "B4A: dynamic geometry",
        description = "Allow to use geometry update API for given object",
        default = False
    )

    obj_type.b4a_export_edited_normals = bpy.props.BoolProperty(
        name = "B4A: export edited normals",
        description = "Export baked vertex normals",
        default = False
    )

    obj_type.b4a_apply_scale = bpy.props.BoolProperty(
        name = "B4A: apply scale",
        description = "Apply scale before export",
        default = False
    )

    obj_type.b4a_apply_modifiers = bpy.props.BoolProperty(
        name = "B4A: apply modifiers",
        description = "Apply object modifiers before export",
        default = False
    )

    b4a_do_not_cull = bpy.props.BoolProperty(
        name = "B4A: do not cull",
        description = "Do not use frustum culling for this object",
        default = False
    )
    obj_type.b4a_do_not_cull = b4a_do_not_cull

    obj_type.b4a_disable_fogging = bpy.props.BoolProperty(
        name = "B4A: disable fogging",
        description = "Prevent object to be fogged in",
        default = False
    )

    obj_type.b4a_do_not_render = bpy.props.BoolProperty(
        name = "B4A: do not render",
        description = "Object will not be rendered",
        default = False
    )

    b4a_shadow_cast = bpy.props.BoolProperty(
        name = "B4A: shadow cast",
        description = "The object will be rendered during the shadow pass",
        default = False
    )
    obj_type.b4a_shadow_cast = b4a_shadow_cast

    obj_type.b4a_shadow_cast_only = bpy.props.BoolProperty(
        name = "B4A: shadow cast only",
        description = "The object will not be rendered, but will cast a shadow",
        default = False
    )

    b4a_shadow_receive = bpy.props.BoolProperty(
        name = "B4A: shadow receive",
        description = "The object will receive shadows",
        default = False
    )
    obj_type.b4a_shadow_receive = b4a_shadow_receive

    b4a_reflexible = bpy.props.BoolProperty(
        name = "B4A: reflexible",
        description = "The object will be rendered during the reflection pass",
        default = False
    )
    obj_type.b4a_reflexible = b4a_reflexible

    b4a_reflexible_only = bpy.props.BoolProperty(
        name = "B4A: reflexible only",
        description = "The object will not be rendered, but will have a reflection",
        default = False
    )
    obj_type.b4a_reflexible_only = b4a_reflexible_only

    b4a_reflective = bpy.props.BoolProperty(
        name = "B4A: reflective",
        description = "The object will receive reflections",
        default = False,
        update = lambda self,context: add_remove_refl_plane(self)
    )
    obj_type.b4a_reflective = b4a_reflective

    b4a_caustics = bpy.props.BoolProperty(
        name = "B4A: caustics",
        description = "The object will receive caustics from water",
        default = False
    )
    obj_type.b4a_caustics = b4a_caustics

    obj_type.b4a_use_default_animation = bpy.props.BoolProperty(
        name = "B4A: use default animation",
        description = "The object will be animated if possible",
        default = False
    )
    obj_type.b4a_anim_behavior = bpy.props.EnumProperty(
        name = "B4A: animation behavior",
        description = "The behavior of finished animation: stop, repeat or reset",
        default = "FINISH_STOP",
        items = [
            ("CYCLIC", "Cyclic", "Behavior: cyclically repeat the finished animation"),
            ("FINISH_RESET", "Finish reset", "Behavior: reset the finished animation"),
            ("FINISH_STOP", "Finish stop", "Behavior: stop the finished animation")
        ]
    )
    obj_type.b4a_animation_mixing = bpy.props.BoolProperty(
        name = "B4A: animation mixing",
        description = "Allow skeletal animations to be mixed with each other",
        default = False
    )

    b4a_group_relative = bpy.props.BoolProperty(
        name = "B4A: group relative",
        description = "Use relative coords for group objects",
        default = False
    )
    obj_type.b4a_group_relative = b4a_group_relative

    obj_type.b4a_proxy_inherit_anim = bpy.props.BoolProperty(
        name = "B4A: inherit animation",
        description = "Inherit animation from proxy object to proxy source",
        default = True
    )

    b4a_wind_bending = bpy.props.BoolProperty(
        name = "B4A: wind bending",
        description = "Object will be bent by wind",
        default = False
    )
    obj_type.b4a_wind_bending = b4a_wind_bending

    b4a_wind_bending_angle = bpy.props.FloatProperty(
        name = "B4A: wind bending max angle",
        description = "Maximum angle amplitude of wind bending",
        default = 10.0,
        min = 0.0,
        soft_max = 90,
        precision = 1
    )
    obj_type.b4a_wind_bending_angle = b4a_wind_bending_angle

    b4a_wind_bending_freq = bpy.props.FloatProperty(
        name = "B4A: wind bending frequency",
        description = "Wind bending frequency in Hz",
        default = 0.25,
        min = 0.0,
        soft_max = 5.0,
        precision = 2
    )
    obj_type.b4a_wind_bending_freq = b4a_wind_bending_freq
    b4a_detail_bending_amp = bpy.props.FloatProperty(
        name = "B4A: detail bending amplitude",
        description = "Detail bending amplitude",
        default = 0.1,
        min = 0.0,
        soft_max = 1.0,
        precision = 4
    )
    obj_type.b4a_detail_bending_amp = b4a_detail_bending_amp

    b4a_branch_bending_amp = bpy.props.FloatProperty(
        name = "B4A: branch bending amplitude",
        description = "Branch bending amplitude",
        default = 0.3,
        min = 0.0,
        soft_max = 1.0,
        precision = 4
    )
    obj_type.b4a_branch_bending_amp = b4a_branch_bending_amp

    b4a_detail_bending_freq = bpy.props.FloatProperty(
        name = "B4A: detail bending frequency",
        description = "Wind bending detail frequency coefficient",
        default = 1.0,
        min = 0.0,
        soft_max = 5.0,
        precision = 3
    )
    obj_type.b4a_detail_bending_freq = b4a_detail_bending_freq

    b4a_main_bend_stiffness_col = bpy.props.StringProperty(
        name = "B4A: Main stiffness vertex color",
        description = "Vertex color for main bending stiffness (A channel)",
        default = ""
    )
    obj_type.b4a_main_bend_stiffness_col = b4a_main_bend_stiffness_col

    b4a_selectable = bpy.props.BoolProperty(
        name = "B4A: selectable",
        description = "Object can be selected (color picking) and glowed",
        default = False
    )
    obj_type.b4a_selectable = b4a_selectable

    b4a_billboard = bpy.props.BoolProperty(
        name = "B4A: billboard",
        description = "Object billboarding",
        default = False
    )
    obj_type.b4a_billboard = b4a_billboard

    b4a_billboard_geometry = bpy.props.EnumProperty(
        name = "B4A: billboard geometry",
        description = "Object billboarding geometry",
        default = "SPHERICAL",
        items = [
            ("SPHERICAL", "Spherical", "Spherical billboarding"),
            ("CYLINDRICAL", "Cylindrical", "Cylindrical billboarding"),
        ]
    )
    obj_type.b4a_billboard_geometry = b4a_billboard_geometry

    obj_type.b4a_glow_settings = bpy.props.PointerProperty(
        name = "B4A: glow settings",
        type = B4A_GlowSettings
    )

    obj_type.b4a_collision = bpy.props.BoolProperty(
        name = "B4A: detect collisions",
        description = "Object will be tested for collisions",
        default = False
    )
    obj_type.b4a_collision_id = bpy.props.StringProperty(
        name = "B4A: collision ID",
        description = "Collision ID for internal application purposes",
        default = ""
    )

    obj_type.b4a_vehicle = bpy.props.BoolProperty(
        name = "B4A: enable vehicle",
        description = "Object will be part of the vehicle",
        default = False
    )

    obj_type.b4a_vehicle_settings = bpy.props.PointerProperty(
        name = "B4A: vehicle settings",
        type = B4A_VehicleSettings
    )

    obj_type.b4a_floating = bpy.props.BoolProperty(
        name = "B4A: enable floating",
        description = "Object will react to water surface",
        default = False
    )

    obj_type.b4a_floating_settings = bpy.props.PointerProperty(
        name = "B4A: floating settings",
        type = B4A_FloatingSettings
    )

    obj_type.b4a_character = bpy.props.BoolProperty(
        name = "B4A: enable character",
        description = "Object will be controlled by the player",
        default = False
    )

    obj_type.b4a_character_settings = bpy.props.PointerProperty(
        name = "B4A: character settings",
        type = B4A_CharacterSettings
    )

    # not exported
    obj_type.b4a_anim_clean_keys = bpy.props.BoolProperty(
        name = "B4A: animation clean keys",
        description = "Perform clean keyframes optimization after animation baking",
        default = True
    )

    # not exported
    obj_type.b4a_loc_export_vertex_anim = bpy.props.BoolProperty(
        name = "B4A: export vertex animation",
        description = "Export baked vertex animation",
        default = False
    )

    obj_type.b4a_lod_transition = bpy.props.FloatProperty(
        name = "B4A: LOD transition ratio",
        description = "LOD transition ratio",
        default = 0.01,
        min = 0.00,
        max = 100,
        soft_min = 0,
        soft_max = 1,
        step = 1,
        precision = 3
    )

    # deprecated
    b4a_lod_distance = bpy.props.FloatProperty(
        name = "B4A: LOD distance",
        description = "LOD maximum distance",
        default = 10000,
        min = 0.0,
        max = 100000,
        soft_min = 0,
        soft_max = 10000,
        step = 10,
        precision = 2
    )
    obj_type.b4a_lod_distance = b4a_lod_distance

    # deprecated
    obj_type.b4a_lods = bpy.props.CollectionProperty(
            type=B4A_LodProperty,
            name="B4A: LODS")
    # deprecated
    obj_type.b4a_lod_index = bpy.props.IntProperty(
            name="B4A: LOD index",
            description="LOD index used in the interface",
            default=0, min=0, max=100, soft_min=0, soft_max=5
    )
    # deprecated
    obj_type.b4a_refl_plane_index = bpy.props.IntProperty(
            name="B4A: Reflection Plane index",
            description="Reflection plane index used in the interface",
            default=0, min=0, max=100, soft_min=0, soft_max=5
    )

    obj_type.b4a_detail_bend_colors = bpy.props.PointerProperty(
            type=B4A_DetailBendingColors,
            name="B4A: Detail Bend")

    obj_type.b4a_correct_bounding_offset = bpy.props.EnumProperty(
        name = "B4A: correct the bounding box",
        description = "Correct the bounding box",
        default = "AUTO",
        items = [
            ("AUTO", "AUTO", "Auto selection bounding offset"),
            ("OFF",  "OFF",  "Disable bounding offset correction"),
            ("ON",   "ON",   "Enable bounding offset correction")
        ]
    )

def add_speaker_properties():
    """Add properties for the speaker panel"""

    spk_type = bpy.types.Speaker

    spk_type.b4a_behavior = bpy.props.EnumProperty(
        name = "B4A: speaker behavior",
        description = "Speaker behavior",
        default = "POSITIONAL",
        items = [
            ("POSITIONAL", "Positional sound", "Positional speaker"),
            ("BACKGROUND_SOUND", "Background sound", "Background sound"),
            ("BACKGROUND_MUSIC", "Background music", "Background music")
        ]
    )
    spk_type.b4a_disable_doppler = bpy.props.BoolProperty(
        name = "B4A: disable doppler",
        description = "Disable the Doppler effect",
        default = False
    )

    spk_type.b4a_cyclic_play = bpy.props.BoolProperty(
        name = "B4A: cyclic play",
        description = "Loop speaker play",
        default = False
    )
    spk_type.b4a_delay = bpy.props.FloatProperty(
        name = "B4A: delay",
        description = "Delay after playback start",
        default = 0.0,
        min = 0.0,
        soft_max = 120,
        precision = 3
    )
    spk_type.b4a_delay_random = bpy.props.FloatProperty(
        name = "B4A: random delay",
        description = "Randomized delay increment",
        default = 0.0,
        min = 0.0,
        soft_max = 120,
        precision = 3
    )

    spk_type.b4a_volume_random = bpy.props.FloatProperty(
        name = "B4A: random volume",
        description = "Randomized volume decrement",
        default = 0.0,
        min = 0.0,
        max = 1.0,
        step = 0.1,
        precision = 3
    )

    spk_type.b4a_pitch_random = bpy.props.FloatProperty(
        name = "B4A: random volume",
        description = "Randomized pitch increment",
        default = 0.0,
        min = 0.0,
        soft_max = 120,
        step = 0.1,
        precision = 3
    )

    spk_type.b4a_fade_in = bpy.props.FloatProperty(
        name = "B4A: fade-in interval",
        description = "Fade-in interval",
        default = 0.0,
        min = 0.0,
        soft_max = 120,
        step = 0.1,
        precision = 3
    )
    spk_type.b4a_fade_out = bpy.props.FloatProperty(
        name = "B4A: fade-out interval",
        description = "Fade-out interval",
        default = 0.0,
        min = 0.0,
        soft_max = 120,
        step = 0.1,
        precision = 3
    )

    spk_type.b4a_loop = bpy.props.BoolProperty(
        name = "B4A: loop",
        description = "Make loop",
        default = False
    )
    spk_type.b4a_loop_count = bpy.props.IntProperty(
        name = "B4A: loop count",
        description = "Max count of loop repeats, 0 for infinite looping",
        default = 0,
        min = 0,
        max = 1000
    )
    spk_type.b4a_loop_count_random = bpy.props.IntProperty(
        name = "B4A: random loop count",
        description = "Randomized loop count increment",
        default = 0,
        min = 0,
        max = 1000
    )

    spk_type.b4a_playlist_id = bpy.props.StringProperty(
        name = "B4A: playlist ID",
        description = "Playlist ID",
        default = ""
    )

def add_material_properties():
    """Add properties for the material panel"""

    mat_type = bpy.types.Material

    mat_type.b4a_water = bpy.props.BoolProperty(
        name = "B4A: water",
        description = "Special water material",
        default = False
    )
    mat_type.b4a_water_shore_smoothing = bpy.props.BoolProperty(
        name = "B4A: shore smoothing",
        description = "Perform the smoothing between the water and the shore objects",
        default = False
    )
    mat_type.b4a_water_dynamic = bpy.props.BoolProperty(
        name = "B4A: water dynamic",
        description = "Dynamic water surface",
        default = False
    )
    mat_type.b4a_waves_height = bpy.props.FloatProperty(
        name = "B4A: waves height",
        description = "Waves height",
        default = 0.0,
        min = 0.0,
        soft_min = 0.0,
        max = 10.0,
        soft_max = 5.0,
        step = 0.1,
        precision = 3
    )
    mat_type.b4a_waves_length = bpy.props.FloatProperty(
        name = "B4A: waves length",
        description = "Waves length",
        default = 10.0,
        min = 0.01,
        soft_min = 0.01,
        max = 200.0,
        soft_max = 100.0,
        step = 0.1,
        precision = 3
    )
    mat_type.b4a_water_absorb_factor = bpy.props.FloatProperty(
        name = "B4A: water absorbtion factor",
        description = "Water absorbtion factor",
        default = 6.0,
        min = 0.0,
        soft_min = 0.0,
        max = 100.0,
        soft_max = 1.0,
        step = 0.1,
        precision = 3
    )
    mat_type.b4a_water_dst_noise_scale0 = bpy.props.FloatProperty(
        name = "B4A: distant noise scale",
        description = "Distant waves noise scale (first component)",
        default = 0.05,
        min = 0.0,
        soft_min = 0.0,
        max = 1.0,
        soft_max = 1.0,
        step = 0.1,
        precision = 3
    )
    mat_type.b4a_water_dst_noise_scale1 = bpy.props.FloatProperty(
        name = "B4A: distant noise scale factor",
        description = "Distant waves noise scale (second component)",
        default = 0.03,
        min = 0.0,
        soft_min = 0.0,
        max = 1.0,
        soft_max = 1.0,
        step = 0.1,
        precision = 3
    )
    mat_type.b4a_water_dst_noise_freq0 = bpy.props.FloatProperty(
        name = "B4A: distant noise frequency",
        description = "Distant waves noise frequency (first component)",
        default = 1.3,
        min = 0.0,
        soft_min = 0.0,
        max = 10.0,
        soft_max = 10.0,
        step = 0.1,
        precision = 3
    )
    mat_type.b4a_water_dst_noise_freq1 = bpy.props.FloatProperty(
        name = "B4A: distant noise frequency",
        description = "Distant waves noise frequency (second component)",
        default = 1.0,
        min = 0.0,
        soft_min = 0.0,
        max = 10.0,
        soft_max = 10.0,
        step = 0.1,
        precision = 3
    )
    mat_type.b4a_water_dir_min_shore_fac = bpy.props.FloatProperty(
        name = "B4A: directional min shore factor",
        description = "Minimum shore factor for directional waves",
        default = 0.4,
        min = 0.0,
        soft_min = 0.0,
        max = 1.0,
        soft_max = 1.0,
        step = 0.1,
        precision = 3
    )
    mat_type.b4a_water_dir_freq = bpy.props.FloatProperty(
        name = "B4A: directional waves frequency",
        description = "Directional waves frequency",
        default = 0.5,
        min = 0.0,
        soft_min = 0.0,
        max = 10.0,
        soft_max = 10.0,
        step = 0.1,
        precision = 3
    )
    mat_type.b4a_water_dir_noise_scale = bpy.props.FloatProperty(
        name = "B4A: directional noise scale",
        description = "Directional waves noise scale",
        default = 0.05,
        min = 0.0,
        soft_min = 0.0,
        max = 1.0,
        soft_max = 5.0,
        step = 0.1,
        precision = 3
    )
    mat_type.b4a_water_dir_noise_freq = bpy.props.FloatProperty(
        name = "B4A: directional noise frequency",
        description = "Directional waves noise frequency",
        default = 0.07,
        min = 0.0,
        soft_min = 0.0,
        max = 1.0,
        soft_max = 1.0,
        step = 0.1,
        precision = 3
    )
    mat_type.b4a_water_dir_min_noise_fac = bpy.props.FloatProperty(
        name = "B4A: directional minimum noise factor",
        description = "Directional waves minimum noise factor",
        default = 0.5,
        min = 0.0,
        soft_min = 0.0,
        max = 1.0,
        soft_max = 1.0,
        step = 0.1,
        precision = 3
    )
    mat_type.b4a_water_dst_min_fac = bpy.props.FloatProperty(
        name = "B4A: distant waves min factor",
        description = "Distant waves min factor",
        default = 0.2,
        min = 0.0,
        soft_min = 0.0,
        max = 1.0,
        soft_max = 1.0,
        step = 0.1,
        precision = 3
    )
    mat_type.b4a_water_waves_hor_fac = bpy.props.FloatProperty(
        name = "B4A: waves horizontal factor",
        description = "Waves horizontal factor",
        default = 5.0,
        min = 0.0,
        soft_min = 0.0,
        max = 10.0,
        soft_max = 10.0,
        step = 0.1,
        precision = 3
    )
    mat_type.b4a_water_absorb_factor = bpy.props.FloatProperty(
        name = "B4A: water absorb factor",
        description = "Water absorb factor",
        default = 6.0,
        min = 0.0,
        soft_min = 0.0,
        max = 100.0,
        soft_max = 100.0,
        step = 0.1,
        precision = 3
    )
    mat_type.b4a_generated_mesh = bpy.props.BoolProperty(
        name = "B4A: water generated mesh",
        description = "Generate a multigrid mesh for the water",
        default = False
    )
    mat_type.b4a_water_num_cascads = bpy.props.IntProperty(
        name = "B4A: water num cascades",
        description = "Number of cascades in the water mesh",
        default = 5,
        min = 1,
        soft_min = 1,
        max = 20,
        soft_max = 20,
    )
    mat_type.b4a_water_subdivs = bpy.props.IntProperty(
        name = "B4A: water subdivs",
        description = "Number of subdivisions in the water mesh cascade (must be POT)",
        default = 64,
        min = 2,
        soft_min = 1,
        max = 512,
        soft_max = 512,
    )
    mat_type.b4a_water_detailed_dist = bpy.props.IntProperty(
        name = "B4A: water detailed distance",
        description = "Distance of the biggest cascade in the water mesh",
        default = 1000,
        min = 1,
        soft_min = 1,
        max = 10000,
        soft_max = 5000,
    )
    mat_type.b4a_water_fog_color = bpy.props.FloatVectorProperty(
        name = "B4A: water fog color",
        description = "Color of fog applied to the underwater objects",
        default = (0.5, 0.5, 0.5),
        min = 0.0,
        soft_min = 0.0,
        max = 1.0,
        soft_max = 1.0,
        precision = 3,
        subtype = 'COLOR',
        size = 3
    )
    mat_type.b4a_water_fog_density = bpy.props.FloatProperty(
        name = "B4A: water fog density",
        description = "Density of fog applied to the underwater objects",
        default = 0.06,
        min = 0.0,
        soft_min = 0.0,
        max = 1.0,
        soft_max = 1.0,
        step = 0.1,
        precision = 4
    )
    mat_type.b4a_foam_factor = bpy.props.FloatProperty(
        name = "B4A: foam factor",
        description = "Water foam intensity factor",
        default = 0.5,
        min = 0.0,
        soft_min = 0.0,
        max = 1.0,
        soft_max = 1.0,
        step = 0.01,
        precision = 3
    )
    mat_type.b4a_shallow_water_col = bpy.props.FloatVectorProperty(
        name = "B4A: shallow water color",
        description = "Color of the shallow water",
        default = (0.0, 0.8, 0.3),
        min = 0,
        soft_min = 0,
        max = 1,
        soft_max = 1,
        subtype = 'COLOR',
    )
    mat_type.b4a_shore_water_col = bpy.props.FloatVectorProperty(
        name = "B4A: shore water color",
        description = "Color of the shallow water",
        default = (0.0, 0.9, 0.2),
        min = 0,
        soft_min = 0,
        max = 1,
        soft_max = 1,
        subtype = 'COLOR',
    )
    mat_type.b4a_shallow_water_col_fac = bpy.props.FloatProperty(
        name = "B4A: shallow water col factor",
        description = "Shallow water color factor",
        default = 1.0,
        min = 0.0,
        max = 2.0,
        step = 0.01,
        precision = 2,
    )
    mat_type.b4a_shore_water_col_fac = bpy.props.FloatProperty(
        name = "B4A: shore water col factor",
        description = "Shore water color factor",
        default = 0.5,
        min = 0.0,
        max = 2.0,
        step = 0.01,
        precision = 2,
    )
    mat_type.b4a_water_sss_strength = bpy.props.FloatProperty(
        name = "B4A: water sss strength",
        description = "Strength of subsurface scattering",
        default = 5.9,
        min = 0.0,
        max = 100.0,
        step = 0.1,
        precision = 2,
    )
    mat_type.b4a_water_sss_width = bpy.props.FloatProperty(
        name = "B4A: water sss strength",
        description = "Width of subsurface scattering",
        default = 0.45,
        min = 0.0,
        max = 1.0,
        step = 0.01,
        precision = 2,
    )

    mat_type.b4a_terrain = bpy.props.BoolProperty(
        name = "B4A: Terrain dynamic grass",
        description = "Special material for terrain dynamic grass",
        default = False
    )
    mat_type.b4a_dynamic_grass_size = bpy.props.StringProperty(
        name = "B4A: Dynamic grass size",
        description = "Optional vertex color used for grass sizing (R)",
        default = ""
    )
    mat_type.b4a_dynamic_grass_color = bpy.props.StringProperty(
        name = "B4A: Dynamic grass color",
        description = "Optional vertex color used for grass tinting",
        default = ""
    )

    mat_type.b4a_collision = bpy.props.BoolProperty(
        name = "B4A: collision",
        description = "Special collision material",
        default = False
    )
    mat_type.b4a_use_ghost = bpy.props.BoolProperty(
        name = "B4A: Ghost",
        description = "Material does not react to collisions like a ghost",
        default = False
    )
    mat_type.b4a_collision_id = bpy.props.StringProperty(
        name = "B4A: collision ID",
        description = "Collision ID for internal application purposes",
        default = ""
    )

    mat_type.b4a_double_sided_lighting = bpy.props.BoolProperty(
        name = "B4A: double-sided lighting",
        description = "Enable double-sided lighting for the material by flipping the normals",
        default = False
    )

    mat_type.b4a_refractive = bpy.props.BoolProperty(
        name = "B4A: refraction",
        description = "Enable refraction for the material by using normal",
        default = False
    )
    mat_type.b4a_refr_bump = bpy.props.FloatProperty(
        name = "B4A: refraction bump",
        description = "Perturbation power of refraction",
        default = 0.001,
        min = 0.0,
        max = 0.2
    )

    mat_type.b4a_halo_sky_stars = bpy.props.BoolProperty(
        name = "B4A: halo sky stars",
        description = "Make halo material stars object",
        default = False
    )

    mat_type.b4a_halo_stars_blend_height = bpy.props.FloatProperty(
        name = "B4A: halo stars blending height",
        description = "Stars blending height",
        default = 10.0
    )

    mat_type.b4a_halo_stars_min_height = bpy.props.FloatProperty(
        name = "B4A: halo stars minimum height",
        description = "Stars minimum height starting from the origin",
        default = 0.0
    )

    mat_type.b4a_collision_group = bpy.props.BoolVectorProperty(
        name = "B4A: collision group",
        subtype = "LAYER",
        description = "Material collision group",
        default = (False, False, False, False, False, False, False, True),
        size = 8
    )

    mat_type.b4a_collision_mask = bpy.props.BoolVectorProperty(
        name = "B4A: collision mask",
        subtype = "LAYER",
        description = "Material collision mask",
        default = (True, True, True, True, True, True, True, False),
        size = 8
    )

    mat_type.b4a_wettable = bpy.props.BoolProperty(
        name = "B4A: wettable",
        description = "Material will get wet near water",
        default = False,
    )

    mat_type.b4a_render_above_all = bpy.props.BoolProperty(
        name = "B4A: render above all",
        description = "Material will be render above all others",
        default = False,
    )


def add_texture_properties():
    """Add properties for texture panel"""

    b4a_use_map_parallax = bpy.props.BoolProperty(
        name = "B4A: use map parallax",
        description = "The texture's alpha channel will be used as the heightmap for warping",
        default = False
    )
    bpy.types.Texture.b4a_use_map_parallax = b4a_use_map_parallax

    b4a_parallax_scale = bpy.props.FloatProperty(
        name = "B4A: parallax scale",
        description = "Scale parameter for texture warping. Height (e.g. 3 cm) is devided by the texture covering size (e.g. 1.5 m)",
        default = 0.02,
        min = 0.0,
        soft_max = 0.1,
        precision = 3
    )
    bpy.types.Texture.b4a_parallax_scale = b4a_parallax_scale;

    b4a_parallax_steps = bpy.props.IntProperty(
        name = "B4A: parallax steps",
        description = "Number of steps taken to build a parallax surface (the more the better)",
        default = 5,
        soft_max = 30,
        min = 1,
        max = 30
    )
    bpy.types.Texture.b4a_parallax_steps = b4a_parallax_steps;

    b4a_parallax_lod_dist = bpy.props.IntProperty(
        name = "B4A: parallax lod distance",
        description = "Level of detail distance for parallax mapping",
        default = 5,
        soft_max = 30,
        min = 1,
        max = 30
    )
    bpy.types.Texture.b4a_parallax_lod_dist = b4a_parallax_lod_dist;

    # see also b4a_anisotropic_filtering for scene
    b4a_anisotropic_filtering = bpy.props.EnumProperty(
        name = "B4A: anisotropic filtering",
        description = "Anisotropic filtering for the texture",
        items = [
            ("DEFAULT", "DEFAULT", "0", 0),
            ("OFF",     "OFF",     "1", 1),
            ("2x",      "2x",      "2", 2),
            ("4x",      "4x",      "3", 3),
            ("8x",      "8x",      "4", 4),
            ("16x",     "16x",     "5", 5)
        ]
    )
    bpy.types.Texture.b4a_anisotropic_filtering = b4a_anisotropic_filtering

    b4a_use_sky = bpy.props.EnumProperty(
        name = "B4A: environment lighting",
        description = "Use texture as skydome or environment lighting",
        items = [
            ("OFF",                  "OFF",                 "0", 0),
            ("SKYDOME",              "SKYDOME",             "1", 1),
            ("ENVIRONMENT_LIGHTING", "ENVIRONMENT_LIGHTING","2", 2),
            ("BOTH",                 "BOTH",                "3", 3)
        ]
    )
    bpy.types.Texture.b4a_use_sky = b4a_use_sky

    # NOTE: it is saved to texture, so there may be issues when textures are shared between materials
    b4a_uv_velocity_trans = bpy.props.FloatVectorProperty(
        name = "B4A: UV translation velocity",
        description = "UV translation velocity for the animated texture",
        default = (0.0, 0.0),
        min = -99.0,
        max = 99.0,
        precision = 3,
        size = 2
    )
    bpy.types.Texture.b4a_uv_velocity_trans = b4a_uv_velocity_trans

    b4a_water_foam = bpy.props.BoolProperty(
        name = "B4A: Water foam",
        description = "Use texture as foam on the water surface",
        default = False
    )
    bpy.types.Texture.b4a_water_foam = b4a_water_foam

    b4a_foam_uv_freq = bpy.props.FloatVectorProperty(
        name = "B4A: Foam UV frequency",
        description = "Foam UV translation frequency",
        default = (1.0, 1.0),
        min = -99.0,
        max = 99.0,
        precision = 3,
        size = 2
    )
    bpy.types.Texture.b4a_foam_uv_freq = b4a_foam_uv_freq

    b4a_foam_uv_magnitude = bpy.props.FloatVectorProperty(
        name = "B4A: Foam UV magnitude",
        description = "Foam UV translation frequency",
        default = (1.0, 1.0),
        min = -99.0,
        max = 99.0,
        precision = 3,
        size = 2
    )
    bpy.types.Texture.b4a_foam_uv_magnitude = b4a_foam_uv_magnitude

    b4a_shore_dist_map = bpy.props.BoolProperty(
        name = "B4A: Shore distance map",
        description = "Use the texture as a shore distance map on the water surface",
        default = False
    )
    bpy.types.Texture.b4a_shore_dist_map = b4a_shore_dist_map

    b4a_render_scene = bpy.props.StringProperty(
        name = "B4A: scene",
        description = "Name of the scene, which will be rendered on the texture",
        default = ""
    )
    bpy.types.Texture.b4a_render_scene = b4a_render_scene

    b4a_shore_boundings = bpy.props.FloatVectorProperty(
        name = "B4A: shore boundings",
        description = "Boundings of the water-to-shore distance map",
        default = (0.0, 0.0, 0.0, 0.0),
        min = -100000.0,
        soft_min = -100000.0,
        max = 100000.0,
        soft_max = 100000.0,
        precision = 2,
        size = 4
    )
    bpy.types.Texture.b4a_shore_boundings = b4a_shore_boundings

    b4a_max_shore_dist = bpy.props.FloatProperty(
        name = "B4A: maximum shore distance",
        description = "Maximum distance to shore in meters (taken as 1.0)",
        default = 100.0,
        min = 0.0,
        max = 100000.0,
        step = 5.0,
        precision = 1,
    )
    bpy.types.Texture.b4a_max_shore_dist = b4a_max_shore_dist

    b4a_disable_compression = bpy.props.BoolProperty(
        name = "B4A: disable compression",
        description = "Do not use DDS file for this texture",
        default = False
    )
    bpy.types.Texture.b4a_disable_compression = b4a_disable_compression

def add_particle_settings_properties():
    """Add properties for particles panel"""

    pset_type = bpy.types.ParticleSettings

    # "EMITTER"

    pset_type.b4a_cyclic = bpy.props.BoolProperty(
        name = "B4A: cyclic emission",
        description = "Loop particles emission",
        default = False
    )

    pset_type.b4a_allow_nla = bpy.props.BoolProperty(
        name = "B4A: allow NLA",
        description = "Allow particles emission to be controlled by the NLA",
        default = True
    )

    b4a_randomize_emission = bpy.props.BoolProperty(
        name = "B4A: randomize emission",
        description = "Randomize the delay for particles emission",
        default = False
    )
    pset_type.b4a_randomize_emission = b4a_randomize_emission

    b4a_fade_in = bpy.props.FloatProperty(
        name = "B4A: fade-in interval",
        description = "Fade-in interval for particles",
        default = 0.0,
        min = 0.0,
        soft_max = 120,
        precision = 3
    )
    pset_type.b4a_fade_in = b4a_fade_in

    b4a_fade_out = bpy.props.FloatProperty(
        name = "B4A: fade-out interval",
        description = "Fade-out interval for particles",
        default = 0.0,
        min = 0.0,
        soft_max = 120,
        precision = 3
    )
    pset_type.b4a_fade_out = b4a_fade_out

    pset_type.b4a_billboard_align = bpy.props.EnumProperty(
        name = "B4A: billboard align",
        description = "Billboard alignment in the world space",
        default = "VIEW",
        items = [
            ("VIEW", "View", "Align to view (active camera)"),
            ("XY", "XY plane", "Align in XY plane"),
            ("YZ", "YZ plane", "Align in YZ plane"),
            ("ZX", "ZX plane", "Align in ZX plane")
        ]
    )

    pset_type.b4a_coordinate_system = bpy.props.EnumProperty(
        name = "B4A: coordinate system",
        description = "Particles coordinate system",
        items = [
            ("WORLD", "World", "World coordinate system"),
            ("LOCAL", "Local", "Emitter's coordinate system"),
        ],
        default = "LOCAL"
    )

    # "HAIR"

    pset_type.b4a_dynamic_grass = bpy.props.BoolProperty(
        name = "B4A: dynamic grass",
        description = "Render on the terrain materials as dynamic grass",
        default = False
    )
    pset_type.b4a_dynamic_grass_scale_threshold = bpy.props.FloatProperty(
        name = "B4A: dynamic grass scale threshold",
        description = "Scale threshold for dynamic grass",
        default = 0.01,
        min = 0.0,
        max = 1.0,
        step = 5.0,
        precision = 3
    )
    pset_type.b4a_randomize_location = bpy.props.BoolProperty(
        name = "B4A: randomize location and size",
        description = "Randomize location and size (±25%) of hair particle objects",
        default = True
    )
    pset_type.b4a_initial_rand_rotation = bpy.props.BoolProperty(
        name = "B4A: initial random rotation",
        description = "Initial random rotation of hair particle objects",
        default = True
    )
    pset_type.b4a_rand_rotation_strength = bpy.props.FloatProperty(
        name = "B4A: random rotation strength",
        description = "Strength of initial random rotation",
        default = 1.0,
        min = 0.0,
        max = 1.0,
        precision = 3
    )
    pset_type.b4a_rotation_type = bpy.props.EnumProperty(
        name = "B4A: rotation type",
        description = "Rotation type of hair particle objects",
        default = "Z",
        items = [
            ("Z", "Z axis", "Rotation around Z axis"),
            ("XYZ", "Random axis", "Rotation around random axis"),
        ]
    )

    pset_type.b4a_hair_billboard = bpy.props.BoolProperty(
        name = "B4A: hair billboard",
        description = "Make billboards from hair particle objects",
        default = False
    )
    pset_type.b4a_hair_billboard_type = bpy.props.EnumProperty(
        name = "B4A: hair billboard type",
        description = "Hair billboard type",
        default = "BASIC",
        items = [
            ("BASIC", "Basic", "Basic one-sided billboarding"),
            ("RANDOM", "Random", "Random two-sided billboarding"),
            ("JITTERED", "Jittered", "One-sided billboarding with jittering"),
        ]
    )
    pset_type.b4a_hair_billboard_jitter_amp = bpy.props.FloatProperty(
        name = "B4A: hair billboard jitter amp",
        description = "Coefficient of the jittering amplitude for the billboard",
        default = 0.0,
        min = 0.0,
        max = 1.0,
        step = 0.001,
        precision = 3
    )
    pset_type.b4a_hair_billboard_jitter_freq = bpy.props.FloatProperty(
        name = "B4A: hair billboard jitter freq",
        description = "Jittering frequency for the billboard, Hz",
        default = 0.0,
        min = 0.0,
        max = 100.0,
        step = 0.001,
        precision = 3
    )
    pset_type.b4a_hair_billboard_geometry = bpy.props.EnumProperty(
        name = "B4A: hair billboard geometry type",
        description = "Hair billboard geometry type",
        default = "SPHERICAL",
        items = [
            ("SPHERICAL", "Spherical", "Spherical billboarding"),
            ("CYLINDRICAL", "Cylindrical", "Cylindrical billboarding"),
        ]
    )

    pset_type.b4a_wind_bend_inheritance = bpy.props.EnumProperty(
        name = "B4A: wind bend inheritance",
        description = "Wind bending inheritance",
        items = [
            ("PARENT", "Parent", "inherit from parent"),
            ("INSTANCE", "Instance", "inherit from instance"),
        ],
        default = "PARENT"
    )

    pset_type.b4a_shadow_inheritance = bpy.props.EnumProperty(
        name = "B4A: shadow inheritance",
        description = "Shadow inheritance",
        items = [
            ("PARENT", "Parent", "inherit from parent"),
            ("INSTANCE", "Instance", "inherit from instance"),
        ],
        default = "PARENT"
    )

    pset_type.b4a_reflection_inheritance = bpy.props.EnumProperty(
        name = "B4A: reflection inheritance",
        description = "Reflection inheritance",
        items = [
            ("PARENT", "Parent", "inherit from parent"),
            ("INSTANCE", "Instance", "inherit from instance"),
        ],
        default = "PARENT"
    )

    pset_type.b4a_vcol_from_name = bpy.props.StringProperty(
        name = "B4A: vcol from name",
        description = "Vertex color from emitter",
        default = ""
    )

    pset_type.b4a_vcol_to_name = bpy.props.StringProperty(
        name = "B4A: vcol to name",
        description = "Vertex color on instance",
        default = ""
    )

def register():
    bpy.utils.register_class(B4A_LodProperty)
    bpy.utils.register_class(B4A_VehicleSettings)
    bpy.utils.register_class(B4A_GlowSettings)
    bpy.utils.register_class(B4A_FloatingSettings)
    bpy.utils.register_class(B4A_CharacterSettings)
    bpy.utils.register_class(B4A_SSAOSettings)
    bpy.utils.register_class(B4A_GodRaysSettings)
    bpy.utils.register_class(B4A_ColorCorrectionSettings)
    bpy.utils.register_class(B4A_ShadowSettings)
    bpy.utils.register_class(B4A_DetailBendingColors)
    bpy.utils.register_class(B4A_SkySettings)
    bpy.utils.register_class(B4A_BloomSettings)
    bpy.utils.register_class(B4A_FogSettings)
    bpy.utils.register_class(B4A_BackgroundSettings)
    bpy.utils.register_class(B4A_VignetteSettings)
    bpy.utils.register_class(B4A_HdrSettings)
    bpy.utils.register_class(B4A_DynamicCompressorSettings)
    bpy.utils.register_class(B4A_MotionBlurSettings)
    bpy.utils.register_class(B4A_BoundingsSettings)
    add_b4a_props()

def unregister():
    bpy.utils.unregister_class(B4A_LodProperty)
    bpy.utils.unregister_class(B4A_VehicleSettings)
    bpy.utils.unregister_class(B4A_GlowSettings)
    bpy.utils.unregister_class(B4A_FloatingSettings)
    bpy.utils.unregister_class(B4A_CharacterSettings)
    bpy.utils.unregister_class(B4A_SSAOSettings)
    bpy.utils.unregister_class(B4A_GodRaysSettings)
    bpy.utils.unregister_class(B4A_ColorCorrectionSettings)
    bpy.utils.unregister_class(B4A_ShadowSettings)
    bpy.utils.unregister_class(B4A_DetailBendingColors)
    bpy.utils.unregister_class(B4A_SkySettings)
    bpy.utils.unregister_class(B4A_BloomSettings)
    bpy.utils.unregister_class(B4A_FogSettings)
    bpy.utils.unregister_class(B4A_BackgroundSettings)
    bpy.utils.unregister_class(B4A_VignetteSettings)
    bpy.utils.unregister_class(B4A_HdrSettings)
    bpy.utils.unregister_class(B4A_DynamicCompressorSettings)
    bpy.utils.unregister_class(B4A_MotionBlurSettings)
    bpy.utils.unregister_class(B4A_BoundingsSettings)

