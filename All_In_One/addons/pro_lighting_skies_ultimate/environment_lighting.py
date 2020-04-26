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
from bpy.types import Operator
from bpy.types import Panel
from bpy.types import PropertyGroup
from bpy.props import BoolProperty
from bpy.props import IntProperty
from bpy.props import FloatProperty
from bpy.props import EnumProperty
from bpy.props import PointerProperty
import bpy.utils.previews


# setting up the environments -------------------------------------------------

# loading the envs data from json file
environments = []
with open(os.path.join(os.path.dirname(__file__), "envs.json")) as data_file:
    # format: ("label", "description", "file_naming", "sun", "sky")
    environments = json.load(data_file)["environments"]
# if there is a problem with the envs file, better let the addon crash

# dict to hold the ui previews collection
preview_collections = {}


# create th previews and an enum with label, tooltip and preview as custom icon
def generate_previews():
    env_previews = preview_collections["env_previews"]
    folder_path = env_previews.imgs_dir

    enum_items = []
    i = 0
    for label, desc, img_name, sun, sky in environments:
        thumb = env_previews.load(
            img_name,
            os.path.join(folder_path, img_name + "_thumb.jpg"),
            'IMAGE'
        )
        enum_items.append((img_name, label, desc, thumb.icon_id, i))
        i += 1

    return enum_items

# -----------------------------------------------------------------------------

# creating the node setup -----------------------------------------------------
def get_node_setup():
    try:
        return get_node_setup.node_setup
    except AttributeError:
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
                "Environment Texture 1": {
                    "type_id": "ShaderNodeTexEnvironment",
                    "type": "TEX_ENVIRONMENT",
                    "name": "Environment Texture 1",
                    "location": mathutils.Vector((-430, 100)),
                },
                "Environment Texture 2": {
                    "type_id": "ShaderNodeTexEnvironment",
                    "type": "TEX_ENVIRONMENT",
                    "name": "Environment Texture 2",
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
                ("Rotate Z", 0, "Environment Texture 1", 0),
                ("Rotate Z", 0, "Environment Texture 2", 0),
                ("Environment Texture 1", 0, "Background 1", 0),
                ("Environment Texture 2", 0, "Background 2", 0),
                ("Environment Texture 2", 0, "Multiply", 0),
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

def get_group(name):
    setup = get_node_setup()["groups"][name]

    # try to get by name
    group_node_tree = bpy.data.node_groups.get(name)

    if group_node_tree:
        # if it has changes, we change the name and make a new node group tree
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

    enum_choice = world.env_previews

    apply_image_change(enum_choice, g_nodes)
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

    # checking nodes

    for g_n in g_nodes:
        d_n = setup['nodes'][g_n.name]

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
            if real_val != def_val:
                return True

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

def get_current_easyhdr_g(self, context):
    world = context.scene.world
    w_nodes = world.node_tree.nodes

    w_out = get_world_output(self, context)
    if w_out:
        easyhdr_g = get_currently_linked(w_out, 0)
        # TODO improve this
        if not (easyhdr_g and easyhdr_g.is_pl_skies):
            groups = [n for n in w_nodes if n.type == 'GROUP' and n.is_pl_skies]
            if next(iter(groups), None):
                easyhdr_g = groups[0]

    # test for changes
    if easyhdr_g:
        if has_changes(easyhdr_g.node_tree, get_node_setup()):
            easyhdr_g = None

    if not easyhdr_g:
        set_group_names_as_edited()
        easyhdr_g = create_node_group_setup()
        easyhdr_g.location = smart_place_easyenv_group(easyhdr_g.name)

        if w_out:
            w_links = world.node_tree.links
            w_links.new(easyhdr_g.outputs[0], w_out.inputs[0])

    return easyhdr_g


def smart_place_world_output(node_name):
    # W out default position
    return (300, 300)

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
                    # there can be more than one lost #TODO how to get the best one?
                    if has_changes(n.node_tree, get_node_setup()) == False:
                        easyhdr_g = n

            if not easyhdr_g:
                # searching for an unchanged easyhdr group node with no users
                for n in bpy.data.node_groups:
                    if n.users == 0 and has_changes(n, get_node_setup()) == False: # n.is_pl_skies
                        set_group_names_as_edited()
                        easyhdr_g = w_nodes.new("ShaderNodeGroup")
                        easyhdr_g.name = get_node_setup()["group"]["name"]
                        easyhdr_g.node_tree = n
                        easyhdr_g.is_pl_skies = True

            if not easyhdr_g:
                # we are turning on easy hdr and there is no previous easyhdr node
                set_group_names_as_edited()
                easyhdr_g = create_node_group_setup()
                easyhdr_g.location = smart_place_easyenv_group(easyhdr_g.name)

        # now we can safely link the easy HDR group with the world output
        w_links.new(easyhdr_g.outputs[0], w_out.inputs[0])

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

            #settings["sun"] = sun  # does not call callback, but also does not update interface

            global setting_value_internally
            setting_value_internally = True

            settings.sun = sun
            apply_sun_change(sun, easyhdr_g)
            settings.sky = sky
            apply_sky_change(sky, easyhdr_g)

            setting_value_internally = False
            break


def apply_change_node_image(tex_node, image_name, image_source_path):

    pl_skies_image = None

    # check if node already has an image that is ours
    if tex_node.image and tex_node.image.pl_skies_flag:
        pl_skies_image = tex_node.image

    # if it does, we just change the source of our image datablock
    if pl_skies_image:
        pl_skies_image.filepath = image_source_path
    # if not, the user has deleted or switched the image, we create a new one
    else:
        # create a new image and assign (do not destroy previously linked img)
        image = bpy.data.images.load(image_source_path)
        image.name = image_name
        image.pl_skies_flag = True

        tex_node.image = image


def apply_image_change(enum_choice, g_nodes):

    # get image source names from current enum choice
    folder_path = preview_collections["env_previews"].imgs_dir
    quality = bpy.context.scene.world.pl_skies_settings.quality

    path_img_exr = os.path.join(folder_path, enum_choice + "_EXR.exr")
    path_img_jpg = os.path.join(folder_path, enum_choice + quality + ".jpg")

    for node_name, image_name, image_source_path in \
        [("Environment Texture 1", "JPG", path_img_jpg),
         ("Environment Texture 2", "EXR", path_img_exr)]:

        # get node by name
        tex_node = g_nodes[node_name]

        apply_change_node_image(tex_node, image_name, image_source_path)

def change_image_cb(self, context):

    easyhdr_g = get_current_easyhdr_g(self, context)
    g_nodes = easyhdr_g.node_tree.nodes

    enum_choice = self.env_previews

    apply_image_change(enum_choice, g_nodes)
    apply_defaults(enum_choice, easyhdr_g)

    return None


def apply_res_change(enum_choice, g_nodes):
    current_env = bpy.context.world.env_previews
    folder_path = preview_collections["env_previews"].imgs_dir
    path_img_jpg = os.path.join(folder_path, current_env + enum_choice + ".jpg")

    # get node by name
    tex_node = g_nodes["Environment Texture 1"]
    apply_change_node_image(tex_node, "JPG", path_img_jpg)

def change_res_cb(self, context):
    easyhdr_g = get_current_easyhdr_g(self, context)
    g_nodes = easyhdr_g.node_tree.nodes

    apply_res_change(self.quality, g_nodes)

    return None


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


def apply_rotation_change(value, group_node):
    group_node.inputs[0].default_value = value

def change_rotation_cb(self, context):
    easyhdr_g = get_current_easyhdr_g(self, context)
    apply_rotation_change(self.z_rotation, easyhdr_g)

    return None

# -----------------------------------------------------------------------------

class CyclesWorld_PT_ProLightingSkies(Panel):
    """Pro Lighting: Skies"""
    bl_idname = "CyclesWorld_PT_ProLightingSkies"
    bl_label = "Pro Lighting: Skies (Ultimate)"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"
    COMPAT_ENGINES = {'CYCLES'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        world = scene.world
        rd = scene.render
        return rd.engine in cls.COMPAT_ENGINES and world

    def draw_header(self, context):
        settings = context.scene.world.pl_skies_settings
        self.layout.prop(settings, "use_pl_skies", text="")

    def draw(self, context):
        layout = self.layout

        world  = context.scene.world
        settings = world.pl_skies_settings
        cworld = context.scene.world.cycles

        layout.enabled = settings.use_pl_skies

        # previews
        layout.template_icon_view(world, "env_previews", show_labels=False)

        # node values
        layout.prop(settings, "sun")
        layout.prop(settings, "sky")
        layout.prop(settings, "z_rotation")

        # quality
        row = layout.row()
        row.label(settings.bl_rna.quality[1]["name"] + ":")
        row.prop(settings, "quality", expand=True)


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
        precision=3
    )

    sky = FloatProperty(
        name="Sky",
        description="Drives the value in the Add node",
        update=change_sky_cb,
        default=1,
        precision=3
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


def register():

    pcoll = bpy.utils.previews.new()
    pcoll.imgs_dir = os.path.join(os.path.dirname(__file__), "hdris")
    preview_collections["env_previews"] = pcoll

    bpy.types.World.env_previews = EnumProperty(
        items=generate_previews(),
        update=change_image_cb
    )

    bpy.types.World.pl_skies_settings = \
        PointerProperty(type=ProLightingSkiesSettings)

    bpy.types.Node.is_pl_skies = BoolProperty(default=False)
    bpy.types.Node.pl_skies_was_last_linked = BoolProperty(default=False)
    bpy.types.Image.pl_skies_flag = BoolProperty(default=False)


def unregister():

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    del bpy.types.World.env_previews

    del bpy.types.World.pl_skies_settings

    del bpy.types.Node.is_pl_skies
    del bpy.types.Node.pl_skies_was_last_linked
    del bpy.types.Image.pl_skies_flag
