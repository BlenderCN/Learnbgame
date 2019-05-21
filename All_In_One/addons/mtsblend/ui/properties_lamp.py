# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender Mitsuba Add-On
# --------------------------------------------------------------------------
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
# ***** END GPL LICENSE BLOCK *****

from bpy.types import Panel

from bl_ui.properties_data_lamp import DataButtonsPanel

from .. import MitsubaAddon
from ..ui import node_tree_selector_draw, panel_node_draw


class mitsuba_lamp_panel(DataButtonsPanel, Panel):
    COMPAT_ENGINES = {'MITSUBA_RENDER'}


@MitsubaAddon.addon_register_class
class MitsubaLamp_PT_lamp(mitsuba_lamp_panel):
    bl_label = 'Lamp'

    def draw(self, context):
        layout = self.layout

        lamp = context.lamp
        ntree = lamp.mitsuba_nodes.get_node_tree()

        node_tree_selector_draw(layout, context, 'lamp')

        if ntree:
            panel_node_draw(layout, context, lamp, 'MtsNodeLampOutput', 'Lamp')

        else:
            layout.prop(lamp, "type", expand=True)

            layout.prop(lamp, "color")
            layout.prop(lamp, "energy")

            split = layout.split()
            col = split.column(align=True)

            if lamp.type == 'POINT':
                col.prop(lamp, "shadow_soft_size", text="Size")

            elif lamp.type == 'SPOT':
                sub = col.column()
                sub.prop(lamp, "spot_size", text="Size")
                sub.prop(lamp, "spot_blend", text="Blend", slider=True)
                col = split.column()
                col.prop(lamp, "show_cone")

            elif lamp.type == 'AREA':
                col.prop(lamp, "shape", text="")
                sub = split.column(align=True)

                if lamp.shape == 'SQUARE':
                    sub.prop(lamp, "size")

                elif lamp.shape == 'RECTANGLE':
                    sub.prop(lamp, "size", text="Size X")
                    sub.prop(lamp, "size_y", text="Size Y")

            elif lamp.type == 'HEMI':
                layout.label(text="Not supported, interpreted as sun lamp")


@MitsubaAddon.addon_register_class
class MitsubaLampNode_PT_exterior(mitsuba_lamp_panel):
    bl_label = 'Exterior Medium'

    def draw(self, context):
        panel_node_draw(self.layout, context, context.lamp, 'MtsNodeLampOutput', 'Exterior Medium')

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.lamp.mitsuba_nodes.nodetree
