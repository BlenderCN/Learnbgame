# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
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
from ...export import get_output_filename
from .utils import is_lightgroup_opencl_compatible


class ConfigExporter(object):
    def __init__(self, luxcore_exporter, blender_scene, is_viewport_render=False):
        self.luxcore_exporter = luxcore_exporter
        self.blender_scene = blender_scene
        self.is_viewport_render = is_viewport_render
        
        self.properties = pyluxcore.Properties()

        self.outputCounter = 0
        self.material_id_mask_counter = 0
        self.by_material_id_counter = 0
        self.active_outputswitcher_channels = []


    def convert(self, film_width, film_height):
        if self.is_viewport_render:
            self.__convert_realtime_settings()
        else:
            # Config for final render
            self.__convert_filter()
            self.__convert_sampler()

        self.__convert_engine()
        self.__convert_seed()
        self.__convert_halt_conditions()
        self.__convert_compute_settings()
        self.__convert_film_size(film_width, film_height)
        self.__convert_accelerator()
        self.__convert_all_channels()
        self.__convert_epsilon()
        self.__convert_custom_props()

        return self.properties


    def convert_channel(self, channelName, id=-1, lightgroup_name=''):
        """
        Sets configuration properties for PBRTv3Core AOV output
        """
        if channelName in self.luxcore_exporter.passes_cache:
            return
        else:
            self.luxcore_exporter.passes_cache.add(channelName)

        # the OpenCL engines only support 1 MATERIAL_ID_MASK, 1 BY_MATERIAL_ID channel and 8 RADIANCE_GROUP channels
        engine = self.get_engine()
        is_ocl_engine = engine.endswith('OCL')

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
            if not is_lightgroup_opencl_compatible(self.luxcore_exporter, id):
                # don't create the output channel
                print('WARNING: OpenCL engines support a maximum of 8 lightgroups! Skipping this lightgroup (ID: %d)'
                       % id)
                return

        self.outputCounter += 1

        # list of channels that don't use an HDR format
        LDR_channels = ['RGB_TONEMAPPED', 'RGBA_TONEMAPPED', 'ALPHA', 'MATERIAL_ID', 'OBJECT_ID', 'DIRECT_SHADOW_MASK',
                        'INDIRECT_SHADOW_MASK', 'MATERIAL_ID_MASK']

        # channel type (e.g. 'film.outputs.1.type')
        outputStringType = 'film.outputs.' + str(self.outputCounter) + '.type'
        self.properties.Set(pyluxcore.Property(outputStringType, [channelName]))

        # output filename (e.g. 'film.outputs.1.filename')
        suffix = ('.png' if (channelName in LDR_channels) else '.exr')
        outputStringFilename = 'film.outputs.' + str(self.outputCounter) + '.filename'

        filename = channelName + '_' + lightgroup_name
        if id != -1:
            filename += '_' + str(id)
        filename = get_output_filename(self.blender_scene) + '_' + filename + suffix

        output_path = efutil.filesystem_path(self.blender_scene.render.filepath)
        if not os.path.isdir(output_path):
            os.makedirs(output_path)

        path = os.path.join(output_path, filename)

        self.properties.Set(pyluxcore.Property(outputStringFilename, path))

        # output id
        if id != -1:
            outputStringId = 'film.outputs.' + str(self.outputCounter) + '.id'
            self.properties.Set(pyluxcore.Property(outputStringId, [id]))


    def get_engine(self):
        """
        Create the final renderengine string from the general type setting ('PATH', 'TILEPATH' etc.) and the device type
        :return: PBRTv3Core renderengine string ('PATHOCL', 'PATHCPU' etc.)
        """
        engine_settings = self.blender_scene.luxcore_enginesettings
        engine = engine_settings.renderengine_type
        device = engine_settings.device_preview if self.is_viewport_render else engine_settings.device
        # (BIDIR* engines don't have OpenCL versions)
        if engine in ['BIDIR', 'BIDIRVM']:
            device = 'CPU'

        #if engine == 'TILEPATH' and self.is_viewport_render and engine_settings.biaspath_use_path_in_viewport:
        #    engine = 'PATH'

        # Use realtime engines for viewport render (only CPU version for now because OCL version is unstable)
        if self.is_viewport_render and engine not in ['BIDIR', 'BIDIRVM'] and device == 'CPU':
            engine = 'RTPATH'

        # Set device type
        engine += device

        return engine


    def __convert_film_size(self, film_width, film_height):
        self.properties.Set(pyluxcore.Property('film.width', film_width))
        self.properties.Set(pyluxcore.Property('film.height', film_height))


    def __convert_seed(self):
        engine_settings = self.blender_scene.luxcore_enginesettings

        if engine_settings.use_animated_seed:
            # frame_current can be 0, but not negative, while PBRTv3Core seed can only be > 1
            seed = self.blender_scene.frame_current + 1
        else:
            seed = engine_settings.seed

        self.properties.Set(pyluxcore.Property('renderengine.seed', seed))


    def __convert_halt_conditions(self):
        engine_settings = self.blender_scene.luxcore_enginesettings

        if engine_settings.use_halt_noise:
            haltthreshold = engine_settings.halt_noise
            self.properties.Set(pyluxcore.Property('batch.haltthreshold', haltthreshold))
            # All other halt conditions are controlled in core/__init__.py and not set via luxcore properties

    
    def __convert_sampler(self):
        engine_settings = self.blender_scene.luxcore_enginesettings

        if self.get_engine() == 'RTPATHCPU':
            # RTPATHCPU needs a special sampler
            self.properties.Set(pyluxcore.Property('sampler.type', 'RTPATHCPUSAMPLER'))
        elif self.get_engine() in ('TILEPATHCPU', 'TILEPATHOCL', 'RTPATHOCL'):
            # (RT)TILEPATHOCL needs a special sampler
            self.properties.Set(pyluxcore.Property('sampler.type', 'TILEPATHSAMPLER'))
        else:
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
        # The optimal accelerator settings are chosen by PBRTv3Core automatically, so we let the user decide only
        # if instancing should be allowed or not
        engine_settings = self.blender_scene.luxcore_enginesettings
        self.properties.Set(pyluxcore.Property('accelerator.instances.enable', engine_settings.instancing))


    def __convert_engine(self):
        engine_settings = self.blender_scene.luxcore_enginesettings
        engine = self.get_engine()

        if self.blender_scene.camera:
            export_to_luxcoreui = self.blender_scene.luxcore_translatorsettings.export_type == 'luxcoreui'
            transparent_film = self.blender_scene.camera.data.pbrtv3_camera.luxcore_imagepipeline.transparent_film
            force_black_background = transparent_film and not export_to_luxcoreui
        else:
            force_black_background = False

        if self.blender_scene.luxcore_translatorsettings.export_type == 'luxcoreui' and not self.is_viewport_render:
            # efutil.export_path is set at the beginning of the render() function in core/__init__.py
            self.properties.Set(pyluxcore.Property('renderengine.type', 'FILESAVER'))
            self.properties.Set(pyluxcore.Property('filesaver.directory', efutil.export_path))
            self.properties.Set(pyluxcore.Property('filesaver.renderengine.type', engine))
        else:
            self.properties.Set(pyluxcore.Property('renderengine.type', engine))

        if engine_settings.use_clamping:
            radiance_clamp = engine_settings.biaspath_clamping_radiance_maxvalue
            pdf_clamp = engine_settings.biaspath_clamping_pdf_value
        else:
            radiance_clamp = 0
            pdf_clamp = 0

        if engine in ['TILEPATHCPU', 'TILEPATHOCL']:
            self.properties.Set(pyluxcore.Property('path.clamping.variance.maxvalue', radiance_clamp))
            self.properties.Set(pyluxcore.Property('path.clamping.pdf.value', pdf_clamp))

            self.properties.Set(pyluxcore.Property('tile.size', [engine_settings.tile_size]))
            self.properties.Set(pyluxcore.Property('tile.multipass.enable',
                                                 [engine_settings.tile_multipass_enable]))
            self.properties.Set(pyluxcore.Property('tile.multipass.convergencetest.threshold',
                                                 [engine_settings.tile_multipass_convergencetest_threshold]))

            if engine_settings.tile_multipass_use_threshold_reduction:
                noise_threshold_reduction = engine_settings.tile_multipass_convergencetest_threshold_reduction
            else:
                noise_threshold_reduction = 0

            # Transparent film enables using black bg
            self.properties.Set(pyluxcore.Property('tilepath.forceblackbackground.enable', force_black_background))

            self.properties.Set(pyluxcore.Property('tile.multipass.convergencetest.threshold.reduction',
                                                 [noise_threshold_reduction]))

            # Always use only 1 sample in viewport render to make it usable
            if self.is_viewport_render:
                aa_samples = diffuse_samples = glossy_samples = specular_samples = 1
            else:
                aa_samples = engine_settings.biaspath_sampling_aa_size
                diffuse_samples = engine_settings.biaspath_sampling_diffuse_size
                glossy_samples = engine_settings.biaspath_sampling_glossy_size
                specular_samples = engine_settings.biaspath_sampling_specular_size

            self.properties.Set(pyluxcore.Property('tilepath.sampling.aa.size', aa_samples))

            if engine == 'TILEPATHCPU':
                self.properties.Set(pyluxcore.Property('tilepath.sampling.diffuse.size', diffuse_samples))
                self.properties.Set(pyluxcore.Property('tilepath.sampling.glossy.size', glossy_samples))
                self.properties.Set(pyluxcore.Property('tilepath.sampling.specular.size', specular_samples))

            # Path depths, note that for non-specular paths +1 is added to the path depth.
            # For details see http://www.luxrender.net/forum/viewtopic.php?f=11&t=11101&start=390#p114959
            self.properties.Set(pyluxcore.Property('path.pathdepth.total',
                                                 [engine_settings.path_pathdepth_total + 1]))
            self.properties.Set(pyluxcore.Property('path.pathdepth.diffuse',
                                                 [engine_settings.path_pathdepth_diffuse + 1]))
            self.properties.Set(pyluxcore.Property('path.pathdepth.glossy',
                                                 [engine_settings.path_pathdepth_glossy + 1]))
            self.properties.Set(pyluxcore.Property('path.pathdepth.specular',
                                                 [engine_settings.path_pathdepth_specular]))
            self.properties.Set(pyluxcore.Property('path.lights.samplingstrategy.type',
                                                 [engine_settings.biaspath_lights_samplingstrategy_type]))
        elif engine in ['PATHCPU', 'PATHOCL', 'RTPATHCPU']:
            self.properties.Set(pyluxcore.Property('path.pathdepth.total',
                                                 [engine_settings.path_pathdepth_total + 1]))
            self.properties.Set(pyluxcore.Property('path.pathdepth.diffuse',
                                                 [engine_settings.path_pathdepth_diffuse + 1]))
            self.properties.Set(pyluxcore.Property('path.pathdepth.glossy',
                                                 [engine_settings.path_pathdepth_glossy + 1]))
            self.properties.Set(pyluxcore.Property('path.pathdepth.specular',
                                                 [engine_settings.path_pathdepth_specular]))

            self.properties.Set(pyluxcore.Property('path.clamping.variance.maxvalue', radiance_clamp))
            self.properties.Set(pyluxcore.Property('path.clamping.pdf.value', pdf_clamp))
            # Transparent film enables using black bg
            self.properties.Set(pyluxcore.Property('path.forceblackbackground.enable', force_black_background))
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

        # Light strategy
        self.properties.Set(pyluxcore.Property('lightstrategy.type', engine_settings.lightstrategy_type))
    
    
    def __convert_realtime_settings(self):
        engine_settings = self.blender_scene.luxcore_enginesettings

        if self.get_engine() == 'RTPATHCPU':
            # RTPATHCPU needs a special sampler
            self.properties.Set(pyluxcore.Property('sampler.type', 'RTPATHCPUSAMPLER'))
        elif self.get_engine() in ('TILEPATHOCL', 'RTPATHOCL'):
            # (RT)TILEPATHOCL needs a special sampler
            self.properties.Set(pyluxcore.Property('sampler.type', 'TILEPATHSAMPLER'))
        else:
            # Sampler settings (same as for final render)
            self.properties.Set(pyluxcore.Property('sampler.type', engine_settings.sampler_type))

        # Special filter settings optimized for realtime preview
        if engine_settings.device_preview == 'CPU':
            self.properties.Set(pyluxcore.Property('film.filter.type', 'BLACKMANHARRIS'))
            self.properties.Set(pyluxcore.Property('film.filter.width', 1.0))
        else:
            self.properties.Set(pyluxcore.Property('film.filter.type', 'NONE'))

        if engine_settings.use_opencl_always_enabled:
            # remember to have a whitespace character at the end of each line
            enabled_features = (
                'MATTE ROUGHMATTE MATTETRANSLUCENT ROUGHMATTETRANSLUCENT '
                'GLOSSY2 GLOSSYTRANSLUCENT '
                'GLASS ARCHGLASS ROUGHGLASS '
                'MIRROR METAL2 '
                'HOMOGENEOUS_VOL CLEAR_VOL '
                'IMAGEMAPS_BYTE_FORMAT IMAGEMAPS_HALF_FORMAT IMAGEMAPS_1xCHANNELS IMAGEMAPS_3xCHANNELS '
                'HAS_BUMPMAPS '
            )
            self.properties.Set(pyluxcore.Property('opencl.code.alwaysenabled', enabled_features))


    def __convert_compute_settings(self):
        engine_settings = self.blender_scene.luxcore_enginesettings

        # CPU settings
        if not engine_settings.auto_threads:
            self.properties.Set(pyluxcore.Property('native.threads.count', engine_settings.native_threads_count))

        # OpenCL settings
        if engine_settings.opencl_settings_type == 'SIMPLE':
            self.properties.Set(pyluxcore.Property('opencl.cpu.use', engine_settings.opencl_use_all_cpus))
            self.properties.Set(pyluxcore.Property('opencl.gpu.use', engine_settings.opencl_use_all_gpus))
            self.properties.Set(pyluxcore.Property('opencl.devices.select', ''))

        elif engine_settings.opencl_settings_type == 'ADVANCED':
            self.properties.Set(pyluxcore.Property('opencl.cpu.use', True))
            self.properties.Set(pyluxcore.Property('opencl.gpu.use', True))

            if len(engine_settings.luxcore_opencl_devices) > 0:
                dev_string = ''
                for dev_index in range(len(engine_settings.luxcore_opencl_devices)):
                    dev = engine_settings.luxcore_opencl_devices[dev_index]
                    dev_string += '1' if dev.opencl_device_enabled else '0'

                self.properties.Set(pyluxcore.Property('opencl.devices.select', dev_string))

        self.properties.Set(pyluxcore.Property('film.opencl.enable', engine_settings.film_use_opencl))

        kernelcache = engine_settings.kernelcache
        self.properties.Set(pyluxcore.Property('opencl.kernelcache', kernelcache))


    def __convert_epsilon(self):
        engine_settings = self.blender_scene.luxcore_enginesettings
        self.properties.Set(pyluxcore.Property('scene.epsilon.min', engine_settings.epsilon_min))
        self.properties.Set(pyluxcore.Property('scene.epsilon.max', engine_settings.epsilon_max))

    
    def __convert_custom_props(self):
        engine_settings = self.blender_scene.luxcore_enginesettings
        # Custom Properties
        if engine_settings.custom_properties:
            custom_params = engine_settings.custom_properties.replace(' ', '').replace(';', ' ').split('|')
            for prop in custom_params:
                prop = prop.split('=')
                self.properties.Set(pyluxcore.Property(prop[0], prop[1]))


    def __convert_all_channels(self):
        # Convert it so it can be saved to the correct filepath
        self.convert_channel('RGB_TONEMAPPED')

        if self.blender_scene.camera is None:
            return

        pbrtv3_camera = self.blender_scene.camera.data.pbrtv3_camera
        output_switcher_channel = pbrtv3_camera.luxcore_imagepipeline.output_switcher_pass
        channels = self.blender_scene.pbrtv3_channels

        convert_channels = channels.enable_aovs and (channels.import_into_blender or channels.saveToDisk)
        transparent_film = pbrtv3_camera.luxcore_imagepipeline.transparent_film

        if convert_channels:
            if channels.RGB:
                self.convert_channel('RGB')
            if channels.RGBA:
                self.convert_channel('RGBA')
            #if channels.RGB_TONEMAPPED:
            #    self.convert_channel('RGB_TONEMAPPED')
            if channels.RGBA_TONEMAPPED or transparent_film:
                self.convert_channel('RGBA_TONEMAPPED')
            if channels.ALPHA or transparent_film:
                self.convert_channel('ALPHA')
            if channels.DEPTH:
                self.convert_channel('DEPTH')
            if channels.POSITION:
                self.convert_channel('POSITION')
            if channels.GEOMETRY_NORMAL:
                self.convert_channel('GEOMETRY_NORMAL')
            if channels.SHADING_NORMAL:
                self.convert_channel('SHADING_NORMAL')
            if channels.MATERIAL_ID:
                self.convert_channel('MATERIAL_ID')
            if channels.OBJECT_ID:
                self.convert_channel('OBJECT_ID')
            if channels.DIRECT_DIFFUSE:
                self.convert_channel('DIRECT_DIFFUSE')
            if channels.DIRECT_GLOSSY:
                self.convert_channel('DIRECT_GLOSSY')
            if channels.EMISSION:
                self.convert_channel('EMISSION')
            if channels.INDIRECT_DIFFUSE:
                self.convert_channel('INDIRECT_DIFFUSE')
            if channels.INDIRECT_GLOSSY:
                self.convert_channel('INDIRECT_GLOSSY')
            if channels.INDIRECT_SPECULAR:
                self.convert_channel('INDIRECT_SPECULAR')
            if channels.DIRECT_SHADOW_MASK:
                self.convert_channel('DIRECT_SHADOW_MASK')
            if channels.INDIRECT_SHADOW_MASK:
                self.convert_channel('INDIRECT_SHADOW_MASK')
            if channels.UV:
                self.convert_channel('UV')
            if channels.RAYCOUNT:
                self.convert_channel('RAYCOUNT')
            if channels.IRRADIANCE:
                self.convert_channel('IRRADIANCE')
        elif transparent_film:
            # Make absolutely sure that these AOVs are enabled when using transparent film, otherwise Blender crashes
            # during the render!
            self.convert_channel('RGBA_TONEMAPPED')
            self.convert_channel('ALPHA')

        if output_switcher_channel != 'disabled':
            if output_switcher_channel not in self.active_outputswitcher_channels:
                self.active_outputswitcher_channels.append(output_switcher_channel)
                self.convert_channel(output_switcher_channel)


    def __convert_lightgroups(self):
        if not self.blender_scene.pbrtv3_lightgroups.ignore:
            for i in range(len(self.luxcore_exporter.lightgroup_cache)):
                self.convert_channel('RADIANCE_GROUP', i)

            for lg, id in self.luxcore_exporter.lightgroup_cache.get_lightgroup_id_pairs():
                self.convert_channel('RADIANCE_GROUP', id, lg)
