import bpy

def silhouette(self, context):

    option = context.scene.silhouette
    gradient = context.user_preferences.themes[0].view_3d.space.gradients
    light = context.user_preferences.system.solid_lights
    space_data = context.space_data
    addon = context.user_preferences.addons[__name__.partition('.')[0]].preferences

    if context.scene.silhouette.show_silhouette:

        option.first_light_diffuse = light[0].diffuse_color
        option.first_light_specular = light[0].specular_color
        option.second_light_diffuse = light[1].diffuse_color
        option.second_light_specular = light[1].specular_color
        option.third_light_diffuse = light[2].diffuse_color
        option.third_light_specular = light[2].specular_color

        option.using_gradient = gradient.show_grad
        option.gradient = gradient.high_gradient
        option.using_matcap = space_data.use_matcap
        option.using_render_only = space_data.show_only_render

        black = (0.0, 0.0, 0.0)
        light[0].diffuse_color = black
        light[0].specular_color = black
        light[1].diffuse_color = black
        light[1].specular_color = black
        light[2].diffuse_color = black
        light[2].specular_color = black
        gradient.show_grad = False
        gradient.high_gradient = addon.background_color
        space_data.use_matcap = False
        space_data.show_only_render = True

    else:

        light[0].diffuse_color = option.first_light_diffuse
        light[0].specular_color = option.first_light_specular
        light[1].diffuse_color = option.second_light_diffuse
        light[1].specular_color = option.second_light_specular
        light[2].diffuse_color = option.third_light_diffuse
        light[2].specular_color = option.third_light_specular
        gradient.show_grad = option.using_gradient
        gradient.high_gradient = option.gradient
        space_data.use_matcap = option.using_matcap
        space_data.show_only_render = option.using_render_only
