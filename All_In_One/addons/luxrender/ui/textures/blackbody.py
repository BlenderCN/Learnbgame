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
class ui_texture_blackbody(luxrender_texture_base):
    bl_label = 'LuxRender Blackbody Texture'

    LUX_COMPAT = {'blackbody'}

    display_property_groups = [
        ( ('texture', 'luxrender_texture'), 'luxrender_tex_blackbody' )
    ]
