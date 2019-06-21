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
from bl_ui.properties_render_layer import RenderLayerButtonsPanel

from .. import MitsubaAddon


class mts_render_layer_panel(RenderLayerButtonsPanel, Panel):
    '''
    Base class for render engine settings panels
    '''

    COMPAT_ENGINES = {'MITSUBA_RENDER'}


@MitsubaAddon.addon_register_class
class MitsubaRenderLayer_PT_layers(mts_render_layer_panel):
    '''
    Render Layers panel
    '''

    bl_label = 'Layer'
    bl_context = "render_layer"

    def draw(self, context):
        #Add in Blender's layer stuff, this is taken from Blender's startup/properties_render_layer.py
        layout = self.layout

        scene = context.scene
        rd = scene.render
        rl = rd.layers.active

        split = layout.split()

        col = split.column()
        col.prop(scene, "layers", text="Scene")
        col.label(text="")
        col = split.column()
        col.prop(rl, "layers", text="Layer")
