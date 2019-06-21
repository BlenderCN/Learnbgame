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
import bpy, bl_ui

from ..extensions_framework.ui import property_group_renderer
from ..outputs.luxcore_api import UsePBRTv3Core

from .. import PBRTv3Addon
from .lamps import lamps_panel
from .materials import pbrtv3_material_base


class world_panel(bl_ui.properties_world.WorldButtonsPanel, property_group_renderer):
    COMPAT_ENGINES = 'PBRTv3_RENDER'


@PBRTv3Addon.addon_register_class
class world_helper(world_panel):
    """
    PBRTv3 World Help
    """

    bl_label = 'PBRTv3 World Helper'

    def draw(self, context):
        layout = self.layout

        layout.label('Background is controlled by hemi and sun lights', icon='INFO')

        row = layout.row(align=True)
        add_sunsky = row.operator('object.lamp_add', text='Add Sun and Sky', icon='LAMP_SUN')
        add_sunsky.type = 'SUN'
        add_hemi = row.operator('object.lamp_add', text='Add Hemi (HDRI)', icon='LAMP_HEMI')
        add_hemi.type = 'HEMI'


@PBRTv3Addon.addon_register_class
class world(world_panel):
    """
    PBRTv3 World Settings
    """

    bl_label = 'PBRTv3 World Settings'

    display_property_groups = [
        ( ('scene',), 'pbrtv3_world' )
    ]

class volumes_base(object):
    """
    Interior/Exterior Volumes Settings
    """
    bl_label = 'PBRTv3 Volumes'

    display_property_groups = [
        ( ('scene',), 'pbrtv3_volumes' )
    ]

    def draw_ior_menu(self, context):
        """
        This is a draw callback from property_group_renderer, due
        to ef_callback item in pbrtv3_volume_data.properties
        """
        vi = context.scene.pbrtv3_volumes.volumes_index
        lv = context.scene.pbrtv3_volumes.volumes[vi]

        if lv.fresnel_fresnelvalue == lv.fresnel_presetvalue:
            menu_text = lv.fresnel_presetstring
        else:
            menu_text = '-- Choose IOR preset --'

        cl = self.layout.column(align=True)
        cl.menu('PBRTv3_MT_ior_presets_volumes', text=menu_text)

    # overridden in order to draw the selected pbrtv3_volume_data property group
    def draw(self, context):
        super().draw(context)

        # row = self.layout.row(align=True)
        # row.menu("PBRTv3_MT_presets_volume", text=bpy.types.PBRTv3_MT_presets_volume.bl_label)
        # row.operator("luxrender.preset_volume_add", text="", icon="ZOOMIN")
        # row.operator("luxrender.preset_volume_add", text="", icon="ZOOMOUT").remove_active = True

        if len(context.scene.pbrtv3_volumes.volumes) > 0:
            current_vol_ind = context.scene.pbrtv3_volumes.volumes_index
            current_vol = context.scene.pbrtv3_volumes.volumes[current_vol_ind]

            # Here we draw the currently selected pbrtv3_volumes_data property group
            if current_vol.nodetree:
                if not UsePBRTv3Core():
                    self.layout.label('Volume nodes not supported in Classic API', icon='ERROR')

                self.layout.prop_search(current_vol, "nodetree", bpy.data, "node_groups")

                if current_vol.nodetree in bpy.data.node_groups:
                    nodetree = bpy.data.node_groups[current_vol.nodetree]

                    output_node = None
                    for node in nodetree.nodes:
                        if node.bl_idname == 'pbrtv3_volume_output_node':
                            output_node = node
                            break

                    if output_node:
                        self.layout.template_node_view(nodetree, output_node, output_node.inputs[0])
                    else:
                        self.layout.label("No output node")
                else:
                    # Nodetree name is invalid (because nodetree is missing or was renamed)
                    self.layout.label('Invalid nodetree name, select a nodetree.', icon='ERROR')
            else:
                # 'name' is not a member of current_vol.properties,
                # so we draw it explicitly
                self.layout.prop(current_vol, 'name')

                col = self.layout.column()
                col.enabled = UsePBRTv3Core()
                col.operator('luxrender.add_volume_nodetree', icon='NODETREE')
                if not UsePBRTv3Core():
                    self.layout.label('Volume nodes not supported in Classic API', icon='INFO')
                self.layout.separator()

                # Here we draw the currently selected pbrtv3_volumes_data property group
                for control in current_vol.controls:
                    # Don't show the "Light Emitter" checkbox in Classic API mode, can't do this in properties/world.py
                    if not (not UsePBRTv3Core() and control == 'use_emission'):
                        self.draw_column(
                            control,
                            self.layout,
                            current_vol,
                            context,
                            property_group=current_vol
                        )


@PBRTv3Addon.addon_register_class
class volumes_world(volumes_base, world_panel):
    pass


@PBRTv3Addon.addon_register_class
class volumes_material(volumes_base, pbrtv3_material_base):
    @classmethod
    def poll(cls, context):
        return super().poll(context) and (
            context.material.pbrtv3_material.Interior_volume
            or
            context.material.pbrtv3_material.Exterior_volume
        )
