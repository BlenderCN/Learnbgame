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

from bl_ui.properties_world import WorldButtonsPanel

from .. import MitsubaAddon
from ..ui import node_tree_selector_draw, panel_node_draw


class mitsuba_world_node_panel(WorldButtonsPanel, Panel):
    COMPAT_ENGINES = {'MITSUBA_RENDER'}
    display_node_inputs = []

    def draw(self, context):
        for node, node_input in self.display_node_inputs:
            panel_node_draw(self.layout, context, context.world, node, node_input)

    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.world.mitsuba_nodes.nodetree


@MitsubaAddon.addon_register_class
class MitsubaWorld_PT_world(WorldButtonsPanel, Panel):
    '''
    Main World UI Panel
    '''

    bl_label = 'World Settings'
    COMPAT_ENGINES = {'MITSUBA_RENDER'}

    def draw(self, context):
        world = context.world

        if world is not None:
            layout = self.layout
            node_tree_selector_draw(layout, context, 'world')


@MitsubaAddon.addon_register_class
class MitsubaWorldNode_PT_environment(mitsuba_world_node_panel):
    '''
    World Environment Node UI Panel
    '''

    bl_label = 'Environment'
    display_node_inputs = [('MtsNodeWorldOutput', 'Environment')]


@MitsubaAddon.addon_register_class
class MitsubaWorldNode_PT_exterior(mitsuba_world_node_panel):
    '''
    World Node Exterior Medium UI Panel
    '''

    bl_label = 'Exterior Medium'
    display_node_inputs = [('MtsNodeWorldOutput', 'Exterior Medium')]
