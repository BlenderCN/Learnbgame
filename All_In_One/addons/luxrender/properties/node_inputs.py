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

import bpy, mathutils
from math import degrees, radians
from ..extensions_framework import declarative_property_group

from .. import LuxRenderAddon
from ..properties import (
    luxrender_texture_node, get_linked_node, check_node_export_texture, check_node_get_paramset
)
from ..properties.texture import (
    import_paramset_to_blender_texture, shorten_name, refresh_preview, luxrender_tex_transform, luxrender_tex_mapping,
    luxrender_tex_imagemap
)
from ..export import (
    ParamSet, process_filepath_data, get_worldscale
)

from ..export.materials import (
    ExportedTextures, add_texture_parameter, get_texture_from_scene
)
from ..outputs import LuxManager, LuxLog

from ..properties.node_material import get_socket_paramsets

from ..properties.node_texture import triple_variant_items

from ..properties.node_sockets import (
    luxrender_TC_Kt_socket, luxrender_transform_socket, luxrender_coordinate_socket
)


@LuxRenderAddon.addon_register_class
class luxrender_3d_coordinates_node(luxrender_texture_node):
    """3D texture coordinates node"""
    bl_idname = 'luxrender_3d_coordinates_node'
    bl_label = '3D Texture Coordinate'
    bl_icon = 'TEXTURE'
    bl_width_min = 260

    for prop in luxrender_tex_transform.properties:
        if prop['attr'].startswith('coordinates'):
            coordinate_items = prop['items']

    coordinates = bpy.props.EnumProperty(name='Coordinates', items=coordinate_items)
    translate = bpy.props.FloatVectorProperty(name='Translate')
    rotate = bpy.props.FloatVectorProperty(name='Rotate', subtype='DIRECTION', unit='ROTATION', min=-radians(359.99),
                                           max=radians(359.99))
    scale = bpy.props.FloatVectorProperty(name='Scale', default=(1.0, 1.0, 1.0))

    def init(self, context):
        self.outputs.new('luxrender_coordinate_socket', '3D Coordinate')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'coordinates')
        if self.coordinates == 'smoke_domain':
            layout.label(text='Auto Using Smoke Domain Data')
        else:
            layout.prop(self, 'translate')
            layout.prop(self, 'rotate')
            layout.prop(self, 'scale')

    def get_paramset(self):
        coord_params = ParamSet()

        ws = get_worldscale(as_scalematrix=False)

        coord_params.add_vector('rotate', [round(degrees(i), 2) for i in self.rotate])

        if self.coordinates == 'smoke_domain':
            for group in bpy.data.node_groups:
                for node in bpy.data.node_groups[group.name].nodes:
                    if bpy.data.node_groups[group.name].nodes[node.name].name == 'Smoke Data Texture':
                        domain = bpy.data.node_groups[group.name].nodes[node.name].domain

            obj = bpy.context.scene.objects[domain]
            vloc = mathutils.Vector((obj.bound_box[0][0], obj.bound_box[0][1], obj.bound_box[0][2]))
            vloc_global = obj.matrix_world * vloc
            d_dim = bpy.data.objects[domain].dimensions
            coord_params.add_string('coordinates', 'global')
            coord_params.add_vector('translate', vloc_global)
            coord_params.add_vector('scale', d_dim)
        else:
            coord_params.add_string('coordinates', self.coordinates)
            coord_params.add_vector('translate', [i * ws for i in self.translate])
            coord_params.add_vector('scale', [i * ws for i in self.scale])

        return coord_params


@LuxRenderAddon.addon_register_class
class luxrender_2d_coordinates_node(luxrender_texture_node):
    """2D texture coordinates node"""
    bl_idname = 'luxrender_2d_coordinates_node'
    bl_label = '2D Texture Coordinate'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    for prop in luxrender_tex_mapping.properties:
        if prop['attr'].startswith('type'):
            coordinate_items = prop['items']

    coordinates = bpy.props.EnumProperty(name='Coordinates', items=coordinate_items)
    center_map = bpy.props.BoolProperty(name='Center Map', default=False)
    uscale = bpy.props.FloatProperty(name='U Scale', default=1.0, min=-10000.0, max=10000.0)
    vscale = bpy.props.FloatProperty(name='V Scale', default=1.0, min=-10000.0, max=10000.0)
    udelta = bpy.props.FloatProperty(name='U Offset', default=0.0, min=-10000.0, max=10000.0)
    vdelta = bpy.props.FloatProperty(name='V Offset', default=0.0, min=-10000.0, max=10000.0)
    v1 = bpy.props.FloatVectorProperty(name='V1', default=(1.0, 0.0, 0.0))
    v2 = bpy.props.FloatVectorProperty(name='V2', default=(0.0, 1.0, 0.0))

    def init(self, context):
        self.outputs.new('luxrender_transform_socket', '2D Coordinate')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'coordinates')

        if self.coordinates == 'planar':
            layout.prop(self, 'v1')
            layout.prop(self, 'v2')
            layout.prop(self, 'udelta')
        else:
            layout.prop(self, 'uscale')
            layout.prop(self, 'vscale')
            layout.prop(self, 'udelta')
            layout.prop(self, 'vdelta')

        if self.coordinates == 'uv':
            layout.prop(self, 'center_map')

    def get_paramset(self):
        coord_params = ParamSet()

        coord_params.add_string('mapping', self.coordinates)
        if self.coordinates == 'planar':
            coord_params.add_vector('v1', self.v1)
            coord_params.add_vector('v2', self.v2)
            coord_params.add_float('udelta', self.udelta)
            coord_params.add_float('vdelta', self.vdelta)

        if self.coordinates == 'cylindrical':
            coord_params.add_float('uscale', self.uscale)
            coord_params.add_float('udelta', self.udelta)

        if self.coordinates == 'spherical':
            coord_params.add_float('uscale', self.uscale)
            coord_params.add_float('vscale', self.vscale)
            coord_params.add_float('udelta', self.udelta)
            coord_params.add_float('vdelta', self.vdelta)

        if self.coordinates == 'uv':
            coord_params.add_float('uscale', self.uscale)
            coord_params.add_float('vscale', self.vscale * -1)  # flip to match blender

            if not self.center_map:
                coord_params.add_float('udelta', self.udelta)
                coord_params.add_float('vdelta',
                                       self.vdelta + 1)  # correction for clamped types, does not harm repeat type
            else:
                coord_params.add_float('udelta', self.udelta + 0.5 * (1.0 - self.uscale))  # auto-center the mapping
                coord_params.add_float('vdelta',
                                       self.vdelta * -1 + 1 - (0.5 * (1.0 - self.vscale)))  # auto-center the mapping

        return coord_params


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_blackbody(luxrender_texture_node):
    """Blackbody spectrum node"""
    bl_idname = 'luxrender_texture_blackbody_node'
    bl_label = 'Blackbody Spectrum'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    temperature = bpy.props.FloatProperty(name='Temperature', default=6500.0)

    def init(self, context):
        self.outputs.new('NodeSocketColor', 'Color')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'temperature')

    def export_texture(self, make_texture):
        blackbody_params = ParamSet()
        blackbody_params.add_float('temperature', self.temperature)

        return make_texture('color', 'blackbody', self.name, blackbody_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_colordepth(luxrender_texture_node):
    """Color at Depth node"""
    bl_idname = 'luxrender_texture_colordepth_node'
    bl_label = 'Color at Depth'
    bl_icon = 'TEXTURE'

    depth = bpy.props.FloatProperty(name='Depth', default=1.0, subtype='DISTANCE', unit='LENGTH')

    def init(self, context):
        self.inputs.new('luxrender_TC_Kt_socket', 'Transmission Color')
        self.outputs.new('NodeSocketColor', 'Color')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'depth')

    def export_texture(self, make_texture):
        colordepth_params = ParamSet()
        colordepth_params.update(get_socket_paramsets(self.inputs, make_texture))
        colordepth_params.add_float('depth', self.depth)

        return make_texture('color', 'colordepth', self.name, colordepth_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_gaussian(luxrender_texture_node):
    """Gaussian spectrum node"""
    bl_idname = 'luxrender_texture_gaussian_node'
    bl_label = 'Gaussian Spectrum'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    energy = bpy.props.FloatProperty(name='Energy', default=1.0, description='Relative energy level')
    wavelength = bpy.props.FloatProperty(name='Wavelength (nm)', default=550.0,
                                         description='Center-point of the spectrum curve')
    width = bpy.props.FloatProperty(name='Width', default=50.0, description='Width of the spectrum curve')

    def init(self, context):
        self.outputs.new('NodeSocketColor', 'Color')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'energy')
        layout.prop(self, 'wavelength')
        layout.prop(self, 'width')

    def export_texture(self, make_texture):
        gaussian_params = ParamSet()
        gaussian_params.add_float('energy', self.energy)
        gaussian_params.add_float('wavelength', self.wavelength)
        gaussian_params.add_float('width', self.width)

        return make_texture('color', 'gaussian', self.name, gaussian_params)


@LuxRenderAddon.addon_register_class  # Drawn in "input" menu, since it does not have any input sockets
class luxrender_texture_type_node_glossyexponent(luxrender_texture_node):
    """Glossy exponent node"""
    bl_idname = 'luxrender_texture_glossyexponent_node'
    bl_label = 'Glossy Exponent'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    exponent = bpy.props.FloatProperty(name='Exponent', default=350.0)

    def init(self, context):
        self.outputs.new('NodeSocketFloat', 'Float')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'exponent')

    def export_texture(self, make_texture):
        glossyexponent_params = ParamSet()
        glossyexponent_params.add_float('value', (2.0 / (self.exponent + 2.0)) ** 0.5)

        return make_texture('float', 'constant', self.name, glossyexponent_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_tabulateddata(luxrender_texture_node):
    """Tabulated Data spectrum node"""
    bl_idname = 'luxrender_texture_tabulateddata_node'
    bl_label = 'Tabulated Data Spectrum'
    bl_icon = 'TEXTURE'

    data_file = bpy.props.StringProperty(name='Data File', description='Data file path', subtype='FILE_PATH')

    def init(self, context):
        self.outputs.new('NodeSocketColor', 'Color')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'data_file')

    def export_texture(self, make_texture):
        tabulateddata_params = ParamSet()

        process_filepath_data(LuxManager.CurrentScene, self, self.data_file, tabulateddata_params, 'filename')

        return make_texture('color', 'tabulateddata', self.name, tabulateddata_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_constant(luxrender_texture_node):
    """Constant texture node"""
    bl_idname = 'luxrender_texture_constant_node'
    bl_label = 'Value'  # Mimics Cycles/Compositor "input > value" node
    bl_icon = 'TEXTURE'

    variant = bpy.props.EnumProperty(name='Variant', items=triple_variant_items, default='color')
    color = bpy.props.FloatVectorProperty(name='Color', subtype='COLOR', min=0.0, max=1.0)
    float = bpy.props.FloatProperty(name='Float', precision=5)
    fresnel = bpy.props.FloatProperty(name='IOR', default=1.52, min=1.0, max=25.0, precision=5)
    col_mult = bpy.props.FloatProperty(name='Multiply Color', default=1.0, precision=5, description='Multiply color')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'variant')

        if self.variant == 'color':
            col = layout.column()
            col.prop(self, 'color')
            col.prop(self, 'col_mult')

        if self.variant == 'float':
            layout.prop(self, 'float')

        if self.variant == 'fresnel':
            layout.prop(self, 'fresnel')

        si = self.inputs.keys()
        so = self.outputs.keys()

        if self.variant == 'color':
            if not 'Color' in so:
                self.outputs.new('NodeSocketColor', 'Color')

            if 'Float' in so:
                self.outputs.remove(self.outputs['Float'])

            if 'Fresnel' in so:
                self.outputs.remove(self.outputs['Fresnel'])

        if self.variant == 'float':
            if not 'Float' in so:
                self.outputs.new('NodeSocketFloat', 'Float')

            if 'Color' in so:
                self.outputs.remove(self.outputs['Color'])

            if 'Fresnel' in so:
                self.outputs.remove(self.outputs['Fresnel'])

        if self.variant == 'fresnel':
            if not 'Fresnel' in so:
                self.outputs.new('luxrender_fresnel_socket', 'Fresnel')

            if 'Color' in so:
                self.outputs.remove(self.outputs['Color'])

            if 'Float' in so:
                self.outputs.remove(self.outputs['Float'])

    def export_texture(self, make_texture):
        constant_params = ParamSet()

        if self.variant == 'float':
            constant_params.add_float('value', self.float)

        if self.variant == 'color':
            constant_params.add_color('value', self.color * self.col_mult)

        if self.variant == 'fresnel':
            constant_params.add_float('value', self.fresnel)

        return make_texture(self.variant, 'constant', self.name, constant_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_hitpointcolor(luxrender_texture_node):
    """Vertex Colors texture node"""
    bl_idname = 'luxrender_texture_hitpointcolor_node'
    bl_label = 'Vertex Colors'
    bl_icon = 'TEXTURE'

    def init(self, context):
        self.outputs.new('NodeSocketColor', 'Color')

    def export_texture(self, make_texture):
        hitpointcolor_params = ParamSet()

        return make_texture('color', 'hitpointcolor', self.name, hitpointcolor_params)


@LuxRenderAddon.addon_register_class
class luxrender_texture_type_node_hitpointgrey(luxrender_texture_node):
    """Vertex Grey texture node"""
    bl_idname = 'luxrender_texture_hitpointgrey_node'
    bl_label = 'Vertex Mask'
    bl_icon = 'TEXTURE'

    for prop in luxrender_tex_imagemap.properties:
        if prop['attr'].startswith('channel'):
            channel_items = prop['items']

    channel = bpy.props.EnumProperty(name='Channel', items=channel_items, default='mean')

    def init(self, context):
        self.outputs.new('NodeSocketFloat', 'Float')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'channel')

    def export_texture(self, make_texture):
        hitpointgrey_params = ParamSet()

        return make_texture('float', 'hitpointgrey', self.name, hitpointgrey_params)

# Hitpointalpha is kind of useless with Blender's vertex color system, so we don't use it
# @LuxRenderAddon.addon_register_class
# class luxrender_texture_type_node_hitpointalpha(luxrender_texture_node):
# '''Vertex Alpha texture node'''
# bl_idname = 'luxrender_texture_hitpointalpha_node'
# bl_label = 'Vertex Alpha'
# bl_icon = 'TEXTURE'
#
# def init(self, context):
# self.outputs.new('NodeSocketFloat', 'Float')
#
# def export_texture(self, make_texture):
# hitpointalpha_params = ParamSet()
#
#       return make_texture('float', 'hitpointalpha', self.name, hitpointalpha_params)
