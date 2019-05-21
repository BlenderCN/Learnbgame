# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond, Daniel Genrich
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

from ..extensions_framework.ui import property_group_renderer

from .. import LuxRenderAddon


@LuxRenderAddon.addon_register_class
class meshes(bl_ui.properties_data_mesh.MeshButtonsPanel, property_group_renderer):
    bl_label = 'LuxRender Mesh Options'
    COMPAT_ENGINES = 'LUXRENDER_RENDER'

    display_property_groups = [
        ( ('mesh',), 'luxrender_mesh' )
    ]

    def draw(self, context):
        if context.object.luxrender_object.append_proxy and context.object.luxrender_object.hide_proxy_mesh:
            msg = ['Mesh options not available when',
                   'object is used as a render proxy',
                   'and \"Don\'t Render Original\" is set.'
            ]
            for t in msg:
                self.layout.label(t)
        else:
            super().draw(context)
