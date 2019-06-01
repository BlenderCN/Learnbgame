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
from ... import LuxRenderAddon
from ...ui.textures import luxrender_texture_base


@LuxRenderAddon.addon_register_class
class ui_texture_cauchy(luxrender_texture_base):
    bl_label = 'LuxRender Cauchy Texture'

    LUX_COMPAT = {'cauchy'}

    display_property_groups = [
        ( ('texture', 'luxrender_texture'), 'luxrender_tex_cauchy' )
    ]

    def draw_ior_menu(self, context):
        """
        This is a draw callback from property_group_renderer, due
        to ef_callback item in luxrender_tex_<tex>.properties
        """

        lmg = context.texture.luxrender_texture.luxrender_tex_cauchy

        if lmg.ior == lmg.ior_presetvalue:
            menu_text = lmg.ior_presetstring
        else:
            menu_text = '-- Choose preset --'

        cl = self.layout.column(align=True)
        cl.menu('LUXRENDER_MT_ior_presets', text=menu_text)
