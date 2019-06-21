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

import struct
import zlib

from .gltf2_debug import *
from .gltf2_get import *
from .import utils

#
# Globals
#

WEBGL_FILTERS = {
    'NEAREST'                : 9728,
    'LINEAR'                 : 9729,
    'NEAREST_MIPMAP_NEAREST' : 9984,
    'LINEAR_MIPMAP_NEAREST'  : 9985,
    'NEAREST_MIPMAP_LINEAR'  : 9986,
    'LINEAR_MIPMAP_LINEAR'   : 9987
}

WEBGL_WRAPPINGS = {
    'CLAMP_TO_EDGE'   : 33071,
    'MIRRORED_REPEAT' : 33648,
    'REPEAT'          : 10497
}

WEBGL_BLEND_EQUATIONS = {
    'FUNC_ADD' : 32774,
    'FUNC_SUBTRACT' : 32778,
    'FUNC_REVERSE_SUBTRACT' : 32779
}

WEBGL_BLEND_FUNCS = {
    'ZERO' : 0,
    'ONE' : 1,
    'SRC_COLOR' : 768,
    'ONE_MINUS_SRC_COLOR' : 769,
    'SRC_ALPHA' : 770,
    'ONE_MINUS_SRC_ALPHA' : 771,
    'DST_ALPHA' : 772,
    'ONE_MINUS_DST_ALPHA' : 773,
    'DST_COLOR' : 774,
    'ONE_MINUS_DST_COLOR' : 775,
    'SRC_ALPHA_SATURATE' : 776,

    # the followings are not supported by the engine yet
    # 'CONSTANT_COLOR' : 32769,
    # 'ONE_MINUS_CONSTANT_COLOR' : 32770,
    # 'CONSTANT_ALPHA' : 32771,
    # 'ONE_MINUS_CONSTANT_ALPHA' : 32772
}

#
# Functions
#

def createAssetExtension(operator, context, export_settings, glTF, extension):
    """
    Create and return top-level asset extension
    """

    createExtensionsUsed(operator, context, export_settings, glTF, extension)

    if glTF.get('extensions') == None:
        glTF['extensions'] = {}

    extensions = glTF['extensions']

    if extensions.get(extension) == None:
        extensions[extension] = {}

    return extensions[extension]

def createExtensionsUsed(operator, context, export_settings, glTF, extension):
    """
    Creates and assigns the 'extensionsUsed' property.
    """

    if glTF.get('extensionsUsed') is None:
        glTF['extensionsUsed'] = []

    extensionsUsed = glTF['extensionsUsed']

    if extension not in extensionsUsed:
        extensionsUsed.append(extension)


def createExtensionsRequired(operator, context, export_settings, glTF, extension):
    """
    Creates and assigns the 'extensionsRequired' property.
    NOTE: unused, reducees asset compatibility
    """

    if glTF.get('extensionsRequired') is None:
        glTF['extensionsRequired'] = []

    extensionsRequired = glTF['extensionsRequired']

    if extension not in extensionsRequired:
        extensionsRequired.append(extension)


def create_sampler(operator, context, export_settings, glTF, magFilter, wrap):
    """
    Creates and appends a texture sampler with the given parameters.
    """

    if glTF.get('samplers') is None:
        glTF['samplers'] = []

    samplers = glTF['samplers']

    if len(samplers) == 0:
        sampler = {}
        samplers.append(sampler)

    if magFilter == WEBGL_FILTERS['LINEAR'] and wrap == WEBGL_WRAPPINGS['REPEAT']:
        return 0

    index = 0

    for currentSampler in samplers:
        if currentSampler.get('magFilter') is None or currentSampler.get('wrapS') is None:
            index += 1
            continue

        if currentSampler['magFilter'] == magFilter and currentSampler['wrapS'] == wrap:
            return index


    minFilter = WEBGL_FILTERS['LINEAR_MIPMAP_LINEAR']

    if magFilter == WEBGL_FILTERS['NEAREST']:
        minFilter = WEBGL_FILTERS['NEAREST_MIPMAP_NEAREST']

    sampler = {
        'magFilter' : magFilter,
        'minFilter' : minFilter,
        'wrapS' : wrap,
        'wrapT' : wrap
    }

    samplers.append(sampler)

    return len(samplers) - 1


def create_bufferView(operator,
                  context,
                  export_settings,
                  glTF,
                  data_buffer, target, alignment):
    """
    Creates and appends a bufferView with the given parameters.
    """

    if data_buffer is None:
        return -1

    gltf_target_number = [ 34962, 34963 ]
    gltf_target_enums = [ "ARRAY_BUFFER", "ELEMENT_ARRAY_BUFFER" ]

    target_number = 0
    if target in gltf_target_enums:
        target_number = gltf_target_number[gltf_target_enums.index(target)]

    #

    if glTF.get('bufferViews') is None:
        glTF['bufferViews'] = []

    bufferViews = glTF['bufferViews']

    #

    bufferView = {}

    if target_number != 0:
        bufferView['target'] = target_number

    bufferView['byteLength'] = len(data_buffer)

    binary = export_settings['gltf_binary']

    #

    binary_length = len(binary)

    remainder = 0

    if alignment > 0:
        remainder = binary_length % alignment

    if remainder > 0:
        padding_byte = struct.pack('<1b', 0)
        for i in range(0, alignment - remainder):
            binary.extend(padding_byte)

    #

    bufferView['byteOffset'] = len(binary)
    binary.extend(data_buffer)

    # Only have one buffer.
    bufferView['buffer'] = 0

    #

    bufferViews.append(bufferView)

    return len(bufferViews) - 1


def create_accessor(operator,
                  context,
                  export_settings,
                  glTF,
                  data, componentType, count, type, target):
    """
    Creates and appends an accessor with the given parameters.
    """

    if data is None:
        printLog('ERROR', 'No data')
        return -1

    gltf_convert_type = [ "b", "B", "h", "H", "I", "f" ]
    gltf_enumNames = [ "BYTE", "UNSIGNED_BYTE", "SHORT", "UNSIGNED_SHORT", "UNSIGNED_INT", "FLOAT" ]
    gltf_convert_type_size = [ 1, 1, 2, 2, 4, 4 ]

    if componentType not in gltf_enumNames:
        printLog('ERROR', 'Invalid componentType ' + componentType)
        return -1

    componentTypeInteger = [ 5120, 5121, 5122, 5123, 5125, 5126 ][gltf_enumNames.index(componentType)]

    convert_type = gltf_convert_type[gltf_enumNames.index(componentType)]
    convert_type_size = gltf_convert_type_size[gltf_enumNames.index(componentType)]

    if count < 1:
        printLog('ERROR', 'Invalid count ' + str(count))
        return -1

    gltf_type_count = [ 1, 2, 3, 4, 4, 9, 16 ]
    gltf_type = [ "SCALAR", "VEC2", "VEC3", "VEC4", "MAT2", "MAT3", "MAT4" ]

    if type not in gltf_type:
        printLog('ERROR', 'Invalid tyoe ' + type)
        return -1

    type_count = gltf_type_count[gltf_type.index(type)]

    #

    if glTF.get('accessors') is None:
        glTF['accessors'] = []

    accessors = glTF['accessors']

    #

    accessor = {
        'componentType' : componentTypeInteger,
        'count' : count,
        'type' : type
    }

    #

    minimum = []
    maximum = []

    for component in range(0, count):
        for component_index in range(0, type_count):
            element = data[component * type_count + component_index]

            if component == 0:
                minimum.append(element)
                maximum.append(element)
            else:
                minimum[component_index] = min(minimum[component_index], element)
                maximum[component_index] = max(maximum[component_index], element)

    accessor['min'] = minimum
    accessor['max'] = maximum

    #

    convert_type = '<' + str(count * type_count) + convert_type

    data_buffer = struct.pack(convert_type, *data)

    bufferView = create_bufferView(operator, context, export_settings, glTF, data_buffer, target, convert_type_size)

    if bufferView < 0:
        printLog('ERROR', 'Invalid buffer view')
        return -1

    accessor['bufferView'] = bufferView

    #

    accessors.append(accessor)

    return len(accessors) - 1


# NOTE: unused
def create_png_data(blender_image):
    """
    Creates a PNG byte array from a given Blender image.
    """
    if blender_image is None:
        return None

    width = blender_image.size[0]
    height = blender_image.size[1]

    buf = bytearray([int(channel * 255.0) for channel in blender_image.pixels])

    #
    # Taken from 'blender-thumbnailer.py' in Blender.
    #

    # reverse the vertical line order and add null bytes at the start
    width_byte_4 = width * 4
    raw_data = b"".join(b'\x00' + buf[span:span + width_byte_4] for span in range((height - 1) * width * 4, -1, - width_byte_4))

    def png_pack(png_tag, data):
        chunk_head = png_tag + data
        return struct.pack("!I", len(data)) + chunk_head + struct.pack("!I", 0xFFFFFFFF & zlib.crc32(chunk_head))

    return b"".join([
        b'\x89PNG\r\n\x1a\n',
        png_pack(b'IHDR', struct.pack("!2I5B", width, height, 8, 6, 0, 0, 0)),
        png_pack(b'IDAT', zlib.compress(raw_data, 9)),
        png_pack(b'IEND', b'')])


def create_custom_property(blender_element):
    """
    Filters and creates a custom property, which is stored in the glTF extra field.
    """
    if not blender_element:
        return None

    props = {}

    # Custom properties, which are in most cases present and should not be exported.
    black_list = ['cycles', 'cycles_visibility', 'cycles_curves', '_RNA_UI', 'v3d']

    count = 0
    for custom_property in blender_element.keys():
        if custom_property in black_list:
            continue

        value = blender_element[custom_property]

        add_value = False

        if isinstance(value, str):
            add_value = True

        if isinstance(value, (int, float)):
            add_value = True

        if hasattr(value, "to_list"):
            value = value.to_list()
            add_value = True

        if add_value:
            props[custom_property] = value
            count += 1

    if count == 0:
        return None

    return props

def create_anim_channel(glTF, bl_object, sampler_name, path, node_name, samplers, channels):
    channel = {}

    channel['sampler'] = get_index(samplers, sampler_name)

    target = {}

    target['path'] = path
    target['node'] = get_node_index(glTF, node_name)

    channel['target'] = target

    # to resolve default animation params
    channel['bl_object'] = bl_object

    channels.append(channel)

    return channel

def create_blend_mode(bl_mat):

    if bpy.app.version < (2,80,0):
        return None

    if not utils.material_is_blend(bl_mat):
        return None

    blend_mode = {
        'blendEquation': WEBGL_BLEND_EQUATIONS['FUNC_ADD']
    }

    if bl_mat.blend_method == 'ADD':
        blend_mode['srcRGB'] = WEBGL_BLEND_FUNCS['ONE']
        blend_mode['dstRGB'] = WEBGL_BLEND_FUNCS['ONE']
    elif bl_mat.blend_method == 'BLEND':
        blend_mode['srcRGB'] = WEBGL_BLEND_FUNCS['ONE']
        blend_mode['dstRGB'] = WEBGL_BLEND_FUNCS['ONE_MINUS_SRC_ALPHA']
    elif bl_mat.blend_method == 'MULTIPLY':
        blend_mode['srcRGB'] = WEBGL_BLEND_FUNCS['DST_COLOR']
        blend_mode['dstRGB'] = WEBGL_BLEND_FUNCS['ONE_MINUS_SRC_ALPHA']

    return blend_mode
