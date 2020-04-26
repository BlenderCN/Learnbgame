# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Simon Wendsche
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

import os

from ...outputs.luxcore_api import pyluxcore
from ...extensions_framework import util as efutil

class ConfigExporter(object):
    def __init__(self, luxcore_exporter, blender_scene, is_viewport_render=False):
        self.luxcore_exporter = luxcore_exporter
        self.blender_scene = blender_scene
        self.is_viewport_render = is_viewport_render
        
        self.properties = pyluxcore.Properties()

        self.outputCounter = 0
        self.material_id_mask_counter = 0
        self.by_material_id_counter = 0


    def convert(self, film_width, film_height):
        realtime_settings = self.blender_scene.luxcore_realtimesettings

        if self.is_viewport_render and not realtime_settings.use_finalrender_settings:
            self.__convert_realtime_settings()
        else:
            # Config for final render
            self.__convert_engine()
            self.__convert_filter()
            self.__convert_sampler()

        self.__convert_film_size(film_width, film_height)
        self.__convert_accelerator()
        self.__convert_custom_props()
        self.__convert_imagepipeline()
        self.__convert_all_channels()

        return self.properties


    def convert_channel(self, channelName, id=-1):
        """
        Sets configuration properties for LuxCore AOV output
        """

        # the OpenCL engines only support 1 MATERIAL_ID_MASK, 1 BY_MATERIAL_ID channel and 8 RADIANCE_GROUP channels
        engine = self.blender_scene.luxcore_enginesettings.renderengine_type
        is_ocl_engine = engine in ['BIASPATHOCL', 'PATHOCL']
        if is_ocl_engine:
            if channelName == 'MATERIAL_ID_MASK':
                if self.material_id_mask_counter == 0:
                    self.material_id_mask_counter += 1
                else:
                    # don't create the output channel
                    return

            elif channelName == 'BY_MATERIAL_ID':
                if self.by_material_id_counter == 0:
                    self.by_material_id_counter += 1
                else:
                    # don't create the output channel
                    return

        if channelName == 'RADIANCE_GROUP':
            if id > 7 and is_ocl_engine:
                # don't create the output channel
                LuxLog('WARNING: OpenCL engines support a maximum of 8 lightgroups! Skipping this lightgroup (ID: %d)'
                       % id)
                return

        self.outputCounter += 1

        # list of channels that don't use an HDR format
        LDR_channels = ['RGB_TONEMAPPED', 'RGBA_TONEMAPPED', 'ALPHA', 'MATERIAL_ID', 'DIRECT_SHADOW_MASK',
                        'INDIRECT_SHADOW_MASK', 'MATERIAL_ID_MASK']

        # channel type (e.g. 'film.outputs.1.type')
        outputStringType = 'film.outputs.' + str(self.outputCounter) + '.type'
        self.properties.Set(pyluxcore.Property(outputStringType, [channelName]))

        # output filename (e.g. 'film.outputs.1.filename')
        suffix = ('.png' if (channelName in LDR_channels) else '.exr')
        outputStringFilename = 'film.outputs.' + str(self.outputCounter) + '.filename'
        filename = channelName + suffix if id == -1 else channelName + '_' + str(id) + suffix
        self.properties.Set(pyluxcore.Property(outputStringFilename, [filename]))

        # output id
        if id != -1:
            outputStringId = 'film.outputs.' + str(self.outputCounter) + '.id'
            self.properties.Set(pyluxcore.Property(outputStringId, [id]))


    def __convert_film_size(self, film_width, film_height):
        self.properties.Set(pyluxcore.Property('film.width', [film_width]))
        self.properties.Set(pyluxcore.Property('film.height', [film_height]))

    def __convert_imagepipeline(self):
        if self.blender_scene.camera is None:
            return
    
        imagepipeline_settings = self.blender_scene.camera.data.luxrender_camera.luxcore_imagepipeline_settings
        index = 0
        prefix = 'film.imagepipeline.'
    
        # Output switcher
        if imagepipeline_settings.output_switcher_pass != 'disabled':
            channel = imagepipeline_settings.output_switcher_pass
            self.properties.Set(pyluxcore.Property(prefix + str(index) + '.type', ['OUTPUT_SWITCHER']))
            self.properties.Set(pyluxcore.Property(prefix + str(index) + '.channel', [channel]))
            index += 1
    
        # Tonemapper
        tonemapper = imagepipeline_settings.tonemapper_type
        self.properties.Set(pyluxcore.Property(prefix + str(index) + '.type', [tonemapper]))
        # Note: TONEMAP_AUTOLINEAR has no parameters and is thus not in the if/elif block
        if tonemapper == 'TONEMAP_LINEAR':
            scale = imagepipeline_settings.linear_scale
            self.properties.Set(pyluxcore.Property(prefix + str(index) + '.scale', [scale]))
        elif tonemapper == 'TONEMAP_REINHARD02':
            prescale = imagepipeline_settings.reinhard_prescale
            postscale = imagepipeline_settings.reinhard_postscale
            burn = imagepipeline_settings.reinhard_burn
            self.properties.Set(pyluxcore.Property(prefix + str(index) + '.prescale', [prescale]))
            self.properties.Set(pyluxcore.Property(prefix + str(index) + '.postscale', [postscale]))
            self.properties.Set(pyluxcore.Property(prefix + str(index) + '.burn', [burn]))
        elif tonemapper == 'TONEMAP_LUXLINEAR':
            lux_camera = self.blender_scene.camera.data.luxrender_camera
            sensitivity = lux_camera.sensitivity
            exposure = lux_camera.exposure_time() if not self.is_viewport_render else lux_camera.exposure_time() * 2.25
            fstop = lux_camera.fstop
            self.properties.Set(pyluxcore.Property(prefix + str(index) + '.sensitivity', [sensitivity]))
            self.properties.Set(pyluxcore.Property(prefix + str(index) + '.exposure', [exposure]))
            self.properties.Set(pyluxcore.Property(prefix + str(index) + '.fstop', [fstop]))
        index += 1
    
        # Camera response function
        if imagepipeline_settings.crf_preset != 'None':
            preset = imagepipeline_settings.crf_preset
            self.properties.Set(pyluxcore.Property(prefix + str(index) + '.type', ['CAMERA_RESPONSE_FUNC']))
            self.properties.Set(pyluxcore.Property(prefix + str(index) + '.name', [preset]))
            index += 1
    
        # Contour lines for IRRADIANCE pass
        if imagepipeline_settings.output_switcher_pass == 'IRRADIANCE':
            self.properties.Set(pyluxcore.Property(prefix + str(index) + '.type', ['CONTOUR_LINES']))
            self.properties.Set(pyluxcore.Property(prefix + str(index) + '.range', [imagepipeline_settings.contour_range]))
            self.properties.Set(pyluxcore.Property(prefix + str(index) + '.scale', [imagepipeline_settings.contour_scale]))
            self.properties.Set(pyluxcore.Property(prefix + str(index) + '.steps', [imagepipeline_settings.contour_steps]))
            self.properties.Set(
                pyluxcore.Property(prefix + str(index) + '.zerogridsize', [imagepipeline_settings.contour_zeroGridSize]))
            index += 1
    
        # Gamma correction: Blender expects gamma corrected image in realtime preview, but not in final render
        if self.is_viewport_render:
            self.properties.Set(pyluxcore.Property(prefix + str(index) + '.type', ['GAMMA_CORRECTION']))
            self.properties.Set(pyluxcore.Property(prefix + str(index) + '.value', [2.2]))
            index += 1
    
        # Deprecated but used for backwardscompatibility
        if getattr(self.blender_scene.camera.data.luxrender_camera.luxrender_film, 'output_alpha'):
            self.properties.Set(pyluxcore.Property('film.alphachannel.enable', ['1']))
    
    
    def __convert_sampler(self):
        engine_settings = self.blender_scene.luxcore_enginesettings
    
        self.properties.Set(pyluxcore.Property('sampler.type', [engine_settings.sampler_type]))
    
        if engine_settings.advanced and engine_settings.sampler_type == 'METROPOLIS':
            self.properties.Set(pyluxcore.Property('sampler.metropolis.largesteprate', [engine_settings.largesteprate]))
            self.properties.Set(
                pyluxcore.Property('sampler.metropolis.maxconsecutivereject', [engine_settings.maxconsecutivereject]))
            self.properties.Set(
                pyluxcore.Property('sampler.metropolis.imagemutationrate', [engine_settings.imagemutationrate]))
    
    
    def __convert_filter(self):
        engine_settings = self.blender_scene.luxcore_enginesettings
    
        self.properties.Set(pyluxcore.Property('film.filter.type', [engine_settings.filter_type]))
        self.properties.Set(pyluxcore.Property('film.filter.width', [engine_settings.filter_width]))
    
    
    def __convert_accelerator(self):
        engine_settings = self.blender_scene.luxcore_enginesettings
        accelerator = engine_settings.accelerator_type
    
        # Embree does not support OpenCL engines
        if str.endswith(engine_settings.renderengine_type, 'OCL') and accelerator == 'EMBREE':
            accelerator = 'AUTO'
    
        self.properties.Set(pyluxcore.Property('accelerator.type', [accelerator]))
        self.properties.Set(pyluxcore.Property('accelerator.instances.enable', [engine_settings.instancing]))
    
    
    def __convert_engine(self):
        engine_settings = self.blender_scene.luxcore_enginesettings
        engine = engine_settings.renderengine_type
        if len(engine) == 0:
            engine = 'PATHCPU'
    
        if self.blender_scene.luxcore_translatorsettings.use_filesaver:
            output_path = efutil.filesystem_path(self.blender_scene.render.filepath)
            if not os.path.isdir(output_path):
                os.makedirs(output_path)
    
            self.properties.Set(pyluxcore.Property('renderengine.type', ['FILESAVER']))
            self.properties.Set(pyluxcore.Property('filesaver.directory', [output_path]))
            self.properties.Set(pyluxcore.Property('filesaver.renderengine.type', [engine]))
        else:
            self.properties.Set(pyluxcore.Property('renderengine.type', [engine]))
    
        if engine in ['BIASPATHCPU', 'BIASPATHOCL']:
            self.properties.Set(pyluxcore.Property('tile.size', [engine_settings.tile_size]))
            self.properties.Set(pyluxcore.Property('tile.multipass.enable',
                                                 [engine_settings.tile_multipass_enable]))
            self.properties.Set(pyluxcore.Property('tile.multipass.convergencetest.threshold',
                                                 [engine_settings.tile_multipass_convergencetest_threshold]))
            self.properties.Set(pyluxcore.Property('tile.multipass.convergencetest.threshold.reduction',
                                                 [engine_settings.tile_multipass_convergencetest_threshold_reduction]))
            self.properties.Set(pyluxcore.Property('biaspath.sampling.aa.size',
                                                 [engine_settings.biaspath_sampling_aa_size]))
            self.properties.Set(pyluxcore.Property('biaspath.sampling.diffuse.size',
                                                 [engine_settings.biaspath_sampling_diffuse_size]))
            self.properties.Set(pyluxcore.Property('biaspath.sampling.glossy.size',
                                                 [engine_settings.biaspath_sampling_glossy_size]))
            self.properties.Set(pyluxcore.Property('biaspath.sampling.specular.size',
                                                 [engine_settings.biaspath_sampling_specular_size]))
            self.properties.Set(pyluxcore.Property('biaspath.pathdepth.total',
                                                 [engine_settings.biaspath_pathdepth_total]))
            self.properties.Set(pyluxcore.Property('biaspath.pathdepth.diffuse',
                                                 [engine_settings.biaspath_pathdepth_diffuse]))
            self.properties.Set(pyluxcore.Property('biaspath.pathdepth.glossy',
                                                 [engine_settings.biaspath_pathdepth_glossy]))
            self.properties.Set(pyluxcore.Property('biaspath.pathdepth.specular',
                                                 [engine_settings.biaspath_pathdepth_specular]))
            self.properties.Set(pyluxcore.Property('biaspath.clamping.radiance.maxvalue',
                                                 [engine_settings.biaspath_clamping_radiance_maxvalue]))
            self.properties.Set(pyluxcore.Property('biaspath.clamping.pdf.value',
                                                 [engine_settings.biaspath_clamping_pdf_value]))
            self.properties.Set(pyluxcore.Property('biaspath.lights.samplingstrategy.type',
                                                 [engine_settings.biaspath_lights_samplingstrategy_type]))
        elif engine in ['PATHCPU', 'PATHOCL']:
            self.properties.Set(pyluxcore.Property('path.maxdepth', [engine_settings.path_maxdepth]))
            self.properties.Set(pyluxcore.Property('path.clamping.radiance.maxvalue',
                                                 [engine_settings.biaspath_clamping_radiance_maxvalue]))
            self.properties.Set(pyluxcore.Property('path.clamping.pdf.value',
                                                 [engine_settings.biaspath_clamping_pdf_value]))
        elif engine in ['BIDIRCPU']:
            self.properties.Set(pyluxcore.Property('path.maxdepth', [engine_settings.bidir_eyedepth]))
            self.properties.Set(pyluxcore.Property('light.maxdepth', [engine_settings.bidir_lightdepth]))
        elif engine in ['BIDIRVMCPU']:
            self.properties.Set(pyluxcore.Property('path.maxdepth', [engine_settings.bidirvm_eyedepth]))
            self.properties.Set(pyluxcore.Property('light.maxdepth', [engine_settings.bidirvm_lightdepth]))
            self.properties.Set(pyluxcore.Property('bidirvm.lightpath.count',
                                                 [engine_settings.bidirvm_lightpath_count]))
            self.properties.Set(pyluxcore.Property('bidirvm.startradius.scale',
                                                 [engine_settings.bidirvm_startradius_scale]))
            self.properties.Set(pyluxcore.Property('bidirvm.alpha', [engine_settings.bidirvm_alpha]))
    
        # CPU settings
        if engine_settings.native_threads_count > 0:
            self.properties.Set(
                pyluxcore.Property('native.threads.count', [engine_settings.native_threads_count]))
    
        # OpenCL settings
        if len(engine_settings.luxcore_opencl_devices) > 0:
            dev_string = ''
            for dev_index in range(len(engine_settings.luxcore_opencl_devices)):
                dev = engine_settings.luxcore_opencl_devices[dev_index]
                dev_string += '1' if dev.opencl_device_enabled else '0'
    
            self.properties.Set(pyluxcore.Property('opencl.devices.select', [dev_string]))
    
    
    def __convert_realtime_settings(self):
        realtime_settings = self.blender_scene.luxcore_realtimesettings
        engine_settings = self.blender_scene.luxcore_enginesettings
    
        # Renderengine
        if realtime_settings.device_type == 'CPU':
            engine = realtime_settings.cpu_renderengine_type
        elif realtime_settings.device_type == 'OCL':
            engine = realtime_settings.ocl_renderengine_type
        else:
            engine = 'PATHCPU'
    
        self.properties.Set(pyluxcore.Property('renderengine.type', [engine]))
    
        # use global clamping settings
        if engine in ['PATHCPU', 'PATHOCL']:
            self.properties.Set(pyluxcore.Property('path.clamping.radiance.maxvalue', [
                engine_settings.biaspath_clamping_radiance_maxvalue]))
            self.properties.Set(pyluxcore.Property('path.clamping.pdf.value',
                                                 [engine_settings.biaspath_clamping_pdf_value]))
    
        # OpenCL settings
        if len(self.blender_scene.luxcore_enginesettings.luxcore_opencl_devices) > 0:
            dev_string = ''
            for dev_index in range(len(self.blender_scene.luxcore_enginesettings.luxcore_opencl_devices)):
                dev = self.blender_scene.luxcore_enginesettings.luxcore_opencl_devices[dev_index]
                dev_string += '1' if dev.opencl_device_enabled else '0'
    
            self.properties.Set(pyluxcore.Property('opencl.devices.select', [dev_string]))
    
        # Sampler settings
        self.properties.Set(pyluxcore.Property('sampler.type', [realtime_settings.sampler_type]))
    
        # Filter settings
        if realtime_settings.device_type == 'CPU':
            filter_type = realtime_settings.filter_type_cpu
        elif realtime_settings.device_type == 'OCL':
            filter_type = realtime_settings.filter_type_ocl
    
        self.properties.Set(pyluxcore.Property('film.filter.type', [filter_type]))
        if filter_type != 'NONE':
            self.properties.Set(pyluxcore.Property('film.filter.width', [1.5]))
    
    
    def __convert_custom_props(self):
        engine_settings = self.blender_scene.luxcore_enginesettings
        # Custom Properties
        if engine_settings.advanced and engine_settings.custom_properties:
            custom_params = engine_settings.custom_properties.replace(' ', '').split('|')
            for prop in custom_params:
                prop = prop.split('=')
                self.properties.Set(pyluxcore.Property(prop[0], prop[1]))


    def __convert_all_channels(self):
        if self.blender_scene.camera is None:
            return

        luxrender_camera = self.blender_scene.camera.data.luxrender_camera
        output_switcher_channel = luxrender_camera.luxcore_imagepipeline_settings.output_switcher_pass
        channels = self.blender_scene.luxrender_channels

        if (channels.enable_aovs and not self.is_viewport_render) or output_switcher_channel != 'disabled':
            if channels.RGB:
                self.convert_channel('RGB')
            if channels.RGBA:
                self.convert_channel('RGBA')
            if channels.RGB_TONEMAPPED:
                self.convert_channel('RGB_TONEMAPPED')
            if channels.RGBA_TONEMAPPED:
                self.convert_channel('RGBA_TONEMAPPED')
            if channels.ALPHA or output_switcher_channel == 'ALPHA':
                self.convert_channel('ALPHA')
            if channels.DEPTH or output_switcher_channel == 'DEPTH':
                self.convert_channel('DEPTH')
            if channels.POSITION or output_switcher_channel == 'POSITION':
                self.convert_channel('POSITION')
            if channels.GEOMETRY_NORMAL or output_switcher_channel == 'GEOMETRY_NORMAL':
                self.convert_channel('GEOMETRY_NORMAL')
            if channels.SHADING_NORMAL or output_switcher_channel == 'SHADING_NORMAL':
                self.convert_channel('SHADING_NORMAL')
            if channels.MATERIAL_ID or output_switcher_channel == 'MATERIAL_ID':
                self.convert_channel('MATERIAL_ID')
            if channels.DIRECT_DIFFUSE or output_switcher_channel == 'DIRECT_DIFFUSE':
                self.convert_channel('DIRECT_DIFFUSE')
            if channels.DIRECT_GLOSSY or output_switcher_channel == 'DIRECT_GLOSSY':
                self.convert_channel('DIRECT_GLOSSY')
            if channels.EMISSION or output_switcher_channel == 'EMISSION':
                self.convert_channel('EMISSION')
            if channels.INDIRECT_DIFFUSE or output_switcher_channel == 'INDIRECT_DIFFUSE':
                self.convert_channel('INDIRECT_DIFFUSE')
            if channels.INDIRECT_GLOSSY or output_switcher_channel == 'INDIRECT_GLOSSY':
                self.convert_channel('INDIRECT_GLOSSY')
            if channels.INDIRECT_SPECULAR or output_switcher_channel == 'INDIRECT_SPECULAR':
                self.convert_channel('INDIRECT_SPECULAR')
            if channels.DIRECT_SHADOW_MASK or output_switcher_channel == 'DIRECT_SHADOW_MASK':
                self.convert_channel('DIRECT_SHADOW_MASK')
            if channels.INDIRECT_SHADOW_MASK or output_switcher_channel == 'INDIRECT_SHADOW_MASK':
                self.convert_channel('INDIRECT_SHADOW_MASK')
            if channels.UV or output_switcher_channel == 'UV':
                self.convert_channel('UV')
            if channels.RAYCOUNT or output_switcher_channel == 'RAYCOUNT':
                self.convert_channel('RAYCOUNT')
            if channels.IRRADIANCE or output_switcher_channel == 'IRRADIANCE':
                self.convert_channel('IRRADIANCE')


    def __convert_lightgroups(self):
        if not self.blender_scene.luxrender_lightgroups.ignore:
            for i in range(len(self.luxcore_exporter.lightgroup_cache)):
                self.convert_channel('RADIANCE_GROUP', i)