# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Simon Wendsche
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

import math

from ...outputs.luxcore_api import pyluxcore
from ...properties import find_node_in_volume

from .utils import convert_texture_channel, generate_volume_name, log_exception


class VolumeExporter(object):
    def __init__(self, luxcore_exporter, blender_scene, volume):
        self.luxcore_exporter = luxcore_exporter
        self.blender_scene = blender_scene
        self.volume = volume

        self.properties = pyluxcore.Properties()
        self.luxcore_name = ''


    def convert(self):
        # Remove old properties
        self.properties = pyluxcore.Properties()

        if self.volume.nodetree:
            self.__convert_node_volume()
        else:
            self.__convert_volume()

        return self.properties


    def __convert_node_volume(self):
        self.__generate_volume_name(self.volume.name)

        output_node = find_node_in_volume(self.volume, 'pbrtv3_volume_output_node')

        if output_node is None:
            self.__export_fallback_volume()
            return

        try:
            self.luxcore_name = output_node.export_luxcore(self.volume, self.properties, self.blender_scene)
        except Exception as err:
            message = 'Node volume export failed, skipping volume: %s\n%s' % (self.volume.name, err)
            log_exception(self.luxcore_exporter, message)
            self.__export_fallback_volume()


    def __export_fallback_volume(self):
        # Black clear volume
        self.properties.Set(pyluxcore.Property('scene.volumes.' + self.luxcore_name + '.type', 'clear'))
        self.properties.Set(pyluxcore.Property('scene.volumes.' + self.luxcore_name + '.absorption', [100, 100, 100]))


    def __generate_volume_name(self, name):
        # materials and volumes must not have the same names
        self.luxcore_name = generate_volume_name(name)

    
    def __convert_volume(self):
        volume = self.volume
        self.__generate_volume_name(volume.name)
        prefix = 'scene.volumes.' + self.luxcore_name
    
        try:
            def absorption_at_depth_scaled(abs_col):
                for i in range(len(abs_col)):
                    v = float(abs_col[i])
                    depth = volume.depth
                    scale = volume.absorption_scale
                    abs_col[i] = (-math.log(max([v, 1e-30])) / depth) * scale * (v == 1.0 and -1 or 1)
    
            print('Converting volume: %s' % volume.name)
    
            # IOR Fresnel
            if volume.fresnel_usefresneltexture:
                ior_val = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, volume, 'fresnel', 'fresnel')
            else:
                ior_val = volume.fresnel_fresnelvalue
    
            # Absorption
            attribute = 'absorption' if volume.type == 'clear' else 'sigma_a'
            absorption_color = getattr(volume, attribute + '_color')
            is_textured = getattr(volume, attribute + '_usecolortexture')

            if is_textured:
                abs_col = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, volume, attribute, 'color')

                if volume.absorption_scale != 1.0:
                    scale_name = self.luxcore_name + '_absorptionscaling'
                    self.properties.Set(pyluxcore.Property('scene.textures.' + scale_name + '.type', 'scale'))
                    self.properties.Set(pyluxcore.Property('scene.textures.' + scale_name + '.texture1', volume.absorption_scale))
                    self.properties.Set(pyluxcore.Property('scene.textures.' + scale_name + '.texture2', abs_col))
                    abs_col = scale_name
            else:
                abs_col = list(absorption_color)
                absorption_at_depth_scaled(abs_col)

            self.properties.Set(pyluxcore.Property(prefix + '.absorption', abs_col))
            self.properties.Set(pyluxcore.Property(prefix + '.type', volume.type))
            self.properties.Set(pyluxcore.Property(prefix + '.ior', ior_val))
            self.properties.Set(pyluxcore.Property(prefix + '.priority', volume.priority))

            # Light emission
            if volume.use_emission:
                emission_color = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, volume, 'emission', 'color')

                if volume.emission_usecolortexture:
                    if volume.gain != 1.0:
                        # Use a scale texture to multiple the textured emission with the gain
                        scale_name = self.luxcore_name + '_emissionscale'
                        self.properties.Set(pyluxcore.Property('scene.textures.' + scale_name + '.type', 'scale'))
                        self.properties.Set(pyluxcore.Property('scene.textures.' + scale_name + '.texture1', emission_color))
                        self.properties.Set(pyluxcore.Property('scene.textures.' + scale_name + '.texture2', volume.gain))
                        emission_color = scale_name
                else:
                    # Emission is not textured, just multiply r,g,b with the gain
                    emission_color[:] = [i * volume.gain for i in emission_color]

                self.properties.Set(pyluxcore.Property(prefix + '.emission', emission_color))

            if volume.type in ['homogeneous', 'heterogeneous']:
                # Scattering color
                if volume.sigma_s_usecolortexture:
                    scattering_col = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, volume, 'sigma_s', 'color')
    
                    if volume.scattering_scale != 1.0:
                        self.properties.Set(pyluxcore.Property('scene.textures.' + self.luxcore_name + '_scatterscaling.type', 'scale'))
                        self.properties.Set(pyluxcore.Property('scene.textures.' + self.luxcore_name + '_scatterscaling.texture1',
                                                             volume.scattering_scale))
                        self.properties.Set(pyluxcore.Property('scene.textures.' + self.luxcore_name + '_scatterscaling.texture2', scattering_col))
                        s_col = self.luxcore_name + '_scatterscaling'
                    else:
                        s_col = scattering_col
                else:
                    s_col = [volume.sigma_s_color.r * volume.scattering_scale,
                             volume.sigma_s_color.g * volume.scattering_scale,
                             volume.sigma_s_color.b * volume.scattering_scale]
    
                self.properties.Set(pyluxcore.Property(prefix + '.scattering', s_col))
                self.properties.Set(pyluxcore.Property(prefix + '.asymmetry', list(volume.g)))
                self.properties.Set(pyluxcore.Property(prefix + '.multiscattering', [volume.multiscattering]))
    
            if volume.type == 'heterogeneous':
                self.properties.Set(pyluxcore.Property(prefix + '.steps.size', volume.stepsize))
        except Exception as err:
            message = 'Volume export failed, skipping volume: %s\n%s' % (volume.name, err)
            log_exception(self.luxcore_exporter, message)
            # define a clear volume instead of actual volume so PBRTv3Core will still start to render
            self.properties.Set(pyluxcore.Property(prefix + '.type', 'clear'))