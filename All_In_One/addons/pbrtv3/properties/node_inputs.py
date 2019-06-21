# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Jens Verwiebe, Jason Clarke, Asbjørn Heid, Simon Wendsche
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

from math import degrees

import bpy
import mathutils

from . import create_luxcore_name, warning_luxcore_node, warning_classic_node
from .. import PBRTv3Addon

from ..export import ParamSet, process_filepath_data, get_worldscale

from ..outputs import PBRTv3Manager
from ..outputs.luxcore_api import UsePBRTv3Core, set_prop_tex

from ..properties import pbrtv3_texture_node
from ..properties.node_sockets import mapping_2d_socketname, mapping_3d_socketname
from ..properties.node_texture import triple_variant_items
from ..properties.texture import pbrtv3_tex_transform, pbrtv3_tex_mapping, pbrtv3_tex_imagemap


@PBRTv3Addon.addon_register_class
class pbrtv3_3d_coordinates_node(pbrtv3_texture_node):
    """3D texture coordinates node"""
    bl_idname = 'pbrtv3_3d_coordinates_node'
    bl_label = '3D Texture Mapping'
    bl_icon = 'TEXTURE'
    bl_width_min = 260

    for prop in pbrtv3_tex_transform.properties:
        if prop['attr'].startswith('coordinates'):
            coordinate_items = prop['items']

    coordinates = bpy.props.EnumProperty(name='Coordinates', items=coordinate_items)
    translate = bpy.props.FloatVectorProperty(name='Translate', subtype='TRANSLATION', description='Moves the texture')
    rotate = bpy.props.FloatVectorProperty(name='Rotate', unit='ROTATION', default=(0, 0, 0), subtype='EULER', description='Rotates the texture')
    scale = bpy.props.FloatVectorProperty(name='Scale', default=(1.0, 1.0, 1.0), subtype='XYZ', description='Scales the texture')
    uniform_scale = bpy.props.FloatProperty(name='', default=1.0, description='Scales the texture uniformly along all axis')
    use_uniform_scale = bpy.props.BoolProperty(name='Uniform', default=False,
                                               description='Use the same scale value for all axis')

    # PBRTv3Core uses different names for the mapping types
    luxcore_mapping_type_map = {
        'global': 'globalmapping3d',
        'local': 'localmapping3d',
        'uv': 'uvmapping3d'
    }

    def init(self, context):
        self.outputs.new('pbrtv3_coordinate_socket', mapping_3d_socketname)

    def draw_buttons(self, context, layout):
        layout.prop(self, 'coordinates')

        if UsePBRTv3Core():
            # PBRTv3Core layout
            if self.coordinates in self.luxcore_mapping_type_map:
                row = layout.row()

                row.column().prop(self, 'translate')
                row.column().prop(self, 'rotate')

                scale_column = row.column()
                if self.use_uniform_scale:
                    scale_column.label(text='Scale:')
                    scale_column.prop(self, 'uniform_scale')
                else:
                    scale_column.prop(self, 'scale')

                scale_column.prop(self, 'use_uniform_scale')
            else:
                layout.label(text='Mapping not supported by PBRTv3Core', icon='ERROR')
        else:
            # Classic layout
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

    def export_luxcore(self, properties):
        mapping_type = self.luxcore_mapping_type_map[self.coordinates]

        # create a location matrix
        tex_loc = mathutils.Matrix.Translation((self.translate))

        # create an identitiy matrix
        tex_sca = mathutils.Matrix()
        tex_sca[0][0] = self.uniform_scale if self.use_uniform_scale else self.scale[0]  # X
        tex_sca[1][1] = self.uniform_scale if self.use_uniform_scale else self.scale[1]  # Y
        tex_sca[2][2] = self.uniform_scale if self.use_uniform_scale else self.scale[2]  # Z

        # create a rotation matrix
        tex_rot0 = mathutils.Matrix.Rotation(self.rotate[0], 4, 'X')
        tex_rot1 = mathutils.Matrix.Rotation(self.rotate[1], 4, 'Y')
        tex_rot2 = mathutils.Matrix.Rotation(self.rotate[2], 4, 'Z')
        tex_rot = tex_rot0 * tex_rot1 * tex_rot2

        # combine transformations
        transformation = tex_loc * tex_rot * tex_sca

        return [mapping_type, transformation]


@PBRTv3Addon.addon_register_class
class pbrtv3_2d_coordinates_node(pbrtv3_texture_node):
    """2D texture coordinates node"""
    bl_idname = 'pbrtv3_2d_coordinates_node'
    bl_label = '2D Texture Mapping'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    for prop in pbrtv3_tex_mapping.properties:
        if prop['attr'].startswith('type'):
            coordinate_items = prop['items']

    coordinates = bpy.props.EnumProperty(name='Coordinates', items=coordinate_items)
    center_map = bpy.props.BoolProperty(name='Center Map', default=False, description='Keep the map centerered even '
                                        'when scaled (e.g. scale to +U and -U equally instead of only in +U direction)')
    uscale = bpy.props.FloatProperty(name='U', default=1.0, min=-10000.0, max=10000.0)
    vscale = bpy.props.FloatProperty(name='V', default=1.0, min=-10000.0, max=10000.0)
    uniform_scale = bpy.props.FloatProperty(name='', default=1.0)
    use_uniform_scale = bpy.props.BoolProperty(name='Uniform', default=False,
                                               description='Use the same scale value for U and V')
    udelta = bpy.props.FloatProperty(name='U', default=0.0, min=-10000.0, max=10000.0)
    vdelta = bpy.props.FloatProperty(name='V', default=0.0, min=-10000.0, max=10000.0)
    v1 = bpy.props.FloatVectorProperty(name='V1', default=(1.0, 0.0, 0.0))
    v2 = bpy.props.FloatVectorProperty(name='V2', default=(0.0, 1.0, 0.0))

    # PBRTv3Core uses different names for the mapping types
    luxcore_mapping_type_map = {
        'uv': 'uvmapping2d'
    }

    def init(self, context):
        self.outputs.new('pbrtv3_transform_socket', mapping_2d_socketname)

    def draw_buttons(self, context, layout):
        layout.prop(self, 'coordinates')

        if UsePBRTv3Core() and not self.coordinates in self.luxcore_mapping_type_map:
            layout.label(text='Mapping not supported by PBRTv3Core', icon='ERROR')
        else:
            if self.coordinates == 'planar':
                layout.prop(self, 'v1')
                layout.prop(self, 'v2')
                layout.prop(self, 'udelta')
            else:
                layout.label('Scale:')

                if self.use_uniform_scale and UsePBRTv3Core():
                    layout.prop(self, 'uniform_scale')
                else:
                    sub = layout.row(align=True)
                    sub.prop(self, 'uscale')
                    sub.prop(self, 'vscale')

                if UsePBRTv3Core():
                    layout.prop(self, 'use_uniform_scale')

                layout.label('Offset:')
                row = layout.row(align=True)
                row.prop(self, 'udelta')
                row.prop(self, 'vdelta')

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

    def export_luxcore(self, properties):
        mapping_type = self.luxcore_mapping_type_map[self.coordinates]

        if self.use_uniform_scale:
            uscale = self.uniform_scale
            vscale = self.uniform_scale
        else:
            uscale = self.uscale
            vscale = self.vscale

        uvscale = [uscale,
                   vscale * -1]

        if not self.center_map:
            uvdelta = [self.udelta,
                       self.vdelta + 1]
        else:
            uvdelta = [self.udelta + 0.5 * (1 - uscale),
                       self.vdelta * -1 + 1 - (0.5 * (1 - vscale))]

        return [mapping_type, uvscale, uvdelta]


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_blackbody(pbrtv3_texture_node):
    """Blackbody spectrum node"""
    bl_idname = 'pbrtv3_texture_blackbody_node'
    bl_label = 'Blackbody Spectrum'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    temperature = bpy.props.FloatProperty(name='Temperature', default=6500.0, step=100, min=1000, max=10000)

    def init(self, context):
        self.outputs.new('NodeSocketColor', 'Color')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'temperature', slider=True)

    def export_texture(self, make_texture):
        blackbody_params = ParamSet()
        blackbody_params.add_float('temperature', self.temperature)

        return make_texture('color', 'blackbody', self.name, blackbody_params)

    def export_luxcore(self, properties):
        luxcore_name = create_luxcore_name(self)

        set_prop_tex(properties, luxcore_name, 'type', 'blackbody')
        set_prop_tex(properties, luxcore_name, 'temperature', self.temperature)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_gaussian(pbrtv3_texture_node):
    """Gaussian spectrum node"""
    bl_idname = 'pbrtv3_texture_gaussian_node'
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
        warning_classic_node(layout)

        layout.prop(self, 'energy')
        layout.prop(self, 'wavelength')
        layout.prop(self, 'width')

    def export_texture(self, make_texture):
        gaussian_params = ParamSet()
        gaussian_params.add_float('energy', self.energy)
        gaussian_params.add_float('wavelength', self.wavelength)
        gaussian_params.add_float('width', self.width)

        return make_texture('color', 'gaussian', self.name, gaussian_params)

    # TODO: PBRTv3Core export once supported by PBRTv3Core


@PBRTv3Addon.addon_register_class  # Drawn in "input" menu, since it does not have any input sockets
class pbrtv3_texture_type_node_glossyexponent(pbrtv3_texture_node):
    """Glossy exponent node"""
    bl_idname = 'pbrtv3_texture_glossyexponent_node'
    bl_label = 'Glossy Exponent'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    exponent = bpy.props.FloatProperty(name='Exponent', default=350.0)

    def calc_roughness(self):
        return (2.0 / (self.exponent + 2.0)) ** 0.5

    def init(self, context):
        self.outputs.new('NodeSocketFloat', 'Roughness')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'exponent')

    def export_texture(self, make_texture):
        glossyexponent_params = ParamSet()
        glossyexponent_params.add_float('value', self.calc_roughness())

        return make_texture('float', 'constant', self.name, glossyexponent_params)

    def export_luxcore(self, properties):
        return self.calc_roughness()


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_tabulateddata(pbrtv3_texture_node):
    """Tabulated Data spectrum node"""
    bl_idname = 'pbrtv3_texture_tabulateddata_node'
    bl_label = 'Tabulated Data Spectrum'
    bl_icon = 'TEXTURE'

    data_file = bpy.props.StringProperty(name='Data File', description='Data file path', subtype='FILE_PATH')

    def init(self, context):
        self.outputs.new('NodeSocketColor', 'Color')

    def draw_buttons(self, context, layout):
        warning_classic_node(layout)

        layout.prop(self, 'data_file')

    def export_texture(self, make_texture):
        tabulateddata_params = ParamSet()

        process_filepath_data(PBRTv3Manager.CurrentScene, self, self.data_file, tabulateddata_params, 'filename')

        return make_texture('color', 'tabulateddata', self.name, tabulateddata_params)

    # TODO: PBRTv3Core export once supported by PBRTv3Core


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_constant(pbrtv3_texture_node):
    """Constant texture node"""
    bl_idname = 'pbrtv3_texture_constant_node'
    bl_label = 'Value'  # Mimics Cycles/Compositor "input > value" node
    bl_icon = 'TEXTURE'

    variant = bpy.props.EnumProperty(name='Variant', items=triple_variant_items, default='color')
    color = bpy.props.FloatVectorProperty(name='Color', subtype='COLOR', min=0.0, max=1.0)
    float = bpy.props.FloatProperty(name='Float', precision=5)
    fresnel = bpy.props.FloatProperty(name='IOR', default=1.52, min=1.0, max=25.0, precision=5)
    col_mult = bpy.props.FloatProperty(name='Multiply Color', default=1.0, precision=5, description='Multiply color')

    def init(self, context):
        # Default is color (need to set it for instances generated from scripts, e.g. the auto-conversion operators)
        self.outputs.new('NodeSocketColor', 'Color')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'variant')

        if self.variant == 'color':
            col = layout.column()
            col.template_color_picker(self, 'color', value_slider=True)
            col.prop(self, 'color', text='')

            col.prop(self, 'col_mult')

        if self.variant == 'float':
            layout.prop(self, 'float')

        if self.variant == 'fresnel':
            warning_classic_node(layout)
            layout.prop(self, 'fresnel')

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
                self.outputs.new('pbrtv3_fresnel_socket', 'Fresnel')
                self.outputs['Fresnel'].needs_link = True

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

    def export_luxcore(self, properties):
        if self.variant == 'color':
            value = [c * self.col_mult for c in self.color]
        elif self.variant == 'float':
            value = self.float
        elif self.variant == 'fresnel':
            value = self.fresnel

        return value


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_hitpointcolor(pbrtv3_texture_node):
    """Vertex Colors texture node"""
    bl_idname = 'pbrtv3_texture_hitpointcolor_node'
    bl_label = 'Vertex Colors'
    bl_icon = 'TEXTURE'

    def init(self, context):
        self.outputs.new('NodeSocketColor', 'Color')

    def export_texture(self, make_texture):
        hitpointcolor_params = ParamSet()

        return make_texture('color', 'hitpointcolor', self.name, hitpointcolor_params)

    def export_luxcore(self, properties):
        luxcore_name = create_luxcore_name(self)

        set_prop_tex(properties, luxcore_name, 'type', 'hitpointcolor')

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_hitpointgrey(pbrtv3_texture_node):
    """Vertex Grey texture node"""
    bl_idname = 'pbrtv3_texture_hitpointgrey_node'
    bl_label = 'Vertex Mask'
    bl_icon = 'TEXTURE'

    for prop in pbrtv3_tex_imagemap.properties:
        if prop['attr'].startswith('channel'):
            channel_items = prop['items']

    channel = bpy.props.EnumProperty(name='Channel', items=channel_items, default='mean')

    channel_luxcore_items = [
        ('-1', 'RGB', 'RGB luminance'),
        ('0', 'R', 'Red luminance'),
        ('1', 'G', 'Green luminance'),
        ('2', 'B', 'Blue luminance'),
    ]
    channel_luxcore = bpy.props.EnumProperty(name='Channel', items=channel_luxcore_items, default='-1')

    def init(self, context):
        self.outputs.new('NodeSocketFloat', 'Float')

    def draw_buttons(self, context, layout):
        if UsePBRTv3Core():
            layout.prop(self, 'channel_luxcore', expand=True)
        else:
            layout.prop(self, 'channel')

    def export_texture(self, make_texture):
        hitpointgrey_params = ParamSet()

        return make_texture('float', 'hitpointgrey', self.name, hitpointgrey_params)

    def export_luxcore(self, properties):
        luxcore_name = create_luxcore_name(self)

        set_prop_tex(properties, luxcore_name, 'type', 'hitpointgrey')
        set_prop_tex(properties, luxcore_name, 'channel', self.channel_luxcore)

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_pointiness(pbrtv3_texture_node):
    """Pointiness texture node"""
    bl_idname = 'pbrtv3_texture_pointiness_node'
    bl_label = 'Pointiness'
    bl_icon = 'TEXTURE'
    bl_width_min = 190

    curvature_items = [
        ('concave', 'Concave', 'Only use dents'),
        ('convex', 'Convex', 'Only use hills'),
        ('both', 'Both', 'Use both hills and dents'),
    ]
    curvature_mode = bpy.props.EnumProperty(items=curvature_items, default='both')

    def init(self, context):
        self.inputs.new('pbrtv3_float_socket', 'Multiplier')
        self.inputs[0].default_value = 10
        self.outputs.new('NodeSocketFloat', 'Float')

    def draw_buttons(self, context, layout):
        warning_luxcore_node(layout)
        layout.prop(self, 'curvature_mode', expand=True)

    def export_luxcore(self, properties):
        # Pointiness is a hitpointalpha texture behind the scenes, just that it implicitly enables pointiness
        # calculation on the mesh (handled in luxcore object export) and has some nice wrapping to get only part of
        # the pointiness information (see code below)
        luxcore_name = create_luxcore_name(self)

        set_prop_tex(properties, luxcore_name, 'type', 'hitpointalpha')

        if self.curvature_mode == 'both':
            # Pointiness values are in [-1..1] range originally
            name_abs = luxcore_name + '_abs'
            set_prop_tex(properties, name_abs, 'type', 'abs')
            set_prop_tex(properties, name_abs, 'texture', luxcore_name)

            luxcore_name = name_abs

        elif self.curvature_mode == 'concave':
            # Only use the positive values of the pointiness information
            name_clamp = luxcore_name + '_clamp'
            set_prop_tex(properties, name_clamp, 'type', 'clamp')
            set_prop_tex(properties, name_clamp, 'texture', luxcore_name)
            set_prop_tex(properties, name_clamp, 'min', 0)
            set_prop_tex(properties, name_clamp, 'max', 1)

            luxcore_name = name_clamp

        elif self.curvature_mode == 'convex':
            # Only use the negative values of the pointiness information by first flipping the values
            name_flip = luxcore_name + '_flip'
            set_prop_tex(properties, name_flip, 'type', 'scale')
            set_prop_tex(properties, name_flip, 'texture1', luxcore_name)
            set_prop_tex(properties, name_flip, 'texture2', -1)

            name_clamp = luxcore_name + '_clamp'
            set_prop_tex(properties, name_clamp, 'type', 'clamp')
            set_prop_tex(properties, name_clamp, 'texture', name_flip)
            set_prop_tex(properties, name_clamp, 'min', 0)
            set_prop_tex(properties, name_clamp, 'max', 1)

            luxcore_name = name_clamp

        multiplier = self.inputs[0].export_luxcore(properties)

        if multiplier != 1:
            multiplier_name = luxcore_name + '_multiplier'
            set_prop_tex(properties, multiplier_name, 'type', 'scale')
            set_prop_tex(properties, multiplier_name, 'texture1', luxcore_name)
            set_prop_tex(properties, multiplier_name, 'texture2', multiplier)

            luxcore_name = multiplier_name

        return luxcore_name


@PBRTv3Addon.addon_register_class
class pbrtv3_texture_type_node_python(pbrtv3_texture_node):
    """Python expression node"""
    bl_idname = 'pbrtv3_texture_python_node'
    bl_label = 'Python Expression'
    bl_icon = 'TEXTURE'
    bl_width_min = 200

    single_line = bpy.props.StringProperty()
    text_block_name = bpy.props.StringProperty()
    input_type_items = [
        ('single_line', 'Single Line', ''),
        ('text_block', 'Text Block', ''),
    ]
    input_type = bpy.props.EnumProperty(items=input_type_items, default='single_line')

    def init(self, context):
        self.outputs.new('NodeSocketFloat', 'result')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'input_type', expand=True)

        col = layout.column(align=True)
        col.scale_y = 0.6
        col.label('Assign result of the expression')
        col.label('to a variable named "result".')
        col.label('Example: result = [1, 0, 0]')

        if self.input_type == 'single_line':
            layout.prop(self, 'single_line', text='')
        elif self.input_type == 'text_block':
            layout.prop_search(self, 'text_block_name', bpy.data, 'texts', 'Script', icon='TEXT')

    def export_luxcore(self, properties):
        if self.input_type == 'single_line':
            # Convenience imports like in the Blender python console
            code = (
                'import bpy\n'
                'from mathutils import *\n'
                'from math import *\n'
                'C = bpy.context\n'
                'D = bpy.data\n'
            )

            code += self.single_line
        else:
            text_block = bpy.data.texts[self.text_block_name]
            code = '\n'.join([line.body for line in text_block.lines])

        global_scope = {}
        local_scope = {}

        exec(code, global_scope, local_scope)
        return local_scope['result']


# Hitpointalpha is kind of useless with Blender's vertex color system, so we don't use it
# @PBRTv3Addon.addon_register_class
# class pbrtv3_texture_type_node_hitpointalpha(pbrtv3_texture_node):
# '''Vertex Alpha texture node'''
# bl_idname = 'pbrtv3_texture_hitpointalpha_node'
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
