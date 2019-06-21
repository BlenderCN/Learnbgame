# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond
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
import bl_ui

from ...extensions_framework.ui import property_group_renderer

from ... import LuxRenderAddon


class luxrender_material_base(bl_ui.properties_material.MaterialButtonsPanel, property_group_renderer):
    COMPAT_ENGINES = 'LUXRENDER_RENDER'


class luxrender_material_sub(luxrender_material_base):
    LUX_COMPAT = set()

    @classmethod
    def poll(cls, context):
        """
        Only show LuxRender panel if luxrender_material.material in LUX_COMPAT
        """
        return super().poll(context) and (context.material.luxrender_material.type in cls.LUX_COMPAT) and (
            not context.material.luxrender_material.nodetree)


