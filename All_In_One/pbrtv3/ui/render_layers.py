# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond, Simon Wendsche
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

from .lamps import lamps_panel
from .imageeditor_panel import imageeditor_panel


class render_layers_panel(bl_ui.properties_render.RenderButtonsPanel, property_group_renderer):
    """
    Base class for render layer settings panels
    """

    COMPAT_ENGINES = 'PBRTv3_RENDER'


@PBRTv3Addon.addon_register_class
class layer_selector(render_layers_panel):
    """
    Render Layers Selector panel
    """

    bl_label = 'Layer Selector'
    bl_options = {'HIDE_HEADER'}
    bl_context = "render_layer"

    def draw(self, context):
        # Add in Blender's layer chooser, this is taken from Blender's startup/properties_render_layer.py
        layout = self.layout

        scene = context.scene
        rd = scene.render

        row = layout.row()
        row.template_list("RENDERLAYER_UL_renderlayers", "", rd, "layers", rd.layers, "active_index", rows=2)

        col = row.column(align=True)
        col.operator("scene.render_layer_add", icon='ZOOMIN', text="")
        col.operator("scene.render_layer_remove", icon='ZOOMOUT', text="")

        row = layout.row()
        rl = rd.layers.active
        if rl:
            row.prop(rl, "name")

        row.prop(rd, "use_single_layer", text="", icon_only=True)


@PBRTv3Addon.addon_register_class
class layers(render_layers_panel):
    """
    Render Layers panel
    """

    bl_label = 'Layer'
    bl_context = "render_layer"

    def draw(self, context):
        # Add in Blender's layer stuff, this is taken from Blender's startup/properties_render_layer.py
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


class lightgroups_base(object):
    """
    Light Groups Settings
    """

    bl_label = 'PBRTv3 Light Groups'

    is_imageeditor_panel = False

    def draw_header(self, context):
        if not self.is_imageeditor_panel:
            self.layout.label('', icon='OUTLINER_OB_LAMP')

    # overridden in order to draw a 'non-standard' panel
    def draw(self, context):
        if UsePBRTv3Core() and not hasattr(pyluxcore.RenderSession, 'Parse'):
            self.layout.label('Outdated PBRTv3Core version!', icon='INFO')
            self.layout.separator()

        def lightgroup_icon(enabled):
            return 'OUTLINER_OB_LAMP' if enabled else 'LAMP'

        def settings_toggle_icon(enabled):
            return 'TRIA_DOWN' if enabled else 'TRIA_RIGHT'

        def draw_lightgroup(lg, lg_index=None):
            is_default_group = lg_index is None

            split = self.layout.split()

            # OpenCL engines only support up to 8 lightgroups. Display a warning for each additional lightgroup.
            # Note that we use "lg_index > 6" because of the additional default lightgroup that has no index in this function
            enginesettings = context.scene.luxcore_enginesettings
            is_opencl_engine = enginesettings.device == 'OCL' or enginesettings.device_preview == 'OCL'
            split.active = not (is_opencl_engine and (lg_index is not None and lg_index > 6))

            col = split.column()
            sub = col.column(align=True)

            # Upper row (enable/disable, name, remove)
            box = sub.box()

            if not split.active:
                box.label('OpenCL engines only support 8 lightgroups!', icon='ERROR')

            row = box.row()
            row.prop(lg, 'show_settings', icon=settings_toggle_icon(lg.show_settings), icon_only=True, emboss=False)
            row.prop(lg, 'lg_enabled', icon=lightgroup_icon(lg.lg_enabled), icon_only=True, toggle=True)

            sub_row = row.row()
            if is_default_group:
                sub_row.label('Default Lightgroup')
            else:
                sub_row.enabled = lg.lg_enabled
                sub_row.prop(lg, 'name', text='')

            if not self.is_imageeditor_panel and not is_default_group:
                # Can't delete the default lightgroup 0, can't delete lightgroups during final render
                row.operator('luxrender.lightgroup_remove', text="", icon="X", emboss=False).lg_index = lg_index

            if lg.show_settings:
                # Lower row (gain settings, RGB gain, temperature)
                box = sub.box()
                box.enabled = lg.lg_enabled

                row = box.row()
                row.prop(lg, 'gain')

                if UsePBRTv3Core():
                    # RGB gain and temperature are not supported by Classic API
                    row = box.row()
                    row.prop(lg, 'use_rgb_gain')
                    sub = row.split()
                    sub.active = lg.use_rgb_gain
                    sub.prop(lg, 'rgb_gain')

                    row = box.row()
                    row.prop(lg, 'use_temperature')
                    sub = row.split()
                    sub.active = lg.use_temperature
                    sub.prop(lg, 'temperature', slider=True)

        # Merge button
        if not self.is_imageeditor_panel:
            row = self.layout.row()
            row.prop(context.scene.pbrtv3_lightgroups, 'ignore')

        # Default lightgroup (PBRTv3Core only)
        if UsePBRTv3Core():
            draw_lightgroup(context.scene.pbrtv3_lightgroups)

        # Normal light groups, this is a "special" panel section
        for lg_index in range(len(context.scene.pbrtv3_lightgroups.lightgroups)):
            lg = context.scene.pbrtv3_lightgroups.lightgroups[lg_index]
            draw_lightgroup(lg, lg_index)

        if not self.is_imageeditor_panel:
            self.layout.operator('luxrender.lightgroup_add', text='Add Lightgroup', icon='ZOOMIN')


@PBRTv3Addon.addon_register_class
class lightgroups_renderlayer(lightgroups_base, render_layers_panel):
    bl_context = 'render_layer'


@PBRTv3Addon.addon_register_class
class lightgroups_imageeditor(lightgroups_base, imageeditor_panel):
    is_imageeditor_panel = True


@PBRTv3Addon.addon_register_class
class lightgroups_lamps(lightgroups_base, lamps_panel):
    @classmethod
    def poll(cls, context):
        return super().poll(context) and context.lamp.pbrtv3_lamp.lightgroup


@PBRTv3Addon.addon_register_class
class materialgroups(render_layers_panel):
    """
    Material Groups Settings
    """

    bl_label = 'PBRTv3 Material Groups'
    bl_context = 'render_layer'

    def draw_header(self, context):
        self.layout.label('', icon='IMASEL')

    # overridden in order to draw a 'non-standard' panel
    def draw(self, context):
        if not UsePBRTv3Core():
            self.layout.label('Not supported in Classic API mode.')
            return

        def settings_toggle_icon(enabled):
            return 'TRIA_DOWN' if enabled else 'TRIA_RIGHT'

        def draw_materialgroup(mg, mg_index=None):
            split = self.layout.split()

            col = split.column()
            sub = col.column(align=True)

            # Upper row (enable/disable, name, remove)
            box = sub.box()
            row = box.row()

            row.prop(mg, 'show_settings', icon=settings_toggle_icon(mg.show_settings), emboss=False)
            row.prop(mg, 'name', text='')

            row.operator('luxrender.materialgroup_remove', text='', icon='X', emboss=False).mg_index = mg_index

            if mg.show_settings:
                box = sub.box()

                row = box.row()
                split = row.split(percentage=0.7, align=True)
                split.prop(mg, 'id')
                split.prop(mg, 'color')
                row = box.row()
                row.prop(mg, 'create_MATERIAL_ID_MASK')
                row.prop(mg, 'create_BY_MATERIAL_ID')

        # Draw all material groups
        for mg_index in range(len(context.scene.pbrtv3_materialgroups.materialgroups)):
            mg = context.scene.pbrtv3_materialgroups.materialgroups[mg_index]
            draw_materialgroup(mg, mg_index)

        self.layout.operator('luxrender.materialgroup_add', text='Add Materialgroup', icon='ZOOMIN')


@PBRTv3Addon.addon_register_class
class passes_aov(render_layers_panel):
    """
    Render passes UI panel
    """

    bl_label = 'PBRTv3 Passes'
    bl_options = {'DEFAULT_CLOSED'}
    bl_context = "render_layer"

    display_property_groups = [
        ( ('scene',), 'pbrtv3_lightgroups' )
    ]

    def draw_header(self, context):
        self.layout.label('', icon='RENDER_RESULT')

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        if UsePBRTv3Core():
            # Show AOV channel panel
            channels = context.scene.pbrtv3_channels
            split = layout.split()
            col = split.column()

            for control in channels.controls:
                self.draw_column(
                    control,
                    col,
                    channels,
                    context,
                    property_group=channels
                )
        else:
            # Add in the relevant bits from Blender's passes stuff, this is
            # taken from Blender's startup/properties_render_layer.py
            rd = scene.render
            rl = rd.layers.active
            split = layout.split()
            col = split.column()
            col.label(text="Passes:")
            col.prop(rl, "use_pass_combined")
            col.prop(rl, "use_pass_z")

        layout.separator()  # give a little gap to seperate next panel
