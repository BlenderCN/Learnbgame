# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
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
# --------------------------------------------------------------------------
# Blender Version                     2.68
# Exporter Version                    0.0.4
# Created on                          26-Aug-2013
# Author                              NodeBench
# --------------------------------------------------------------------------

from .. import SunflowAddon

from extensions_framework import declarative_property_group
from extensions_framework import util as efutil


@SunflowAddon.addon_register_class
class sunflow_performance(declarative_property_group):
    """ 
    To tell sunflow how many CPU threads to use for rendering and 
    few other controls to enhance the performance of the renderer.  
    
    """

    ef_attach_to = ['Scene']
    # all controls are manually assigned to performance panel   
    controls = []                   
    visibility = {}
    enabled = {}
    alert = {}
    
    properties = [
        {
            'type': 'bool',
            'attr': 'useCacheObjects',
            'name': 'Cache Objects',
            'description': 'if set to True sunflow will not recalculate geometry on next render.',
            'default' : True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'useSmallMesh',
            'name': 'Small Mesh',
            'description': 'if set to True sunflow will load triangle meshes using triangles optimized for memory use.',
            'default' : True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'ipr',
            'name': 'IPR',
            'description': 'progressive rendering.',
            'default' : False,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'useRandom',
            'name': 'Random',
            'description': 'save render image using random number at end.',
            'default' : True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'threadHighPriority',
            'name': 'High Priority',
            'description': 'Set sunflow thread priority to high (default is low priority).',
            'default' : False,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'enableVerbosity',
            'name': 'Verbosity',
            'description': 'Set sunflow verbosity level to 4 (detailed) ( default is none). ',
            'default' : False,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'bucketSize',
            'name': 'Bucket Size',
            'description': 'Sunflow rendering bucket or tile size (default 64).',
            'save_in_preset': True,
            'min': 1,
            'max': 65536,
            'default': 64
        },
        {
            'type': 'enum',
            'attr': 'bucketOrder',
            'name': 'Bucket Order',
            'description': 'Specifies the type of bucket/tile order to use in sunflow (default is hilbert).',
            'default': 'hilbert',
            'items': [
                ('hilbert', 'Hilbert', 'hilbert'),
                # ('hilbertRev', 'Hilbert (Reverse)', 'hilbertRev'),
                ('spiral', 'Spiral', 'spiral'),
                # ('spiralRev', 'Spiral (Reverse)', 'spiralRev'),
                ('column', 'Column', 'column'),
                ('row', 'Row', 'row'),
                ('diagonal', 'Diagonal', 'diagonal'),
                ('random', 'Random', 'random')
            ],
            'save_in_preset': True
        },
                  ]


@SunflowAddon.addon_register_class
class sunflow_antialiasing(declarative_property_group):
    """ 
    Sunflow adaptively varies anti-alias sampling on a pixel range
    The variation is between the min and max range given in the settings.
    
    """
    ef_attach_to = ['Scene']   
    controls = [
                ['adaptiveAAMin', 'adaptiveAAMax'],
                ['jitterAA', 'samplesAA'],
                'imageFilter',
                ]                   
    visibility = {}
    enabled = {}
    alert = {}
    
    properties = [
        {
            'type': 'int',
            'attr': 'adaptiveAAMin',
            'name': 'Adaptive Min',
            'description': 'value of 0 corresponds to 1 sample per pixel. A value of -1 corresponds to (1 per 2x2 pixel block) (default 0) ',
            'min':-10,
            'max': 10,
            'default': 0,
            'save_in_preset': True
         },
        {
            'type': 'int',
            'attr': 'adaptiveAAMax',
            'name': 'Adaptive Max',
            'description': 'A value of 1 corresponds to 4 samples per pixel (2x2 subpixel grid) A value of 2 corresponds to 16 samples per pixel (4x4 subpixel grid)  (default 1) ',
            'min':-10,
            'max': 10,
            'default': 1,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'samplesAA',
            'name': 'Samples',
            'description': 'number of samples. directly affects DoF and camera/object motion blur. (default 4) ',
            'min': 0,
            'max': 1024,
            'default': 4,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'imageFilter',
            'name': 'Image Filter',
            'description': 'This will smooth out over-sampled images (default is hilbert).',
            'items': [
                ('box', 'Box', 'box (filter size = 1)'),
                ('triangle', 'Triangle', 'triangle (filter size = 2)'),
                ('gaussian', 'Gaussian', 'gaussian (filter size = 3)'),
                ('mitchell', 'Mitchell', 'mitchell (filter size = 4)'),
                ('catmull-rom', 'Catmull Rom', 'catmull-rom (filter size = 4)'),
                ('blackman-harris', 'Blackman Harris', 'blackman-harris (filter size = 4)'),
                ('sinc', 'Sinc', 'sinc (filter size = 4)'),
                ('bspline', 'Bspline', 'bspline (filter size = 4)'),
                ('lanczos', 'Lanczos', 'lanczos (filter size = 4)')
            ],
            'default': 'mitchell',
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'jitterAA',
            'name': 'Anti Aliasing Jitter',
            'description': ' Jitter moves the rays randomly a small amount to reduce aliasing that might still be present even when anti-aliasing is turned on. ( default is off). ',
            'default' : False,
            'save_in_preset': True
        },
        ]



@SunflowAddon.addon_register_class
class sunflow_tracing(declarative_property_group):
    """ 
    Tracing depth and caustics.
    
    """
    ef_attach_to = ['Scene']   

    controls = [
                [0.4, 'diffuseBouncesText', 'diffuseBounces'],
                [0.4, 'reflectionDepthText', 'reflectionDepth'],
                [0.4, 'refractionDepthText', 'refractionDepth'],
                'useCaustics',
                [0.4, 'causticPhotonsText', 'causticPhotons'],
                [0.4, 'estimationPhotonsText', 'estimationPhotons'],
                [0.4, 'estimationRadiusText', 'estimationRadius'],
                ]                   
    visibility = {
                  'causticPhotonsText'      : { 'useCaustics': True },
                  'causticPhotons'          : { 'useCaustics': True },
                  'estimationPhotonsText'   : { 'useCaustics': True },
                  'estimationPhotons'       : { 'useCaustics': True },
                  'estimationRadiusText'    : { 'useCaustics': True },
                  'estimationRadius'        : { 'useCaustics': True },
                  }
    enabled = {}
    alert = {}
    
    properties = [
        {
            'type': 'text',
            'attr': 'diffuseBouncesText',
            'name': 'Diffuse trace depth :',
         },
        {
            'type': 'int',
            'attr': 'diffuseBounces',
            'name': 'Bounces',
            'description': 'The maximum number of bounces that a diffuse ray can perform. A diffuse ray is used for indirect illumination such as color-bleeding (default 1) ',
            'min': 0,
            'max': 1000,
            'default': 1,
            'save_in_preset': True
         },
        {
            'type': 'text',
            'attr': 'reflectionDepthText',
            'name': 'Ray-traced recursion :',
         },
        {
            'type': 'int',
            'attr': 'reflectionDepth',
            'name': 'Depth',
            'description': 'Puts a maximum limit on ray-traced recursion (reflections of reflection of reflections...) (default 4) ',
            'min': 0,
            'max': 1000,
            'default': 4,
            'save_in_preset': True
         },
        {
            'type': 'text',
            'attr': 'refractionDepthText',
            'name': 'Refraction trace depth :',
         },
        {
            'type': 'int',
            'attr': 'refractionDepth',
            'name': 'Depth',
            'description': 'Number of refractions the ray can perform (default 4).',
            'min': 0,
            'max': 1000,
            'default': 4,
            'save_in_preset': True
         },
        {
            'type': 'bool',
            'attr': 'useCaustics',
            'name': 'Caustics',
            'description': 'Enable caustics in the scene',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'text',
            'attr': 'causticPhotonsText',
            'name': 'Caustic photons :'
         },
        {
            'type': 'int',
            'attr': 'causticPhotons',
            'name': 'Photons',
            'description': 'The maximum number of photons emitted (default 200000). ',
            'min': 0,
            'max':  200000000,
            'default': 200000,
            'save_in_preset': True
         },
        {
            'type': 'text',
            'attr': 'estimationPhotonsText',
            'name': 'Estimation photons :'
         },
        {
            'type': 'int',
            'attr': 'estimationPhotons',
            'name': 'Photons',
            'description': 'The maximum number of photons emitted (default 100). ',
            'min': 0,
            'max': 2000000,
            'default': 100,
            'save_in_preset': True
         },
        {
            'type': 'text',
            'attr': 'estimationRadiusText',
            'name': 'Estimation radius :'
         },
        {
            'type': 'float',
            'attr': 'estimationRadius',
            'name': 'Radius',
            'description': 'Estimation sphere radius (default 0.5).',
            'save_in_preset': True,
            'min': 0,
            'max': 100,
            'default': 0.5
         },

        ]
