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
import bl_ui

from ...extensions_framework.ui import property_group_renderer

from ... import PBRTv3Addon


class pbrtv3_material_base(bl_ui.properties_material.MaterialButtonsPanel, property_group_renderer):
    COMPAT_ENGINES = 'PBRTv3_RENDER'


class pbrtv3_material_sub(pbrtv3_material_base):
    PBRTv3_COMPAT = set()

    @classmethod
    def poll(cls, context):
        """
        Only show PBRTv3 panel if pbrtv3_material.material in PBRTv3_COMPAT
        """
        return super().poll(context) and (context.material.pbrtv3_material.type in cls.PBRTv3_COMPAT) and (
            not context.material.pbrtv3_material.nodetree)


