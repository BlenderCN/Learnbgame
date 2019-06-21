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
import bpy, bl_ui

from ..extensions_framework.ui import property_group_renderer

from .. import LuxRenderAddon
from .lamps import lamps_panel
from .materials import luxrender_material_base


class world_panel(bl_ui.properties_world.WorldButtonsPanel, property_group_renderer):
    COMPAT_ENGINES = 'LUXRENDER_RENDER'


@LuxRenderAddon.addon_register_class
class world(world_panel):
    """
    LuxRender World Settings
    """

    bl_label = 'LuxRender World Settings'

    display_property_groups = [
        ( ('scene',), 'luxrender_world' )
    ]


class volumes_base(object):
    """
    Interior/Exterior Volumes Settings
    """
    bl_label = 'LuxRender Volumes'

    display_property_groups = [
        ( ('scene',), 'luxrender_volumes' )
    ]

    def draw_ior_menu(self, context):
        """
        This is a draw callback from property_group_renderer, due
        to ef_callback item in luxrender_volume_data.properties
        """
        vi = context.scene.luxrender_volumes.volumes_index
        lv = context.scene.luxrender_volumes.volumes[vi]

        if lv.fresnel_fresnelvalue == lv.fresnel_presetvalue:
            menu_text = lv.fresnel_presetstring
        else:
            menu_text = '-- Choose preset --'

        cl = self.layout.column(align=True)
        cl.menu('LUXRENDER_MT_ior_presets_volumes', text=menu_text)

    # overridden in order to draw the selected luxrender_volume_data property group
    def draw(self, context):
        super().draw(context)

        # row = self.layout.row(align=True)
        # row.menu("LUXRENDER_MT_presets_volume", text=bpy.types.LUXRENDER_MT_presets_volume.bl_label)
        # row.operator("luxrender.preset_volume_add", text="", icon="ZOOMIN")
        # row.operator("luxrender.preset_volume_add", text="", icon="ZOOMOUT").remove_active = True

        if len(context.scene.luxrender_volumes.volumes) > 0:
            current_vol_ind = context.scene.luxrender_volumes.volumes_index
            current_vol = context.scene.luxrender_volumes.volumes[current_vol_ind]

            # 'name' is not a member of current_vol.properties,
            # so we draw it explicitly
            self.layout.prop(
                current_vol, 'name'
            )

            # Here we draw the currently selected luxrender_volumes_data property group
            for control in current_vol.controls:
                self.draw_column(
                    control,
                    self.layout,
                    current_vol,
                    context,
                    property_group=current_vol
                )


@LuxRenderAddon.addon_register_class
class volumes_world(volumes_base, world_panel):
    pass


@LuxRenderAddon.addon_register_class
class volumes_material(volumes_base, luxrender_material_base):
    @classmethod
    def poll(cls, context):
        return super().poll(context) and (
            context.material.luxrender_material.Interior_volume
            or
            context.material.luxrender_material.Exterior_volume
        )


class lightgroups_base(object):
    """
    Light Groups Settings
    """

    bl_label = 'LuxRender Light Groups'

    display_property_groups = [
        ( ('scene',), 'luxrender_lightgroups' )
    ]

    # overridden in order to draw a 'non-standard' panel
    def draw(self, context):
        super().draw(context)

        for lg_index in range(len(context.scene.luxrender_lightgroups.lightgroups)):
            lg = context.scene.luxrender_lightgroups.lightgroups[lg_index]
            row = self.layout.row()
            row.prop(lg, 'lg_enabled', text="")
            subrow = row.row()
            subrow.enabled = lg.lg_enabled
            subrow.prop(lg, 'name', text="")

            # Here we draw the currently selected luxrender_lightgroups_data property group
            for control in lg.controls:
                self.draw_column(
                    control,
                    subrow.column(),
                    lg,
                    context,
                    property_group=lg
                )

            row.operator('luxrender.lightgroup_remove', text="", icon="ZOOMOUT").lg_index = lg_index


@LuxRenderAddon.addon_register_class
class lightgroups_world(lightgroups_base, world_panel):
    pass


@LuxRenderAddon.addon_register_class
class lightgroups_lamps(lightgroups_base, lamps_panel):
    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.lamp.luxrender_lamp.lightgroup
