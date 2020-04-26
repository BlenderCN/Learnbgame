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

import bpy, math, mathutils, os, tempfile

from ...extensions_framework import util as efutil
from ...outputs.luxcore_api import pyluxcore
from ...outputs.luxcore_api import ToValidPBRTv3CoreName
from ...export import matrix_to_list
from ...export import get_expanded_file_name
from ...export.volumes import SmokeCache

from .utils import convert_texture_channel


class TextureExporter(object):
    def __init__(self, luxcore_exporter, blender_scene, texture):
        self.luxcore_exporter = luxcore_exporter
        self.blender_scene = blender_scene
        self.texture = texture

        self.properties = pyluxcore.Properties()
        self.luxcore_name = ''


    def convert(self, name=''):
        # Remove old properties
        self.properties = pyluxcore.Properties()

        self.__convert_texture(name)

        return self.properties


    def __convert_mapping(self, prefix, texture):
        # Note 2DMapping is used for: bilerp, checkerboard(dimension == 2), dots, imagemap, normalmap, uv, uvmask
        # Blender - image
        luxMapping = getattr(texture.pbrtv3_texture, 'pbrtv3_tex_mapping')

        if luxMapping.type == 'uv':
            self.properties.Set(pyluxcore.Property(prefix + '.mapping.type', 'uvmapping2d'))
            self.properties.Set(
                pyluxcore.Property(prefix + '.mapping.uvscale', [luxMapping.uscale, luxMapping.vscale * - 1.0]))

            if not luxMapping.center_map:
                self.properties.Set(
                    pyluxcore.Property(prefix + '.mapping.uvdelta', [luxMapping.udelta, luxMapping.vdelta + 1.0]))
            else:
                self.properties.Set(pyluxcore.Property(prefix + '.mapping.uvdelta', [
                    luxMapping.udelta + 0.5 * (1.0 - luxMapping.uscale),
                    luxMapping.vdelta * - 1.0 + 1.0 - (0.5 * (1.0 - luxMapping.vscale))]))
        else:
            raise Exception('Unsupported mapping for texture: ' + texture.name)


    def __convert_transform(self, prefix, texture):
        # Note 3DMapping is used for: brick, checkerboard(dimension == 3), cloud', densitygrid,
        # exponential, fbm', marble', windy, wrinkled
        # BLENDER - CLOUDS,DISTORTED_NOISE,MAGIC,MARBLE, MUSGRAVE,STUCCI,VORONOI, WOOD
        luxTransform = getattr(texture.pbrtv3_texture, 'pbrtv3_tex_transform')

        if luxTransform.coordinates == 'uv':
            self.properties.Set(pyluxcore.Property(prefix + '.mapping.type', 'uvmapping3d'))
        elif luxTransform.coordinates == 'global':
            self.properties.Set(pyluxcore.Property(prefix + '.mapping.type', 'globalmapping3d'))
        elif luxTransform.coordinates == 'local':
            self.properties.Set(pyluxcore.Property(prefix + '.mapping.type', 'localmapping3d'))
        elif luxTransform.coordinates == 'smoke_domain':
            self.properties.Set(pyluxcore.Property(prefix + '.mapping.type', 'globalmapping3d'))            
        else:
            raise Exception('Unsupported mapping "%s" for texture "%s"' % (luxTransform.coordinates, texture.name))

        if luxTransform.coordinates == 'smoke_domain':
            #For correct densitygrid texture transformation use smoke domain bounding box
            tex = texture.pbrtv3_texture.pbrtv3_tex_densitygrid
            obj = bpy.context.scene.objects[tex.domain_object]
            
            luxScale = obj.dimensions
            luxTranslate = obj.matrix_world * mathutils.Vector([v for v in obj.bound_box[0]])
            luxRotate = obj.rotation_euler
        else:
            luxTranslate = getattr(texture.pbrtv3_texture.pbrtv3_tex_transform, 'translate')
            luxScale = getattr(texture.pbrtv3_texture.pbrtv3_tex_transform, 'scale')
            luxRotate = getattr(texture.pbrtv3_texture.pbrtv3_tex_transform, 'rotate')

        # create a location matrix
        tex_loc = mathutils.Matrix.Translation((luxTranslate))

        # create an identitiy matrix
        tex_sca = mathutils.Matrix()
        tex_sca[0][0] = luxScale[0]  # X
        tex_sca[1][1] = luxScale[1]  # Y
        tex_sca[2][2] = luxScale[2]  # Z

        # create a rotation matrix
        tex_rot0 = mathutils.Matrix.Rotation(math.radians(luxRotate[0]), 4, 'X')
        tex_rot1 = mathutils.Matrix.Rotation(math.radians(luxRotate[1]), 4, 'Y')
        tex_rot2 = mathutils.Matrix.Rotation(math.radians(luxRotate[2]), 4, 'Z')
        tex_rot = tex_rot0 * tex_rot1 * tex_rot2

        # combine transformations
        f_matrix = matrix_to_list(tex_loc * tex_rot * tex_sca, apply_worldscale=True, invert=True)

        self.properties.Set(pyluxcore.Property(prefix + '.mapping.transformation', f_matrix))


    def __convert_colorramp(self):
        if self.texture.use_color_ramp:
            ramp = self.texture.color_ramp
            ramp_luxcore_name = self.luxcore_name + '_colorramp'
            ramp_prefix = 'scene.textures.' + ramp_luxcore_name

            self.properties.Set(pyluxcore.Property(ramp_prefix + '.type', 'band'))
            self.properties.Set(pyluxcore.Property(ramp_prefix + '.amount', self.luxcore_name))
            self.properties.Set(pyluxcore.Property(ramp_prefix + '.offsets', len(ramp.elements)))

            if ramp.interpolation == 'CONSTANT':
                interpolation = 'none'
            elif ramp.interpolation == 'LINEAR':
                interpolation = 'linear'
            else:
                interpolation = 'cubic'

            self.properties.Set(pyluxcore.Property(ramp_prefix + '.interpolation', interpolation))

            for i in range(len(ramp.elements)):
                position = ramp.elements[i].position
                color = list(ramp.elements[i].color[:3])  # Ignore alpha
                self.properties.Set(pyluxcore.Property(ramp_prefix + '.offset%d' % i, position))
                self.properties.Set(pyluxcore.Property(ramp_prefix + '.value%d' % i, color))

            self.luxcore_name = ramp_luxcore_name


    def __generate_texture_name(self, name):
        if self.texture.library:
            name += '_' + self.texture.library.name

        self.luxcore_name = ToValidPBRTv3CoreName(name)


    def __convert_texture(self, name=''):
        texture = self.texture

        texType = texture.pbrtv3_texture.type

        if name == '':
            self.__generate_texture_name(texture.name)
        else:
            self.__generate_texture_name(name)

        prefix = 'scene.textures.' + self.luxcore_name

        if texType == 'BLENDER':
            bl_texType = getattr(texture, 'type')

            # ###################################################################
            # BLEND
            ####################################################################
            if bl_texType == 'BLEND':
                self.properties.Set(pyluxcore.Property(prefix + '.type', ['blender_blend']))
                self.properties.Set(pyluxcore.Property(prefix + '.progressiontype',
                                             ''.join(str(i).lower() for i in getattr(texture, 'progression'))))
                self.properties.Set(pyluxcore.Property(prefix + '.direction',
                                             ''.join(str(i).lower() for i in getattr(texture, 'use_flip_axis'))))
            ####################################################################
            # CLOUDS
            ####################################################################
            elif bl_texType == 'CLOUDS':
                self.properties.Set(pyluxcore.Property(prefix + '.type', ['blender_clouds']))
                self.properties.Set(pyluxcore.Property(prefix + '.noisetype',
                                             ''.join(str(i).lower() for i in getattr(texture, 'noise_type'))))
                self.properties.Set(pyluxcore.Property(prefix + '.noisebasis',
                                             ''.join(str(i).lower() for i in getattr(texture, 'noise_basis'))))
                self.properties.Set(pyluxcore.Property(prefix + '.noisesize', [float(texture.noise_scale)]))
                self.properties.Set(pyluxcore.Property(prefix + '.noisedepth', [float(texture.noise_depth)]))
            ####################################################################
            # Distorted Noise
            ####################################################################
            elif bl_texType == 'DISTORTED_NOISE':
                self.properties.Set(pyluxcore.Property(prefix + '.type', ['blender_distortednoise']))
                self.properties.Set(pyluxcore.Property(prefix + '.noise_distortion',
                                             ''.join(str(i).lower() for i in getattr(texture, 'noise_distortion'))))
                self.properties.Set(pyluxcore.Property(prefix + '.noisebasis',
                                             ''.join(str(i).lower() for i in getattr(texture, 'noise_basis'))))
                self.properties.Set(pyluxcore.Property(prefix + '.noisesize', [float(texture.noise_scale)]))
                self.properties.Set(pyluxcore.Property(prefix + '.distortion', [float(texture.distortion)]))
            ####################################################################
            # IMAGE/MOVIE/SEQUENCE
            ####################################################################
            elif bl_texType == 'IMAGE' and texture.image and texture.image.source in ['GENERATED', 'FILE', 'SEQUENCE']:
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                tex_image = temp_file.name

                if texture.image.source == 'GENERATED':
                    texture.image.save_render(tex_image, self.blender_scene)

                if texture.image.source == 'FILE':
                    if texture.image.packed_file:
                        texture.image.save_render(tex_image, self.blender_scene)
                    else:
                        if texture.library is not None:
                            f_path = efutil.filesystem_path(
                                bpy.path.abspath(texture.image.filepath, texture.library.filepath))
                        else:
                            f_path = efutil.filesystem_path(texture.image.filepath)

                        if not os.path.exists(f_path):
                            raise Exception(
                                'Image referenced in blender texture %s doesn\'t exist: %s' % (texture.name, f_path))

                        tex_image = efutil.filesystem_path(f_path)

                if texture.image.source == 'SEQUENCE':
                    if texture.image.packed_file:
                        tex_image = 'luxblend_extracted_image_%s.%s' % (
                            bpy.path.clean_name(texture.name), self.blender_scene.render.image_settings.file_format)
                        tex_image = os.path.join(extract_path, tex_image)
                        texture.image.save_render(tex_image, self.blender_scene)
                    else:
                        # sequence params from blender
                        # remove tex_preview extension to avoid error
                        sequence = bpy.data.textures[(texture.name).replace('.001', '')].image_user
                        seqframes = sequence.frame_duration
                        seqoffset = sequence.frame_offset
                        seqstartframe = sequence.frame_start  # the global frame at which the imagesequence starts
                        seqcyclic = sequence.use_cyclic
                        currentframe = self.blender_scene.frame_current

                        if texture.library is not None:
                            f_path = efutil.filesystem_path(
                                bpy.path.abspath(texture.image.filepath, texture.library.filepath))
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
                                return 'ERR: Can\'t find pattern'

                            rightmost_number = m[len(m) - 1]
                            seq_length = len(rightmost_number)

                            nstr = '%i' % number
                            new_seq_number = nstr.zfill(seq_length)

                            return f_path.replace(rightmost_number, new_seq_number)

                        f_path = get_seq_filename(fnumber, f_path)

                        if not os.path.exists(f_path):
                            raise Exception(
                                'Image referenced in blender texture %s doesn\'t exist: %s' % (texture.name, f_path))
                        tex_image = efutil.filesystem_path(f_path)


                gamma = texture.pbrtv3_texture.pbrtv3_tex_imagesampling.gamma
                gain = texture.pbrtv3_texture.pbrtv3_tex_imagesampling.gain
                channel = texture.pbrtv3_texture.pbrtv3_tex_imagesampling.channel_luxcore

                self.properties.Set(pyluxcore.Property(prefix + '.type', ['imagemap']))
                self.properties.Set(pyluxcore.Property(prefix + '.file', [tex_image]))
                self.properties.Set(pyluxcore.Property(prefix + '.gamma', gamma))
                self.properties.Set(pyluxcore.Property(prefix + '.gain', gain))
                self.properties.Set(pyluxcore.Property(prefix + '.channel', channel))

                self.__convert_mapping(prefix, texture)
            ####################################################################
            # MAGIC
            ####################################################################
            elif bl_texType == 'MAGIC':
                self.properties.Set(pyluxcore.Property(prefix + '.type', ['blender_magic']))
                self.properties.Set(pyluxcore.Property(prefix + '.turbulence', [float(texture.turbulence)]))
                self.properties.Set(pyluxcore.Property(prefix + '.noisedepth', [float(texture.noise_depth)]))
            ####################################################################
            # MARBLE
            ####################################################################
            elif bl_texType == 'MARBLE':
                self.properties.Set(pyluxcore.Property(prefix + '.type', ['blender_marble']))
                self.properties.Set(pyluxcore.Property(prefix + '.marbletype',
                                             ''.join(str(i).lower() for i in getattr(texture, 'marble_type'))))
                self.properties.Set(pyluxcore.Property(prefix + '.noisebasis',
                                             ''.join(str(i).lower() for i in getattr(texture, 'noise_basis'))))
                self.properties.Set(pyluxcore.Property(prefix + '.noisebasis2',
                                             ''.join(str(i).lower() for i in getattr(texture, 'noise_basis_2'))))
                self.properties.Set(pyluxcore.Property(prefix + '.noisesize', [float(texture.noise_scale)]))
                self.properties.Set(pyluxcore.Property(prefix + '.noisedepth', [float(texture.noise_depth)]))
                self.properties.Set(pyluxcore.Property(prefix + '.turbulence', [float(texture.turbulence)]))
                self.properties.Set(pyluxcore.Property(prefix + '.noisetype',
                                             ''.join(str(i).lower() for i in getattr(texture, 'noise_type'))))
            ####################################################################
            # MUSGRAVE
            ####################################################################
            elif bl_texType == 'MUSGRAVE':
                self.properties.Set(pyluxcore.Property(prefix + '.type', ['blender_musgrave']))
                self.properties.Set(pyluxcore.Property(prefix + '.musgravetype',
                                             ''.join(str(i).lower() for i in getattr(texture, 'musgrave_type'))))
                self.properties.Set(pyluxcore.Property(prefix + '.noisebasis',
                                             ''.join(str(i).lower() for i in getattr(texture, 'noise_basis'))))
                self.properties.Set(pyluxcore.Property(prefix + '.dimension', [float(texture.dimension_max)]))
                self.properties.Set(pyluxcore.Property(prefix + '.intensity', [float(texture.noise_intensity)]))
                self.properties.Set(pyluxcore.Property(prefix + '.lacunarity', [float(texture.lacunarity)]))
                self.properties.Set(pyluxcore.Property(prefix + '.offset', [float(texture.offset)]))
                self.properties.Set(pyluxcore.Property(prefix + '.gain', [float(texture.gain)]))
                self.properties.Set(pyluxcore.Property(prefix + '.octaves', [float(texture.octaves)]))
                self.properties.Set(pyluxcore.Property(prefix + '.dimension', [float(texture.noise_scale)]))
                self.properties.Set(pyluxcore.Property(prefix + '.noisesize', [float(texture.noise_scale)]))
            # Not in blender:
            # self.properties.Set(pyluxcore.Property(prefix + '.noisetype', ''.join(str(i).lower() for i in getattr(texture, 'noise_type'))))
            ####################################################################
            # NOISE
            ####################################################################
            elif bl_texType == 'NOISE':
                self.properties.Set(pyluxcore.Property(prefix + '.type', ['blender_noise']))
                self.properties.Set(pyluxcore.Property(prefix + '.noisedepth', [float(texture.noise_depth)]))
            ####################################################################
            # STUCCI
            ####################################################################
            elif bl_texType == 'STUCCI':
                self.properties.Set(pyluxcore.Property(prefix + '.type', ['blender_stucci']))
                self.properties.Set(pyluxcore.Property(prefix + '.stuccitype',
                                             ''.join(str(i).lower() for i in getattr(texture, 'stucci_type'))))
                self.properties.Set(pyluxcore.Property(prefix + '.noisebasis',
                                             ''.join(str(i).lower() for i in getattr(texture, 'noise_basis'))))
                self.properties.Set(pyluxcore.Property(prefix + '.noisetype',
                                             ''.join(str(i).lower() for i in getattr(texture, 'noise_type'))))
                self.properties.Set(pyluxcore.Property(prefix + '.noisesize', [float(texture.noise_scale)]))
                self.properties.Set(pyluxcore.Property(prefix + '.turbulence', [float(texture.turbulence)]))
            ####################################################################
            # VORONOI
            ####################################################################
            elif bl_texType == 'VORONOI':
                self.properties.Set(pyluxcore.Property(prefix + '.type', ['blender_voronoi']))
                self.properties.Set(pyluxcore.Property(prefix + '.dismetric',
                                             ''.join(str(i).lower() for i in getattr(texture, 'distance_metric'))))
                # Not yet in luxcore:
                #self.properties.Set(pyluxcore.Property(prefix + '.colormode', ''.join(str(i).lower() for i in getattr(texture, 'color_mode'))))
                self.properties.Set(pyluxcore.Property(prefix + '.intensity', [float(texture.noise_intensity)]))
                self.properties.Set(pyluxcore.Property(prefix + '.exponent', [float(texture.minkovsky_exponent)]))
                self.properties.Set(pyluxcore.Property(prefix + '.w1', [float(texture.weight_1)]))
                self.properties.Set(pyluxcore.Property(prefix + '.w2', [float(texture.weight_2)]))
                self.properties.Set(pyluxcore.Property(prefix + '.w3', [float(texture.weight_3)]))
                self.properties.Set(pyluxcore.Property(prefix + '.w4', [float(texture.weight_4)]))
                self.properties.Set(pyluxcore.Property(prefix + '.noisesize', [float(texture.noise_scale)]))
            ####################################################################
            # WOOD
            ####################################################################
            elif bl_texType == 'WOOD':
                self.properties.Set(pyluxcore.Property(prefix + '.type', ['blender_wood']))
                self.properties.Set(pyluxcore.Property(prefix + '.woodtype',
                                             ''.join(str(i).lower() for i in getattr(texture, 'wood_type'))))
                self.properties.Set(pyluxcore.Property(prefix + '.noisebasis2',
                                             ''.join(str(i).lower() for i in getattr(texture, 'noise_basis_2'))))
                self.properties.Set(pyluxcore.Property(prefix + '.noisetype',
                                             ''.join(str(i).lower() for i in getattr(texture, 'noise_type'))))
                self.properties.Set(pyluxcore.Property(prefix + '.noisesize', [float(texture.noise_scale)]))
                self.properties.Set(pyluxcore.Property(prefix + '.turbulence', [float(texture.turbulence)]))
            ####################################################################
            # Parameters shared by all blender textures
            ####################################################################
            if bl_texType != 'IMAGE':
                # bright/contrast are not supported by PBRTv3Core imagemaps
                self.properties.Set(pyluxcore.Property(prefix + '.bright', [float(texture.intensity)]))
                self.properties.Set(pyluxcore.Property(prefix + '.contrast', [float(texture.contrast)]))
                self.__convert_transform(prefix, texture)

            self.__convert_colorramp()
            return

        elif texType != 'BLENDER':
            luxTex = getattr(texture.pbrtv3_texture, 'pbrtv3_tex_' + texType)

            ####################################################################
            # ADD/SUBTRACT
            ####################################################################
            if texType in ('add', 'subtract'):
                tex1 = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxTex, 'tex1', luxTex.variant)
                tex2 = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxTex, 'tex2', luxTex.variant)
                self.properties.Set(pyluxcore.Property(prefix + '.texture1', tex1))
                self.properties.Set(pyluxcore.Property(prefix + '.texture2', tex2))
            ####################################################################
            # BAND
            ####################################################################
            elif texType == 'band':
                if luxTex.variant != 'fresnel':
                    amount = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxTex, 'amount', 'float')
                    # Create all sub-texture definitions before the band texture definition
                    values = []
                    for i in range(luxTex.noffsets):
                        values.append(convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxTex, 'tex%s' % str(i + 1), luxTex.variant))

                    self.properties.Set(pyluxcore.Property(prefix + '.amount', amount))
                    self.properties.Set(pyluxcore.Property(prefix + '.offsets', [(luxTex.noffsets)]))

                    for i in range(luxTex.noffsets):
                        self.properties.Set(pyluxcore.Property(prefix + '.offset%d' % i,
                                                     [float(getattr(luxTex, 'offset%s%s' % (luxTex.variant, str(i + 1))))]))

                        value = values[i]

                        if isinstance(value, str):
                            # PBRTv3Core currently does not support textured values, set color to black
                            print('WARNING: PBRTv3Core does not support textured values in the band texture, '
                                  'using black color instead (texture: "%s")' % texture.name)
                            value = [0] * 3

                        if len(value) == 1:
                            value = [value[0]] * 3

                        self.properties.Set(pyluxcore.Property(prefix + '.value%d' % i, value))
                        i += 1
                else:
                    print('WARNING: Unsupported variant %s for texture: %s' % (luxTex.variant, texture.name))
            ####################################################################
            # BLACKBODY
            ####################################################################
            elif texType == 'blackbody':
                self.properties.Set(pyluxcore.Property(prefix + '.temperature', [float(luxTex.temperature)]))
            ####################################################################
            # Brick
            ####################################################################
            elif texType == 'brick':
                bricktex = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxTex, 'bricktex', luxTex.variant)
                brickmodtex = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxTex, 'brickmodtex', luxTex.variant)
                mortartex = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxTex, 'mortartex', luxTex.variant)

                self.properties.Set(pyluxcore.Property(prefix + '.brickbond', [(luxTex.brickbond)]))

                if texture.pbrtv3_texture.pbrtv3_tex_brick.brickbond in ('running', 'flemish'):
                    self.properties.Set(pyluxcore.Property(prefix + '.brickrun', [float(luxTex.brickrun)]))

                self.properties.Set(pyluxcore.Property(prefix + '.mortarsize', [float(luxTex.mortarsize)]))
                self.properties.Set(pyluxcore.Property(prefix + '.brickwidth', [float(luxTex.brickwidth)]))
                self.properties.Set(pyluxcore.Property(prefix + '.brickdepth', [float(luxTex.brickdepth)]))
                self.properties.Set(pyluxcore.Property(prefix + '.brickheight', [float(luxTex.brickheight)]))
                self.properties.Set(pyluxcore.Property(prefix + '.bricktex', bricktex))
                self.properties.Set(pyluxcore.Property(prefix + '.brickmodtex', brickmodtex))
                self.properties.Set(pyluxcore.Property(prefix + '.mortartex', mortartex))
                self.__convert_transform(prefix, texture)
            ####################################################################
            # CHECKERBOARD
            ####################################################################
            elif texType == 'checkerboard':
                # self.properties.Set(pyluxcore.Property(prefix + '.aamode', [float(luxTex.aamode)])) # not yet in luxcore
                tex1 = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxTex, 'tex1', 'float')
                tex2 = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxTex, 'tex2', 'float')
                self.properties.Set(pyluxcore.Property(prefix + '.texture1', tex1))
                self.properties.Set(pyluxcore.Property(prefix + '.texture2', tex2))
                if texture.pbrtv3_texture.pbrtv3_tex_checkerboard.dimension == 2:
                    self.properties.Set(pyluxcore.Property(prefix + '.type', ['checkerboard2d']))
                    self.__convert_mapping(prefix, texture)
                else:
                    self.properties.Set(pyluxcore.Property(prefix + '.type', ['checkerboard3d']))
                    self.__convert_transform(prefix, texture)
            ####################################################################
            # CLOUD
            ####################################################################
            elif texType == 'cloud':
                self.properties.Set(pyluxcore.Property(prefix + '.radius', [float(luxTex.radius)]))
                self.properties.Set(pyluxcore.Property(prefix + '.noisescale', [float(luxTex.noisescale)]))
                self.properties.Set(pyluxcore.Property(prefix + '.turbulence', [float(luxTex.turbulence)]))
                self.properties.Set(pyluxcore.Property(prefix + '.sharpness', [float(luxTex.sharpness)]))
                self.properties.Set(pyluxcore.Property(prefix + '.noiseoffset', [float(luxTex.noiseoffset)]))
                self.properties.Set(pyluxcore.Property(prefix + '.spheres', [luxTex.spheres]))
                self.properties.Set(pyluxcore.Property(prefix + '.octaves', [luxTex.octaves]))
                self.properties.Set(pyluxcore.Property(prefix + '.omega', [float(luxTex.omega)]))
                self.properties.Set(pyluxcore.Property(prefix + '.variability', [float(luxTex.variability)]))
                self.properties.Set(pyluxcore.Property(prefix + '.baseflatness', [float(luxTex.baseflatness)]))
                self.properties.Set(pyluxcore.Property(prefix + '.spheresize', [float(luxTex.spheresize)]))
                self.__convert_transform(prefix, texture)
            ####################################################################
            # CONSTANT
            ####################################################################
            elif texType == 'constant':
                if luxTex.variant == 'color':
                    self.properties.Set(pyluxcore.Property(prefix + '.type', ['constfloat3']))
                    self.properties.Set(pyluxcore.Property(prefix + '.value',
                                                 [luxTex.colorvalue[0], luxTex.colorvalue[1], luxTex.colorvalue[2]]))
                elif luxTex.variant == 'float':
                    self.properties.Set(pyluxcore.Property(prefix + '.type', ['constfloat1']))
                    self.properties.Set(pyluxcore.Property(prefix + '.value', [float(luxTex.floatvalue)]))
                else:
                    print('WARNING: Unsupported variant %s for texture: %s' % (luxTex.variant, texture.name))
            ####################################################################
            # DOTS
            ####################################################################
            elif texType == 'dots':
                inside = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxTex, 'inside', 'float')
                outside = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxTex, 'outside', 'float')
                self.properties.Set(pyluxcore.Property(prefix + '.inside', inside))
                self.properties.Set(pyluxcore.Property(prefix + '.outside', outside))
                self.__convert_mapping(prefix, texture)
            ####################################################################
            # FBM
            ####################################################################
            elif texType == 'fbm':
                self.properties.Set(pyluxcore.Property(prefix + '.octaves', [float(luxTex.octaves)]))
                self.properties.Set(pyluxcore.Property(prefix + '.roughness', [float(luxTex.roughness)]))
                self.__convert_transform(prefix, texture)
            ####################################################################
            # IMAGEMAP
            ####################################################################
            elif texType == 'imagemap':
                full_name, base_name = get_expanded_file_name(texture, luxTex.filename)
                self.properties.Set(pyluxcore.Property(prefix + '.file', full_name))
                self.properties.Set(pyluxcore.Property(prefix + '.gamma', [float(luxTex.gamma)]))
                self.properties.Set(pyluxcore.Property(prefix + '.gain', [float(luxTex.gain)]))
                if luxTex.variant == 'float':
                    self.properties.Set(pyluxcore.Property(prefix + '.channel', [(luxTex.channel)]))
                self.__convert_mapping(prefix, texture)
            ####################################################################
            # LAMPSPECTRUM
            ####################################################################
            elif texType == 'lampspectrum':
                self.properties.Set(pyluxcore.Property(prefix + '.name', [luxTex.preset]))
            ####################################################################
            # Normalmap
            ####################################################################
            elif texType == 'normalmap':
                full_name, base_name = get_expanded_file_name(texture, luxTex.filename)
                self.properties.Set(pyluxcore.Property(prefix + '.file', full_name))
                self.__convert_mapping(prefix, texture)
            ####################################################################
            # Marble
            ####################################################################
            elif texType == 'marble':
                self.properties.Set(pyluxcore.Property(prefix + '.octaves', [float(luxTex.octaves)]))
                self.properties.Set(pyluxcore.Property(prefix + '.roughness', [float(luxTex.roughness)]))
                self.properties.Set(pyluxcore.Property(prefix + '.scale', [float(luxTex.scale)]))
                self.properties.Set(pyluxcore.Property(prefix + '.variation', [float(luxTex.variation)]))
                self.__convert_transform(prefix, texture)
            ####################################################################
            # Mix
            ####################################################################
            elif texType == 'mix':
                amount = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxTex, 'amount', 'float')
                tex1 = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxTex, 'tex1', luxTex.variant)
                tex2 = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxTex, 'tex2', luxTex.variant)

                self.properties.Set(pyluxcore.Property(prefix + '.amount', amount))
                self.properties.Set(pyluxcore.Property(prefix + '.texture1', tex1))
                self.properties.Set(pyluxcore.Property(prefix + '.texture2', tex2))
            ####################################################################
            # Scale
            ####################################################################
            elif texType == 'scale':
                tex1 = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxTex, 'tex1', luxTex.variant)
                tex2 = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxTex, 'tex2', luxTex.variant)
                self.properties.Set(pyluxcore.Property(prefix + '.texture1', tex1))
                self.properties.Set(pyluxcore.Property(prefix + '.texture2', tex2))
            ####################################################################
            # UV
            ####################################################################
            elif texType == 'uv':
                self.__convert_mapping(prefix, texture)
            ####################################################################
            # WINDY
            ####################################################################
            elif texType == 'windy':
                self.__convert_transform(prefix, texture)
            ####################################################################
            # WRINKLED
            ####################################################################
            elif texType == 'wrinkled':
                self.properties.Set(pyluxcore.Property(prefix + '.octaves', [float(luxTex.octaves)]))
                self.properties.Set(pyluxcore.Property(prefix + '.roughness', [float(luxTex.roughness)]))
                self.__convert_transform(prefix, texture)
            ####################################################################
            # Vertex Colors
            ####################################################################
            elif texType in ['hitpointcolor', 'hitpointgrey', 'hitpointalpha']:
                pass
            ####################################################################
            # Fresnel color
            ####################################################################
            elif texType == 'fresnelcolor':
                self.properties.Set(pyluxcore.Property(prefix + '.kr', convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxTex, 'Kr', 'color')))
            ####################################################################
            # Fresnel preset (name)
            ####################################################################
            elif texType == 'fresnelname':
                self.properties.Set(pyluxcore.Property(prefix + '.type', 'fresnelpreset'))
                self.properties.Set(pyluxcore.Property(prefix + '.name', luxTex.name))
            ####################################################################
            # Fresnel sopra
            ####################################################################
            elif texType == 'sopra':
                self.properties.Set(pyluxcore.Property(prefix + '.type', 'fresnelsopra'))
                full_name, base_name = get_expanded_file_name(texture, luxTex.filename)
                self.properties.Set(pyluxcore.Property(prefix + '.file', full_name))
            ####################################################################
            # Fresnel luxpop
            ####################################################################
            elif texType == 'luxpop':
                self.properties.Set(pyluxcore.Property(prefix + '.type', 'fresnelluxpop'))
                full_name, base_name = get_expanded_file_name(texture, luxTex.filename)
                self.properties.Set(pyluxcore.Property(prefix + '.file', full_name))
            ####################################################################
            # Pointiness (hitpointalpha texture behind the scenes, just that it
            #            implicitly enables pointiness calculation on the mesh)
            ####################################################################
            elif texType == 'pointiness':
                self.properties.Set(pyluxcore.Property(prefix + '.type', 'hitpointalpha'))

                if luxTex.curvature_mode == 'both':
                    name_abs = self.luxcore_name + '_abs'
                    self.properties.Set(pyluxcore.Property('scene.textures.' + name_abs + '.type', 'abs'))
                    self.properties.Set(pyluxcore.Property('scene.textures.' + name_abs + '.texture', self.luxcore_name))

                    self.luxcore_name = name_abs

                elif luxTex.curvature_mode == 'concave':
                    name_clamp = self.luxcore_name + '_clamp'
                    self.properties.Set(pyluxcore.Property('scene.textures.' + name_clamp + '.type', 'clamp'))
                    self.properties.Set(pyluxcore.Property('scene.textures.' + name_clamp + '.texture', self.luxcore_name))
                    self.properties.Set(pyluxcore.Property('scene.textures.' + name_clamp + '.min', 0.0))
                    self.properties.Set(pyluxcore.Property('scene.textures.' + name_clamp + '.max', 1.0))

                    self.luxcore_name = name_clamp

                elif luxTex.curvature_mode == 'convex':
                    name_flip = self.luxcore_name + '_flip'
                    self.properties.Set(pyluxcore.Property('scene.textures.' + name_flip + '.type', 'scale'))
                    self.properties.Set(pyluxcore.Property('scene.textures.' + name_flip + '.texture1', self.luxcore_name))
                    self.properties.Set(pyluxcore.Property('scene.textures.' + name_flip + '.texture2', -1.0))

                    name_clamp = self.luxcore_name + '_clamp'
                    self.properties.Set(pyluxcore.Property('scene.textures.' + name_clamp + '.type', 'clamp'))
                    self.properties.Set(pyluxcore.Property('scene.textures.' + name_clamp + '.texture', name_flip))
                    self.properties.Set(pyluxcore.Property('scene.textures.' + name_clamp + '.min', 0.0))
                    self.properties.Set(pyluxcore.Property('scene.textures.' + name_clamp + '.max', 1.0))

                    self.luxcore_name = name_clamp
            ####################################################################
            # Densitygrid
            ####################################################################
            elif texType == 'densitygrid':
                self.properties.Set(pyluxcore.Property(prefix + '.wrap', luxTex.wrapping))

                if SmokeCache.needs_update(self.blender_scene, luxTex.domain_object, luxTex.source):
                    grid = SmokeCache.convert(self.blender_scene, luxTex.domain_object, luxTex.source)
                    self.properties.Set(pyluxcore.Property(prefix + '.data', grid[3]))
                    self.properties.Set(pyluxcore.Property(prefix + '.nx', int(grid[0])))
                    self.properties.Set(pyluxcore.Property(prefix + '.ny', int(grid[1])))
                    self.properties.Set(pyluxcore.Property(prefix + '.nz', int(grid[2])))

                self.__convert_transform(prefix, texture)
            ####################################################################
            # HSV
            ####################################################################
            elif texType == 'hsv':
                input = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxTex, 'input', 'color')
                hue = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxTex, 'hue', 'float')
                saturation = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxTex, 'saturation', 'float')
                value = convert_texture_channel(self.luxcore_exporter, self.properties, self.luxcore_name, luxTex, 'value', 'float')

                self.properties.Set(pyluxcore.Property(prefix + '.texture', input))
                self.properties.Set(pyluxcore.Property(prefix + '.hue', hue))
                self.properties.Set(pyluxcore.Property(prefix + '.saturation', saturation))
                self.properties.Set(pyluxcore.Property(prefix + '.value', value))
            ####################################################################
            # Fallback to exception
            ####################################################################
            else:
                raise Exception('Unknown type ' + texType + ' for texture: ' + texture.name)

            if texType not in ('normalmap', 'checkerboard', 'constant', 'fresnelname', 'luxpop', 'sopra', 'pointiness'):
                self.properties.Set(pyluxcore.Property(prefix + '.type', texType))

            self.__convert_colorramp()
            return

        raise Exception('Unknown texture type: ' + texture.name)