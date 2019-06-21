import bpy

from bpy.types import PropertyGroup
from bpy.props import BoolProperty, FloatVectorProperty

from . import state

class silhouette(PropertyGroup):

    show_silhouette = BoolProperty(
        name = 'Silhouette',
        description = 'Display silhouette.',
        update = state.silhouette,
        default = False
    )

    first_light_diffuse = FloatVectorProperty(
        name = 'First Light Diffuse',
        description = 'The user\'s orginal diffuse color value for the first light in user preferences',
        subtype = 'COLOR',
        size = 3,
        min = 0.0,
        max = 1.0,
        default = bpy.context.user_preferences.system.solid_lights[0].diffuse_color
    )

    first_light_specular = FloatVectorProperty(
        name = 'First Light Specular',
        description = 'The user\'s original specular color value for the first light in user preferences',
        subtype = 'COLOR',
        size = 3,
        min = 0.0,
        max = 1.0,
        default = bpy.context.user_preferences.system.solid_lights[0].specular_color
    )

    second_light_diffuse = FloatVectorProperty(
        name = 'Second Light Diffuse',
        description = 'The user\'s original diffuse color value for the second light in user preferences',
        subtype = 'COLOR',
        size = 3,
        min = 0.0,
        max = 1.0,
        default = bpy.context.user_preferences.system.solid_lights[1].diffuse_color
    )

    second_light_specular = FloatVectorProperty(
        name = 'Second Light Specular',
        description = 'The user\'s original specular color value for the second light in user preferences',
        subtype = 'COLOR',
        size = 3,
        min = 0.0,
        max = 1.0,
        default = bpy.context.user_preferences.system.solid_lights[1].specular_color
    )

    third_light_diffuse = FloatVectorProperty(
        name = 'Third Light Diffuse',
        description = 'The user\'s original diffuse color value for the third light in user preferences',
        subtype = 'COLOR',
        size = 3,
        min = 0.0,
        max = 1.0,
        default = bpy.context.user_preferences.system.solid_lights[2].diffuse_color
    )

    third_light_specular = FloatVectorProperty(
        name = 'Third Light Specular',
        description = 'The user\'s original specular color value for the third light in user preferences',
        subtype = 'COLOR',
        size = 3,
        min = 0.0,
        max = 1.0,
        default = bpy.context.user_preferences.system.solid_lights[2].specular_color
    )

    using_gradient = BoolProperty(
        name = 'Using Gradient',
        description = 'Storage for the state of the user preferences theme use gradient option for the 3D view.',
        default = bpy.context.user_preferences.themes['Default'].view_3d.space.gradients.show_grad
    )

    gradient = FloatVectorProperty(
        name = 'Gradient',
        description = 'The user\'s original gradient color value for the background in the user preferences.',
        subtype = 'COLOR',
        size = 3,
        min = 0.0,
        max = 1.0,
        default = bpy.context.user_preferences.themes['Default'].view_3d.space.gradients.high_gradient
    )

    using_matcap = BoolProperty(
        name = 'Using matcap',
        description = 'Storage for the state of the matcap toggle.',
        default = False
    )

    using_render_only = BoolProperty(
        name = 'Using render only',
        description = 'Storage for the state of the render only toggle.',
        default = False
    )
