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
from ..extensions_framework.validate import Logic_OR as O, Logic_Operator as LO, Logic_AND as A

from .. import PBRTv3Addon


@PBRTv3Addon.addon_register_class
class luxcore_translatorsettings(declarative_property_group):
    """
    Storage class for PBRTv3Core translator settings.
    """

    ef_attach_to = ['Scene']

    controls = [
        ['export_particles', 'export_hair', 'export_proxies'],
        'override_materials',
        ['override_glass', 'override_lights', 'override_null'],
        ['label_debug', 'print_cfg', 'print_scn'],
        'use_rtpathcpu',
    ]

    visibility = {
        'override_glass': {'override_materials': True},
        'override_lights': {'override_materials': True},
        'override_null': {'override_materials': True},
    }

    alert = {}

    properties = [
        {
            'type': 'bool',
            'attr': 'export_particles',
            'name': 'Particles',
            'description': 'Export particle systems',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'export_hair',
            'name': 'Hair',
            'description': 'Export hair systems',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'export_proxies',
            'name': 'Proxies',
            'description': 'Load linked PLY files for proxy objects',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'override_materials',
            'name': 'Override Materials (Clay Render)',
            'description': 'Replace all scene materials with a white matte material',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'override_glass',
            'name': 'Glass',
            'description': 'Replace glass materials with clay',
            'default': False,
            'toggle': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'override_lights',
            'name': 'Emission',
            'description': 'Replace light emitting materials with clay (turning them off)',
            'default': False,
            'toggle': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'override_null',
            'name': 'Null',
            'description': 'Replace null materials with clay',
            'default': False,
            'toggle': True,
            'save_in_preset': True
        },
        {
            'type': 'text',
            'attr': 'label_debug',
            'name': 'Debug:',
            'icon': 'CONSOLE',
        },
        {
            'type': 'bool',
            'attr': 'print_cfg',
            'name': 'Print CFG',
            'description': 'Print generated renderconfig in system console',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'print_scn',
            'name': 'Print SCN',
            'description': 'Print generated sceneconfig in system console',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'export_type',
            'name': 'Export Type',
            'description': 'How to export and render the scene',
            'default': 'internal',
            'items': [
                ('internal', 'Internal', 'Do not export any files, render inside of Blender'),
                ('luxcoreui', 'PBRTv3CoreUI', 'Export scene files to output path and render using PBRTv3CoreUI'),
            ],
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'run_luxcoreui',
            'name': 'Run PBRTv3CoreUI',
            'description': 'After exporting, start PBRTv3CoreUI with the exported scene files',
            'default': True,
            'save_in_preset': True
        },
        {   # TODO: remove when daily builds catch up
            'type': 'bool',
            'attr': 'use_rtpathcpu',
            'name': 'Use RTPathCPU',
            'description': 'Use RTPathCPU instead of PathCPU for viewport render. Note that you need to compile the '
                           'very latest PBRTv3Core from source for this to work, daily builds do not contain it yet',
            'default': False,
        },
    ]
