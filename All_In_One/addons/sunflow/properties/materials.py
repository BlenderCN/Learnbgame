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

import bpy, bl_ui

from .. import SunflowAddon
from .viewObjectColor import change_color
from extensions_framework import declarative_property_group
from extensions_framework.validate import Logic_Operator, Logic_OR as LOR


@SunflowAddon.addon_register_class
class sunflow_material(declarative_property_group):
    '''
    materials supported by sunflow renderer
    mesh light is also included as a material.
    '''
    ef_attach_to = ['Material']
    
    
    controls = [
            # TYPE
            'type',
            # CONST
            'diffuseColor',
            'constantEmit',
            'uberDiffBlend',
            # DIFF
            #--------------------------------------------------- 'diffuseColor',
            # PHON
            #--------------------------------------------------- 'diffuseColor',
            'specularColor',
            ['phongSamples',
            'phongSpecHardness'],
            # SHIN
            #--------------------------------------------------- 'diffuseColor',
            'shinyReflection',
            'shinyExponent',
            # GLAS
            'glassETA',
            #--------------------------------------------------- 'diffuseColor',
            'glassAbsDistance',
            'glassAbsColor',
            # MIRR
            'mirrorReflection',
            # WARD
            #--------------------------------------------------- 'diffuseColor',
            #-------------------------------------------------- 'specularColor',
            ['wardRoughX',
            'wardRoughY'],
            'wardSamples',
            # AO
            'ambientBright',
            'ambientDark',
            ['ambientSamples',
            'ambientDistance'],
            # UBER
            #--------------------------------------------------- 'diffuseColor',
            
            #-------------------------------------------------- 'specularColor',
            'uberSpecBlend',
            ['uberGlossy',
            'uberSamples'],
            # LIGHT
            #--------------------------------------------------- 'diffuseColor',
            'lightRadiance',
            'lightSamples',
            # JANI
            # 'janinoPath',
    ]
    
    visibility = {
           
        'diffuseColor'      :{ 'type': LOR(['constant' , 'diffuse' , 'phong' , 'shiny' , 'glass', 'ward' , 'uber' , 'light']) },
        'specularColor'     :{ 'type': LOR(['phong' , 'ward' , 'uber' ]) },
        # CONST    
        'constantEmit'      :{ 'type':'constant' },
        # DIFF
        # PHON
        
        'phongSamples'      :{ 'type':'phong' },
        'phongSpecHardness' :{ 'type':'phong' },
        # SHIN
        'shinyReflection'   :{ 'type':'shiny' },
        'shinyExponent'     :{ 'type':'shiny' },
        # GLAS
        'glassETA'          :{ 'type':'glass' },
        'glassAbsDistance'  :{ 'type':'glass' },
        'glassAbsColor'     :{ 'type':'glass' },
        # MIRR
        'mirrorReflection'  :{ 'type':'mirror' },
        # WARD
        'wardRoughX'        :{ 'type':'ward' },
        'wardRoughY'        :{ 'type':'ward' },
        'wardSamples'       :{ 'type':'ward' },
        # AO
        'ambientBright'     :{ 'type':'amb-occ' },
        'ambientDark'       :{ 'type':'amb-occ' },
        'ambientSamples'    :{ 'type':'amb-occ' },
        'ambientDistance'   :{ 'type':'amb-occ' },
        # UBER
        'uberDiffBlend'     :{ 'type':'uber' },
        'uberSpecBlend'     :{ 'type':'uber' },
        'uberGlossy'        :{ 'type':'uber' },
        'uberSamples'       :{ 'type':'uber' },
        # LIGHT
        'lightRadiance'     :{ 'type':'light' },
        'lightSamples'      :{ 'type':'light' },
        # JANI
        # 'janinoPath'        :{ 'type':'janino' },
                  }
    
    properties = [
        {
            'type': 'enum',
            'attr': 'type',
            'name': 'Material Type',
            'description': 'Specifes the type of sunflow material',
            'items': [
                ('constant', 'constant', 'surface variation wont be considered.'),
                ('diffuse', 'Diffuse', 'Plain diffuse shader.'),
                ('phong', 'Phong', 'Phong'),
                ('shiny', 'Shiny', 'Shiny'),
                ('glass', 'Glass', 'Glass'),
                ('mirror', 'Mirror', 'Mirror'),
                ('ward', 'Ward', 'Ward'),
                ('amb-occ', 'Ambient Occlusion', 'Ambient Occlusion'),
                ('uber', 'Uber', 'Diffuse ,Specular mix shader'),
                # ('janino', 'Janino', 'Java compile time shader'),
                ('light', 'Light', 'If applied to an object , that object will be considered as a mesh light.')
            ],
            'default': 'diffuse',
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'constantEmit',
            'name': 'Emit',
            'description': 'Over driving color value to get color bleed in path tracing (default 1.0). ',
            'min': 1.0,
            'max': 10.0,
            'default': 1.0,
            'update'    : change_color,
            'slider': True,
            'save_in_preset': True
        },
                  
        {
            'type'      : 'float_vector',
            'subtype'   : 'COLOR',
            'attr'      : 'diffuseColor',
            'name'      : 'Diffuse',
            'description': 'Diffuse color.',
            'default'   : (0.8, 0.8, 0.8),
            'min'       : 0.0,
            'max'       : 1.0,
            'update'    : change_color,
            'save_in_preset': True
        },
        {
            'type'      : 'float_vector',
            'subtype'   : 'COLOR',
            'attr'      : 'specularColor',
            'name'      : 'Specular',
            'description': 'Specular color value.',
            'default'   : (0.8, 0.8, 0.8),
            'min'       : 0.0,
            'max'       : 1.0,
            'update'    : change_color,
            'save_in_preset': True
        },
        {
            'type'      : 'float_vector',
            'subtype'   : 'COLOR',
            'attr'      : 'glassAbsColor',
            'name'      : 'Absorption Color',
            'description': 'The color which is most attenuated inside the glass.',
            'default'   : (0.8, 0.8, 0.8),
            'min'       : 0.0,
            'max'       : 1.0,
            'save_in_preset': True
        },
                  
        {
            'type'      : 'float_vector',
            'subtype'   : 'COLOR',
            'attr'      : 'mirrorReflection',
            'name'      : 'Reflection Strength',
            'description': 'Reflection strength.',
            'default'   : (0.8, 0.8, 0.8),
            'min'       : 0.0,
            'max'       : 1.0,
            'save_in_preset': True
        },
        {
            'type'      : 'float_vector',
            'subtype'   : 'COLOR',
            'attr'      : 'ambientBright',
            'name'      : 'Ambient Bright',
            'description': 'Ambient color.',
            'default'   : (0.8, 0.8, 0.8),
            'min'       : 0.0,
            'max'       : 1.0,
            'save_in_preset': True
        },
        {
            'type'      : 'float_vector',
            'subtype'   : 'COLOR',
            'attr'      : 'ambientDark',
            'name'      : 'Ambient Dark',
            'description': 'Ambient Dark color.',
            'default'   : (0.1, 0.1, 0.1),
            'min'       : 0.0,
            'max'       : 1.0,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'phongSamples',
            'name': 'Samples',
            'description': 'The number of samples used to calculate the irradiance (default 8). ',
            'min': 0,
            'max':   2048,
            'default' : 8 ,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'phongSpecHardness',
            'name': 'Hardness',
            'description': '"power" or hardness of the specularity (default 50). ',
            'min': 0,
            'max': 50000,
            'default': 50,
            'update'    : change_color,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'shinyReflection',
            'name': 'Reflection',
            'description': 'The reflection value of shiny shader (default 0.01).',
            'min': 0.0,
            'max': 1.0,
            'default': 0.01,
            'slider'    : True,
            'save_in_preset': True
            
            # math.pow(10,4*val)
        },
        {
            'type': 'bool',
            'attr': 'shinyExponent',
            'name': 'Exponent',
            'description': 'If set then the shiny reflection value is taken exponentially 0 means 1.0 and 1 means 10000.0(default False).',
            'default': False,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'glassETA',
            'name': 'ETA',
            'description': 'Glass IOR (default 1.33).',
            'min':  0.0,
            'max': 10.0,
            'default': 1.33,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'glassAbsDistance',
            'name': 'Absorption Distance',
            'description': 'Distance up to which light travels in a medium without attenuation (default 1.0).',
            'min': 0.0,
            'max': 100.0,
            'default': 1.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'wardRoughX',
            'name': 'Rough X',
            'description': 'Roughness in UV tangent directions (default 0.2).',
            'min': 0.0,
            'max': 1.0,
            'default': 0.2,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'wardRoughY',
            'name': 'Rough Y',
            'description': 'Roughness in UV tangent directions (default 0.2).',
            'min': 0.0,
            'max': 1.0,
            'default': 0.2,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'wardSamples',
            'name': 'Samples',
            'description': 'indirect glossy reflections (default 4). ',
            'min': 0,
            'max':   2048,
            'default' : 4 ,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'ambientSamples',
            'name': 'Samples',
            'description': 'Ambient Occlusion Samples (default 16). ',
            'min': 0,
            'max':   2048,
            'default' : 16 ,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'ambientDistance',
            'name': 'AO Distance',
            'description': 'Ambient Occlusion Distance (default 2.0).',
            'min': 0.0,
            'max': 1000.0,
            'default': 2.0,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'uberDiffBlend',
            'name': 'Diffuse blend',
            'description': 'Blending factor between diffuse colour and diffuse texture colour.(default 0.001).',
            'min': 0.0,
            'max': 1.0,
            'default': 0.001,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'uberSpecBlend',
            'name': 'Specular blend',
            'description': 'Blending factor between specular colour and specular texture colour.(default 0.001).',
            'min': 0.0,
            'max': 1.0,
            'default': 0.001,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'uberGlossy',
            'name': 'Glossyness',
            'description': 'A value of zero is shiny, and a value of 1 has no glossyness.(Logarthmic scale coversion is used; default 1.0).',
            'min': 0.0,
            'max': 1.0,
            'default': 1.0,
            'save_in_preset': True
            # if val==0: ret 0.0 else: math.pow(0.1,(5*(1.0-val)))
        },
        {
            'type': 'int',
            'attr': 'uberSamples',
            'name': 'Samples',
            'description': 'Uber Samples (default 4). ',
            'min': 0,
            'max':   2048,
            'default' : 4 ,
            'save_in_preset': True
        },
        {
            'type': 'float',
            'attr': 'lightRadiance',
            'name': 'Radiance',
            'description': 'Specifies the intensity of the light source',
            'default': 10.0,
            'min': 0.0,
            'soft_min': 1e-3,
            'max': 1e5,
            'soft_max': 1e5,
            'save_in_preset': True
        },
        {
            'type': 'int',
            'attr': 'lightSamples',
            'name': 'Samples',
            'description': 'Mesh light sampling (default 16). ',
            'min': 0,
            'max':   2048,
            'default' : 16 ,
            'save_in_preset': True
        },
        {
            'type': 'string',
            'subtype': 'FILE_PATH',
            'attr': 'janinoPath',
            'name': 'Path to Janino shader',
            'description': 'Path to a Janino shader defenition file'
        },
                                   
    ] 
    