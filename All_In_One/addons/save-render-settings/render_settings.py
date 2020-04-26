"""
This module has functions to save and load blender render settings (for cycles) into YAML files.

It requires `yaml` and `bpy` modules.

The settings saved are whitelisted in the global dictionary `RENDER_SETTINGS_SAVE_WHITELIST`.
This dictionary contains cycles specific settings (under the `cycles` key), and more general settings
(under the `scene` key).

# How to

## Save settings

Just call `save_render_settings()` with the blender scene and the YAML path as arguments. For example:

```python
save_render_settings(bpy.context.scene, "path/to/YAML/file")
```

## Load settings

First you need to load the settings from the file and then apply them on a scene. For example:

```python
settings = load_render_settings("path/to/YAML/file")
apply_render_settings(bpy.context.scene, settings)
```

## Check blender version

This module works with blender 2.79.
Because render settings names can change across different blender versions, the YAML file stores the version of blender
it has been saved with. At loading, you can check if the settings version matches the current blender version
with `check_settings_blender_version(settings)`.

"""

import bpy
import json


# settings whitelist
RENDER_SETTINGS_SAVE_WHITELIST = {"cycles": ["aa_samples",
                                        "ao_bounces",
                                        "ao_bounces_render",
                                        "ao_samples",
                                        "bake_type",
                                        "blur_glossy",
                                        "camera_cull_margin",
                                        "caustics_reflective",
                                        "caustics_refractive",
                                        "debug_bvh_time_steps",
                                        "debug_bvh_type",
                                        "debug_cancel_timeout",
                                        "debug_opencl_device_type",
                                        "debug_opencl_kernel_single_program",
                                        "debug_opencl_kernel_type",
                                        "debug_opencl_mem_limit",
                                        "debug_reset_timeout",
                                        "debug_text_timeout",
                                        "debug_tile_size",
                                        "debug_use_cpu_avx",
                                        "debug_use_cpu_avx2",
                                        "debug_use_cpu_split_kernel",
                                        "debug_use_cpu_sse2",
                                        "debug_use_cpu_sse3",
                                        "debug_use_cpu_sse41",
                                        "debug_use_cuda_adaptive_compile",
                                        "debug_use_cuda_split_kernel",
                                        "debug_use_hair_bvh",
                                        "debug_use_opencl_debug",
                                        "debug_use_qbvh",
                                        "debug_use_spatial_splits",
                                        "device",
                                        "dicing_rate",
                                        "diffuse_bounces",
                                        "diffuse_samples",
                                        "distance_cull_margin",
                                        "feature_set",
                                        "film_exposure",
                                        "film_transparent",
                                        "filter_type",
                                        "filter_width",
                                        "glossy_bounces",
                                        "glossy_samples",
                                        "light_sampling_threshold",
                                        "max_bounces",
                                        "max_subdivisions",
                                        "mesh_light_samples",
                                        "min_bounces",
                                        "motion_blur_position",
                                        "pixel_filter_type",
                                        "preview_aa_samples",
                                        "preview_active_layer",
                                        "preview_dicing_rate",
                                        "preview_pause",
                                        "preview_samples",
                                        "preview_start_resolution",
                                        "progressive",
                                        "rolling_shutter_duration",
                                        "rolling_shutter_type",
                                        "sample_all_lights_direct",
                                        "sample_all_lights_indirect",
                                        "sample_clamp_direct",
                                        "sample_clamp_indirect",
                                        "samples",
                                        "sampling_pattern",
                                        "seed",
                                        "shading_system",
                                        "subsurface_samples",
                                        "texture_limit",
                                        "texture_limit_render",
                                        "tile_order",
                                        "transmission_bounces",
                                        "transmission_samples",
                                        "transparent_max_bounces",
                                        "transparent_min_bounces",
                                        "use_animated_seed",
                                        "use_camera_cull",
                                        "use_distance_cull",
                                        "use_layer_samples",
                                        "use_progressive_refine",
                                        "use_square_samples",
                                        "use_transparent_shadows",
                                        "volume_bounces",
                                        "volume_max_steps",
                                        "volume_samples",
                                        "volume_step_size"],
                             "scene": ["engine",
                                       "threads",
                                       "threads_mode",
                                       "tile_x",
                                       "tile_y",
                                       "use_border",
                                       "use_compositing",
                                       "use_crop_to_border",
                                       "use_file_extension",
                                       "use_free_image_textures",
                                       "use_instances",
                                       "use_motion_blur",
                                       "use_multiview",
                                       "use_render_cache",
                                       "use_save_buffers",
                                       "use_single_layer"]}


def blender_version():
    """
    Gives the current blender version.
    :return: A `str` formatted like: "2.79.0"
    """
    return ".".join([str(i) for i in bpy.app.version])


def dump_render_settings(scene):
    """
    Retrieves the settings that are in the whitelist and put them in a `dict`.
    :param scene: the blender scene whose settings are taken from
    :return: A `dict` containing all the settings
    """
    settings = {}

    # cycles settings
    settings["cycles"] = {}
    for prop in RENDER_SETTINGS_SAVE_WHITELIST["cycles"]:
        if hasattr(scene.cycles, prop):
            settings["cycles"][prop] = getattr(scene.cycles, prop)

    # scene render settings
    settings["scene"] = {}
    for prop in RENDER_SETTINGS_SAVE_WHITELIST["scene"]:
        if hasattr(scene.render, prop):
            settings["scene"][prop] = getattr(scene.render, prop)

    # additional information
    settings["info"] = {}
    settings["info"]["blender_version"] = blender_version()

    return settings


def apply_render_settings(scene, settings):
    """
    Fill the given blender scene with the given settings.
    :param scene: Blender scene
    :param settings: `dict`with all the settings (formatted as returned by `dump_render_settings()`
    """
    for section in settings.keys():
        if section == "cycles":
            bl_object = scene.cycles
        elif section == "scene":
            bl_object = scene.render
        else:  # not a valid section
            continue
        # fill the right section with the right settings
        for prop_name, prop_val in settings[section].items():
            if hasattr(bl_object, prop_name):
                setattr(bl_object, prop_name, prop_val)


def check_settings_blender_version(settings):
    """
    Check if the settings' blender version matches the current blender version
    :param settings: `dict` of all the settings
    :return: `tuple(bool, str)`. First boolean is true with the versions are the same, false otherwise. The second \
            string contains a description of the error if versions do not match (the string is empty if they match)
    """
    if ("info" in settings) and ("blender_version" in settings["info"]):
        if settings["info"]["blender_version"] == blender_version():
            return (True, "")
        else:
            return (False, "The settings were saved from a different blender version (" +
                    settings["info"]["blender_version"] + ") than the current one (" +
                    blender_version() + ").")
    else:
        return (False, "The settings file has no blender version information attached, and may have " +
                       "been saved with a different version than the current one.")


def save_render_settings(scene, path):
    """
    Saves the scene's render settings into a JSON file
    :param scene: Blender scene
    :param path: Path to JSON file
    """
    settings = dump_render_settings(scene)
    with open(path, 'w') as file:
        json.dump(settings, file)


def load_render_settings(path):
    """
    Loads and returns settings from a YAML file
    :param path: path of the YAML file
    """
    with open(path, 'r') as file:
        return json.load(file)

