# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# David Bucciarelli, Simon Wendsche
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

from ..extensions_framework import declarative_property_group
from ..extensions_framework.validate import Logic_OR as O, Logic_Operator as LO

from .. import LuxRenderAddon
from ..outputs.luxcore_api import ScenePrefix


@LuxRenderAddon.addon_register_class
class luxcore_lamp(declarative_property_group):
    """
    Storage class for LuxCore lamp settings.
    """

    ef_attach_to = ['luxrender_lamp']

    controls = [
        'label_light_visibility',
        ['visibility_indirect_diffuse_enable', 'visibility_indirect_glossy_enable', 'visibility_indirect_specular_enable'],
    ]

    visibility = {
        'label_light_visibility':
            {ScenePrefix() + 'luxcore_enginesettings.renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])},
        'visibility_indirect_diffuse_enable':
            {ScenePrefix() + 'luxcore_enginesettings.renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])},
        'visibility_indirect_glossy_enable':
            {ScenePrefix() + 'luxcore_enginesettings.renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])},
        'visibility_indirect_specular_enable':
            {ScenePrefix() + 'luxcore_enginesettings.renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])},
    }

    alert = {}

    properties = [
        {
            'type': 'text',
            'attr': 'label_light_visibility',
            'name': 'Visibility for indirect rays:'
        },
        {
            'type': 'bool',
            'attr': 'visibility_indirect_diffuse_enable',
            'name': 'Diffuse',
            'description': 'Enable material visibility for indirect rays',
            'default': True,
            'toggle': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'visibility_indirect_glossy_enable',
            'name': 'Glossy',
            'description': 'Enable material visibility for glossy rays',
            'default': True,
            'toggle': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'visibility_indirect_specular_enable',
            'name': 'Specular',
            'description': 'Enable material visibility for specular rays',
            'default': True,
            'toggle': True,
            'save_in_preset': True
        },
    ]
