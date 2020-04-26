# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
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

from .. import LuxRenderAddon


@LuxRenderAddon.addon_register_class
class luxcore_translatorsettings(declarative_property_group):
    """
    Storage class for LuxCore translator settings.
    """

    ef_attach_to = ['Scene']

    controls = [
        ['export_particles', 'export_hair'],
        'override_materials',
        ['override_glass', 'override_lights', 'override_null'],
        'use_filesaver',
        'label_debug',
        'print_config'
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
            'name': 'Export Particles',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'export_hair',
            'name': 'Export Hair',
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
            'type': 'bool',
            'attr': 'use_filesaver',
            'name': 'Only Export Files',
            'description': 'Instead of rendering, only export CFG/SCN files, meshes and textures to output path',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'text',
            'attr': 'label_debug',
            'name': 'Debug:',
        },
        {
            'type': 'bool',
            'attr': 'print_config',
            'name': 'Print Config in Terminal',
            'description': 'Print generated renderconfig and sceneconfig in system console',
            'default': False,
            'save_in_preset': True
        },
    ]
