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

#import bpy
from bpy.types import Panel, Menu

import bl_ui
from bl_ui.properties_render import RenderButtonsPanel

from ..extensions_framework.ui import property_group_renderer

from .. import MitsubaAddon


# Add options by render image/anim buttons
def render_start_options(self, context):
    if context.scene.render.engine == 'MITSUBA_RENDER':
        col = self.layout.column()
        #row = self.layout.row()
        col.prop(context.scene.mitsuba_engine, "export_type", text="Export Type")

        if context.scene.mitsuba_engine.export_type == 'EXT':
            col.prop(context.scene.mitsuba_engine, "binary_name", text="Render Using")
        #if context.scene.mitsuba_engine.export_type == 'INT':
        #    row.prop(context.scene.mitsuba_engine, "write_files", text="Write to Disk")
        #    row.prop(context.scene.mitsuba_engine, "integratedimaging", text="Integrated Imaging")

bl_ui.properties_render.RENDER_PT_render.append(render_start_options)


class mts_render_panel(RenderButtonsPanel, property_group_renderer):
    '''
    Base class for render engine settings panels
    '''

    COMPAT_ENGINES = {'MITSUBA_RENDER'}


@MitsubaAddon.addon_register_class
class MitsubaRender_MT_engine_presets(Menu):
    bl_label = "Mitsuba Engine Presets"
    preset_subdir = "mitsuba/engine"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


@MitsubaAddon.addon_register_class
class MitsubaRender_PT_motion_blur(RenderButtonsPanel, Panel):
    bl_label = "Motion Blur"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'MITSUBA_RENDER'}

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return rd.engine in cls.COMPAT_ENGINES

    def draw_header(self, context):
        rd = context.scene.render

        self.layout.prop(rd, "use_motion_blur", text="")

    def draw(self, context):
        layout = self.layout

        rd = context.scene.render
        layout.active = rd.use_motion_blur

        row = layout.row()
        row.prop(rd, "motion_blur_samples")
        row.prop(rd, "motion_blur_shutter")


@MitsubaAddon.addon_register_class
class MitsubaRender_PT_active_film(mts_render_panel):
    '''
    Active Camera Film settings UI Panel
    '''

    bl_label = "Active Camera Film Settings"
    bl_options = {'DEFAULT_CLOSED'}

    display_property_groups = [
        (('scene', 'camera', 'data', 'mitsuba_camera'), 'mitsuba_film')
    ]


@MitsubaAddon.addon_register_class
class MitsubaRender_PT_engine_presets(mts_render_panel):
    '''
    Engine settings presets UI Panel
    '''

    bl_label = 'Engine Presets'

    def draw(self, context):
        row = self.layout.row(align=True)
        row.menu("MitsubaRender_MT_engine_presets")
        row.operator("mitsuba.preset_engine_add", text="", icon="ZOOMIN")
        row.operator("mitsuba.preset_engine_add", text="", icon="ZOOMOUT").remove_active = True


@MitsubaAddon.addon_register_class
class MitsubaRender_PT_engine(mts_render_panel):
    '''
    Engine settings UI Panel
    '''

    bl_label = 'Engine Settings'

    display_property_groups = [
        (('scene',), 'mitsuba_engine')
    ]


@MitsubaAddon.addon_register_class
class MitsubaRender_PT_integrator(mts_render_panel):
    '''
    Integrator settings UI Panel
    '''

    bl_label = 'Integrator Settings'

    display_property_groups = [
        (('scene',), 'mitsuba_integrator')
    ]


@MitsubaAddon.addon_register_class
class MitsubaRender_PT_adaptive(mts_render_panel):
    '''
    Adaptive settings UI Panel
    '''

    bl_label = 'Use Adaptive Integrator'
    bl_options = {'DEFAULT_CLOSED'}
    display_property_groups = [
        (('scene', 'mitsuba_integrator',), 'mitsuba_adaptive')
    ]

    def draw_header(self, context):
        self.layout.prop(context.scene.mitsuba_integrator.mitsuba_adaptive, "use_adaptive", text="")

    def draw(self, context):
        self.layout.active = (context.scene.mitsuba_integrator.mitsuba_adaptive.use_adaptive)
        return super().draw(context)


@MitsubaAddon.addon_register_class
class MitsubaRender_PT_irrcache(mts_render_panel):
    '''
    Sampler settings UI Panel
    '''

    bl_label = 'Use Irradiance Cache'
    bl_options = {'DEFAULT_CLOSED'}
    display_property_groups = [
        (('scene', 'mitsuba_integrator',), 'mitsuba_irrcache')
    ]

    def draw_header(self, context):
        self.layout.prop(context.scene.mitsuba_integrator.mitsuba_irrcache, "use_irrcache", text="")

    def draw(self, context):
        self.layout.active = (context.scene.mitsuba_integrator.mitsuba_irrcache.use_irrcache)
        return super().draw(context)


@MitsubaAddon.addon_register_class
class MitsubaRender_PT_sampler(mts_render_panel):
    '''
    Sampler settings UI Panel
    '''

    bl_label = 'Sampler Settings'

    display_property_groups = [
        (('scene',), 'mitsuba_sampler')
    ]


@MitsubaAddon.addon_register_class
class MitsubaRender_PT_testing(mts_render_panel):
    bl_label = 'Test/Debugging Options'
    bl_options = {'DEFAULT_CLOSED'}

    display_property_groups = [
        (('scene',), 'mitsuba_testing')
    ]
