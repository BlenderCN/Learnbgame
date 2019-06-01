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

from bpy.types import NodeSocket
from bpy.props import BoolProperty, FloatProperty, FloatVectorProperty

from ..nodes import MitsubaSocketTypes


def draw_color_socket(cls, context, layout, node, text):
    if cls.is_linked or cls.bl_static_type == 'SHADER':
        layout.label(text=cls.name, icon=cls.linked_node_icon())

    else:
        row = layout.row()
        row.alignment = 'LEFT'
        row.prop(cls, 'default_value', text='')
        row.label(text=cls.name)


def draw_vector_socket(cls, context, layout, node, text):
    if cls.is_linked or cls.bl_static_type == 'SHADER':
        layout.label(text=cls.name, icon=cls.linked_node_icon())

    else:
        split = layout.split()
        split.label(text=cls.name)
        col = split.column()
        col.prop(cls, 'default_value', text='')


def ColorParams(attr, name, description='', subtype='COLOR', default=(0.8, 0.8, 0.8), min=0.0, max=1.0, precision=2, draw=draw_color_socket):
    color_dict = {
        'attr': attr,
        'name': name,
        'description': description if description else name,
        'subtype': subtype,
        'default': default,
        'min': min,
        'max': max,
        'precision': precision,
        'draw': draw,
    }

    return color_dict


def FloatParams(attr, name, description='', subtype='NONE', unit='NONE', default=0.0, min=0.0, max=1.0, precision=6):
    float_dict = {
        'attr': attr,
        'name': name,
        'description': description if description else '%s value' % name,
        'subtype': subtype,
        'unit': unit,
        'default': default,
        'min': min,
        'max': max,
        'precision': precision,
    }

    return float_dict


class mitsuba_socket:
    bl_custom_type = 'UNDEFINED'
    ui_open = BoolProperty(name='UI Open', default=True)
    socket_color = (0.0, 0.0, 0.0, 1.0)

    def draw_color(self, context, node):
        return self.socket_color

    def draw(self, context, layout, node, text):
        layout.label(text=self.name, icon=self.linked_node_icon())

    def get_linked_node(self):
        if self.enabled and self.is_linked and self.links:
            node = self.links[0].from_node
            socket = self.links[0].from_socket

            if node:
                if socket.bl_custom_type == self.bl_custom_type:
                    return node

        return None

    def linked_node_icon(self):
        if self.is_linked and self.links:
            node = self.links[0].from_node
            socket = self.links[0].from_socket

            if node:
                if socket.bl_custom_type == self.bl_custom_type:
                    return 'NONE'

                else:
                    return 'ERROR'

        return 'NONE'


class mitsuba_socket_spectrum(mitsuba_socket):
    bl_static_type = 'RGBA'
    bl_custom_type = 'SPECTRUM'

    draw = draw_color_socket

    def get_spectrum_dict(self, export_ctx, multiplier=1.0):
        spectrum_node = self.get_linked_node()

        if spectrum_node:
            return spectrum_node.get_spectrum_dict(export_ctx, multiplier)

        else:
            value = [x * multiplier for x in self.default_value[:]]
            return export_ctx.spectrum(value)

    def set_spectrum_socket(self, ntree, params, normalize=False):
        if isinstance(params, dict) and 'type' in params:
            if params['type'] in {'rgb', 'spectrum'} and 'value' in params:
                values = [float(x) for x in params['value'].split()]

                if len(values) == 3:
                    maxval = max(values)

                    if maxval <= 1.0:
                        self.default_value = values
                        return 1.0

                    elif normalize:
                        values = [x / maxval for x in values]
                        self.default_value = values
                        return maxval

            elif params['type'] == 'spectrum' and 'filename' in params:
                params['type'] = 'spdfile'

            ntree.new_node_from_dict(params, self)

        else:
            print("Unknown spectrum socket params:", params)

        return 1.0


class mitsuba_socket_color(mitsuba_socket):
    bl_static_type = 'RGBA'
    bl_custom_type = 'COLOR'

    draw = draw_color_socket

    def get_color_dict(self, export_ctx):
        tex_node = self.get_linked_node()

        if tex_node:
            return tex_node.get_color_dict(export_ctx)

        else:
            return export_ctx.spectrum(self.default_value)

    def set_color_socket(self, ntree, params, normalize=False):
        if isinstance(params, dict) and 'type' in params:
            if params['type'] == 'rgb' and 'value' in params:
                values = [float(x) for x in params['value'].split()]

                if len(values) == 3:
                    maxval = max(values)

                    if maxval <= 1.0:
                        self.default_value = values
                        return 1.0

                    elif normalize:
                        values = [x / maxval for x in values]
                        self.default_value = values
                        return maxval

            ntree.new_node_from_dict(params, self)

        else:
            print("Unknown color socket params:", params)

        return 1.0


class mitsuba_socket_float(mitsuba_socket):
    bl_static_type = 'VALUE'
    bl_custom_type = 'FLOAT'

    def draw(self, context, layout, node, text):
        if self.is_linked or self.bl_static_type == 'SHADER':
            layout.label(text=self.name, icon=self.linked_node_icon())

        else:
            layout.prop(self, 'default_value', text=self.name)

    def get_float_dict(self, export_ctx, minval=None):
        tex_node = self.get_linked_node()

        if tex_node:
            return tex_node.get_float_dict(export_ctx)

        else:
            if minval is not None:
                return max(self.default_value, minval)

            else:
                return self.default_value

    def set_float_socket(self, ntree, params):
        if isinstance(params, (float, int)):
            self.default_value = params

        elif isinstance(params, dict) and 'type' in params:
            ntree.new_node_from_dict(params, self)

        else:
            print("Unknown float socket params:", params)


# Basic sockets


mitsuba_socket_definitions = {
    'SPECTRUM': {
        'name': 'MtsSocketSpectrum',
        'label': 'Spectrum',
        'description': 'Connect a Spectrum node to this socket',
        'color': (0.16, 0.78, 0.78, 1.0),  # Custom
        'class': mitsuba_socket_spectrum,
    },
    'COLOR': {
        'name': 'MtsSocketColor',
        'label': 'Color',
        'description': 'Connect a Color node to this socket',
        'color': (0.78, 0.78, 0.16, 1.0),  # Same as SOCK_RGBA
        'class': mitsuba_socket_color,
    },
    'FLOAT': {
        'name': 'MtsSocketFloat',
        'label': 'Value',
        'description': 'Connect a Value node to this socket',
        'color': (0.63, 0.63, 0.63, 1.0),  # Same as SOCK_FLOAT
        'class': mitsuba_socket_float,
    },
    'BSDF': {
        'name': 'MtsSocketBsdf',
        'label': 'Bsdf',
        'description': 'Connect a Bsdf node to this socket',
        'color': (0.39, 0.78, 0.39, 1.0),  # Same as SOCK_SHADER
    },
    'SUBSURFACE': {
        'name': 'MtsSocketSubsurface',
        'label': 'Subsurface',
        'description': 'Connect a Subsurface node to this socket',
        'color': (0.78, 0.39, 0.16, 1.0),  # Custom
    },
    'MEDIUM': {
        'name': 'MtsSocketMedium',
        'label': 'Medium',
        'description': 'Connect an Medium node to this socket',
        'color': (0.16, 0.39, 0.78, 1.0),  # Custom
    },
    'EMITTER': {
        'name': 'MtsSocketEmitter',
        'label': 'Emitter',
        'description': 'Connect an Emitter node to this socket',
        'color': (1.0, 1.0, 1.0, 1.0),  # Custom
    },
    'TEXTURE': {
        'name': 'MtsSocketTexture',
        'label': 'Texture',
        'description': 'Connect a Texture node to this socket',
        'color': (0.16, 0.78, 0.39, 1.0),  # Custom
    },
    'UVMAPPING': {
        'name': 'MtsSocketUVMapping',
        'label': 'UV Mapping',
        'description': 'Connect an UV Mapping node to this socket',
        'color': (0.65, 0.55, 0.75, 1.0),  # Custom
    },
    'LAMP': {
        'name': 'MtsSocketLamp',
        'label': 'Lamp',
        'description': 'Connect a Lamp node to this socket',
        'color': (1.0, 1.0, 1.0, 1.0),  # Custom
    },
    'ENVIRONMENT': {
        'name': 'MtsSocketEnvironment',
        'label': 'Environment',
        'description': 'Connect an Environment node to this socket',
        'color': (1.0, 1.0, 1.0, 1.0),  # Custom
    },
}

for socket_type, socket_params in mitsuba_socket_definitions.items():
    # Register the socket class
    MitsubaSocketTypes.register(type(
        socket_params['name'],
        (socket_params['class'] if 'class' in socket_params else mitsuba_socket, NodeSocket, ),
        {
            'bl_idname': socket_params['name'],
            'bl_label': '%s socket' % socket_params['label'],
            'bl_static_type': 'SHADER',
            'bl_custom_type': socket_type,
            'socket_color': socket_params['color']
        }
    ))

# Spectrum sockets

spectrum_sockets = [
    ColorParams('sigmaS', 'Scattering Coefficient', subtype='NONE', default=(0.8, 0.8, 0.8), precision=6, draw=draw_vector_socket),
    ColorParams('sigmaA', 'Absorption Coefficient', subtype='NONE', default=(0.0, 0.0, 0.0), precision=6, draw=draw_vector_socket),
    ColorParams('g', 'Anisotropy', subtype='NONE', default=(0.0, 0.0, 0.0), min=-0.999999, max=0.999999, precision=6, draw=draw_vector_socket),

    ColorParams('sigmaT', 'Extinction Coefficient', subtype='NONE', default=(0.8, 0.8, 0.8), precision=6, draw=draw_vector_socket),
    ColorParams('albedo', 'Albedo', default=(0.01, 0.01, 0.01)),

    ColorParams('groundAlbedo', 'Ground Albedo', default=(0.15, 0.15, 0.15)),
    ColorParams('colorA', 'Color 1', default=(0.2, 0.2, 0.2)),
    ColorParams('colorB', 'Color 2', default=(0.4, 0.4, 0.4)),
    ColorParams('interiorColor', 'Face Color', default=(0.5, 0.5, 0.5)),
    ColorParams('edgeColor', 'Edge Color', default=(0.1, 0.1, 0.1)),
    ColorParams('radiance', 'Radiance', default=(1.0, 1.0, 1.0)),
    ColorParams('eta', 'IOR', subtype='NONE', default=(0.0, 0.0, 0.0), min=0.0, max=10.0, draw=draw_vector_socket),
    ColorParams('k', 'Absorption Coefficient', default=(1.0, 1.0, 1.0)),
]

for params in spectrum_sockets:
    # Register the socket class
    MitsubaSocketTypes.register(type(
        'MtsSocketSpectrum_%s' % params['attr'],
        (mitsuba_socket_spectrum, NodeSocket, ),
        {
            'bl_idname': 'MtsSocketSpectrum_%s' % params['attr'],
            'bl_label': '%s socket' % params['name'],
            'socket_color': mitsuba_socket_definitions['SPECTRUM']['color'],
            'default_value': FloatVectorProperty(
                name=params['name'],
                description=params['description'],
                default=params['default'],
                subtype=params['subtype'],
                min=params['min'],
                max=params['max'],
            ),
            'draw': params['draw'],
        }
    ))

# Color sockets

color_sockets = [
    ColorParams(
        'diffuseReflectance',
        'Diffuse Reflectance',
        description='Specifies the diffuse albedo of the material.',
        default=(0.5, 0.5, 0.5)
    ),
    ColorParams(
        'specularReflectance',
        'Specular Reflectance',
        description='Optional factor that can be used to modulate the specular reflection component. Note that for physical realism, this parameter should never be touched.',
        default=(1.0, 1.0, 1.0)
    ),
    ColorParams(
        'specularTransmittance',
        'Specular Transmittance',
        description='Optional factor that can be used to modulate the specular transmission component. Note that for physical realism, this parameter should never be touched.',
        default=(1.0, 1.0, 1.0)
    ),
    ColorParams('transmittance', 'Transmittance', default=(0.5, 0.5, 0.5)),
    ColorParams('opacity', 'Opacity Mask', default=(0.5, 0.5, 0.5)),
    ColorParams('sigmaS', 'Scattering Coefficient', subtype='NONE', default=(0.8, 0.8, 0.8), precision=6, draw=draw_vector_socket),
    ColorParams('sigmaA', 'Absorption Coefficient', subtype='NONE', default=(0.0, 0.0, 0.0), precision=6, draw=draw_vector_socket),
    ColorParams('sigmaT', 'Extinction Coefficient', subtype='NONE', default=(0.8, 0.8, 0.8), precision=6, draw=draw_vector_socket),
    ColorParams('albedo', 'Albedo', default=(0.01, 0.01, 0.01)),
]

for params in color_sockets:
    # Register the socket class
    MitsubaSocketTypes.register(type(
        'MtsSocketColor_%s' % params['attr'],
        (mitsuba_socket_color, NodeSocket, ),
        {
            'bl_idname': 'MtsSocketColor_%s' % params['attr'],
            'bl_label': '%s socket' % params['name'],
            'socket_color': mitsuba_socket_definitions['COLOR']['color'],
            'default_value': FloatVectorProperty(
                name=params['name'],
                description=params['description'],
                default=params['default'],
                subtype=params['subtype'],
                min=params['min'],
                max=params['max'],
            ),
            'draw': params['draw'],
        }
    ))

# Float sockets

float_sockets = [
    FloatParams(
        'alpha',
        'Roughness',
        description='Specifies the roughness of the unresolved surface micro-geometry.',
        default=0.0
    ),
    FloatParams(
        'alphaU',
        'Roughness U',
        description='Specifies the roughness of the unresolved surface micro-geometry. When anisotropy is used, specifies the anisotropic roughness value along the tangent direction.',
        default=0.0
    ),
    FloatParams(
        'alphaV',
        'Roughness V',
        description='Specifies the anisotropic roughness value along the bitangent direction.',
        default=0.1
    ),
    FloatParams('exponent', 'Exponent', default=30, max=1000),
    FloatParams('weight', 'Blending factor', default=0.2),
]

for params in float_sockets:
    # Register the socket class
    MitsubaSocketTypes.register(type(
        'MtsSocketFloat_%s' % params['attr'],
        (mitsuba_socket_float, NodeSocket, ),
        {
            'bl_idname': 'MtsSocketFloat_%s' % params['attr'],
            'bl_label': '%s socket' % params['name'],
            'socket_color': mitsuba_socket_definitions['FLOAT']['color'],
            'default_value': FloatProperty(
                name=params['name'],
                description=params['description'],
                default=params['default'],
                subtype=params['subtype'],
                unit=params['unit'],
                min=params['min'],
                max=params['max'],
                precision=params['precision'],
            ),
        }
    ))
