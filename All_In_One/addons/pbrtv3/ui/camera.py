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
import bl_ui
import bpy

from ..extensions_framework.ui import property_group_renderer

from ..outputs.luxcore_api import UsePBRTv3Core
from .. import PBRTv3Addon
from ..export import get_worldscale


class camera_panel(bl_ui.properties_data_camera.CameraButtonsPanel, property_group_renderer):
    COMPAT_ENGINES = 'PBRTv3_RENDER'


@PBRTv3Addon.addon_register_class
class camera(camera_panel):
    bl_label = 'PBRTv3 Camera'

    display_property_groups = [
        ( ('camera',), 'pbrtv3_camera' ),
    ]

    def draw(self, context):
        layout = self.layout
        blender_cam = context.camera
        lux_cam = context.camera.pbrtv3_camera

        # Draw property groups
        super().draw(context)

        if lux_cam.use_dof and not lux_cam.usemblur:
            # mblur already has a trailing separator if enabled
            layout.separator()

        layout.prop(lux_cam, "use_dof", toggle=True)

        if lux_cam.use_dof:
            split = layout.split()

            column = split.column()
            column.label("Focus:")
            column.prop(lux_cam, "autofocus")

            # Disable "Distance" and "Object" settings if autofocus is used
            sub_autofocus = column.column()
            sub_autofocus.enabled = not lux_cam.autofocus
            sub_autofocus.prop(blender_cam, "dof_object", text="")

            # Disable "Distance" setting if a focus object is used
            sub_distance = sub_autofocus.row()
            sub_distance.enabled = blender_cam.dof_object is None
            sub_distance.prop(blender_cam, "dof_distance", text="Distance")

            column = split.column(align=True)
            column.enabled = not UsePBRTv3Core()
            column.label("Bokeh Shape:")

            if UsePBRTv3Core():
                column.label("No PBRTv3Core support", icon="INFO")
            else:
                sub_bokeh = column.column()
                sub_bokeh.prop(lux_cam, "blades", text="Blades")
                sub_bokeh.prop(lux_cam, "distribution", text="")
                sub_bokeh.prop(lux_cam, "power", text="Power")

            layout.label("DoF strength is controlled by f/Stop value", icon="INFO")

        if UsePBRTv3Core():
            if lux_cam.enable_clipping_plane or lux_cam.use_dof:
                layout.separator()

            layout.prop(lux_cam, "enable_clipping_plane", toggle=True)

            if lux_cam.enable_clipping_plane:
                layout.prop_search(lux_cam, "clipping_plane_obj", context.scene, "objects", text="Plane")


@PBRTv3Addon.addon_register_class
class film(camera_panel):
    bl_label = 'PBRTv3 Film'

    display_property_groups = [
        ( ('camera', 'pbrtv3_camera'), 'pbrtv3_film', lambda: not UsePBRTv3Core() ),
        ( ('camera', 'pbrtv3_camera', 'pbrtv3_film'), 'pbrtv3_colorspace', lambda: not UsePBRTv3Core() ),
        ( ('camera', 'pbrtv3_camera', 'pbrtv3_film'), 'pbrtv3_tonemapping', lambda: not UsePBRTv3Core() ),
        ( ('camera', 'pbrtv3_camera'), 'luxcore_imagepipeline', lambda: UsePBRTv3Core() ),
    ]

    def draw_crf_preset_menu(self, context):
        if UsePBRTv3Core():
            self.layout.menu('IMAGEPIPELINE_MT_pbrtv3_crf',
                         text=context.camera.pbrtv3_camera.luxcore_imagepipeline.crf_preset)
        else:
            self.layout.menu('CAMERA_MT_pbrtv3_crf',
                         text=context.camera.pbrtv3_camera.pbrtv3_film.pbrtv3_colorspace.crf_preset)

    def draw(self, context):
        layout = self.layout

        if UsePBRTv3Core():
            imagepipeline_settings = context.scene.camera.data.pbrtv3_camera.luxcore_imagepipeline

            # Show warning in case of missing passes
            if imagepipeline_settings.use_background_image:
                if not context.scene.pbrtv3_channels.enable_aovs:
                    layout.label('Background image not available (passes disabled)', icon='ERROR')
                elif not context.scene.pbrtv3_channels.ALPHA:
                    layout.label('Background image not available (Alpha pass disabled)', icon='ERROR')

            if imagepipeline_settings.use_mist:
                if not context.scene.pbrtv3_channels.enable_aovs:
                    layout.label('Mist not available (passes disabled)', icon='ERROR')
                elif not context.scene.pbrtv3_channels.DEPTH:
                    layout.label('Mist not available (Depth pass disabled)', icon='ERROR')

        super().draw(context)

        if UsePBRTv3Core():
            imagepipeline_settings = context.scene.camera.data.pbrtv3_camera.luxcore_imagepipeline
            layout.label('Framerate: %d fps' % (1 / (imagepipeline_settings.viewport_interval / 1000)))
