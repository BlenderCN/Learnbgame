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
from ..extensions_framework.validate import Logic_AND as A

from .. import LuxRenderAddon


@LuxRenderAddon.addon_register_class
class luxcore_tile_highlighting(declarative_property_group):
    """
    Storage class for LuxCore render interface settings.
    These are the settings displayed in the properties bar (key: N) of the
    image editor window. 
    Examples: tile highlighting settings for BIASPATH render modes.
    """
    
    ef_attach_to = ['Scene']
    alert = {}

    controls = [
                  'use_tile_highlighting',
                  'show_converged', 
                  'show_unconverged', 
                  'show_pending'
    ]
    
    visibility = {
        'label_display': {'use_tile_highlighting': True},
        'show_converged': {'use_tile_highlighting': True},
        'show_unconverged': {'use_tile_highlighting': True},
        'show_pending': {'use_tile_highlighting': True},
    }

    properties = [
        {
            'type': 'bool',
            'attr': 'use_tile_highlighting',
            'name': 'Tile Highlighting',
            'description': 'Highlight tiles',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'show_converged',
            'name': 'Converged',
            'description': 'Show finished tiles',
            'default': True,
            'toggle': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'show_unconverged',
            'name': 'Unconverged',
            'description': 'Show unfinished tiles',
            'default': False,
            'toggle': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'show_pending',
            'name': 'Pending',
            'description': 'Show tiles that are actively rendered',
            'default': True,
            'toggle': True,
            'save_in_preset': True
        },
    ]
