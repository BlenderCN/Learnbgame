# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
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

from ..outputs.luxcore_api import UsePBRTv3Core
from .. import PBRTv3Addon


@PBRTv3Addon.addon_register_class
class meshes(bl_ui.properties_data_mesh.MeshButtonsPanel, property_group_renderer):
    bl_label = 'PBRTv3 Mesh Options'
    COMPAT_ENGINES = 'PBRTv3_RENDER'

    display_property_groups = [
        ( ('mesh',), 'pbrtv3_mesh' )
    ]

    def draw(self, context):
        if UsePBRTv3Core():
            self.layout.label('Displacement and portals not yet supported by PBRTv3Core', icon='INFO')

            if context.object.data.pbrtv3_mesh.portal:
                self.layout.label('This mesh was flagged as portal and won\'t be exported', icon='INFO')

        else:
            if context.object.pbrtv3_object.append_proxy and context.object.pbrtv3_object.hide_proxy_mesh:
                msg = ['Mesh options not available when',
                       'object is used as a render proxy',
                       'and \"Don\'t Render Original\" is set.'
                ]

                col = self.layout.column()
                col.scale_y = 0.6

                for t in msg:
                    col.label(t)
            else:
                super().draw(context)
