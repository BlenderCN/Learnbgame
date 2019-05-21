# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
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

import bpy

from ..extensions_framework import declarative_property_group
from ..extensions_framework.validate import Logic_OR as O, Logic_Operator as LO

from .. import PBRTv3Addon
from ..outputs.luxcore_api import ScenePrefix


@PBRTv3Addon.addon_register_class
class luxcore_material(declarative_property_group):
    """
    Storage class for PBRTv3Core material settings.
    """

    ef_attach_to = ['Material']

    controls = [
        'materialgroup_chooser',
        ['is_shadow_catcher', 'sc_onlyinfinitelights'],
        #'id',
        #'create_MATERIAL_ID_MASK',
        #'create_BY_MATERIAL_ID',
        'label_biaspath_only_settings',
        ['samples', 'emission_samples'],
        'label_material_visibility',
        ['visibility_indirect_diffuse_enable', 'visibility_indirect_glossy_enable', 'visibility_indirect_specular_enable'],
    ]

    visibility = {
        'label_biaspath_only_settings':
            {ScenePrefix() + 'luxcore_enginesettings.renderengine_type': O(['PATH', 'BIDIR', 'BIDIRVM'])},
    }

    enabled = {
        'samples': {ScenePrefix() + 'luxcore_enginesettings.renderengine_type': 'TILEPATH'},
        'label_material_visibility': {
        ScenePrefix() + 'luxcore_enginesettings.renderengine_type': 'TILEPATH'},
        'emission_samples': {
        ScenePrefix() + 'luxcore_enginesettings.renderengine_type': 'TILEPATH'},
        'visibility_indirect_diffuse_enable':
            {ScenePrefix() + 'luxcore_enginesettings.renderengine_type': 'TILEPATH'},
        'visibility_indirect_glossy_enable':
            {ScenePrefix() + 'luxcore_enginesettings.renderengine_type': 'TILEPATH'},
        'visibility_indirect_specular_enable':
            {ScenePrefix() + 'luxcore_enginesettings.renderengine_type': 'TILEPATH'},
        'sc_onlyinfinitelights': {'is_shadow_catcher': True},
    }

    alert = {}

    properties = [
        {
            'attr': 'materialgroup',
            'type': 'string',
            'name': 'Materialgroup',
            'description': 'Materialgroup; leave blank to use default',
        },
        {
            'type': 'prop_search',
            'attr': 'materialgroup_chooser',
            'src': lambda s, c: s.scene.pbrtv3_materialgroups,
            'src_attr': 'materialgroups',
            'trg': lambda s, material: material.luxcore_material,
            'trg_attr': 'materialgroup',
            'name': 'Material Group',
            'icon': 'IMASEL'
        },
        ##########
        {
            'type': 'bool',
            'attr': 'is_shadow_catcher',
            'name': 'Shadow Catcher',
            'description': 'Make material transparent where hit by light and opaque where shadowed (alpha transparency)',
            'default': False,
        },
        {
            'type': 'bool',
            'attr': 'sc_onlyinfinitelights',
            'name': 'Only Infinite Lights',
            'description': 'Only consider infinite lights for this shadow catcher',
            'default': False,
        },
        {
            'type': 'int',
            'attr': 'id',
            'name': 'Material ID',
            'description': 'Material ID (-1 = auto), used for AOVs',
            'default': -1,
            'min': -1,
            'max': 65536,
        },
        {
            'type': 'bool',
            'attr': 'create_MATERIAL_ID_MASK',
            'name': 'MATERIAL_ID_MASK pass',
            'description': 'Create a mask for this material (AOV channel)',
            'default': False,
        },
        {
            'type': 'bool',
            'attr': 'create_BY_MATERIAL_ID',
            'name': 'BY_MATERIAL_ID pass',
            'description': 'Create a pass containing only objects with this material ID (AOV channel)',
            'default': False,
        },
        {
            'type': 'int',
            'attr': 'samples',
            'name': 'Samples',
            'description': 'Material samples count (-1 = global default, size x size)',
            'default': -1,
            'min': -1,
            'soft_max': 16,
            'max': 256,
        },
        {
            'type': 'int',
            'attr': 'emission_samples',
            'name': 'Emission samples',
            'description': 'Material emission samples count (-1 = global default, size x size)',
            'default': -1,
            'min': -1,
            'soft_max': 16,
            'max': 256,
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
        {
            'type': 'text',
            'attr': 'label_biaspath_only_settings',
            'name': 'Biased Path specific settings:'
        },
    ]
