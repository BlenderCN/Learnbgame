# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
# --------------------------------------------------------------------------
#
# Authors:
# David Bucciarelli
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

from ..extensions_framework import declarative_property_group
from ..extensions_framework.validate import Logic_OR as O, Logic_Operator as LO, Logic_AND as A

from .. import PBRTv3Addon


@PBRTv3Addon.addon_register_class
class luxcore_opencl_devices(declarative_property_group):
    """
    Storage class for available OpenCL devices
    """

    ef_attach_to = []  # not attached
    alert = {}

    controls = [  # opencl_device_enabled is drawn manually in the UI class
                  'label_opencl_device_enabled'
    ]

    properties = [
        {
            'type': 'bool',
            'attr': 'opencl_device_enabled',
            'name': 'Enabled',
            'description': 'Enable this OpenCL device',
            'default': True
        },
    ]

def detect_cpu_corecount():
    corecount = 4 # Fallback

    try:
        import multiprocessing
        corecount = multiprocessing.cpu_count()
    except NotImplementedError:
        pass
    finally:
        return corecount

@PBRTv3Addon.addon_register_class
class luxcore_enginesettings(declarative_property_group):
    """
    Storage class for PBRTv3Core engine settings.

    Labels are used to minimize visual noise of non-equal button widths:
    Instead of this
        Engine:         [ Bidir ]
        [x] Clamp   (    100    )

    We get this
        Engine:     [   Bidir   ]
        [x] Clamp   (    100    )
    """

    ef_attach_to = ['Scene']

    controls = [
        # BIDIR
        ['bidir_eyedepth', 'bidir_lightdepth'],
        # PATH
        'label_path_depth',
        'path_pathdepth_total',
        ['path_pathdepth_diffuse', 'path_pathdepth_glossy', 'path_pathdepth_specular'],
        # BIDIRVMCPU
        ['bidirvm_eyedepth', 'bidirvm_lightdepth'],
        'bidirvm_lightpath_count',
        ['bidirvm_startradius_scale', 'bidirvm_alpha'],
        # TILEPATH
        'label_sampling',
        'biaspath_sampling_aa_size',
        ['biaspath_sampling_diffuse_size', 'biaspath_sampling_glossy_size', 'biaspath_sampling_specular_size'],
        ['use_clamping', 'biaspath_clamping_radiance_maxvalue'],
        ['label_sampler_type', 'sampler_type'],
        ['label_biaspath_sampler_type', 'biaspath_sampler_type'],
        # Filter width
        ['label_filter_width', 'filter_width'],

        # Advanced settings
        'advanced',
        [0.498, 'label_seed', ['seed', 'use_animated_seed']],
        ['label_accelerator_type', 'instancing'],
        ['label_filter_type', 'filter_type'],
        ['label_biaspath_lights_samplingstrategy_type', 'biaspath_lights_samplingstrategy_type'],
        ['label_biaspath_lights_nearstart', 'biaspath_lights_nearstart'],
        ['label_lightstrategy_type', 'lightstrategy_type'],
        ['label_largesteprate', 'largesteprate'],
        ['label_maxconsecutivereject', 'maxconsecutivereject'],
        ['label_imagemutationrate', 'imagemutationrate'],
        ['epsilon_min', 'epsilon_max'],

        # Halt conditions
        'show_halt_conditions',
        #'label_halt_conditions',
        ['tile_multipass_enable', 'tile_multipass_convergencetest_threshold'],
        ['tile_multipass_use_threshold_reduction', 'tile_multipass_convergencetest_threshold_reduction'],
        ['use_halt_samples', 'halt_samples'],
        ['use_halt_time', 'halt_time'],
        ['use_halt_noise', 'halt_noise'],
        'label_halt_conditions_preview',
        ['use_halt_samples_preview', 'halt_samples_preview'],
        ['use_halt_time_preview', 'halt_time_preview'],
    ]

    visibility = {
        # BIDIR
        'bidir_eyedepth': {'renderengine_type': 'BIDIR'},
        'bidir_lightdepth': {'renderengine_type': 'BIDIR'},
        # (BIAS)PATH
        'label_path_depth': {'renderengine_type': O(['TILEPATH', 'PATH'])},
        'path_pathdepth_total': {'renderengine_type': O(['TILEPATH', 'PATH'])},
        'path_pathdepth_diffuse': {'renderengine_type': O(['TILEPATH', 'PATH'])},
        'path_pathdepth_glossy': {'renderengine_type': O(['TILEPATH', 'PATH'])},
        'path_pathdepth_specular': {'renderengine_type': O(['TILEPATH', 'PATH'])},
        # BIDIRVM
        'bidirvm_eyedepth': {'renderengine_type': 'BIDIRVM'},
        'bidirvm_lightdepth': {'renderengine_type': 'BIDIRVM'},
        'bidirvm_lightpath_count': {'advanced': True, 'renderengine_type': 'BIDIRVM'},
        'bidirvm_startradius_scale': {'advanced': True, 'renderengine_type': 'BIDIRVM'},
        'bidirvm_alpha': {'advanced': True, 'renderengine_type': 'BIDIRVM'},
        # TILEPATH sampling
        'label_sampling': {'renderengine_type': 'TILEPATH'},
        'biaspath_sampling_aa_size': {'renderengine_type': 'TILEPATH'},
        'biaspath_sampling_diffuse_size': A([{'device': 'CPU'}, {'renderengine_type': 'TILEPATH'}]),
        'biaspath_sampling_glossy_size': A([{'device': 'CPU'}, {'renderengine_type': 'TILEPATH'}]),
        'biaspath_sampling_specular_size': A([{'device': 'CPU'}, {'renderengine_type': 'TILEPATH'}]),
        # TILEPATH obscure features
        'label_biaspath_lights_samplingstrategy_type':  A([{'advanced': True}, {'renderengine_type': 'TILEPATH'}]),
        'biaspath_lights_samplingstrategy_type': A([{'advanced': True}, {'renderengine_type': 'TILEPATH'}]),
        'label_biaspath_lights_nearstart': A([{'advanced': True}, {'renderengine_type': 'TILEPATH'}]),
        'biaspath_lights_nearstart': A([{'advanced': True}, {'renderengine_type': 'TILEPATH'}]),
        # Clamping (all unidirectional path engines)
        'use_clamping': {'renderengine_type': O(['TILEPATH', 'PATH'])},
        'biaspath_clamping_radiance_maxvalue': {'renderengine_type': O(['TILEPATH', 'PATH'])},
        'spacer_pdf_clamping': A([{'advanced': True}, {'renderengine_type': O(['TILEPATH', 'PATH'])}]),
        'biaspath_clamping_pdf_value': A([{'advanced': True}, {'renderengine_type': O(['TILEPATH', 'PATH'])}]),
        # Sampler settings, show for all but TILEPATH
        'label_sampler_type': {'renderengine_type': O(['PATH', 'BIDIR', 'BIDIRVM'])},
        'sampler_type': {'renderengine_type': O(['PATH', 'BIDIR', 'BIDIRVM'])},
        'label_largesteprate': A([{'advanced': True}, {'sampler_type': 'METROPOLIS'},
            {'renderengine_type': O(['PATH', 'BIDIR', 'BIDIRVM'])}]),
        'largesteprate': A([{'advanced': True}, {'sampler_type': 'METROPOLIS'},
            {'renderengine_type': O(['PATH', 'BIDIR', 'BIDIRVM'])}]),
        'label_maxconsecutivereject': A([{'advanced': True}, {'sampler_type': 'METROPOLIS'},
            {'renderengine_type': O(['PATH', 'BIDIR', 'BIDIRVM'])}]),
        'maxconsecutivereject': A([{'advanced': True}, {'sampler_type': 'METROPOLIS'},
            {'renderengine_type': O(['PATH', 'BIDIR', 'BIDIRVM'])}]),
        'label_imagemutationrate': A([{'advanced': True}, {'sampler_type': 'METROPOLIS'},
            {'renderengine_type': O(['PATH', 'BIDIR', 'BIDIRVM'])}]),
        'imagemutationrate': A([{'advanced': True}, {'sampler_type': 'METROPOLIS'},
            {'renderengine_type': O(['PATH', 'BIDIR', 'BIDIRVM'])}]),
        # Fake sampler settings for TILEPATH
        'label_biaspath_sampler_type': {'renderengine_type': 'TILEPATH'},
        'biaspath_sampler_type': {'renderengine_type': 'TILEPATH'},
        # Filter settings
        'label_filter_type': {'advanced': True},
        'filter_type': {'advanced': True},
        # don't show filter width if NONE filter is selected
        'label_filter_width': {'filter_type': O(['BLACKMANHARRIS', 'MITCHELL', 'MITCHELL_SS', 'BOX', 'GAUSSIAN'])},
        'filter_width': {'filter_type': O(['BLACKMANHARRIS', 'MITCHELL', 'MITCHELL_SS', 'BOX', 'GAUSSIAN'])},
        # Accelerator settings
        'label_accelerator_type': {'advanced': True},
        'instancing': {'advanced': True},
        # Light strategy
        'label_lightstrategy_type': {'advanced': True},
        'lightstrategy_type': {'advanced': True},
        # Halt conditions
        'use_halt_samples': {'show_halt_conditions': True, 'renderengine_type': O(['PATH', 'BIDIR', 'BIDIRVM'])},
        'halt_samples': {'show_halt_conditions': True, 'renderengine_type': O(['PATH', 'BIDIR', 'BIDIRVM'])},
        'use_halt_time': {'show_halt_conditions': True},
        'halt_time': {'show_halt_conditions': True},
        'use_halt_noise': {'show_halt_conditions': True, 'renderengine_type': O(['PATH', 'BIDIR', 'BIDIRVM'])},
        'halt_noise': {'show_halt_conditions': True, 'renderengine_type': O(['PATH', 'BIDIR', 'BIDIRVM'])},
        'label_halt_conditions_preview': {'show_halt_conditions': True},
        'use_halt_samples_preview': {'show_halt_conditions': True},
        'halt_samples_preview': {'show_halt_conditions': True},
        'use_halt_time_preview': {'show_halt_conditions': True},
        'halt_time_preview': {'show_halt_conditions': True},
        # TILEPATH noise controls
        'tile_multipass_enable': {'show_halt_conditions': True, 'renderengine_type': 'TILEPATH'},
        'tile_multipass_convergencetest_threshold': {'show_halt_conditions': True, 'renderengine_type': 'TILEPATH'},
        'tile_multipass_use_threshold_reduction': {'show_halt_conditions': True, 'renderengine_type': 'TILEPATH'},
        'tile_multipass_convergencetest_threshold_reduction': {'show_halt_conditions': True, 'renderengine_type': 'TILEPATH'},
        # Seed (advanced option)
        'label_seed': {'advanced': True},
        'seed': {'advanced': True},
        'use_animated_seed': {'advanced': True},
        # Epsilon (advanced option)
        'epsilon_min': {'advanced': True},
        'epsilon_max': {'advanced': True},
    }

    alert = {}

    enabled = {
        # Clamping value
        'biaspath_clamping_radiance_maxvalue': {'use_clamping': True},
        'biaspath_clamping_pdf_value': {'use_clamping': True},
        # Halt Conditions
        'halt_samples': {'use_halt_samples': True},
        'halt_time': {'use_halt_time': True},
        'halt_noise': {'use_halt_noise': True},
        'halt_samples_preview': {'use_halt_samples_preview': True},
        'halt_time_preview': {'use_halt_time_preview': True},
        # TILEPATH noise multiplier
        'tile_multipass_convergencetest_threshold': {'tile_multipass_enable': True},
        'tile_multipass_use_threshold_reduction': {'tile_multipass_enable': True},
        'tile_multipass_convergencetest_threshold_reduction': {'tile_multipass_enable': True,
                                                               'tile_multipass_use_threshold_reduction': True},
    }

    properties = [
        {
            'type': 'bool',
            'attr': 'advanced',
            'name': 'Advanced Settings',
            'description': 'Show extra settings that rarely need to be changed',
            'default': False,
            'icon': 'TRIA_DOWN',
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'biaspath_show_sample_estimates',
            'name': 'Sample Estimates',
            'description': 'Show estimated sampling statistics',
            'default': False,
        },
        {
            'type': 'bool',
            'attr': 'biaspath_use_path_in_viewport',
            'name': 'Use Path in Viewport',
            'description': 'Use the Path renderengine instead of Biased Path for viewport rendering (Biased Path is '
                           'not well suited for interactive rendering due to the tiled rendering)',
            'default': False,
        },
        {
            'type': 'text',
            'attr': 'label_renderengine_type',
            'name': 'Engine:',
        },
        {
            'type': 'enum',
            'attr': 'renderengine_type',
            'name': '',
            'description': 'Rendering engine to use',
            'default': 'BIDIR',
            'items': [
                ('PATH', 'Path', 'Path tracer', '', 0),
                ('TILEPATH', 'Biased Path', 'Biased path tracer', '', 1),
                ('BIDIR', 'Bidir', 'Bidirectional path tracer', '', 2),
                ('BIDIRVM', 'BidirVM (Experimental)', 'Bidirectional path tracer with vertex merging. '
                 'Warning: Experimental! May use large amounts of RAM or crash!', 'ERROR', 3),
            ],
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'device',
            'name': 'Final Device',
            'description': 'Device',
            'default': 'CPU',
            'items': [
                ('CPU', 'CPU', 'Use CPU only rendering'),
                ('OCL', 'OpenCL', 'Use OpenCL to render on GPUs, CPUs or both (see "Compute Settings" panel for details)'),
            ],
            'expand': True,
            'save_in_preset': True
        },
        {
            # Fake device to show that only a CPU version of the engine exists
            'type': 'enum',
            'attr': 'device_cpu_only',
            'name': 'Final Device',
            'description': 'Device',
            'default': 'CPU',
            'items': [
                ('CPU', 'CPU', 'Use CPU only rendering'),
                ('OCL', 'OpenCL', 'Not supported by the selected renderengine'),
            ],
            'expand': True,
            'save_in_preset': True
        },
        {
            # Device that is used for viewport rendering
            'type': 'enum',
            'attr': 'device_preview',
            'name': 'Viewport Device',
            'description': 'CPU rendering has lower latency, GPU rendering is faster',
            'default': 'CPU',
            'items': [
                ('CPU', 'CPU', 'Use the CPU (slow rendering, fast updates)'),
                ('OCL', 'OpenCL', 'Use the graphics card via OpenCL (fast rendering, slow updates)'),
            ],
            'expand': True,
            'save_in_preset': True
        },
        {
            'type': 'string',
            'attr': 'custom_properties',
            'name': '',
            'description': 'PBRTv3Core custom properties (separated by \'|\', suggested only for advanced users)',
            'default': '',
            'save_in_preset': True
        },
        {   # BIDIR
            'type': 'int',
            'attr': 'bidir_eyedepth',
            'name': 'Max Eye Depth',
            'description': 'Max recursion depth for ray casting from eye',
            'default': 16,
            'min': 1,
            'max': 2048,
            'save_in_preset': True
        },  
        {
            'type': 'int',
            'attr': 'bidir_lightdepth',
            'name': 'Max Light Depth',
            'description': 'Max recursion depth for ray casting from light',
            'default': 16,
            'min': 1,
            'max': 2048,
            'save_in_preset': True
        },
        {   # (BIAS)PATH
            'type': 'text',
            'attr': 'label_path_depth',
            'name': 'Path Depths:',
        },
        {
            'type': 'int',
            'attr': 'path_pathdepth_total',
            'name': 'Max Total Depth',
            'description': 'Max recursion depth for ray casting from eye',
            'default': 8,
            'min': 1,
            'max': 2048,
            'save_in_preset': True
        },
        {   # (BIAS)PATH
            'type': 'int',
            'attr': 'path_pathdepth_diffuse',
            'name': 'Diffuse',
            'description': 'Max recursion depth for a diffuse path',
            'default': 8,
            'min': 0,
            'max': 2048,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'path_pathdepth_glossy',
            'name': 'Glossy',
            'description': 'Max recursion depth for a glossy path',
            'default': 8,
            'min': 0,
            'max': 2048,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'path_pathdepth_specular',
            'name': 'Specular',
            'description': 'Max recursion depth for a specular path',
            'default': 8,
            'min': 0,
            'max': 2048,
            'save_in_preset': True
        },
        {   # BIDIRVM
            'type': 'int',
            'attr': 'bidirvm_eyedepth',
            'name': 'Max Eye Depth',
            'description': 'Max recursion depth for ray casting from eye',
            'default': 16,
            'min': 1,
            'max': 2048,
            'save_in_preset': True
        },  
        {
            'type': 'int',
            'attr': 'bidirvm_lightdepth',
            'name': 'Max Light Depth',
            'description': 'Max recursion depth for ray casting from light',
            'default': 16,
            'min': 1,
            'max': 2048,
            'save_in_preset': True
        },  
        {   
            'type': 'int',
            'attr': 'bidirvm_lightpath_count',
            'name': 'Lightpath Count',
            'description': '',
            'default': 16000,
            'min': 1000,
            'max': 1000000,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'bidirvm_startradius_scale',
            'name': 'Startradius Scale',
            'description': '',
            'default': 0.003,
            'min': 0.0001,
            'max': 0.1,
            'precision': 4,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'bidirvm_alpha',
            'name': 'Alpha',
            'description': '',
            'default': 0.95,
            'min': 0.5,
            'max': 0.99,
            'save_in_preset': True
        },
        {   # TILEPATH
            'type': 'text',
            'name': 'Tiles:',
            'attr': 'label_tiles',
        },
        {
            'type': 'int',
            'attr': 'tile_size',
            'name': 'Tile size',
            'description': 'Tile width and height in pixels',
            'default': 32,
            'min': 8,
            'max': 2048,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'tile_multipass_enable',
            'name': 'Adaptive Rendering',
            'description': 'Continue rendering until the noise threshold is reached',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'tile_multipass_convergencetest_threshold',
            'name': 'Noise level',
            'description': 'Lower values mean less noise',
            'default': 0.05,
            'min': 0.000001,
            'soft_min': 0.02,
            'max': 0.9,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'tile_multipass_use_threshold_reduction',
            'name': 'Reduce Noise Level',
            'description': 'When the target noise level is reached, reduce it with the multiplier and continue \
rendering with the reduced noise level',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'tile_multipass_convergencetest_threshold_reduction',
            'name': 'Multiplier',
            'description': 'Multiply noise level with this value after all tiles have converged',
            'default': 0.5,
            'min': 0.001,
            'soft_min': 0.1,
            'max': 0.99,
            'soft_max': 0.9,
            'save_in_preset': True
        },
        {
            'type': 'text',
            'name': 'Sampling:',
            'attr': 'label_sampling',
        },
        {   # BISASPATH + PATH
            'type': 'int',
            'attr': 'biaspath_sampling_aa_size',
            'name': 'AA Samples',
            'description': 'Anti-aliasing samples',
            'default': 3,
            'min': 1,
            'max': 64,
            'save_in_preset': True
        },
        {   # BISASPATH + PATHHOCL
            'type': 'int',
            'attr': 'biaspath_sampling_diffuse_size',
            'name': 'Diffuse',
            'description': 'Diffuse material samples (e.g. matte)',
            'default': 2,
            'min': 1,
            'max': 64,
            'save_in_preset': True
        },
        {   # BISASPATH + PATHHOCL
            'type': 'int',
            'attr': 'biaspath_sampling_glossy_size',
            'name': 'Glossy',
            'description': 'Glossy material samples (e.g. glossy, metal)',
            'default': 2,
            'min': 1,
            'max': 64,
            'save_in_preset': True
        },
        {   # BISASPATH + PATHHOCL
            'type': 'int',
            'attr': 'biaspath_sampling_specular_size',
            'name': 'Specular',
            'description': 'Specular material samples (e.g. glass, mirror)',
            'default': 1,
            'min': 1,
            'max': 64,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'use_clamping',
            'name': 'Clamp Brightness',
            'description': '',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'biaspath_clamping_radiance_maxvalue',
            'name': 'Max Brightness',
            'description': 'Max acceptable radiance value for a sample (0.0 = disabled). Used to prevent fireflies',
            'default': 0.0,
            'min': 0.0,
            'save_in_preset': True
        },
        {
            'type': 'text',
            'attr': 'spacer_pdf_clamping',
            'name': '',
        },
        {
            'type': 'float',
            'attr': 'biaspath_clamping_pdf_value',
            'name': 'PDF clamping',
            'description': 'Max acceptable PDF (0.0 = disabled)',
            'default': 0.0,
            'min': 0.0,
            'max': 999.0,
            'save_in_preset': True
        },
        {
            'type': 'text',
            'attr': 'label_biaspath_lights_samplingstrategy_type',
            'name': 'Light Sampling:',
        },
        {
            'type': 'enum',
            'attr': 'biaspath_lights_samplingstrategy_type',
            'name': '',
            'description': 'How to sample multiple light sources',
            'default': 'ALL',
            'items': [
                ('ALL', 'ALL', 'ALL'),
                ('ONE', 'ONE', 'ONE'),
            ],
            'save_in_preset': True
        },
        {
            'type': 'text',
            'attr': 'label_biaspath_lights_nearstart',
            'name': 'Near Start:',
        },
        {
            'type': 'float',
            'attr': 'biaspath_lights_nearstart',
            'name': 'Distance',
            'description': 'How far, from the light source, must be a point to receive light',
            'default': 0.001,
            'min': 0.0,
            'max': 1000.0,
            'subtype': 'DISTANCE',
            'unit': 'LENGTH',
            'save_in_preset': True
        },  
        # Sampler settings
        {
            'type': 'text',
            'attr': 'label_sampler_type',
            'name': 'Sampler:',
        },
        {
            'type': 'enum',
            'attr': 'sampler_type',
            'name': '',
            'description': 'Pixel sampling algorithm to use',
            'default': 'METROPOLIS',
            'items': [
                ('METROPOLIS', 'Metropolis', 'Recommended for scenes with difficult lighting (caustics, indoors)'),
                ('SOBOL', 'Sobol', 'Recommended for scenes with simple lighting (outdoors, studio setups)'),
            ],
            'save_in_preset': True
        },
        {
            'type': 'text',
            'attr': 'label_largesteprate',
            'name': 'Large Mutation Probability:',
        },
        {
            'type': 'float',
            'attr': 'largesteprate',
            'name': '',
            'description': 'Probability of a completely random mutation rather than a guided one. Lower values \
increase sampler strength',
            'default': 0.4,
            'min': 0,
            'max': 1,
            'slider': True,
            'save_in_preset': True
        },
        {
            'type': 'text',
            'attr': 'label_maxconsecutivereject',
            'name': 'Max Consecutive Rejections:',
        },
        {
            'type': 'int',
            'attr': 'maxconsecutivereject',
            'name': '',
            'description': 'Maximum amount of samples in a particular area before moving on. Setting this too low \
may mute lamps and caustics',
            'default': 512,
            'min': 128,
            'max': 2048,
            'save_in_preset': True
        },
        {
            'type': 'text',
            'attr': 'label_imagemutationrate',
            'name': 'Image Mutation Rate:',
        },
        {
            'type': 'float',
            'attr': 'imagemutationrate',
            'name': '',
            'description': '',
            'default': 0.1,
            'min': 0,
            'max': 1,
            'slider': True,
            'save_in_preset': True
        },
        # Fake sampler to show to the user that TILEPATH sampler is fixed
        {
            'type': 'text',
            'attr': 'label_biaspath_sampler_type',
            'name': 'Sampler:',
        },
        {
            'type': 'enum',
            'attr': 'biaspath_sampler_type',
            'name': '',
            'description': 'Pixel sampling algorithm to use',
            'default': 'SOBOL',
            'items': [
                ('SOBOL', 'Stratified Sampler', 'Biased Path uses a fixed stratified sampler'),
            ],
            'save_in_preset': True
        },
        # Filter settings
        {
            'type': 'text',
            'attr': 'label_filter_type',
            'name': 'Filter Type:',
        },
        {
            'type': 'enum',
            'attr': 'filter_type',
            'name': '',
            'description': 'Pixel filter to use',
            'default': 'BLACKMANHARRIS',
            'items': [
                ('BLACKMANHARRIS', 'Blackman-Harris', 'Default, usually the best option'),
                ('MITCHELL_SS', 'Mitchell', 'Sharp, but can produce black ringing artifacts around bright pixels'),
                ('GAUSSIAN', 'Gaussian', 'Blurry'),
                ('NONE', 'None', 'Disable pixel filtering. Fastest setting when rendering on GPU')
            ],
            'save_in_preset': True
        },
        {
            'type': 'text',
            'attr': 'label_filter_width',
            'name': 'Filter Width:',
        },
        {
            'type': 'float',
            'attr': 'filter_width',
            'name': 'Pixels',
            'description': 'Filter width in pixels. Lower values result in a sharper image, higher values smooth out noise',
            'default': 1.5,
            'min': 0.5,
            'soft_min': 0.5,
            'max': 10.0,
            'soft_max': 2.5,
            'save_in_preset': True
        },
        # Accelerator settings
        {
            'type': 'text',
            'attr': 'label_accelerator_type',
            'name': 'Accelerator:',
        },
        {
            'type': 'bool',
            'attr': 'instancing',
            'name': 'Use Instancing',
            'description': 'Lower memory usage for instances (like particles), but also lower rendering speed',
            'default': True,
            'save_in_preset': True
        },
        # Light strategy
        {
            'type': 'text',
            'attr': 'label_lightstrategy_type',
            'name': 'Light Strategy:',
        },
        {
            'type': 'enum',
            'attr': 'lightstrategy_type',
            'name': '',
            'description': 'Light sampling strategy type',
            'default': 'LOG_POWER',
            'items': [
                ('LOG_POWER', 'Log Power', 'Sample lights according to their brightness, but weighting very bright '
                                           'lights not much more than dim lights (recommended when using environment '
                                           'lights (hemi/sky) plus few small light sources)'),
                ('POWER', 'Power', 'Sample lights according to their brightness (recommended when using very bright '
                                   'lights (e.g. sun) together with highpoly meshlights with more than about 10 tris)'),
                ('UNIFORM', 'Uniform', 'Sample all lights equally, not according to their brightness')
            ],
            'save_in_preset': True
        },
        # Kernel cache
        {
            'type': 'enum',
            'attr': 'kernelcache',
            'name': 'Kernel Cache',
            'description': 'Kernel cache mode',
            'default': 'PERSISTENT',
            'items': [
                ('PERSISTENT', 'Persistent', ''),
                ('VOLATILE', 'Volatile', ''),
                ('NONE', 'None', ''),
            ],
            'save_in_preset': True
        },
        # Compute settings
        {
            'type': 'text',
            'name': 'Compute settings:',
            'attr': 'label_compute_settings',
        },  
        # CPU settings
        {
            'type': 'bool',
            'attr': 'auto_threads',
            'name': 'Auto Threads',
            'description': 'Auto-detect the optimal number of CPU threads',
            'default': True,
        },
        {
            'type': 'int',
            'attr': 'native_threads_count',
            'name': 'Threads count',
            'description': 'Number of CPU threads used for the rendering',
            'default': detect_cpu_corecount(),
            'min': 1,
            'max': 512,
        },  
        # OpenCL settings
        {
            'type': 'collection',
            'ptype': luxcore_opencl_devices,
            'attr': 'luxcore_opencl_devices',
            'name': 'OpenCL Devices',
            'items': []
        },
        {
            'type': 'operator',
            'attr': 'op_opencl_device_list_update',
            'operator': 'luxrender.opencl_device_list_update',
            'text': 'Update OpenCL device list',
        },
        # Halt condition settings (halt time and halt spp)
        {
            'type': 'bool',
            'attr': 'show_halt_conditions',
            'name': 'Halt Conditions',
            'description': 'Show/hide halt conditions (settings will still be used even when hidden)',
            'default': False,
            'icon': 'TRIA_DOWN',
        },
        {
            'type': 'text',
            'name': 'Halt Conditions:',
            'attr': 'label_halt_conditions',
        },
        {
            'type': 'text',
            'name': 'Viewport Halt Conditions:',
            'attr': 'label_halt_conditions_preview',
        },
        {
            'type': 'bool',
            'attr': 'use_halt_samples',
            'name': 'Samples',
            'description': 'Rendering process will stop at specified amount of samples',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'halt_samples',
            'name': '',
            'description': 'Rendering process will stop at specified amount of samples',
            'default': 100,
            'min': 1,
            'soft_min': 5,
            'soft_max': 2000,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'use_halt_samples_preview',
            'name': 'Samples',
            'description': 'Rendering process will stop at specified amount of samples',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'halt_samples_preview',
            'name': '',
            'description': 'Viewport rendering process will stop at specified amount of samples',
            'default': 20,
            'min': 1,
            'soft_min': 5,
            'soft_max': 2000,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'use_halt_time',
            'name': 'Time',
            'description': 'Rendering process will stop after specified amount of seconds',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'halt_time',
            'name': '',
            'description': 'Rendering process will stop after specified amount of seconds',
            'default': 60,
            'min': 1,
            'soft_min': 5,
            'soft_max': 3600,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'use_halt_time_preview',
            'name': 'Time',
            'description': 'Viewport rendering process will stop after specified amount of seconds',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'halt_time_preview',
            'name': '',
            'description': 'Viewport rendering process will stop after specified amount of seconds',
            'default': 10,
            'min': 1,
            'soft_max': 120,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'use_halt_noise',
            'name': 'Noise',
            'description': 'Rendering process will stop when the specified noise level is reached',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'halt_noise',
            'name': '',
            'description': 'Rendering process will stop when the specified noise level is reached (lower = less noise)',
            'default': 0.0001,
            'min': 0.000001,
            'max': 0.9,
            'save_in_preset': True
        },
        # OpenCL settings (drawn manually in "Compute Settings" panel)
        {
            'type': 'enum',
            'attr': 'opencl_settings_type',
            'name': 'OpenCL Settings',
            'description': 'How to configure the OpenCL settings',
            'default': 'SIMPLE',
            'items': [
                ('SIMPLE', 'Simple', 'Simple settings that allow to use all CPUs/no CPUs and all GPUs/no GPUs'),
                ('ADVANCED', 'Advanced', 'Enable the OpenCL devices you want to use individually for each device'),
            ],
        },
        {
            'type': 'bool',
            'attr': 'opencl_use_all_cpus',
            'name': 'Use all CPUs',
            'description': 'Use all available CPUs',
            'default': False,
        },
        {
            'type': 'bool',
            'attr': 'opencl_use_all_gpus',
            'name': 'Use all GPUs',
            'description': 'Use all available graphics cards',
            'default': True,
        },
        {
            'type': 'bool',
            'attr': 'use_opencl_always_enabled',
            'name': 'Low Latency Viewport Kernel',
            'description': 'Always enable the most common materials and textures for viewport rendering (rendering is '
                           'slower, but less kernel recompilations are necessary)',
            'default': True,
        },
        {
            'type': 'bool',
            'attr': 'film_use_opencl',
            'name': 'OpenCL Imagepipeline',
            'description': 'Use OpenCL to accelerate tonemapping and other imagepipeline operations (both viewport '
                           'and final render)',
            'default': True,
        },
        # Seed
        {
            'type': 'text',
            'attr': 'label_seed',
            'name': 'Seed:',
        },
        {
            'type': 'int',
            'attr': 'seed',
            'name': '',
            'description': 'Seed for random number generation. Images rendered with the same seed will have the same '
                           'noise pattern',
            'default': 1,
            'min': 1,
        },
        {
            'type': 'bool',
            'attr': 'use_animated_seed',
            'name': '',
            'description': 'Use different seed values for different frames',
            'default': False,
            'icon': 'TIME',
            'toggle': True,
        },
        # Epsilon
        {
            'type': 'float',
            'attr': 'epsilon_min',
            'name': 'Min Epsilon',
            'description': 'User higher values when artifacts appear in large scenes',
            # Lux(Core) default is 10^-9, which causes dark specks in the world center
            'default': 10**-5,
            'soft_min': 10**-9,
            'soft_max': 0.1,
            'precision': 10000,
        },
        {
            'type': 'float',
            'attr': 'epsilon_max',
            'name': 'Max Epsilon',
            'description': '',
            'default': 0.1,
            'soft_min': 0.001,
            'soft_max': 100,
        },
    ]