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

import bpy, mathutils, math

from ...outputs.luxcore_api import pyluxcore
from ...outputs.luxcore_api import ToValidLuxCoreName
from ...export import is_obj_visible
from ...export import ParamSet
from ...export import get_worldscale
from ...export import matrix_to_list
from ...export import get_expanded_file_name

from .utils import convert_param_to_luxcore_property


class LightExporter(object):
    def __init__(self, luxcore_exporter, blender_scene, blender_object):
        self.luxcore_exporter = luxcore_exporter
        self.blender_scene = blender_scene
        self.blender_object = blender_object

        self.properties = pyluxcore.Properties()
        self.luxcore_name = ''


    def convert(self, luxcore_scene):
        # Remove old properties
        self.properties = pyluxcore.Properties()
        
        self.__convert_light(luxcore_scene)

        return self.properties


    def __convert_light(self, luxcore_scene):
        # TODO: refactor this horrible... thing
        # TODO: find solution for awkward sunsky problem
        
        obj = self.blender_object
        
        hide_lamp = not is_obj_visible(self.blender_scene, obj)
        if hide_lamp:
            return
    
        light = obj.data
        luxcore_name = ToValidLuxCoreName(obj.name)
    
        light_params = ParamSet() \
            .add_float('gain', light.energy) \
            .add_float('importance', light.luxrender_lamp.importance)
    
        # Params from light sub-types
        light_params.update(getattr(light.luxrender_lamp, 'luxrender_lamp_%s' % light.type.lower()).get_paramset(obj))
    
        params_converted = []
        for rawParam in light_params:
            params_converted.append(convert_param_to_luxcore_property(rawParam))
    
        params_keyValue = {}
        for param in params_converted:
            params_keyValue[param[0]] = param[1]
    
        # Common light params
        lux_lamp = getattr(light.luxrender_lamp, 'luxrender_lamp_%s' % light.type.lower())
        energy = params_keyValue['gain'] if not hide_lamp else 0  # workaround for no lights render recovery
        importance = params_keyValue['importance']
    
        # Lightgroup
        lightgroup = getattr(light.luxrender_lamp, 'lightgroup')
        lightgroup_id = -1  # for luxcore RADIANCE_GROUP
    
        if lightgroup != '':
            lightgroup_enabled = self.blender_scene.luxrender_lightgroups.lightgroups[lightgroup].lg_enabled
            if lightgroup_enabled:
                energy *= self.blender_scene.luxrender_lightgroups.lightgroups[lightgroup].gain
    
                if lightgroup in self.luxcore_exporter.lightgroup_cache:
                    # lightgroup already has a luxcore id, use it
                    lightgroup_id = self.luxcore_exporter.lightgroup_cache[lightgroup]
                else:
                    # this is the first material to use this lightgroup, add an entry with a new id
                    lightgroup_id = len(self.luxcore_exporter.lightgroup_cache)
                    self.luxcore_exporter.lightgroup_cache[lightgroup] = lightgroup_id
            else:
                energy = 0  # use gain for muting to keep geometry exported
    
        # Don't set lightgroup for sun because it might be split into sun + sky
        if lightgroup_id != -1 and light.type != 'SUN' and not self.blender_scene.luxrender_lightgroups.ignore:
            self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.id', [lightgroup_id]))
    
        # Visibility settings for indirect rays (not for sun because it might be split into sun + sky,
        # and not for area light because it needs a different prefix (scene.materials.)
        if light.type != 'SUN' and not (light.type == 'AREA' and not light.luxrender_lamp.luxrender_lamp_laser.is_laser):
            self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.visibility.indirect.diffuse.enable',
                                                 light.luxrender_lamp.luxcore_lamp.visibility_indirect_diffuse_enable))
            self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.visibility.indirect.glossy.enable',
                                                 light.luxrender_lamp.luxcore_lamp.visibility_indirect_glossy_enable))
            self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.visibility.indirect.specular.enable',
                                                 light.luxrender_lamp.luxcore_lamp.visibility_indirect_specular_enable))
    
        gain_spectrum = [energy, energy, energy]  # luxcore gain is spectrum!
    
        # not for distant light,
        # not for area lamps (because these are meshlights and gain is controlled by material settings
        if getattr(lux_lamp, 'L_color') and not (
                        light.type == 'SUN' and getattr(lux_lamp, 'sunsky_type') != 'distant') and not (
                        light.type == 'AREA' and not light.luxrender_lamp.luxrender_lamp_laser.is_laser):
            iesfile = getattr(light.luxrender_lamp, 'iesname')
            iesfile, basename = get_expanded_file_name(light, iesfile)
            if iesfile != '':
                self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.iesfile', iesfile))
    
            # Workaround for lights without color, multiply gain with color here
            if (light.type == 'HEMI' and (not getattr(lux_lamp, 'infinite_map')
                                          or getattr(lux_lamp, 'hdri_multiply'))) or light.type == 'SPOT':
                colorRaw = getattr(lux_lamp, 'L_color') * energy
                gain_spectrum = [colorRaw[0], colorRaw[1], colorRaw[2]]
            else:
                colorRaw = getattr(lux_lamp, 'L_color')
                color = [colorRaw[0], colorRaw[1], colorRaw[2]]
                self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.color', color))
    
            self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.gain', gain_spectrum))
            self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.importance', importance))
    
        ####################################################################
        # Sun (includes sun, sky, distant)
        ####################################################################
        if light.type == 'SUN':
            invmatrix = obj.matrix_world.inverted()
            sundir = [invmatrix[2][0], invmatrix[2][1], invmatrix[2][2]]
            samples = params_keyValue['nsamples']
    
            sunsky_type = light.luxrender_lamp.luxrender_lamp_sun.sunsky_type
            legacy_sky = light.luxrender_lamp.luxrender_lamp_sun.legacy_sky
    
            if 'sun' in sunsky_type:
                name = luxcore_name + '_sun'
                if lightgroup_id != -1 and not self.blender_scene.luxrender_lightgroups.ignore:
                    self.properties.Set(pyluxcore.Property('scene.lights.' + name + '.id', [lightgroup_id]))
    
                turbidity = params_keyValue['turbidity']
    
                self.properties.Set(pyluxcore.Property('scene.lights.' + name + '.type', ['sun']))
                self.properties.Set(pyluxcore.Property('scene.lights.' + name + '.turbidity', [turbidity]))
                self.properties.Set(pyluxcore.Property('scene.lights.' + name + '.dir', sundir))
                self.properties.Set(pyluxcore.Property('scene.lights.' + name + '.gain', gain_spectrum))
                self.properties.Set(pyluxcore.Property('scene.lights.' + name + '.importance', importance))
                self.properties.Set(pyluxcore.Property('scene.lights.' + name + '.samples', [samples]))
    
                if 'relsize' in params_keyValue:
                    relsize = params_keyValue['relsize']
                    self.properties.Set(pyluxcore.Property('scene.lights.' + name + '.relsize', [relsize]))
    
                # Settings for indirect light visibility
                self.properties.Set(pyluxcore.Property('scene.lights.' + name + '.visibility.indirect.diffuse.enable',
                                                     light.luxrender_lamp.luxcore_lamp.visibility_indirect_diffuse_enable))
                self.properties.Set(pyluxcore.Property('scene.lights.' + name + '.visibility.indirect.glossy.enable',
                                                     light.luxrender_lamp.luxcore_lamp.visibility_indirect_glossy_enable))
                self.properties.Set(pyluxcore.Property('scene.lights.' + name + '.visibility.indirect.specular.enable',
                                                     light.luxrender_lamp.luxcore_lamp.visibility_indirect_specular_enable))
    
            if 'sky' in sunsky_type:
                name = luxcore_name + '_sky'
                if lightgroup_id != -1 and not self.blender_scene.luxrender_lightgroups.ignore:
                    self.properties.Set(pyluxcore.Property('scene.lights.' + name + '.id', [lightgroup_id]))
    
                turbidity = params_keyValue['turbidity']
                skyVersion = 'sky' if legacy_sky else 'sky2'
    
                self.properties.Set(pyluxcore.Property('scene.lights.' + name + '.type', [skyVersion]))
                self.properties.Set(pyluxcore.Property('scene.lights.' + name + '.turbidity', [turbidity]))
                self.properties.Set(pyluxcore.Property('scene.lights.' + name + '.dir', sundir))
                self.properties.Set(pyluxcore.Property('scene.lights.' + name + '.gain', gain_spectrum))
                self.properties.Set(pyluxcore.Property('scene.lights.' + name + '.importance', importance))
                self.properties.Set(pyluxcore.Property('scene.lights.' + name + '.samples', [samples]))
    
                # Settings for indirect light visibility
                self.properties.Set(pyluxcore.Property('scene.lights.' + name + '.visibility.indirect.diffuse.enable',
                                                     light.luxrender_lamp.luxcore_lamp.visibility_indirect_diffuse_enable))
                self.properties.Set(pyluxcore.Property('scene.lights.' + name + '.visibility.indirect.glossy.enable',
                                                     light.luxrender_lamp.luxcore_lamp.visibility_indirect_glossy_enable))
                self.properties.Set(pyluxcore.Property('scene.lights.' + name + '.visibility.indirect.specular.enable',
                                                     light.luxrender_lamp.luxcore_lamp.visibility_indirect_specular_enable))
    
            if sunsky_type == 'distant':
                if lightgroup_id != -1 and not self.blender_scene.luxrender_lightgroups.ignore:
                    self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.id', [lightgroup_id]))
    
                distant_dir = [-sundir[0], -sundir[1], -sundir[2]]
    
                self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.type', ['distant']))
                self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.direction', distant_dir))
    
                if 'theta' in params_keyValue:
                    theta = params_keyValue['theta']
                    self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.theta', [theta]))
    
                # Settings for indirect light visibility
                self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.visibility.indirect.diffuse.enable',
                                                     light.luxrender_lamp.luxcore_lamp.visibility_indirect_diffuse_enable))
                self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.visibility.indirect.glossy.enable',
                                                     light.luxrender_lamp.luxcore_lamp.visibility_indirect_glossy_enable))
                self.properties.Set(
                    pyluxcore.Property('scene.lights.' + luxcore_name + '.visibility.indirect.specular.enable',
                                       light.luxrender_lamp.luxcore_lamp.visibility_indirect_specular_enable))
    
        ####################################################################
        # Hemi (infinite)
        ####################################################################
        elif light.type == 'HEMI':
            infinite_map_path = getattr(lux_lamp, 'infinite_map')
            if infinite_map_path:
                infinite_map_path_abs, basename = get_expanded_file_name(light, infinite_map_path)
                self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.type', ['infinite']))
                self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.file', infinite_map_path_abs))
            else:
                self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.type', ['constantinfinite']))
    
            self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.gamma', getattr(lux_lamp, 'gamma')))
            hemi_fix = mathutils.Matrix.Scale(1.0, 4)  # create new scale matrix 4x4
            hemi_fix[0][0] = -1.0  # mirror the hdri_map
            transform = matrix_to_list(hemi_fix * obj.matrix_world.inverted(), apply_worldscale=True)
            self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.transformation', transform))
    
        ####################################################################
        # Point
        ####################################################################
        elif light.type == 'POINT':
            # if getattr(lux_lamp, 'usesphere'):
            # print('------------------------', getattr(lux_lamp, 'pointsize'))
            if iesfile:
                self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.type', ['mappoint']))
            else:
                self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.type', ['point']))
    
            if getattr(lux_lamp, 'flipz'):
                self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.flipz', lux_lamp.flipz))
    
            transform = matrix_to_list(obj.matrix_world, apply_worldscale=True)
            self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.transformation', transform))
            self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.position', [0.0, 0.0, 0.0]))
            self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.power', getattr(lux_lamp, 'power')))
            self.properties.Set(
                pyluxcore.Property('scene.lights.' + luxcore_name + '.efficency', getattr(lux_lamp, 'efficacy')))
    
        ####################################################################
        # Spot (includes projector)
        ####################################################################
        elif light.type == 'SPOT':
            coneangle = math.degrees(light.spot_size) * 0.5
            conedeltaangle = math.degrees(light.spot_size * 0.5 * light.spot_blend)
            if getattr(lux_lamp, 'projector'):
                projector_map_path = getattr(lux_lamp, 'mapname')
                projector_map_path_abs, basename = get_expanded_file_name(light, projector_map_path)
                self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.type', ['projection']))
                self.properties.Set(
                    pyluxcore.Property('scene.lights.' + luxcore_name + '.mapfile', projector_map_path_abs))
                self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.fov', coneangle * 2))
            else:
                self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.type', ['spot']))
    
            spot_fix = mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'Z')  # match to lux
            transform = matrix_to_list(obj.matrix_world * spot_fix, apply_worldscale=True)
            self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.transformation', transform))
            self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.position', [0.0, 0.0, 0.0]))
            self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.target', [0.0, 0.0, -1.0]))
    
            self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.coneangle', coneangle))
            self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.conedeltaangle', conedeltaangle))
            self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.power', getattr(lux_lamp, 'power')))
            self.properties.Set(
                pyluxcore.Property('scene.lights.' + luxcore_name + '.efficency', getattr(lux_lamp, 'efficacy')))
    
        ####################################################################
        # Area (includes laser)
        ####################################################################
        elif light.type == 'AREA':
            if light.luxrender_lamp.luxrender_lamp_laser.is_laser:
                # Laser lamp
                transform = matrix_to_list(obj.matrix_world, apply_worldscale=True)
                self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.transformation', transform))
                self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.position', [0.0, 0.0, 0.0]))
                self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.type', ['laser']))
                self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.target', [0.0, 0.0, -1.0]))
                self.properties.Set(pyluxcore.Property('scene.lights.' + luxcore_name + '.radius', [light.size]))
            else:
                # TODO: visibility for indirect rays
    
                # Area lamp workaround: create plane and add emitting material
                mat_name = luxcore_name + '_helper_mat'
                # TODO: match brightness with API 1.x
                # overwrite gain with a gain scaled by ws^2 to account for change in lamp area
                raw_color = light.luxrender_lamp.luxrender_lamp_area.L_color * energy * (
                    get_worldscale(as_scalematrix=False) ** 2)
                emission_color = [raw_color[0], raw_color[1], raw_color[2]]
    
                # light_params.add_float('gain', light.energy * lg_gain * (get_worldscale(as_scalematrix=False) ** 2))
    
                self.properties.Set(pyluxcore.Property('scene.materials.' + mat_name + '.type', ['matte']))
                self.properties.Set(pyluxcore.Property('scene.materials.' + mat_name + '.kd', [0.0, 0.0, 0.0]))
                self.properties.Set(pyluxcore.Property('scene.materials.' + mat_name + '.power',
                                                     [light.luxrender_lamp.luxrender_lamp_area.power]))
                self.properties.Set(pyluxcore.Property('scene.materials.' + mat_name + '.efficiency',
                                                     [light.luxrender_lamp.luxrender_lamp_area.efficacy]))
    
                translator_settings = self.blender_scene.luxcore_translatorsettings
                if not (translator_settings.override_materials and translator_settings.override_lights):
                    self.properties.Set(pyluxcore.Property('scene.materials.' + mat_name + '.emission', emission_color))
    
                # assign material to object
                self.properties.Set(pyluxcore.Property('scene.objects.' + luxcore_name + '.material', [mat_name]))
    
                # add mesh
                mesh_name = 'Mesh-' + luxcore_name
                if not luxcore_scene.IsMeshDefined(mesh_name):
                    vertices = [
                        (1, 1, 0),
                        (1, -1, 0),
                        (-1, -1, 0),
                        (-1, 1, 0)
                    ]
                    faces = [
                        (0, 1, 2),
                        (2, 3, 0)
                    ]
                    luxcore_scene.DefineMesh(mesh_name, vertices, faces, None, None, None, None)
                # assign mesh to object
                self.properties.Set(pyluxcore.Property('scene.objects.' + luxcore_name + '.ply', [mesh_name]))
    
                # copy transformation of area lamp object
                scale_matrix = mathutils.Matrix()
                scale_matrix[0][0] = light.size / 2.0 * obj.scale.x
                scale_matrix[1][1] = light.size_y / 2.0 if light.shape == 'RECTANGLE' else light.size / 2.0
                scale_matrix[1][1] *= obj.scale.y
                rotation_matrix = obj.rotation_euler.to_matrix()
                rotation_matrix.resize_4x4()
                transform_matrix = mathutils.Matrix()
                transform_matrix[0][3] = obj.location.x
                transform_matrix[1][3] = obj.location.y
                transform_matrix[2][3] = obj.location.z
    
                transform = matrix_to_list(transform_matrix * rotation_matrix * scale_matrix, apply_worldscale=True)
                self.properties.Set(pyluxcore.Property('scene.objects.' + luxcore_name + '.transformation', transform))
    
        else:
            raise Exception('Unknown lighttype ' + light.type + ' for light: ' + obj.name)