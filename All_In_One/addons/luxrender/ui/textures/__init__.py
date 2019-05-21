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


class luxrender_texture_base(bl_ui.properties_texture.TextureButtonsPanel, property_group_renderer):
    """
    This is the base class for all LuxRender texture sub-panels.
    All subpanels should have their own property_groups, and define
    a string attribute in their property_group called 'variant'.
    It should be set to either 'float' or 'color' depending on the
    texture type, and may display the choice to the user as a switch,
    or keep it as a hidden attribute if the texture is mono-typed.
    """

    # bl_options		= {'HIDE_HEADER'}
    COMPAT_ENGINES = 'LUXRENDER_RENDER'
    LUX_COMPAT = set()
    BL_COMPAT = set()

    @classmethod
    def poll(cls, context):
        """
        Only show LuxRender panel if luxrender_texture.type in LUX_COMPAT
        """

        tex = context.texture
        if not tex:
            return False

        if context.texture.luxrender_texture.type == 'BLENDER':
            return tex and \
                   (context.scene.render.engine in cls.COMPAT_ENGINES) and \
                   context.texture.type in cls.BL_COMPAT
        else:
            return tex and \
                   (context.scene.render.engine in cls.COMPAT_ENGINES) and \
                   context.texture.luxrender_texture.type in cls.LUX_COMPAT

