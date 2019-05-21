# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Simon Wendsche (BYOB)
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

from .. import PBRTv3Addon


@PBRTv3Addon.addon_register_class
class luxcore_rendering_controls(declarative_property_group):
    """
    Storage class for settings that can be changed during the rendering process,
    e.g. pause/resume, tonemapping settings and other imagepipeline options
    """
    
    ef_attach_to = ['Scene']
    alert = {}

    controls = [
        'stats_samples',
        'stats_samples_per_sec',
        'stats_rays_per_sample',
        'stats_convergence',
        'stats_memory',
        'stats_tris',
        'stats_engine_info',
        'stats_tiles',
    ]
    
    visibility = {

    }

    properties = [
        {
            'type': 'bool',
            'attr': 'pause_render',
            'name': 'Pause Render',
            'description': 'Pause/resume rendering without losing sampling progress',
            'default': False
        },
        {
            'type': 'bool',
            'attr': 'pause_viewport_render',
            'name': 'Pause Preview',
            'description': 'Pause all viewport render sessions',
            'default': False
        },
        {
            'type': 'bool',
            'attr': 'stats_samples',
            'name': 'Samples',
            'description': '',
            'default': True,
        },
        {
            'type': 'bool',
            'attr': 'stats_convergence',
            'name': 'Convergence',
            'description': 'Level of noise convergence, 1.0 = not converged, 0.0 = fully converged',
            'default': False,
        },
        {
            'type': 'bool',
            'attr': 'stats_samples_per_sec',
            'name': 'Samples/Sec',
            'description': '',
            'default': True,
        },
        {
            'type': 'bool',
            'attr': 'stats_rays_per_sample',
            'name': 'Rays/Sample',
            'description': '',
            'default': False,
        },
        {
            'type': 'bool',
            'attr': 'stats_memory',
            'name': 'VRAM Usage',
            'description': 'Amount of GPU RAM used by PBRTv3Core (only available when using an OpenCL engine)',
            'default': True,
        },
        {
            'type': 'bool',
            'attr': 'stats_tris',
            'name': 'Triangles',
            'description': 'Amount of triangles in the scene',
            'default': True,
        },
        {
            'type': 'bool',
            'attr': 'stats_engine_info',
            'name': 'Engine Info',
            'description': 'Information about the engine and sampler used to render the image',
            'default': True,
        },
        {
            'type': 'bool',
            'attr': 'stats_tiles',
            'name': 'Tile Info',
            'description': 'Tile convergence status (only available when using Biased Path engine)',
            'default': True,
        },
    ]
