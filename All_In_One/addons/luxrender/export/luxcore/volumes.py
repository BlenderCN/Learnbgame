# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
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
from ...outputs.luxcore_api import ToValidLuxCoreName

from .utils import convert_texture_channel, generate_volume_name


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

        self.__convert_volume()

        return self.properties


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
            if volume.type == 'clear':
                if volume.absorption_usecolortexture:
                    abs_col = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, volume, 'absorption', 'color')
                else:
                    abs_col = [volume.absorption_color.r, volume.absorption_color.g, volume.absorption_color.b]
                    absorption_at_depth_scaled(abs_col)
            else:
                if volume.sigma_a_usecolortexture:
                    abs_col = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, volume, 'sigma_a', 'color')
                else:
                    abs_col = [volume.sigma_a_color.r, volume.sigma_a_color.g, volume.sigma_a_color.b]
                    absorption_at_depth_scaled(abs_col)
    
            self.properties.Set(pyluxcore.Property(prefix + '.absorption', abs_col))
            self.properties.Set(pyluxcore.Property(prefix + '.type', [volume.type]))
            self.properties.Set(pyluxcore.Property(prefix + '.ior', ior_val))
            self.properties.Set(pyluxcore.Property(prefix + '.priority', volume.priority))
    
            if volume.type in ['homogeneous', 'heterogeneous']:
                # Scattering color
                if volume.sigma_s_usecolortexture:
                    s_source = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, volume, 'sigma_s', 'color')
    
                    if volume.scattering_scale != 1.0:
                        s_source = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, volume, 'sigma_s', 'color')
    
                        self.properties.Set(pyluxcore.Property('scene.textures.' + self.luxcore_name + '_scatterscaling.type', ['scale']))
                        self.properties.Set(pyluxcore.Property('scene.textures.' + self.luxcore_name + '_scatterscaling.texture1',
                                                             volume.scattering_scale))
                        self.properties.Set(
                            pyluxcore.Property('scene.textures.' + self.luxcore_name + '_scatterscaling.texture2', s_source))
                        s_col = self.luxcore_name + '_scatterscaling'
                    else:
                        s_col = s_source
                else:
                    s_col = [volume.sigma_s_color.r * volume.scattering_scale,
                             volume.sigma_s_color.g * volume.scattering_scale,
                             volume.sigma_s_color.b * volume.scattering_scale]
    
                self.properties.Set(pyluxcore.Property(prefix + '.scattering', s_col))
                self.properties.Set(pyluxcore.Property(prefix + '.asymmetry', list(volume.g)))
                self.properties.Set(pyluxcore.Property(prefix + '.multiscattering', [volume.multiscattering]))
    
            if volume.type == 'heterogenous':
                self.properties.Set(pyluxcore.Property(prefix + '.steps.size', volume.stepsize))
        except Exception as err:
            print('Volume export failed, skipping volume: %s\n%s' % (volume.name, err))
            import traceback
    
            traceback.print_exc()
    
            # define a clear volume instead of actual volume so LuxCore will still start to render
            self.properties.Set(pyluxcore.Property(prefix + '.type', ['clear']))