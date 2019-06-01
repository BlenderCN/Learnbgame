# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
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

from .. import PBRTv3Addon
from ..outputs.luxcore_api import ScenePrefix


@PBRTv3Addon.addon_register_class
class luxcore_lamp(declarative_property_group):
    """
    Storage class for PBRTv3Core lamp settings.
    """

    ef_attach_to = ['pbrtv3_lamp']

    controls = [
        ['label_rgb_gain', 'gain_r', 'gain_g', 'gain_b'],
        'label_message',
        'samples',
        'label_light_visibility',
        ['visibility_indirect_diffuse_enable', 'visibility_indirect_glossy_enable', 'visibility_indirect_specular_enable'],
    ]

    visibility = {}

    enabled = {
        'samples': {ScenePrefix() + 'luxcore_enginesettings.renderengine_type': 'TILEPATH'},
        'label_light_visibility': {ScenePrefix() + 'luxcore_enginesettings.renderengine_type': 'TILEPATH'},
        'visibility_indirect_diffuse_enable': {ScenePrefix() + 'luxcore_enginesettings.renderengine_type': 'TILEPATH'},
        'visibility_indirect_glossy_enable': {ScenePrefix() + 'luxcore_enginesettings.renderengine_type': 'TILEPATH'},
        'visibility_indirect_specular_enable': {ScenePrefix() + 'luxcore_enginesettings.renderengine_type': 'TILEPATH'},
    }

    alert = {}

    properties = [
        {
            'type': 'text',
            'attr': 'label_rgb_gain',
            'name': 'RGB Gain:'
        },
        {
            'type': 'float',
            'attr': 'gain_r',
            'name': 'R',
            'description': 'Red multiplier',
            'default': 1,
            'min': 0.0,
            'soft_max': 1000.0,
        },
        {
            'type': 'float',
            'attr': 'gain_g',
            'name': 'G',
            'description': 'Green multiplier',
            'default': 1,
            'min': 0.0,
            'soft_max': 1000.0,
        },
        {
            'type': 'float',
            'attr': 'gain_b',
            'name': 'B',
            'description': 'Blue multiplier',
            'default': 1,
            'min': 0.0,
            'soft_max': 1000.0,
        },
        {
            'type': 'int',
            'attr': 'samples',
            'name': 'Samples',
            'description': 'Light samples count (-1 = global default, size x size)',
            'default': -1,
            'min': -1,
            'soft_max': 16,
            'max': 256,
        },
        {
            'type': 'text',
            'attr': 'label_message',
            'name': 'Biased Path specific settings:'
        },
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
        },
        {
            'type': 'bool',
            'attr': 'visibility_indirect_glossy_enable',
            'name': 'Glossy',
            'description': 'Enable material visibility for glossy rays',
            'default': True,
        },
        {
            'type': 'bool',
            'attr': 'visibility_indirect_specular_enable',
            'name': 'Specular',
            'description': 'Enable material visibility for specular rays',
            'default': True,
        },
    ]
