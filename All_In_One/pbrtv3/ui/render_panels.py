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

from ..outputs.luxcore_api import UsePBRTv3Core, pyluxcore
from .. import PBRTv3Addon

from .lamps import lamps_panel
from .imageeditor_panel import imageeditor_panel


class render_panel(bl_ui.properties_render.RenderButtonsPanel, property_group_renderer):
    """
    Base class for render engine settings panels
    """

    COMPAT_ENGINES = 'PBRTv3_RENDER'


@PBRTv3Addon.addon_register_class
class render_settings(render_panel):
    """
    Render settings UI Panel
    """

    bl_label = 'PBRTv3 Settings'

    display_property_groups = [
        ( ('scene',), 'pbrtv3_rendermode', lambda: not UsePBRTv3Core() ),
        ( ('scene',), 'pbrtv3_integrator', lambda: not UsePBRTv3Core() ),
        ( ('scene',), 'pbrtv3_sampler', lambda: not UsePBRTv3Core() ),
        ( ('scene',), 'pbrtv3_volumeintegrator', lambda: not UsePBRTv3Core() ),
        ( ('scene',), 'pbrtv3_filter', lambda: not UsePBRTv3Core() ),
        ( ('scene',), 'pbrtv3_accelerator', lambda: not UsePBRTv3Core() ),
        ( ('scene',), 'pbrtv3_halt', lambda: not UsePBRTv3Core() ),
        ( ('scene',), 'luxcore_enginesettings', lambda: UsePBRTv3Core() ),
    ]

    def draw(self, context):
        layout = self.layout
        engine_settings = context.scene.luxcore_enginesettings

        if not UsePBRTv3Core():
            row = layout.row(align=True)
            rd = context.scene.render
            split = layout.split()
            row.menu("PBRTv3_MT_presets_engine", text=bpy.types.PBRTv3_MT_presets_engine.bl_label)
            row.operator("luxrender.preset_engine_add", text="", icon="ZOOMIN")
            row.operator("luxrender.preset_engine_add", text="", icon="ZOOMOUT").remove_active = True

        # Draw PBRTv3Core stuff above settings defined via property group (device selection)
        # This is done here so the device enums are expanded properly (horizontal, not vertical)
        if UsePBRTv3Core():
            vs = context.scene.view_settings
            if vs.view_transform != 'Default' or vs.exposure != 0 or vs.gamma != 1 or vs.look != 'None' or vs.use_curve_mapping:
                col = layout.column(align=True)
                col.scale_y = 0.8
                col.label('Color Management not using default values!', icon='ERROR')
                col.label('Viewport render might not match final render.')
                layout.operator('luxrender.fix_color_management')

            # Engines
            split = layout.split()

            row = split.row()
            sub = row.row()
            sub.label(text='Engines:')

            sub.prop(engine_settings, 'renderengine_type')

            # Device enums
            split = layout.split()

            row = split.row()
            sub = row.row()
            sub.label(text='Final Device:')

            row = split.row()
            sub = row.row()

            if engine_settings.renderengine_type in ['PATH', 'TILEPATH']:
                # These engines have OpenCL versions
                sub.prop(engine_settings, 'device', expand=True)
            else:
                # Fake device enum, always disabled, to show that BIDIR and BIDIRVM only have CPU support
                sub.enabled = False
                sub.prop(engine_settings, 'device_cpu_only', expand=True)

            split = layout.split()

            row = split.row()
            sub = row.row()
            sub.label(text='Viewport Device:')

            row = split.row()
            sub = row.row()

            if engine_settings.renderengine_type in ['PATH', 'TILEPATH']:
                # These engines have OpenCL versions
                sub.prop(engine_settings, 'device_preview', expand=True)
            else:
                # Fake device enum, always disabled, to show that BIDIR and BIDIRVM only have CPU support
                sub.enabled = False
                sub.prop(engine_settings, 'device_cpu_only', expand=True)

            if engine_settings.renderengine_type == 'TILEPATH':
                row = layout.row()
                row.label('')
                row.prop(engine_settings, 'biaspath_use_path_in_viewport')

            if engine_settings.renderengine_type == 'TILEPATH':
                split = layout.split()

                row = split.row()
                sub = row.row()
                sub.label(text='')

                row = split.row()
                sub = row.row()
                sub.prop(engine_settings, 'biaspath_show_sample_estimates', toggle=True, icon='TRIA_DOWN')

                if engine_settings.biaspath_show_sample_estimates:
                    # Sample settings
                    aa = engine_settings.biaspath_sampling_aa_size
                    if engine_settings.device == 'CPU':
                        diffuse = engine_settings.biaspath_sampling_diffuse_size
                        glossy = engine_settings.biaspath_sampling_glossy_size
                        specular = engine_settings.biaspath_sampling_specular_size
                    else:
                        diffuse = glossy = specular = aa
                    # Pathdepth settings
                    depth_total = engine_settings.path_pathdepth_total
                    depth_diffuse = engine_settings.path_pathdepth_diffuse
                    depth_glossy = engine_settings.path_pathdepth_glossy
                    depth_specular = engine_settings.path_pathdepth_specular

                    col = layout.column(align=True)
                    col.scale_y = 0.6
                    
                    # Pixel samples
                    aaSamplesCount = aa ** 2
                    col.label(text='AA: %d' % aaSamplesCount)

                    # Diffuse samples
                    maxDiffusePathDepth = max(0, min(depth_total, depth_diffuse - 1))
                    diffuseSamplesCount = aaSamplesCount * (diffuse ** 2)
                    maxDiffuseSamplesCount = diffuseSamplesCount * maxDiffusePathDepth
                    col.label(text='Diffuse: %d (with max. bounces %d: %d)' %
                                      (diffuseSamplesCount, maxDiffusePathDepth, maxDiffuseSamplesCount))

                    # Glossy samples
                    maxGlossyPathDepth = max(0, min(depth_total, depth_glossy - 1))
                    glossySamplesCount = aaSamplesCount * (glossy ** 2)
                    maxGlossySamplesCount = glossySamplesCount * maxGlossyPathDepth
                    col.label(text='Glossy: %d (with max. bounces %d: %d)' %
                                      (glossySamplesCount, maxGlossyPathDepth, maxGlossySamplesCount))

                    # Specular samples
                    maxSpecularPathDepth = max(0, min(depth_total, depth_specular - 1))
                    specularSamplesCount = aaSamplesCount * (specular ** 2)
                    maxSpecularSamplesCount = specularSamplesCount * maxSpecularPathDepth
                    col.label(text='Specular: %d (with max. bounces %d: %d)' %
                                      (specularSamplesCount, maxSpecularPathDepth, maxSpecularSamplesCount))

                    # TODO: implement - problem: how to get the number of light sources in the scene? (remember that
                    # each triangle of a meshlight counts as one lightsource)
                    # Direct light samples
                    #directLightSamplesCount = aaSamplesCount * firstVertexLightSampleCount *
                    #        (directLightSamples * directLightSamples) * renderConfig->scene->lightDefs.GetSize()
                    #SLG_LOG("[BiasPathCPURenderEngine] Direct light samples on first hit: " << directLightSamplesCount)

                    # Total samples for a pixel with hit on diffuse surfaces
                    col.label(text='Total on diffuse surfaces: %d' %
                                      (maxDiffuseSamplesCount + diffuseSamplesCount * max(0, maxDiffusePathDepth - 1)))

                    '''
                    // Total samples for a pixel with hit on diffuse surfaces
                    SLG_LOG("[BiasPathCPURenderEngine] Total samples for a pixel with hit on diffuse surfaces: " <<
                            // Direct light sampling on first hit
                            directLightSamplesCount +
                            // Diffuse samples
                            maxDiffuseSamplesCount +
                            // Direct light sampling for diffuse samples
                            diffuseSamplesCount * Max<int>(0, maxDiffusePathDepth - 1));
                    '''


        # Draw property groups
        super().draw(context)


@PBRTv3Addon.addon_register_class
class device_settings(render_panel):
    """
    OpenCL Devices UI Panel
    """

    bl_label = 'PBRTv3 Compute Settings'

    def draw(self, context):
        engine_settings = context.scene.luxcore_enginesettings
        render_mode = context.scene.pbrtv3_rendermode.rendermode
    
        if (render_mode in ['hybridpath', 'luxcorepathocl', 'luxcorebiaspathocl'] and not UsePBRTv3Core()) \
                or ((UsePBRTv3Core() and (engine_settings.renderengine_type in ['PATH', 'TILEPATH']
                                       and engine_settings.device == 'OCL')
                or engine_settings.device_preview == 'OCL')):
            self.layout.label('OpenCL Settings:')
            
            if UsePBRTv3Core():
                self.layout.prop(engine_settings, 'opencl_settings_type', expand=True)

            if UsePBRTv3Core() and engine_settings.opencl_settings_type == 'SIMPLE':
                row = self.layout.row()
                row.prop(engine_settings, 'opencl_use_all_gpus')
                row.prop(engine_settings, 'opencl_use_all_cpus')

            elif not UsePBRTv3Core() or engine_settings.opencl_settings_type == 'ADVANCED':
                if UsePBRTv3Core():
                    self.layout.prop(context.scene.luxcore_enginesettings, 'use_opencl_always_enabled')
                    self.layout.prop(context.scene.luxcore_enginesettings, 'film_use_opencl')
                    self.layout.prop(context.scene.luxcore_enginesettings, 'kernelcache')

                self.layout.operator('luxrender.opencl_device_list_update')

                # This is a "special" panel section for the list of OpenCL devices
                if len(context.scene.luxcore_enginesettings.luxcore_opencl_devices) > 0:
                    for dev in context.scene.luxcore_enginesettings.luxcore_opencl_devices:
                        row = self.layout.row()
                        row.prop(dev, 'opencl_device_enabled', text='')
                        subrow = row.row()
                        subrow.enabled = dev.opencl_device_enabled
                        subrow.label(dev.name)
                else:
                    self.layout.label('No OpenCL devices available', icon='ERROR')

        if UsePBRTv3Core() and (engine_settings.renderengine_type in ['BIDIR', 'BIDIRVM']
                or engine_settings.device == 'CPU'
                or engine_settings.device_preview == 'CPU'):
            self.layout.label('CPU Settings:')

            if engine_settings.auto_threads:
                self.layout.prop(engine_settings, 'auto_threads')
            else:
                row = self.layout.row()
                sub = row.row()
                sub.prop(engine_settings, 'auto_threads')
                sub.prop(engine_settings, 'native_threads_count')

        if not UsePBRTv3Core() and not 'ocl' in render_mode:
            # Classic Threads
            threads = context.scene.pbrtv3_engine
            row = self.layout.row()
            row.prop(threads, 'threads_auto')
            if not threads.threads_auto:
                row.prop(threads, 'threads')

        # Tile settings
        if UsePBRTv3Core() and context.scene.luxcore_enginesettings.renderengine_type == 'TILEPATH':
            self.layout.prop(engine_settings, 'tile_size')
			
@PBRTv3Addon.addon_register_class
class translator(render_panel):
    """
    Translator settings UI Panel
    """

    bl_label = 'PBRTv3 Export Settings'
    bl_options = {'DEFAULT_CLOSED'}

    display_property_groups = [
        ( ('scene',), 'luxcore_scenesettings', lambda: UsePBRTv3Core() ),
        ( ('scene',), 'pbrtv3_engine', lambda: not UsePBRTv3Core() ),
        ( ('scene',), 'pbrtv3_testing', lambda: not UsePBRTv3Core() ),
        ( ('scene',), 'luxcore_translatorsettings', lambda: UsePBRTv3Core() ),
    ]

    def draw(self, context):
        if not UsePBRTv3Core():
            super().draw(context)
            row = self.layout.row(align=True)
            rd = context.scene.render
        else:
            super().draw(context)
            self.layout.label('Custom PBRTv3Core config properties:')
            self.layout.prop(context.scene.luxcore_enginesettings, 'custom_properties')

@PBRTv3Addon.addon_register_class
class networking(render_panel):
    """
    Networking settings UI Panel
    """

    bl_label = 'PBRTv3 Networking'
    bl_options = {'DEFAULT_CLOSED'}

    display_property_groups = [
        ( ('scene',), 'pbrtv3_networking', lambda: not UsePBRTv3Core() )
    ]

    def draw_header(self, context):
        if not UsePBRTv3Core():
            self.layout.prop(context.scene.pbrtv3_networking, "use_network_servers", text="")

    def draw(self, context):
        if not UsePBRTv3Core():
            row = self.layout.row(align=True)
            row.menu("PBRTv3_MT_presets_networking", text=bpy.types.PBRTv3_MT_presets_networking.bl_label)
            row.operator("luxrender.preset_networking_add", text="", icon="ZOOMIN")
            row.operator("luxrender.preset_networking_add", text="", icon="ZOOMOUT").remove_active = True
        else:
            self.layout.label("Note: not yet supported by PBRTv3Core")

        super().draw(context)

@PBRTv3Addon.addon_register_class
class postprocessing(render_panel):
    """
    Post Pro UI panel
    """

    bl_label = 'Post Processing'
    bl_options = {'DEFAULT_CLOSED'}

    # We make our own post-pro panel so we can have one without BI's options
    # here. Theoretically, if Lux gains the ability to do lens effects through
    # the command line/API, we could add that here

    def draw(self, context):
        layout = self.layout

        rd = context.scene.render

        split = layout.split()

        col = split.column()
        col.prop(rd, "use_compositing")
        col.prop(rd, "use_sequencer")

        split.prop(rd, "dither_intensity", text="Dither", slider=True)
