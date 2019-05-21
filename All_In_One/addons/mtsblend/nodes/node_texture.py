# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender Mitsuba Add-On
# --------------------------------------------------------------------------
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
# ***** END GPL LICENSE BLOCK *****

import bpy
from bpy.types import Node
from bpy.props import FloatProperty, EnumProperty, StringProperty

from ..nodes import (
    MitsubaNodeTypes, mitsuba_node
)


class mitsuba_texture_node(mitsuba_node):
    bl_icon = 'TEXTURE'
    bl_width_min = 220
    shader_type_compat = {'OBJECT'}
    mitsuba_nodetype = 'TEXTURE'

    custom_outputs = [
        {'type': 'MtsSocketColor', 'name': 'Color'},
        {'type': 'MtsSocketFloat', 'name': 'Value'},
        {'type': 'MtsSocketTexture', 'name': 'Texture'},
    ]

    def get_uvmapping_dict(self):
        mapping = self.inputs['UV Mapping'].get_linked_node()

        if mapping:
            return mapping.get_uvmapping_dict()

        else:
            return {}

    def set_uvmapping_dict(self, ntree, params):
        uvparams = {}

        if 'uscale' in params:
            uvparams['uscale'] = params['uscale']

        if 'vscale' in params:
            uvparams['vscale'] = params['vscale']

        if 'uoffset' in params:
            uvparams['uoffset'] = params['uoffset']

        if 'voffset' in params:
            uvparams['voffset'] = params['voffset']

        if uvparams:
            uvparams['type'] = 'uvmapping'
            ntree.new_node_from_dict(uvparams, self.inputs['UV Mapping'])

    def get_texture_dict(self, export_ctx):
        pass

    def get_color_dict(self, export_ctx):
        return self.get_texture_dict(export_ctx)

    def get_float_dict(self, export_ctx):
        return self.get_texture_dict(export_ctx)


@MitsubaNodeTypes.register
class MtsNodeTexture_bitmap(mitsuba_texture_node, Node):
    """Bitmap texture node"""
    bl_idname = 'MtsNodeTexture_bitmap'
    bl_label = 'Bitmap Texture'
    plugin_types = {'bitmap'}

    def update_image(self, context):
        if self.image:
            self.filename = bpy.data.images[self.image].filepath

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        row.prop_search(self, 'image', bpy.data, 'images')
        row.operator('image.open', text='', icon='FILESEL')

        if not self.image:
            layout.prop(self, 'filename')

        layout.prop(self, 'channel')
        layout.prop(self, 'wrapModeU')
        layout.prop(self, 'wrapModeV')
        layout.prop(self, 'gammaType')

        if self.gammaType == 'custom':
            layout.prop(self, 'gamma')

        layout.prop(self, 'filterType')

        if self.filterType == 'ewa':
            layout.prop(self, 'maxAnisotropy')

        layout.prop(self, 'cache')

    image = StringProperty(
        name='Image',
        description='Select image',
        default='',
        update=update_image
    )

    filename = StringProperty(
        subtype='FILE_PATH',
        name='File Name',
        description='Path to an image file',
        default='',
    )

    wrapModeU = EnumProperty(
        name="U Wrapping",
        description='What should be done when encountering U coordinates outside of the range [0,1].',
        items=[
            ('repeat', 'Repeat', 'repeat'),
            ('mirror', 'Mirror', 'mirror'),
            ('clamp', 'Clamp', 'clamp'),
            ('zero', 'Black', 'zero'),
            ('one', 'White', 'one'),
        ],
        default='repeat',
    )

    wrapModeV = EnumProperty(
        name="V Wrapping",
        description='What should be done when encountering V coordinates outside of the range [0,1].',
        items=[
            ('repeat', 'Repeat', 'repeat'),
            ('mirror', 'Mirror', 'mirror'),
            ('clamp', 'Clamp', 'clamp'),
            ('zero', 'Black', 'zero'),
            ('one', 'White', 'one'),
        ],
        default='repeat',
    )

    gammaType = EnumProperty(
        name="Image Gamma",
        description='Select Image gamma.',
        items=[
            ('auto', 'Autodetect', 'auto'),
            ('srgb', 'sRGB', 'srgb'),
            ('custom', 'Custom', 'custom'),
        ],
        default='auto',
    )

    gamma = FloatProperty(
        name='Gamma',
        description='Specifies the texture gamma value.',
        default=2.2,
        min=0.01,
        max=6.0,
    )

    filterType = EnumProperty(
        name="Filter type",
        description='Specifies the type of texture filtering.',
        items=[
            ('ewa', 'Anisotropic (EWA Filtering)', 'ewa'),
            ('trilinear', 'Isotropic (Trilinear Filtering)', 'trilinear'),
            ('nearest', 'No filter (Nearest neighbor)', 'nearest'),
        ],
        default='ewa',
    )

    maxAnisotropy = FloatProperty(
        name='Max. Anisotropy',
        description='Maximum allowed anisotropy when using the EWA filter.',
        default=20,
    )

    cache = EnumProperty(
        name="Image Cache",
        description='Select Image cache mode.',
        items=[
            ('auto', 'Autodetect', 'auto'),
            ('true', 'Always', 'always'),
            ('false', 'Never', 'false'),
        ],
        default='auto',
    )

    channel = EnumProperty(
        name='Channel',
        description='Select the channel used for output Value.',
        items=[
            ('all', 'Average', 'all'),
            ('r', 'Red', 'r'),
            ('g', 'Green', 'g'),
            ('b', 'Blue', 'b'),
            ('a', 'Alpha', 'a'),
        ],
        default='all',
    )

    custom_inputs = [
        {'type': 'MtsSocketUVMapping', 'name': 'UV Mapping'},
    ]

    def get_texture_dict(self, export_ctx):
        params = {
            'type': 'bitmap',
        }

        if self.image and self.image in bpy.data.images:
            params.update({'image': bpy.data.images[self.image]})

        elif self.filename:
            params.update({'filename': export_ctx.get_export_path(self.filename)})

        if self.wrapModeU != 'repeat' or self.wrapModeV != 'repeat':
            params.update({
                'wrapModeU': self.wrapModeU,
                'wrapModeV': self.wrapModeV,
            })

        if self.filterType != 'ewa':
            params.update({'filterType': self.filterType})

        elif self.maxAnisotropy != 20:
            params.update({'maxAnisotropy': self.maxAnisotropy})

        if self.gammaType == 'custom':
            params.update({'gamma': self.gamma})

        elif self.gammaType == 'srgb':
            params.update({'gamma': -1})

        if self.cache != 'auto':
            params.update({'cache': self.cache})

        mapping = self.get_uvmapping_dict()

        if mapping:
            params.update(mapping)

        return params

    def get_float_dict(self, export_ctx):
        params = self.get_texture_dict(export_ctx)

        if self.channel != 'all':
            params.update({'channel': self.channel})

        return params

    def set_from_dict(self, ntree, params):
        if 'image' in params:
            self.image = params['image'].name

        elif 'filename' in params:
            self.filename = params['filename']

        if 'wrapModeU' in params:
            self.wrapModeU = params['wrapModeU']

        if 'wrapModeV' in params:
            self.wrapModeV = params['wrapModeV']

        if 'filterType' in params:
            self.filterType = params['filterType']

        if 'maxAnisotropy' in params:
            self.maxAnisotropy = params['maxAnisotropy']

        if 'gamma' in params:
            if params['gamma'] == -1:
                self.gammaType = 'srgb'
            else:
                self.gamma = params['gamma']

        if 'cache' in params:
            self.cache = params['cache']

        self.set_uvmapping_dict(ntree, params)


@MitsubaNodeTypes.register
class MtsNodeTexture_checkerboard(mitsuba_texture_node, Node):
    """Checkerboard texture node"""
    bl_idname = 'MtsNodeTexture_checkerboard'
    bl_label = 'Checkerboard Texture'
    plugin_types = {'checkerboard'}

    custom_inputs = [
        {'type': 'MtsSocketSpectrum_colorA', 'name': 'Color 1'},
        {'type': 'MtsSocketSpectrum_colorB', 'name': 'Color 2'},
        {'type': 'MtsSocketUVMapping', 'name': 'UV Mapping'},
    ]

    def get_texture_dict(self, export_ctx):
        params = {
            'type': 'checkerboard',
            'color0': self.inputs['Color 1'].get_spectrum_dict(export_ctx),
            'color1': self.inputs['Color 2'].get_spectrum_dict(export_ctx),
        }

        mapping = self.get_uvmapping_dict()

        if mapping:
            params.update(mapping)

        return params

    def set_from_dict(self, ntree, params):
        if 'color0' in params:
            self.inputs['Color 1'].set_spectrum_socket(ntree, params['color0'])

        if 'color1' in params:
            self.inputs['Color 2'].set_spectrum_socket(ntree, params['color1'])

        self.set_uvmapping_dict(ntree, params)


@MitsubaNodeTypes.register
class MtsNodeTexture_gridtexture(mitsuba_texture_node, Node):
    """Grid texture node"""
    bl_idname = 'MtsNodeTexture_gridtexture'
    bl_label = 'Grid Texture'
    plugin_types = {'gridtexture'}

    def draw_buttons(self, context, layout):
        layout.prop(self, 'lineWidth')

    lineWidth = FloatProperty(name='Line Width', default=0.01, min=0.0, max=1.0)

    custom_inputs = [
        {'type': 'MtsSocketSpectrum_colorA', 'name': 'Color 1'},
        {'type': 'MtsSocketSpectrum_colorB', 'name': 'Color 2'},
        {'type': 'MtsSocketUVMapping', 'name': 'UV Mapping'},
    ]

    def get_texture_dict(self, export_ctx):
        params = {
            'type': 'gridtexture',
            'color0': self.inputs['Color 1'].get_spectrum_dict(export_ctx),
            'color1': self.inputs['Color 2'].get_spectrum_dict(export_ctx),
            'lineWidth': self.lineWidth,
        }

        mapping = self.get_uvmapping_dict()

        if mapping:
            params.update(mapping)

        return params

    def set_from_dict(self, ntree, params):
        if 'color0' in params:
            self.inputs['Color 1'].set_spectrum_socket(ntree, params['color0'])

        if 'color1' in params:
            self.inputs['Color 2'].set_spectrum_socket(ntree, params['color1'])

        if 'lineWidth' in params:
            self.lineWidth = params['lineWidth']

        self.set_uvmapping_dict(ntree, params)


@MitsubaNodeTypes.register
class MtsNodeTexture_scale(mitsuba_texture_node, Node):
    """Scale texture node"""
    bl_idname = 'MtsNodeTexture_scale'
    bl_label = 'Scale Texture'
    plugin_types = {'scale'}

    def draw_buttons(self, context, layout):
        layout.prop(self, 'scale')

    scale = FloatProperty(name='Scale Factor', description='Multiply texture color by Scale value', default=1.0, min=0.001, max=100.0)

    custom_inputs = [
        {'type': 'MtsSocketTexture', 'name': 'Texture'},
    ]

    def get_texture_dict(self, export_ctx):
        tex_node = self.inputs['Texture'].get_linked_node()

        if tex_node:
            params = tex_node.get_texture_dict(export_ctx)

            if self.scale != 1.0:
                return {
                    'type': 'scale',
                    'scale': self.scale,
                    'texture': params
                }

            else:
                return params

        else:
            return {}

    def set_from_dict(self, ntree, params):
        if 'texture' in params:
            ntree.new_node_from_dict(params['texture'], self.inputs['Texture'])

        if 'scale' in params:
            self.scale = params['scale']


@MitsubaNodeTypes.register
class MtsNodeTexture_vertexcolors(mitsuba_texture_node, Node):
    """Vertex Colors texture node"""
    bl_idname = 'MtsNodeTexture_vertexcolors'
    bl_label = 'Vertex Colors Texture'
    plugin_types = {'vertexcolors'}

    def get_texture_dict(self, export_ctx):
        return {
            'type': 'vertexcolors',
        }

    def set_from_dict(self, ntree, params):
        pass


@MitsubaNodeTypes.register
class MtsNodeTexture_wireframe(mitsuba_texture_node, Node):
    """Wireframe texture node"""
    bl_idname = 'MtsNodeTexture_wireframe'
    bl_label = 'Wireframe Texture'
    plugin_types = {'wireframe'}

    def draw_buttons(self, context, layout):
        layout.prop(self, 'lineWidth')
        layout.prop(self, 'stepWidth')

    lineWidth = FloatProperty(name='Line Width', default=0.01, min=0.0, max=1.0)
    stepWidth = FloatProperty(name='Step Width', default=0.5, min=0.0, max=1.0)

    custom_inputs = [
        {'type': 'MtsSocketSpectrum_interiorColor', 'name': 'Face Color'},
        {'type': 'MtsSocketSpectrum_edgeColor', 'name': 'Edge Color'},
    ]

    def get_texture_dict(self, export_ctx):
        return {
            'type': 'wireframe',
            'interiorColor': self.inputs['Face Color'].get_spectrum_dict(export_ctx),
            'edgeColor': self.inputs['Edge Color'].get_spectrum_dict(export_ctx),
            'lineWidth': self.lineWidth,
            'stepWidth': self.stepWidth,
        }

    def set_from_dict(self, ntree, params):
        if 'interiorColor' in params:
            self.inputs['Face Color'].set_spectrum_socket(ntree, params['interiorColor'])

        if 'edgeColor' in params:
            self.inputs['Edge Color'].set_spectrum_socket(ntree, params['edgeColor'])

        if 'lineWidth' in params:
            self.lineWidth = params['lineWidth']

        if 'stepWidth' in params:
            self.stepWidth = params['stepWidth']


@MitsubaNodeTypes.register
class MtsNodeTexture_curvature(mitsuba_texture_node, Node):
    """Curvature texture node"""
    bl_idname = 'MtsNodeTexture_curvature'
    bl_label = 'Curvature Texture'
    plugin_types = {'curvature'}

    def draw_buttons(self, context, layout):
        layout.prop(self, 'curvature')
        layout.prop(self, 'scale')

    curvature_type_items = [
        ('mean', 'Mean', 'mean'),
        ('gaussian', 'Gaussian', 'gaussian'),
    ]

    curvature = EnumProperty(name='Curvature Type', items=curvature_type_items, default='mean')
    scale = FloatProperty(name='Scale', default=1.0, min=-1.0, max=1.0)

    def get_texture_dict(self, export_ctx):
        return {
            'type': 'curvature',
            'curvature': self.curvature,
            'scale': self.scale,
        }

    def set_from_dict(self, ntree, params):
        if 'curvature' in params:
            self.curvature = params['curvature']

        if 'scale' in params:
            self.scale = params['scale']
