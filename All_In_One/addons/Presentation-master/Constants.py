import bpy
import bpy.types
import inspect
import json

_keypoint_settings = ["co", "handle_left_type", "handle_right_type", "handle_left", "handle_right", "interpolation","amplitude", "easing"]
KEYPOINT_SETTINGS = []
for i in _keypoint_settings:
    KEYPOINT_SETTINGS.append({ i : i })
KEYPOINT_OVERRIDE = { "handle_left_type": "FREE", "handle_right_type": "FREE" }

ANIMATION_TRANSLATION = [ { "location": [{"x":0},{"y":1},{"z":2}], "json": "translate", "blender":"location" } , { "scale": [{"x":0},{"y":1},{"z":2}], "json": "scale", "blender":"scale"} , { "rotation_euler": [{"x":0},{"y":1},{"z":2}], "json": "rotation", "blender":"rotation_euler", "convert":"degrees" }]
SCENE_SETTINGS = [{"proskies.skies.use_pl_skies" : "world.pl_skies_settings.use_pl_skies"}, {"proskies.skies.sun" : "world.pl_skies_settings.sun"}, {"proskies.skies.sky" : "world.pl_skies_settings.sky"}, {"proskies.skies.z_rotation" : "world.pl_skies_settings.z_rotation"},  {"proskies.skies.evn_previews" : "world.env_previews"},{"name":"name"}]
BLENDER_SETTINGS = [{"RenderEngine": "render.engine"}, {"FrameStart": "frame_start"} , {"FrameEnd": "frame_end"}, {"samples": "cycles.samples"}, {"Device": "cycles.device"},{"fps":"render.fps"}, {"fps":"render.fps_base"}, {"resolution_x":"render.resolution_x"},
{"resolution_y": "render.resolution_y"}]
CYCLESRENDERSETTINGS = ["use_animated_seed",
        "sample_clamp_direct",
        "sample_clamp_indirect",
        "aa_samples",
        "progressive",
        "diffuse_samples",
        "glossy_samples",
        "transmission_samples",
        "ao_samples",
        "mesh_light_samples",
        "subsurface_samples",
        "volume_samples",
        "sampling_pattern",
        "transparent_max_bounces",
        "transparent_min_bounces",
        "use_transparent_shadows",
        "caustics_reflective",
        "caustics_refractive",
        "blur_glossy",
        "max_bounces",
        "film_transparent",
        "min_bounces" ,
        "diffuse_bounces",
        "glossy_bounces",
        "transmission_bounces",
        "volume_bounces"]
RENDERSETTINGS = [
        "use_compositing",
        "use_sequencer"]

IMAGE_SETTINGS = ["file_format", "film_transparent"]
CONVERT_INDEX = {"x": 0, "y": 1, "z": 2}

for ls in IMAGE_SETTINGS:
    BLENDER_SETTINGS.append({ls : "render."+ls})
for crs in CYCLESRENDERSETTINGS:
    BLENDER_SETTINGS.append({crs: "cycles."+crs})

SHADER_EMISSION = "ShaderNodeEmission"
SHADER_OUTPUT_MATERIAL = "ShaderNodeOutputMaterial"
SHADER_MIX_RGB = "ShaderNodeMixRGB"
SHADER_NODE_VALUE = "ShaderNodeValue"
SHADER_NODE_MIX = "ShaderNodeMixShader"
SHADER_NODE_DIFFUSE = "ShaderNodeBsdfDiffuse"
SHADER_WORLD_NODE_OUTPUT = "ShaderNodeOutputWorld"
SHADER_NODE_BACKGROUND = "ShaderNodeBackground"
COMPOSITOR_NODE_COMPOSITE = "CompositorNodeComposite"

DEFAULT_ENVIRONMENT = {
    "id": "TestScene_3",
    "name": "TestScene_3",
    "folder": "TestScene_3",
    "resourceType": "TestScene_3",
    "source": "empty.blend",
    "type": "composite",
    "src": "empty.png",
    "config": {
        "name": "placements",
        "group": "placements",
        "type": "custom",
        "stage_group": "Wall_Tile_05"
    },
    "camera": "default_camera",
    "composite_parameters": {
        "start_frame": 1,
        "end_frame": 178,
        "frame_count": 178,
        "environment_path": "",
        "image_type": "exr"
    },
    "scene": None,
    "billboardComposite": None,
    "composite": None,
    "proskies": None,
    "parameters": [],
    "places": [
        {
            "id": "Place01",
            "name": "Place 1",
            "src": None,
            "camerapasses": [
                "Long shot"
            ]
        }
    ]
}