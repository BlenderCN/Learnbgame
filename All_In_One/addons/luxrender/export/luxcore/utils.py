# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# David Bucciarelli, Jens Verwiebe, Tom Bech, Simon Wendsche
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
#

from  math import pi

from ...outputs.luxcore_api import pyluxcore
from ...outputs.luxcore_api import ToValidLuxCoreName
from ...export.materials import get_texture_from_scene


def convert_texture_channel(luxcore_exporter, properties, element_name, textured_element, channel, type):
    """
    :param luxcore_exporter: the luxcore_exporter instance of the calling texture/volume/material exporter
    :param properties: pyluxcore.Properties
    :param element_name: name of the luxrender material/volume/texture
    :param textured_element: luxrender material, volume, texture or anything else with attributes that can be textured
    :param channel: name of the textured attribute, e.g. "Kd", "Ks" etc.
    :param type: "color" or "float"
    :return: name of the created texture or raw value if the channel is untextured
    """
    if type == 'color':
        value = list(getattr(textured_element, '%s_color' % channel))
    else:
        value = getattr(textured_element, '%s_%svalue' % (channel, type))

    if getattr(textured_element, '%s_use%stexture' % (channel, type)):
        # The material attribute is textured, export the texture
        texture_name = getattr(textured_element, '%s_%stexturename' % (channel, type))

        if not texture_name:
            # No texture is selected for the channel
            return value

        texture = get_texture_from_scene(luxcore_exporter.blender_scene, texture_name)

        if texture is not None:
            luxcore_exporter.convert_texture(texture)
            texture_exporter = luxcore_exporter.texture_cache[texture]

            is_multiplied = getattr(textured_element, '%s_multiply%s' % (channel, type))

            if is_multiplied:
                scale_tex_name = element_name + channel + type + texture_exporter.luxcore_name
                create_scale_texture(properties, texture_exporter.luxcore_name, scale_tex_name, value)
                return scale_tex_name
            else:
                return texture_exporter.luxcore_name
    else:
        # The material attribute is not textured, return base color/float value
        return value

    raise Exception(
        'Unknown texture in channel' + channel + ' for material/volume/texture ' + textured_element.type)


def create_scale_texture(properties, base_texture_name, scale_texture_name, multiplier):
    properties.Set(pyluxcore.Property('scene.textures.' + scale_texture_name + '.type', 'scale'))
    properties.Set(pyluxcore.Property('scene.textures.' + scale_texture_name + '.texture1', base_texture_name))
    properties.Set(pyluxcore.Property('scene.textures.' + scale_texture_name + '.texture2', multiplier))


def convert_param_to_luxcore_property(param):
    """
    Convert Luxrender parameters of the form
    ['float gain', 1.0]
    to LuxCore property format

    Returns list of parsed values without type specifier
    e.g. ['gain', 1.0]
    """

    parsed = param[0].split(' ')
    parsed.pop(0)

    return [parsed[0], param[1]]


def calc_shutter(blender_scene, lux_camera_settings):
    fps = blender_scene.render.fps / blender_scene.render.fps_base

    if lux_camera_settings.exposure_mode == 'normalised':
        shutter_open = lux_camera_settings.exposure_start_norm / fps
        shutter_close = lux_camera_settings.exposure_end_norm / fps
    elif lux_camera_settings.exposure_mode == 'absolute':
        shutter_open = lux_camera_settings.exposure_start_abs
        shutter_close = lux_camera_settings.exposure_end_abs
    elif lux_camera_settings.exposure_mode == 'degrees':
        shutter_open = lux_camera_settings.exposure_degrees_start / (fps * 2 * pi)
        shutter_close = lux_camera_settings.exposure_degrees_end / (fps * 2 * pi)
    else:
        raise Exception('exposure mode "%s" not supported' % lux_camera_settings.exposure_mode)

    return shutter_open, shutter_close


def generate_volume_name(name):
    return ToValidLuxCoreName(name + '_vol')