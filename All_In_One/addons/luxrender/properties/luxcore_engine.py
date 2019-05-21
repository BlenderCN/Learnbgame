# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
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

from .. import LuxRenderAddon


@LuxRenderAddon.addon_register_class
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


@LuxRenderAddon.addon_register_class
class luxcore_enginesettings(declarative_property_group):
    """
    Storage class for LuxCore engine settings.
    """

    ef_attach_to = ['Scene']

    controls = [
        'advanced',
        'renderengine_type',
        'label_custom_properties',
        'custom_properties',
        # BIDIR
        ['bidir_eyedepth', 'bidir_lightdepth'],
        # PATH
        'path_maxdepth',
        # BIDIRVMCPU
        ['bidirvm_eyedepth', 'bidirvm_lightdepth'],
        'bidirvm_lightpath_count',
        ['bidirvm_startradius_scale', 'bidirvm_alpha'],
        # BIASPATH
        'label_sampling',
        'biaspath_sampling_aa_size',
        ['biaspath_sampling_diffuse_size', 'biaspath_sampling_glossy_size', 'biaspath_sampling_specular_size'],
        'label_path_depth',
        'biaspath_pathdepth_total',
        ['biaspath_pathdepth_diffuse', 'biaspath_pathdepth_glossy', 'biaspath_pathdepth_specular'],
        'label_clamping',
        'biaspath_clamping_radiance_maxvalue',
        'biaspath_clamping_pdf_value',
        'label_lights',
        'biaspath_lights_samplingstrategy_type',
        'biaspath_lights_nearstart',
        # Sampler settings (for all but BIASPATH)
        'sampler_type',
        'biaspath_sampler_type',
        'largesteprate',
        'maxconsecutivereject',
        'imagemutationrate',
        # Filter settings (for all but BIASPATH)
        'filter_type',
        'filter_width',
        # Accelerator settings
        'accelerator_type',
        'instancing',
        # Halt condition settings (halt time and halt spp)
        'label_halt',
        ['halt_samples', 'halt_time'],
        # BIASPATH specific halt condition
        'tile_multipass_enable',
        'tile_multipass_convergencetest_threshold',
        'tile_multipass_convergencetest_threshold_reduction',

    ]

    visibility = {
                    'label_custom_properties': {'advanced': True},
                    'custom_properties': {'advanced': True},
                    # BIDIR
                    'bidir_eyedepth': {'renderengine_type': 'BIDIRCPU'},
                    'bidir_lightdepth': {'renderengine_type': 'BIDIRCPU'},
                    # PATH
                    'path_maxdepth': {'renderengine_type': O(['PATHCPU', 'PATHOCL'])},
                    # BIDIRVM
                    'bidirvm_eyedepth': {'renderengine_type': 'BIDIRVMCPU'},
                    'bidirvm_lightdepth': {'renderengine_type': 'BIDIRVMCPU'},
                    'bidirvm_lightpath_count': {'advanced': True, 'renderengine_type': 'BIDIRVMCPU'},
                    'bidirvm_startradius_scale': {'advanced': True, 'renderengine_type': 'BIDIRVMCPU'}, 
                    'bidirvm_alpha': {'advanced': True, 'renderengine_type': 'BIDIRVMCPU'},
                    # BIASPATH
                    'tile_multipass_enable': {'renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])},
                    'tile_multipass_convergencetest_threshold':
                        {'tile_multipass_enable': True, 'renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])},
                    'tile_multipass_convergencetest_threshold_reduction':
                        {'tile_multipass_enable': True, 'renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])},
                    'label_sampling': {'renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])},
                    'biaspath_sampling_aa_size': {'renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])},
                    'biaspath_sampling_diffuse_size': {'renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])},
                    'biaspath_sampling_glossy_size': {'renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])},
                    'biaspath_sampling_specular_size': {'renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])},
                    'label_path_depth': {'renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])},
                    'biaspath_pathdepth_total': {'renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])},
                    'biaspath_pathdepth_diffuse': {'renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])},
                    'biaspath_pathdepth_glossy': {'renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])},
                    'biaspath_pathdepth_specular': {'renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])},
                    'label_clamping': {'renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])},
                    'biaspath_clamping_radiance_maxvalue': 
                    	{'renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL', 'PATHCPU', 'PATHOCL'])},
                    'biaspath_clamping_pdf_value': 
                    	A([{'advanced': True}, {'renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL', 'PATHCPU', 'PATHOCL'])}]),
                    'label_lights': 
                    	A([{'advanced': True}, {'renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])}]),
                    'biaspath_lights_samplingstrategy_type':
                        A([{'advanced': True}, {'renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])}]),
                    'biaspath_lights_nearstart': 
                    	A([{'advanced': True}, {'renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])}]),
                    # Sampler settings, show for all but BIASPATH
                    'sampler_type': {'renderengine_type': O(['PATHCPU', 'PATHOCL', 'BIDIRCPU', 'BIDIRVMCPU'])},
                    'largesteprate': A([{'advanced': True}, {'sampler_type': 'METROPOLIS'}, 
                    	{'renderengine_type': O(['PATHCPU', 'PATHOCL', 'BIDIRCPU', 'BIDIRVMCPU'])}]),
                    'maxconsecutivereject': A([{'advanced': True}, {'sampler_type': 'METROPOLIS'}, 
                    	{'renderengine_type': O(['PATHCPU', 'PATHOCL', 'BIDIRCPU', 'BIDIRVMCPU'])}]),
                    'imagemutationrate': A([{'advanced': True}, {'sampler_type': 'METROPOLIS'}, 
                    	{'renderengine_type': O(['PATHCPU', 'PATHOCL', 'BIDIRCPU', 'BIDIRVMCPU'])}]),
                    # Show "fake" sampler settings for BIASPATH so the user knows the other samplers are not supported
                    'biaspath_sampler_type': {'renderengine_type': O(['BIASPATHCPU', 'BIASPATHOCL'])},
                    # Filter settings
                    'filter_type': {'advanced': True},
                    # don't show filter width if NONE filter is selected
                    'filter_width': A([{'advanced': True},
                    	{'filter_type': O(['BLACKMANHARRIS', 'MITCHELL', 'MITCHELL_SS', 'BOX', 'GAUSSIAN'])}]),
                    # Accelerator settings
                    'accelerator_type': {'advanced': True},
                    'instancing': {'advanced': True},
    }

    alert = {}

    enabled = {
        # Fake settings for BIASPATH are always disabled
        'biaspath_sampler_type': {'renderengine_type': ''},
    }

    properties = [
        {
            'type': 'enum',
            'attr': 'renderengine_type',
            'name': 'Engine',
            'description': 'Rendering engine to use',
            'default': 'BIDIRCPU',
            'items': [
                ('PATHCPU', 'Path', 'Path tracer'),
                ('PATHOCL', 'Path OpenCL', 'Pure OpenCL path tracer'),
                ('BIASPATHCPU', 'Biased Path', 'Biased path tracer'),
                ('BIASPATHOCL', 'Biased Path OpenCL', 'Pure OpenCL biased path tracer'),
                ('BIDIRCPU', 'Bidir', 'Bidirectional path tracer'),
                ('BIDIRVMCPU', 'BidirVCM', 'Bidirectional path tracer with vertex merging'),
            ],
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'advanced',
            'name': 'Advanced Settings',
            'description': 'Configure advanced engine settings',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'text',
            'attr': 'label_custom_properties',
            'name': 'Custom properties:',
        },
        {
            'type': 'string',
            'attr': 'custom_properties',
            'name': '',
            'description': 'LuxCore custom properties (separated by \'|\', suggested only for advanced users)',
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
        {   # PATH
            'type': 'int',
            'attr': 'path_maxdepth',
            'name': 'Max. Depth',
            'description': 'Max recursion depth for ray casting from eye',
            'default': 8,
            'min': 1,
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
        {   # BIASPATH
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
            'name': 'Enable Multipass (Adaptive Rendering)',
            'description': 'Continue rendering until the noise threshold is reached',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'tile_multipass_convergencetest_threshold',
            'name': 'Noise level:',
            'description': 'Lower values mean less noise',
            'default': 0.04,
            'min': 0.001,
            'max': 0.9,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'tile_multipass_convergencetest_threshold_reduction',
            'name': 'Noise level reduction:',
            'description': 'Multiply noise level with this value after all tiles have converged and continue rendering (0.0 = disabled)',
            'default': 0.0,
            'min': 0.0,
            'max': 0.99,
            'save_in_preset': True
        },
        {
            'type': 'text',
            'name': 'Sampling:',
            'attr': 'label_sampling',
        },
        {
            'type': 'int',
            'attr': 'biaspath_sampling_aa_size',
            'name': 'AA',
            'description': 'Anti-aliasing samples',
            'default': 3,
            'min': 1,
            'max': 64,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'biaspath_sampling_diffuse_size',
            'name': 'Diffuse',
            'description': 'Diffuse material samples (e.g. matte)',
            'default': 2,
            'min': 1,
            'max': 64,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'biaspath_sampling_glossy_size',
            'name': 'Glossy',
            'description': 'Glossy material samples (e.g. glossy, metal)',
            'default': 2,
            'min': 1,
            'max': 64,
            'save_in_preset': True
        },
        {
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
            'type': 'text',
            'name': 'Path depths:',
            'attr': 'label_path_depth',
        },
        {
            'type': 'int',
            'attr': 'biaspath_pathdepth_total',
            'name': 'Max Total Depth',
            'description': 'Max recursion total depth for a path',
            'default': 10,
            'min': 1,
            'max': 2048,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'biaspath_pathdepth_diffuse',
            'name': 'Diffuse',
            'description': 'Max recursion depth for a diffuse path',
            'default': 3,
            'min': 0,
            'max': 2048,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'biaspath_pathdepth_glossy',
            'name': 'Glossy',
            'description': 'Max recursion depth for a glossy path',
            'default': 1,
            'min': 0,
            'max': 2048,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'biaspath_pathdepth_specular',
            'name': 'Specular',
            'description': 'Max recursion depth for a specular path',
            'default': 2,
            'min': 0,
            'max': 2048,
            'save_in_preset': True
        },
        {
            'type': 'text',
            'name': 'Clamping:',
            'attr': 'label_clamping',
        },
        {
            'type': 'float',
            'attr': 'biaspath_clamping_radiance_maxvalue',
            'name': 'Clamping',
            'description': 'Max acceptable radiance value for a sample (0.0 = disabled). Used to prevent fireflies',
            'default': 0.0,
            'min': 0.0,
            'max': 999999.0,
            'save_in_preset': True
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
            'name': 'Lights:',
            'attr': 'label_lights',
        },
        {
            'type': 'enum',
            'attr': 'biaspath_lights_samplingstrategy_type',
            'name': 'Sampling strategy',
            'description': 'How to sample multiple light sources',
            'default': 'ALL',
            'items': [
                ('ALL', 'ALL', 'ALL'),
                ('ONE', 'ONE', 'ONE'),
            ],
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'biaspath_lights_nearstart',
            'name': 'Near start',
            'description': 'How far, from the light source, must be a point to receive light',
            'default': 0.001,
            'min': 0.0,
            'max': 1000.0,
            'save_in_preset': True
        },  
        # Sampler settings
        {
            'type': 'enum',
            'attr': 'sampler_type',
            'name': 'Sampler',
            'description': 'Pixel sampling algorithm to use',
            'default': 'METROPOLIS',
            'items': [
                ('METROPOLIS', 'Metropolis', 'Recommended for scenes with difficult lighting (caustics, indoors)'),
                ('SOBOL', 'Sobol', 'Recommended for scenes with simple lighting (outdoors, studio setups)'),
                ('RANDOM', 'Random', 'Completely random sampler, not recommended')
            ],
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'largesteprate',
            'name': 'Large Mutation Probability',
            'description': 'Probability of a completely random mutation rather than a guided one. Lower values \
            increase sampler strength',
            'default': 0.4,
            'min': 0,
            'max': 1,
            'slider': True,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'maxconsecutivereject',
            'name': 'Max. Consecutive Rejections',
            'description': 'Maximum amount of samples in a particular area before moving on. Setting this too low \
            may mute lamps and caustics',
            'default': 512,
            'min': 128,
            'max': 2048,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'imagemutationrate',
            'name': 'Image Mutation Rate',
            'description': '',
            'default': 0.1,
            'min': 0,
            'max': 1,
            'slider': True,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'biaspath_sampler_type',
            'name': 'Sampler',
            'description': 'Pixel sampling algorithm to use',
            'default': 'SOBOL',
            'items': [
                ('SOBOL', 'Stratified Sampler', 'Fixed sampler for Biased Path')
            ],
            'save_in_preset': True
        },
        # Filter settings
        {
            'type': 'enum',
            'attr': 'filter_type',
            'name': 'Filter',
            'description': 'Pixel filter to use',
            'default': 'BLACKMANHARRIS',
            'items': [
                ('BLACKMANHARRIS', 'Blackman-Harris', 'default'),
                ('MITCHELL', 'Mitchell', 'can produce black ringing artifacts around bright pixels'),
                ('MITCHELL_SS', 'Mitchell_SS', ''),
                ('BOX', 'Box', ''),
                ('GAUSSIAN', 'Gaussian', ''),
                ('NONE', 'None', 'Disable pixel filtering. Fastest setting when rendering on GPU')
            ],
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'filter_width',
            'name': 'Filter Width',
            'description': 'Width of pixel filter curve. Higher values are smoother and more blurred',
            'default': 2.0,
            'min': 0.5,
            'soft_min': 0.5,
            'max': 10.0,
            'soft_max': 4.0,
            'save_in_preset': True
        },
        # Accelerator settings
        {
            'type': 'enum',
            'attr': 'accelerator_type',
            'name': 'Accelerator',
            'description': 'Accelerator to use',
            'default': 'AUTO',
            'items': [
                ('AUTO', 'Auto', 'Automatically choose the best accelerator for each device (strongly recommended!)'),
                ('BVH', 'BVH', 'Static BVH'),
                ('MBVH', 'MBVH', 'Dynamic BVH'),
                ('QBVH', 'QBVH', 'Static QBVH'),
                ('MQBVH', 'MQBVH', 'Dynamic QBVH'),
                ('EMBREE', 'Embree', 'Fastest build times and render speed. Supports only one substep for motion blur. Not supported for OpenCL engines')
            ],
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'instancing',
            'name': 'Use Instancing',
            'description': 'Lower memory usage for instances (like particles), but also lower rendering speed',
            'default': True,
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
            'type': 'int',
            'attr': 'native_threads_count',
            'name': 'Threads count',
            'description': 'Number of CPU threads used for the rendering (0 = auto)',
            'default': 0,
            'min': 0,
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
            'type': 'text',
            'attr': 'label_halt',
            'name': 'Halt Conditions:',
        },
        {
            'type': 'int',
            'attr': 'halt_samples',
            'name': 'Samples',
            'description': 'Rendering process will stop at specified amount of samples (0 = disabled)',
            'default': 0,
            'min': 0,
            'max': 1000000,
            'soft_max': 1000,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'halt_time',
            'name': 'Time',
            'description': 'Rendering process will stop after specified amount of seconds (0 = disabled)',
            'default': 0,
            'min': 0,
            'max': 500000,
            'soft_max': 3600,
            'save_in_preset': True
        },
    ]
