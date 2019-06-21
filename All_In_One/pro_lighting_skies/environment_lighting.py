# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

import os
import json
from math import radians
import mathutils
import bpy
import zipfile
import shutil
from bpy.types import Operator
from bpy.types import Panel
from bpy.types import PropertyGroup
from bpy.props import BoolProperty
from bpy.props import IntProperty
from bpy.props import FloatProperty
from bpy.props import EnumProperty
from bpy.props import FloatVectorProperty
from bpy.props import PointerProperty
from bpy.types import AddonPreferences
from bpy_extras.io_utils import ImportHelper
from bpy.app.handlers import persistent

use_icons = False
try:
    import bpy.utils.previews
    use_icons = True
except:
    pass


# global variables ------------------------------------------------------------

environments = []
categories = []
sublist = []
category_selected = ""
newload = False
temp_node_change = False # called by changing 'used advanced settings'
internal_fave_change = False # for active favorite updates


# update check, ensure we use the new json file
if os.path.isfile(os.path.join(os.path.dirname(__file__), "envs_update.json")):
    tmp = os.path.join(os.path.dirname(__file__), "envs_update.json")
    tmp1 = os.path.join(os.path.dirname(__file__), "envs.json")
    try:
        os.remove(tmp1)
    except:
        pass
    os.rename(tmp,tmp1)

with open(os.path.join(os.path.dirname(__file__), "envs.json")) as data_file:
    # format: ("label", "description", "file_naming", "sun", "sky")
    data = json.load(data_file) # better to fail if this loads wrong
    environments = data["environments"]
    categories = data["categories"]

# dict to hold the ui previews collection
preview_collections = {}
thumb_ids = {}


# create the previews and enum with label, tooltip and preview as custom icon
def generate_previews():
    env_previews = preview_collections["env_previews"]
    folder_path = env_previews.imgs_dir
    global thumb_ids

    enum_items = []
    i = 0

    # get the category name
    try:
        items_in_category = categories[category_selected]
    except:
        items_in_category = "all"
    global sublist
    sublist = []

    for label, desc, img_name, sun, sky in environments:
        if os.path.isfile( os.path.join(\
            folder_path, img_name + "_thumb.jpg") )==False: continue


        if img_name not in thumb_ids:
            # try catch?
            thumb = env_previews.load(
                img_name,
                os.path.join(folder_path, img_name + "_thumb.jpg"),
                'IMAGE'
            )
            thumb_ids[img_name] = thumb.icon_id
            thumb = thumb.icon_id
        else:
            thumb = thumb_ids[img_name]

        if items_in_category!="all" and \
            img_name not in items_in_category: continue
        enum_items.append((img_name, label, desc, thumb, i))
        sublist.append( (label, desc, img_name, sun, sky) ) # for categories
        i += 1
    return enum_items


# if preview icons are unavailable
def generate_previews_text():
    env_previews = preview_collections["env_previews"]
    folder_path = env_previews.imgs_dir
    global sublist
    sublist = []

    enum_items = []
    i = 0

    # get the category name
    try:
        items_in_category = categories[category_selected]
    except:
        items_in_category = "all"

    for label, desc, img_name, sun, sky in environments:
        if items_in_category!="all" and img_name not in items_in_category:
            continue
        if os.path.isfile( os.path.join(\
            folder_path, img_name + "_thumb.jpg") )==False: continue
        thumb = "QUESTION"
        enum_items.append((img_name, label, desc))
        sublist.append( (label, desc, img_name, sun, sky) )
        i += 1

    return enum_items




def run_resync(self,context):
    global newload
    global category_selected

    if newload==False:
        # skip for other functions in usual case
        return
    newload = False

    settings = bpy.context.scene.world.pl_skies_settings
    setname = settings.category_string

    # fix the node complexity
    newload = True
    node_resync(self,context)
    newload = False

    newload = True
    global temp_node_change
    temp_node_change = True

    # save the cusotm settings
    easyhdr_g = get_current_easyhdr_g(self, context)
    rotation = easyhdr_g.inputs[0].default_value
    sun = easyhdr_g.inputs[1].default_value
    sky = easyhdr_g.inputs[2].default_value

    # fix the image and
    current_img = settings.image_string
    if current_img=="":
        current_img = bpy.context.scene.world.env_previews

    # to be safe, always set back to 'all'
    newload = False
    settings.category = "all"

    newload = False
    set_image_by_category(current_img) # possible fail point, check list
    settings.z_rotation = rotation
    settings.sun = sun
    settings.sky = sky

    temp_node_change = False
    newload = False



# reusable for perhaps inside the individual params
def node_resync(self,context):
    settings = bpy.context.scene.world.pl_skies_settings
    setname = settings.category_string
    easyhdr_g = get_current_easyhdr_g(self, context, \
            change_node_complexity=True, newload=True)

    if settings.use_advanced_sky == True and len(easyhdr_g.inputs)<5:
        settings.use_advanced_sky = False
        # apply the settings even though should stay false, better ultiamtely
        # than having lighting error
        settings.use_advanced_sky = True

        tmp = settings.hue_camera
        apply_cam_hue_change( [tmp.r,tmp.g,tmp.b,1], easyhdr_g)
        apply_cam_sat_change(settings.saturation_camera, easyhdr_g)
        tmp = settings.hue_lighting
        apply_light_hue_change( [tmp.r,tmp.g,tmp.b,1], easyhdr_g)
        apply_light_sat_change(settings.saturation_lighting, easyhdr_g)
        tmp = settings.background_color
        apply_background_color_change( [tmp.r,tmp.g,tmp.b,1], easyhdr_g)
        apply_mirror_sky_change(settings.mirror_sky, easyhdr_g)

    elif settings.use_advanced_sky == False and len(easyhdr_g.inputs)>5:
        settings.use_advanced_sky = True

        tmp = settings.hue_camera
        apply_cam_hue_change( [tmp.r,tmp.g,tmp.b,1], easyhdr_g)
        apply_cam_sat_change(settings.saturation_camera, easyhdr_g)
        tmp = settings.hue_lighting
        apply_light_hue_change( [tmp.r,tmp.g,tmp.b,1], easyhdr_g)
        apply_light_sat_change(settings.saturation_lighting, easyhdr_g)
        tmp = settings.background_color
        apply_background_color_change( [tmp.r,tmp.g,tmp.b,1], easyhdr_g)
        apply_mirror_sky_change(settings.mirror_sky, easyhdr_g)



class resync_active(bpy.types.Operator):
    """Resync the active sky"""
    bl_idname = "scene.prolightingskies_resync"
    bl_label = "Resync the active sky"
    bl_description = "After loading a file previously using skies, "+\
            "reload the thumb and fix any filepaths"

    def execute(self,context):
        global newload
        newload = True #force that it always will run the resync if pressed
        run_resync(self,context)
        return {'FINISHED'}


# -----------------------------------------------------------------------------

# creating the node setup -----------------------------------------------------

def sky_node_complexity(self, context):
    # This switches between the advanced and simple set based on the property
    global temp_node_change
    if newload==True:
        return

    easyhdr_g = get_current_easyhdr_g(self, context)
    rotation = easyhdr_g.inputs[0].default_value
    sun = easyhdr_g.inputs[1].default_value
    sky = easyhdr_g.inputs[2].default_value

    temp_node_change = True
    easyhdr_g = get_current_easyhdr_g(self, context, True)

    # apply the settings back
    settings = bpy.context.scene.world.pl_skies_settings
    settings.z_rotation = rotation
    settings.sun = sun
    settings.sky = sky


def get_node_setup():
    if hasattr(get_node_setup,'node_setup') and temp_node_change==False:
        return get_node_setup.node_setup
    else:
        # global temp_node_change #
        # temp_node_change = False
        world  = bpy.context.scene.world
        if world.pl_skies_settings.use_advanced_sky==True:
            get_node_setup.node_setup = {
                "group": {
                    "name": "Pro Lighting: Skies",
                },
                "nodes": {
                    "Group Input": {
                        "type_id": "NodeGroupInput",
                        "type": "GROUP_INPUT",
                        "name": "Group Input",
                        "location": mathutils.Vector((-1500, -200)),
                    },
                    "Texture Coordinate": {
                        "type_id": "ShaderNodeTexCoord",
                        "type": "TEX_COORD",
                        "name": "Texture Coordinate",
                        "location": mathutils.Vector((-1500, 100)),
                    },
                    "Rotate Z": {
                        "type_id": "ShaderNodeGroup",
                        "type": "GROUP",
                        "name": "Rotate Z",
                        "location": mathutils.Vector((-1260, 0)),
                        "node_tree": get_group_zrot,
                    },
                    "Horizon Mapping": {
                        "type_id": "ShaderNodeMapping",
                        "type": "MAPPING",
                        "name": "Horizon Mapping",
                        "location": mathutils.Vector((-1020, 350)),
                        "scale":mathutils.Vector((1,1,1)),
                        "rotation":mathutils.Euler((0,0,0),"XYZ"),
                        "translation":mathutils.Vector((0,0,0)),
                    },
                    "Mirror Mapping": {
                        "type_id": "ShaderNodeMapping",
                        "type": "MAPPING",
                        "name": "Mirror Mapping",
                        "location": mathutils.Vector((-1020, 0)),
                        "scale":mathutils.Vector((-1,-1,-1)),
                        "rotation":mathutils.Euler((0,0,3.1416),"XYZ"),
                    },
                    "Environment Texture 1-top": {
                        "type_id": "ShaderNodeTexEnvironment",
                        "type": "TEX_ENVIRONMENT",
                        "name": "Environment Texture 1-top",
                        "location": mathutils.Vector((-630, 350)),
                    },
                    "Environment Texture 1-bottom": {
                        "type_id": "ShaderNodeTexEnvironment",
                        "type": "TEX_ENVIRONMENT",
                        "name": "Environment Texture 1-bottom",
                        "location": mathutils.Vector((-630, 100)),
                    },
                    "Environment Texture 2-top": {
                        "type_id": "ShaderNodeTexEnvironment",
                        "type": "TEX_ENVIRONMENT",
                        "name": "Environment Texture 2-top",
                        "location": mathutils.Vector((-630, -150)),
                    },
                    "Environment Texture 2-bottom": {
                        "type_id": "ShaderNodeTexEnvironment",
                        "type": "TEX_ENVIRONMENT",
                        "name": "Environment Texture 2-bottom",
                        "location": mathutils.Vector((-630, -400)),
                    },
                    "Advanced Settings-cam": {
                        "type_id": "ShaderNodeGroup",
                        "type": "GROUP",
                        "name": "Advanced Settings-cam",
                        "location": mathutils.Vector((-430, 250)),
                        "node_tree": get_group_advanced,
                    },
                    "Advanced Settings-light": {
                        "type_id": "ShaderNodeGroup",
                        "type": "GROUP",
                        "name": "Advanced Settings-light",
                        "location": mathutils.Vector((-430, -250)),
                        "node_tree": get_group_advanced,
                    },
                    "Multiply": {
                        "type_id": "ShaderNodeMath",
                        "type": "MATH",
                        "name":  "Multiply",
                        "operation": 'MULTIPLY',
                        "location": mathutils.Vector((-190, -290)),
                    },
                    "Add": {
                        "type_id": "ShaderNodeMath",
                        "type": "MATH",
                        "name": "Add",
                        "location": mathutils.Vector((50, -290)),
                    },
                    "Light Path": {
                        "type_id": "ShaderNodeLightPath",
                        "type": "LIGHT_PATH",
                        "name": "Light Path",
                        "location": mathutils.Vector((280, 400)),
                    },
                    "Background 1": {
                        "type_id": "ShaderNodeBackground",
                        "type": "BACKGROUND",
                        "name": "Background 1",
                        "location": mathutils.Vector((280, 100)),
                    },
                    "Background 2": {
                        "type_id": "ShaderNodeBackground",
                        "type": "BACKGROUND",
                        "name": "Background 2",
                        "location": mathutils.Vector((280, -150)),
                    },
                    "Mix": {
                        "type_id": "ShaderNodeMixShader",
                        "type": "MIX_SHADER",
                        "name": "Mix",
                        "location": mathutils.Vector((520, 0)),
                    },
                    "Group Output": {
                        "type_id": "NodeGroupOutput",
                        "type": "GROUP_OUTPUT",
                        "name": "Group Output",
                        "location": mathutils.Vector((760, 0)),
                        "is_active_output": True,
                    }
                },
                "links": [
                    # (from_node, from_socket, to_node, to_socket)
                    ("Group Input", 0, "Rotate Z", 1),
                    ("Group Input", 1, "Multiply", 1),
                    ("Group Input", 2, "Add", 1),
                    ("Texture Coordinate", 0, "Rotate Z", 0),

                    ("Rotate Z", 0, "Horizon Mapping", 0),
                    ("Rotate Z", 0, "Mirror Mapping", 0),

                    ("Horizon Mapping", 0, "Environment Texture 1-top", 0),
                    ("Horizon Mapping", 0, "Environment Texture 2-top", 0),

                    ("Mirror Mapping", 0, "Environment Texture 1-bottom", 0),
                    ("Mirror Mapping", 0, "Environment Texture 2-bottom", 0),

                    ("Environment Texture 1-top", 0, "Advanced Settings-cam", 0),
                    ("Environment Texture 1-bottom", 0, "Advanced Settings-cam", 1),
                    ("Group Input", 3, "Advanced Settings-cam", 2),
                    ("Group Input", 8, "Advanced Settings-cam", 3),
                    ("Group Input", 7, "Advanced Settings-cam", 4),
                    ("Group Input", 4, "Advanced Settings-cam", 5),

                    ("Environment Texture 2-top", 0, "Advanced Settings-light", 0),
                    ("Environment Texture 2-bottom", 0, "Advanced Settings-light", 1),
                    ("Group Input", 5, "Advanced Settings-light", 2),
                    ("Group Input", 8, "Advanced Settings-light", 3),
                    ("Group Input", 7, "Advanced Settings-light", 4),
                    ("Group Input", 6, "Advanced Settings-light", 5),

                    ("Advanced Settings-cam", 0, "Background 1", 0),
                    ("Advanced Settings-light", 0, "Background 2", 0),

                    ("Advanced Settings-light", 0, "Multiply", 0),
                    ("Multiply", 0, "Add", 0),
                    ("Add", 0, "Background 1", 1),
                    ("Add", 0, "Background 2", 1),
                    ("Light Path", 0, "Mix", 0),
                    ("Background 1", 0, "Mix", 2),
                    ("Background 2", 0, "Mix", 1),
                    ("Mix", 0, "Group Output", 0),
                ],
                "inputs": [
                    ("NodeSocketFloatAngle", "Rotation"),
                    ("NodeSocketFloat", "Sun"),
                    ("NodeSocketFloat", "Sky"),
                    ("NodeSocketColor", "Cam Hue"),
                    ("NodeSocketFloat", "Cam Saturation"),
                    ("NodeSocketColor", "Light Hue"),
                    ("NodeSocketFloat", "Light Saturation"),
                    ("NodeSocketFloat", "Mirror Sky"),
                    ("NodeSocketColor", "Background Color"),
                ],
                "groups": {
                    "Advanced Settings": {
                        "nodes": {
                            "Group Input": {
                                "type_id": "NodeGroupInput",
                                "type": "GROUP_INPUT",
                                "name": "Group Input",
                                "location": mathutils.Vector((-630, 195)),
                            },
                            "Mirror Sky": {
                                "type_id": "ShaderNodeMixRGB",
                                "type": "MIX_RGB",
                                "name": "Mirror Sky",
                                "location": mathutils.Vector((-400, 400)),
                                "blend_type":"ADD",
                            },
                            "Segment BG": {
                                "type_id": "ShaderNodeMath",
                                "type": "MATH",
                                "name": "Segment BG",
                                "location": mathutils.Vector((-400, 200)),
                                "operation":"LESS_THAN",
                            },
                            "BG Color Add": {
                                "type_id": "ShaderNodeMixRGB",
                                "type": "MIX_RGB",
                                "name": "BG Color Add",
                                "location": mathutils.Vector((-200, 200)),
                                "blend_type":"ADD",
                            },
                            "BG to Mirror Mix": {
                                "type_id": "ShaderNodeMixRGB",
                                "type": "MIX_RGB",
                                "name": "BG to Mirror Mix",
                                "location": mathutils.Vector((0, 200)),
                                "blend_type":"MIX",
                            },
                            "Segment BG-2": {
                                "type_id": "ShaderNodeMath",
                                "type": "MATH",
                                "name": "Segment BG-2",
                                "location": mathutils.Vector((200, 000)),
                                "operation":"LESS_THAN",
                            },
                            "BG Color Add-2": {
                                "type_id": "ShaderNodeMixRGB",
                                "type": "MIX_RGB",
                                "name": "BG Color Add-2",
                                "location": mathutils.Vector((200, 200)),
                                "blend_type":"ADD",
                            },
                            "Hue Multiply": {
                                "type_id": "ShaderNodeMixRGB",
                                "type": "MIX_RGB",
                                "name": "Hue Multiply",
                                "location": mathutils.Vector((400, 200)),
                                "blend_type":"MULTIPLY",
                            },
                            "Saturation": {
                                "type_id": "ShaderNodeHueSaturation",
                                "type": "HUE_SAT",
                                "name": "Saturation",
                                "location": mathutils.Vector((600, 200)),
                            },
                            "Group Output": {
                                "type_id": "NodeGroupOutput",
                                "type": "GROUP_OUTPUT",
                                "name": "Group Output",
                                "location": mathutils.Vector((800, 200)),
                                "is_active_output": True,
                            }
                        },
                        "links": [
                            ("Group Input", 0, "Mirror Sky", 1),
                            ("Group Input", 1, "Mirror Sky", 2),
                            ("Group Input", 0, "Segment BG", 0),
                            # (0.01, 2, "Segment BG", 1),
                            ("Segment BG", 0, "Mirror Sky", 0),
                            ("Segment BG", 0, "BG Color Add", 0),
                            ("Group Input", 0, "BG Color Add", 1),
                            ("Group Input", 3, "BG Color Add", 2),
                            ("Group Input", 4, "BG to Mirror Mix", 0),
                            ("BG Color Add", 0, "BG to Mirror Mix", 1),
                            ("Mirror Sky", 0, "BG to Mirror Mix", 2),
                            # (1, 0, "Hue Multiply", 0),
                            #("BG to Mirror Mix", 0, "Hue Multiply", 1),
                            ("BG to Mirror Mix", 0, "Segment BG-2", 0),

                            ("Segment BG-2", 0, "BG Color Add-2", 0),
                            ("BG to Mirror Mix", 0, "BG Color Add-2", 1),
                            ("Group Input", 3, "BG Color Add-2", 2),
                            ("BG Color Add-2", 0, "Hue Multiply", 1),


                            ("Group Input", 2, "Hue Multiply", 2),
                            ("Group Input", 5, "Saturation", 1),
                            ("Hue Multiply", 0, "Saturation", 4),
                            ("Saturation", 0, "Group Output",0),

                        ],
                        "inputs": [
                            ("NodeSocketColor", "Top Hemi"),
                            ("NodeSocketColor", "Bottom Hemi"),
                            ("NodeSocketColor", "Hue"),
                            ("NodeSocketColor", "BG Color"),
                            ("NodeSocketFloat", "Mirror Factor"),
                            ("NodeSocketFloat", "Saturation"),
                        ]
                    },
                    "Rotate Z": {
                        "nodes": {
                            "Group Input": {
                                "type_id": "NodeGroupInput",
                                "type": "GROUP_INPUT",
                                "name": "Group Input",
                                "location": mathutils.Vector((-630, 195)),
                            },
                            "Separate XYZ": {
                                "type_id": "ShaderNodeSeparateXYZ",
                                "type": "SEPXYZ",
                                "name":  "Separate XYZ",
                                "location": mathutils.Vector((-390, 260)),
                            },
                            "Sine": {
                                "type_id": "ShaderNodeMath",
                                "type": "MATH",
                                "name":  "Sine",
                                "location": mathutils.Vector((-390, 60)),
                                "operation": 'SINE',
                                "hide": True,
                            },
                            "Cosine": {
                                "type_id": "ShaderNodeMath",
                                "type": "MATH",
                                "name":  "Cosine",
                                "location": mathutils.Vector((-390, -70)),
                                "operation": 'COSINE',
                                "hide": True,
                            },
                            "Multiply 1": {
                                "type_id": "ShaderNodeMath",
                                "type": "MATH",
                                "name":  "Multiply 1",
                                "location": mathutils.Vector((0, 130)),
                                "operation": 'MULTIPLY',
                                "hide": True,
                            },
                            "Multiply 2": {
                                "type_id": "ShaderNodeMath",
                                "type": "MATH",
                                "name":  "Multiply 2",
                                "location": mathutils.Vector((0, 50)),
                                "operation": 'MULTIPLY',
                                "hide": True,
                            },
                            "Multiply 3": {
                                "type_id": "ShaderNodeMath",
                                "type": "MATH",
                                "name":  "Multiply 3",
                                "location": mathutils.Vector((0, -30)),
                                "operation": 'MULTIPLY',
                                "hide": True,
                            },
                            "Multiply 4": {
                                "type_id": "ShaderNodeMath",
                                "type": "MATH",
                                "name":  "Multiply 4",
                                "location": mathutils.Vector((0, -110)),
                                "operation": 'MULTIPLY',
                                "hide": True,
                            },
                            "Add": {
                                "type_id": "ShaderNodeMath",
                                "type": "MATH",
                                "name": "Add",
                                "location": mathutils.Vector((160, -70)),
                                "hide": True,
                            },
                            "Subtract": {
                                "type_id": "ShaderNodeMath",
                                "type": "MATH",
                                "name":  "Subtract",
                                "location": mathutils.Vector((160, 90)),
                                "operation": 'SUBTRACT',
                                "hide": True,
                            },
                            "Combine XYZ": {
                                "type_id": "ShaderNodeCombineXYZ",
                                "type": "COMBXYZ",
                                "name":  "Combine XYZ",
                                "location": mathutils.Vector((350, 280)),
                            },
                            "Group Output": {
                                "type_id": "NodeGroupOutput",
                                "type": "GROUP_OUTPUT",
                                "name": "Group Output",
                                "location": mathutils.Vector((580, 275)),
                                "is_active_output": True,
                            }

                        },
                        "links": [
                            ("Group Input", 0, "Separate XYZ", 0),
                            ("Group Input", 1, "Sine", 0),
                            ("Group Input", 1, "Cosine", 0),

                            ("Cosine", 0, "Multiply 1", 0),
                            ("Separate XYZ", 0, "Multiply 1", 1),
                            ("Sine", 0, "Multiply 2", 0),
                            ("Separate XYZ", 1, "Multiply 2", 1),
                            ("Multiply 1", 0, "Subtract", 0),
                            ("Multiply 2", 0, "Subtract", 1),
                            ("Subtract", 0, "Combine XYZ", 0),

                            ("Sine", 0, "Multiply 3", 0),
                            ("Separate XYZ", 0, "Multiply 3", 1),
                            ("Cosine", 0, "Multiply 4", 0),
                            ("Separate XYZ", 1, "Multiply 4", 1),
                            ("Multiply 3", 0, "Add", 0),
                            ("Multiply 4", 0, "Add", 1),
                            ("Add", 0, "Combine XYZ", 1),

                            ("Separate XYZ", 2, "Combine XYZ", 2),
                            ("Combine XYZ", 0, "Group Output", 0),
                        ],
                        "inputs": [
                            ("NodeSocketVector", "Vector"),
                            ("NodeSocketFloat", "Angle"),
                        ]
                    }
                }
            }

            return get_node_setup.node_setup

        else: # alternative, do simple version
            get_node_setup.node_setup = {
                "group": {
                    "name": "Pro Lighting: Skies",
                },
                "nodes": {
                    "Group Input": {
                        "type_id": "NodeGroupInput",
                        "type": "GROUP_INPUT",
                        "name": "Group Input",
                        "location": mathutils.Vector((-910, -200)),
                    },
                    "Texture Coordinate": {
                        "type_id": "ShaderNodeTexCoord",
                        "type": "TEX_COORD",
                        "name": "Texture Coordinate",
                        "location": mathutils.Vector((-910, 100)),
                    },
                    "Rotate Z": {
                        "type_id": "ShaderNodeGroup",
                        "type": "GROUP",
                        "name": "Rotate Z",
                        "location": mathutils.Vector((-670, 0)),
                        "node_tree": get_group_zrot,
                    },
                    "Environment Texture 1-top": {
                        "type_id": "ShaderNodeTexEnvironment",
                        "type": "TEX_ENVIRONMENT",
                        "name": "Environment Texture 1-top",
                        "location": mathutils.Vector((-430, 100)),
                    },
                    "Environment Texture 2-top": {
                        "type_id": "ShaderNodeTexEnvironment",
                        "type": "TEX_ENVIRONMENT",
                        "name": "Environment Texture 2-top",
                        "location": mathutils.Vector((-430, -150)),
                    },
                    "Multiply": {
                        "type_id": "ShaderNodeMath",
                        "type": "MATH",
                        "name":  "Multiply",
                        "operation": 'MULTIPLY',
                        "location": mathutils.Vector((-190, -290)),
                    },
                    "Add": {
                        "type_id": "ShaderNodeMath",
                        "type": "MATH",
                        "name": "Add",
                        "location": mathutils.Vector((50, -290)),
                    },
                    "Light Path": {
                        "type_id": "ShaderNodeLightPath",
                        "type": "LIGHT_PATH",
                        "name": "Light Path",
                        "location": mathutils.Vector((280, 400)),
                    },
                    "Background 1": {
                        "type_id": "ShaderNodeBackground",
                        "type": "BACKGROUND",
                        "name": "Background 1",
                        "location": mathutils.Vector((280, 100)),
                    },
                    "Background 2": {
                        "type_id": "ShaderNodeBackground",
                        "type": "BACKGROUND",
                        "name": "Background 2",
                        "location": mathutils.Vector((280, -150)),
                    },
                    "Mix": {
                        "type_id": "ShaderNodeMixShader",
                        "type": "MIX_SHADER",
                        "name": "Mix",
                        "location": mathutils.Vector((520, 0)),
                    },
                    "Group Output": {
                        "type_id": "NodeGroupOutput",
                        "type": "GROUP_OUTPUT",
                        "name": "Group Output",
                        "location": mathutils.Vector((760, 0)),
                        "is_active_output": True,
                    }
                },
                "links": [
                    # (from_node, from_socket, to_node, to_socket)
                    ("Group Input", 0, "Rotate Z", 1),
                    ("Group Input", 1, "Multiply", 1),
                    ("Group Input", 2, "Add", 1),
                    ("Texture Coordinate", 0, "Rotate Z", 0),
                    ("Rotate Z", 0, "Environment Texture 1-top", 0),
                    ("Rotate Z", 0, "Environment Texture 2-top", 0),
                    ("Environment Texture 1-top", 0, "Background 1", 0),
                    ("Environment Texture 2-top", 0, "Background 2", 0),
                    ("Environment Texture 2-top", 0, "Multiply", 0),
                    ("Multiply", 0, "Add", 0),
                    ("Add", 0, "Background 1", 1),
                    ("Add", 0, "Background 2", 1),
                    ("Light Path", 0, "Mix", 0),
                    ("Background 1", 0, "Mix", 2),
                    ("Background 2", 0, "Mix", 1),
                    ("Mix", 0, "Group Output", 0),
                ],
                "inputs": [
                    ("NodeSocketFloatAngle", "Rotation"),
                    ("NodeSocketFloat", "Sun"),
                    ("NodeSocketFloat", "Sky"),
                ],
                "groups": {
                    "Rotate Z": {
                        "nodes": {
                            "Group Input": {
                                "type_id": "NodeGroupInput",
                                "type": "GROUP_INPUT",
                                "name": "Group Input",
                                "location": mathutils.Vector((-630, 195)),
                            },
                            "Separate XYZ": {
                                "type_id": "ShaderNodeSeparateXYZ",
                                "type": "SEPXYZ",
                                "name":  "Separate XYZ",
                                "location": mathutils.Vector((-390, 260)),
                            },
                            "Sine": {
                                "type_id": "ShaderNodeMath",
                                "type": "MATH",
                                "name":  "Sine",
                                "location": mathutils.Vector((-390, 60)),
                                "operation": 'SINE',
                                "hide": True,
                            },
                            "Cosine": {
                                "type_id": "ShaderNodeMath",
                                "type": "MATH",
                                "name":  "Cosine",
                                "location": mathutils.Vector((-390, -70)),
                                "operation": 'COSINE',
                                "hide": True,
                            },
                            "Multiply 1": {
                                "type_id": "ShaderNodeMath",
                                "type": "MATH",
                                "name":  "Multiply 1",
                                "location": mathutils.Vector((0, 130)),
                                "operation": 'MULTIPLY',
                                "hide": True,
                            },
                            "Multiply 2": {
                                "type_id": "ShaderNodeMath",
                                "type": "MATH",
                                "name":  "Multiply 2",
                                "location": mathutils.Vector((0, 50)),
                                "operation": 'MULTIPLY',
                                "hide": True,
                            },
                            "Multiply 3": {
                                "type_id": "ShaderNodeMath",
                                "type": "MATH",
                                "name":  "Multiply 3",
                                "location": mathutils.Vector((0, -30)),
                                "operation": 'MULTIPLY',
                                "hide": True,
                            },
                            "Multiply 4": {
                                "type_id": "ShaderNodeMath",
                                "type": "MATH",
                                "name":  "Multiply 4",
                                "location": mathutils.Vector((0, -110)),
                                "operation": 'MULTIPLY',
                                "hide": True,
                            },
                            "Add": {
                                "type_id": "ShaderNodeMath",
                                "type": "MATH",
                                "name": "Add",
                                "location": mathutils.Vector((160, -70)),
                                "hide": True,
                            },
                            "Subtract": {
                                "type_id": "ShaderNodeMath",
                                "type": "MATH",
                                "name":  "Subtract",
                                "location": mathutils.Vector((160, 90)),
                                "operation": 'SUBTRACT',
                                "hide": True,
                            },
                            "Combine XYZ": {
                                "type_id": "ShaderNodeCombineXYZ",
                                "type": "COMBXYZ",
                                "name":  "Combine XYZ",
                                "location": mathutils.Vector((350, 280)),
                            },
                            "Group Output": {
                                "type_id": "NodeGroupOutput",
                                "type": "GROUP_OUTPUT",
                                "name": "Group Output",
                                "location": mathutils.Vector((580, 275)),
                                "is_active_output": True,
                            }

                        },
                        "links": [
                            ("Group Input", 0, "Separate XYZ", 0),
                            ("Group Input", 1, "Sine", 0),
                            ("Group Input", 1, "Cosine", 0),

                            ("Cosine", 0, "Multiply 1", 0),
                            ("Separate XYZ", 0, "Multiply 1", 1),
                            ("Sine", 0, "Multiply 2", 0),
                            ("Separate XYZ", 1, "Multiply 2", 1),
                            ("Multiply 1", 0, "Subtract", 0),
                            ("Multiply 2", 0, "Subtract", 1),
                            ("Subtract", 0, "Combine XYZ", 0),

                            ("Sine", 0, "Multiply 3", 0),
                            ("Separate XYZ", 0, "Multiply 3", 1),
                            ("Cosine", 0, "Multiply 4", 0),
                            ("Separate XYZ", 1, "Multiply 4", 1),
                            ("Multiply 3", 0, "Add", 0),
                            ("Multiply 4", 0, "Add", 1),
                            ("Add", 0, "Combine XYZ", 1),

                            ("Separate XYZ", 2, "Combine XYZ", 2),
                            ("Combine XYZ", 0, "Group Output", 0),
                        ],
                        "inputs": [
                            ("NodeSocketVector", "Vector"),
                            ("NodeSocketFloat", "Angle"),
                        ]
                    }
                }
            }
            return get_node_setup.node_setup


def create_node_tree(name, setup):

    node_tree = bpy.data.node_groups.new(
        type="ShaderNodeTree",
        name=name)

    g_nodes = node_tree.nodes
    g_links = node_tree.links

    # Setting the group interface
    for socket in setup["inputs"]:
        node_tree.inputs.new(socket[0], socket[1])

    # Adding Nodes
    for node_name, node_data in setup["nodes"].items():
        node = g_nodes.new(node_data["type_id"])
        for key, value in node_data.items():
            if key not in {"type", "type_id"}:
                if hasattr(value, '__call__'):
                    value = value()
                setattr(node, key, value)

    # Linking
    for from_node, from_socket, to_node, to_socket in setup["links"]:
        g_links.new(
            g_nodes[from_node].outputs[from_socket],
            g_nodes[to_node].inputs[to_socket])

    return node_tree


def get_group_zrot():
    return get_group("Rotate Z")

def get_group_advanced():
    return get_group("Advanced Settings")

def get_group(name):
    setup = get_node_setup()["groups"][name]

    # try to get by name
    group_node_tree = bpy.data.node_groups.get(name)

    if group_node_tree:
        # if it has changes, change the name and make a new node group tree
        if has_changes(group_node_tree, setup):
            set_name_as_edited(group_node_tree)
        else:
            return group_node_tree

    # if not previously existing or had changes
    return create_node_tree(name, setup)


def create_node_group_setup():
    context = bpy.context
    world = context.scene.world

    tree = world.node_tree
    w_nodes = tree.nodes
    w_links = tree.links

    # Creating node tree

    name = get_node_setup()["group"]["name"]
    setup = get_node_setup()
    group_node_tree = create_node_tree(name, setup)

    g_nodes = group_node_tree.nodes
    g_links = group_node_tree.links

    # Creating node group to hold the tree

    group = w_nodes.new("ShaderNodeGroup")
    group.name = get_node_setup()["group"]["name"]
    group.node_tree = group_node_tree
    group.is_pl_skies = True

    # Setting node values with data of current environment
    enum_choice = get_image_by_category()

    world.pl_skies_settings.image_string = enum_choice
    apply_image_change(enum_choice, g_nodes,)
    apply_defaults(enum_choice, group)

    return group

# -----------------------------------------------------------------------------

# checking node setup for changes ---------------------------------------------

ignore_change_props_list = (
    "rna_type", "location", "width", "width_hidden", "height", "dimensions",
    "name", "label", "use_custom_color", "color", "select", "show_options",
    "show_preview", "hide", "mute", "show_texture", "shading_compatibility",
    "bl_idname", "bl_label", "bl_description", "bl_icon", "bl_static_type",
    "bl_width_default", "bl_width_min", "bl_width_max", "bl_height_default",
    "bl_height_min", "bl_height_max",
    "is_pl_skies", "pl_skies_was_last_linked",
    "inputs", "outputs", "internal_links",
)

# note: array defaults, collections, strings and pointer values are not well
# supported, but they also shouldn't exist in the node setup
def get_rna_default(prop_id, prop_type, prop):

    if prop_type in {'BOOLEAN', 'INT', 'FLOAT'}:
        if prop.array_length == 0:
            return prop.default
        else:
            if prop.subtype in {'TRANSLATION', 'XYZ'}:
                return mathutils.Vector(prop.default_array)
            elif prop.subtype == 'EULER':
                return mathutils.Euler(prop.default_array)
            else:
                # unrecognized array type
                return

    elif prop_type == 'ENUM':
        if prop.is_enum_flag:
            return prop.default_flag
        else:
            return prop.default

    elif prop_type in {'COLLECTION', 'STRING', 'POINTER'}:
        return


def has_changes(node_tree, setup):

    # real
    g_nodes = node_tree.nodes
    g_links = node_tree.links

    # default
    d_nodes = setup['nodes']
    d_links = setup['links']


    # quick test on number of links
    if not len(g_links) == len(d_links):
        return True

    # quick test on number of nodes
    if not len(g_nodes) == len(d_nodes):
        return True

    # one specific node name, to test against previous version
    # if not "Environment Texture 1-top" in g_nodes:
    #     print("Old version loaded in, should update")
    #     return True

    # checking nodes

    for g_n in g_nodes:
        try:
            d_n = setup['nodes'][g_n.name]
        except:
            return True

        if d_n is None:
            return True

        # checking every property against the RNA default or setup default
        for prop_id, prop in g_n.bl_rna.properties.items():

            # changes to this property are ignored
            if prop_id in ignore_change_props_list:
                continue

            real_val = getattr(g_n, prop_id)

            # special, check subgroup
            if prop_id == "node_tree":
                # TODO (in a rush) get node name instead of hardcode
                # so far so fine, because there is only one one internal group.
                # Disabling, because it is not important if it was altered
                #if has_changes(real_val, get_node_setup()["groups"]["Rotate Z"]):
                #    return True
                #else:
                continue
            # overridden prop. get the setup default, not RNA default
            if prop_id in d_n:
                def_val = d_n[prop_id]

            # test default rna value
            else:
                if prop.type in {'POINTER', 'STRING', 'COLLECTION'}:
                    # not supported yet
                    continue
                else:
                    def_val = get_rna_default(prop_id, prop.type, prop)

            # compare real value with the default
            # this fails for pre-blender 2.75, so just skip check to make usable
            if real_val != def_val and use_icons==True:
                # exception because of translation val
                if g_n.name == "Horizon Mapping": continue

                return True

    return False


    # checking links

    for g_l in g_links:

        found_match = False

        for f_node_name, f_socket_id, t_node_name, t_socket_id in d_links:
            if g_l.from_node.name == f_node_name \
            and g_l.from_socket.identifier == \
                g_nodes[f_node_name].outputs[f_socket_id].identifier \
            and g_l.to_node.name == t_node_name \
            and g_l.to_socket.identifier == \
                g_nodes[t_node_name].inputs[t_socket_id].identifier:
                found_match = True
                break

        if not found_match:
            return True

    # there were no changes detected so far, we conclude there are no changes
    return False


# -----------------------------------------------------------------------------

# World getting and node toggling ---------------------------------------------

def get_default_node_by_name(setup, name):
    for n in setup['nodes']:
        if n['name'] == name:
            return n
    return None

def get_world_output(self, context):
    world = context.scene.world

    w_nodes = world.node_tree.nodes
    w_links = world.node_tree.links

    for n in w_nodes:
        if n.type == 'OUTPUT_WORLD' and n.is_active_output:
            return n

    for n in w_nodes:
        if n.type == 'OUTPUT_WORLD':
            return n

    return None

def get_currently_linked(node, index):
    current_end_node = None

    if len(node.inputs) > index:
        if next(iter(node.inputs[index].links), None):
            current_end_node = node.inputs[index].links[0].from_node
    return current_end_node

def get_current_easyhdr_g(self, context, change_node_complexity=False, newload=False):
    world = context.scene.world
    w_nodes = world.node_tree.nodes

    w_out = get_world_output(self, context)
    if w_out:
        easyhdr_g = get_currently_linked(w_out, 0)

        if not (easyhdr_g and easyhdr_g.is_pl_skies):
            groups = [n for n in w_nodes if n.type == 'GROUP' and n.is_pl_skies]
            if next(iter(groups), None):
                easyhdr_g = groups[0]

    # only want it to return existing group for quick check
    if newload==True:
        return easyhdr_g

    # test for changes
    if easyhdr_g:
        if has_changes(easyhdr_g.node_tree, get_node_setup()):
            easyhdr_g = None

    if not easyhdr_g:
        if change_node_complexity==False:
            set_group_names_as_edited()
            easyhdr_g = create_node_group_setup()
            easyhdr_g.location = smart_place_easyenv_group(easyhdr_g.name)
        else:
            # changing the node to/from simple/complex
            easyhdr_g = create_node_group_setup()
            easyhdr_g.location = toggle_place_easyenv_group(easyhdr_g.name)


        if w_out:
            w_links = world.node_tree.links
            w_links.new(easyhdr_g.outputs[0], w_out.inputs[0])

    # elif temp_node_change==True:
    #     easyhdr_g = create_node_group_setup()
    #     easyhdr_g.location = toggle_place_easyenv_group(easyhdr_g.name)
    #     if w_out:
    #         w_links = world.node_tree.links
    #         w_links.new(easyhdr_g.outputs[0], w_out.inputs[0])
    return easyhdr_g


def smart_place_world_output(node_name):
    # W out default position
    return (300, 300)

def toggle_place_easyenv_group(node_name):
    context = bpy.context
    world = context.scene.world
    w_nodes = world.node_tree.nodes

    n_left = None
    n_left2 = None
    x = -1000
    for n in w_nodes:
        if n.is_pl_skies and n.name != node_name:
            n_loc = n.location
            x = max(n_loc.x, x)
            n_left2 = n_left
            n_left = n

    if n_left:
        x = n_left.location.x
        y = n_left.location.y
        w_nodes.remove(n_left)

    else:
        x = 10
        y = 100

    return (x, y)

def smart_place_easyenv_group(node_name):
    context = bpy.context
    world = context.scene.world
    w_nodes = world.node_tree.nodes

    n_left = None
    x = -1000
    for n in w_nodes:
        if n.is_pl_skies and n.name != node_name:
            n_loc = n.location
            x = max(n_loc.x, x)
            n_left = n

    if n_left:
        x = n_left.location.x + 40
        y = n_left.location.y - 40
    else:
        x = 10
        y = 100

    return (x, y)


def set_name_as_edited(thing):
    thing.name = "Custom " + thing.name

def set_group_names_as_edited():
    context = bpy.context
    world = context.scene.world

    w_nodes = world.node_tree.nodes

    for n in w_nodes:
        if n.is_pl_skies:
            if has_changes(n.node_tree, get_node_setup()):
                if n.name == get_node_setup()["group"]["name"]:
                    set_name_as_edited(n)
                if n.node_tree.name == get_node_setup()["group"]["name"]:
                    set_name_as_edited(n.node_tree)


def switch_multiple_sample_values(self, context):
    world  = context.scene.world
    cworld = world.cycles
    settings = world.pl_skies_settings

    attrs = ["sample_as_light", "sample_map_resolution", "samples"]

    for attr in attrs:
        temp = getattr(cworld, attr)
        setattr(cworld, attr, getattr(settings, attr))
        setattr(settings, attr, temp)



def toggle_pl_skies(self, context):

    scene = context.scene
    world = context.scene.world

    # check compatibility with enabling
    if "pl_studio_props" in scene:
        plstudio = context.scene.pl_studio_props
        if plstudio.use_pl_studio_background == True or plstudio.use_pl_studio_reflections == True:
            print("Not compatible with studio background/reflections")
            return

    # setting use_nodes True creates a background and world output nodes
    world.use_nodes = True

    w_nodes = world.node_tree.nodes
    w_links = world.node_tree.links

    w_out = get_world_output(self, context)


    # searching and clearing previous end node
    previous_end_node = None
    for n in w_nodes:
        if n.pl_skies_was_last_linked:
            previous_end_node = n
            # clearing
            n.pl_skies_was_last_linked = False

    if self.use_pl_skies:
        # turning easyHDRs  ON


        # there was no world output node, so we make one
        if not w_out:
            w_out = w_nodes.new('ShaderNodeOutputWorld')
            w_out.name = "World Output"
            w_out.location = smart_place_world_output(w_out.name)


        # TODO more safety with inputs[0]
        # get end node currently linked to the world_output if any
        current_end_node = get_currently_linked(w_out, 0)
        if current_end_node:
            if current_end_node.is_pl_skies:
                return None
            else:
                current_end_node.pl_skies_was_last_linked = True

        if previous_end_node:
            easyhdr_g = previous_end_node
        else:
            # checking if there is some lost easyHDR, just in case
            easyhdr_g = None
            for n in w_nodes:
                if n.is_pl_skies:
                    if has_changes(n.node_tree, get_node_setup()) == False:
                        easyhdr_g = n

            if not easyhdr_g:
                # searching for an unchanged easyhdr group node with no users
                for n in bpy.data.node_groups:
                    if n.users == 0 and has_changes(n, get_node_setup()) \
                        == False: # n.is_pl_skies
                        set_group_names_as_edited()
                        easyhdr_g = w_nodes.new("ShaderNodeGroup")
                        easyhdr_g.name = get_node_setup()["group"]["name"]
                        easyhdr_g.node_tree = n
                        easyhdr_g.is_pl_skies = True

            if not easyhdr_g:
                # turning on easy hdr and there is no previous easyhdr node
                set_group_names_as_edited()
                easyhdr_g = create_node_group_setup()
                easyhdr_g.location = smart_place_easyenv_group(easyhdr_g.name)

        # now we can safely link the easy HDR group with the world output
        w_links.new(easyhdr_g.outputs[0], w_out.inputs[0])

        run_resync(self,context)

    else:
        # turning easyHDRs  OFF

        # TODO more safety with inputs[0]
        # get end node currently linked to the world_output if any
        current_end_node = get_currently_linked(w_out, 0)
        if current_end_node:
            if not current_end_node.is_pl_skies:
                return None
            else:
                # setting currently linked node to was_last_linked
                current_end_node.pl_skies_was_last_linked = True
                # delete previous link to world output
                for l in w_out.inputs[0].links:
                    w_links.remove(l)

        # link previous end node with world output if both existing
        if previous_end_node and w_out:
            w_links.new(previous_end_node.outputs[0], w_out.inputs[0])

    # multisample
    switch_multiple_sample_values(self, context)

    # update functions of properties should return None
    return None

# -----------------------------------------------------------------------------

# detect and apply changes from the panel values ------------------------------
# XX_cb are triggered by the interface and need to check if there are any
# unsupported changes to the node setup.
# apply_XX are only called internally when sure of the node setup integrity


# global control var needed to avoid checking for a correct node group every
# time the value is set internally (we are sure everything is correct, just
# need to update the panel value) without triggering more checks
setting_value_internally = False

def apply_defaults(enum_choice, easyhdr_g):
    context = bpy.context
    settings = context.scene.world.pl_skies_settings

    for label, desc, img_name, sun, sky in environments:
        if img_name == enum_choice:

            global setting_value_internally
            setting_value_internally = True

            # check favorite status for custom value setting
            if 'favorites' in categories and enum_choice in categories['favorites']:
                sun_fav, sky_fav = categories['favorites'][enum_choice]
                settings.sun = sun_fav
                settings.sky = sky_fav
            else:
                settings.sun = sun
                settings.sky = sky

            apply_sun_change(settings.sun, easyhdr_g)
            apply_sky_change(settings.sky, easyhdr_g)

            if settings.use_advanced_sky==True:
                tmp = settings.hue_camera
                apply_cam_hue_change( [tmp.r,tmp.g,tmp.b,1], easyhdr_g)
                apply_cam_sat_change(settings.saturation_camera, easyhdr_g)
                tmp = settings.hue_lighting
                apply_light_hue_change( [tmp.r,tmp.g,tmp.b,1], easyhdr_g)
                apply_light_sat_change(settings.saturation_lighting, easyhdr_g)
                tmp = settings.background_color
                apply_background_color_change( [tmp.r,tmp.g,tmp.b,1], easyhdr_g)
                apply_mirror_sky_change(settings.mirror_sky, easyhdr_g)

                # perhaps a better way, but need to hard set these nodes
                nds = bpy.data.node_groups['Advanced Settings'].nodes
                nds['Segment BG'].inputs[1].default_value = 0.01
                nds['Segment BG-2'].inputs[1].default_value = 0.01
                nds['Mirror Sky'].inputs[0].default_value = 1
                nds['Hue Multiply'].inputs[0].default_value = 1

                easyhdr_g.node_tree.nodes["Horizon Mapping"].translation[2] = 0

            setting_value_internally = False
            break


def apply_change_node_image(tex_node, image_name, image_source_path):

    pl_skies_image = None

    # check if node already has an image that is ours
    if tex_node.image and tex_node.image.pl_skies_flag:
        pl_skies_image = tex_node.image

    # if it does, we just change the source of our image datablock
    if pl_skies_image and bpy.data.use_autopack==False:
        pl_skies_image.filepath = image_source_path
    # if not, the user has deleted or switched the image, we create a new one
    else:
        if bpy.data.use_autopack:
            # autopack prevent supdating images, re-import after removing users
            try:
                print("clear it")
                # tex_node.image
                img_to_clear = tex_node.image
                img_to_clear.user_clear()
                print("clear or error?")
            except:
                print("passed")
                pass # if first time use already packed, no images to clear

        # create a new image and assign (do not destroy previously linked img)
        try:
            if image_name in bpy.data.images and temp_node_change==True:
                tex_node.image = bpy.data.images[image_name]
                return
            image = bpy.data.images.load(image_source_path)
            image.name = image_name
            image.pl_skies_flag = True

            tex_node.image = image
            print("name:",tex_node.image.name)
            tex_node.image.name = image_name
            print("name2:",tex_node.image.name)
        except:
            print("ERROR, could not load set")



def apply_image_change(enum_choice, g_nodes):
    try:
        bpy.data.images['EXR'].unpack(method="USE_ORIGINAL")
    except:
        pass
    try:
        bpy.data.images['JPG'].unpack(method="USE_ORIGINAL")
    except:
        pass
    # get image source names from current enum choice
    folder_path = preview_collections["env_previews"].imgs_dir
    quality = bpy.context.scene.world.pl_skies_settings.quality

    path_img_exr = os.path.join(folder_path, enum_choice + "_EXR.exr")
    if os.path.isfile(path_img_exr) == False:
        # .hdr option
        path_img_exr = os.path.join(folder_path, enum_choice + "_HDR.hdr")
    path_img_jpg = os.path.join(folder_path, enum_choice + quality + ".jpg")


    if os.path.isfile(path_img_exr)== False and\
            os.path.isfile(path_img_jpg)==False:
        x = "uhoh"
        # print("Could not find sky files, check HDRs are installed correctly")
        # can't raise in this context, let it fail via user popup

    global temp_node_change

    for node_name, image_name, image_source_path, match_node in \
        [("Environment Texture 1-top", "JPG", path_img_jpg,\
                "Environment Texture 1-bottom"),
         ("Environment Texture 2-top", "EXR", path_img_exr,\
                "Environment Texture 2-bottom")]:

        # reload from source, to fix auto-pack
        if image_name in bpy.data.images and temp_node_change==False and \
                bpy.data.use_autopack==False:
            bpy.data.images[image_name].filepath = image_source_path
            bpy.data.images[image_name].reload()

        # get node by name
        tex_node = g_nodes[node_name]

        apply_change_node_image(tex_node, image_name, image_source_path)

        # now make the other node have the same image
        if bpy.context.scene.world.pl_skies_settings.use_advanced_sky==True:
            second_tex_node = g_nodes[match_node]
            image_matched = tex_node.image
            second_tex_node.image = image_matched

    # after changing simple versus complex node change, to avoid double loading
    if temp_node_change==True:
        temp_node_change=False

    bpy.data.images['EXR'].pack()
    bpy.data.images['JPG'].pack()
# generalize setting the image to different category enums
def set_image_by_category(new_choice):

    env_names = []
    for n in environments:
        env_names.append(n[2])

    if new_choice not in env_names:
        global category_selected, newload
        print("Error, sky not found in this category: {x}, category {y}"\
                .format(x=new_choice,y=category_selected))
        global newload
        newload = False # clear it out

        if len(sublist[0][2])>0:
            print("Setting to first sky")
            new_choice = sublist[0][2]
        else:
            category_selected = "all"

            # run change category
            print("Setting category for all")

            return
        return

    if use_icons==False:
        bpy.context.world.env_previews = new_choice
    elif category_selected == "all":
        bpy.context.world.env_previews = new_choice
    elif category_selected == "night":
        bpy.context.world.env_previews_night = new_choice
    elif category_selected == "overcast":
        bpy.context.world.env_previews_overcast = new_choice
    elif category_selected == "evening":
        bpy.context.world.env_previews_evening = new_choice
    elif category_selected == "cloudy":
        bpy.context.world.env_previews_cloudy = new_choice
    elif category_selected == "sunset":
        bpy.context.world.env_previews_sunset = new_choice
    elif category_selected == "morning":
        bpy.context.world.env_previews_morning = new_choice
    elif category_selected == "clear":
        bpy.context.world.env_previews_clear = new_choice
    elif category_selected == "space":
        bpy.context.world.env_previews_space = new_choice
    elif category_selected == "custom":
        bpy.context.world.env_previews_custom = new_choice
    elif category_selected == "favorites":
        bpy.context.world.env_previews_favorites = new_choice
    else:
        bpy.context.world.env_previews = new_choice

# generalize getting the image to different category enums
def get_image_by_category():
    if use_icons==False:
        return bpy.context.world.env_previews
    if category_selected == "all":
        return bpy.context.world.env_previews
    elif category_selected == "night":
        return bpy.context.world.env_previews_night
    elif category_selected == "overcast":
        return bpy.context.world.env_previews_overcast
    elif category_selected == "evening":
        return bpy.context.world.env_previews_evening
    elif category_selected == "cloudy":
        return bpy.context.world.env_previews_cloudy
    elif category_selected == "sunset":
        return bpy.context.world.env_previews_sunset
    elif category_selected == "morning":
        return bpy.context.world.env_previews_morning
    elif category_selected == "clear":
        return bpy.context.world.env_previews_clear
    elif category_selected == "space":
        return bpy.context.world.env_previews_space
    elif category_selected == "custom":
        return bpy.context.world.env_previews_custom
    elif category_selected == "favorites":
        return bpy.context.world.env_previews_favorites
    else:
        return bpy.context.world.env_previews


def change_image_cb(self, context):

    easyhdr_g = get_current_easyhdr_g(self, context)
    g_nodes = easyhdr_g.node_tree.nodes

    enum_choice = get_image_by_category()

    # update the favorite status
    settings = bpy.context.scene.world.pl_skies_settings
    settings.image_string = enum_choice

    apply_image_change(enum_choice, g_nodes)
    apply_defaults(enum_choice, easyhdr_g)

    if 'favorites' not in categories:
        # it's just false
        settings.current_favorite = False
    else:
        if enum_choice in categories['favorites']:
            settings.current_favorite = True
        else:
            settings.current_favorite = False
    return None


def apply_res_change(enum_choice, g_nodes):
    current_env = get_image_by_category()
    folder_path = preview_collections["env_previews"].imgs_dir
    path_img_jpg = os.path.join(folder_path, current_env + enum_choice + ".jpg")

    # get node by name
    tex_node = g_nodes["Environment Texture 1-top"]
    apply_change_node_image(tex_node, "JPG", path_img_jpg)

def change_res_cb(self, context):
    easyhdr_g = get_current_easyhdr_g(self, context)
    g_nodes = easyhdr_g.node_tree.nodes

    apply_res_change(self.quality, g_nodes)

    return None

def category_load(self, context):
    global category_selected
    global internal_fave_change
    global newload

    run_resync(self,context)

    if internal_fave_change==True:
        internal_fave_change = False
        # skip because this is called by favorites, not by changing categories
        return

    world  = context.scene.world
    settings = world.pl_skies_settings
    category_selected = settings.category
    settings.category_string = settings.category # for loading other blends

    reloadIcons(keep_previews=True)

    if use_icons:
        if len(sublist)!=0:
            set_image_by_category(sublist[0][2])
    else:
        if len(sublist)!=0:
            #context.scene.world.env_previews = sublist[0][2]
            set_image_by_category(sublist[0][2])

def category_items(self, context):

    items = []
    items.append(("all","All skies","Show all skies"))
    sorted_cats = sorted(categories)
    for item in sorted_cats:
        items.append((item, item, "Show all skies in the '"+item+"' category"))
    return items

def apply_sun_change(value, group_node):
    group_node.inputs[1].default_value = value
def change_sun_cb(self, context):
    if(setting_value_internally):
        return None

    easyhdr_g = get_current_easyhdr_g(self, context)
    apply_sun_change(self.sun, easyhdr_g)

    return None


def apply_sky_change(value, group_node):
    group_node.inputs[2].default_value = value
def change_sky_cb(self, context):
    if(setting_value_internally):
        return None

    easyhdr_g = get_current_easyhdr_g(self, context)
    apply_sky_change(self.sky, easyhdr_g)

    return None

def apply_cam_hue_change(value, group_node):
    group_node.inputs[3].default_value = value
def change_cam_hue(self, context):
    if(setting_value_internally):
        return None

    easyhdr_g = get_current_easyhdr_g(self, context)
    tmp = self.hue_camera # need to add alpha channel
    apply_cam_hue_change( [tmp.r,tmp.g,tmp.b,1], easyhdr_g)

    return None

def apply_cam_sat_change(value, group_node):
    group_node.inputs[4].default_value = value
def change_cam_sat(self, context):
    if(setting_value_internally):
        return None

    easyhdr_g = get_current_easyhdr_g(self, context)
    apply_cam_sat_change(self.saturation_camera, easyhdr_g)

    return None

def apply_light_hue_change(value, group_node):
    group_node.inputs[5].default_value = value
def change_light_hue(self, context):
    if(setting_value_internally):
        return None

    easyhdr_g = get_current_easyhdr_g(self, context)
    tmp = self.hue_lighting # need to add alpha channel
    apply_light_hue_change( [tmp.r,tmp.g,tmp.b,1], easyhdr_g)

    return None

def apply_light_sat_change(value, group_node):
    group_node.inputs[6].default_value = value
def change_light_sat(self, context):
    if(setting_value_internally):
        return None

    easyhdr_g = get_current_easyhdr_g(self, context)
    apply_light_sat_change(self.saturation_lighting, easyhdr_g)

    return None

def apply_background_color_change(value, group_node):
    group_node.inputs[8].default_value = value
def change_background_color(self, context):
    if(setting_value_internally):
        return None

    easyhdr_g = get_current_easyhdr_g(self, context)
    tmp = self.background_color # need to add alpha channel
    apply_background_color_change( [tmp.r,tmp.g,tmp.b,1], easyhdr_g)

    return None

def apply_mirror_sky_change(value, group_node):
    group_node.inputs[7].default_value = value
def change_mirror_sky(self, context):
    if(setting_value_internally):
        return None

    easyhdr_g = get_current_easyhdr_g(self, context)
    apply_mirror_sky_change(self.mirror_sky, easyhdr_g)

    return None

def apply_change_horizon(value, group_node):
    group_node.node_tree.nodes["Horizon Mapping"].translation[2] = -value


def change_horizon(self, context):
    if(setting_value_internally):
        return None

    easyhdr_g = get_current_easyhdr_g(self, context)
    apply_change_horizon(self.horizon, easyhdr_g)

def apply_rotation_change(value, group_node):
    group_node.inputs[0].default_value = value
def change_rotation_cb(self, context):
    easyhdr_g = get_current_easyhdr_g(self, context)
    apply_rotation_change(self.z_rotation, easyhdr_g)

    return None


def skies_is_keyframed(self, context):
    anim = context.scene.world.animation_data
    datasets = ["pl_skies_settings.sun",
            "pl_skies_settings.sky",
            "pl_skies_settings.z_rotation",
            "pl_skies_settings.mirror_sky",
            "pl_skies_settings.background_color",
            "pl_skies_settings.hue_camera",
            "pl_skies_settings.hue_lighting",
            "pl_skies_settings.saturation_camera",
            "pl_skies_settings.saturation_lighting",
            "pl_skies_settings.horizon"]

    if anim is not None and anim.action is not None:
        for fcu in anim.action.fcurves:
            if fcu.data_path in datasets:
                return True
    return False



# -----------------------------------------------------------------------------

# utility operators  ----------------------------------------------------------


class nextSky(bpy.types.Operator):
    """Choose the next sky available"""
    bl_idname = "scene.prolightingskies_next"
    bl_label = "Choose the next sky available"

    def execute(self,context):
        run_resync(self,context)

        current = get_image_by_category()

        for i in range(len(sublist)):
            if sublist[i][2]==current:
                if i==len(sublist)-1:
                    set_image_by_category(sublist[0][2])
                else:
                    set_image_by_category(sublist[i+1][2])

        return {'FINISHED'}


class previousSky(bpy.types.Operator):
    """Choose the previous sky available"""
    bl_idname = "scene.prolightingskies_previous"
    bl_label = "Choose the previous sky available"

    def execute(self,context):
        run_resync(self,context)

        current = get_image_by_category()

        for i in range(len(sublist)):
            if sublist[i][2]==current:
                if i==0:
                    set_image_by_category(sublist[len(sublist)-1][2])
                else:
                    set_image_by_category(sublist[i-1][2])

        return {'FINISHED'}


class reset_settings(bpy.types.Operator):
    """Reset settings to defaults"""
    bl_idname = "scene.prolightingskies_reset"
    bl_label = "Reset settings"

    def execute(self,context):

        context = bpy.context
        settings = context.scene.world.pl_skies_settings

        global setting_value_internally
        setting_value_internally = True

        # first set the properties
        settings.hue_camera = [1,1,1]
        settings.hue_lighting = [1,1,1]
        settings.saturation_camera = 1
        settings.saturation_lighting = 1
        settings.background_color = [0,0,0]
        settings.mirror_sky = 0
        settings.horizon = 0
        # settings.z_rotation = 0

        # now apply these defaults
        easyhdr_g = get_current_easyhdr_g(self, context)

        # apply_rotation_change(settings.z_rotation, easyhdr_g)
        if settings.use_advanced_sky==True:
            tmp = settings.hue_camera
            apply_cam_hue_change( [tmp.r,tmp.g,tmp.b,1], easyhdr_g)
            apply_cam_sat_change(settings.saturation_camera, easyhdr_g)
            tmp = settings.hue_lighting
            apply_light_hue_change( [tmp.r,tmp.g,tmp.b,1], easyhdr_g)
            apply_light_sat_change(settings.saturation_lighting, easyhdr_g)
            tmp = settings.background_color
            apply_background_color_change( [tmp.r,tmp.g,tmp.b,1], easyhdr_g)
            apply_mirror_sky_change(settings.mirror_sky, easyhdr_g)

            nds = bpy.data.node_groups['Advanced Settings'].nodes
            nds['Segment BG'].inputs[1].default_value = 0.01
            nds['Segment BG-2'].inputs[1].default_value = 0.01
            nds['Mirror Sky'].inputs[0].default_value = 1
            nds['Hue Multiply'].inputs[0].default_value = 1

            easyhdr_g = get_current_easyhdr_g(self, context)
            easyhdr_g.node_tree.nodes["Horizon Mapping"].translation[2] = 0

        setting_value_internally = False

        return {'FINISHED'}

# fix this later/make it better
filepath_global_temp = []

class install_zips_warning_menu(bpy.types.Menu):
    bl_label = "Blender freeze warning"
    bl_idname = "scene.installskybyzip_notice"

    def draw(self, context):
        layout = self.layout
        layout.label("Blender may freeze during install but please be patient as this is normal.", icon="ERROR")
        row = layout.row()
        row.scale_y = 2
        row.operator("scene.installskybyzip_delay",\
            text="Click to continue and wait")
        row = layout.row()
        row.scale_y = 1
        row.operator("scene.sky_insall_cancel",text="Cancel")

class install_skies_from_zip_delay(bpy.types.Operator):
    """Cancell installtion"""
    bl_idname = "scene.sky_insall_cancel"
    bl_label = "Cancel installing"

    def execute(self,context):
        return {'FINISHED'}

### ADDED NEW
class install_skies_from_zip_delay(bpy.types.Operator):
    """Blender may be unresponsive while zips install"""
    bl_idname = "scene.installskybyzip_delay"
    bl_label = "Blender may be unresponsive while zips install"

    def installSingleSet(self,exrpath,hdrroot):
        base = exrpath[:-8] # format ..._EXR.exr
        word = base.split(os.path.sep)[-1]
        hasThumb = os.path.isfile(base+"_thumb.jpg")
        hasHigh = os.path.isfile(base+"_high.jpg")
        hasMed = os.path.isfile(base+"_medium.jpg")
        hasLow = os.path.isfile(base+"_low.jpg")
        if hasThumb and hasHigh and hasMed and hasLow:

            for part in ["_EXR.exr","_thumb.jpg","_high.jpg",\
                    "_medium.jpg","_low.jpg"]:
                new_path = os.path.join(hdrroot,word+part)
                if os.path.isfile(new_path):
                    print("\tSkipping {x}, already installed".format(\
                        x = word+part))
                else:
                    os.rename( base+part,new_path )

            print("Installed {x} HDR set".format(x=word))
            return 1
        else:
            print("Missing at least one file of {x} pack".format(x=base))
            return 0

    def secure_unzip(self, source_filename, dest_dir):
        with zipfile.ZipFile(source_filename) as zf:
            for member in zf.infolist():
                words = member.filename.split(os.path.sep)
                path = dest_dir
                for word in words[:-1]:
                    drive, word = os.path.splitdrive(word)
                    head, word = os.path.split(word)
                    if word in (os.curdir, os.pardir, ''): continue
                    path = os.path.join(path, word)
                zf.extract(member, path)

    def start(self, context, filepath):
        filepath = bpy.path.abspath(filepath)
        if not os.path.isfile(filepath) or filepath[-4:] != ".zip":
            self.report({'ERROR'}, "Non zipfile selected or not found")
            return {'CANCELLED'}
        else:
            print("Installing "+filepath)
        numInstalled = 0
        tmpdir = os.path.join(os.path.dirname(__file__),"tmp")
        self.secure_unzip(filepath, tmpdir)

        # now go through and check each set, get a list of .exr's and such
        onlydirs = [ f for f in os.listdir(tmpdir) if \
                os.path.isdir(os.path.join(tmpdir,f)) ]

        for adir in onlydirs:
            ittemp = os.path.join(tmpdir,adir,adir)
            onlyfiles = [ f for f in os.listdir(ittemp) if \
                os.path.isfile(os.path.join(ittemp,f)) ]

            for fi in onlyfiles:
                if fi[-4:] == ".exr" or fi[-4:] == ".EXR":
                    numInstalled += self.installSingleSet( \
                        os.path.join(ittemp,fi),os.path.join( \
                        os.path.dirname(__file__),"hdris"))

        # now also do the root level, any files that may be there
        onlyfiles_root = [ f for f in os.listdir(tmpdir) if \
                os.path.isfile(os.path.join(tmpdir,f)) ]
        for fi in onlyfiles_root:
            if fi[-4:] == ".exr" or fi[-4:] == ".EXR":
                numInstalled += self.installSingleSet( \
                    os.path.join(tmpdir,fi),os.path.join( \
                    os.path.dirname(__file__),"hdris"))

        # at the very end, delete this temporary folder.
        shutil.rmtree(os.path.join(os.path.dirname(__file__),"tmp"))

        reload_all_JSON()
        #self.report({'INFO'}, "{x} skies installed".format(x=numInstalled))
        return numInstalled


    def execute(self,context):
        if len(filepath_global_temp)==0:
            self.report({'ERROR'}, "No files selected")
            print("No files selected")
            return {'CANCELLED'}

        check = False
        for one_zip in filepath_global_temp:
            if os.path.isfile(bpy.path.abspath(one_zip)):
                check = True
                break
        if check==False:
            self.report({'ERROR'}, "Zip file(s) not found")
            print("Zip file(s) not found")
            return {'CANCELLED'}

        print(filepath_global_temp)
        count = 0
        for one_zip in filepath_global_temp:
            count += self.start(context,one_zip)
        self.report({'INFO'}, "{x} skies installed".format(x=count))
        return {'FINISHED'}


class installSkiesFromZip(bpy.types.Operator, ImportHelper):
    """Install approved HDR pack from selected zips"""
    bl_idname = "scene.installskybyzip"
    bl_label = "Install blenderguru HDR pack from selected zip files"

    filename_ext = ".zip"
    filter_glob = bpy.props.StringProperty(
            default="*.zip",
            options={'HIDDEN'},
            )
    fileselectparams = "use_filter_blender"
    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    def execute(self,context):
        global filepath_global_temp
        folder = (os.path.dirname(self.filepath))
        paths = [os.path.join(folder, name.name)
                 for name in self.files]
        filepath_global_temp = paths

        bpy.ops.wm.call_menu(name=install_zips_warning_menu.bl_idname)
        return {'FINISHED'}


class fav_toggle_op(bpy.types.Operator):
    """Set or remove this sky from favorites"""
    bl_idname = "scene.proskies_fave_toggle_op"
    bl_label = "Togle Favorite"
    bl_description = "Toggle the favorite status of this sky"

    def execute(self,context):


        global internal_fave_change
        global environments
        global categories
        global category_selected

        internal_fave_change = True

        settings = context.scene.world.pl_skies_settings
        envs_path = os.path.join(os.path.dirname(__file__), "envs.json")

        # save the state
        current = get_image_by_category() # check this is the correct one
        current_cat = settings.category

        infile = open(envs_path,'r')
        try:
            data = json.load(infile)
        except:
            self.report({'ERROR'}, \
                    "Error loading the JSON file, restore envs.json or "+\
                    "reinstall the addon")
            return {'CANCELLED'}

        infile.close()
        if 'favorites' not in data['categories']:
            data['categories']['favorites']={}
        elif type(data['categories']['favorites']) == type([]):
            # turn list into dictionary
            print("Updating the datastructure of sky favorites")
            d = {}
            for entry in data['categories']['favorites']:
                d.update({entry:[-1,-1]})
            data['categories']['favorites'] = d

        # should do a check on the legitimacy of the favorites structure
        # this *shouldn't* ever happen however after the above
        if type(data['categories']['favorites']) != type({}):
            self.report({'ERROR'},"Error processing favorites in envs.json,"+\
                    " please reinstall Pro Lighting: skies")
            return {'CANCELLED'}

        # now for the toggle aspect: add or remove this sky
        if current not in data['categories']['favorites']:
            data['categories']['favorites'].update(
                    { current:[settings.sun,settings.sky] })
        else:
            #ind = data['categories']['favorites'].index(current)
            #del data['categories']['favorites'][ind]

            # possible error, do handling
            data['categories']['favorites'].pop(current)

        # ensure cateogires/etc are properly updated
        environments = data["environments"]
        categories = data["categories"]

        # the definite way to do it, though toggling would be more direct
        if current in categories['favorites']:
            settings.current_favorite = True
        else:
            settings.current_favorite = False

        # force the categories to be correct
        settings.category = current_cat # shouldn't have to
        category_selected = current_cat
        settings.category_string = current_cat

        # save the file back out for future use of favorite
        outf = open(envs_path,'w')
        data_out = json.dumps(data,indent=4)
        outf.write(data_out)
        outf.close()

        return {'FINISHED'}


def reload_all_JSON():

    addon_prefs = \
            bpy.context.user_preferences.addons[__package__].preferences

    # relaod the json file
    global environments
    global categories
    if os.path.isfile( os.path.join(os.path.dirname(__file__),"envs.json") ) == False:
        self.report({'ERROR'}, "Missing envs.json file, please reinstall skies addon")
        return
    builtin = []

    with open(os.path.join(os.path.dirname(__file__),"envs.json")) as data_file:
        ### can't do error reporting in this context
        # try:
        #     data = json.load(data_file)
        # except:
        #     self.report({'ERROR'}, \
        #             "Error loading the JSON file, restore envs.json")
        #     return {'CANCELLED'}

        data = json.load(data_file)
        environments = data["environments"]
        categories = data["categories"]
        builtin = data["builtin_check"]

    # reset the number installed, to check if all are installed
    hdris_path = os.path.join(os.path.dirname(__file__),"hdris")

    if os.path.isdir(hdris_path)==False:
        os.mkdir(hdris_path) # could be an exception if no permission


    # now verify if everything is installed
    addon_prefs.installedHDRcount = 0
    addon_prefs.builtin_counted = len(builtin)
    for f in builtin:
        installed = True
        base = os.path.join(hdris_path,f)
        if not (os.path.isfile(base+"_EXR.exr") or os.path.isfile(base+"_HDR.hdr")):
            print("\tMissing {f}'s EXR/HDR".format(f=f))
            installed = False
        if not os.path.isfile(base+"_thumb.jpg"):
            print("\tMissing {f}_thumb.jpg".format(f=f))
            installed = False

        hasHigh = os.path.isfile(base+"_high.jpg")
        hasMed = os.path.isfile(base+"_medium.jpg")
        hasLow = os.path.isfile(base+"_low.jpg")
        if not hasHigh:
            print("\tmissing {f}_high.jpg".format(f=f))
            installed = False
        if not hasMed:
            print("\tmissing {f}_medium.jpg".format(f=f))
            installed = False
        if not hasLow:
            print("\tmissing {f}_low.jpg".format(f=f))
            installed = False

        if installed==True:
            addon_prefs.installedHDRcount+= 1
        else:
            print("Set "+f+"\tis missing some files")


    # reload icons
    reloadIcons(keep_previews=False)



class reloadJSONS(bpy.types.Operator):
    """Reload all skies/icons, use after manually copying HDRs to the hdris folder"""
    bl_idname = "scene.prolightingskies_reload_jsons"
    bl_label = "Reload all skies/icons, use after manually copying HDRs to the hdris folder"

    def execute(self,context):
        reload_all_JSON()
        return {'FINISHED'}


class openHDRFolder(bpy.types.Operator):
    """Open the hdr folder for manual sky installing"""
    bl_idname = "scene.open_hdr_folder"
    bl_label = "Open hdr folder"

    def execute(self,context):
        import subprocess
        path = os.path.join(os.path.dirname(__file__), "hdris")
        try:
            # windows... untested
            subprocess.Popen('explorer "{x}"'.format(x=bpy.path.abspath(path)))
        except:
            try:
                # mac... works on Yosemite minimally
                subprocess.call(["open", bpy.path.abspath(path)])
            except:
                self.report({'ERROR'}, \
                    "Didn't open folder, navigate to {x} manually".format(x=path))
                return {'CANCELLED'}
        return {'FINISHED'}


class disableIncompatible(bpy.types.Operator):
    """Disable incompatbile Pro Lighting: Studio background/reflections"""
    bl_idname = "scene.prolightingskies_disable_plstudio"
    bl_label = "Disable Pro Lighting: Studio"

    def execute(self,context):

        if "pl_studio_props" in context.scene:
            plstudio = context.scene.pl_studio_props
            if plstudio.use_pl_studio_background == True:
                plstudio.use_pl_studio_background = False
            if plstudio.use_pl_studio_reflections == True:
                plstudio.use_pl_studio_reflections = False

            # now apply enable or not
            settings = context.scene.world.pl_skies_settings
            settings.use_pl_skies = settings.use_pl_skies

        return {'FINISHED'}


def reloadIcons(keep_previews=True):
    # after installing HDRI's or changing category
    # first clear existing if needed

    if keep_previews==False:
        if use_icons:
            for pcoll in preview_collections.values():
                bpy.utils.previews.remove(pcoll)
            preview_collections.clear()

        preview_collections.clear()
        global thumb_ids
        thumb_ids = {} # clear them out too

    # now reload
    if use_icons:
        pcoll = bpy.utils.previews.new()
        pcoll.imgs_dir = os.path.join(os.path.dirname(__file__), "hdris")
        preview_collections["env_previews"] = pcoll

        # default / all
        bpy.types.World.env_previews = EnumProperty(
            items=generate_previews(),
            update=change_image_cb
        )
        # categorical
        bpy.types.World.env_previews_night = EnumProperty(
            items=reload_night(),
            update=change_image_cb_night
        )
        bpy.types.World.env_previews_overcast = EnumProperty(
            items=reload_overcast(),
            update=change_image_cb_overcast
        )
        bpy.types.World.env_previews_evening = EnumProperty(
            items=reload_evening(),
            update=change_image_cb_evening
        )
        bpy.types.World.env_previews_cloudy = EnumProperty(
            items=reload_cloudy(),
            update=change_image_cb_cloudy
        )
        bpy.types.World.env_previews_sunset = EnumProperty(
            items=reload_sunset(),
            update=change_image_cb_sunset
        )
        bpy.types.World.env_previews_morning = EnumProperty(
            items=reload_morning(),
            update=change_image_cb_morning
        )
        bpy.types.World.env_previews_clear = EnumProperty(
            items=reload_clear(),
            update=change_image_cb_clear
        )
        bpy.types.World.env_previews_space = EnumProperty(
            items=reload_space(),
            update=change_image_cb_space
        )
        bpy.types.World.env_previews_custom = EnumProperty(
            items=reload_custom(),
            update=change_image_cb_custom
        )
        bpy.types.World.env_previews_favorites = EnumProperty(
            items=reload_favorites(),
            update=change_image_cb_favorites
        )


    else:
        preview_collections["env_previews"] = previewsReplacement()
        preview_collections["env_previews"].imgs_dir = \
            os.path.join(os.path.dirname(__file__), "hdris")
        bpy.types.World.env_previews = EnumProperty(
            items=generate_previews_text(),
            update=change_image_cb
        )


class setCyclesActive(bpy.types.Operator):
    """Set render engine to cycles to use addon"""
    bl_idname = "scene.prolightingskies_set_cycles"
    bl_label = "Enable Cycles"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        bpy.context.scene.render.engine = 'CYCLES'
        return {'FINISHED'}


# intermediates to have loading individualized
def reload_all():
    return generate_previews()
def reload_night():
    return generate_previews()
def reload_overcast():
    return generate_previews()
def reload_evening():
    return generate_previews()
def reload_cloudy():
    return generate_previews()
def reload_sunset():
    return generate_previews()
def reload_morning():
    return generate_previews()
def reload_clear():
    return generate_previews()
def reload_space():
    return generate_previews()
def reload_custom():
    return generate_previews()
def reload_favorites():
    return generate_previews()

# and for the change images
def change_image_cb_all(self, context):
    change_image_cb(self, context)
    return None
def change_image_cb_night(self, context):
    change_image_cb(self, context)
    return None
def change_image_cb_overcast(self, context):
    change_image_cb(self, context)
    return None
def change_image_cb_evening(self, context):
    change_image_cb(self, context)
    return None
def change_image_cb_cloudy(self, context):
    change_image_cb(self, context)
    return None
def change_image_cb_sunset(self, context):
    change_image_cb(self, context)
    return None
def change_image_cb_morning(self, context):
    change_image_cb(self, context)
    return None
def change_image_cb_clear(self, context):
    change_image_cb(self, context)
    return None
def change_image_cb_space(self, context):
    change_image_cb(self, context)
    return None
def change_image_cb_custom(self, context):
    change_image_cb(self, context)
    return None
def change_image_cb_favorites(self, context):
    change_image_cb(self, context)
    return None


# -----------------------------------------------------------------------------

class CyclesWorld_PT_ProLightingSkies(Panel):
    """Pro Lighting: Skies"""
    bl_idname = "CyclesWorld_PT_ProLightingSkies"
    bl_label = "Pro Lighting: Skies (Demo)"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"
    COMPAT_ENGINES = {'CYCLES'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        world = scene.world
        rd = scene.render
        return world

    def draw_header(self, context):
        settings = context.scene.world.pl_skies_settings
        self.layout.prop(settings, "use_pl_skies", text="")

    def draw(self, context):
        global category_selected
        global newload

        addon_prefs = \
            bpy.context.user_preferences.addons[__package__].preferences

        layout = self.layout
        world  = context.scene.world

        # if render engine not cycles, give warning message
        if context.scene.render.engine != 'CYCLES':
            layout.label(text="Addon only compatible with Cycles",
                        icon='ERROR')
            # enable cycles button? nah.
            layout.operator("scene.prolightingskies_set_cycles")
            return

        if "pl_studio_props" in context.scene:
            try: # just in case
                plstudio = context.scene.pl_studio_props
                if plstudio.use_pl_studio_background == True or plstudio.use_pl_studio_reflections == True:
                    layout.label(text="Addon not compatible with",
                            icon='ERROR')
                    layout.label(text="Pro Lighting studio backgrounds")
                    layout.label(text="or reflections")
                    # enable cycles button? nah.
                    layout.operator("scene.prolightingskies_disable_plstudio")
                    return
            except:
                pass

        settings = world.pl_skies_settings
        cworld = context.scene.world.cycles

        layout.enabled = settings.use_pl_skies

        # check for installed hdris
        if addon_prefs.installedHDRcount == 0:
            layout.label(text="No HDRs are installed, go to", icon="ERROR")
            layout.label(text="user preferences to install them")
            return
        elif addon_prefs.builtin_counted > addon_prefs.installedHDRcount:
            layout.label(text="Only {x} of {y} non-custom HDRs installed, go to".format( \
                x=addon_prefs.installedHDRcount,\
                y=addon_prefs.builtin_counted), icon="ERROR")
            layout.label(text="user preferences to install the rest")

        # debug
        if False:
            layout.label(text="text="+temp_node_change)

        row = layout.row()
        col = row.column()
        col.prop(settings,"category")
        col = row.column()
        if newload==True:
            col.enabled=False
        if settings.current_favorite==False:
            # col.prop(settings,"current_favorite", text='', icon='SOLO_OFF')
            col.operator("scene.proskies_fave_toggle_op",icon='SOLO_OFF',text='')
        else:
            # col.prop(settings,"current_favorite", text='', icon='SOLO_ON')
            col.operator("scene.proskies_fave_toggle_op",icon='SOLO_ON',text='')
        if use_icons:
            row = layout.row()
            col = row.column()
            col.scale_y= 6
            col.operator("scene.prolightingskies_previous",\
                         icon="TRIA_LEFT",text="")
            col = row.column()
            if settings.category != category_selected:
                # they were different
                category_selected = settings.category
            elif category_selected=="":
                category_selected = "all"

            if newload == False:
                if hasattr(world,"env_previews_"+category_selected)==True:
                    col.template_icon_view(world, "env_previews_"+category_selected,\
                                show_labels=False) #layout
                else:
                    # default ategory, or one from previous version
                    col.template_icon_view(world, "env_previews",\
                               show_labels=False) #layout
            else:
                col.scale_y= 6
                col.operator("scene.prolightingskies_resync",
                    text="Press to resync active sky")
            col = row.column()
            col.scale_y= 6
            col.operator("scene.prolightingskies_next",\
                        icon="TRIA_RIGHT",text="")

        else:
            # For previous blender versions without custom icons
            layout.prop(world, "env_previews")
            layout.label("(Use blender 2.75+ for previews)")

        # node values
        layout.prop(settings, "sun")
        layout.prop(settings, "sky")
        layout.prop(settings, "z_rotation")

        if skies_is_keyframed(self, context):
            layout.label(text="Don't add keyframes here,", icon="ERROR")
            layout.label("    keyframe world node group directly")
            layout.label("    (clear keyframes to remove warning)")

        # quality
        row = layout.row()
        row.label("Background quality:")
        row = layout.row()
        row.prop(settings, "quality", text="Background quality", expand=True)
        adv = layout.row()
        adv.label("")

        # advanced options
        adv = layout.row()
        if settings.show_advanced == False:
            adv.prop(settings, "show_advanced", icon="TRIA_RIGHT",\
                text="Show advanced options")
        else:
            adv.prop(settings, "show_advanced", icon="TRIA_DOWN",\
                text="Hide advanced options")


            box = layout.box()

            row = box.row()
            row.prop(settings,"use_advanced_sky")
            row = box.row()
            row.operator("scene.prolightingskies_reset")
            # col = row.column()
            if newload==True or settings.use_advanced_sky==False:
                row.enabled=False


            row = box.row()
            row.enabled = settings.use_advanced_sky
            col = row.column()
            col.prop(settings, "horizon", text="Horizon level", slider=True)
            row = box.row()
            row.label("Sky bottom settings")
            row = box.row()
            row.enabled = settings.use_advanced_sky
            col = row.column()
            col.prop(settings, "background_color", text="")
            col = row.column()
            col.prop(settings, "mirror_sky", text="Mirror", slider=True)

            row = box.row()
            row.label("Background Color")
            row = box.row()
            row.enabled = settings.use_advanced_sky
            col = row.column()
            col.prop(settings, "hue_camera", text="")
            col = row.column()
            col.prop(settings, "saturation_camera", text="Saturation")

            row = box.row()
            row.enabled = settings.use_advanced_sky
            row.label("Lighting Color")
            row = box.row()
            row.enabled = settings.use_advanced_sky
            col = row.column()
            col.prop(settings, "hue_lighting", text="")
            col = row.column()
            col.prop(settings, "saturation_lighting", text="Saturation")


            row = box.row()
            row.label("Scene settings")
            row = box.row()

            scene = context.scene
            cscene = scene.cycles
            split = row.split()
            col = split.column()
            col.prop(cscene, "film_exposure")

            col = split.column()
            sub = col.column(align=True)
            sub.prop(cscene, "film_transparent")


class ProLightingSkiesSettings(PropertyGroup):

    use_pl_skies = BoolProperty(
        name="Pro Lighting: Skies",
        description="Use a Pro Lighting: Skies node setup for the world",
        default=False,
        update=toggle_pl_skies
    )

    sun = FloatProperty(
        name="Sun",
        description="Drives the value in the Multiply node",
        update=change_sun_cb,
        default=1,
        precision=3,
        min=0
    )

    sky = FloatProperty(
        name="Sky",
        description="Drives the value in the Add node",
        update=change_sky_cb,
        default=1,
        precision=3,
        min=0
    )

    z_rotation = FloatProperty(
        name="Rotation",
        description="Rotation of the Sky around Z",
        update=change_rotation_cb,
        default=radians(0),
        unit='ROTATION'
    )

    quality = EnumProperty(
        name="Quality",
        description="Resolution of the JPG image used in the node setup",
        update=change_res_cb,
        items=[
            ('_low', "Low", "", 0),
            ('_medium', "Medium", "", 1),
            ('_high', "High", "", 2),
        ],
        default='_medium'
    )

    hue_camera = FloatVectorProperty(
        name="Camera Hue",
        description="Color tinting for background. White is off.",
        subtype='COLOR',
        update=change_cam_hue,
        default=[1.0,1.0,1.0],
        min=0.0,
        max=1.0,
    )
    saturation_camera = FloatProperty(
        name="Camera saturation",
        description="Color saturation for background. 1 is default.",
        update=change_cam_sat,
        default=1,
        min=0.0,
    )

    hue_lighting = FloatVectorProperty(
        name="Lighting Hue",
        description="Color tinting for scene lighting. White is off.",
        subtype='COLOR',
        update=change_light_hue,
        default=[1.0,1.0,1.0],
        min=0.0,
        max=1.0,
    )
    saturation_lighting = FloatProperty(
        name="Lighting saturation",
        description="Color saturation for lighting. 1 is default",
        update=change_light_sat,
        default=1,
        min=0.0,
    )
    background_color = FloatVectorProperty(
        name="Background Color",
        description="Replaces pure black in hdr's with this color",
        subtype='COLOR',
        update=change_background_color,
        default=[0.0,0.0,0.0],
        min=0.0,
        max=1.0,
    )
    mirror_sky = FloatProperty(
        name="Mirror sky",
        description="Mix between no and full sky top/bottom mirroring",
        update=change_mirror_sky,
        default=0,
        min=0.0,
        max=1.0,
    )
    horizon = FloatProperty(
        name="Horizon level",
        description="Adjust the level of the horizon",
        update=change_horizon,
        default=0,
        min=-1.0,
        max=1.0,
    )

    # multi importance sampling backup

    sample_as_light = BoolProperty(
        name="Multiple Importance Bckp",
        description="Backup for the value before turning EasyEnv On/Off",
        default=True,
    )
    sample_map_resolution = IntProperty(
        name="MI Map Res Bckp",
        description="Backup for the value before turning EasyEnv On/Off",
        default=2048,
    )
    samples = IntProperty(
        name="MI Samples Bckp",
        description="Backup for the value before turning EasyEnv On/Off",
        default=4,
    )
    show_advanced = BoolProperty(
        name="Show or hide advanced options",
        description="Show/hide the advanced sky lighting options",
        default=False,
    )
    show_debug = BoolProperty(
        name="Installation debugging",
        description="Show or hide installation debug functions",
        default=False,
    )
    use_advanced_sky = BoolProperty(
        name="Use advanced settings",
        description="Enable for more artistic control, but slightly slower renders",
        default=False,
        update=sky_node_complexity,
    )
    current_favorite = BoolProperty(
        name="Toggle Favorite",
        description="Set or remove this sky from favorites",
        default=False,
    )

    category = EnumProperty(
        name="Sky category",
        description="Category of skies to show",
        update=category_load,
        items=category_items
    )
    category_string = bpy.props.StringProperty(
        name="Internal String Name",
        description="String category of skies to show, for resync",
        default=""
    )
    image_string = bpy.props.StringProperty(
        name="Internal image Name",
        description="String image of skies to show, for resync",
        default=""
    )


class prolightingSkiesPreferencePanel(bpy.types.AddonPreferences):
    bl_idname = __package__
    scriptdir = bpy.path.abspath(os.path.dirname(__file__))

    hdrpath = bpy.props.StringProperty(
        name = "hdrpath",
        description = "Folder where the hdr's reside",
        subtype = 'DIR_PATH',
        default = scriptdir+'/hdris/'
    )
    installedHDRcount = IntProperty(
        name="MI Samples Bckp",
        description="A second check for installed HDRs",
        default=0,
    )
    use_icons_pref = bpy.props.BoolProperty(
        name = "Use preview icons",
        description = "For blender 2.75+, enable or disable icon use",
        default = True)
    show_custom_install = bpy.props.BoolProperty(
        name = "Install custom HDRs",
        description = "Instructions for installing custom sets of skies",
        default = False
    )
    builtin_counted = IntProperty(
        name = "Builtin skies counted",
        description = "Backend property for verifying proper count"+\
            "of provided skies installed",
        default = 0
    )

    def draw(self, context):


        layout = self.layout
        not_installed = self.builtin_counted > self.installedHDRcount

        if not_installed == True:
            # check for installed hdris
            if self.installedHDRcount == 0:
                layout.label(text="No HDRs are installed,", icon="ERROR")
                layout.label(text="    follow the instructions below")
            elif self.builtin_counted > self.installedHDRcount:
                layout.label(text="Only {x} of {y} HDRs installed,".format( \
                    x=self.installedHDRcount,y=self.builtin_counted), icon="ERROR")
                layout.label(text="    follow the instructions below")

        else:

            if context.scene.render.engine != 'CYCLES':
                layout.label(text="Cycles not active,", icon="ERROR")
                layout.operator("scene.prolightingskies_set_cycles")
            else:
                layout.label("All {y} HDRs installed. ".format( \
                    y=self.builtin_counted), icon="FILE_TICK")
                layout.label("Addon is now successfully installed and ready to use :)")

        # primary installation
        row = layout.row()
        col = row.column()
        col.scale_x = 0.125
        col.label("")
        col = row.column()
        col.scale_x = 0.75
        box = col.box()
        box.operator("wm.url_open",text="Watch Installation Video",\
            icon='CLIP').url = \
            "http://www.blenderguru.com/install-pro-lighting-skies/"
        box.label(text="INSTALLATION STEPS")
        box.label(text="1. Click the 'Install HDRs from ZIP' button below")
        box.label(text="2. Locate the HDR zip you downloaded from Blender Guru, xxx.zip")
        box.label(text="3. Select the zip file")
        box.label(text="5. Click the install button, but expect blender to hang while installing")
        box.label(text="4. The icon above should change to a green tick when"+\
                            " installation is complete.")
        box.label(text="")
        box.operator("scene.installskybyzip",text="Install HDRs from zip",
                icon="PACKAGE")
        col = row.column()
        col.scale_x = 0.125
        col.label("")

        row = layout.row()
        if not_installed == False:
            row.enabled = False


        # primary installation
        row = layout.row()
        col = row.column()
        col.scale_x = 0.125
        col.label("")
        col = row.column()
        col.scale_x = 0.75
        box = col.box()
        box.label(text="CUSTOM HDR INSTALLATION")
        box.label(text='Get the lite or ultimate version to custom install your own HDRs')
        box.operator("wm.url_open",text="Get Pro Lighting: Skies here",\
            ).url = \
            "http://www.blenderguru.com/product/pro-lighting-skies/"
        # box.operator("scene.install_custom",text="Install custom HDR set",
        #         icon='IMAGE_DATA')
        col = row.column()
        col.scale_x = 0.125

        col.label("")

        #row.prop(self,"use_icons_pref")

        # debugging
        layout = self.layout
        world  = context.scene.world
        settings = world.pl_skies_settings
        layout.label("Install debugging")
        row = layout.row()
        col = row.column()
        col.operator("scene.prolightingskies_reload_jsons", \
            text="Reload all skies", icon="LOOP_BACK")
        col = row.column()
        col.operator("scene.open_hdr_folder", text="Open HDR folder",
                icon="FILE_FOLDER")


# class to mimic utils.previews object, for blender without custom icons
class previewsReplacement(dict):
    pass


def register():

    # first, rebuild the json for installed hdrs
    bpy.types.World.pl_skies_settings = \
        PointerProperty(type=ProLightingSkiesSettings)
    bpy.types
    reload_all_JSON()

    bpy.types.Node.is_pl_skies = BoolProperty(default=False)
    bpy.types.Node.pl_skies_was_last_linked = BoolProperty(default=False)
    bpy.types.Image.pl_skies_flag = BoolProperty(default=False)




def unregister():

    if use_icons:
        for pcoll in preview_collections.values():
            bpy.utils.previews.remove(pcoll)
        preview_collections.clear()

    preview_collections.clear()

    del bpy.types.World.env_previews
    del bpy.types.World.pl_skies_settings

    del bpy.types.Node.is_pl_skies
    del bpy.types.Node.pl_skies_was_last_linked
    del bpy.types.Image.pl_skies_flag
