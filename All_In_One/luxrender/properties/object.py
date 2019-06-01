# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond
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
from ..extensions_framework import declarative_property_group

import math

from .. import LuxRenderAddon
from ..extensions_framework.validate import Logic_OR as O


@LuxRenderAddon.addon_register_class
class luxrender_object(declarative_property_group):
    ef_attach_to = ['Object']

    controls = [
        ['append_proxy', 'hide_proxy_mesh'],
        'proxy_type',
        'use_smoothing',
        'external_mesh',
        ['radius', 'phimax'],
        ['zmin', 'zmax'],
    ]
    visibility = {
        'proxy_type': {'append_proxy': True},
        'hide_proxy_mesh': {'append_proxy': True},
        'use_smoothing': {'append_proxy': True, 'proxy_type': O(['plymesh', 'stlmesh'])},
        'external_mesh': {'append_proxy': True, 'proxy_type': O(['plymesh', 'stlmesh'])},
        'radius': {'append_proxy': True, 'proxy_type': O(['sphere', 'cylinder', 'cone', 'disk', 'paraboloid'])},
        'phimax': {'append_proxy': True, 'proxy_type': O(['sphere', 'cylinder', 'cone', 'disk', 'paraboloid'])},
        'zmin': {'append_proxy': True, 'proxy_type': 'cylinder'},
        'zmax': {'append_proxy': True, 'proxy_type': O(['cylinder', 'paraboloid'])},
    }
    properties = [
        {
            'type': 'bool',
            'attr': 'append_proxy',
            'name': 'Use As Proxy',
            'description': 'Use this object to place a primitive or external mesh file in the scene',
            'default': False
        },
        {
            'type': 'bool',
            'attr': 'hide_proxy_mesh',
            'name': 'Don\'t Render Original',
            'description': 'Replace Blender proxy object with selected Lux object. Disable to render both objects',
            'default': True
        },
        {
            'type': 'enum',
            'attr': 'proxy_type',
            'name': 'Render Object',
            'items': [
                ('plymesh', 'PLY Mesh', 'Load a PLY mesh file'),
                ('stlmesh', 'STL Mesh', 'Load an STL mesh file'),
                ('sphere', 'Sphere', 'Geometric sphere primitive'),
                ('cylinder', 'Cylinder', 'Geometric cylinder primitive'),
                ('cone', 'Cone', 'Geometric cone primitive'),
                ('disk', 'Disk', 'Geometric disk primitive'),
                ('paraboloid', 'Paraboloid', 'Geometric paraboloid primitive'),
            ],
            # If you add items to this, be sure they are the actual names of the primitives, this string
            # is written directly to the scene file in export/geometry/buildMesh!
            'default': 'plymesh'
        },
        {
            'type': 'bool',
            'attr': 'use_smoothing',
            'name': 'Use Smoothing',
            'description': 'Apply normal smoothing to the external mesh',
            'default': False
        },
        {
            'type': 'string',
            'subtype': 'FILE_PATH',
            'attr': 'external_mesh',
            'name': 'Mesh file',
            'description': 'External mesh file to place in scene',
        },
        {
            'type': 'float',
            'attr': 'radius',
            'name': 'Radius',
            'description': 'Radius of the object',
            'default': 1.0,
            'min': 0.00001,
            'subtype': 'DISTANCE',
            'unit': 'LENGTH',
        },
        {
            'type': 'float',
            'attr': 'phimax',
            'name': 'Phi Max',
            'description': 'Angle swept out by the sphape',
            'precision': 1,
            'default': 2 * math.pi,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 2 * math.pi,
            'soft_max': 2 * math.pi,
            'subtype': 'ANGLE',
            'unit': 'ROTATION'
        },
        {
            'type': 'float',
            'attr': 'zmin',
            'name': 'Z Min',
            'description': 'Distance to base of the shape along its Z axis',
            'default': -1.0,
            'max': 0.0,
            'subtype': 'DISTANCE',
            'unit': 'LENGTH',
        },
        {
            'type': 'float',
            'attr': 'zmax',
            'name': 'Z Max',
            'description': 'Distance to top of the shape along its Z axis',
            'default': 1.0,
            'min': 0.0,
            'subtype': 'DISTANCE',
            'unit': 'LENGTH',
        },
        {
            'type': 'float',
            'attr': 'radius',
            'name': 'Radius',
            'description': 'Radius of the object',
            'default': 1.0,
            'min': 0.00001,
            'subtype': 'DISTANCE',
            'unit': 'LENGTH',
        },
    ]
