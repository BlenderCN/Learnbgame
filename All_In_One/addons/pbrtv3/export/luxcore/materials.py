# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
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

import bpy, os

from ...outputs.luxcore_api import pyluxcore
from ...outputs.luxcore_api import ToValidPBRTv3CoreName
from ...export.materials import get_texture_from_scene
from ...export import get_expanded_file_name
from ...properties import find_node

from .utils import convert_texture_channel, get_elem_key, is_lightgroup_opencl_compatible, log_exception
from .textures import TextureExporter


DEFAULT_MATTE = 'DEFAULT_MATTE'
DEFAULT_NULL = 'DEFAULT_NULL'


class MaterialExporter(object):
    def __init__(self, luxcore_exporter, blender_scene, material):
        self.luxcore_exporter = luxcore_exporter
        self.blender_scene = blender_scene
        self.material = material

        self.properties = pyluxcore.Properties()
        self.luxcore_name = ''


    def convert(self):
        # Remove old properties
        self.properties = pyluxcore.Properties()

        if self.material is None:
            self.__convert_default_matte()
        elif self.material.pbrtv3_material.nodetree:
            self.__convert_node_material()
        else:
            self.__convert_material()

        return self.properties


    def __convert_node_material(self):
        # Clay render handling
        if self.blender_scene.luxcore_translatorsettings.override_materials:
            self.__convert_default_matte()
            return

        self.__generate_material_name(self.material.name)

        output_node = find_node(self.material, 'pbrtv3_material_output_node')

        if output_node is None:
            self.__convert_default_matte()

        try:
            output_node.export_luxcore(self.material, self.properties, self.blender_scene, self.luxcore_exporter, self.luxcore_name)

            prefix = 'scene.materials.' + self.luxcore_name
            self.__set_material_volumes(prefix, output_node.interior_volume, output_node.exterior_volume)

            # PBRTv3Core specific material settings
            lc_mat = self.material.luxcore_material

            if lc_mat.id != -1 and not self.luxcore_exporter.is_viewport_render:
                self.properties.Set(pyluxcore.Property(prefix + '.id', [lc_mat.id]))
                if lc_mat.create_MATERIAL_ID_MASK and self.blender_scene.pbrtv3_channels.enable_aovs:
                    self.luxcore_exporter.config_exporter.convert_channel('MATERIAL_ID_MASK', lc_mat.id)
                if lc_mat.create_BY_MATERIAL_ID and self.blender_scene.pbrtv3_channels.enable_aovs:
                    self.luxcore_exporter.config_exporter.convert_channel('BY_MATERIAL_ID', lc_mat.id)
        except Exception as err:
            message = 'Node material export failed, skipping material: %s\n%s' % (self.material.name, err)
            log_exception(self.luxcore_exporter, message)
            self.__convert_default_matte()


    def __generate_material_name(self, name):
        if self.material.library:
            name += '_' + self.material.library.name

        # materials and volumes must not have the same names
        self.luxcore_name = ToValidPBRTv3CoreName(name + '_mat')


    def __convert_default_matte(self):
        if self.luxcore_name == '':
            self.luxcore_name = DEFAULT_MATTE

        self.properties.Set(pyluxcore.Property('scene.materials.' + self.luxcore_name + '.type', 'matte'))
        self.properties.Set(pyluxcore.Property('scene.materials.' + self.luxcore_name + '.kd', [0.6, 0.6, 0.6]))


    def __convert_default_null(self):
        self.properties.Set(pyluxcore.Property('scene.materials.' + DEFAULT_NULL + '.type', 'null'))


    def __set_material_volumes(self, prefix, interior, exterior):
        # This code checks if the volumes are set correctly so rendering does not fail when volumes are missing
        # from the scene. It is assumed that all volumes are already exported prior to material export.
        vol_cache = self.luxcore_exporter.volume_cache
        scene_volumes = {vol_exporter.volume.name: vol_exporter.luxcore_name for vol_exporter in vol_cache.values()}

        default_interior = self.blender_scene.pbrtv3_world.default_interior_volume
        default_exterior = self.blender_scene.pbrtv3_world.default_exterior_volume

        if interior in scene_volumes:
            self.properties.Set(pyluxcore.Property(prefix + '.volume.interior', scene_volumes[interior]))
        elif default_interior in scene_volumes:
            self.properties.Set(pyluxcore.Property(prefix + '.volume.interior', scene_volumes[default_interior]))

        if exterior in scene_volumes:
            self.properties.Set(pyluxcore.Property(prefix + '.volume.exterior', scene_volumes[exterior]))
        elif default_exterior in scene_volumes:
            self.properties.Set(pyluxcore.Property(prefix + '.volume.exterior', scene_volumes[default_exterior]))


    def __convert_material(self):
        try:
            material = self.material

            print('Converting material: %s' % material.name)

            self.__generate_material_name(material.name)

            lux_mat_type = material.pbrtv3_material.type
            lux_mat = getattr(material.pbrtv3_material, 'pbrtv3_mat_' + lux_mat_type)
            prefix = 'scene.materials.' + self.luxcore_name

            # Material override (clay render)
            translator_settings = self.blender_scene.luxcore_translatorsettings
            if translator_settings.override_materials:
                if material.pbrtv3_emission.use_emission:
                    if translator_settings.override_lights:
                        self.__convert_default_matte()
                        return
                elif lux_mat_type != 'mix':
                    if 'glass' in lux_mat_type:
                        if translator_settings.override_glass:
                            self.__convert_default_matte()
                            return
                    elif lux_mat_type == 'null':
                        if translator_settings.override_null:
                            self.__convert_default_matte()
                            return
                    else:
                        # all materials that are not glass, lights or null
                        self.__convert_default_matte()
                        return

            # ###################################################################
            # Matte and Roughmatte
            ####################################################################
            if lux_mat_type == 'matte':
                sigma = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'sigma', 'float')

                if sigma[0] == 0:
                    self.properties.Set(pyluxcore.Property(prefix + '.type', ['matte']))
                    self.properties.Set(pyluxcore.Property(prefix + '.kd', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Kd', 'color')))
                else:
                    self.properties.Set(pyluxcore.Property(prefix + '.type', ['roughmatte']))
                    self.properties.Set(pyluxcore.Property(prefix + '.kd', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Kd', 'color')))
                    self.properties.Set(pyluxcore.Property(prefix + '.sigma', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'sigma', 'float')))

            ####################################################################
            # Mattetranslucent
            ####################################################################
            elif lux_mat_type == 'mattetranslucent':
                self.properties.Set(pyluxcore.Property(prefix + '.type', ['mattetranslucent']))
                self.properties.Set(pyluxcore.Property(prefix + '.kr', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Kr', 'color')))
                self.properties.Set(pyluxcore.Property(prefix + '.kt', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Kt', 'color')))
                self.properties.Set(pyluxcore.Property(prefix + '.sigma', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'sigma', 'float')))

            ####################################################################
            # Metal (for keeping backwards compatibility, internally metal2)
            ####################################################################
            elif lux_mat_type == 'metal':
                fcol = self.luxcore_name + '_fcol'
                self.properties.Set(pyluxcore.Property(prefix + '.type', ['metal2']))
                self.properties.Set(pyluxcore.Property(prefix + '.fresnel', [fcol]))
                m_type = material.pbrtv3_material.pbrtv3_mat_metal.name

                if m_type != 'nk':
                    self.properties.Set(pyluxcore.Property('scene.textures.' + fcol + '.type', ['fresnelpreset']))
                    self.properties.Set(
                        pyluxcore.Property('scene.textures.' + fcol + '.name',
                                           material.pbrtv3_material.pbrtv3_mat_metal.name))

                elif m_type == 'nk':
                    full_name, base_name = get_expanded_file_name(material, lux_mat.filename)
                    self.properties.Set(pyluxcore.Property('scene.textures.' + fcol + '.type', ['fresnelsopra']))
                    self.properties.Set(pyluxcore.Property('scene.textures.' + fcol + '.file', full_name))

                u_roughness = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'uroughness', 'float')
                if lux_mat.anisotropic:
                    v_roughness = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'vroughness', 'float')
                else:
                    v_roughness = u_roughness

                self.properties.Set(pyluxcore.Property(prefix + '.uroughness', u_roughness))
                self.properties.Set(pyluxcore.Property(prefix + '.vroughness', v_roughness))

            ####################################################################
            # Metal2
            ####################################################################
            elif lux_mat_type == 'metal2':
                fcol = self.luxcore_name + '_fcol'
                m2_type = material.pbrtv3_material.pbrtv3_mat_metal2.metaltype

                if m2_type == 'preset':
                    self.properties.Set(pyluxcore.Property('scene.textures.' + fcol + '.type', ['fresnelpreset']))
                    self.properties.Set(
                        pyluxcore.Property('scene.textures.' + fcol + '.name',
                                           material.pbrtv3_material.pbrtv3_mat_metal2.preset))

                elif m2_type == 'fresnelcolor':
                    value = list(getattr(lux_mat, 'Kr_color'))

                    if getattr(lux_mat, 'Kr_usecolortexture'):
                        # The material attribute is textured, export the texture
                        texture_name = getattr(lux_mat, 'Kr_colortexturename')

                        if texture_name:
                            texture = get_texture_from_scene(self.luxcore_exporter.blender_scene, texture_name)

                            if texture:
                                self.luxcore_exporter.convert_texture(texture)
                                texture_exporter = self.luxcore_exporter.texture_cache[get_elem_key(texture)]

                                is_multiplied = getattr(lux_mat, 'Kr_multiplycolor')

                                if is_multiplied:
                                    scale_tex_name = self.luxcore_name + 'Krcolor' + fcol
                                    self.properties.Set(pyluxcore.Property('scene.textures.' + scale_tex_name + '.type', 'scale'))
                                    self.properties.Set(pyluxcore.Property('scene.textures.' + scale_tex_name + '.texture1', texture_exporter.luxcore_name))
                                    self.properties.Set(pyluxcore.Property('scene.textures.' + scale_tex_name + '.texture2', value))
                                    value = scale_tex_name
                                else:
                                    value = texture_exporter.luxcore_name

                    self.properties.Set(pyluxcore.Property('scene.textures.' + fcol + '.type', ['fresnelcolor']))
                    self.properties.Set(pyluxcore.Property('scene.textures.' + fcol + '.kr', value))

                elif m2_type == 'nk':
                    full_name, base_name = get_expanded_file_name(material, lux_mat.filename)
                    self.properties.Set(pyluxcore.Property('scene.textures.' + fcol + '.type', ['fresnelsopra']))
                    self.properties.Set(pyluxcore.Property('scene.textures.' + fcol + '.file', full_name))

                elif m2_type == 'fresneltex':
                    texture_name = lux_mat.fresnel_fresneltexturename

                    if texture_name:
                        texture = get_texture_from_scene(self.blender_scene, texture_name)

                        if texture:
                            self.luxcore_exporter.convert_texture(texture)
                            texture_exporter = self.luxcore_exporter.texture_cache[get_elem_key(texture)]

                            fcol = texture_exporter.luxcore_name

                else:
                    print('WARNING: Not yet supported metal2 type: %s' % m2_type)

                self.properties.Set(pyluxcore.Property(prefix + '.type', ['metal2']))
                self.properties.Set(pyluxcore.Property(prefix + '.fresnel', [fcol]))

                u_roughness = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'uroughness', 'float')
                if lux_mat.anisotropic:
                    v_roughness = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'vroughness', 'float')
                else:
                    v_roughness = u_roughness

                self.properties.Set(pyluxcore.Property(prefix + '.uroughness', u_roughness))
                self.properties.Set(pyluxcore.Property(prefix + '.vroughness', v_roughness))

            ####################################################################
            # Mirror
            ####################################################################
            elif lux_mat_type == 'mirror':
                self.properties.Set(pyluxcore.Property(prefix + '.type', ['mirror']))
                self.properties.Set(pyluxcore.Property(prefix + '.kr', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Kr', 'color')))

            ####################################################################
            # Glossy
            ####################################################################
            elif lux_mat_type == 'glossy':
                self.properties.Set(pyluxcore.Property(prefix + '.type', ['glossy2']))
                self.properties.Set(pyluxcore.Property(prefix + '.kd', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Kd', 'color')))

                if material.pbrtv3_material.pbrtv3_mat_glossy.useior:
                    self.properties.Set(
                        pyluxcore.Property(prefix + '.index', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'index', 'float')))
                else:
                    self.properties.Set(pyluxcore.Property(prefix + '.ks', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Ks', 'color')))

                self.properties.Set(pyluxcore.Property(prefix + '.ka', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Ka', 'color')))
                self.properties.Set(pyluxcore.Property(prefix + '.multibounce',
                                             material.pbrtv3_material.pbrtv3_mat_glossy.multibounce))
                self.properties.Set(pyluxcore.Property(prefix + '.sigma', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'sigma', 'float')))
                self.properties.Set(pyluxcore.Property(prefix + '.d', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'd', 'float')))

                u_roughness = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'uroughness', 'float')
                if lux_mat.anisotropic:
                    v_roughness = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'vroughness', 'float')
                else:
                    v_roughness = u_roughness

                self.properties.Set(pyluxcore.Property(prefix + '.uroughness', u_roughness))
                self.properties.Set(pyluxcore.Property(prefix + '.vroughness', v_roughness))

            ####################################################################
            # Glossycoating
            ####################################################################
            elif lux_mat_type == 'glossycoating':
                self.properties.Set(pyluxcore.Property(prefix + '.type', ['glossycoating']))
                if not material.pbrtv3_material.pbrtv3_mat_glossycoating.basematerial_material:
                    self.__convert_default_matte()
                    return
                else:
                    try:
                        material_base_name = material.pbrtv3_material.pbrtv3_mat_glossycoating.basematerial_material

                        base = bpy.data.materials[material_base_name]
                        self.luxcore_exporter.convert_material(base)
                        base_exporter = self.luxcore_exporter.material_cache[get_elem_key(base)]
                        luxcore_base_name = base_exporter.luxcore_name

                        self.properties.Set(pyluxcore.Property(prefix + '.base', [luxcore_base_name]))
                    except Exception as err:
                        message = 'Unable to convert base material %s\n%s' % (material.name, err)
                        log_exception(self.luxcore_exporter, message)

                if material.pbrtv3_material.pbrtv3_mat_glossycoating.useior:
                    self.properties.Set(
                        pyluxcore.Property(prefix + '.index', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'index', 'float')))
                else:
                    self.properties.Set(pyluxcore.Property(prefix + '.ks', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Ks', 'color')))

                self.properties.Set(pyluxcore.Property(prefix + '.ka', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Ka', 'color')))
                self.properties.Set(pyluxcore.Property(prefix + '.multibounce',
                                             material.pbrtv3_material.pbrtv3_mat_glossycoating.multibounce))
                self.properties.Set(pyluxcore.Property(prefix + '.d', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'd', 'float')))

                u_roughness = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'uroughness', 'float')
                if lux_mat.anisotropic:
                    v_roughness = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'vroughness', 'float')
                else:
                    v_roughness = u_roughness

                self.properties.Set(pyluxcore.Property(prefix + '.uroughness', u_roughness))
                self.properties.Set(pyluxcore.Property(prefix + '.vroughness', v_roughness))

            ####################################################################
            # Glossytranslucent
            ####################################################################
            elif lux_mat_type == 'glossytranslucent':
                self.properties.Set(pyluxcore.Property(prefix + '.type', ['glossytranslucent']))
                self.properties.Set(pyluxcore.Property(prefix + '.kt', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Kt', 'color')))
                self.properties.Set(pyluxcore.Property(prefix + '.kd', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Kd', 'color')))

                if material.pbrtv3_material.pbrtv3_mat_glossytranslucent.useior:
                    self.properties.Set(pyluxcore.Property(prefix + '.index', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'index', 'float')))
                else:
                    self.properties.Set(pyluxcore.Property(prefix + '.ks', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Ks', 'color')))

                self.properties.Set(pyluxcore.Property(prefix + '.ka', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Ka', 'color')))
                self.properties.Set(pyluxcore.Property(prefix + '.multibounce',
                                             material.pbrtv3_material.pbrtv3_mat_glossytranslucent.multibounce))
                self.properties.Set(pyluxcore.Property(prefix + '.d', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'd', 'float')))

                u_roughness = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'uroughness', 'float')
                if lux_mat.anisotropic:
                    v_roughness = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'vroughness', 'float')
                else:
                    v_roughness = u_roughness

                self.properties.Set(pyluxcore.Property(prefix + '.uroughness', u_roughness))
                self.properties.Set(pyluxcore.Property(prefix + '.vroughness', v_roughness))

                # Backface values
                if material.pbrtv3_material.pbrtv3_mat_glossytranslucent.two_sided:
                    if material.pbrtv3_material.pbrtv3_mat_glossytranslucent.bf_useior:
                        self.properties.Set(pyluxcore.Property(prefix + '.index_bf',
                                                     convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'bf_index', 'float')))
                    else:
                        self.properties.Set(pyluxcore.Property(prefix + '.ks_bf',
                                                     convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'backface_Ks', 'color')))

                    self.properties.Set(
                        pyluxcore.Property(prefix + '.ka_bf', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'backface_Ka', 'color')))
                    self.properties.Set(pyluxcore.Property(prefix + '.multibounce_bf',
                                                 material.pbrtv3_material.pbrtv3_mat_glossytranslucent.backface_multibounce))
                    self.properties.Set(pyluxcore.Property(prefix + '.d_bf', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'bf_d', 'float')))
                    self.properties.Set(pyluxcore.Property(prefix + '.uroughness_bf',
                                                 convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'bf_uroughness', 'float')))
                    self.properties.Set(pyluxcore.Property(prefix + '.vroughness_bf',
                                                 convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'bf_vroughness', 'float')))

                    u_roughness_bf = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'bf_uroughness', 'float')
                    if lux_mat.bf_anisotropic:
                        v_roughness_bf = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'bf_vroughness', 'float')
                    else:
                        v_roughness_bf = u_roughness_bf

                    self.properties.Set(pyluxcore.Property(prefix + '.uroughness_bf', u_roughness_bf))
                    self.properties.Set(pyluxcore.Property(prefix + '.vroughness_bf', v_roughness_bf))

            ####################################################################
            # Glass
            ####################################################################
            elif lux_mat_type == 'glass':
                glassType = 'archglass' if material.pbrtv3_material.pbrtv3_mat_glass.architectural else 'glass'
                self.properties.Set(pyluxcore.Property(prefix + '.type', [glassType]))
                self.properties.Set(pyluxcore.Property(prefix + '.kr', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Kr', 'color')))
                self.properties.Set(pyluxcore.Property(prefix + '.kt', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Kt', 'color')))
                self.properties.Set(pyluxcore.Property(prefix + '.cauchyb', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'cauchyb', 'float')))
                self.properties.Set(pyluxcore.Property(prefix + '.film', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'film', 'float')))
                self.properties.Set(pyluxcore.Property(prefix + '.interiorior', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'index', 'float')))

            ####################################################################
            # Glass2
            ####################################################################
            elif lux_mat_type == 'glass2':
                glassType = 'archglass' if material.pbrtv3_material.pbrtv3_mat_glass2.architectural else 'glass'
                self.properties.Set(pyluxcore.Property(prefix + '.type', [glassType]))
                self.properties.Set(pyluxcore.Property(prefix + '.kr', '1.0 1.0 1.0'))
                self.properties.Set(pyluxcore.Property(prefix + '.kt', '1.0 1.0 1.0'))

            ####################################################################
            # Roughlass
            ####################################################################
            elif lux_mat_type == 'roughglass':
                self.properties.Set(pyluxcore.Property(prefix + '.type', ['roughglass']))
                self.properties.Set(pyluxcore.Property(prefix + '.kr', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Kr', 'color')))
                self.properties.Set(pyluxcore.Property(prefix + '.kt', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Kt', 'color')))
                self.properties.Set(pyluxcore.Property(prefix + '.cauchyb', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'cauchyb', 'float')))
                self.properties.Set(pyluxcore.Property(prefix + '.interiorior', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'index', 'float')))

                u_roughness = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'uroughness', 'float')
                if lux_mat.anisotropic:
                    v_roughness = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'vroughness', 'float')
                else:
                    v_roughness = u_roughness

                self.properties.Set(pyluxcore.Property(prefix + '.uroughness', u_roughness))
                self.properties.Set(pyluxcore.Property(prefix + '.vroughness', v_roughness))

            ####################################################################
            # Cloth
            ####################################################################
            elif lux_mat_type == 'cloth':
                self.properties.Set(pyluxcore.Property(prefix + '.type', ['cloth']))
                self.properties.Set(
                    pyluxcore.Property(prefix + '.preset', material.pbrtv3_material.pbrtv3_mat_cloth.presetname))
                self.properties.Set(pyluxcore.Property(prefix + '.warp_kd', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'warp_Kd', 'color')))
                self.properties.Set(pyluxcore.Property(prefix + '.warp_ks', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'warp_Ks', 'color')))
                self.properties.Set(pyluxcore.Property(prefix + '.weft_kd', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'weft_Kd', 'color')))
                self.properties.Set(pyluxcore.Property(prefix + '.weft_ks', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'weft_Ks', 'color')))
                self.properties.Set(
                    pyluxcore.Property(prefix + '.repeat_u', material.pbrtv3_material.pbrtv3_mat_cloth.repeat_u))
                self.properties.Set(
                    pyluxcore.Property(prefix + '.repeat_v', material.pbrtv3_material.pbrtv3_mat_cloth.repeat_v))

            ####################################################################
            # Carpaint
            ####################################################################
            elif lux_mat_type == 'carpaint':
                self.properties.Set(pyluxcore.Property(prefix + '.type', ['carpaint']))
                self.properties.Set(
                    pyluxcore.Property(prefix + '.preset', material.pbrtv3_material.pbrtv3_mat_carpaint.name))
                self.properties.Set(pyluxcore.Property(prefix + '.kd', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Kd', 'color')))
                self.properties.Set(pyluxcore.Property(prefix + '.ka', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Ka', 'color')))
                self.properties.Set(pyluxcore.Property(prefix + '.ks1', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Ks1', 'color')))
                self.properties.Set(pyluxcore.Property(prefix + '.ks2', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Ks2', 'color')))
                self.properties.Set(pyluxcore.Property(prefix + '.ks3', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Ks3', 'color')))
                self.properties.Set(pyluxcore.Property(prefix + '.d', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'd', 'float')))
                self.properties.Set(pyluxcore.Property(prefix + '.m1',
                                             material.pbrtv3_material.pbrtv3_mat_carpaint.M1_floatvalue))
                self.properties.Set(pyluxcore.Property(prefix + '.m2',
                                             material.pbrtv3_material.pbrtv3_mat_carpaint.M2_floatvalue))
                self.properties.Set(pyluxcore.Property(prefix + '.m3',
                                             material.pbrtv3_material.pbrtv3_mat_carpaint.M3_floatvalue))
                self.properties.Set(pyluxcore.Property(prefix + '.r1',
                                             material.pbrtv3_material.pbrtv3_mat_carpaint.R1_floatvalue))
                self.properties.Set(pyluxcore.Property(prefix + '.r2',
                                             material.pbrtv3_material.pbrtv3_mat_carpaint.R2_floatvalue))
                self.properties.Set(pyluxcore.Property(prefix + '.r3',
                                             material.pbrtv3_material.pbrtv3_mat_carpaint.R3_floatvalue))

            ####################################################################
            # Velvet
            ####################################################################
            elif lux_mat_type == 'velvet':
                self.properties.Set(pyluxcore.Property(prefix + '.type', ['velvet']))
                self.properties.Set(pyluxcore.Property(prefix + '.kd', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'Kd', 'color')))
                self.properties.Set(pyluxcore.Property(prefix + '.thickness',
                                             material.pbrtv3_material.pbrtv3_mat_velvet.thickness))
                self.properties.Set(pyluxcore.Property(prefix + '.p1', material.pbrtv3_material.pbrtv3_mat_velvet.p1))
                self.properties.Set(pyluxcore.Property(prefix + '.p2', material.pbrtv3_material.pbrtv3_mat_velvet.p2))
                self.properties.Set(pyluxcore.Property(prefix + '.p3', material.pbrtv3_material.pbrtv3_mat_velvet.p3))

            ####################################################################
            # Null
            ####################################################################
            elif lux_mat_type == 'null':
                self.properties.Set(pyluxcore.Property(prefix + '.type', ['null']))

            ####################################################################
            # Mix
            ####################################################################
            elif lux_mat_type == 'mix':
                if (not material.pbrtv3_material.pbrtv3_mat_mix.namedmaterial1_material or
                        not material.pbrtv3_material.pbrtv3_mat_mix.namedmaterial2_material):
                    self.__convert_default_matte()
                    return
                else:
                    try:
                        mat1_name = material.pbrtv3_material.pbrtv3_mat_mix.namedmaterial1_material
                        mat2_name = material.pbrtv3_material.pbrtv3_mat_mix.namedmaterial2_material

                        mat1 = bpy.data.materials[mat1_name]
                        mat2 = bpy.data.materials[mat2_name]

                        self.luxcore_exporter.convert_material(mat1)
                        self.luxcore_exporter.convert_material(mat2)

                        mat1_luxcore_name = self.luxcore_exporter.material_cache[get_elem_key(mat1)].luxcore_name
                        mat2_luxcore_name = self.luxcore_exporter.material_cache[get_elem_key(mat2)].luxcore_name

                        self.properties.Set(pyluxcore.Property(prefix + '.type', ['mix']))
                        self.properties.Set(pyluxcore.Property(prefix + '.material1', mat1_luxcore_name))
                        self.properties.Set(pyluxcore.Property(prefix + '.material2', mat2_luxcore_name))
                        self.properties.Set(pyluxcore.Property(prefix + '.amount', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, lux_mat, 'amount', 'float')))
                    except Exception as err:
                        message = 'Unable to convert mix material %s\n%s' % (material.name, err)
                        log_exception(self.luxcore_exporter, message)
                        self.__convert_default_matte()

            ####################################################################
            # Fallback
            ####################################################################
            else:
                self.__convert_default_matte()
                return

            ####################################################################
            # Common settings for all material types
            ####################################################################
            if not translator_settings.override_materials:
                # Combined  bump/normaltex
                if material.pbrtv3_material.bumpmap_usefloattexture and material.pbrtv3_material.normalmap_usefloattexture \
                                                                        and material.pbrtv3_material.normalmap_floattexturename:
                    bump_texture = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name,
                                                        material.pbrtv3_material, 'bumpmap', 'float')
                    normalmap_texture = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name,
                                                        material.pbrtv3_material, 'normalmap', 'float')

                    normalmap_luxcore_name = ToValidPBRTv3CoreName(material.pbrtv3_material.normalmap_floattexturename)
                    # We have to set normalmap gamma to 1
                    self.properties.Set(pyluxcore.Property('scene.textures.' + normalmap_luxcore_name + '.gamma', 1))
                    if getattr(material.pbrtv3_material, 'normalmap_multiplyfloat'):
                        # Overide the multiplier in the created scale texture, we attach this later to the normalmap_helper
                        self.properties.Set(pyluxcore.Property('scene.textures.' + normalmap_texture + '.texture2', 1))

                    # Create a normalmap
                    normalmap_helper = '%s_normal_map_float' % normalmap_luxcore_name
                    normalmap_multiplier = getattr(material.pbrtv3_material, 'normalmap_floatvalue')
                    self.properties.Set(pyluxcore.Property('scene.textures.' + normalmap_helper + '.type', 'normalmap'))
                    self.properties.Set(pyluxcore.Property('scene.textures.' + normalmap_helper + '.texture', normalmap_texture))
                    if getattr(material.pbrtv3_material, 'normalmap_multiplyfloat'):
                        self.properties.Set(pyluxcore.Property('scene.textures.' + normalmap_helper + '.scale', normalmap_multiplier))

                    # Create combined texture ( add, or rather mix ? )
                    add_texture = '%s_bump_normal_add' % normalmap_luxcore_name
                    self.properties.Set(pyluxcore.Property('scene.textures.' + add_texture + '.type', 'add'))
                    self.properties.Set(pyluxcore.Property('scene.textures.' + add_texture + '.texture1', bump_texture))
                    self.properties.Set(pyluxcore.Property('scene.textures.' + add_texture + '.texture2', normalmap_helper))
                    self.properties.Set(pyluxcore.Property(prefix + '.bumptex', add_texture))

                # Bump mapping
                elif material.pbrtv3_material.bumpmap_usefloattexture:
                    self.properties.Set(pyluxcore.Property(prefix + '.bumptex',
                                                 convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, material.pbrtv3_material, 'bumpmap',
                                                                            'float')))

                # Normal mapping (make sure a texture is selected)
                elif material.pbrtv3_material.normalmap_usefloattexture and material.pbrtv3_material.normalmap_floattexturename:
                    normalmap = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name,
                                                        material.pbrtv3_material, 'normalmap', 'float')
                    # We have to set normalmap gamma to 1
                    self.properties.Set(pyluxcore.Property('scene.textures.' + normalmap + '.gamma', 1))

                    self.properties.Set(pyluxcore.Property(prefix + '.normaltex', normalmap))

                # Interior/exterior volumes
                interior = self.material.pbrtv3_material.Interior_volume
                exterior = self.material.pbrtv3_material.Exterior_volume
                self.__set_material_volumes(prefix, interior, exterior)

            # coating for all materials
            if hasattr(material, 'pbrtv3_coating') and material.pbrtv3_coating.use_coating:
                name_coating = self.luxcore_name + '_coated'
                luxMat_coated = material.pbrtv3_coating
                prefix += '_coated'
                self.properties.Set(pyluxcore.Property(prefix + '.type', ['glossycoating']))
                self.properties.Set(pyluxcore.Property(prefix + '.base', [self.luxcore_name]))
                self.properties.Set(pyluxcore.Property(prefix + '.kd', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxMat_coated, 'Ks', 'color')))

                if material.pbrtv3_coating.useior:
                    self.properties.Set(
                        pyluxcore.Property(prefix + '.index', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxMat_coated, 'index', 'float')))
                else:
                    self.properties.Set(pyluxcore.Property(prefix + '.ks', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxMat_coated, 'Ks', 'color')))

                self.properties.Set(pyluxcore.Property(prefix + '.ka', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxMat_coated, 'Ka', 'color')))
                self.properties.Set(pyluxcore.Property(prefix + '.multibounce',
                                             material.pbrtv3_coating.multibounce))
                self.properties.Set(pyluxcore.Property(prefix + '.d', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxMat_coated, 'd', 'float')))

                u_roughness = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxMat_coated, 'uroughness', 'float')
                if luxMat_coated.anisotropic:
                    v_roughness = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxMat_coated, 'vroughness', 'float')
                else:
                    v_roughness = u_roughness

                self.properties.Set(pyluxcore.Property(prefix + '.uroughness', u_roughness))
                self.properties.Set(pyluxcore.Property(prefix + '.vroughness', v_roughness))

                self.luxcore_name = name_coating

            # PBRTv3Core specific material settings
            lc_mat = material.luxcore_material

            self.properties.Set(pyluxcore.Property(prefix + '.shadowcatcher.enable', lc_mat.is_shadow_catcher))
            self.properties.Set(pyluxcore.Property(prefix + '.shadowcatcher.onlyinfinitelights', lc_mat.sc_onlyinfinitelights))

            # Material group
            materialgroup_name = lc_mat.materialgroup
            if materialgroup_name in self.blender_scene.pbrtv3_materialgroups.materialgroups:
                mg = self.blender_scene.pbrtv3_materialgroups.materialgroups[materialgroup_name]

                self.properties.Set(pyluxcore.Property(prefix + '.id', mg.id))
                if mg.create_MATERIAL_ID_MASK and self.blender_scene.pbrtv3_channels.enable_aovs:
                    self.luxcore_exporter.config_exporter.convert_channel('MATERIAL_ID_MASK', mg.id)
                if mg.create_BY_MATERIAL_ID and self.blender_scene.pbrtv3_channels.enable_aovs:
                    self.luxcore_exporter.config_exporter.convert_channel('BY_MATERIAL_ID', mg.id)

            self.properties.Set(pyluxcore.Property(prefix + '.samples', [lc_mat.samples]))

            if material.pbrtv3_emission.use_emission:
                self.properties.Set(pyluxcore.Property(prefix + '.emission.samples', [lc_mat.emission_samples]))

            self.properties.Set(pyluxcore.Property(prefix + '.visibility.indirect.diffuse.enable',
                                         lc_mat.visibility_indirect_diffuse_enable))
            self.properties.Set(pyluxcore.Property(prefix + '.visibility.indirect.glossy.enable',
                                         lc_mat.visibility_indirect_glossy_enable))
            self.properties.Set(pyluxcore.Property(prefix + '.visibility.indirect.specular.enable',
                                         lc_mat.visibility_indirect_specular_enable))

            if not (translator_settings.override_materials and translator_settings.override_lights):
                # PBRTv3 emission
                if material.pbrtv3_emission.use_emission:
                    emit_enabled = self.blender_scene.pbrtv3_lightgroups.is_enabled(material.pbrtv3_emission.lightgroup)
                    emit_enabled &= (material.pbrtv3_emission.L_color.v * material.pbrtv3_emission.gain) > 0.0
                    if emit_enabled:
                        self.properties.Set(pyluxcore.Property(prefix + '.emission',
                                                     convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, material.pbrtv3_emission, 'L', 'color')))

                        self.properties.Set(pyluxcore.Property(prefix + '.emission.power', material.pbrtv3_emission.power))
                        self.properties.Set(pyluxcore.Property(prefix + '.emission.efficency', material.pbrtv3_emission.efficacy))

                        lightgroup = material.pbrtv3_emission.lightgroup
                        lightgroup_id = self.luxcore_exporter.lightgroup_cache.get_id(lightgroup, self.blender_scene, self)

                        if not self.blender_scene.pbrtv3_lightgroups.ignore and is_lightgroup_opencl_compatible(self.luxcore_exporter, lightgroup_id):
                            self.properties.Set(pyluxcore.Property(prefix + '.emission.id', [lightgroup_id]))

                        gain = material.pbrtv3_emission.gain
                        self.properties.Set(pyluxcore.Property(prefix + '.emission.gain', [gain] * 3))

                        # Ies
                        iesfile = material.pbrtv3_emission.iesname
                        iesfile, basename = get_expanded_file_name(material.pbrtv3_emission, iesfile)
                        if os.path.exists(iesfile):
                            self.properties.Set(pyluxcore.Property(prefix + '.emission.iesfile', iesfile))

            # alpha transparency
            if hasattr(material, 'pbrtv3_transparency') and material.pbrtv3_transparency.transparent:
                use_alpha_transparency = True

                alpha = 0.0

                self.__convert_default_null()

                sourceMap = {
                    'carpaint': 'Kd',
                    'glass': 'Kr',
                    'glossy': 'Kd',
                    'glossytranslucent': 'Kd',
                    'matte': 'Kd',
                    'mattetranslucent': 'Kr',
                    'mirror': 'Kr',
                    'roughglass': 'Kr',
                    'scatter': 'Kd',
                    'shinymetal': 'Kr',
                    'velvet': 'Kd',
                    'metal2': 'Kr',
                }

                alpha_source = material.pbrtv3_transparency.alpha_source

                if alpha_source == 'texture':
                    if hasattr(material.pbrtv3_transparency, 'alpha_floattexturename'):
                        texture_name = material.pbrtv3_transparency.alpha_floattexturename

                        if texture_name in bpy.data.textures:
                            texture = bpy.data.textures[texture_name]

                            alpha_tex_exporter = TextureExporter(self.luxcore_exporter, self.blender_scene, texture)
                            alpha_tex_exporter.convert(texture_name + material.name + '_alpha')
                            alpha = alpha_tex_exporter.luxcore_name

                            self.properties.Set(alpha_tex_exporter.properties)
                            # Note: the channel (rgb/alpha/mean/...) is set in the texture

                            if material.pbrtv3_transparency.inverse:
                                inverter_name = alpha + '_inverter'
                                inverter_prefix = 'scene.textures.' + inverter_name

                                self.properties.Set(pyluxcore.Property(inverter_prefix + '.type', 'mix'))
                                self.properties.Set(pyluxcore.Property(inverter_prefix + '.amount', alpha))
                                self.properties.Set(pyluxcore.Property(inverter_prefix + '.texture1', 1.0))
                                self.properties.Set(pyluxcore.Property(inverter_prefix + '.texture2', 0.0))

                                alpha = inverter_name
                        else:
                            use_alpha_transparency = False

                elif alpha_source == 'constant':
                    alpha = material.pbrtv3_transparency.alpha_value

                # diffusealpha, diffusemean, diffuseintensity
                elif (material.pbrtv3_material.type in sourceMap
                      and getattr(lux_mat, '%s_usecolortexture' % sourceMap[material.pbrtv3_material.type])):
                    # Get base texture name
                    texture_name = getattr(lux_mat, '%s_colortexturename' % sourceMap[material.pbrtv3_material.type])

                    if texture_name in bpy.data.textures:
                        # Get blender texture
                        texture = bpy.data.textures[texture_name]
                        # Export texture, get luxcore texture name
                        alpha_tex_exporter = TextureExporter(self.luxcore_exporter, self.blender_scene, texture)
                        alpha_tex_exporter.convert(texture_name + material.name + '_alpha')
                        alpha = alpha_tex_exporter.luxcore_name

                        self.properties.Set(alpha_tex_exporter.properties)

                        channelMap = {
                            'diffusealpha': 'alpha',
                            'diffusemean': 'mean',
                            'diffuseintensity': 'colored_mean',
                        }
                        self.properties.Set(pyluxcore.Property('scene.textures.' + alpha + '.channel', [channelMap[alpha_source]]))
                    else:
                        use_alpha_transparency = False
                else:
                    print(
                    'WARNING: alpha transparency not supported for material type %s' % material.pbrtv3_material.type)
                    use_alpha_transparency = False

                if use_alpha_transparency:
                    if not prefix.endswith('_coated'):
                        self.properties.Set(pyluxcore.Property(prefix + '.transparency', alpha))
                    else:
                        # We must apply the transparency to the basemat
                        base_prefix = prefix.replace('_coated', '')
                        self.properties.Set(pyluxcore.Property(base_prefix + '.transparency', alpha))

        except Exception as err:
            message = 'Material export failed, skipping material: %s\n%s' % (self.material.name, err)
            log_exception(self.luxcore_exporter, message)
            self.__convert_default_matte()