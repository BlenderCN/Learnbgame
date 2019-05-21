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

from ..extensions_framework import declarative_property_group

from .. import MitsubaAddon


@MitsubaAddon.addon_register_class
class mitsuba_hair(declarative_property_group):
    """
    Storage class for Mitsuba Hair Rendering settings.
    """

    ef_attach_to = ['ParticleSettings']

    controls = [
        'hair_width',
    ]

    properties = [
        {
            'type': 'float',
            'attr': 'hair_width',
            'name': 'Hair Width',
            'description': 'Thickness of hair',
            'default': 0.001,
            'min': 0.000001,
            'max': 1000.0,
            'precision': 3,
            'sub_type': 'DISTANCE',
            'unit': 'LENGTH',
        },
    ]
