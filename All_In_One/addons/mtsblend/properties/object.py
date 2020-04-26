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
class mitsuba_object(declarative_property_group):
    ef_attach_to = ['Object']

    controls = [
        'motion_samples_override',
        'motion_blur_samples',
    ]

    properties = [
        {
            'type': 'bool',
            'attr': 'motion_samples_override',
            'name': 'Override Motion Samples',
            'description': 'Override motion blur samples defined in the engine',
            'default': False,
        },
        {
            'type': 'int',
            'attr': 'motion_blur_samples',
            'name': 'Motion Samples',
            'description': 'Number of motion steps per frame. Increase for non-linear motion blur or high velocity rotations',
            'default': 1,
            'min': 1,
            'soft_min': 1,
            'max': 100,
            'soft_max': 100
        },
    ]
