import bpy


from . import (
            properties_camera,
            properties_light,
            properties_material,
            properties_render,
            properties_render_layer,
            properties_world,
            )


from bl_ui import properties_scene
properties_scene.SCENE_PT_scene.COMPAT_ENGINES.add('PEARRAY_RENDER')
properties_scene.SCENE_PT_unit.COMPAT_ENGINES.add('PEARRAY_RENDER')
properties_scene.SCENE_PT_keying_sets.COMPAT_ENGINES.add('PEARRAY_RENDER')
properties_scene.SCENE_PT_color_management.COMPAT_ENGINES.add('PEARRAY_RENDER')
properties_scene.SCENE_PT_audio.COMPAT_ENGINES.add('PEARRAY_RENDER')
properties_scene.SCENE_PT_custom_props.COMPAT_ENGINES.add('PEARRAY_RENDER')
del properties_scene


from bl_ui import properties_texture
properties_texture.TEXTURE_PT_context_texture.COMPAT_ENGINES.add('PEARRAY_RENDER')
properties_texture.TEXTURE_PT_preview.COMPAT_ENGINES.add('PEARRAY_RENDER')
properties_texture.TEXTURE_PT_image.COMPAT_ENGINES.add('PEARRAY_RENDER')
properties_texture.TEXTURE_PT_image_mapping.COMPAT_ENGINES.add('PEARRAY_RENDER')
properties_texture.TEXTURE_PT_custom_props.COMPAT_ENGINES.add('PEARRAY_RENDER')
del properties_texture


from bl_ui import properties_particle as properties_particle
for member in dir(properties_particle):
    subclass = getattr(properties_particle, member)
    try:
        subclass.COMPAT_ENGINES.add('PEARRAY_RENDER')
    except:
        pass
del properties_particle


def register():
    pass


def unregister():
    pass