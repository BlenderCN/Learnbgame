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
from ...ui.materials import luxrender_material_sub


@LuxRenderAddon.addon_register_class
class ui_material_glossycoating(luxrender_material_sub):
    bl_label = 'LuxRender Glossy Coating Material'

    LUX_COMPAT = {'glossycoating'}

    display_property_groups = [
        ( ('material', 'luxrender_material'), 'luxrender_mat_glossycoating' )
    ]

    def draw_ior_menu(self, context):
        """
        This is a draw callback from property_group_renderer, due
        to ef_callback item in luxrender_mat_<mat>.properties
        """

        lmg = context.material.luxrender_material.luxrender_mat_glossycoating

        if lmg.index_floatvalue == lmg.index_presetvalue:
            menu_text = lmg.index_presetstring
        else:
            menu_text = '-- Choose preset --'

        cl = self.layout.column(align=True)
        cl.menu('LUXRENDER_MT_ior_presets', text=menu_text)
