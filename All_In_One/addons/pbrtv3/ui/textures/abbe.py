# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
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
from ... import PBRTv3Addon
from ...ui.textures import pbrtv3_texture_base


@PBRTv3Addon.addon_register_class
class ui_texture_abbe(pbrtv3_texture_base):
    bl_label = 'PBRTv3 Abbe Texture'

    PBRTv3_COMPAT = {'abbe'}

    display_property_groups = [
        ( ('texture', 'pbrtv3_texture'), 'pbrtv3_tex_abbe' )
    ]
