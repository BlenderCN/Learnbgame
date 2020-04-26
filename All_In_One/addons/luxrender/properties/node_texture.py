# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Jens Verwiebe, Jason Clarke, Asbjørn Heid
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

import re

import bpy

from ..extensions_framework import declarative_property_group

from .. import LuxRenderAddon
from ..properties import (luxrender_texture_node, get_linked_node, check_node_export_texture, check_node_get_paramset)
from ..properties.texture import (
    import_paramset_to_blender_texture, shorten_name, refresh_preview
)
from ..export import ParamSet, get_worldscale, process_filepath_data
from ..export.volumes import export_smoke
from ..export.materials import (
    ExportedTextures, add_texture_parameter, get_texture_from_scene
)
from ..outputs import LuxManager, LuxLog

from ..properties.texture import (
    luxrender_tex_brick, luxrender_tex_imagemap, luxrender_tex_normalmap, luxrender_tex_transform, luxrender_tex_mapping
)
from ..properties.node_material import get_socket_paramsets

from ..properties.node_sockets import (
    luxrender_TF_brickmodtex_socket, luxrender_TF_bricktex_socket, luxrender_TF_mortartex_socket,
    luxrender_TC_brickmodtex_socket, luxrender_TC_bricktex_socket, luxrender_TC_mortartex_socket,
    luxrender_transform_socket, luxrender_coordinate_socket
)

# Define the list of noise types globally, this gets used by a few different nodes
noise_basis_items = [
    ('blender_original', 'Blender Original', ''),
    ('original_perlin', 'Original Perlin', ''),
    ('improved_perlin', 'Improved Perlin', ''),
    ('voronoi_f1', 'Voronoi F1', ''),
    ('voronoi_f2', 'Voronoi F2', ''),
    ('voronoi_f3', 'Voronoi F3', ''),
    ('voronoi_f4', 'Voronoi F4', ''),
    ('voronoi_f2f1', 'Voronoi F2-F1', ''),
    ('voronoi_crackle', 'Voronoi Crackle', ''),
    ('cell_noise', 'Cell Noise', ''),
]

noise_type_items = [
    ('soft_noise', 'Soft', ''),
    ('hard_noise', 'Hard', '')
]

variant_items = [
    ('color', 'Color', 'This node ouputs color data'),
    ('float', 'Float', 'This node outputs floating point data')
]

triple_variant_items = [
    ('color', 'Color', 'This node ouputs color data'),
    ('float', 'Float', 'This node outputs floating point data'),
    ('fresnel', 'Fresnel', 'This node outputs an optical dataset')
]


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_blender_blend(luxrender_texture_node):
    """Blend texture node"""
    bl_idname = 'luxrender_texture_blender_blend_node'
    bl_label = 'Blend Texture'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    progression_items = [
        ('lin', 'Linear', 'linear'),
        ('quad', 'Quadratic', 'quadratic'),
        ('ease', 'Easing', 'easing'),
        ('diag', 'Diagonal', 'diagonal'),
        ('sphere', 'Spherical', 'spherical'),
        ('halo', 'Quadratic Sphere', 'quadratic sphere'),
        ('radial', 'Radial', 'radial'),
    ]

    flipxy = bpy.props.BoolProperty(name='Flip XY', description='Switch between horizontal and linear gradient',
                                    default=False)
    type = bpy.props.EnumProperty(name='Progression', description='progression', items=progression_items, default='lin')
    bright = bpy.props.FloatProperty(name='Brightness', default=1.0)
    contrast = bpy.props.FloatProperty(name='Contrast', default=1.0)

    def init(self, context):
        self.inputs.new('luxrender_coordinate_socket', '3D Coordinate')
        self.outputs.new('NodeSocketFloat', 'Float')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'flipxy')
        layout.prop(self, 'type')
        layout.prop(self, 'bright')
        layout.prop(self, 'contrast')

    def export_texture(self, make_texture):
        blend_params = ParamSet() \
            .add_bool('flipxy', self.flipxy) \
            .add_string('type', self.type) \
            .add_float('bright', self.bright) \
            .add_float('contrast', self.contrast)

        coord_node = get_linked_node(self.inputs[0])

        if coord_node and check_node_get_paramset(coord_node):
            blend_params.update(coord_node.get_paramset())

        return make_texture('float', 'blender_blend', self.name, blend_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_brick(luxrender_texture_node):
    """Brick texture node"""
    bl_idname = 'luxrender_texture_brick_node'
    bl_label = 'Brick Texture'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    for prop in luxrender_tex_brick.properties:
        if prop['attr'].startswith('brickbond'):
            brickbond_items = prop['items']

    variant = bpy.props.EnumProperty(name='Variant', items=variant_items, default='color')
    brickbond = bpy.props.EnumProperty(name='Bond Type', items=brickbond_items, default='running')
    brickrun = bpy.props.FloatProperty(name='Brick Run', default=0.5, subtype='PERCENTAGE')
    mortarsize = bpy.props.FloatProperty(name='Mortar Size', description='Width of mortar segments', default=0.01,
                                         subtype='DISTANCE', unit='LENGTH')
    width = bpy.props.FloatProperty(name='Width', default=0.3, subtype='DISTANCE', unit='LENGTH')
    depth = bpy.props.FloatProperty(name='Depth', default=0.15, subtype='DISTANCE', unit='LENGTH')
    height = bpy.props.FloatProperty(name='Height', default=0.10, subtype='DISTANCE', unit='LENGTH')

    def init(self, context):
        self.inputs.new('luxrender_coordinate_socket', '3D Coordinate')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'variant')
        layout.prop(self, 'brickbond')
        layout.prop(self, 'brickrun')
        layout.prop(self, 'mortarsize')
        layout.prop(self, 'width')
        layout.prop(self, 'depth')
        layout.prop(self, 'height')

        si = self.inputs.keys()
        so = self.outputs.keys()

        if self.variant == 'color':
            if not 'Brick Color' in si:  # If there aren't color inputs, create them
                self.inputs.new('luxrender_TC_brickmodtex_socket', 'Brick Modulation Color')
                self.inputs.new('luxrender_TC_bricktex_socket', 'Brick Color')
                self.inputs.new('luxrender_TC_mortartex_socket', 'Mortar Color')

            if 'Brick Value' in si:  # If there are float inputs, destory them
                self.inputs.remove(self.inputs['Brick Modulation Value'])
                self.inputs.remove(self.inputs['Brick Value'])
                self.inputs.remove(self.inputs['Mortar Value'])

            if not 'Color' in so:  # If there is no color output, create it
                self.outputs.new('NodeSocketColor', 'Color')

            if 'Float' in so:  # If there is a float output, destroy it
                self.outputs.remove(self.outputs['Float'])

        if self.variant == 'float':
            if not 'Brick Value' in si:
                self.inputs.new('luxrender_TF_brickmodtex_socket', 'Brick Modulation Value')
                self.inputs.new('luxrender_TF_bricktex_socket', 'Brick Value')
                self.inputs.new('luxrender_TF_mortartex_socket', 'Mortar Value')

            if 'Brick Color' in si:
                self.inputs.remove(self.inputs['Brick Modulation Color'])
                self.inputs.remove(self.inputs['Brick Color'])
                self.inputs.remove(self.inputs['Mortar Color'])

            if not 'Float' in so:
                self.outputs.new('NodeSocketFloat', 'Float')

            if 'Color' in so:
                self.outputs.remove(self.outputs['Color'])

    def export_texture(self, make_texture):
        brick_params = ParamSet() \
            .add_string('brickbond', self.brickbond) \
            .add_float('brickrun', self.brickrun) \
            .add_float('mortarsize', self.mortarsize) \
            .add_float('brickwidth', self.width) \
            .add_float('brickdepth', self.depth) \
            .add_float('brickheight', self.height)

        coord_node = get_linked_node(self.inputs[0])

        if coord_node and check_node_get_paramset(coord_node):
            brick_params.update(coord_node.get_paramset())

        brick_params.update(get_socket_paramsets(self.inputs, make_texture))

        return make_texture(self.variant, 'brick', self.name, brick_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_blender_clouds(luxrender_texture_node):
    """Clouds texture node"""
    bl_idname = 'luxrender_texture_blender_clouds_node'
    bl_label = 'Clouds Texture'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    noisetype = bpy.props.EnumProperty(name='Noise Type', description='Soft or hard noise', items=noise_type_items,
                                       default='soft_noise')
    noisebasis = bpy.props.EnumProperty(name='Noise Basis', description='Type of noise used', items=noise_basis_items,
                                        default='blender_original')
    noisesize = bpy.props.FloatProperty(name='Noise Size', default=0.25)
    noisedepth = bpy.props.IntProperty(name='Noise Depth', default=2)
    bright = bpy.props.FloatProperty(name='Brightness', default=1.0)
    contrast = bpy.props.FloatProperty(name='Contrast', default=1.0)

    def init(self, context):
        self.inputs.new('luxrender_coordinate_socket', '3D Coordinate')
        self.outputs.new('NodeSocketFloat', 'Float')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'noisetype')
        layout.prop(self, 'noisebasis')
        layout.prop(self, 'noisesize')
        layout.prop(self, 'noisedepth')
        layout.prop(self, 'bright')
        layout.prop(self, 'contrast')

    def export_texture(self, make_texture):
        clouds_params = ParamSet() \
            .add_string('noisetype', self.noisetype) \
            .add_string('noisebasis', self.noisebasis) \
            .add_float('noisesize', self.noisesize) \
            .add_integer('noisedepth', self.noisedepth) \
            .add_float('bright', self.bright) \
            .add_float('contrast', self.contrast)

        coord_node = get_linked_node(self.inputs[0])

        if coord_node and check_node_get_paramset(coord_node):
            clouds_params.update(coord_node.get_paramset())

        return make_texture('float', 'blender_clouds', self.name, clouds_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_blender_distortednoise(luxrender_texture_node):
    """Distorted noise texture node"""
    bl_idname = 'luxrender_texture_blender_distortednoise_node'
    bl_label = 'Distorted Noise Texture'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    noisebasis = bpy.props.EnumProperty(name='Noise Basis', description='Type of noise used', items=noise_basis_items,
                                        default='blender_original')
    type = bpy.props.EnumProperty(name='Noise Basis', description='Type of noise used', items=noise_basis_items,
                                  default='blender_original')
    distamount = bpy.props.FloatProperty(name='Distortion', default=1.00)
    noisesize = bpy.props.FloatProperty(name='Noise Size', default=0.25)
    nabla = bpy.props.FloatProperty(name='Nabla', default=0.025)
    bright = bpy.props.FloatProperty(name='Brightness', default=1.0)
    contrast = bpy.props.FloatProperty(name='Contrast', default=1.0)

    def init(self, context):
        self.inputs.new('luxrender_coordinate_socket', '3D Coordinate')
        self.outputs.new('NodeSocketFloat', 'Float')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'noisebasis')
        layout.prop(self, 'type')
        layout.prop(self, 'distamount')
        layout.prop(self, 'noisesize')
        layout.prop(self, 'nabla')
        layout.prop(self, 'bright')
        layout.prop(self, 'contrast')

    def export_texture(self, make_texture):
        distortednoise_params = ParamSet() \
            .add_string('noisebasis', self.noisebasis) \
            .add_string('type', self.type) \
            .add_float('noisesize', self.noisesize) \
            .add_float('distamount', self.distamount) \
            .add_float('nabla', self.nabla) \
            .add_float('bright', self.bright) \
            .add_float('contrast', self.contrast)

        coord_node = get_linked_node(self.inputs[0])

        if coord_node and check_node_get_paramset(coord_node):
            distortednoise_params.update(coord_node.get_paramset())

        return make_texture('float', 'blender_distortednoise', self.name, distortednoise_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_fbm(luxrender_texture_node):
    """FBM texture node"""
    bl_idname = 'luxrender_texture_fbm_node'
    bl_label = 'FBM Texture'
    bl_icon = 'TEXTURE'
    bl_width_min = 160

    octaves = bpy.props.IntProperty(name='Octaves', default=8)
    roughness = bpy.props.FloatProperty(name='Roughness', default=0.5)

    def init(self, context):
        self.inputs.new('luxrender_coordinate_socket', '3D Coordinate')
        self.outputs.new('NodeSocketFloat', 'Float')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'octaves')
        layout.prop(self, 'roughness')

    def export_texture(self, make_texture):
        fbm_params = ParamSet() \
            .add_integer('octaves', self.octaves) \
            .add_float('roughness', self.roughness)

        coord_node = get_linked_node(self.inputs[0])

        if coord_node and check_node_get_paramset(coord_node):
            fbm_params.update(coord_node.get_paramset())

        return make_texture('float', 'fbm', self.name, fbm_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_harlequin(luxrender_texture_node):
    """Harlequin texture node"""
    bl_idname = 'luxrender_texture_harlequin_node'
    bl_label = 'Harlequin Texture'
    bl_icon = 'TEXTURE'

    def init(self, context):
        self.outputs.new('NodeSocketColor', 'Color')

    def export_texture(self, make_texture):
        harlequin_params = ParamSet()
        return make_texture('color', 'harlequin', self.name, harlequin_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_image_map(luxrender_texture_node):
    """Image map texture node"""
    bl_idname = 'luxrender_texture_image_map_node'
    bl_label = 'Image Map Texture'
    bl_icon = 'TEXTURE'
    bl_width_min = 220

    for prop in luxrender_tex_imagemap.properties:
        if prop['attr'].startswith('filtertype'):
            filter_items = prop['items']
        if prop['attr'].startswith('wrap'):
            wrap_items = prop['items']
        if prop['attr'].startswith('channel'):
            channel_items = prop['items']

    filename = bpy.props.StringProperty(name='File Name', description='Path to the normal map', subtype='FILE_PATH')
    variant = bpy.props.EnumProperty(name='Variant', items=variant_items, default='color')
    channel = bpy.props.EnumProperty(name='Channel', items=channel_items, default='mean')
    gamma = bpy.props.FloatProperty(name='Gamma', default=2.2, min=0.0, max=5.0)
    gain = bpy.props.FloatProperty(name='Gain', default=1.0, min=-10.0, max=10.0)
    filtertype = bpy.props.EnumProperty(name='Filter Type', description='Texture filtering method', items=filter_items,
                                        default='bilinear')
    wrap = bpy.props.EnumProperty(name='Wrapping', description='Texture wrapping method', items=wrap_items,
                                  default='repeat')
    maxanisotropy = bpy.props.FloatProperty(name='Max Anisotropy', default=8.0)
    discardmipmaps = bpy.props.IntProperty(name='Discard Mipmaps', default=1)


    def init(self, context):
        self.inputs.new('luxrender_transform_socket', '2D Coordinate')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'filename')
        layout.prop(self, 'variant')

        if self.variant == 'float':
            layout.prop(self, 'channel')

        layout.prop(self, 'gamma')
        layout.prop(self, 'gain')
        layout.prop(self, 'filtertype')

        if self.filtertype in ('mipmap_trilinear', 'mipmap_ewa'):
            layout.prop(self, 'maxanisotropy')
            layout.prop(self, 'discardmipmaps')

        layout.prop(self, 'wrap')

        s = self.outputs.keys()

        if self.variant == 'color':
            if not 'Color' in s:
                self.outputs.new('NodeSocketColor', 'Color')
            if 'Float' in s:
                self.outputs.remove(self.outputs['Float'])

        if self.variant == 'float':
            if not 'Float' in s:
                self.outputs.new('NodeSocketFloat', 'Float')
            if 'Color' in s:
                self.outputs.remove(self.outputs['Color'])

    def export_texture(self, make_texture):
        imagemap_params = ParamSet()
        process_filepath_data(LuxManager.CurrentScene, self, self.filename, imagemap_params, 'filename')

        if self.variant == 'float':
            imagemap_params.add_string('channel', self.channel)

        imagemap_params.add_string('filtertype', self.filtertype)
        imagemap_params.add_float('gain', self.gain)
        imagemap_params.add_float('gamma', self.gamma)
        imagemap_params.add_string('wrap', self.wrap)

        if self.filtertype in ('mipmap_ewa', 'mipmap_trilinear'):
            imagemap_params.add_float('maxanisotropy', self.maxanisotropy)
            imagemap_params.add_integer('discardmipmaps', self.discardmipmaps)

        coord_node = get_linked_node(self.inputs[0])

        if coord_node and check_node_get_paramset(coord_node):
            imagemap_params.update(coord_node.get_paramset())
        else:
            imagemap_params.add_float('vscale', -1.0)

        return make_texture(self.variant, 'imagemap', self.name, imagemap_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_blender_marble(luxrender_texture_node):
    """Marble texture node"""
    bl_idname = 'luxrender_texture_blender_marble_node'
    bl_label = 'Marble Texture'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    marble_type_items = [
        ('soft', 'Soft', ''),
        ('sharp', 'Sharp', ''),
        ('sharper', 'Sharper', ''),
    ]

    marble_noise_items = [
        ('sin', 'Sin', ''),
        ('saw', 'Saw', ''),
        ('tri', 'Tri', ''),
    ]

    type = bpy.props.EnumProperty(name='Type', description='Type of noise used', items=marble_type_items,
                                  default='soft')
    noisebasis = bpy.props.EnumProperty(name='Noise Basis', description='Basis of noise used', items=noise_basis_items,
                                        default='blender_original')
    noisebasis2 = bpy.props.EnumProperty(name='Noise Basis 2', description='Second basis of noise used',
                                         items=marble_noise_items, default='sin')
    noisetype = bpy.props.EnumProperty(name='Noise Type', description='Soft or hard noise', items=noise_type_items,
                                       default='soft_noise')
    noisesize = bpy.props.FloatProperty(name='Noise Size', default=0.25)
    noisedepth = bpy.props.IntProperty(name='Noise Depth', default=2)
    turbulence = bpy.props.FloatProperty(name='Turbulence', default=5.0)
    bright = bpy.props.FloatProperty(name='Brightness', default=1.0)
    contrast = bpy.props.FloatProperty(name='Contrast', default=1.0)

    def init(self, context):
        self.inputs.new('luxrender_coordinate_socket', '3D Coordinate')
        self.outputs.new('NodeSocketFloat', 'Float')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'type')
        layout.prop(self, 'noisebasis')
        layout.prop(self, 'noisebasis2')
        layout.prop(self, 'noisetype')
        layout.prop(self, 'noisesize')
        layout.prop(self, 'noisedepth')
        layout.prop(self, 'turbulence')
        layout.prop(self, 'bright')
        layout.prop(self, 'contrast')

    def export_texture(self, make_texture):
        marble_params = ParamSet() \
            .add_string('type', self.type) \
            .add_string('noisebasis', self.noisebasis) \
            .add_string('noisebasis2', self.noisebasis2) \
            .add_string('noisetype', self.noisetype) \
            .add_float('noisesize', self.noisesize) \
            .add_integer('noisedepth', self.noisedepth) \
            .add_float('turbulence', self.turbulence) \
            .add_float('bright', self.bright) \
            .add_float('contrast', self.contrast)

        coord_node = get_linked_node(self.inputs[0])

        if coord_node and check_node_get_paramset(coord_node):
            marble_params.update(coord_node.get_paramset())

        return make_texture('float', 'blender_marble', self.name, marble_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_blender_musgrave(luxrender_texture_node):
    """Musgrave texture node"""
    bl_idname = 'luxrender_texture_blender_musgrave_node'
    bl_label = 'Musgrave Texture'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    musgrave_type_items = [
        ('multifractal', 'Multifractal', ''),
        ('ridged_multifractal', 'Ridged Multifractal', ''),
        ('hybrid_multifractal', 'Hybrid Multifractal', ''),
        ('hetero_terrain', 'Hetero Terrain', ''),
        ('fbm', 'FBM', ''),
    ]

    musgravetype = bpy.props.EnumProperty(name='Noise Type', description='Type of noise used',
                                          items=musgrave_type_items, default='multifractal')
    noisebasis = bpy.props.EnumProperty(name='Noise Basis', description='Basis of noise used', items=noise_basis_items,
                                        default='blender_original')
    noisesize = bpy.props.FloatProperty(name='Noise Size', default=0.25)
    h = bpy.props.FloatProperty(name='Dimension', default=1.0)
    lacu = bpy.props.FloatProperty(name='Lacunarity', default=2.0)
    octs = bpy.props.FloatProperty(name='Octaves', default=2.0)
    offset = bpy.props.FloatProperty(name='Offset', default=1.0)
    gain = bpy.props.FloatProperty(name='Gain', default=1.0)
    iscale = bpy.props.FloatProperty(name='Intensity', default=1.0)
    bright = bpy.props.FloatProperty(name='Brightness', default=1.0)
    contrast = bpy.props.FloatProperty(name='Contrast', default=1.0)

    def init(self, context):
        self.inputs.new('luxrender_coordinate_socket', '3D Coordinate')
        self.outputs.new('NodeSocketFloat', 'Float')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'musgravetype')
        layout.prop(self, 'noisebasis')
        layout.prop(self, 'noisesize')
        layout.prop(self, 'h')
        layout.prop(self, 'lacu')
        layout.prop(self, 'octs')

        if self.musgravetype in ('ridged_multifractal', 'hybrid_multifractal', 'hetero_terrain'):
            layout.prop(self, 'offset')

        if self.musgravetype in ('ridged_multifractal', 'hybrid_multifractal'):
            layout.prop(self, 'gain')

        if self.musgravetype != 'fbm':
            layout.prop(self, 'iscale')

        layout.prop(self, 'bright')
        layout.prop(self, 'contrast')

    def export_texture(self, make_texture):
        musgrave_params = ParamSet()
        musgrave_params.add_string('musgravetype', self.musgravetype)
        musgrave_params.add_string('noisebasis', self.noisebasis)
        musgrave_params.add_float('noisesize', self.noisesize)
        musgrave_params.add_float('h', self.h)
        musgrave_params.add_float('lacu', self.lacu)
        musgrave_params.add_float('octs', self.octs)

        if self.musgravetype in ('ridged_multifractal', 'hybrid_multifractal', 'hetero_terrain'):
            musgrave_params.add_float('offset', self.offset)

        if self.musgravetype in ('ridged_multifractal', 'hybrid_multifractal'):
            musgrave_params.add_float('gain', self.gain)

        if self.musgravetype != 'fbm':
            musgrave_params.add_float('iscale', self.iscale)

        musgrave_params.add_float('bright', self.bright)
        musgrave_params.add_float('contrast', self.contrast)

        coord_node = get_linked_node(self.inputs[0])

        if coord_node and check_node_get_paramset(coord_node):
            musgrave_params.update(coord_node.get_paramset())

        return make_texture('float', 'blender_musgrave', self.name, musgrave_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_normal_map(luxrender_texture_node):
    """Normal map texture node"""
    bl_idname = 'luxrender_texture_normal_map_node'
    bl_label = 'Normal Map Texture'
    bl_icon = 'TEXTURE'
    bl_width_min = 220

    for prop in luxrender_tex_normalmap.properties:
        if prop['attr'].startswith('filtertype'):
            filter_items = prop['items']
        if prop['attr'].startswith('wrap'):
            wrap_items = prop['items']

    filename = bpy.props.StringProperty(name='File Name', description='Path to the normal map', subtype='FILE_PATH')
    filtertype = bpy.props.EnumProperty(name='Filter Type', description='Texture filtering method', items=filter_items,
                                        default='bilinear')
    wrap = bpy.props.EnumProperty(name='Wrapping', description='Texture wrapping method', items=wrap_items,
                                  default='repeat')
    maxanisotropy = bpy.props.FloatProperty(name='Max Anisotropy', default=8.0)
    discardmipmaps = bpy.props.IntProperty(name='Discard Mipmaps', default=1)

    def init(self, context):
        self.inputs.new('luxrender_transform_socket', '2D Coordinate')
        self.outputs.new('NodeSocketFloat', 'Float')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'filename')
        layout.prop(self, 'filtertype')

        if self.filtertype in ('mipmap_trilinear', 'mipmap_ewa'):
            layout.prop(self, 'maxanisotropy')
            layout.prop(self, 'discardmipmaps')

        layout.prop(self, 'wrap')

    def export_texture(self, make_texture):
        normalmap_params = ParamSet()
        process_filepath_data(LuxManager.CurrentScene, self, self.filename, normalmap_params, 'filename')
        normalmap_params.add_string('filtertype', self.filtertype)
        normalmap_params.add_string('wrap', self.wrap)

        if self.filtertype in ('mipmap_ewa', 'mipmap_trilinear'):
            normalmap_params.add_float('maxanisotropy', self.maxanisotropy)
            normalmap_params.add_integer('discardmipmaps', self.discardmipmaps)

        coord_node = get_linked_node(self.inputs[0])

        if coord_node and check_node_get_paramset(coord_node):
            normalmap_params.update(coord_node.get_paramset())
        else:
            normalmap_params.add_float('vscale', -1.0)

        return make_texture('float', 'normalmap', self.name, normalmap_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_blender_stucci(luxrender_texture_node):
    """Stucci texture node"""
    bl_idname = 'luxrender_texture_blender_stucci_node'
    bl_label = 'Stucci Texture'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    stucci_type_items = [
        ('plastic', 'Plastic', ''),
        ('wall_in', 'Wall In', ''),
        ('wall_out', 'Wall Out', ''),
    ]

    type = bpy.props.EnumProperty(name='Type', description='Type of noise used', items=stucci_type_items,
                                  default='plastic')
    noisebasis = bpy.props.EnumProperty(name='Noise Basis', description='Basis of noise used', items=noise_basis_items,
                                        default='blender_original')
    noisetype = bpy.props.EnumProperty(name='Noise Type', description='Soft or hard noise', items=noise_type_items,
                                       default='soft_noise')
    noisesize = bpy.props.FloatProperty(name='Noise Size', default=0.25)
    turbulence = bpy.props.FloatProperty(name='Turbulence', default=5.0)
    bright = bpy.props.FloatProperty(name='Brightness', default=1.0)
    contrast = bpy.props.FloatProperty(name='Contrast', default=1.0)

    def init(self, context):
        self.inputs.new('luxrender_coordinate_socket', '3D Coordinate')
        self.outputs.new('NodeSocketFloat', 'Float')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'type')
        layout.prop(self, 'noisebasis')
        layout.prop(self, 'noisetype')
        layout.prop(self, 'noisesize')
        layout.prop(self, 'turbulence')
        layout.prop(self, 'bright')
        layout.prop(self, 'contrast')

    def export_texture(self, make_texture):
        stucci_params = ParamSet() \
            .add_string('type', self.type) \
            .add_string('noisebasis', self.noisebasis) \
            .add_string('noisetype', self.noisetype) \
            .add_float('noisesize', self.noisesize) \
            .add_float('turbulence', self.noisesize) \
            .add_float('bright', self.bright) \
            .add_float('contrast', self.contrast)

        coord_node = get_linked_node(self.inputs[0])

        if coord_node and check_node_get_paramset(coord_node):
            stucci_params.update(coord_node.get_paramset())

        return make_texture('float', 'blender_stucci', self.name, stucci_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_uv(luxrender_texture_node):
    """UV texture node"""
    bl_idname = 'luxrender_texture_uv_node'
    bl_label = 'UV Test Texture'
    bl_icon = 'TEXTURE'

    def init(self, context):
        self.inputs.new('luxrender_transform_socket', '2D Transform')

        self.outputs.new('NodeSocketColor', 'Color')

    def export_texture(self, make_texture):
        uvtest_params = ParamSet()
        coord_node = get_linked_node(self.inputs[0])

        if coord_node and check_node_get_paramset(coord_node):
            uvtest_params.update(coord_node.get_paramset())
        else:
            uvtest_params.add_float('vscale', -1.0)

        return make_texture('color', 'uv', self.name, uvtest_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_blender_voronoi(luxrender_texture_node):
    """Voronoi texture node"""
    bl_idname = 'luxrender_texture_blender_voronoi_node'
    bl_label = 'Voronoi Texture'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    distance_items = [
        ('actual_distance', 'Actual Distance', 'actual distance'),
        ('distance_squared', 'Distance Squared', 'distance squared'),
        ('manhattan', 'Manhattan', 'manhattan'),
        ('chebychev', 'Chebychev', 'chebychev'),
        ('minkovsky_half', 'Minkowsky 1/2', 'minkowsky half'),
        ('minkovsky_four', 'Minkowsky 4', 'minkowsky four'),
        ('minkovsky', 'Minkowsky', 'minkowsky'),
    ]

    distmetric = bpy.props.EnumProperty(name='Distance Metric',
                                        description='Algorithm used to calculate distance of sample points to feature points',
                                        items=distance_items, default='actual_distance')
    minkowsky_exp = bpy.props.FloatProperty(name='Exponent', default=1.0)
    noisesize = bpy.props.FloatProperty(name='Noise Size', default=0.25)
    nabla = bpy.props.FloatProperty(name='Nabla', default=0.025)
    w1 = bpy.props.FloatProperty(name='Weight 1', default=1.0, min=0.0, max=1.0, subtype='FACTOR')
    w2 = bpy.props.FloatProperty(name='Weight 2', default=0.0, min=0.0, max=1.0, subtype='FACTOR')
    w3 = bpy.props.FloatProperty(name='Weight 3', default=0.0, min=0.0, max=1.0, subtype='FACTOR')
    w4 = bpy.props.FloatProperty(name='Weight 4', default=0.0, min=0.0, max=1.0, subtype='FACTOR')
    bright = bpy.props.FloatProperty(name='Brightness', default=1.0)
    contrast = bpy.props.FloatProperty(name='Contrast', default=1.0)

    def init(self, context):
        self.inputs.new('luxrender_coordinate_socket', '3D Coordinate')
        self.outputs.new('NodeSocketFloat', 'Float')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'distmetric')
        layout.prop(self, 'minkowsky_exp')
        layout.prop(self, 'noisesize')
        layout.prop(self, 'nabla')
        layout.prop(self, 'w1')
        layout.prop(self, 'w2')
        layout.prop(self, 'w3')
        layout.prop(self, 'w4')
        layout.prop(self, 'bright')
        layout.prop(self, 'contrast')

    def export_texture(self, make_texture):
        voronoi_params = ParamSet() \
            .add_string('distmetric', self.distmetric) \
            .add_float('minkovsky_exp', self.minkowsky_exp) \
            .add_float('noisesize', self.noisesize) \
            .add_float('nabla', self.nabla) \
            .add_float('w1', self.w1) \
            .add_float('w2', self.w2) \
            .add_float('w3', self.w3) \
            .add_float('w4', self.w4) \
            .add_float('bright', self.bright) \
            .add_float('contrast', self.contrast)

        coord_node = get_linked_node(self.inputs[0])

        if coord_node and check_node_get_paramset(coord_node):
            voronoi_params.update(coord_node.get_paramset())

        return make_texture('float', 'blender_voronoi', self.name, voronoi_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_windy(luxrender_texture_node):
    """Windy texture node"""
    bl_idname = 'luxrender_texture_windy_node'
    bl_label = 'Windy Texture'
    bl_icon = 'TEXTURE'
    bl_width_min = 160

    def init(self, context):
        self.inputs.new('luxrender_coordinate_socket', '3D Coordinate')
        self.outputs.new('NodeSocketFloat', 'Float')

    def export_texture(self, make_texture):
        windy_params = ParamSet()

        coord_node = get_linked_node(self.inputs[0])

        if coord_node and check_node_get_paramset(coord_node):
            wrinkled_params.update(coord_node.get_paramset())

        return make_texture('float', 'windy', self.name, windy_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_blender_wood(luxrender_texture_node):
    """Wood texture node"""
    bl_idname = 'luxrender_texture_blender_wood_node'
    bl_label = 'Wood Texture'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    wood_type_items = [
        ('bands', 'Bands', ''),
        ('rings', 'Rings', ''),
        ('bandnoise', 'Band Noise', ''),
        ('ringnoise', 'Ring Noise', ''),
    ]

    wood_noise_items = [
        ('sin', 'Sin', ''),
        ('saw', 'Saw', ''),
        ('tri', 'Tri', ''),
    ]

    type = bpy.props.EnumProperty(name='Type', description='Type of noise used', items=wood_type_items, default='bands')
    noisebasis = bpy.props.EnumProperty(name='Noise Basis', description='Basis of noise used', items=noise_basis_items,
                                        default='blender_original')
    noisebasis2 = bpy.props.EnumProperty(name='Noise Basis 2', description='Second basis of noise used',
                                         items=wood_noise_items, default='sin')
    noisetype = bpy.props.EnumProperty(name='Noise Type', description='Soft or hard noise', items=noise_type_items,
                                       default='soft_noise')
    noisesize = bpy.props.FloatProperty(name='Noise Size', default=0.25)
    turbulence = bpy.props.FloatProperty(name='Turbulence', default=5.0)
    bright = bpy.props.FloatProperty(name='Brightness', default=1.0)
    contrast = bpy.props.FloatProperty(name='Contrast', default=1.0)

    def init(self, context):
        self.inputs.new('luxrender_coordinate_socket', '3D Coordinate')
        self.outputs.new('NodeSocketFloat', 'Float')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'type')
        layout.prop(self, 'noisebasis')
        layout.prop(self, 'noisebasis2')
        layout.prop(self, 'noisetype')
        layout.prop(self, 'noisesize')
        layout.prop(self, 'turbulence')
        layout.prop(self, 'bright')
        layout.prop(self, 'contrast')

    def export_texture(self, make_texture):
        wood_params = ParamSet() \
            .add_string('type', self.type) \
            .add_string('noisebasis', self.noisebasis) \
            .add_string('noisebasis2', self.noisebasis2) \
            .add_string('noisetype', self.noisetype) \
            .add_float('noisesize', self.noisesize) \
            .add_float('turbulence', self.turbulence) \
            .add_float('bright', self.bright) \
            .add_float('contrast', self.contrast)

        coord_node = get_linked_node(self.inputs[0])

        if coord_node and check_node_get_paramset(coord_node):
            wood_params.update(coord_node.get_paramset())

        return make_texture('float', 'blender_wood', self.name, wood_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_wrinkled(luxrender_texture_node):
    """Wrinkled texture node"""
    bl_idname = 'luxrender_texture_wrinkled_node'
    bl_label = 'Wrinkled Texture'
    bl_icon = 'TEXTURE'
    bl_width_min = 160

    octaves = bpy.props.IntProperty(name='Octaves', default=8)
    roughness = bpy.props.FloatProperty(name='Roughness', default=0.5)


    def init(self, context):
        self.inputs.new('luxrender_coordinate_socket', '3D Coordinate')
        self.outputs.new('NodeSocketFloat', 'Float')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'octaves')
        layout.prop(self, 'roughness')

    def export_texture(self, make_texture):
        wrinkled_params = ParamSet() \
            .add_integer('octaves', self.octaves) \
            .add_float('roughness', self.roughness)

        coord_node = get_linked_node(self.inputs[0])

        if coord_node and check_node_get_paramset(coord_node):
            wrinkled_params.update(coord_node.get_paramset())

        return make_texture('float', 'wrinkled', self.name, wrinkled_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_cloud(luxrender_texture_node):
    """Cloud volume texture node"""
    bl_idname = 'luxrender_texture_vol_cloud_node'
    bl_label = 'Cloud Volume Texture'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    radius = bpy.props.FloatProperty(name='Radius', default=0.5, min=0.0, soft_max=0.5,
                                     description='Overall cloud radius inside the base cube')
    noisescale = bpy.props.FloatProperty(name='Noise Scale', default=0.5, min=0.0, max=1.0,
                                         description='Strength of the noise')
    turbulence = bpy.props.FloatProperty(name='Turbulence', default=0.01, min=0.0, soft_max=0.2,
                                         description='Size of the noise displacement')
    sharpness = bpy.props.FloatProperty(name='Sharpness', default=6.00,
                                        description='Noise sharpness - increase for more spikey appearance')
    noiseoffset = bpy.props.FloatProperty(name='Noise Offset', default=0.00, min=0.0, max=1.0)
    spheres = bpy.props.IntProperty(name='Spheres', default=0,
                                    description='If greater than 0, the cloud will consist of a bunch of random \
                                    spheres to mimic a cumulus, this is the number of random spheres. If set to 0, the \
                                    cloud will consist of single displaced sphere')
    octaves = bpy.props.IntProperty(name='Octaves', default=1, description='Number of octaves for the noise function')
    omega = bpy.props.FloatProperty(name='Omega', default=0.75, min=0.0, max=1.0,
                                    description='Amount of noise per octave')
    variability = bpy.props.FloatProperty(name='Variability', default=0.9, min=0.0, max=1.0,
                                          description='Amount of extra noise')
    baseflatness = bpy.props.FloatProperty(name='Base Flatness', default=0.8, min=0.0, max=0.99,
                                           description='How much the base of the cloud is flattened')
    spheresize = bpy.props.FloatProperty(name='Sphere Size', default=0.15, min=0.0,
                                         description='Maxiumum size of cumulus spheres')

    def init(self, context):
        self.inputs.new('luxrender_coordinate_socket', '3D Coordinate')
        self.outputs.new('NodeSocketFloat', 'Float')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'radius')
        layout.prop(self, 'noisescale')
        layout.prop(self, 'turbulence')
        layout.prop(self, 'sharpness')
        layout.prop(self, 'noiseoffset')
        layout.prop(self, 'spheres')
        layout.prop(self, 'octaves')
        layout.prop(self, 'omega')
        layout.prop(self, 'variability')
        layout.prop(self, 'baseflatness')
        layout.prop(self, 'spheresize')

    def export_texture(self, make_texture):
        cloud_vol_params = ParamSet() \
            .add_float('radius', self.radius) \
            .add_float('noisescale', self.noisescale) \
            .add_float('turbulence', self.turbulence) \
            .add_float('sharpness', self.sharpness) \
            .add_float('noiseoffset', self.noiseoffset) \
            .add_integer('spheres', self.spheres) \
            .add_integer('octaves', self.octaves) \
            .add_float('omega', self.omega) \
            .add_float('variability', self.variability) \
            .add_float('baseflatness', self.baseflatness) \
            .add_float('spheresize', self.spheresize)

        coord_node = get_linked_node(self.inputs[0])

        if coord_node and check_node_get_paramset(coord_node):
            cloud_vol_params.update(coord_node.get_paramset())

        return make_texture('float', 'cloud', self.name, cloud_vol_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_vol_exponential(luxrender_texture_node):
    """Exponential texture node"""
    bl_idname = 'luxrender_texture_vol_exponential_node'
    bl_label = 'Exponential Volume Texture'
    bl_icon = 'TEXTURE'
    bl_width_min = 230

    origin = bpy.props.FloatVectorProperty(name='Origin',
                                           description='The reference point to compute the exponential decay',
                                           default=[0.0, 0.0, 0.0])
    updir = bpy.props.FloatVectorProperty(name='Up Vector', description='The direction of the exponential decay',
                                          default=[0.0, 0.0, 1.0])
    decay = bpy.props.FloatProperty(name='Decay Rate', default=1.00)

    def init(self, context):
        self.outputs.new('NodeSocketFloat', 'Float')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'origin')
        layout.prop(self, 'updir')
        layout.prop(self, 'decay')

    def export_texture(self, make_texture):
        exponential_params = ParamSet() \
            .add_vector('updir', self.updir) \
            .add_point('origin', self.origin) \
            .add_float('decay', self.decay)

        return make_texture('float', 'exponential', self.name, exponential_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_vol_smoke_data(luxrender_texture_node):
    """Smoke Data node"""
    bl_idname = 'luxrender_texture_vol_smoke_data_node'
    bl_label = 'Smoke Data Texture'
    bl_icon = 'TEXTURE'
    bl_width_min = 230

    for prop in luxrender_tex_imagemap.properties:
        if prop['attr'].startswith('wrap'):
            wrap_items = prop['items']

    smoke_channels = [
        ('density', 'Density', 'Smoke density grid'),
        ('fire', 'Fire', 'Fire grid'),
    ]

    domain = bpy.props.StringProperty(name='Domain Object')
    source = bpy.props.EnumProperty(name='Source', items=smoke_channels, default='density')
    wrap = bpy.props.EnumProperty(name='Wrapping', items=wrap_items, default='black')

    def init(self, context):
        self.inputs.new('luxrender_coordinate_socket', '3D Coordinate')
        self.outputs.new('NodeSocketFloat', 'Float')

    def draw_buttons(self, context, layout):
        layout.prop_search(self, "domain", bpy.data, "objects")
        layout.prop(self, 'source')
        layout.prop(self, 'wrap')

    def export_texture(self, make_texture):
        # smoke_path = export_smoke(self.domain, self.source)
        grid = export_smoke(self.domain, self.source)
        nx = grid[0]
        ny = grid[1]
        nz = grid[2]
        density = grid[3]

        smokedata_params = ParamSet() \
            .add_string('wrap', self.wrap) \
            .add_integer('nx', nx) \
            .add_integer('ny', ny) \
            .add_integer('nz', nz) \
            .add_float('density', density)

        coord_node = get_linked_node(self.inputs[0])

        if coord_node and check_node_get_paramset(coord_node):
            smokedata_params.update(coord_node.get_paramset())

        return make_texture('float', 'densitygrid', self.name, smokedata_params)
