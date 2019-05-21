# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond, Michael Klemm
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
import math
import os

import bpy

from ..extensions_framework import util as efutil
from ..extensions_framework import declarative_property_group
from ..extensions_framework.validate import Logic_OR as O

from .. import LuxRenderAddon
from ..export import get_worldscale, get_output_filename
from ..export import ParamSet, LuxManager
from ..export import fix_matrix_order
from ..outputs.pure_api import LUXRENDER_VERSION


@LuxRenderAddon.addon_register_class
class luxrender_hair(declarative_property_group):
    """
    Storage class for LuxRender Hair Rendering settings.
    """
    ef_attach_to = ['ParticleSettings']
    controls = [
        'hair_size',
        ['root_width', 'tip_width', 'width_offset'],
        'use_binary_output',
        'tesseltype',
        'solid_sidecount',
        ['solid_capbottom', 'solid_captop'],
        'adaptive_maxdepth',
        'adaptive_error',
        'acceltype',
        'export_color',
    ]

    visibility = {
        'adaptive_maxdepth': {'tesseltype': O(['ribbonadaptive', 'solidadaptive'])},
        'adaptive_error': {'tesseltype': O(['ribbonadaptive', 'solidadaptive'])},
        'solid_sidecount': {'tesseltype': O(['solid', 'solidadaptive'])},
        'solid_capbottom': {'tesseltype': O(['solid', 'solidadaptive'])},
        'solid_captop': {'tesseltype': O(['solid', 'solidadaptive'])},

    }

    properties = [
        {
            'type': 'float',
            'attr': 'hair_size',
            'name': 'Hair Size',
            'description': 'Thickness of hair',
            'default': 0.001,
            'min': 0.000001,
            'soft_min': 0.000001,
            'max': 1000.0,
            'soft_max': 1000.0,
            'precision': 3,
            'sub_type': 'DISTANCE',
            'unit': 'LENGTH',
        },
        {
            'type': 'float',
            'attr': 'root_width',
            'name': 'Root',
            'description': 'Thickness of hair at root',
            'default': 1.0,
            'min': 0.000001,
            'soft_min': 0.000001,
            'max': 1.0,
            'soft_max': 1.0,
            'precision': 3,
        },
        {
            'type': 'float',
            'attr': 'tip_width',
            'name': 'Tip',
            'description': 'Thickness of hair at tip',
            'default': 1.0,
            'min': 0.000001,
            'soft_min': 0.000001,
            'max': 1.0,
            'soft_max': 1.0,
            'precision': 3
        },
        {
            'type': 'float',
            'attr': 'width_offset',
            'name': 'Offset',
            'description': 'Offset from root for thickness variation',
            'default': 0.0,
            'min': 0.000001,
            'soft_min': 0.000001,
            'max': 1.0,
            'soft_max': 1.0,
            'precision': 3
        },
        {
            'type': 'bool',
            'attr': 'use_binary_output',
            'name': 'Use Binary Strand Primitive',
            'description': 'Use binary hair description file and strand primitive for export',
            'default': True,
        },
        {
            'type': 'enum',
            'attr': 'tesseltype',
            'name': 'Tessellation Type',
            'description': 'Tessellation method for hair strands',
            'default': 'ribbonadaptive',
            'items': [
                ('ribbon', 'Triangle Ribbon', 'Render hair as ribbons of triangles facing the camera'),
                ('ribbonadaptive', 'Adaptive Triangle Ribbon',
                 'Render hair as ribbons of triangles facing the camera, with adaptive tessellation'),
                ('solid', 'Solid', 'Render hairs as solid mesh cylinders (memory intensive!)'),
                ('solidadaptive', 'Adaptive Solid', 'Render hairs as solid mesh cylinders with adaptive tesselation'),
            ],
        },
        {
            'type': 'int',
            'attr': 'adaptive_maxdepth',
            'name': 'Max Tessellation Depth',
            'description': 'Maximum tessellation depth for adaptive modes.',
            'default': 8,
            'min': 1,
            'soft_min': 2,
            'max': 24,
            'soft_max': 12,
        },
        {
            'type': 'int',
            'attr': 'solid_sidecount',
            'name': 'Number of Sides',
            'description': 'Number of sides for each hair cylinder',
            'default': 3,
            'min': 3,
            'soft_min': 3,
            'max': 64,
            'soft_max': 8,
        },
        {
            'type': 'bool',
            'attr': 'solid_capbottom',
            'name': 'Cap Root',
            'description': 'Add a base cap to each hair cylinder',
            'default': False,
        },
        {
            'type': 'bool',
            'attr': 'solid_captop',
            'name': 'Cap Tip',
            'description': 'Add an end cap to each hair cylinder',
            'default': False,
        },
        {
            'type': 'float',
            'attr': 'adaptive_error',
            'name': 'Max Tessellation Error',
            'description': 'Maximum tessellation error for adaptive modes',
            'default': 0.1,
            'min': 0.001,
            'max': 0.9,
        },
        {
            'type': 'enum',
            'attr': 'acceltype',
            'name': 'Hair Accelerator',
            'description': 'Acceleration structure used for this hair system',
            'default': 'qbvh',
            'items': [
                ('qbvh', 'QBVH', 'SSE-accelerated quad bounding volume hierarchy'),
                ('kdtree', 'KD-Tree', 'KD-Tree'),
            ],
        },
        {
            'type': 'enum',
            'attr': 'export_color',
            'name': 'Color Export Mode',
            'desciption': 'Mode of color export for the hair file',
            'default': 'none',
            'items': [
                ('vertex_color', 'Vertex Color', 'Use vertex color as hair color'),
                ('uv_texture_map', 'UV Texture Map', 'Use UV texture map as hair color'),
                ('none', 'None', 'none'),
            ],
        }
    ]


