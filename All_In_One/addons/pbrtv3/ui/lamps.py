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

narrowui = 180


class lamps_panel(bl_ui.properties_data_lamp.DataButtonsPanel, property_group_renderer):
    COMPAT_ENGINES = 'PBRTv3_RENDER'


@PBRTv3Addon.addon_register_class
class ui_pbrtv3_lamps(lamps_panel):
    bl_label = 'PBRTv3 Lamps'

    display_property_groups = [
        ( ('lamp',), 'pbrtv3_lamp' )
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
                self.layout.prop(context.lamp.pbrtv3_lamp, "iesname", text="IES Data")


@PBRTv3Addon.addon_register_class
class ui_pbrtv3_lamp_point(lamps_panel):
    bl_label = 'PBRTv3 Point Lamp'

    display_property_groups = [
        ( ('lamp', 'pbrtv3_lamp'), 'pbrtv3_lamp_point' )
    ]

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.lamp.type == 'POINT'


@PBRTv3Addon.addon_register_class
class ui_pbrtv3_lamp_spot(lamps_panel):
    bl_label = 'PBRTv3 Spot Lamp'

    display_property_groups = [
        ( ('lamp', 'pbrtv3_lamp'), 'pbrtv3_lamp_spot' )
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
                projector = context.lamp.pbrtv3_lamp.pbrtv3_lamp_spot.projector

                if wide_ui and not projector:
                    col = self.layout.row()
                else:
                    col = self.layout.column()

                col.prop(context.lamp, "spot_size", text="Size")

                if not projector:
                    col.prop(context.lamp, "spot_blend", text="Blend", slider=True)

                row = self.layout.row()
                row.prop(context.lamp, "show_cone", text="Show Cone")


@PBRTv3Addon.addon_register_class
class ui_pbrtv3_lamp_sun(lamps_panel):
    bl_label = 'PBRTv3 Sun Lamp'

    display_property_groups = [
        ( ('lamp', 'pbrtv3_lamp'), 'pbrtv3_lamp_sun' )
    ]

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.lamp.type == 'SUN'

    def draw(self, context):
        if context.lamp is not None:
            super().draw(context)

            if context.lamp.type == 'SUN':
                layout = self.layout

                sun_props = context.lamp.pbrtv3_lamp.pbrtv3_lamp_sun

                if UsePBRTv3Core() and 'sky' in sun_props.sunsky_type:
                    row = layout.row(align=True)
                    row.label('Ground Albedo:')

                    if sun_props.link_albedo_groundcolor:
                        row.prop(sun_props, 'groundcolor')
                    else:
                        row.prop(sun_props, 'groundalbedo')

                    if sun_props.use_groundcolor:
                        row.prop(sun_props, 'link_albedo_groundcolor', icon='CONSTRAINT', toggle=True)

                    row = layout.row(align=True)
                    row.prop(sun_props, 'use_groundcolor')
                    row.prop(sun_props, 'groundcolor')

                    if sun_props.use_groundcolor:
                        row.prop(sun_props, 'link_albedo_groundcolor', icon='CONSTRAINT', toggle=True)


@PBRTv3Addon.addon_register_class
class ui_pbrtv3_lamp_hemi(lamps_panel):
    bl_label = 'PBRTv3 Hemi Lamp'

    display_property_groups = [
        ( ('lamp', 'pbrtv3_lamp'), 'pbrtv3_lamp_hemi' )
    ]

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.lamp.type == 'HEMI'


@PBRTv3Addon.addon_register_class
class ui_pbrtv3_lamp_area(lamps_panel):
    bl_label = 'PBRTv3 Area Lamp'

    display_property_groups = [
        ( ('lamp', 'pbrtv3_lamp'), 'pbrtv3_lamp_area' ),
        ( ('lamp', 'pbrtv3_lamp'), 'pbrtv3_lamp_laser', lambda: UsePBRTv3Core() )
    ]

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.lamp.type == 'AREA'

    def draw(self, context):
        if context.lamp is not None:
            wide_ui = context.region.width > narrowui
            lux_lamp = context.lamp.pbrtv3_lamp
            lux_lamp_area = lux_lamp.pbrtv3_lamp_area
            is_laser = lux_lamp.pbrtv3_lamp_laser.is_laser

            super().draw(context)

            # AREA LAMP: Blender Properties
            if context.lamp.type == 'AREA':
                if wide_ui:
                    col = self.layout.row()
                else:
                    col = self.layout.column()

                row = col.row()
                row.active = not is_laser
                row.prop(context.lamp, "shape", expand=True)
                sub = col.column(align=True)

                if context.lamp.shape == 'SQUARE':
                    sub.prop(context.lamp, "size")
                elif context.lamp.shape == 'RECTANGLE':
                    sub.prop(context.lamp, "size", text="Size X")
                    sub2 = sub.column(align=True)
                    sub2.active = not is_laser
                    sub2.prop(context.lamp, "size_y", text="Size Y")

                if lux_lamp_area.opacity_floatvalue != 1 or lux_lamp_area.opacity_usefloattexture:
                    if is_laser:
                        self.layout.label('Laser does not support opacity setting', icon='INFO')
                    else:
                        self.layout.label('Warning: Invisible lamps can cause artifacts', icon='INFO')


@PBRTv3Addon.addon_register_class
class ui_luxcore_lamp(lamps_panel):
    """
    PBRTv3Core light settings
    """

    bl_label = 'PBRTv3Core specific settings'
    bl_options = {'DEFAULT_CLOSED'}

    display_property_groups = [
        ( ('lamp', 'pbrtv3_lamp' ), 'luxcore_lamp', lambda: UsePBRTv3Core() )
    ]

    def draw(self, context):
        if not UsePBRTv3Core():
            self.layout.label("Not available with API v1.x")

        super().draw(context)

    @classmethod
    def poll(cls, context):
        if not UsePBRTv3Core():
            return False

        return super().poll(context)