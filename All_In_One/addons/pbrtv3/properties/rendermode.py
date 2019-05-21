# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond, Jason Clarke
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

import bpy

from ..extensions_framework import declarative_property_group

from .. import PBRTv3Addon
from ..export import ParamSet
from ..extensions_framework.validate import Logic_OR as O

@PBRTv3Addon.addon_register_class
class pbrtv3_rendermode(declarative_property_group):
    """
    This class holds the renderingmode menu and renderer prefs. Surface integrators settings are
    in a seperate class, due to there being a hell of a lot of them
    """

    ef_attach_to = ['Scene']

    controls = [
        'rendermode',
        'luxcore_custom_properties',
        ['usegpus', 'usecpus'],
        'opencl_prefs',
        'opencl_platform_index',
        'configfile',
        'raybuffersize',
        'statebuffercount',
        'workgroupsize',
        'bvhstacksize',
        'kernelcache'
    ]

    visibility = {
        'luxcore_custom_properties': {'renderer': 'luxcore'},
        'opencl_prefs': {'rendermode': O(['hybridpath', 'hybridbidir', 'luxcorepathocl', 'luxcorebiaspathocl'])},
        'opencl_platform_index': {'renderer': 'hybrid'},
        'configfile': {'opencl_prefs': True, 'renderer': 'hybrid'},
        'raybuffersize': {'opencl_prefs': True, 'renderer': 'hybrid'},
        'statebuffercount': {'opencl_prefs': True, 'renderer': 'hybrid'},
        'workgroupsize': {'opencl_prefs': True,
                          'rendermode': O(['hybridpath', 'hybridbidir', 'luxcorepathocl', 'luxcorebiaspathocl'])},
        'bvhstacksize': {'opencl_prefs': True, 'renderer': 'hybrid'},
        'kernelcache': {'opencl_prefs': True, 'rendermode': O(['luxcorepathocl', 'luxcorebiaspathocl'])},
        'usegpus': {'rendermode': O(['hybridpath', 'hybridbidir', 'luxcorepathocl', 'luxcorebiaspathocl'])},
        'usecpus': {'rendermode': O(['luxcorepathocl', 'luxcorebiaspathocl'])},
    }

    # This function sets renderer and surface integrator according to rendermode setting
    def update_rendering_mode(self, context):
        if self.rendermode in ('luxcorepath', 'luxcorepathocl', 'luxcorebiaspath', 'luxcorebiaspathocl', 'hybridpath'):
            context.scene.pbrtv3_integrator.surfaceintegrator = 'path'
        elif self.rendermode in ('luxcorebidir', 'luxcorebidirvcm', 'hybridbidir'):
            context.scene.pbrtv3_integrator.surfaceintegrator = 'bidirectional'
        else:
            context.scene.pbrtv3_integrator.surfaceintegrator = self.rendermode

        if self.rendermode in ('hybridpath', 'hybridbidir'):
            self.renderer = 'hybrid'
        elif self.rendermode == 'sppm':
            self.renderer = 'sppm'
        elif self.rendermode in (
                'luxcorepath', 'luxcorepathocl', 'luxcorebiaspath', 'luxcorebiaspathocl', 'luxcorebidir',
                'luxcorebidirvcm'):
            self.renderer = 'luxcore'
        else:
            self.renderer = 'sampler'

    properties = [
        {
            'type': 'enum',
            'attr': 'rendermode',
            'name': 'Rendering Mode',
            'description': 'Renderer and surface integrator combination to use',
            'default': 'path',
            'items': [
                ('bidirectional', 'Bidirectional', 'Bidirectional path tracer'),
                ('path', 'Path', 'Simple (eye-only) Path tracer'),
                ('directlighting', 'Direct Lighting', 'Direct-light (Whitted) ray tracer'),
                ('distributedpath', 'Distributed Path',
                 'Distributed path tracer, similar to Cycles non-progressive integrator'),
                # ('igi', 'Instant Global Illumination', 'Instant global illumination renderer',),
                ('exphotonmap', 'Ex-Photon Map', 'Traditional photon mapping integrator'),
                ('sppm', 'SPPM (Experimental)', 'Stochastic progressive photon mapping integrator'),
                # ('hybridbidir', 'Hybrid Bidirectional', 'Experimental OpenCL-acclerated bidirectional path tracer'),
                ('hybridpath', 'Hybrid Path', 'OpenCL-accelerated simple (eye-only) path tracer'),
                ('luxcorepath', 'PBRTv3Core Path', 'Experimental path tracer'),
                ('luxcorepathocl', 'PBRTv3Core Path OpenCL', 'Experimental pure OpenCL path tracer'),
                ('luxcorebiaspath', 'PBRTv3Core Biased Path', 'Experimental biased path tracer'),
                ('luxcorebiaspathocl', 'PBRTv3Core Biased Path OpenCL', 'Experimental pure OpenCL biased path tracer'),
                ('luxcorebidir', 'PBRTv3Core Bidir', 'Experimental bidirectional integrator'),
                ('luxcorebidirvcm', 'PBRTv3Core BidirVCM', 'Experimental bidirectional/vertex merging integrator'),
            ],
            'update': update_rendering_mode,
            'save_in_preset': True
        },
        {
            'type': 'string',
            'attr': 'luxcore_custom_properties',
            'name': 'Custom properties',
            'description': 'PBRTv3Core custom properties (separated by \'|\', suggested only for advanced users)',
            'default': '',
            'save_in_preset': True
        },  # This parameter is fed to the "renderer' context, and holds the actual
        # renderer setting. The user does not interact with it directly, and it  # does not appear in the panels
        {
            'type': 'enum',
            'attr': 'renderer',
            'name': 'Renderer',
            'description': 'Renderer Type',
            'default': 'sampler',
            'items': [
                ('sampler', 'Sampler (traditional CPU)', 'sampler'),
                ('hybrid', 'Hybrid (CPU+GPU)', 'hybrid'),
                ('sppm', 'SPPM (CPU)', 'sppm'),
                ('luxcore', 'PBRTv3Core Renderer (GPU)', 'luxcore'),
            ],  # 'update': lambda s,c: check_renderer_settings(c),
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'opencl_prefs',
            'name': 'Show OpenCL Options',
            'description': 'Enable manual OpenCL configuration options',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'opencl_platform_index',
            'name': 'OpenCL Platform Index',
            'description': 'OpenCL Platform to target. Try increasing this value 1 at a time if PBRTv3 fails \
            to use your GPU. -1=all platforms',
            'default': 0,
            'min': -1,
            'soft_min': 0,
            'max': 16,
            'soft_max': 16,
            'save_in_preset': True
        },
        {
            'type': 'string',
            'subtype': 'FILE_PATH',
            'attr': 'configfile',
            'name': 'OpenCL Config File',
            'description': 'Path to a machine-specific OpenCL configuration file. The settings from the lxs (set \
            below) are used if this is not specified or found',
            'default': '',
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'raybuffersize',
            'name': 'Ray Buffer Size',
            'description': 'Size of ray "bundles" fed to OpenCL device',
            'default': 8192,
            'min': 1024,
            'soft_min': 1024,
            'max': 65536,
            'soft_max': 65536,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'statebuffercount',
            'name': 'State Buffer Count',
            'description': 'Numbers of ray buffers to maintain simultaneously',
            'default': 1,
            'min': 1,
            'soft_min': 1,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'workgroupsize',
            'name': 'OpenCL Work Group Size',
            'description': 'Size of OpenCL work group. Use 0 for auto',
            'default': 64,
            'min': 0,
            'soft_min': 0,
            'max': 1024,
            'soft_max': 1024,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'bvhstacksize',
            'name': 'BVH Stack Size',
            'description': 'Max depth of GPU BVH stack. Lower this if you get an out-of-resources error',
            'default': 32,
            'min': 16,
            'max': 64,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'kernelcache',
            'name': 'OpenCL Kernel Cache',
            'description': 'Select the type of OpenCL compilation kernel cache used (in order to reduce compilation \
            time)',
            'default': 'PERSISTENT',
            'items': [
                ('NONE', 'None', 'NONE'),
                ('VOLATILE', 'Volatile', 'VOLATILE'),
                ('PERSISTENT', 'Persistent', 'PERSISTENT'),
            ],
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'usegpus',
            'name': 'Use GPUs',
            'description': 'Target GPU devices in luxcore or hybrid',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'usecpus',
            'name': 'Use CPUs',
            'description': 'Target CPU devices in luxcore render',
            'default': True,
            'save_in_preset': True
        },
    ]

    def api_output(self):
        renderer_params = ParamSet()

        if self.opencl_prefs:
            engine_settings = bpy.context.scene.luxcore_enginesettings
            dev_string = ''
            if len(engine_settings.luxcore_opencl_devices) > 0:
                for dev_index in range(len(engine_settings.luxcore_opencl_devices)):
                    dev = engine_settings.luxcore_opencl_devices[dev_index]
                    dev_string += '1' if dev.opencl_device_enabled else '0'

        if self.renderer in ['hybrid']:
            renderer_params.add_bool('opencl.gpu.use', self.usegpus)

            if self.opencl_prefs:
                renderer_params.add_integer('opencl.platform.index', self.opencl_platform_index)
                renderer_params.add_string('configfile', self.configfile)
                renderer_params.add_integer('raybuffersize', self.raybuffersize)
                renderer_params.add_integer('statebuffercount', self.statebuffercount)
                renderer_params.add_integer('opencl.gpu.workgroup.size', self.workgroupsize)
                renderer_params.add_integer('accelerator.bvh.stacksize.max', self.bvhstacksize)
                renderer_params.add_string('opencl.devices.select', dev_string if '1' in dev_string else "") # blank

        if self.renderer in ['luxcore']:
            # PBRTv3CoreRenderer specific parameters
            luxcore_use_gpu = "opencl.gpu.use = 1" if self.usegpus else "opencl.gpu.use = 0"
            luxcore_use_cpu = "opencl.cpu.use = 1" if self.usecpus else "opencl.cpu.use = 0"
            luxcore_params = '" "'.join((luxcore_use_gpu, luxcore_use_cpu))

            if self.opencl_prefs:
                luxcore_gpu_workgroups = "opencl.gpu.workgroup.size = " + str(self.workgroupsize)
                luxcore_devices_select = "opencl.devices.select = " + dev_string if '1' in dev_string else "" # blank
                luxcore_params = '" "'.join(
                    (luxcore_params, luxcore_devices_select)) if luxcore_devices_select else luxcore_params
                luxcore_kernel_cache = "opencl.kernelcache = " + self.kernelcache
                luxcore_params = '" "'.join((luxcore_params, luxcore_gpu_workgroups, luxcore_kernel_cache))

            luxcore_renderengine_type = 'PATHCPU'

            if self.rendermode == 'luxcorepath':
                luxcore_renderengine_type = 'PATHCPU'
            elif self.rendermode == 'luxcorepathocl':
                luxcore_renderengine_type = 'PATHOCL'
            elif self.rendermode == 'luxcorebiaspath':
                luxcore_renderengine_type = 'TILEPATHCPU'
            elif self.rendermode == 'luxcorebiaspathocl':
                luxcore_renderengine_type = 'TILEPATHOCL'
            elif self.rendermode == 'luxcorebidir':
                luxcore_renderengine_type = 'BIDIRCPU'
            elif self.rendermode == 'luxcorebidirvcm':
                luxcore_renderengine_type = 'BIDIRVMCPU'

            luxcore_params = '" "'.join((luxcore_params, 'renderengine.type = ' + luxcore_renderengine_type))

            if self.rendermode in ['luxcorebiaspath', 'luxcorebiaspathocl']:
                luxcore_params = '" "'.join((luxcore_params, 'tile.multipass.enable = 1'))

            # Set native  threadcount when manually set
            if not bpy.context.scene.pbrtv3_engine.threads_auto:
                luxcore_native_threads = "native.threads.count = " +  str(bpy.context.scene.pbrtv3_engine.threads)
                luxcore_params = '" "'.join((luxcore_params, luxcore_native_threads))

            # Finally add custom properties
            luxcore_params = '" "'.join([luxcore_params] + self.luxcore_custom_properties.split("|"))
            renderer_params.add_string('config', luxcore_params)

        return self.renderer, renderer_params


@PBRTv3Addon.addon_register_class
class pbrtv3_halt(declarative_property_group):
    """
    Storage class for PBRTv3 Halt settings.
    """

    ef_attach_to = ['Scene']

    controls = [
        ['haltthreshold', 'convergencestep'],
        ['haltspp', 'halttime'],
    ]

    properties = [
        {
            'type': 'int',
            'attr': 'haltspp',
            'name': 'Halt Samples',
            'description': 'Halt the rendering at this number of samples/px or passes (0=disabled)',
            'default': 16,
            'min': 0,
            'soft_min': 0,
            'max': 65535,
            'soft_max': 10000,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'halttime',
            'name': 'Halt Time',
            'description': 'Halt the rendering at this number seconds (0=disabled)',
            'default': 0,
            'min': 0,
            'soft_min': 0,
            'max': 65535,
            'soft_max': 65535,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'haltthreshold',
            'name': 'Halt Threshold',
            'description': 'Target quality level (logarithmic % of pixels passing the convergence test)',
            'default': 0.0,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 10.0,
            'soft_max': 10.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'convergencestep',
            'name': 'Convergence Step',
            'description': 'Update steps of the convergence test',
            'default': 32.0,
            'min': 4.0,
            'soft_min': 4.0,
            'max': 512.0,
            'soft_max': 512.0,
            'step': 1600,
            'save_in_preset': True
        },
    ]
