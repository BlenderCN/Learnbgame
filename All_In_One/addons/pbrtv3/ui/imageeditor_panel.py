# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond, Simon Wendsche (BYOB)
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

from ..outputs.luxcore_api import UsePBRTv3Core, pyluxcore
from .. import PBRTv3Addon


class imageeditor_panel(property_group_renderer):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    COMPAT_ENGINES = 'PBRTv3_RENDER'

    @classmethod
    def poll(cls, context):
        engine_is_lux = context.scene.render.engine in cls.COMPAT_ENGINES
        return engine_is_lux and UsePBRTv3Core()


@PBRTv3Addon.addon_register_class
class rendering_controls_panel(imageeditor_panel):
    bl_label = 'PBRTv3 Controls'
    COMPAT_ENGINES = 'PBRTv3_RENDER'

    def draw(self, context):
        if context.scene.luxcore_rendering_controls.pause_render:
            button_text = 'Resume Render'
            button_icon = 'PLAY'
        else:
            button_text = 'Pause Render'
            button_icon = 'PAUSE'

        self.layout.prop(context.scene.luxcore_rendering_controls, 'pause_render', toggle=True, text=button_text,
                         icon=button_icon)


@PBRTv3Addon.addon_register_class
class tonemapping_panel(imageeditor_panel):
    bl_label = 'PBRTv3 Imagepipeline'
    COMPAT_ENGINES = 'PBRTv3_RENDER'

    def draw(self, context):
        layout = self.layout

        if not hasattr(pyluxcore.RenderSession, 'Parse'):
            layout.label('Outdated PBRTv3Core version!', icon='INFO')
            return

        if context.scene.camera is None:
            layout.label('No camera in scene.')
            return

        lux_cam = context.scene.camera.data.pbrtv3_camera
        imagepipeline_settings = lux_cam.luxcore_imagepipeline

        layout.prop(imagepipeline_settings, 'displayinterval')

        layout.label('Tonemapper:')
        layout.prop(imagepipeline_settings, 'tonemapper_type')

        if imagepipeline_settings.tonemapper_type == 'TONEMAP_LINEAR':
            layout.prop(imagepipeline_settings, 'use_auto_linear')

        if imagepipeline_settings.tonemapper_type == 'TONEMAP_LINEAR':
            layout.prop(imagepipeline_settings, 'linear_scale')
        elif imagepipeline_settings.tonemapper_type == 'TONEMAP_LUXLINEAR':
            # Since fstop and exposure time should also change DOF/motion blur we don't show them here - ISO is enough
            layout.prop(lux_cam, 'sensitivity')
        elif imagepipeline_settings.tonemapper_type == 'TONEMAP_REINHARD02':
            sub = layout.column(align=True)
            sub.prop(imagepipeline_settings, 'reinhard_prescale')
            sub.prop(imagepipeline_settings, 'reinhard_postscale')
            sub.prop(imagepipeline_settings, 'reinhard_burn')

        layout.prop(imagepipeline_settings, 'use_bloom')
        if imagepipeline_settings.use_bloom:
            col = layout.column(align=True)
            col.prop(imagepipeline_settings, 'bloom_radius', slider=True)
            col.prop(imagepipeline_settings, 'bloom_weight', slider=True)

        layout.prop(imagepipeline_settings, 'use_color_aberration')
        if imagepipeline_settings.use_color_aberration:
            layout.prop(imagepipeline_settings, 'color_aberration_amount', slider=True)

        layout.prop(imagepipeline_settings, 'use_vignetting')
        if imagepipeline_settings.use_vignetting:
            layout.prop(imagepipeline_settings, 'vignetting_scale', slider=True)

        layout.label('Analog Film Simulation:')
        layout.prop(imagepipeline_settings, 'crf_type', expand=True)
        if imagepipeline_settings.crf_type == 'PRESET':
            layout.menu('IMAGEPIPELINE_MT_pbrtv3_crf', text=imagepipeline_settings.crf_preset)
        elif imagepipeline_settings.crf_type == 'FILE':
            layout.prop(imagepipeline_settings, 'crf_file')

        # TODO: can we only show the available passes here?
        layout.prop(imagepipeline_settings, 'output_switcher_pass')

        if imagepipeline_settings.output_switcher_pass == 'IRRADIANCE':
            sub = layout.column(align=True)
            row = sub.row(align=True)
            row.prop(imagepipeline_settings, 'contour_scale')
            row.prop(imagepipeline_settings, 'contour_range')
            row = sub.row(align=True)
            row.prop(imagepipeline_settings, 'contour_steps')
            row.prop(imagepipeline_settings, 'contour_zeroGridSize')

        # Background plugin (needs alpha pass. If alpha pass is not available, it cannot be activated during render)
        alpha_pass_available = True
        if not context.scene.pbrtv3_channels.enable_aovs:
            layout.label('Not available (passes disabled)', icon='ERROR')
            alpha_pass_available = False
        elif not context.scene.pbrtv3_channels.ALPHA:
            layout.label('Not available (Alpha pass disabled)', icon='ERROR')
            alpha_pass_available = False

        sub = layout.column()
        sub.enabled = alpha_pass_available
        sub.prop(imagepipeline_settings, 'use_background_image')
        if imagepipeline_settings.use_background_image:
            sub = sub.column()
            sub.active = alpha_pass_available
            sub.prop(imagepipeline_settings, 'background_image', text='')
            sub.prop(imagepipeline_settings, 'background_image_gamma')

        # Mist plugin (needs depth pass. If depth pass is not available, it cannot be activated during render)
        depth_pass_available = True
        if not context.scene.pbrtv3_channels.enable_aovs:
            layout.label('Not available (passes disabled)', icon='ERROR')
            depth_pass_available = False
        elif not context.scene.pbrtv3_channels.DEPTH:
            layout.label('Not available (Depth pass disabled)', icon='ERROR')
            depth_pass_available = False

        sub = layout.column()
        sub.enabled = depth_pass_available
        sub.prop(imagepipeline_settings, 'use_mist')
        if imagepipeline_settings.use_mist:
            sub = sub.column(align=True)
            sub.active = depth_pass_available
            sub.prop(imagepipeline_settings, 'mist_excludebackground')
            sub.prop(imagepipeline_settings, 'mist_color')
            sub.prop(imagepipeline_settings, 'mist_amount')
            sub.prop(imagepipeline_settings, 'mist_startdistance')
            sub.prop(imagepipeline_settings, 'mist_enddistance')


@PBRTv3Addon.addon_register_class
class halt_conditions_panel(imageeditor_panel):
    bl_label = 'PBRTv3 Halt Conditions'
    COMPAT_ENGINES = 'PBRTv3_RENDER'


    @classmethod
    def poll(cls, context):
        engine_is_lux = context.scene.render.engine in cls.COMPAT_ENGINES
        # Custom poll because the halt conditions of TILEPATH cannot be adjusted during the rendering
        return engine_is_lux and UsePBRTv3Core() and context.scene.luxcore_enginesettings.renderengine_type != 'TILEPATH'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.luxcore_enginesettings

        def draw_condition_pair(halt_conditon):
            """
            designed for halt conditons of the form 'use_<name>' and '<name>', where the first is the checkbox and
            the second is the value (e.g. 'use_halt_samples' is a boolean and 'halt_samples' is an int)
            """
            bool_name = 'use_%s' % halt_conditon

            row = layout.row()
            row.prop(settings, bool_name)
            sub = row.split()
            sub.active = getattr(settings, bool_name)
            sub.prop(settings, halt_conditon)

        draw_condition_pair('halt_samples')
        draw_condition_pair('halt_time')
        draw_condition_pair('halt_noise')


@PBRTv3Addon.addon_register_class
class rendering_statistics_panel(imageeditor_panel):
    bl_label = 'PBRTv3 Statistics'
    COMPAT_ENGINES = 'PBRTv3_RENDER'

    def draw(self, context):
        box = self.layout.box()
        for elem in context.scene.luxcore_rendering_controls.controls:
            box.prop(context.scene.luxcore_rendering_controls, elem)

        if bpy.context.scene.luxcore_enginesettings.renderengine_type == 'TILEPATH':
            box = self.layout.box()
            box.prop(context.scene.luxcore_tile_highlighting, 'use_tile_highlighting')

            if context.scene.luxcore_tile_highlighting.use_tile_highlighting:
                box.separator()
                box.prop(context.scene.luxcore_tile_highlighting, 'show_converged')
                box.prop(context.scene.luxcore_tile_highlighting, 'show_unconverged')
                box.prop(context.scene.luxcore_tile_highlighting, 'show_pending')