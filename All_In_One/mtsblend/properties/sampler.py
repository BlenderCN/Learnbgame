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

from .. import MitsubaAddon
from ..extensions_framework import declarative_property_group
from ..extensions_framework.validate import Logic_OR as O


@MitsubaAddon.addon_register_class
class mitsuba_sampler(declarative_property_group):
    '''
    Storage class for Mitsuba Sampler settings.
    This class will be instantiated within a Blender scene
    object.
    '''

    ef_attach_to = ['Scene']

    controls = [
        'type',
        'sampleCount',
        'scramble'
    ]

    visibility = {
        'scramble': {'type': O(['halton', 'hammersley', 'sobol'])}

    }

    properties = [
        {
            'type': 'enum',
            'attr': 'type',
            'name': 'Type',
            'description': 'Specifies the type of sampler to use',
            'default': 'ldsampler',
            'items': [
                ('sobol', 'Sobol QMC sampler', 'sobol'),
                ('hammersley', 'Hammersley QMC sampler', 'hammersley'),
                ('halton', 'Halton QMC sampler', 'halton'),
                ('ldsampler', 'Low discrepancy', 'ldsampler'),
                ('stratified', 'Stratified', 'stratified'),
                ('independent', 'Independent', 'independent'),
            ],
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'sampleCount',
            'name': 'Pixel samples',
            'description': 'Number of samples to use for estimating the illumination at each pixel',
            'default': 16,
            'min': 1,
            'max': 16384,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'scramble',
            'name': 'Scramble value',
            'description': 'This plugin can operate in one of three scrambling modes: -1, 0, gt= : 1',
            'default': -1,
            'min': -1,
            'max': 1024,
            'save_in_preset': True
        }
    ]

    def api_output(self):
        sampler_dict = {}

        sampler_dict['type'] = self.type
        sampler_dict['sampleCount'] = self.sampleCount

        if self.type == 'halton' or self.type == 'hammersley':
            sampler_dict['scramble'] = self.scramble

        elif self.type == 'sobol':
            sampler_dict['scramble'] = self.scramble + 1

        return sampler_dict
