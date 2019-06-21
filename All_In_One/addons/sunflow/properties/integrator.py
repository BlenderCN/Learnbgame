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
from extensions_framework.validate import Logic_OR as LOR, Logic_AND as LAND


@SunflowAddon.addon_register_class
class sunflow_integrator(declarative_property_group):
    """ Defines the global illumination types of used with sunflow. There are 
    five types of global illumination supported with sunflow.
        1.Instant GI    
        2.Irradiance Caching (aka Final Gathering)    
        3.Path Tracing    
        4.Ambient Occlusion    
        5.Fake Ambient
    
    """

    ef_attach_to = ['Scene']
    controls = [
                'giOverride',
                'globalIllumination',
                # FINALGATHER               
                ['fgSpacingMin',
                 'fgSpacingMax'],
                ['fgSamples',
                 'fgTolerance'],
                'secondaryBounces',
                # FINALGATHER PHOTONS
                'globalMapping',
                'globalPhotons',
                ['globalPhotonsEstimate',
                'globalPhotonsRadius'],
                # IGI
                ['instantSets',
                'instantSamples'],
                ['instantPercentBias',
                'instantBiasSamples'],
                # PATHTRACING
                'pathTracingSamples',
                # AO
                ['occlusionSamples',
                'occlusionDistance'],
                'occlusionBrightText',
                'occlusionBright',
                'occlusionDarkText',
                'occlusionDark',
                # FAKEAO
                'fakeAOuppositionVector',
                'fakeAOSkyText',
                'fakeAOSky',
                'fakeAOGroundText',
                'fakeAOGround',
                ]
    
    visibility = {
                'giOverride'            :{ 'globalIllumination': LOR(['finalgathering', 'instantgi', 'pathtracing' , 'ambientocclusion', 'fakeambient'])},
                # FINALGATHER               
                'fgSpacingMin'          :{ 'globalIllumination':'finalgathering'},
                'fgSpacingMax'          :{ 'globalIllumination':'finalgathering'},
                'fgSamples'             :{ 'globalIllumination':'finalgathering'},
                'fgTolerance'           :{ 'globalIllumination':'finalgathering'},
                'secondaryBounces'      :{ 'globalIllumination':'finalgathering'},
                # FINALGATHER PHOTONS
                'globalMapping'         :{ 'globalIllumination':'finalgathering' , 'secondaryBounces':True},
                'globalPhotons'         :{ 'globalIllumination':'finalgathering' , 'secondaryBounces':True},
                'globalPhotonsEstimate' :{ 'globalIllumination':'finalgathering' , 'secondaryBounces':True},
                'globalPhotonsRadius'   :{ 'globalIllumination':'finalgathering' , 'secondaryBounces':True},
                # IGI
                'instantSets'           :{ 'globalIllumination':'instantgi'},
                'instantSamples'        :{ 'globalIllumination':'instantgi'},
                'instantPercentBias'    :{ 'globalIllumination':'instantgi'},
                'instantBiasSamples'    :{ 'globalIllumination':'instantgi'},
                # PATHTRACING
                'pathTracingSamples'    :{ 'globalIllumination':'pathtracing'},
                # AO
                'occlusionSamples'      :{ 'globalIllumination':'ambientocclusion'},
                'occlusionDistance'     :{ 'globalIllumination':'ambientocclusion'},
                'occlusionBrightText'   :{ 'globalIllumination':'ambientocclusion'},
                'occlusionBright'       :{ 'globalIllumination':'ambientocclusion'},
                'occlusionDarkText'     :{ 'globalIllumination':'ambientocclusion'},
                'occlusionDark'         :{ 'globalIllumination':'ambientocclusion'},
                # FAKEAO
                'fakeAOuppositionVector':{ 'globalIllumination':'fakeambient'},
                'fakeAOSkyText'         :{ 'globalIllumination':'fakeambient'},
                'fakeAOSky'             :{ 'globalIllumination':'fakeambient'},
                'fakeAOGroundText'      :{ 'globalIllumination':'fakeambient'},
                'fakeAOGround'          :{ 'globalIllumination':'fakeambient'}
                  }
    
    enabled = {}
    alert = {}
    
    properties = [    
        {
            'type': 'text',
            'attr': 'occlusionBrightText',
            'name': 'Bright colour:',
        },
        {
            'type': 'text',
            'attr': 'occlusionDarkText',
            'name': 'Dark colour:',
        },
        {
            'type': 'text',
            'attr': 'fakeAOSkyText',
            'name': 'Sky colour:',
        },
        {
            'type': 'text',
            'attr': 'fakeAOGroundText',
            'name': 'Ground colour:',
        },
        {
            'type': 'enum',
            'attr': 'globalIllumination',
            'name': 'Gi Method',
            'description': 'global illumination (Gi) types (default None).',
            'default': 'none',
            'items': [
                ('none', 'None', 'Gi not used'),
                ('finalgathering', 'Final Gathering', 'Final Gathering (Irradiance Caching)'),
                ('instantgi', 'Instant GI', 'Instant GI'),
                ('pathtracing', 'Path Tracing', ' Sunflow`s implementation only handles diffuse inter-reflection and will not produce any caustics. most accurate, but slowest, gi method.'),
                ('ambientocclusion', 'Ambient Occlusion', 'Ambient Occlusion'),
                ('fakeambient', 'Fake Ambient', 'Fake Ambient'),
            ],
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'giOverride',
            'name': 'Gi Override',
            'description': 'override the global photons and global illumination to render only these feature`s contribution to the scene (so you can fine tune your settings).',
            'default': 'fullrender',
            'items': [
                ('fullrender', 'Full Render', 'No Overriding'),
                ('gionly', 'Gi only', 'To view the gi in the scene'),
                ('photonsonly', 'Photons only', 'To view global photons you would us'),
            ],
            'expand' : True,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'fgSpacingMin',
            'name': 'Minimum',
            'description': 'minimum and maximum distance from the sampled point that will be used to look for other initial ray bounces. (default 1.0).',
            'min': 0.0,
            'max': 100.0,
            'default': 1.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'fgSpacingMax',
            'name': 'Maximum',
            'description': 'Minimum and maximum distance from the sampled point that will be used to look for other initial ray bounces. (default 1.0).',
            'min': 0.0,
            'max': 100.0,
            'default': 1.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'fgTolerance',
            'name': 'Tolerance',
            'description': 'The tolerance option indicates how much error you will allow in the calculation (default 0.01).',
            'min': 0.0,
            'max': 10.0,
            'default': 0.01,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'fgSamples',
            'name': 'Samples',
            'description': 'The number of samples (virtual rays) used to calculate the irradiance (default 256). ',
            'min': 0,
            'max':   8192,
            'default': 256,
            'save_in_preset': True
        },
        {
            'type': 'bool',
            'attr': 'secondaryBounces',
            'name': 'Use Global Photons',
            'description': 'Pre-compute local irradiance values at the photon positions.',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'globalMapping',
            'name': 'Mapping',
            'description': 'Defines how global photons mapped. (default grid).',
            'default': 'grid',
            'items': [
                ('grid', 'Grid', 'grid'),
                ('kd', 'Kd Tree', 'kd tree')
            ],
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'globalPhotons',
            'name': 'Photons',
            'description': 'The number of global photons emitted for irradiance (default 1000000). ',
            'min': 0,
            'max':   200000000,
            'default': 1000000,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'globalPhotonsEstimate',
            'name': 'Estimate',
            'description': 'The number of photons emitted (default 100). ',
            'min': 0,
            'max': 2000000,
            'default': 100,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'globalPhotonsRadius',
            'name': 'Radius',
            'description': 'Estimation sphere radius (default 0.5).',
            'save_in_preset': True,
            'min': 0.0,
            'max': 100.0,
            'default': 0.5
        },
        {
            'type': 'int',
            'attr': 'instantSets',
            'name': 'Sets',
            'description': 'This is the number of sets of virtual photons emitted (default 1).',
            'min': 0,
            'max': 2048,
            'default': 1,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'instantSamples',
            'name': 'Samples',
            'description': 'Number of virtual photons used per set (default 64).',
            'min': 0,
            'max': 2048,
            'default': 64,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'instantPercentBias',
            'name': 'Percentage Bias',
            'description': 'Estimate of direct illumination, `b` value in percentage (default 1.0).',
            'min': 0.0,
            'max': 100.0,
            'default': 1.0,
            'slider': True,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'instantBiasSamples',
            'name': 'Bias Samples',
            'description': 'The amount of samples of bias-diverted rays (default 0).',
            'min': 0,
            'max': 2048,
            'default': 0,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'pathTracingSamples',
            'name': 'Samples',
            'description': ' Number of rays to throw.',
            'min': 0,
            'max': 2048,
            'default': 16,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'occlusionSamples',
            'name': 'Samples',
            'description': 'Number of rays to emit to do the AO calculation (default 16).',
            'min': 0,
            'max': 2048,
            'default': 16,
            'save_in_preset': True
        },
                  
        {
            'type': 'float',
            'attr': 'occlusionDistance',
            'name': 'Distance',
            'description': 'Maximum distance of the objects to taken into consideration for occlusion (default 3.0).',
            'min': 0.0,
            'max': 100.0,
            'default': 3.0,
            'slider': True,
            'save_in_preset': True
        },
             
        {
            'type': 'enum',
            'attr': 'occlusionBright',
            'name': 'Bright Color',
            'description': 'Assign Bright color from world properties Horizon -or- Zenith -or- Ambient Colors (default Ambient).',
            'default': 'ambient',
            'items': [
                ('horizon', 'Horizon', 'World Horizon Color'),
                ('zenith', 'Zenith', 'World Zenith Color'),
                ('ambient', 'Ambient', 'World Ambient Color'),
            ],
            'expand' : True,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'occlusionDark',
            'name': 'Dark Color',
            'description': 'Assign Dark color from world properties Horizon -or- Zenith -or- Ambient Colors (default Zenith).',
            'default': 'zenith',
            'items': [
                ('horizon', 'Horizon', 'World Horizon Color'),
                ('zenith', 'Zenith', 'World Zenith Color'),
                ('ambient', 'Ambient', 'World Ambient Color'),
            ],
            'expand' : True,
            'save_in_preset': True
        },
        {
            'type': 'string',
            'attr': 'upVectorEmpty',
            'name': 'upVectorEmpty',
            'description': 'Name of the Empty object which gives the up direction vector for fake ambient occlusion' ,
            'save_in_preset': True
        },
        {
            'type': 'prop_search',
            'attr': 'fakeAOuppositionVector',
            'name': 'Direction Vector Empty',
            'src': lambda s, c: s.scene,
            'src_attr': 'objects',
            'trg': lambda s, c: c.sunflow_integrator,
            'trg_attr': 'upVectorEmpty',
            'description': 'Position of this Empty with respect to origin will give the up direction vector for fake ambient occlusion (must be an EMPTY)' ,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'fakeAOSky',
            'name': 'Sky Color',
            'description': 'Assign Sky color from world properties Horizon -or- Zenith -or- Ambient Colors (default Zenith).',
            'default': 'zenith',
            'items': [
                ('horizon', 'Horizon', 'World Horizon Color'),
                ('zenith', 'Zenith', 'World Zenith Color'),
                ('ambient', 'Ambient', 'World Ambient Color'),
            ],
            'expand' : True,
            'save_in_preset': True
        },
        {
            'type': 'enum',
            'attr': 'fakeAOGround',
            'name': 'Ground Color',
            'description': 'Assign Ground color from world properties Horizon -or- Zenith -or- Ambient Colors (default Ambient).',
            'default': 'ambient',
            'items': [
                ('horizon', 'Horizon', 'World Horizon Color'),
                ('zenith', 'Zenith', 'World Zenith Color'),
                ('ambient', 'Ambient', 'World Ambient Color'),
            ],
            'expand' : True,
            'save_in_preset': True
        },
                  ]
