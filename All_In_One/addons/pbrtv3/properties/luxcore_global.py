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
#
import bpy

from .. import PBRTv3Addon
from ..extensions_framework import declarative_property_group

@PBRTv3Addon.addon_register_class
class luxcore_global(declarative_property_group):
    """
    Global settings only used in PBRTv3Core API mode
    """

    ef_attach_to = ['Scene']

    properties = [
        # Global node editor properties
        {
            'type': 'bool',
            'attr': 'nodeeditor_show_imagemap_previews',
            'name': 'Thumbnails',
            'description': 'Show preview images in imagemap nodes',
            'default': True,
        },
        # Cycles converter properties
        {
            'type': 'float_vector',
            'subtype': 'COLOR',
            'attr': 'cycles_converter_fallback_color',
            'name': 'Fallback Color',
            'description': 'Color to use on materials where the conversion failed',
            'default': (0.6, 0.6, 0.6),
            'min': 0,
            'max': 1,
        },
    ]