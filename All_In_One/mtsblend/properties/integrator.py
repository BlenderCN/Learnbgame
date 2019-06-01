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

from .. import MitsubaAddon
from ..extensions_framework import declarative_property_group
from ..extensions_framework.validate import Logic_OR as O


@MitsubaAddon.addon_register_class
class mitsuba_integrator(declarative_property_group):
    '''
    Storage class for Mitsuba Integrator settings.
    This class will be instantiated within a Blender scene
    object.
    '''

    ef_attach_to = ['Scene']

    controls = [
        'type',
        'shadingSamples',
        'rayLength',
        'emitterSamples',
        'bsdfSamples',
        'maxDepth',
        'rrDepth',
        'strictNormals',
        'lightImage',
        'sampleDirect',
        'directSamples',
        'glossySamples',
        'globalPhotons',
        'causticPhotons',
        'volumePhotons',
        'globalLookupRadius',
        'causticLookupRadius',
        'causticLookupSize',
        'granularityPM',
        'photonCount',
        'initialRadius',
        'alphaR',
        'luminanceSamples',
        'pLarge',
        'lambdaMP',
        'bidirectional',
        'twoStage',
        'bidirectionalMutation',
        'lensPerturbation',
        'causticPerturbation',
        'multiChainPerturbation',
        'manifoldPerturbation',
        'numChains',
        'maxChains',
        'chainLength',
        'granularityPT',
        'shadowMapResolution',
        'clamping',
        'hideEmitters',
    ]

    visibility = {
        'shadingSamples':           {'type': 'ao'},
        'rayLength':                {'type': 'ao'},
        'emitterSamples':           {'type': 'direct'},
        'bsdfSamples':              {'type': 'direct'},
        'maxDepth':                 {'type': O(['path', 'volpath_simple', 'volpath', 'bdpt', 'photonmapper',
                                        'ppm', 'sppm', 'pssmlt', 'mlt', 'erpt', 'ptracer', 'vpl'])},
        'rrDepth':                  {'type': O(['path', 'volpath_simple', 'volpath', 'bdpt', 'photonmapper',
                                        'ppm', 'sppm', 'pssmlt', 'erpt', 'ptracer'])},
        'strictNormals':            {'type': O(['direct', 'path', 'volpath_simple', 'volpath'])},
        'hideEmitters':             {'type': O(['direct', 'path', 'volpath_simple', 'volpath', 'photonmapper'])},
        'lightImage':               {'type': 'bdpt'},
        'sampleDirect':             {'type': 'bdpt'},
        'directSamples':            {'type': O(['photonmapper', 'pssmlt', 'mlt', 'erpt'])},
        'glossySamples':            {'type': 'photonmapper'},
        'globalPhotons':            {'type': 'photonmapper'},
        'causticPhotons':           {'type': 'photonmapper'},
        'volumePhotons':            {'type': 'photonmapper'},
        'globalLookupRadius':       {'type': 'photonmapper'},
        'causticLookupRadius':      {'type': 'photonmapper'},
        'causticLookupSize':        {'type': 'photonmapper'},
        'granularityPM':            {'type': O(['photonmapper', 'ppm', 'sppm'])},
        'photonCount':              {'type': O(['ppm', 'sppm'])},
        'initialRadius':            {'type': O(['ppm', 'sppm'])},
        'alphaR':                   {'type': O(['ppm', 'sppm'])},
        'luminanceSamples':         {'type': O(['pssmlt','mlt','erpt'])},
        'pLarge':                   {'type': 'pssmlt'},
        'lambdaMP':                 {'type': O(['mlt','erpt'])},
        'bidirectional':            {'type': 'pssmlt'},
        'twoStage':                 {'type': O(['pssmlt','mlt'])},
        'bidirectionalMutation':    {'type': O(['mlt','erpt'])},
        'lensPerturbation':         {'type': O(['mlt','erpt'])},
        'causticPerturbation':      {'type': O(['mlt','erpt'])},
        'multiChainPerturbation':   {'type': O(['mlt','erpt'])},
        'manifoldPerturbation':     {'type': O(['mlt','erpt'])},
        'numChains':                {'type': 'erpt'},
        'maxChains':                {'type': 'erpt'},
        'chainLength':              {'type': 'erpt'},
        'granularityPT':            {'type': 'ptracer'},
        'shadowMapResolution':      {'type': 'vpl'},
        'clamping':                 {'type': 'vpl'},
    }

    properties = [
        {
            'type': 'enum',
            'attr': 'type',
            'name': 'Type',
            'description': 'Specifies the type of integrator to use',
            'default': 'direct',
            'items': [
                ('vpl', 'Virtual Point Light', 'vpl'),
                ('ptracer', 'Adjoint Particle Tracer', 'ptracer'),
                ('erpt', 'Energy Redistribution PT', 'erpt'),
                ('mlt', 'Path Space MLT', 'mlt'),
                ('pssmlt', 'Primary Sample Space MLT', 'pssmlt'),
                ('sppm', 'Stochastic Progressive Photon Mapping', 'sppm'),
                ('ppm', 'Progressive Photon Mapping', 'ppm'),
                ('photonmapper', 'Photon Mapper', 'photonmapper'),
                ('bdpt', 'Bidirectional Path Tracer', 'path'),
                ('volpath', 'Extended Volumetric Path Tracer', 'volpath'),
                ('volpath_simple', 'Simple Volumetric Path Tracer', 'volpath_simple'),
                ('path', 'Path Tracer', 'path'),
                ('direct', 'Direct Illumination', 'direct'),
                ('ao', 'Ambient Occlusion', 'ao')
            ],
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'shadingSamples',
            'name': 'Shading Samples',
            'description': 'Set both Luminaire and BSDF at same time',
            'save_in_preset': True,
            'min': 1,
            'max': 512,
            'default': 1
        },
        {
            'type': 'float',
            'attr': 'rayLength',
            'name': 'Occlusion Ray Length',
            'description': 'World-space length of the ambient occlusion rays that will be cast (default: -1, i.e. Automatic).',
            'save_in_preset': True,
            'min': -1,
            'max': 10000,
            'default': -1
        },
        {
            'type': 'int',
            'attr': 'emitterSamples',
            'name': 'Emitter Samples',
            'description': 'Number of samples to take using the emitter sampling technique',
            'save_in_preset': True,
            'min': 1,
            'max': 512,
            'default': 1
        },
        {
            'type': 'int',
            'attr': 'bsdfSamples',
            'name': 'BSDF Samples',
            'description': 'Number of samples to take using the BSDF sampling technique',
            'save_in_preset': True,
            'min': 1,
            'max': 512,
            'default': 1
        },
        {
            'type': 'bool',
            'attr': 'strictNormals',
            'name': 'Strict Normals',
            'description': 'Be strict about potential inconsistencies involving shading normals?',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'hideEmitters',
            'name': 'Hide Emitters',
            'description': 'Hide environment and area emitters?',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'granularityPT',
            'name': 'Work unit granularity',
            'description': 'Granularity of the work units used in parallelizing the particle tracing task (default: 200K samples). Should be high enough so that sending and accumulating the partially exposed films is not the bottleneck.',
            'save_in_preset': True,
            'min': 1,
            'max': 10000000,
            'default': 200000
        },
        {
            'type': 'int',
            'attr': 'directSamples',
            'name': 'Direct Samples',
            'description': 'Direct Samples. Default 16.',
            'save_in_preset': True,
            'min': -1,
            'max': 512,
            'default': 16
        },
        {
            'type': 'int',
            'attr': 'glossySamples',
            'name': 'Glossy samples',
            'description': 'Number on glossy samples for direct illuminaiton',
            'save_in_preset': True,
            'min': 2,
            'max': 100,
            'default': 32
        },
        {
            'type': 'int',
            'attr': 'maxDepth',
            'name': 'Max. path depth',
            'description': 'Maximum path depth to be rendered. (-1=infinite) 1 corresponds to direct illumination, 2 is 1-bounce indirect illumination, etc.',
            'save_in_preset': True,
            'min': -1,
            'max': 100,
            'default': 24
        },
        {
            'type': 'int',
            'attr': 'globalPhotons',
            'name': 'Global photons',
            'description': 'Number of photons to collect for the global photon map',
            'save_in_preset': True,
            'min': 0,
            'max': 10000000,
            'default': 250000
        },
        {
            'type': 'int',
            'attr': 'causticPhotons',
            'name': 'Caustic photons',
            'description': 'Number of photons to collect for the caustic photon map',
            'save_in_preset': True,
            'min': 0,
            'max': 10000000,
            'default': 250000
        },
        {
            'type': 'int',
            'attr': 'volumePhotons',
            'name': 'Volume photons',
            'description': 'Number of photons to collect for the volume photon map',
            'save_in_preset': True,
            'min': 0,
            'max': 10000000,
            'default': 250000
        },
        {
            'type': 'int',
            'attr': 'causticLookupSize',
            'name': 'Caustic photon map lookup size',
            'description': 'Amount of photons to consider in a caustic photon map lookup',
            'save_in_preset': True,
            'min': 0,
            'max': 1000,
            'default': 120
        },
        {
            'type': 'int',
            'attr': 'granularityPM',
            'name': 'Work unit granularity',
            'description': 'Granularity of photon tracing work units (in shot particles, 0 => decide automatically)',
            'save_in_preset': True,
            'min': 0,
            'max': 1000,
            'default': 0
        },
        {
            'type': 'int',
            'attr': 'rrDepth',
            'name': 'Russian roulette starting depth',
            'description': 'Depth to start using russian roulette when tracing photons',
            'save_in_preset': True,
            'min': 0,
            'max': 100,
            'default': 10
        },
        {
            'type': 'bool',
            'attr': 'sampleDirect',
            'name': 'Use direct sampling methods',
            'description': 'Enable direct sampling strategies?',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'photonCount',
            'name': 'Photon Count',
            'description': 'Number of photons to be shot per iteration',
            'save_in_preset': True,
            'min': 0,
            'max': 10000000,
            'default': 250000
        },
        {
            'type': 'float',
            'attr': 'initialRadius',
            'name': 'Initial Radius',
            'description': 'Initial radius of gather points in world space units (0 => decide automatically)',
            'save_in_preset': True,
            'min': 0,
            'max': 100,
            'default': 0
        },
        {
            'type': 'float',
            'attr': 'alphaR',
            'name': 'Radius Alpha',
            'description': 'Radius reduction parameter alpha',
            'save_in_preset': True,
            'min': 0.0001,
            'max': 10,
            'default': 0.7
        },
        {
            'type': 'int',
            'attr': 'luminanceSamples',
            'name': 'Luminance samples',
            'description': 'Number of samples used to estimate the total luminance received by the camera\'s sensor.',
            'save_in_preset': True,
            'min': 10000,
            'max': 500000,
            'default': 100000
        },
        {
            'type': 'bool',
            'attr': 'lightImage',
            'name': 'Create light image',
            'description': 'Include sampling strategies that connect paths traced from emitters directly to the camera?',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'globalLookupRadius',
            'name': 'Lookup radius (global)',
            'description': 'Radius of lookups in the global photon map (relative to the scene size)',
            'save_in_preset': True,
            'min': 0.0001,
            'max': 10,
            'default': 0.05
        },
        {
            'type': 'float',
            'attr': 'causticLookupRadius',
            'name': 'Lookup radius (caustic)',
            'description': 'Radius of lookups in the caustic photon map (relative to the scene size)',
            'save_in_preset': True,
            'min': 0.0001,
            'max': 10,
            'default': 0.0125
        },
        {
            'type': 'bool',
            'attr': 'bidirectional',
            'name': 'Bidirectional',
            'description': 'If set to true, the MLT algorithm runs on top of a bidirectional path tracer with multiple importance sampling. Otherwise, the implementation reverts to a basic path tracer. Generally, the bidirectional path tracer should be noticably better, so it\'s best to this setting at its default.',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'bidirectionalMutation',
            'name': 'Bidirectional Mutation',
            'description': 'Selectively enable/disable the bidirectional mutation',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'lensPerturbation',
            'name': 'Lens perturbation',
            'description': 'Selectively enable/disable the lens perturbation',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'causticPerturbation',
            'name': 'Caustic perturbation',
            'description': 'Selectively enable/disable the caustic perturbation',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'multiChainPerturbation',
            'name': 'Multi-chain perturbation',
            'description': 'Selectively enable/disable the multi-chain perturbation',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'manifoldPerturbation',
            'name': 'Manifold perturbation',
            'description': 'Selectively enable/disable the manifold perturbation',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'twoStage',
            'name': 'Two-stage MLT',
            'description': 'This setting can be very useful to reduce noise in dark regions of the image: it activates two-stage MLT, where a nested MLT renderer first creates a tiny version of the output image. In a second pass, the full version is then rendered, while making use of information about the image-space luminance distribution found in the first pass. Two-stage MLT is very useful in making the noise characteristics more uniform over time image -- specifically, since MLT tends to get stuck in very bright regions at the cost of the remainder of the image.',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'pLarge',
            'name': 'Large step probability',
            'description': 'Probability of creating large mutations in the [Kelemen et. al] MLT variant. The default is 0.3. There is little need to change it.',
            'save_in_preset': True,
            'min': 0.01,
            'max': 1,
            'default': 0.3
        },
        {
            'type': 'float',
            'attr': 'lambdaMP',
            'name': 'Probability factor',
            'description': 'Manifold perturbation: probability factor ("lambda"). Default: 50',
            'save_in_preset': True,
            'min': 0.1,
            'max': 100,
            'default': 50
        },
        {
            'type': 'float',
            'attr': 'numChains',
            'name': 'Average number of chains',
            'description': 'Specifies the number of Markov Chains that, on average, are started per pixel. Default 1',
            'save_in_preset': True,
            'min': 0,
            'max': 100,
            'default': 1
        },
        {
            'type': 'int',
            'attr': 'maxChains',
            'name': 'Max. number of chains',
            'description': 'Specifies a limit for the number of chains that will be started at a pixel. \'0\' disables this option. Default 0',
            'save_in_preset': True,
            'min': 0,
            'max': 100,
            'default': 0
        },
        {
            'type': 'int',
            'attr': 'chainLength',
            'name': 'Mutations per chain',
            'description': 'Specifies the number of mutations to be performed in each Markov Chain. Default 100',
            'save_in_preset': True,
            'min': 1,
            'max': 500,
            'default': 100
        },
        {
            'type': 'int',
            'attr': 'shadowMapResolution',
            'name': 'Shadow map resolution',
            'description': 'Resolution of the shadow maps that are used to compute the point-to-point visibility.',
            'save_in_preset': True,
            'min': 1,
            'max': 4096,
            'default': 512
        },
        {
            'type': 'float',
            'attr': 'clamping',
            'name': 'Clamping',
            'description': 'Relaitve clamping factor between [0,1] that is used to control the rendering artifact.',
            'save_in_preset': True,
            'min': 0,
            'max': 1,
            'default': 0.1
        },
    ]

    def api_output(self):
        params = {}

        if self.type == 'ao':
            params = {
                'shadingSamples': self.shadingSamples,
                'rayLength': self.rayLength,
            }

        elif self.type == 'direct':
            params = {
                'emitterSamples': self.emitterSamples,
                'bsdfSamples': self.bsdfSamples,
                'strictNormals': self.strictNormals,
                'hideEmitters': self.hideEmitters,
            }

        elif self.type in {'path', 'volpath_simple', 'volpath'}:
            params = {
                'maxDepth': self.maxDepth,
                'rrDepth': self.rrDepth,
                'strictNormals': self.strictNormals,
                'hideEmitters': self.hideEmitters,
            }

        elif self.type == 'bdpt':
            params = {
                'maxDepth': self.maxDepth,
                'lightImage': self.lightImage,
                'sampleDirect': self.sampleDirect,
                'rrDepth': self.rrDepth,
            }

        elif self.type == 'photonmapper':
            params = {
                'directSamples': self.directSamples,
                'glossySamples': self.glossySamples,
                'maxDepth': self.maxDepth,
                'globalPhotons': self.globalPhotons,
                'causticPhotons': self.causticPhotons,
                'volumePhotons': self.volumePhotons,
                'globalLookupRadius': self.globalLookupRadius,
                'causticLookupRadius': self.causticLookupRadius,
                'lookupSize': self.causticLookupSize,
                'granularity': self.granularityPM,
                'hideEmitters': self.hideEmitters,
                'rrDepth': self.rrDepth,
            }

        elif self.type in {'ppm', 'sppm'}:
            params = {
                'maxDepth': self.maxDepth,
                'photonCount': self.photonCount,
                'initialRadius': self.initialRadius,
                'alpha': self.alphaR,
                'granularity': self.granularityPM,
                'rrDepth': self.rrDepth,
            }

        elif self.type == 'pssmlt':
            params = {
                'bidirectional': self.bidirectional,
                'maxDepth': self.maxDepth,
                'directSamples': self.directSamples,
                'rrDepth': self.rrDepth,
                'luminanceSamples': self.luminanceSamples,
                'twoStage': self.twoStage,
                'pLarge': self.pLarge,
            }

        elif self.type == 'mlt':
            params = {
                'maxDepth': self.maxDepth,
                'directSamples': self.directSamples,
                'luminanceSamples': self.luminanceSamples,
                'twoStage': self.twoStage,
                'bidirectionalMutation': self.bidirectionalMutation,
                'lensPerturbation': self.lensPerturbation,
                'causticPerturbation': self.causticPerturbation,
                'multiChainPerturbation': self.multiChainPerturbation,
                'manifoldPerturbation': self.manifoldPerturbation,
                'lambda': self.lambdaMP,
            }

        elif self.type == 'erpt':
            params = {
                'maxDepth': self.maxDepth,
                'numChains': self.numChains,
                'maxChains': self.maxChains,
                'chainLength': self.chainLength,
                'directSamples': self.directSamples,
                'luminanceSamples': self.luminanceSamples,
                'bidirectionalMutation': self.bidirectionalMutation,
                'lensPerturbation': self.lensPerturbation,
                'causticPerturbation': self.causticPerturbation,
                'multiChainPerturbation': self.multiChainPerturbation,
                'manifoldPerturbation': self.manifoldPerturbation,
                'lambda': self.lambdaMP,
                'rrDepth': self.rrDepth,
            }

        elif self.type == 'ptracer':
            params = {
                'maxDepth': self.maxDepth,
                'rrDepth': self.rrDepth,
                'granularity': self.granularityPT,
            }

        elif self.type == 'vpl':
            params = {
                'maxDepth': self.maxDepth,
                'shadowMapResolution': self.shadowMapResolution,
                'clamping': self.clamping,
            }

        params['type'] = self.type

        if self.mitsuba_irrcache.use_irrcache:
            params = self.mitsuba_irrcache.api_output(params)

        if self.mitsuba_adaptive.use_adaptive:
            params = self.mitsuba_adaptive.api_output(params)

        return params


@MitsubaAddon.addon_register_class
class mitsuba_adaptive(declarative_property_group):
    ef_attach_to = ['mitsuba_integrator']

    controls = [
        'maxError',
        'pValue',
        'maxSampleFactor',
    ]

    properties = [
        {
            'type': 'bool',
            'attr': 'use_adaptive',
            'name': 'Use Adaptive Integrator',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'maxError',
            'name': 'Max Relative Error',
            'description': 'Maximum relative error threshold.',
            'save_in_preset': True,
            'min': 0,
            'max': 1,
            'default': 0.05
        },
        {
            'type': 'float',
            'attr': 'pValue',
            'name': 'Required P-value',
            'description': 'Required p-value to accept a sample.',
            'save_in_preset': True,
            'min': 0,
            'max': 1,
            'default': 0.05
        },
        {
            'type': 'int',
            'attr': 'maxSampleFactor',
            'name': 'Max Number of Samples',
            'description': 'Maximum number of samples to be generated relative to the number of configured pixel samples.',
            'save_in_preset': True,
            'min': 0,
            'max': 100,
            'default': 32
        }
    ]

    def api_output(self, integrator):

        if self.use_adaptive:
            adaptive = {
                'type': 'adaptive',
                'maxError': self.maxError,
                'pValue': self.pValue,
                'maxSampleFactor': self.maxSampleFactor,
                'integrator': integrator,
            }

            return adaptive

        else:
            return integrator


@MitsubaAddon.addon_register_class
class mitsuba_irrcache(declarative_property_group):
    ef_attach_to = ['mitsuba_integrator']

    controls = [
        'resolution',
        'quality',
        'gradients',
        'clampNeighbor',
        'clampScreen',
        'overture',
        'qualityAdjustment',
        'indirectOnly',
        'debug',
    ]

    properties = [
        {
            'type': 'bool',
            'attr': 'use_irrcache',
            'name': 'Use Irradiance Cache',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'clampNeighbor',
            'name': 'Neighbor clamping',
            'description': 'Should neighbor clamping [Krivanek et al.] be used? This propagates geometry information amongst close-by samples and generally leads to better sample placement. ',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'clampScreen',
            'name': 'Screen-space clamping',
            'description': 'If set to true, the influence region of samples will be clamped using the screen-space metric by [Tabellion et al.]? Turning this off may lead to excessive sample placement.',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'debug',
            'name': 'Show sample placement',
            'description': 'If set to true, sample locations are visually highlighted as they are generated. This won\'t show samples generated during a separate overture pass, so be sure to turn it off if you want to see all of the sample locations.',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'indirectOnly',
            'name': 'Show indirect illumination only',
            'description': 'Only show indirect ilumination? Useful for checking the interpolation quality',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'gradients',
            'name': 'Irradiance gradients',
            'description': 'Should irradiance gradients be used? Generally, this will significantly improve the interpolation quality.',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'overture',
            'name': 'Overture pass',
            'description': 'If set to true, the irradiance cache will be filled by a parallel overture pass before the main rendering process starts. This is strongly recommended.',
            'default': True,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'quality',
            'name': 'Quality',
            'description': 'Quality setting (\kappa in the [Tabellion et al.] paper). A value of 1 should be adequate in most cases.',
            'save_in_preset': True,
            'min': 0,
            'max': 100,
            'default': 1
        },
        {
            'type': 'float',
            'attr': 'qualityAdjustment',
            'name': 'Quality adjustment',
            'description': 'Multiplicative factor for the quality parameter following an overture pass. This can be used to interpolate amongst more samples, creating a visually smoother result. Must be 1 or less.',
            'save_in_preset': True,
            'min': 0,
            'max': 1,
            'default': 0.5
        },
        {
            'type': 'int',
            'attr': 'resolution',
            'name': 'Final Gather resolution',
            'description': 'Elevational resolution of the stratified final gather hemisphere. The azimuthal resolution is three times this value. Default: 14, which leads to 14x(3*14)=588 samples',
            'save_in_preset': True,
            'min': 0,
            'max': 20,
            'default': 14
        }
    ]

    def api_output(self, integrator):

        if self.use_irrcache:
            irrcache = {
                'type': 'irrcache',
                'clampNeighbor': self.clampNeighbor,
                'clampScreen': self.clampScreen,
                'debug': self.debug,
                'indirectOnly': self.indirectOnly,
                'gradients': self.gradients,
                'overture': self.overture,
                'quality': self.quality,
                'qualityAdjustment': self.qualityAdjustment,
                'resolution': self.resolution,
                'integrator': integrator,
            }

            return irrcache

        else:
            return integrator
