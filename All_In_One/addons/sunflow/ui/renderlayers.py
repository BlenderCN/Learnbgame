# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
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
# --------------------------------------------------------------------------
# Blender Version                     2.68
# Exporter Version                    0.0.4
# Created on                          26-Aug-2013
# Author                              NodeBench
# --------------------------------------------------------------------------


import bpy, bl_ui
from .. import SunflowAddon
from extensions_framework.ui import property_group_renderer


class sunflow_rlayers(bl_ui.properties_render_layer.RenderLayerButtonsPanel, property_group_renderer):
    COMPAT_ENGINES = { 'SUNFLOW_RENDER' }

@SunflowAddon.addon_register_class
class SunflowRender_PT_configure(sunflow_rlayers):
    bl_label = "Configure"
    bl_options = {'DEFAULT_CLOSED'}
    
    display_property_groups = [
        (('scene',), 'sunflow_renderconfigure')
    ]
        
    def draw(self, context):
        super().draw(context)
        
        layout = self.layout

        # Create two columns, by using a split layout.
        split = layout.split()

        col = split.column()        
        col = split.column()  
        col.operator('sunflow.save_settings', icon='SAVE_PREFS')
                       
@SunflowAddon.addon_register_class
class SunflowRender_PT_quickpasses(sunflow_rlayers):
    bl_label = "Quick Passes"
    # bl_options = {'DEFAULT_CLOSED'}
    
    display_property_groups = [
        (('scene',), 'sunflow_passes')
    ]    
