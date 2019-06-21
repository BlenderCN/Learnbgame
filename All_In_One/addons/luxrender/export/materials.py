# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond, Genscher
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
import os

import bpy

from ..extensions_framework import util as efutil

from ..export import ParamSet
from ..outputs import LuxLog, LuxManager
from ..properties import find_node


class TextureCounter(object):
    stack = []

    @classmethod
    def reset(cls):
        cls.stack = []

    def __init__(self, name):
        self.ident = name

    def __enter__(self):
        if self.ident in TextureCounter.stack:
            raise Exception("Recursion in texture assignment: %s" % ' -> '.join(TextureCounter.stack))
        TextureCounter.stack.append(self.ident)

    def __exit__(self, exc_type, exc_val, exc_tb):
        TextureCounter.stack.pop()


class ExportedTextures(object):
    # static class variables
    texture_names = []  # Name
    texture_types = []  # Float|Color
    texture_texts = []  # Texture plugin name
    texture_psets = []  # ParamSets
    exported_texture_names = []
    scalers_count = 0

    @staticmethod
    def clear():
        TextureCounter.reset()
        ExportedTextures.texture_names = []
        ExportedTextures.texture_types = []
        ExportedTextures.texture_texts = []
        ExportedTextures.texture_psets = []
        ExportedTextures.exported_texture_names = []
        ExportedTextures.scalers_count = 0

    @staticmethod
    def next_scale_value():
        ExportedTextures.scalers_count += 1
        return ExportedTextures.scalers_count

    @staticmethod
    def texture(lux_context, name, type, texture, params):
        if lux_context.API_TYPE == 'PURE':
            lux_context.texture(name, type, texture, params)
            ExportedTextures.exported_texture_names.append(name)
            return

        if name not in ExportedTextures.exported_texture_names:
            ExportedTextures.texture_names.append(name)
            ExportedTextures.texture_types.append(type)
            ExportedTextures.texture_texts.append(texture)
            ExportedTextures.texture_psets.append(params)

    @staticmethod
    def export_new(lux_context):
        for n, ty, tx, p in zip(
                ExportedTextures.texture_names,
                ExportedTextures.texture_types,
                ExportedTextures.texture_texts,
                ExportedTextures.texture_psets
        ):
            if lux_context.API_TYPE != 'PURE' and n not in ExportedTextures.exported_texture_names:
                lux_context.texture(n, ty, tx, p)
                ExportedTextures.exported_texture_names.append(n)


class MaterialCounter(object):
    stack = []

    @classmethod
    def reset(cls):
        cls.stack = []

    def __init__(self, name):
        self.ident = name

    def __enter__(self):
        if self.ident in MaterialCounter.stack:
            raise Exception("Recursion in material assignment: %s" % ' -> '.join(MaterialCounter.stack))

        MaterialCounter.stack.append(self.ident)

    def __exit__(self, exc_type, exc_val, exc_tb):
        MaterialCounter.stack.pop()


class ExportedMaterials(object):
    # Static class variables
    material_names = []
    material_psets = []
    exported_material_names = []

    @staticmethod
    def clear():
        MaterialCounter.reset()
        ExportedMaterials.material_names = []
        ExportedMaterials.material_psets = []
        ExportedMaterials.exported_material_names = []

    @staticmethod
    def makeNamedMaterial(lux_context, name, paramset):
        if lux_context.API_TYPE == 'PURE':
            lux_context.makeNamedMaterial(name, paramset)
            return

        if name not in ExportedMaterials.exported_material_names:
            ExportedMaterials.material_names.append(name)
            ExportedMaterials.material_psets.append(paramset)

    @staticmethod
    def export_new_named(lux_context):
        for n, p in zip(ExportedMaterials.material_names, ExportedMaterials.material_psets):
            if lux_context.API_TYPE != 'PURE' and n not in ExportedMaterials.exported_material_names:
                lux_context.makeNamedMaterial(n, p)
                ExportedMaterials.exported_material_names.append(n)


def get_instance_materials(ob):
    obmats = []
    # Grab materials attached to object instances ...
    if hasattr(ob, 'material_slots'):
        for ms in ob.material_slots:
            obmats.append(ms.material)
    # ... and to the object's mesh data
    if hasattr(ob.data, 'materials'):
        for m in ob.data.materials:
            obmats.append(m)

    # per instance materials will take precedence
    # over the base mesh's material definition.
    return obmats


def get_material_volume_defs(m):
    if m.luxrender_material.nodetree:
        outputNode = find_node(m, 'luxrender_material_output_node')
        tree_name = m.luxrender_material.nodetree

        if outputNode is None:
            print('Node tree is assigned, but does not contain an output node')
            return ""

        int_vol_socket = outputNode.inputs[1]

        if int_vol_socket.is_linked:
            int_vol_node = int_vol_socket.links[0].from_node

        ext_vol_socket = outputNode.inputs[2]

        if ext_vol_socket.is_linked:
            ext_vol_node = ext_vol_socket.links[0].from_node

        int_vol_name = '%s::%s' % (tree_name, int_vol_node.name) if int_vol_socket.is_linked else ""
        ext_vol_name = '%s::%s' % (tree_name, ext_vol_node.name) if ext_vol_socket.is_linked else ""

        return int_vol_name, ext_vol_name
    else:
        return m.luxrender_material.Interior_volume, m.luxrender_material.Exterior_volume


def get_preview_flip(m):
    return m.luxrender_material.mat_preview_flip_xz


def get_preview_zoom(m):
    return m.luxrender_material.preview_zoom


def convert_texture(scene, texture, variant_hint=None):
    # Lux only supports blender's textures in float variant (except for image/ocean,
    # but both of these are exported as imagemap)
    variant = 'float'
    paramset = ParamSet()

    lux_tex_name = 'blender_%s' % texture.type.lower()

    mapping_type = '3D'

    if texture.type not in ('IMAGE', 'OCEAN'):
        paramset.add_float('bright', texture.intensity)
        paramset.add_float('contrast', texture.contrast)

    if texture.type == 'BLEND':
        progression_map = {
            'LINEAR': 'lin',
            'QUADRATIC': 'quad',
            'EASING': 'ease',
            'DIAGONAL': 'diag',
            'SPHERICAL': 'sphere',
            'QUADRATIC_SPHERE': 'halo',
            'RADIAL': 'radial'
        }
        direction_map = {
            'HORIZONTAL': False,
            'VERTICAL': True
        }

        paramset.add_bool('flipxy', direction_map[texture.use_flip_axis]) \
            .add_string('type', progression_map[texture.progression])

    if texture.type == 'CLOUDS':
        paramset.add_string('noisetype', texture.noise_type.lower()) \
            .add_string('noisebasis', texture.noise_basis.lower()) \
            .add_float('noisesize', texture.noise_scale) \
            .add_integer('noisedepth', texture.noise_depth)

    if texture.type == 'DISTORTED_NOISE':
        lux_tex_name = 'blender_distortednoise'
        paramset.add_string('type', texture.noise_distortion.lower()) \
            .add_string('noisebasis', texture.noise_basis.lower()) \
            .add_float('distamount', texture.distortion) \
            .add_float('noisesize', texture.noise_scale) \
            .add_float('nabla', texture.nabla)

    if texture.type == 'MAGIC':
        paramset.add_integer('noisedepth', texture.noise_depth) \
            .add_float('turbulence', texture.turbulence)

    if texture.type == 'MARBLE':
        paramset.add_string('type', texture.marble_type.lower()) \
            .add_string('noisetype', texture.noise_type.lower()) \
            .add_string('noisebasis', texture.noise_basis.lower()) \
            .add_string('noisebasis2', texture.noise_basis_2.lower()) \
            .add_float('noisesize', texture.noise_scale) \
            .add_float('turbulence', texture.turbulence) \
            .add_integer('noisedepth', texture.noise_depth)

    if texture.type == 'MUSGRAVE':
        paramset.add_string('type', texture.musgrave_type.lower()) \
            .add_float('h', texture.dimension_max) \
            .add_float('lacu', texture.lacunarity) \
            .add_string('noisebasis', texture.noise_basis.lower()) \
            .add_float('noisesize', texture.noise_scale) \
            .add_float('octs', texture.octaves)

    # NOISE shows no params ?

    if texture.type == 'STUCCI':
        paramset.add_string('type', texture.stucci_type.lower()) \
            .add_string('noisetype', texture.noise_type.lower()) \
            .add_string('noisebasis', texture.noise_basis.lower()) \
            .add_float('noisesize', texture.noise_scale) \
            .add_float('turbulence', texture.turbulence)

    if texture.type == 'VORONOI':
        distancem_map = {
            'DISTANCE': 'actual_distance',
            'DISTANCE_SQUARED': 'distance_squared',
            'MANHATTAN': 'manhattan',
            'CHEBYCHEV': 'chebychev',
            'MINKOVSKY_HALF': 'minkovsky_half',
            'MINKOVSKY_FOUR': 'minkovsky_four',
            'MINKOVSKY': 'minkovsky'
        }
        paramset.add_string('distmetric', distancem_map[texture.distance_metric]) \
            .add_float('minkovsky_exp', texture.minkovsky_exponent) \
            .add_float('noisesize', texture.noise_scale) \
            .add_float('nabla', texture.nabla) \
            .add_float('w1', texture.weight_1) \
            .add_float('w2', texture.weight_2) \
            .add_float('w3', texture.weight_3) \
            .add_float('w4', texture.weight_4)

    if texture.type == 'WOOD':
        paramset.add_string('noisebasis', texture.noise_basis.lower()) \
            .add_string('noisebasis2', texture.noise_basis_2.lower()) \
            .add_float('noisesize', texture.noise_scale) \
            .add_string('noisetype', texture.noise_type.lower()) \
            .add_float('turbulence', texture.turbulence) \
            .add_string('type', texture.wood_type.lower())

    # Translate Blender Image/movie into lux tex
    if texture.type == 'IMAGE' and texture.image and texture.image.source in ['GENERATED', 'FILE', 'SEQUENCE']:
        extract_path = os.path.join(
            efutil.scene_filename(),
            bpy.path.clean_name(scene.name),
            '%05d' % scene.frame_current
        )

        if texture.image.source == 'GENERATED':
            tex_image = 'luxblend_baked_image_%s.%s' % (
                bpy.path.clean_name(texture.name), scene.render.image_settings.file_format)
            tex_image = os.path.join(extract_path, tex_image)
            texture.image.save_render(tex_image, scene)

        if texture.image.source == 'FILE':
            if texture.image.packed_file:
                tex_image = 'luxblend_extracted_image_%s.%s' % (
                    bpy.path.clean_name(texture.name), scene.render.image_settings.file_format)

                tex_image = os.path.join(extract_path, tex_image)
                texture.image.save_render(tex_image, scene)
            else:
                if texture.library is not None:
                    f_path = efutil.filesystem_path(bpy.path.abspath(texture.image.filepath, texture.library.filepath))
                else:
                    f_path = efutil.filesystem_path(texture.image.filepath)
                if not os.path.exists(f_path):
                    raise Exception(
                        'Image referenced in blender texture %s doesn\'t exist: %s' % (texture.name, f_path))

                tex_image = efutil.filesystem_path(f_path)

        if texture.image.source == 'SEQUENCE':
            if texture.image.packed_file:
                tex_image = 'luxblend_extracted_image_%s.%s' % (
                    bpy.path.clean_name(texture.name), scene.render.image_settings.file_format)

                tex_image = os.path.join(extract_path, tex_image)
                texture.image.save_render(tex_image, scene)
            else:
                # sequence params from blender
                # remove tex_preview extension to avoid error
                sequence = bpy.data.textures[texture.name.replace('.001', '')].image_user

                seqframes = sequence.frame_duration
                seqoffset = sequence.frame_offset
                seqstartframe = sequence.frame_start  # the global frame at which the imagesequence starts
                seqcyclic = sequence.use_cyclic
                currentframe = scene.frame_current

                if texture.library is not None:
                    f_path = efutil.filesystem_path(bpy.path.abspath(texture.image.filepath, texture.library.filepath))
                else:
                    f_path = efutil.filesystem_path(texture.image.filepath)

                if currentframe < seqstartframe:
                    fnumber = 1 + seqoffset
                else:
                    fnumber = currentframe - (seqstartframe - 1) + seqoffset

                if fnumber > seqframes:
                    if not seqcyclic:
                        fnumber = seqframes
                    else:
                        fnumber = (currentframe - (seqstartframe - 1)) % seqframes

                        if fnumber == 0:
                            fnumber = seqframes

                import re

                def get_seq_filename(number, f_path):
                    m = re.findall(r'(\d+)', f_path)

                    if len(m) == 0:
                        return "ERR: Can't find pattern"

                    rightmost_number = m[len(m) - 1]
                    seq_length = len(rightmost_number)

                    nstr = "%i" % number
                    new_seq_number = nstr.zfill(seq_length)

                    return f_path.replace(rightmost_number, new_seq_number)

                f_path = get_seq_filename(fnumber, f_path)

                # print("-----------------", f_path)

                if not os.path.exists(f_path):
                    raise Exception(
                        'Image referenced in blender texture %s doesn\'t exist: %s' % (texture.name, f_path))

                tex_image = efutil.filesystem_path(f_path)

        lux_tex_name = 'imagemap'
        sampling = texture.luxrender_texture.luxrender_tex_imagesampling

        if variant_hint:
            variant = variant_hint
        else:
            variant = 'color'

        paramset.add_string('filename', tex_image)

        if variant_hint == float:
            paramset.add_string('channel', sampling.channel)

        paramset.add_integer('discardmipmaps', sampling.discardmipmaps)
        paramset.add_float('gain', sampling.gain)
        paramset.add_float('gamma', sampling.gamma)
        paramset.add_float('maxanisotropy', sampling.maxanisotropy)
        paramset.add_string('wrap', sampling.wrap)
        mapping_type = '2D'

    # Similar to image handler, but for Ocean tex
    if texture.type == 'OCEAN':
        if texture.ocean.output == 'FOAM':

            ocean_mods = [m for m in texture.ocean.ocean_object.modifiers if m.type == 'OCEAN']
            if len(ocean_mods) == 0:
                print('No ocean modifiers!')
            else:
                ocean_mod = ocean_mods[0]

            if texture.ocean.output == 'FOAM':
                tex_image = efutil.filesystem_path(
                    os.path.join(ocean_mod.filepath, 'foam_%04d.exr' % scene.frame_current))
                # SOON! (until 3D disp support...)
            # elif texture.ocean.output == 'DISPLACEMENT':
            # tex_image = os.path.join(ocean_mod.filepath, 'disp_%04d.exr' % scene.frame_current)

            lux_tex_name = 'imagemap'
            if variant_hint:
                variant = variant_hint
            else:
                variant = 'color'

            paramset.add_string('filename', tex_image)
            paramset.add_float('gamma', 1.0)
            mapping_type = '2D'

        else:
            lux_tex_name = 'constant'

    if mapping_type == '3D':
        paramset.update(texture.luxrender_texture.luxrender_tex_transform.get_paramset(scene))
    else:
        paramset.update(texture.luxrender_texture.luxrender_tex_mapping.get_paramset(scene))

    return variant, lux_tex_name, paramset


def value_transform_passthrough(val):
    return val


def get_texture_from_scene(scene, tex_name):
    if scene.world is not None:
        for tex_slot in scene.world.texture_slots:
            if tex_slot is not None and tex_slot.texture is not None and tex_slot.texture.name == tex_name:
                return tex_slot.texture

    for obj in scene.objects:
        for mat_slot in obj.material_slots:
            if mat_slot is not None and mat_slot.material is not None:
                for tex_slot in mat_slot.material.texture_slots:
                    if tex_slot is not None and tex_slot.texture is not None and tex_slot.texture.name == tex_name:
                        return tex_slot.texture

        if obj.type == 'LAMP':
            for tex_slot in obj.data.texture_slots:
                if tex_slot is not None and tex_slot.texture is not None and tex_slot.texture.name == tex_name:
                    return tex_slot.texture

    # Last but not least, look in global bpy.data
    if tex_name in bpy.data.textures:
        return bpy.data.textures[tex_name]

    LuxLog('Failed to find Texture "%s" in Scene "%s"' % (tex_name, scene.name))
    return False


def add_texture_parameter(lux_context, lux_prop_name, variant, property_group, value_transform_function=None):
    """
    lux_context				pylux.Context - like object
    lux_prop_name			LuxRender material/texture parameter name
    variant					Required variant: 'float' or 'color' or 'fresnel'
    property_group			luxrender_material or luxrender_texture IDPropertyGroup FOR THE CONTAINING MATERIAL/TEXTURE

    Either insert a float parameter or a float texture reference, depending on setup

    Returns					ParamSet
    """
    params = ParamSet()

    if hasattr(property_group, '%s_use%stexture' % (lux_prop_name, variant)):
        export_param_name = getattr(property_group, lux_prop_name)

        if value_transform_function is None:
            value_transform_function = value_transform_passthrough

        if getattr(property_group, '%s_use%stexture' % (lux_prop_name, variant)):
            texture_name = getattr(property_group, '%s_%stexturename' % (lux_prop_name, variant))
            if texture_name:
                with TextureCounter(texture_name):
                    texture = get_texture_from_scene(LuxManager.CurrentScene, texture_name)

                    if texture != False:
                        if texture.luxrender_texture.type != 'BLENDER':
                            tex_luxrender_texture = texture.luxrender_texture
                            lux_tex_variant, paramset = tex_luxrender_texture.get_paramset(LuxManager.CurrentScene,
                                                                                           texture)
                            if lux_tex_variant == variant:
                                ExportedTextures.texture(lux_context, texture_name, variant, tex_luxrender_texture.type,
                                                         paramset)
                            else:
                                LuxLog('WARNING: Texture %s is wrong variant; needed %s, got %s' % (
                                    lux_prop_name, variant, lux_tex_variant))
                        else:
                            lux_tex_variant, lux_tex_name, paramset = convert_texture(LuxManager.CurrentScene, texture,
                                                                                      variant_hint=variant)
                            if texture.type in ('OCEAN', 'IMAGE'):
                                texture_name = texture_name + "_" + lux_tex_variant

                            if lux_tex_variant == variant:
                                ExportedTextures.texture(lux_context, texture_name, lux_tex_variant, lux_tex_name,
                                                         paramset)
                            else:
                                LuxLog('WARNING: Texture %s is wrong variant; needed %s, got %s' % (
                                    lux_prop_name, variant, lux_tex_variant))

                        if hasattr(property_group, '%s_multiplyfloat' % lux_prop_name) and \
                                getattr(property_group, '%s_multiplyfloat' % lux_prop_name):
                            sv = ExportedTextures.next_scale_value()
                            ExportedTextures.texture(
                                lux_context,
                                '%s_scaled_%i' % (texture_name, sv),
                                variant,
                                'scale',
                                ParamSet() \
                                .add_float('tex1', float(getattr(property_group, '%s_floatvalue' % lux_prop_name))) \
                                .add_texture('tex2', texture_name)
                            )
                            texture_name += '_scaled_%i' % sv

                        if hasattr(property_group, '%s_multiplyfresnel' % lux_prop_name) and \
                                getattr(property_group, '%s_multiplyfresnel' % lux_prop_name):
                            sv = ExportedTextures.next_scale_value()
                            ExportedTextures.texture(
                                lux_context,
                                '%s_scaled_%i' % (texture_name, sv),
                                variant,
                                'scale',
                                ParamSet() \
                                .add_float('tex1',
                                           float(getattr(property_group, '%s_fresnelvalue' % lux_prop_name))) \
                                .add_texture('tex2', texture_name)
                            )
                            texture_name += '_scaled_%i' % sv

                        if hasattr(property_group, '%s_multiplycolor' % lux_prop_name) and \
                                getattr(property_group, '%s_multiplycolor' % lux_prop_name):
                            sv = ExportedTextures.next_scale_value()
                            ExportedTextures.texture(
                                lux_context,
                                '%s_scaled_%i' % (texture_name, sv),
                                variant,
                                'scale',
                                ParamSet() \
                                .add_color(
                                    'tex1',
                                    [float(value_transform_function(i)) for i in
                                     getattr(property_group, '%s_color' % lux_prop_name)]
                                ) \
                                .add_texture('tex2', texture_name)
                            )
                            texture_name += '_scaled_%i' % sv

                        ExportedTextures.export_new(lux_context)

                        params.add_texture(
                            export_param_name,
                            texture_name
                        )

            elif export_param_name not in ['bumpmap', 'displacementmap']:
                LuxLog('WARNING: Unassigned %s texture slot %s' % (variant, export_param_name))
        else:
            if variant == 'float':
                fval = float(getattr(property_group, '%s_floatvalue' % lux_prop_name))
                if not getattr(property_group, '%s_ignore_unassigned' % lux_prop_name):
                    params.add_float(
                        export_param_name,
                        fval
                    )
            elif variant == 'color':
                params.add_color(
                    export_param_name,
                    [float(value_transform_function(i)) for i in getattr(property_group, '%s_color' % lux_prop_name)]
                )
            elif variant == 'fresnel':
                fval = float(getattr(property_group, '%s_fresnelvalue' % lux_prop_name))
                params.add_float(
                    export_param_name,
                    fval
                )
    else:
        LuxLog('WARNING: Texture %s is unsupported variant; needed %s' % (lux_prop_name, variant))

    return params
