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
import bl_ui
import bpy

from ..extensions_framework.ui import property_group_renderer

from ..outputs.luxcore_api import UseLuxCore
from .. import LuxRenderAddon


class camera_panel(bl_ui.properties_data_camera.CameraButtonsPanel, property_group_renderer):
    COMPAT_ENGINES = 'LUXRENDER_RENDER'


@LuxRenderAddon.addon_register_class
class camera(camera_panel):
    bl_label = 'LuxRender Camera'

    display_property_groups = [
        ( ('camera',), 'luxrender_camera' )
    ]


@LuxRenderAddon.addon_register_class
class film(camera_panel):
    bl_label = 'LuxRender Film'

    display_property_groups = [
        ( ('camera', 'luxrender_camera'), 'luxrender_film', lambda: not UseLuxCore() ),
        ( ('camera', 'luxrender_camera', 'luxrender_film'), 'luxrender_colorspace', lambda: not UseLuxCore() ),
        ( ('camera', 'luxrender_camera', 'luxrender_film'), 'luxrender_tonemapping',lambda: not UseLuxCore() ),
    ]

    def draw_crf_preset_menu(self, context):
        self.layout.menu('CAMERA_MT_luxrender_crf',
                         text=context.camera.luxrender_camera.luxrender_film.luxrender_colorspace.crf_preset)

@LuxRenderAddon.addon_register_class
class imagepipeline(camera_panel):
    """
    LuxCore Imagepipeline settings UI Panel
    """

    bl_label = 'LuxCore Imagepipeline'
    bl_options = {'DEFAULT_CLOSED'}

    display_property_groups = [
        ( ('camera', 'luxrender_camera'), 'luxcore_imagepipeline_settings' ),
    ]

    def draw(self, context):
        if UseLuxCore():
            layout = self.layout
            super().draw(context)

    def draw_crf_preset_menu(self, context):
        self.layout.menu('IMAGEPIPELINE_MT_luxrender_crf',
                         text=context.camera.luxrender_camera.luxcore_imagepipeline_settings.crf_preset)
