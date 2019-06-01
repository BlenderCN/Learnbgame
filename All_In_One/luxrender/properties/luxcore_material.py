# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# David Bucciarelli
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
class luxcore_material(declarative_property_group):
    """
    Storage class for LuxCore material settings.
    """

    ef_attach_to = ['Material']

    controls = [
        'advanced',
        'id',
        'create_MATERIAL_ID_MASK',
        'create_BY_MATERIAL_ID',
        ['samples', 'emission_samples'],
        'bumpsamplingdistance',
        'label_material_visibility',
        ['visibility_indirect_diffuse_enable', 'visibility_indirect_glossy_enable', 'visibility_indirect_specular_enable'],
    ]

    visibility = {
        'samples': {ScenePrefix() + 'luxcore_enginesettings.renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])},
        'bumpsamplingdistance': {'advanced': True},
        'label_material_visibility': {
        ScenePrefix() + 'luxcore_enginesettings.renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])},
        'emission_samples': {
        ScenePrefix() + 'luxcore_enginesettings.renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])},
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
            'type': 'bool',
            'attr': 'advanced',
            'name': 'Advanced Settings',
            'description': 'Configure advanced LuxCore material settings',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'id',
            'name': 'Material ID',
            'description': 'Material ID (-1 = auto), used for AOVs',
            'default': -1,
            'min': -1,
            'max': 65536,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'emission_id',
            'name': 'Emission ID',
            'description': 'Material emission ID (-1 = automatic), used for AOVs',
            'default': -1,
            'min': -1,
            'max': 65536,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'create_MATERIAL_ID_MASK',
            'name': 'MATERIAL_ID_MASK pass',
            'description': 'Create a mask for this material (AOV channel)',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'create_BY_MATERIAL_ID',
            'name': 'BY_MATERIAL_ID pass',
            'description': 'Create a pass containing only objects with this material ID (AOV channel)',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'samples',
            'name': 'Samples',
            'description': 'Material samples count (-1 = global default, size x size)',
            'default': -1,
            'min': -1,
            'max': 256,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'emission_samples',
            'name': 'Emission samples',
            'description': 'Material emission samples count (-1 = global default, size x size)',
            'default': -1,
            'min': -1,
            'max': 256,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'bumpsamplingdistance',
            'name': 'Bump mapping sampling distance',
            'description': 'Bump mapping sampling distance',
            'default': 0.001,
            'min': 0.00001,
            'max': 1000.0,
            'save_in_preset': True
        },
        {
            'type': 'text',
            'attr': 'label_material_visibility',
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
