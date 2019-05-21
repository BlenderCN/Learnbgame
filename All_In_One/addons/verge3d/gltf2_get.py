# Copyright (c) 2017 The Khronos Group Inc.
# Modifications Copyright (c) 2017-2018 Soft8Soft LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

#
# Imports
#

import bpy
import os

from .gltf2_debug import *
from .utils import *

#
# Globals
#

#
# Functions
#


def get_used_materials():
    """
    Gathers and returns all unfiltered, valid Blender materials.
    """

    materials = []

    for blender_material in bpy.data.materials:
        materials.append(blender_material)

    return materials


def get_material_requires_texcoords(glTF, index):
    """
    Query function, if a material "needs" texture cooridnates. This is the case, if a texture is present and used.
    """

    if glTF.get('materials') is None:
        return False

    materials = glTF['materials']

    if index < 0 or index >= len(materials):
        return False

    material = materials[index]

    # General

    if material.get('emissiveTexture') is not None:
        return True

    if material.get('normalTexture') is not None:
        return True

    if material.get('occlusionTexture') is not None:
        return True

    # Metallic roughness

    if material.get('baseColorTexture') is not None:
        return True

    if material.get('metallicRoughnessTexture') is not None:
        return True

    # Common Material

    v3d_data = get_asset_extension(material, 'S8S_v3d_material_data')
    if v3d_data:

        if v3d_data.get('diffuseTexture') is not None:
            return True

        if v3d_data.get('alphaTexture') is not None:
            return True

        if v3d_data.get('specularTexture') is not None:
            return True

    return False


def get_material_requires_normals(glTF, index):
    """
    Query function, if a material "needs" normals. This is the case, if a texture is present and used.
    At point of writing, same function as for texture coordinates.
    """
    return get_material_requires_texcoords(glTF, index)


def get_image_index(export_settings, uri):
    """
    Return the image index in the glTF array.
    """

    if export_settings['gltf_uri_data'] is None:
        return -1

    if uri in export_settings['gltf_uri_data']['uri']:
        return export_settings['gltf_uri_data']['uri'].index(uri)

    return -1


def get_texture_index_by_image(export_settings, glTF, bl_image):
    """
    Return the texture index in the glTF array by a given blender image.
    """

    if bl_image.filepath is None:
        return -1

    uri = get_image_exported_uri(export_settings, bl_image)

    if export_settings['gltf_uri_data'] is None:
        return -1


    if glTF.get('textures') is None:
        return -1

    image_uri = export_settings['gltf_uri_data']['uri']

    index = 0

    for texture in glTF['textures']:

        if 'source' in texture:
            current_image_uri = image_uri[texture['source']]
            if current_image_uri == uri:
                return index

        index += 1

    return -1

def get_texture_index(glTF, name):
    """
    Return the texture index in the glTF array.
    """
    if name is None:
        return -1

    if glTF.get('textures') is None:
        return -1

    index = 0
    for texture in glTF['textures']:
        if texture['name'] == name:
            return index

        index += 1

    return -1

def get_texture_index_by_texture(export_settings, glTF, bl_texture):
    """
    Return the texture index in the glTF array by a given texture. Safer than
    "get_texture_index_by_image" and "get_texture_index" in case of different
    textures with the same image or linked textures with the same name but with
    different images.
    """

    if (export_settings['gltf_uri_data'] is None or glTF.get('textures') is None
            or bl_texture is None):
        return -1

    bl_image = get_tex_image(bl_texture)
    if bl_image is None or bl_image.filepath is None:
        return -1

    uri = get_image_exported_uri(export_settings, bl_image)
    image_uri = export_settings['gltf_uri_data']['uri']
    tex_name = get_texture_name(bl_texture)

    index = 0
    for texture in glTF['textures']:
        if 'source' in texture and 'name' in texture:
            current_image_uri = image_uri[texture['source']]
            if current_image_uri == uri and texture['name'] == tex_name:
                return index

        index += 1

    return -1

def get_texture_index_node(export_settings, glTF, name, shader_node_group):
    """
    Return the texture index in the glTF array.
    """

    if shader_node_group is None:
        return -1

    if not isinstance(shader_node_group, bpy.types.ShaderNodeGroup):
        return -1

    if shader_node_group.inputs.get(name) is None:
        return -1

    if len(shader_node_group.inputs[name].links) == 0:
        return -1

    from_node = shader_node_group.inputs[name].links[0].from_node

    #

    if not isinstance(from_node, bpy.types.ShaderNodeTexImage):
        return -1

    if get_tex_image(from_node) is None or get_tex_image(from_node).size[0] == 0 or get_tex_image(from_node).size[1] == 0:
        return -1

    return get_texture_index_by_texture(export_settings, glTF, from_node)


def get_texcoord_index(glTF, name, shader_node_group):
    """
    Return the texture coordinate index, if assigend and used.
    """

    if shader_node_group is None:
        return 0

    if not isinstance(shader_node_group, bpy.types.ShaderNodeGroup):
        return 0

    if shader_node_group.inputs.get(name) is None:
        return 0

    if len(shader_node_group.inputs[name].links) == 0:
        return 0

    from_node = shader_node_group.inputs[name].links[0].from_node

    #

    if not isinstance(from_node, bpy.types.ShaderNodeTexImage):
        return 0

    #

    if len(from_node.inputs['Vector'].links) == 0:
        return 0

    input_node = from_node.inputs['Vector'].links[0].from_node

    if not isinstance(input_node, bpy.types.ShaderNodeUVMap):
        return 0

    if input_node.uv_map == '':
        return 0

    #

    # Try to gather map index.
    for blender_mesh in bpy.data.meshes:
        texCoordIndex = blender_mesh.uv_layers.find(input_node.uv_map)
        if texCoordIndex >= 0:
            return texCoordIndex

    return 0

def get_cycles_node_types():
    return [
        bpy.types.ShaderNodeAddShader,
        bpy.types.ShaderNodeAmbientOcclusion,
        bpy.types.ShaderNodeAttribute,
        bpy.types.ShaderNodeBackground,
        bpy.types.ShaderNodeBlackbody,
        bpy.types.ShaderNodeBsdfAnisotropic,
        bpy.types.ShaderNodeBsdfDiffuse,
        bpy.types.ShaderNodeBsdfGlass,
        bpy.types.ShaderNodeBsdfGlossy,
        bpy.types.ShaderNodeBsdfHair,
        bpy.types.ShaderNodeBsdfRefraction,
        bpy.types.ShaderNodeBsdfToon,
        bpy.types.ShaderNodeBsdfTranslucent,
        bpy.types.ShaderNodeBsdfTransparent,
        bpy.types.ShaderNodeBsdfVelvet,
        bpy.types.ShaderNodeBump,
        bpy.types.ShaderNodeCombineXYZ,
        bpy.types.ShaderNodeEmission,
        bpy.types.ShaderNodeHairInfo,
        bpy.types.ShaderNodeHoldout,
        bpy.types.ShaderNodeMixShader,
        bpy.types.ShaderNodeNewGeometry,
        bpy.types.ShaderNodeOutputLamp,
        bpy.types.ShaderNodeOutputLineStyle,
        bpy.types.ShaderNodeOutputMaterial,
        bpy.types.ShaderNodeOutputWorld,
        bpy.types.ShaderNodeScript,
        bpy.types.ShaderNodeSeparateXYZ,
        bpy.types.ShaderNodeSubsurfaceScattering,
        bpy.types.ShaderNodeTangent,
        bpy.types.ShaderNodeTexBrick,
        bpy.types.ShaderNodeTexChecker,
        bpy.types.ShaderNodeTexCoord,
        bpy.types.ShaderNodeTexEnvironment,
        bpy.types.ShaderNodeTexGradient,
        bpy.types.ShaderNodeTexImage,
        bpy.types.ShaderNodeTexMagic,
        bpy.types.ShaderNodeTexMusgrave,
        bpy.types.ShaderNodeTexNoise,
        bpy.types.ShaderNodeTexPointDensity,
        bpy.types.ShaderNodeTexSky,
        bpy.types.ShaderNodeTexVoronoi,
        bpy.types.ShaderNodeTexWave,
        bpy.types.ShaderNodeUVAlongStroke,
        bpy.types.ShaderNodeUVMap,
        bpy.types.ShaderNodeVolumeAbsorption,
        bpy.types.ShaderNodeVolumeScatter,
        bpy.types.ShaderNodeWavelength,
        bpy.types.ShaderNodeWireframe
    ]

def get_material_type(bl_material):
    """
    get blender material type: PBR, CYCLES, NODE, BASIC
    """

    if not bl_material.use_nodes or bl_material.node_tree == None:
        return 'BASIC'

    for bl_node in bl_material.node_tree.nodes:
        if (isinstance(bl_node, bpy.types.ShaderNodeGroup) and
                bl_node.node_tree.name.startswith('Verge3D PBR')):
            return 'PBR'

    # NOTE: temporary
    if bpy.app.version > (2,80,0):
        return 'CYCLES'

    for bl_node in bl_material.node_tree.nodes:
        if type(bl_node) in get_cycles_node_types():
            return 'CYCLES'

    return 'NODE'

def get_material_index(glTF, name):
    """
    Return the material index in the glTF array.
    """
    if name is None:
        return -1

    if glTF.get('materials') is None:
        return -1

    index = 0
    for material in glTF['materials']:
        if material['name'] == name:
            return index

        index += 1

    return -1


def getMeshIndex(glTF, idname):
    """
    Return the mesh index in the glTF array.
    """

    if glTF.get('meshes') is None:
        return -1

    index = 0
    for mesh in glTF['meshes']:
        if (isinstance(idname, int) and mesh.get('id') == idname) or mesh['name'] == idname:
            return index

        index += 1

    return -1


def get_skin_index(glTF, name, index_offset):
    """
    Return the skin index in the glTF array.
    """

    if glTF.get('skins') is None:
        return -1

    skeleton = get_node_index(glTF, name)

    index = 0
    for skin in glTF['skins']:
        if skin['skeleton'] == skeleton:
            return index + index_offset

        index += 1

    return -1


def get_camera_index(glTF, name):
    """
    Return the camera index in the glTF array.
    """

    if glTF.get('cameras') is None:
        return -1

    index = 0
    for camera in glTF['cameras']:
        if camera['name'] == name:
            return index

        index += 1

    return -1

def get_curve_index(glTF, name):
    """
    Return the curve index in the glTF array.
    """

    v3d_data = get_asset_extension(glTF, 'S8S_v3d_data')

    if v3d_data == None:
        return -1

    if v3d_data.get('curves') == None:
        return -1

    curves = v3d_data['curves']

    index = 0
    for curve in curves:
        if curve['name'] == name:
            return index

        index += 1

    return -1

def get_light_index(glTF, name):
    """
    Return the light index in the glTF array.
    """

    v3d_data = get_asset_extension(glTF, 'S8S_v3d_data')

    if v3d_data == None:
        return -1

    if v3d_data.get('lights') == None:
        return -1

    lights = v3d_data['lights']

    index = 0
    for light in lights:
        if light['name'] == name:
            return index

        index += 1

    return -1


def get_node_graph_index(glTF, name):
    """
    Return the node graph index in the glTF array.
    """

    v3d_data = get_asset_extension(glTF, 'S8S_v3d_data')

    if v3d_data == None:
        return -1

    if v3d_data.get('nodeGraphs') == None:
        return -1

    index = 0
    for graph in v3d_data['nodeGraphs']:
        if graph['name'] == name:
            return index

        index += 1

    return -1

def get_node_index(glTF, name):
    """
    Return the node index in the glTF array.
    """

    if glTF.get('nodes') is None:
        return -1

    index = 0
    for node in glTF['nodes']:
        if node['name'] == name:
            return index

        index += 1

    return -1


def get_scene_index(glTF, name):
    """
    Return the scene index in the glTF array.
    """

    if glTF.get('scenes') is None:
        return -1

    index = 0
    for scene in glTF['scenes']:
        if scene['name'] == name:
            return index

        index += 1

    return -1

def get_image_exported_uri(export_settings, bl_image):
    """
    Return exported URI for a blender image.
    """

    name, ext = os.path.splitext(bpy.path.basename(bl_image.filepath))

    uri_name = name if name != '' else 'v3d_exported_image_' + bl_image.name

    uri_ext = ''
    if (bl_image.file_format == 'JPEG'
            or bl_image.file_format == 'BMP'
            or bl_image.file_format == 'HDR'
            or bl_image.file_format == 'PNG'):
        if ext != '':
            uri_ext = ext
    else:
        uri_ext = '.png'

    uri_data = export_settings['gltf_uri_data']

    unique_uri = uri_name + uri_ext
    i = 0
    while unique_uri in uri_data['uri']:

        index = uri_data['uri'].index(unique_uri)
        if uri_data['bl_datablocks'][index] == bl_image:
            break

        i += 1
        unique_uri = uri_name + '_' + integer_to_bl_suffix(i) + uri_ext

    return unique_uri

def get_image_exported_mime_type(bl_image):

    if bl_image.file_format == 'JPEG':
        return 'image/jpeg'
    elif bl_image.file_format == 'BMP':
        return 'image/bmp'
    elif bl_image.file_format == 'HDR':
        return 'image/vnd.radiance'
    else:
        return 'image/png'

def get_name_in_brackets(data_path):
    """
    Return Blender node on a given Blender data path.
    """

    if data_path is None:
        return None

    index = data_path.find("[\"")
    if (index == -1):
        return None

    node_name = data_path[(index + 2):]

    index = node_name.find("\"")
    if (index == -1):
        return None

    return node_name[:(index)]

def get_anim_param_dim(fcurves, node_name):
    dim = 0

    for fcurve in fcurves:
        if get_name_in_brackets(fcurve.data_path) == node_name:
            dim = max(dim, fcurve.array_index+1)

    return dim

def get_anim_param(data_path):
    """
    return animated param in data path:
    nodes['name'].outputs[0].default_value -> default_value
    """

    index = data_path.rfind('.')

    if index == -1:
        return data_path

    return data_path[(index + 1):]


def get_scalar(default_value, init_value = 0.0):
    """
    Return scalar with a given default/fallback value.
    """

    return_value = init_value

    if default_value is None:
        return return_value

    return_value = default_value

    return return_value


def get_vec2(default_value, init_value = [0.0, 0.0]):
    """
    Return vec2 with a given default/fallback value.
    """

    return_value = init_value

    if default_value is None or len(default_value) < 2:
        return return_value

    index = 0
    for number in default_value:
        return_value[index] = number

        index += 1
        if index == 2:
            return return_value

    return return_value


def get_vec3(default_value, init_value = [0.0, 0.0, 0.0]):
    """
    Return vec3 with a given default/fallback value.
    """

    return_value = init_value

    if default_value is None or len(default_value) < 3:
        return return_value

    index = 0
    for number in default_value:
        return_value[index] = number

        index += 1
        if index == 3:
            return return_value

    return return_value


def get_vec4(default_value, init_value = [0.0, 0.0, 0.0, 1.0]):
    """
    Return vec4 with a given default/fallback value.
    """

    return_value = init_value

    if default_value is None or len(default_value) < 4:
        return return_value

    index = 0
    for number in default_value:
        return_value[index] = number

        index += 1
        if index == 4:
            return return_value

    return return_value


def get_index(list, name):
    """
    Return index of a glTF element by a given name.
    """

    if list is None or name is None:
        return -1

    index = 0
    for element in list:
        if element.get('name') is None:
            continue

        if element['name'] == name:
            return index

        index += 1

    return -1

def get_by_name(list, name):
    """
    Return element by a given name.
    """

    if list is None or name is None:
        return None

    for element in list:
        if element.get('name') is None:
            continue

        if element['name'] == name:
            return element

    return None


def get_asset_extension(glTF, extension):
    """
    Get top-level asset extension
    """

    if glTF.get('extensions') == None:
        return None

    return glTF['extensions'].get(extension)


def get_or_create_default_material_index(glTF):
    def_idx = get_material_index(glTF, DEFAULT_MAT_NAME)

    if def_idx == -1:
        if 'materials' not in glTF:
            glTF['materials'] = []

        if isCyclesRender(bpy.context):
            glTF['materials'].append(create_default_material_cycles())
        else:
            glTF['materials'].append(create_default_material_internal())

        def_idx = len(glTF['materials']) - 1

    return def_idx

def create_default_material_cycles():
    return {
        "emissiveFactor" : [
            0.0,
            0.0,
            0.0
        ],
        "extensions" : {
            "S8S_v3d_material_data" : {
                "nodeGraph" : {
                    "edges" : [
                        {
                            "fromNode" : 1,
                            "fromOutput" : 0,
                            "toInput" : 0,
                            "toNode" : 0
                        }
                    ],
                    "nodes" : [
                        {
                            "inputs" : [
                                [ 0, 0, 0, 0 ],
                                [ 0, 0, 0, 0 ],
                                0.0
                            ],
                            "is_active_output" : True,
                            "name" : "Material Output",
                            "outputs" : [],
                            "type" : "OUTPUT_MATERIAL"
                        },
                        {
                            "inputs" : [
                                [ 0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0 ],
                                0.0,
                                [ 0.0, 0.0, 0.0 ]
                            ],
                            "is_active_output" : False,
                            "name" : "Diffuse BSDF",
                            "outputs" : [
                                [ 0, 0, 0, 0 ]
                            ],
                            "type" : "BSDF_DIFFUSE"
                        }
                    ]
                },
                "useCastShadows" : False,
                "useShadows" : False
            }
        },
        "name" : DEFAULT_MAT_NAME
    }

def create_default_material_internal():
    return {
        "extensions" : {
            "S8S_v3d_material_data" : {
                "nodeGraph" : {
                    "edges" : [
                        {
                            "fromNode" : 1,
                            "fromOutput" : 0,
                            "toInput" : 0,
                            "toNode" : 0
                        },
                        {
                            "fromNode" : 1,
                            "fromOutput" : 1,
                            "toInput" : 1,
                            "toNode" : 0
                        }
                    ],
                    "nodes" : [
                        {
                            "inputs" : [
                                [ 1, 1, 1, 1 ],
                                1
                            ],
                            "is_active_output" : True,
                            "name" : "Output",
                            "outputs" : [],
                            "type" : "OUTPUT"
                        },
                        {
                            "inputs" : [
                                [ 0.800000011920929, 0.800000011920929, 0.800000011920929, 1 ],
                                [ 1.0, 1.0, 1.0, 1 ],
                                0.800000011920929,
                                [ 0, 0, 0 ],
                                [ 0, 0, 0, 0 ],
                                1.0,
                                0.0,
                                1.0,
                                0,
                                1.0,
                                0
                            ],
                            "invertNormal" : False,
                            "is_active_output" : False,
                            "materialName" : "Material",
                            "name" : "Material",
                            "outputs" : [
                                [ 0, 0, 0, 0 ],
                                0,
                                [ 0, 0, 0 ],
                                [ 0, 0, 0, 0 ],
                                [ 0, 0, 0, 0 ],
                                [ 0, 0, 0, 0 ]
                            ],
                            "specularHardness" : 50,
                            "specularIntensity" : 0.5,
                            "type" : "MATERIAL_EXT",
                            "useDiffuse" : True,
                            "useShadeless" : False,
                            "useSpecular" : True
                        }
                    ]
                },
                "useCastShadows" : False,
                "useShadows" : False
            }
        },
        "name" : DEFAULT_MAT_NAME
    }
