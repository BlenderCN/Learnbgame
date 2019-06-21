# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond, Simon Wendsche (BYOB)
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

from ..extensions_framework.ui import property_group_renderer

from ..outputs.luxcore_api import UseLuxCore
from .. import LuxRenderAddon


@LuxRenderAddon.addon_register_class
class imageeditor_panel(property_group_renderer):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_label = "Tile Highlighting"
    COMPAT_ENGINES = 'LUXRENDER_RENDER'

    @classmethod
    def poll(cls, context):
        engine_is_lux = context.scene.render.engine in cls.COMPAT_ENGINES

        return engine_is_lux and UseLuxCore()

    display_property_groups = [
        ( ('scene',), 'luxcore_tile_highlighting', lambda: UseLuxCore() 
            and bpy.context.scene.luxcore_enginesettings.renderengine_type in ['BIASPATHCPU', 'BIASPATHOCL']),
    ]

    def draw(self, context):
        # Draw as normal ...
        property_group_renderer.draw(self, context)

