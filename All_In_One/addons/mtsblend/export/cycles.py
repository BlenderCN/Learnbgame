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

from collections import OrderedDict

RoughnessMode = {'GGX': 'ggx', 'SHARP': 'beckmann', 'BECKMANN': 'beckmann'}


def IOR_transform(node):
    params = {}

    if node.inputs['IOR'].is_linked:
        pass    # it is not supported in mitsuba

    else:
        value = node.inputs['IOR'].default_value

        if value == 1.0:
            params = {
                'intIOR': 1.0,
                'type': 'thindielectric',
            }

        elif value < 1.0:
            params = {
                'intIOR': 1.0,
                'extIOR': 1.0 / value,
            }

        else:
            params = {
                'intIOR': value,
            }

    return params


def convert_float_texture_node(export_ctx, socket):
    params = None

    if socket.is_linked:
        node = socket.links[0].from_node

        if node.type == "TEX_IMAGE":
            params = {
                'type': 'bitmap',
                'image': node.image
            }

    else:
        params = socket.default_value

    return params


def convert_color_texture_node(export_ctx, socket):
    params = None

    if socket.is_linked:
        node = socket.links[0].from_node

        if node.type == "TEX_IMAGE":
            params = {
                'type': 'bitmap',
                'image': node.image
            }

    else:
        params = export_ctx.spectrum(socket.default_value)

    return params


def convert_diffuse_materials_cycles(export_ctx, currentNode):
    params = {}

    roughness = convert_float_texture_node(export_ctx, currentNode.inputs['Roughness'])
    if roughness:
        params.update({
            'type': 'roughdiffuse',
            'alpha': roughness,
            'distribution': 'beckmann',
        })

    else:
        params.update({
            'type': 'diffuse',
        })

    reflectance = convert_color_texture_node(export_ctx, currentNode.inputs['Color'])

    if reflectance is not None:
        params.update({
            'reflectance': reflectance,
        })

    return params


def convert_glossy_materials_cycles(export_ctx, currentNode):
    params = {'material': 'none'}

    roughness = convert_float_texture_node(export_ctx, currentNode.inputs['Roughness'])

    if roughness:
        params.update({
            'type': 'roughconductor',
            'alpha': roughness,
            'distribution': RoughnessMode[currentNode.distribution],
        })

    else:
        params.update({
            'type': 'conductor',
        })

    specular_reflectance = convert_color_texture_node(export_ctx, currentNode.inputs['Color'])

    if specular_reflectance is not None:
        params.update({
            'specularReflectance': specular_reflectance,
        })

    return params


def convert_glass_materials_cycles(export_ctx, currentNode):
    params = IOR_transform(currentNode)

    if 'type' not in params:
        roughness = convert_float_texture_node(export_ctx, currentNode.inputs['Roughness'])

        if roughness:
            params.update({
                'type': 'roughdielectric',
                'alpha': roughness,
                'distribution': RoughnessMode[currentNode.distribution],
            })

        else:
            params.update({
                'type': 'dielectric',
            })

    specular_transmittance = convert_color_texture_node(export_ctx, currentNode.inputs['Color'])

    if specular_transmittance is not None:
        params.update({
            'specularTransmittance': specular_transmittance,
        })

    return params


def convert_transparent_materials_cycles(export_ctx, currentNode):
    params = {
        'type': 'thindielectric',
        'intIOR': 1.0,
    }

    specular_transmittance = convert_color_texture_node(export_ctx, currentNode.inputs['Color'])

    if specular_transmittance is not None:
        params.update({
            'specularTransmittance': specular_transmittance,
        })

    return params


def convert_translucent_materials_cycles(export_ctx, currentNode):
    params = {
        'type': 'difftrans',
    }

    transmittance = convert_color_texture_node(export_ctx, currentNode.inputs['Color'])

    if transmittance is not None:
        params.update({
            'transmittance': transmittance,
        })

    return params


def convert_refraction_materials_cycles(export_ctx, currentNode):
    params = IOR_transform(currentNode)

    if 'type' not in params:
        roughness = convert_float_texture_node(export_ctx, currentNode.inputs['Roughness'])

        if roughness:
            params.update({
                'type': 'roughdielectric',
                'alpha': roughness,
                'distribution': RoughnessMode[currentNode.distribution],
            })

        else:
            params.update({
                'type': 'dielectric',
            })

    specular_transmittance = convert_color_texture_node(export_ctx, currentNode.inputs['Color'])

    if specular_transmittance is not None:
        params.update({
            'specularTransmittance': specular_transmittance,
        })

    return params


def convert_emitter_materials_cycles(export_ctx, currentNode):
    radiance = 10

    if  currentNode.inputs["Strength"].is_linked:
        pass  # it is not supported in mitsuba

    else:
        radiance = radiance * currentNode.inputs["Strength"].default_value

    if currentNode.inputs['Color'].is_linked:
        pass  # it is not supported in mitsuba

    else:
        radiance = [x * radiance for x in currentNode.inputs["Color"].default_value[:]]

    params = {
        'type': 'area',
        'radiance': export_ctx.spectrum(radiance),
    }

    return params


def convert_mix_materials_cycles(export_ctx, currentNode):
    addShader = (currentNode.type == 'ADD_SHADER')

    # in the case of AddShader 1-True = 0
    mat_I = currentNode.inputs[1 - addShader].links[0].from_node
    mat_II = currentNode.inputs[2 - addShader].links[0].from_node

    #TODO: XOR would be better in case of two emission type material
    emitter = ((mat_I.type == 'EMISSION') or (mat_II.type == 'EMISSION'))

    if emitter:
        params = cycles_material_to_dict(export_ctx, mat_I)
        params.update(cycles_material_to_dict(export_ctx, mat_II))

        return params

    else:
        if addShader:
            weight = 0.5

        else:
            weight = currentNode.inputs['Fac'].default_value

        params = OrderedDict([
            ('type', 'blendbsdf'),
            ('weight', weight),
        ])

        # add first material
        mat_A = cycles_material_to_dict(export_ctx, mat_I)
        params.update([
            ('bsdf1', mat_A['bsdf'])
        ])

        # add second materials
        mat_B = cycles_material_to_dict(export_ctx, mat_II)
        params.update([
            ('bsdf2', mat_B['bsdf'])
        ])

        return params

#TODO: Add more support for other materials
cycles_converters = {
    "BSDF_DIFFUSE": convert_diffuse_materials_cycles,
    'BSDF_GLOSSY': convert_glossy_materials_cycles,
    'BSDF_GLASS': convert_glass_materials_cycles,
    'EMISSION': convert_emitter_materials_cycles,
    'MIX_SHADER': convert_mix_materials_cycles,
    'BSDF_TRANSPARENT': convert_transparent_materials_cycles,
    'BSDF_REFRACTION': convert_refraction_materials_cycles,
    'BSDF_TRANSLUCENT': convert_translucent_materials_cycles,
    'ADD_SHADER': convert_mix_materials_cycles,
}


def cycles_material_to_dict(export_ctx, node):
    ''' Converting one material from Blender to Mitsuba dict'''
    params = {}

    if node.type in cycles_converters:
        params = cycles_converters[node.type](export_ctx, node)

    mat_params = {}

    if 'type' in params:
        if params['type'] == 'area':
            mat_params.update({
                'emitter': params
            })

        else:
            mat_params.update({
                'bsdf': params
            })

    else:
        mat_params = params

    return mat_params
