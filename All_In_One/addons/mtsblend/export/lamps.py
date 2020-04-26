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

import math

import mathutils

from ..export import compute_normalized_radiance
from ..outputs.file_api import FileExportContext


def lamp_dict_to_nodes(ntree, params):
    shader = None

    if params['type'] == 'rectangle':
        shader = ntree.nodes.new('MtsNodeEmitter_area')
        radiance = [float(x) for x in params['emitter']['radiance']['value'].split()]
        toworld = params['toWorld']

        if toworld['type'] == 'scale':
            if 'value' in toworld:
                shader.width = toworld['value'] * 2
                shader.shape = 'square'

            else:
                shader.width = toworld['x'] * 2
                shader.height = toworld['y'] * 2
                shader.shape = 'rectangle'

    elif params['type'] == 'sphere':
        shader = ntree.nodes.new('MtsNodeEmitter_point')
        shader.size = params['radius'] * 2
        radiance = [float(x) for x in params['emitter']['radiance']['value'].split()]

    elif params['type'] == 'point':
        shader = ntree.nodes.new('MtsNodeEmitter_point')
        shader.size = 0
        radiance = [float(x) for x in params['intensity']['value'].split()]

    elif params['type'] == 'spot':
        shader = ntree.nodes.new('MtsNodeEmitter_spot')
        shader.cutoffAngle = params['cutoffAngle']
        shader.spotBlend = 1 - (params['beamWidth'] / params['cutoffAngle'])
        radiance = [float(x) for x in params['intensity']['value'].split()]

    elif params['type'] == 'directional':
        shader = ntree.nodes.new('MtsNodeEmitter_directional')
        radiance = [float(x) for x in params['irradiance']['value'].split()]

    if shader:

        if 'emitter' in params and 'scale' in params['emitter']:
            shader.inputs['Radiance'].default_value = [x / params['emitter']['scale'] for x in radiance]
            shader.scale = params['emitter']['scale']

        elif 'scale' in params:
            shader.inputs['Radiance'].default_value = [x / params['scale'] for x in radiance]
            shader.scale = params['scale']

        else:
            compute_normalized_radiance(shader, radiance)

    return shader


def blender_lamp_to_dict(export_ctx, lamp):
    if export_ctx is None:
        export_ctx = FileExportContext()

    params = {}

    if lamp.type == 'AREA':

        if lamp.shape == 'RECTANGLE':
            boost = max(1, 1 / lamp.size * lamp.size_y) * 20
            toworld = {
                'type': 'scale',
                'x': lamp.size / 2.0,
                'y': lamp.size_y / 2.0,
            }

        else:
            boost = max(1, 1 / lamp.size * lamp.size) * 20
            toworld = {
                'type': 'scale',
                'value': lamp.size / 2.0,
            }

        params = {
            'type': 'rectangle',
            'toWorld': toworld,
            'emitter': {
                'type': 'area',
                'radiance': export_ctx.spectrum(lamp.color * lamp.energy * boost),
                'scale': lamp.energy * boost,
            },
            'bsdf': {
                'type': 'diffuse',
                'reflectance': export_ctx.spectrum(lamp.color),
            },
        }

    elif lamp.type == 'POINT':
        params = {'id': '%s-pointlight' % lamp.name}

        if lamp.shadow_soft_size >= 0.01:
            radius = lamp.shadow_soft_size / 2.0
            boost = max(1.0, 1 / (4 * math.pi * radius * radius)) * 20
            params.update({
                'type': 'sphere',
                'radius': radius,
                'emitter': {
                    'type': 'area',
                    'radiance': export_ctx.spectrum(lamp.color * lamp.energy * boost),
                    'scale': lamp.energy * boost,
                },
                'bsdf': {
                    'type': 'diffuse',
                    'reflectance': export_ctx.spectrum(lamp.color),
                },
            })

        else:
            params.update({
                'type': 'point',
                'intensity': export_ctx.spectrum(lamp.color * lamp.energy * 20),
                'scale': lamp.energy * 20,
            })

    elif lamp.type == 'SPOT':
        params = {
            'type': 'spot',
            'cutoffAngle': lamp.spot_size * 180 / (math.pi * 2.0),
            'beamWidth': (1 - lamp.spot_blend) * (lamp.spot_size * 180 / (math.pi * 2.0)),
            'intensity': export_ctx.spectrum(lamp.color * lamp.energy * 20),
            'scale': lamp.energy * 20,
        }

    elif lamp.type in {'SUN', 'HEMI'}:
        params = {
            'type': 'directional',
            'irradiance': export_ctx.spectrum(lamp.color * lamp.energy),
            'scale': lamp.energy,
        }

    return params


def blender_lamp_to_nodes(ntree, lamp):
    params = blender_lamp_to_dict(None, lamp)

    if params:
        return lamp_dict_to_nodes(ntree, params)

    return None


def export_lamp_instance(export_ctx, instance, name):
    lamp = instance.obj.data

    ntree = lamp.mitsuba_nodes.get_node_tree()
    params = {}

    if ntree:
        params = ntree.get_nodetree_dict(export_ctx, lamp)

    if not params:
        params = blender_lamp_to_dict(export_ctx, lamp)

        if params['type'] in {'rectangle', 'sphere'}:
            del params['emitter']['scale']

        else:
            del params['scale']

    if params and 'type' in params:
        try:
            hide_emitters = export_ctx.scene_data['integrator']['hideEmitters']

        except:
            hide_emitters = False

        if params['type'] in {'rectangle', 'disk'}:
            toworld = params.pop('toWorld')

            if 'value' in toworld:
                size_x = size_y = toworld['value']

            else:
                size_x = toworld['x']
                size_y = toworld['y']

            params.update({
                'id': '%s-arealight' % name,
                'toWorld': export_ctx.animated_transform(
                    [(t, m * mathutils.Matrix(((size_x, 0, 0, 0), (0, size_y, 0, 0), (0, 0, -1, 0), (0, 0, 0, 1)))) for (t, m) in instance.motion]
                ),
            })

            if hide_emitters:
                params.update({'bsdf': {'type': 'null'}})

        elif params['type'] in {'point', 'sphere'}:
            params.update({
                'id': '%s-pointlight' % name,
                'toWorld': export_ctx.animated_transform(instance.motion),
            })

            if hide_emitters:
                params.update({'bsdf': {'type': 'null'}})

        elif params['type'] in {'spot', 'directional', 'collimated'}:
            params.update({
                'id': '%s-%slight' % (name, params['type']),
                'toWorld': export_ctx.animated_transform(
                    [(t, m * mathutils.Matrix(((-1, 0, 0, 0), (0, 1, 0, 0), (0, 0, -1, 0), (0, 0, 0, 1)))) for (t, m) in instance.motion]
                ),
            })

        export_ctx.data_add(params)
