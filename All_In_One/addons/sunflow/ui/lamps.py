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



import bpy
import bl_ui

from .. import SunflowAddon
from extensions_framework.ui import property_group_renderer

narrowui = 180

class lamps_panel(bl_ui.properties_data_lamp.DataButtonsPanel, property_group_renderer):
    COMPAT_ENGINES = { 'SUNFLOW_RENDER' }

@SunflowAddon.addon_register_class
class lamps(lamps_panel):
    bl_label = 'Sunflow Lamps'
    
    display_property_groups = [
        (('lamp',), 'sunflow_lamp')
    ]
    
    # Overridden to draw some of blender's lamp controls
    def draw(self, context):
        lamp = context.lamp
        if lamp is not None:
            layout = self.layout
            wide_ui = context.region.width > narrowui

            if wide_ui:
                layout.prop(lamp, "type", expand=True)
            else:
                layout.prop(lamp, "type", text="")

            split = layout.split()
            
            col = split.column()

            layout.prop(lamp, "color", text="Color")
            
            if lamp.type != 'SUN':
                layout.prop(lamp.sunflow_lamp, "lightRadiance", text="Radiance")
            
            if not lamp.type in ['SPOT', 'POINT']:
                layout.prop(lamp.sunflow_lamp, "lightSamples", text="Samples")
            

            # SPOT LAMP: Blender Properties
            if lamp.type == 'SPOT':
                wide_ui = context.region.width > narrowui
                
                if wide_ui:
                    # col = split.column()
                    col = layout.row()
                else:
                    col = layout.column()
                col.prop(lamp, "spot_size", text="Size")
                col = layout.row()
                col.prop(lamp, "show_cone")

            
            # SUN LAMP: Blender Properties
            if lamp.type == 'SUN':
                wide_ui = context.region.width > narrowui
                
                if wide_ui:
                    # col = split.column()
                    col = layout.row()
                else:
                    col = layout.column()
                col.prop(lamp.sky, "atmosphere_turbidity", text="Turbidity")
                col = layout.row()
                col.prop(lamp.sunflow_lamp, "lightSunDirection", text="East Direction", expand=False)

            # AREA LAMP: Blender Properties
            elif lamp.type == 'AREA':
                if wide_ui:
                    col = layout.row()
                else:
                    col = layout.column()
                col.row().prop(lamp, "shape", expand=True)
                sub = col.column(align=True)

                if (lamp.shape == 'SQUARE'):
                    sub.prop(lamp, "size")
                elif (lamp.shape == 'RECTANGLE'):
                    sub.prop(lamp, "size", text="Size X")
                    sub.prop(lamp, "size_y", text="Size Y")
            elif wide_ui:
                col = split.column()
            

            if lamp.type == 'HEMI':
                layout.prop(lamp.sunflow_lamp, "lightShericalRadius", text="Spherical Radius")

