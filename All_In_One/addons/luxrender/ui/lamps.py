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

from ..outputs.luxcore_api import UseLuxCore
from .. import LuxRenderAddon

narrowui = 180


class lamps_panel(bl_ui.properties_data_lamp.DataButtonsPanel, property_group_renderer):
    COMPAT_ENGINES = 'LUXRENDER_RENDER'


@LuxRenderAddon.addon_register_class
class ui_luxrender_lamps(lamps_panel):
    bl_label = 'LuxRender Lamps'

    display_property_groups = [
        ( ('lamp',), 'luxrender_lamp' )
    ]

    # Overridden here and in each sub-type UI to draw some of blender's lamp controls
    def draw(self, context):
        if context.lamp is not None:
            wide_ui = context.region.width > narrowui

            if wide_ui:
                self.layout.prop(context.lamp, "type", expand=True)
            else:
                self.layout.prop(context.lamp, "type", text="")

            self.layout.prop(context.lamp, "energy", text="Gain")

            super().draw(context)

            if context.lamp.type in ('AREA', 'POINT', 'SPOT'):
                self.layout.prop(context.lamp.luxrender_lamp, "iesname", text="IES Data")


@LuxRenderAddon.addon_register_class
class ui_luxrender_lamp_point(lamps_panel):
    bl_label = 'LuxRender Point Lamp'

    display_property_groups = [
        ( ('lamp', 'luxrender_lamp'), 'luxrender_lamp_point' )
    ]

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.lamp.type == 'POINT'


@LuxRenderAddon.addon_register_class
class ui_luxrender_lamp_spot(lamps_panel):
    bl_label = 'LuxRender Spot Lamp'

    display_property_groups = [
        ( ('lamp', 'luxrender_lamp'), 'luxrender_lamp_spot' )
    ]

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.lamp.type == 'SPOT'

    def draw(self, context):
        if context.lamp is not None:
            wide_ui = context.region.width > narrowui
            super().draw(context)

            # SPOT LAMP: Blender Properties
            if context.lamp.type == 'SPOT':
                projector = context.lamp.luxrender_lamp.luxrender_lamp_spot.projector

                if wide_ui and not projector:
                    col = self.layout.row()
                else:
                    col = self.layout.column()

                col.prop(context.lamp, "spot_size", text="Size")

                if not projector:
                    col.prop(context.lamp, "spot_blend", text="Blend", slider=True)

                row = self.layout.row()
                row.prop(context.lamp, "show_cone", text="Show Cone")


@LuxRenderAddon.addon_register_class
class ui_luxrender_lamp_sun(lamps_panel):
    bl_label = 'LuxRender Sun Lamp'

    display_property_groups = [
        ( ('lamp', 'luxrender_lamp'), 'luxrender_lamp_sun' )
    ]

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.lamp.type == 'SUN'


@LuxRenderAddon.addon_register_class
class ui_luxrender_lamp_hemi(lamps_panel):
    bl_label = 'LuxRender Hemi Lamp'

    display_property_groups = [
        ( ('lamp', 'luxrender_lamp'), 'luxrender_lamp_hemi' )
    ]

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.lamp.type == 'HEMI'


@LuxRenderAddon.addon_register_class
class ui_luxrender_lamp_area(lamps_panel):
    bl_label = 'LuxRender Area Lamp'

    display_property_groups = [
        ( ('lamp', 'luxrender_lamp'), 'luxrender_lamp_area' ),
        ( ('lamp', 'luxrender_lamp'), 'luxrender_lamp_laser', lambda: UseLuxCore() )
    ]

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.lamp.type == 'AREA'

    def draw(self, context):
        if context.lamp is not None:
            wide_ui = context.region.width > narrowui
            super().draw(context)

            # AREA LAMP: Blender Properties
            if context.lamp.type == 'AREA':
                if wide_ui:
                    col = self.layout.row()
                else:
                    col = self.layout.column()

                col.row().prop(context.lamp, "shape", expand=True)
                sub = col.column(align=True)

                if context.lamp.shape == 'SQUARE':
                    sub.prop(context.lamp, "size")
                elif context.lamp.shape == 'RECTANGLE':
                    sub.prop(context.lamp, "size", text="Size X")
                    sub.prop(context.lamp, "size_y", text="Size Y")


@LuxRenderAddon.addon_register_class
class ui_luxcore_lamp(lamps_panel):
    """
    LuxCore light settings
    """

    bl_label = 'LuxCore specific settings'
    bl_options = {'DEFAULT_CLOSED'}

    display_property_groups = [
        ( ('lamp', 'luxrender_lamp' ), 'luxcore_lamp', lambda: UseLuxCore() )
    ]

    def draw(self, context):
        if not UseLuxCore():
            self.layout.label("Not available with API v1.x")

        super().draw(context)

    @classmethod
    def poll(cls, context):
        return super().poll(context)