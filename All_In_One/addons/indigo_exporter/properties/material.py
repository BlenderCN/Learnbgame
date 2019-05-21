import re, os, zipfile
from copy import deepcopy

import bpy        #@UnresolvedImport
import bl_ui
import xml.etree.cElementTree as ET

from ..extensions_framework import util as efutil
#from extensions_framework.ui import property_group_renderer
from ..extensions_framework.validate import Logic_OR as LOR, Logic_AND as LAND 

#from indigo import IndigoAddon
from .. core.util import getResourcesPath 
from .. export.materials.Diffuse    import DiffuseMaterial
from .. export.materials.Phong        import PhongMaterial
from .. export.materials.Coating    import CoatingMaterial
from .. export.materials.DoubleSidedThin    import DoubleSidedThinMaterial
from .. export.materials.Specular    import SpecularMaterial
from .. export.materials.Blend        import BlendMaterial
from .. export.materials.medium      import  medium_xml
from .. export.materials.External    import ExternalMaterial
from .. export.materials.Null    import NullMaterial
from .. export.materials.FastSSS    import FastSSSMaterial
# from .. export import ( indigo_log )

from .. import export
from . import register_properties_dict

PROPERTY_GROUP_USAGE = {
    'colour': {'diffuse', 'phong', 'fastsss'},
    'specular': {'specular'},
    'phong': {'phong'},
    'coating': {'coating'},
    'absorption': {'coating'},
    'absorption_layer': {'specular'},
    'medium': {},
    'doublesidedthin': {'doublesidedthin'},
    'transmittance': {'doublesidedthin'},
    'diffuse': {'diffuse'},
    'blended': {'blended'},
    'external': {'external'},
    'bumpmap': {'diffuse', 'phong', 'specular', 'coating', 'doublesidedthin', 'fastsss'},
    'normalmap': {'diffuse', 'phong', 'specular', 'coating', 'doublesidedthin', 'fastsss'},
    'displacement': {'diffuse', 'phong', 'specular', 'coating', 'doublesidedthin', 'fastsss'},
    'exponent': {'phong', 'specular'}, #legacy
    'roughness': {'phong', 'specular', 'fastsss'},
    'blendmap': {'blended'},
    'emission': {'diffuse', 'phong', 'specular', 'coating', 'doublesidedthin', 'null', 'fastsss'},
    'fresnel_scale': {'phong', 'fastsss'},
    'null': {'null'},
    'fastsss': {'fastsss'},
}

def build_material_features(PGU):
    mf = {}
    for k, v in PGU.items():
        for mat_type in v:
            if mat_type not in mf.keys():
                mf[mat_type] = set()
            mf[mat_type].add(k)
    return mf

# This is the inverse of PROPERTY_GROUP_USAGE
MATERIAL_FEATURES = build_material_features(PROPERTY_GROUP_USAGE)

class Spectrum(object):
    
    #channel_name = None
    #name = None
    #controls = None
    #visibility = None
    #properties = None
    
    def __init__(self, channel, **opts):
        self.channel_name = channel
        self.name = channel+'_SP'
        defaults = {
            'rgb':                False,
            'rgbgain':            False,
            'uniform':            False,
            'peak':                False,
            'blackbody':        False,
            'tabulated':        False,
            'master_colour':    False,
            'rgb_default':        (0.8,0.8,0.8),
        }
        defaults.update(opts)
        self.opts = defaults
        
        self.types = []
        if self.opts['rgb']:
            self.types.append( ('rgb', 'RGB', 'rgb') )
        if self.opts['uniform']:
            self.types.append( ('uniform', 'Uniform', 'uniform') )
        if self.opts['peak']:
            self.types.append( ('peak', 'Peak', 'peak') )
        if self.opts['blackbody']:
            self.types.append( ('blackbody', 'Black body', 'blackbody') )
        if self.opts['tabulated']:
            self.types.append( ('tabulated', 'Regular tabulated', 'tabulated') )
        
        self.properties = self.get_properties()
    
    def set_master_colour(self, s, c):
        '''
        This update callback will set the blender material colour to the value
        given in the indigo material panel via the property's update function.
        We can specify more than one property to be 'master_colour' so long as
        they are not both visible in the panel simultaneously.
        (for diffuse and phong we use the color_rgb property and for specular we
        use medium_basic_rgb. We could perhaps do the arithmetic for blend too)
        '''
        
        if self.opts['master_colour'] != False:
            if c.material.diffuse_color != getattr(s, self.name+'_rgb'):
                c.material.diffuse_color = getattr(s, self.name+'_rgb')
    
    def get_properties(self):
        p = [{
            'type': 'enum',
            'attr': self.name + '_type',
            'name': 'Colour Type',
            'description': 'Type',
            'default': self.types[0][0],
            'items': self.types
        },
        {
            'type': 'float_vector',
            'attr': self.name + '_rgb',
            'name': 'RGB Colour',
            'description': 'RGB Colour',
            'default': self.opts['rgb_default'],
            'min': 0.0,
            'soft_min': 0.0,
            'max': 1.0,
            'soft_max': 1.0,
            'subtype': 'COLOR',
            'precision': 5,
            'update': lambda s,c: self.set_master_colour(s, c)
        },
        {
            'type': 'float',
            'attr': self.name + '_uniform_val',
            'name': 'Value',
            'description': 'Value',
            'min': 0.0,
            'max': 1.0,
            'default': 1.0,
            'precision': 5,
        },
        {
            'type': 'int',
            'attr': self.name + '_uniform_exp',
            'name': 'Exponent',
            'description': 'Exponent',
            'min': -5,
            'max': 5,
            'default': 0
        },
        {
            'type': 'float',
            'attr': self.name + '_blackbody_temp',
            'name': 'Temperature',
            'description': 'Temperature',
            'min': 1000.0,
            'max': 10000.0,
            'default': 6500.0
        },
        {
            'type': 'float',
            'attr': self.name + '_blackbody_gain',
            'name': 'Gain',
            'description': 'Gain',
            'min': 0.0,
            'max': 1000000.0,
            'default': 1.0,
            'precision': 6,
        }]
        
        if self.opts['rgbgain']:
            p.append({
                'type': 'float',
                'attr': self.name + '_rgb_gain',
                'name': 'RGB Gain',
                'description': 'RGB Gain',
                'min': 0.0,
                'max': 1000000.0,
                'default': 1.0,
                'precision': 6,
            })
        
        return p
    
class Shader(object):
    
    #channel_name = None
    #name = None
    
    #controls = None
    #visibility = None
    #properties = None
    
    def __init__(self, channel, **opts):
        self.channel_name = channel
        self.name = channel+'_SH'
        defaults = { }
        defaults.update(opts)
        self.opts = defaults
        
        self.properties = self.get_properties()
    
    def get_properties(self):
        return [
            {
                'type': 'prop_search',
                'attr': self.name + '_sht',
                'name': 'Shader text',
                'src': lambda s,c: bpy.data,
                'src_attr': 'texts',
                'trg': lambda s,c: getattr(c, 'indigo_material_' + self.channel_name),
                'trg_attr': self.name + '_text',
            },
            {
                # this is a hidden attr that is fed by the UI list above
                'type': 'string',
                'attr': self.name + '_text',
                'name': '_shader_text_',
                'description': 'Shader text',
            },
        ]
        
class Texture(object):
    
    #channel_name = None
    #name = None
    #controls = None
    #visibility = None
    #properties = None
    
    def __init__(self, channel, **opts):
        self.channel_name = channel
        self.name = channel+'_TX'
        defaults = { }
        defaults.update(opts)
        self.opts = defaults
        
        self.properties = self.get_properties()
    
    def get_properties(self):
        return [
            {
                'type': 'prop_search',
                'attr': self.name + '_texture_chooser',
                'name': 'Texture',
                'description': 'Texture',
                'src': lambda s,c: s.material,
                'src_attr': 'texture_slots',
                'trg': lambda s, c: getattr(c, 'indigo_material_' + self.channel_name),
                'trg_attr': self.name + '_texture',
            },
            {
                # this is a hidden attr that is fed by the UI list above
                'type': 'string',
                'attr': self.name + '_texture',
                'name': 'Texture',
                'description': 'Texture',
            },
            {
                'type': 'bool',
                'attr': self.name+'_abc_from_tex',
                'name': 'Use texture A,B,C',
                'default': False
            },
            {
                'type': 'bool',
                'attr': self.name+'_smooth',
                'name': 'Smooth',
                'description': 'Smooth the texture by up-converting from 8bit to 16bit (for bumpmaps etc)',
                'default': False
            },
            {
                'type': 'float',
                'attr': self.name+'_A',
                'name': '(A) Brightness',
                'description': '(A) Brightness',
                'default': 0.0,
                'precision': 5,
            },
            {
                'type': 'float',
                'attr': self.name+'_B',
                'name': '(B) Scale',
                'description': '(B) Scale',
                'default': 1.0,
                'precision': 5,
                #'sub_type': 'DISTANCE',
                #'unit': 'LENGTH'
            },
            {
                'type': 'float',
                'attr': self.name+'_C',
                'name': '(C) Offset',
                'description': '(C) Offset',
                'default': 0.0,
                'precision': 5,
                #'sub_type': 'DISTANCE',
                #'unit': 'LENGTH'
            },
            {
                'type': 'prop_search',
                'attr': self.name+'_uvset_list',
                'name': 'UV Set',
                'description': 'UV Set',
                'src': lambda s, c: s.object.data,
                'src_attr': 'uv_textures',
                'trg': lambda s, c: getattr(c, 'indigo_material_%s'%self.channel_name),
                'trg_attr': self.name+'_uvset',
            },
            {
                # this is a hidden attr that is fed by the UI list above
                'type': 'string',
                'attr': self.name+'_uvset',
                'name': 'UV Set',
                'description': 'UV Set',
            },
        ]


@register_properties_dict
class Indigo_Texture_Properties(bpy.types.PropertyGroup):
    properties = [
        {
            'type': 'enum',
            'attr': 'image_ref',
            'name': 'Image Type',
            'items': [
                ('blender', 'Blender', 'Use blender image reference'),
                ('file', 'File', 'Use file reference')
            ],
            'expand': True
        },
        {
            'type': 'string',
            'attr': 'image',
            'name': 'Image'
        },
        {
            'type': 'prop_search',
            'attr': 'image_chooser',
            'name': 'Image',
            'description': 'Image',
            'src': lambda s, c: bpy.data,
            'src_attr': 'images',
            'trg': lambda s, c: getattr(c, 'indigo_texture'),
            'trg_attr': 'image',
        },
        {
            'type': 'string',
            'attr': 'path',
            'name': 'File',
            'description': 'File',
            'default': '',
            'subtype': 'FILE_PATH'
        },
        {
            'type': 'float',
            'attr': 'gamma',
            'name': 'Gamma',
            'description':'Gamma',
            'default': 2.2,
            'precision': 5,
        },
        {
            'type': 'float',
            'attr': 'A',
            'name': '(A) Brightness',
            'description': '(A) Brightness',
            'default': 0.0,
            'precision': 5,
        },
        {
            'type': 'float',
            'attr': 'B',
            'name': '(B) Scale',
            'description': '(B) Scale',
            'default': 1.0,
            'precision': 5,
            #'sub_type': 'DISTANCE',
            #'unit': 'LENGTH'
        },
        {
            'type': 'float',
            'attr': 'C',
            'name': '(C) Offset',
            'description': '(C) Offset',
            'default': 0.0,
            'precision': 5,
            #'sub_type': 'DISTANCE',
            #'unit': 'LENGTH'
        }
    ]
    
    
class MaterialChannel(object):
    
    def __init__(self, name, **opts):
        
        self.name = name
        
        defaults = {
            'spectrum': False,
            #'constant': False,
            'texture': False,
            'shader': False,
            'switch': False,
            'spectrum_types': { 'rgb': True },
            'label': None,
            'master_colour': False,
            #'constant_settings': {
            #    'min': 0.0,
            #    'max': 1.0,
            #    'default': 0.666,
            #},
        }
        defaults.update(opts)
        self.opts = defaults
        self.types = []
        
        if self.opts['spectrum']:
            self.types.append( ('spectrum', 'Colour', 'spectrum') )
            if self.opts['master_colour']: self.opts['spectrum_types'].update({ 'master_colour': True })
            self.spectrum = Spectrum(name, **self.opts['spectrum_types'])
        else:
            self.spectrum = None
            
        #if self.opts['constant']:
        #    self.types.append( ('constant', 'Constant', 'constant') )
        #    self.constant = Constant(name, **self.opts['constant_settings'])
        #else:
        #    self.constant = None
        
        if self.opts['texture']:
            self.types.append( ('texture', 'Texture', 'texture') )
            self.texture = Texture(name)
        else:
            self.texture = None
        
        if self.opts['shader']:
            self.types.append( ('shader', 'Shader', 'shader') )
            self.shader = Shader(name)
        else:
            self.shader = None
                  
        self.properties = self.get_properties()
    
    def get_properties(self):
        if self.opts['label'] is None:
            p = [{
                'type': 'text',
                'attr': self.name+'_label',
                'name': ' '.join([i.capitalize() for i in self.name.split('_')]),
            }]
        else:
            p = [{
                'type': 'text',
                'attr': self.name+'_label',
                'name': self.opts['label'],
            }]
        
        if self.opts['switch']:
            p += [{
                'type': 'bool',
                'attr': self.name + '_enabled',
                'name': 'Enabled',
                'description': 'Enabled',
                'default': False
            }]
        
        p += [{
            'type': 'enum',
            'attr': self.name + '_type',
            'name': self.name + ' Type',
            'description': 'Type',
            'default': self.types[0][0],
            'items': self.types
        }]
        
        if self.spectrum is not None:
            p += self.spectrum.properties
        #if self.constant is not None:
        #    p += self.constant.properties
        if self.texture is not None:
            p += self.texture.properties
        if self.shader is not None:
            p += self.shader.properties
            
        return p
    


class indigo_material_feature(bpy.types.PropertyGroup):#just a label for now
    pass

Cha_Emit = MaterialChannel('emission', spectrum=True,  texture=True, shader=False, switch=True, label='Emission', spectrum_types={'rgb':True,'blackbody':True,'uniform':True})
def EmissionLightLayerParameter():
    return [
        {
            'attr': 'emit_layer',
            'type': 'string',
            'name': 'Light Layer',
            'description': 'lightlayer; leave blank to use default'
        },
        {
            'type': 'prop_search',
            'attr': 'lightlayer_chooser',
            'src': lambda s,c: s.scene.indigo_lightlayers,
            'src_attr': 'lightlayers',
            'trg': lambda s,c: c.indigo_material_emission,
            'trg_attr': 'emit_layer',
            'name': 'Light Layer'
        },
    ]
@register_properties_dict
class indigo_material_emission(indigo_material_feature):
    
    properties = Cha_Emit.properties + \
        EmissionLightLayerParameter() + \
        [
        {
            'type': 'float',
            'attr': 'emit_power',
            'name': ' Power',
            'description': ' Power',
            'default': 1500.0,
            'min': 0.0,
            'max': 1000000.0
        },
        {
            'type': 'float',
            'attr': 'emit_gain_val',
            'name': ' Gain',
            'description': ' Gain',
            'default': 1.0,
            'min': 0.0,
            'max': 1.0
        },
        {
            'type': 'int',
            'attr': 'emit_gain_exp',
            'name': '*10^',
            'description': 'Exponent',
            'default': 0,
            'min': -30,
            'max': 30
        },
        {
            'type': 'bool',
            'attr': 'emission_scale',
            'name': 'Emission scale',
            'description': 'Emission scale',
            'default': False,
        },
        {
            'type': 'enum',
            'attr': 'emission_scale_measure',
            'name': 'Unit',
            'description': 'Units for emission scale',
            'default': 'luminous_flux',
            'items': [
                ('luminous_flux', 'lm', 'Luminous flux'),
                ('luminous_intensity', 'cd', 'Luminous intensity (lm/sr)'),
                ('luminance', 'nits', 'Luminance (lm/sr/m/m)'),
                ('luminous_emittance', 'lux', 'Luminous emittance (lm/m/m)')
            ],
        },
        {
            'type': 'float',
            'attr': 'emission_scale_value',
            'name': 'Value',
            'description': 'Emission scale value',
            'default': 1.0,
            'min': 0.0,
            'soft_min': 0.0,
            'max': 10.0,
            'soft_max': 10.0,
        },
        {
            'type': 'int',
            'attr': 'emission_scale_exp',
            'name': '*10^',
            'description': 'Emission scale exponent',
            'default': 0,
            'min': -30,
            'max': 30
        },
        {
            'type': 'bool',
            'attr': 'emit_ies',
            'name': 'IES Profile',
            'description': 'IES Profile',
            'default': False,
        },
        {
            'type': 'string',
            'subtype': 'FILE_PATH',
            'attr': 'emit_ies_path',
            'name': ' IES Path',
            'description': ' IES Path',
            'default': '',
        },
        {
            'type': 'bool',
            'attr': 'backface_emit',
            'name': 'Back face emission',
            'description': 'Controls of back of face is emitting or not',
            'default': False,
        },
        {
            'type': 'float',
            'attr': 'em_sampling_mult',
            'name': 'Emission Sampling Multiplier',
            'description': 'A multiplier for the amount of sampling emission from this light material will receive',
            'default': 1.0,
            'min': 0.0,
            #'soft_min': 0.0,
            'max': 99999.0,
            #'soft_max': 10.0,
        },
    ]
    
    def get_output(self, obj, indigo_material, blender_material, scene):
        return []
    
Cha_Colour = MaterialChannel('colour', spectrum=True, texture=True, shader=True, switch=False, master_colour=True)
@register_properties_dict
class indigo_material_colour(indigo_material_feature):
    properties    = Cha_Colour.properties
    
    def get_output(self, obj, indigo_material, blender_material, scene):
        return []
    
Cha_Bump = MaterialChannel('bumpmap', spectrum=False, texture=True,  shader=True,  switch=True, label='Bump Map')
@register_properties_dict
class indigo_material_bumpmap(indigo_material_feature):
    properties    = Cha_Bump.properties
    
    def get_output(self, obj, indigo_material, blender_material, scene):
        return []
    
Cha_Normal = MaterialChannel('normalmap', spectrum=False, texture=True,  shader=True,  switch=True, label='Normal Map')
@register_properties_dict
class indigo_material_normalmap(indigo_material_feature):
    properties    = Cha_Normal.properties
    
    def get_output(self, obj, indigo_material, blender_material, scene):
        return []
    
Cha_Disp = MaterialChannel('displacement', spectrum=False, texture=True,  shader=True,  switch=True, label='Displacement Map')
@register_properties_dict
class indigo_material_displacement(indigo_material_feature):
    properties    = Cha_Disp.properties
    
    def get_output(self, obj, indigo_material, blender_material, scene):
        return []

#legacy    
Cha_Exp = MaterialChannel('exponent', spectrum=False, texture=True,  shader=True,  switch=True, label='Exponent Map')
@register_properties_dict
class indigo_material_exponent(indigo_material_feature):
    properties    = Cha_Exp.properties
    
    def get_output(self, obj, indigo_material, blender_material, scene):
        return []
#new
Cha_Rough = MaterialChannel('roughness', spectrum=False, texture=True,  shader=True,  switch=True, label='Roughness Map')
@register_properties_dict
class indigo_material_roughness(indigo_material_feature):
    properties    = Cha_Rough.properties
    
    def get_output(self, obj, indigo_material, blender_material, scene):
        return []
        
Cha_Fres = MaterialChannel('fresnel_scale', spectrum=False, texture=True,  shader=True,  switch=True, label='Fresnel Scale Map')
@register_properties_dict
class indigo_material_fresnel_scale(indigo_material_feature):
    properties    = Cha_Fres.properties
    
    def get_output(self, obj, indigo_material, blender_material, scene):
        return []

Cha_BlendMap  = MaterialChannel('blendmap', spectrum=False, texture=True,  shader=True,  switch=True, label='Blend Map')
@register_properties_dict
class indigo_material_blendmap(indigo_material_feature):
    properties    = Cha_BlendMap.properties
    
    def get_output(self, obj, indigo_material, blender_material, scene):
        return []
        
Cha_Transmittance  = MaterialChannel('transmittance', spectrum=True, texture=True,  shader=True,  switch=False, spectrum_types={'rgb':True, 'uniform':True, 'rgb_default':(0.5,0.5,0.5)}, label='Transmittance')
@register_properties_dict
class indigo_material_transmittance(indigo_material_feature):
    properties    = Cha_Transmittance.properties
    
    def get_output(self, obj, indigo_material, blender_material, scene):
        return []
        
Cha_Absorption  = MaterialChannel('absorption', spectrum=True, texture=True,  shader=True,  switch=False, spectrum_types={'rgb':True, 'rgbgain':True, 'uniform':True, 'rgb_default':(0.0,0.0,0.0)}, label='Absorption')
@register_properties_dict
class indigo_material_absorption(indigo_material_feature):
    properties    = Cha_Absorption.properties
    
    def get_output(self, obj, indigo_material, blender_material, scene):
        return []

Cha_AbsorptionLayer  = MaterialChannel('absorption_layer', spectrum=True, texture=True,  shader=True,  switch=True, spectrum_types={'rgb':True, 'rgbgain':True, 'uniform':True, 'blackbody': True, 'rgb_default':(0.0,0.0,0.0)}, label='Absorption Layer')
@register_properties_dict
class indigo_material_absorption_layer(indigo_material_feature):
    properties    = Cha_AbsorptionLayer.properties
    
    def get_output(self, obj, indigo_material, blender_material, scene):
        return []

def getRoughness(self):
    if self.use_roughness:
        return self.roughness_value
    else:
        roughness = (2/(self.exponent + 2))**(1/6)
        return roughness
    
def setRoughness(self, value):
    self.use_roughness = True
    self.roughness_value = value
    return None

@register_properties_dict
class indigo_material_specular(indigo_material_feature):
    #roughness = bpy.props.FloatProperty(description='Roughness', get=getRoughness)#, set=setRoughness)

    properties = [
        {
            'type': 'enum',
            'attr': 'type',
            'name': 'Specular Type',
            'description': 'Specular Type',
            'default': 'specular',
            'expand': True,
            'items': [
                ('specular', 'Specular', 'specular'),
                ('glossy_transparent', 'Glossy Transparent', 'glossy_transparent'),
            ]
        },
        {
            'type': 'prop_search',
            'attr': 'medium_chooser',
            'src': lambda s,c:  s.scene.indigo_material_medium,
            'src_attr': 'medium',
            'trg': lambda s,c:  c.indigo_material_specular,
            'trg_attr': 'medium_chooser',
            'name': 'Medium'
        },
        {
            'type': 'string',
            'attr': 'medium_chooser',
            'name': 'Medium',
            'description': 'Medium',
            'items': []
        },
        {
            'type': 'bool',
            'attr': 'transparent',
            'name': 'Transparent',
            'description': 'Transparent',
            'default': True,
        },
        {
            'type': 'float',
            'attr': 'exponent',
            'name': 'Exponent',
            'description': 'Exponent',
            'default': 1000.0,
            'min': 0.0,
            'max': 1000000.0
        },
        {
            # this acts as exponent-roughness bridge
            'type': 'float',
            'attr': 'roughness',
            'name': 'Roughness',
            'description': 'Roughness',
            'default': 0.5,
            'min': 0.0,
            'max': 1.0,
            'get': getRoughness,
            'set': setRoughness,
        },
        {
            'type': 'float',
            'attr': 'roughness_value',
            'name': 'Roughness',
            'description': 'Roughness',
            'default': 0.5,
            'min': 0.0,
            'max': 1.0,
        },
        {
            'type': 'bool',
            'attr': 'use_roughness',
            'name': 'Use Roughness',
            'description': 'Use Roughness',
            'default': False,
        },
        {
            'type': 'bool',
            'attr': 'arch_glass',
            'name': 'Arch Glass',
            'description': 'Arch Glass',
            'default': False,
        },
        {
            'type': 'bool',
            'attr': 'single_face',
            'name': 'Single Face',
            'description': 'Single Face',
            'default': False,
        },
        {
            'type': 'int',
            'attr': 'precedence',
            'name': 'Precedence',
            'description': 'Precedence',
            'default': 10,
            'min': 1,
            'max': 100
        },
    ] 
        
    def _copy_props(self, src, trg):
        for prop in src.properties:
            attr_name = prop['attr']
            if hasattr(src, attr_name):
                setattr(
                    trg,
                    attr_name,
                    getattr(src, attr_name)
                )
    
    def get_output(self, obj, indigo_material, blender_material, scene):
        im = SpecularMaterial(obj, blender_material.name, indigo_material, self).build_xml_element(
            blender_material,
            scene=scene
        )
        
        return [ im ]

@register_properties_dict
class indigo_material_diffuse(indigo_material_feature):
    
    channel_name = 'albedo'
    
    properties = [
        {
            'type': 'bool',
            'attr': 'transmitter',
            'name': 'Transmitter',
            'description': 'Diffuse Transmitter',
            'default': False,
        },
        {
            'type': 'float',
            'attr': 'sigma', # if sigma > 0, export an oren-nayar instead
            'name': 'Sigma',
            'description': 'Oren-Nayar Sigma Parameter',
            'default': 0.0,
            'min': 0.0,
            'max': 20.0
        },
        {
            'type': 'bool',
            'attr': 'shadow_catcher',
            'name': 'Shadow Catcher',
            'description': 'Make this material a shadow catching material.  For use with the shadow pass.',
            'default': False,
        },
    ]
    
    def get_output(self, obj, indigo_material, blender_material, scene):
        im = DiffuseMaterial(obj, blender_material.name, indigo_material, self).build_xml_element(
            blender_material,
            scene=scene
        )
        return [im]
    
NK_CACHE = {}

def find_nkdata(self, context):
    try:
        nk_path = os.path.join(getResourcesPath(context.scene), 'nkdata')
        if not os.path.exists(nk_path):
            return []
        
        if nk_path in NK_CACHE.keys():
            return NK_CACHE[nk_path]
        
        nks = os.listdir(nk_path)
        nks = [('nkdata/' + nk, nk[:-3], nk[:-3]) for nk in nks if nk[0] != '.' and nk not in ('7059.nk')] # 7059.nk not supported in Indigo
        NK_CACHE[nk_path] = nks
        return nks
    except:
        return []

@register_properties_dict
class indigo_material_phong(indigo_material_feature):
    
    channel_name = 'diffuse_albedo'
    
    properties = [
        {
            'type': 'bool',
            'attr': 'specular_reflectivity',
            'name': 'Specular Reflectivity',
            'description': 'Specular Reflectivity',
            'default': False
        },
        {
            'type': 'enum',
            'attr': 'nk_data_type',
            'name': 'NK Type',
            'items': [
                ('none', 'None', 'Do not use NK data'),
                ('preset', 'Preset', 'Use an NK preset'),
                ('file', 'File', 'Use specified NK file')
            ],
            'default': 'none'
        },
        {
            'type': 'enum',
            'attr': 'nk_data_preset',
            'name': 'NK Preset',
            'items': find_nkdata
        },
        {
            'type': 'string',
            'attr': 'nk_data_file',
            'name': 'NK Data',
            'description': 'NK Data',
            'default': '',
            'subtype': 'FILE_PATH'
        },
        {
            'type': 'float',
            'attr': 'exponent',
            'name': 'Exponent',
            'description': 'Exponent',
            'default': 1000.0,
            'min': 0.0,
            'max': 1000000.0
        },
        {
            # this acts as exponent-roughness bridge
            'type': 'float',
            'attr': 'roughness',
            'name': 'Roughness',
            'description': 'Roughness',
            'default': 0.5,
            'min': 0.0,
            'max': 1.0,
            'get': getRoughness,
            'set': setRoughness,
        },
        {
            'type': 'float',
            'attr': 'roughness_value',
            'name': 'Roughness',
            'description': 'Roughness',
            'default': 0.5,
            'min': 0.0,
            'max': 1.0,
        },
        {
            'type': 'bool',
            'attr': 'use_roughness',
            'name': 'Use Roughness',
            'description': 'Use Roughness',
            'default': False,
        },
        {
            'type': 'float',
            'attr': 'fresnel_scale',
            'name': 'Fresnel Scale',
            'description': 'Fresnel Scale',
            'default': 1.0,
            'min': 0.0,
            'max': 1.0
        },
        {
            'type': 'float',
            'attr': 'ior',
            'name': 'IOR',
            'description': 'IOR',
            'default': 1.3,
            'min': 0.0,
            'max': 20.0,
            'precision': 6
        },
    ]
    
    def get_output(self, obj, indigo_material, blender_material, scene):
        im = PhongMaterial(obj, blender_material.name, indigo_material, self).build_xml_element(
            blender_material,
            scene=scene
        )
        return [im]
        
        
@register_properties_dict
class indigo_material_coating(indigo_material_feature):
    
    properties = [
        {
            'type': 'float',
            'attr': 'thickness',
            'name': 'Thickness',
            'description': 'thickness',
            'default': 1.0, # micrometres
            'min': 0.0,
            'max': 1000000.0
        },
        {
            'type': 'float',
            'attr': 'roughness',
            'name': 'Roughness',
            'description': 'roughness',
            'default': 0.3,
            'min': 0.0,
            'max': 1.0
        },
        {
            'type': 'float',
            'attr': 'fresnel_scale',
            'name': 'Fresnel Scale',
            'description': 'Fresnel Scale',
            'default': 1.0,
            'min': 0.0,
            'max': 1.0
        },
        {
            'type': 'float',
            'attr': 'ior',
            'name': 'IOR',
            'description': 'IOR',
            'default': 1.3,
            'min': 0.0,
            'max': 20.0,
            'precision': 6
        },
        {
            'type': 'bool',
            'attr': 'interference',
            'name': 'interference',
            'description': 'interference',
            'default': False,
        },
        {
            'type': 'string',
            'attr': 'substrate_material_index',
            'name': 'substrate_material_index',
            'description': 'substrate_material_index',
        },
        {
            'attr': 'substrate_material',
            'type': 'prop_search',
            'name': 'Substrate Material',
            # source data list
            'src': lambda s,c: bpy.data,
            'src_attr': 'materials',
            # target property
            'trg': lambda s,c: c.indigo_material_coating,
            'trg_attr': 'substrate_material_index',
            'text': 'Substrate Material',
        },
    ]
    
    def get_output(self, obj, indigo_material, blender_material, scene):
        
        materials = []
        
        # Try and get the XML for the substrate material
        if self.substrate_material_index in bpy.data.materials:
            mata = bpy.data.materials[self.substrate_material_index]
            materials.extend(
                mata.indigo_material.factory(obj, mata, scene)
            )
            
        im = CoatingMaterial(obj, blender_material.name, indigo_material, self).build_xml_element(
            blender_material,
            scene=scene
        )
        materials.append(im)
        
        return materials
        
        
@register_properties_dict
class indigo_material_doublesidedthin(indigo_material_feature):
    
    properties = [
        {
            'type': 'float',
            'attr': 'front_roughness',
            'name': 'Front Roughness',
            'description': 'front_roughness',
            'default': 0.3,
            'min': 0.0,
            'max': 1.0
        },
        {
            'type': 'float',
            'attr': 'back_roughness',
            'name': 'Back Roughness',
            'description': 'back_roughness',
            'default': 0.3,
            'min': 0.0,
            'max': 1.0
        },
        {
            'type': 'float',
            'attr': 'r_f',
            'name': 'Reflectance fraction (r_f)',
            'description': 'Reflectance fraction',
            'default': 0.5,
            'min': 0.0,
            'max': 1.0
        },
        {
            'type': 'float',
            'attr': 'front_fresnel_scale',
            'name': 'Front Fresnel Scale',
            'description': 'Front Fresnel Scale',
            'default': 1.0,
            'min': 0.0,
            'max': 1.0
        },
        {
            'type': 'float',
            'attr': 'back_fresnel_scale',
            'name': 'Back Fresnel Scale',
            'description': 'Back Fresnel Scale',
            'default': 1.0,
            'min': 0.0,
            'max': 1.0
        },
        {
            'type': 'float',
            'attr': 'ior',
            'name': 'IOR',
            'description': 'IOR',
            'default': 1.3,
            'min': 0.0,
            'max': 20.0,
            'precision': 6
        },
        {
            'type': 'string',
            'attr': 'front_material_index',
            'name': 'front_material_index',
            'description': 'front_material_index',
        },
        {
            'type': 'string',
            'attr': 'back_material_index',
            'name': 'back_material_index',
            'description': 'back_material_index',
        },
        {
            'attr': 'front_material',
            'type': 'prop_search',
            'name': 'Front Material',
            # source data list
            'src': lambda s,c: bpy.data,
            'src_attr': 'materials',
            # target property
            'trg': lambda s,c: c.indigo_material_doublesidedthin,
            'trg_attr': 'front_material_index',
            'text': 'Substrate Material',
        },
        {
            'attr': 'back_material',
            'type': 'prop_search',
            'name': 'Back Material',
            # source data list
            'src': lambda s,c: bpy.data,
            'src_attr': 'materials',
            # target property
            'trg': lambda s,c: c.indigo_material_doublesidedthin,
            'trg_attr': 'back_material_index',
            'text': 'Back Material',
        },
    ]
    
    def get_output(self, obj, indigo_material, blender_material, scene):
        
        materials = []
        
        # Try and get the XML for the front, back material
        if self.front_material_index in bpy.data.materials:
            mata = bpy.data.materials[self.front_material_index]
            materials.extend(
                mata.indigo_material.factory(obj, mata, scene)
            )
        if self.back_material_index in bpy.data.materials:
            mata = bpy.data.materials[self.back_material_index]
            materials.extend(
                mata.indigo_material.factory(obj, mata, scene)
            )
            
        im = DoubleSidedThinMaterial(obj, blender_material.name, indigo_material, self).build_xml_element(
            blender_material,
            scene=scene
        )
        materials.append(im)
        
        return materials
        

@register_properties_dict
class indigo_material_blended(indigo_material_feature):
    
    properties = [
        {
            'type': 'float',
            'attr': 'factor',
            'name': 'Blend Factor',
            'description': 'Blend Factor',
            'default': 0.5,
            'min': 0.0,
            'max': 1.0,
        },
        {
            'type': 'bool',
            'attr': 'step',
            'name': 'Step Blend',
            'description': 'Step Blend; use for "clip maps"',
            'default': False,
        },
        {
            'type': 'string',
            'attr': 'a_index',
            'name': 'a_index',
            'description': 'a_index',
        },
        {
            'attr': 'a',
            'type': 'prop_search',
            'name': 'Material A',
            # source data list
            'src': lambda s,c: bpy.data,
            'src_attr': 'materials',
            # target property
            'trg': lambda s,c: c.indigo_material_blended,
            'trg_attr': 'a_index',
            'text': 'Material A',
        },
        {
            'type': 'bool',
            'attr': 'a_null',
            'name': 'Null',
            'description': 'Use Null material for slot A',
            'default': False,
        },
        
        {
            'type': 'string',
            'attr': 'b_index',
            'name': 'b_index',
            'description': 'b_index',
        },
        {
            'attr': 'b',
            'type': 'prop_search',
            'name': 'Material B',
            # source data list
            'src': lambda s,c: bpy.data,
            'src_attr': 'materials',
            # target property
            'trg': lambda s,c: c.indigo_material_blended,
            'trg_attr': 'b_index',
            'text': 'Material B',
        },
        {
            'type': 'bool',
            'attr': 'b_null',
            'name': 'Null',
            'description': 'Use Null material for slot B',
            'default': False,
        },
    ]
    
    def get_output(self, obj, indigo_material, blender_material, scene):
        materials = []
        
        if not self.a_null and self.a_index in bpy.data.materials:
            mata = bpy.data.materials[self.a_index]
            materials.extend(
                mata.indigo_material.factory(obj, mata, scene)
            )
        
        if not self.b_null and self.b_index in bpy.data.materials:
            matb = bpy.data.materials[self.b_index]
            materials.extend(
                matb.indigo_material.factory(obj, matb, scene)
            )
        
        materials.append( BlendMaterial(obj, blender_material.name, indigo_material, self).build_xml_element(
            blender_material,
            scene=scene
        ) )
        return materials

def try_file_decode(raw_bytes):
    if type(raw_bytes) != type(b''):
        return raw_bytes
    
    # use these character encodings in order of preference
    for encoding in ['utf-8', 'latin-1', 'ascii']:
        try:
            decoded_string = raw_bytes.decode(encoding)
            return decoded_string
        except:
            continue
    
    raise Exception('Cannot decode bytes from file')
    
    
def updated_event(self, context):
    try:
        self.material_name = get_material_filename_from_external_mat(self, context)
    except:
        pass
        
        
def get_material_name_from_IGM(igm_contents):
    try:
        root = ET.fromstring(igm_contents)

        # For each material definition:
        name = ""
        for material in root.findall('material'):
            name_elem = material.find('name')
            if(name_elem == None):
                raise Exception('Failed to find material name in IGM file.')
            name = name_elem.text

        # Return last name found
        return name
    except Exception as e:
        raise Exception('While parsing IGM file: ' + str(e))

    
def get_material_filename_from_external_mat(self, blender_material):
    try:
        #NOTE: We can't set material_name etc.. here, or we get an error message about updating attributes when we render animations.
        # self.material_name = 'Checking...'
        extmat_file = efutil.filesystem_path( self.filename )
        if not os.path.exists(extmat_file):
            ex_str = 'Invalid file path for External material'
            if (hasattr(blender_material, "name")):
                ex_str += ' "%s"' % blender_material.name
            raise Exception(ex_str)
            
        # If the user specified a PIGM file:
        if self.filename[-5:].lower() == '.pigm':

            # Check it is a valid zip file
            if not zipfile.is_zipfile( extmat_file ):
                ex_str = 'Invalid PIGM file for External material'
                if (hasattr(blender_material, "name")):
                    ex_str += ' "%s"' % blender_material.name
                raise Exception(ex_str)

            # Find the name of the IGM file inside the PIGM
            with zipfile.ZipFile(extmat_file, 'r') as zf:
                igm_filename = ''
                for zf_internal in zf.namelist():
                    if zf_internal[-4:].lower() == '.igm':
                        igm_filename = zf_internal
                        break
                
                # If no IGM file found, raise exception
                if igm_filename == '':
                    ex_str = 'No IGM found in PIGM for External material'
                    if (hasattr(blender_material, "name")):
                        ex_str += ' "%s"' % blender_material.name
                    raise Exception(ex_str)

                # Get the file contents, store in 'igm_data'
                with zf.open(igm_filename, 'r') as igm_file:
                    igm_data = try_file_decode(igm_file.read())

        # Else if the user specified an IGM file:
        elif self.filename[-4:].lower() == '.igm':
            with open(extmat_file, 'r') as igm_file:
                igm_data = try_file_decode(igm_file.read()) # Get the file contents
        else:
            ex_str = "'" + str(self.filename) + "' is not an IGM or PIGM file.  (For External material"
            if (hasattr(blender_material, "name")):
                ex_str += ' "%s"' % blender_material.name + ")"
            raise Exception(ex_str)

        igm_name = get_material_name_from_IGM(igm_data)
        # print("igm_name: '" + str(igm_name) + "'")
        
        if igm_name == '':
            ex_str = 'Cannot find IGM name for External material'
            if (hasattr(blender_material, "name")):
                ex_str += ' "%s"' % blender_material.name
            raise Exception(ex_str)
        
        self.material_name = igm_name # ??? seems to work both in stills and animations - MZ
            
        return igm_name
        
        # self.is_valid = True
    except Exception as err:
        #print('%s' % err)
        # self.material_name = '%s' % err
        # self.is_valid = False
        raise err

@register_properties_dict
class indigo_material_external(indigo_material_feature):
    
    properties = [
        {
            'type': 'string',
            'subtype': 'FILE_PATH',
            'attr': 'filename',
            'name': 'IGM or PIGM file',
            'description': 'IGM or PIGM file',
            'default': '',
            'update': updated_event
        },
        {
            'type': 'string',
            'attr': 'material_name',
            'name': 'Name'
        },
        # NOTE: is_valid is not used any more.
        {
            'type': 'bool',
            'attr': 'is_valid',
            'default': False
        },
    ]
    
    # Returns list of XML elements or something like that.
    def get_output(self, obj, indigo_material, blender_material, scene):

        try:
            # Check that we can extract the material name from the external material file.
            # Note that we don't actually do anything with the result, but it may throw an exception if it fails.
            get_material_filename_from_external_mat(self, blender_material)
            
            extmat_file = efutil.filesystem_path( self.filename )
            if not os.path.exists(extmat_file):
                return []
            
            if self.filename[-5:].lower() == '.pigm':
                
                if not zipfile.is_zipfile( extmat_file ):
                    return []
                
                with zipfile.ZipFile(extmat_file) as zf:
                    igm_filename = ''
                    for zf_internal in zf.namelist():
                        if zf_internal[-4:].lower() == '.igm':
                            igm_filename = zf_internal
                            break
                    
                    if igm_filename == '':
                        return []
                    
                    # Extract the material to the export directory
                    zf.extractall(efutil.export_path)
            
            elif self.filename[-4:].lower() == '.igm':
                extmat_file = efutil.path_relative_to_export( self.filename )
                igm_filename = extmat_file
            else:
                return []
            
            im = ExternalMaterial(igm_filename).build_xml_element(
                blender_material
            )
            return [im]

        except Exception as err:
            raise Exception(str(err))

@register_properties_dict
class indigo_material_null(indigo_material_feature):
    properties = []
    
    def get_output(self, obj, indigo_material, blender_material, scene):
        im = NullMaterial(obj, blender_material.name, indigo_material, self).build_xml_element(
            blender_material,
            scene=scene
        )
        return [im]
    
@register_properties_dict
class indigo_material_fastsss(indigo_material_feature):
    channel_name = 'albedo'
    
    properties = [
        {
            'type': 'prop_search',
            'attr': 'medium_chooser',
            'src': lambda s,c:  s.scene.indigo_material_medium,
            'src_attr': 'medium',
            'trg': lambda s,c:  c.indigo_material_specular,
            'trg_attr': 'medium_chooser',
            'name': 'Medium'
        },
        {
            'type': 'string',
            'attr': 'medium_chooser',
            'name': 'Medium',
            'description': 'Medium',
            'items': []
        },
        {
            'type': 'float',
            'attr': 'roughness',
            'name': 'Roughness',
            'description': 'Roughness',
            'default': 0.5,
            'min': 0.0,
            'max': 1.0,
        },
        {
            'type': 'float',
            'attr': 'fresnel_scale',
            'name': 'Fresnel Scale',
            'description': 'Fresnel Scale',
            'default': 1.0,
            'min': 0.0,
            'max': 1.0
        },
    ]
    
    def get_output(self, obj, indigo_material, blender_material, scene):
        im = FastSSSMaterial(obj, blender_material.name, indigo_material, self).build_xml_element(
            blender_material,
            scene=scene
        )
        return [im]
            
@register_properties_dict
class Indigo_Material_Properties(bpy.types.PropertyGroup):
    properties = [
        # Master material type
        {
            'type': 'enum',
            'attr': 'type',
            'name': 'Material Type',
            'description': 'Indigo Material Type',
            'default': 'diffuse',
            'items': [
                ('diffuse', 'Diffuse', 'diffuse'),
                ('phong', 'Phong', 'phong'),
                ('coating', 'Coating', 'coating'),
                ('doublesidedthin', 'DoubleSidedThin', 'doublesidedthin'),
                ('specular', 'Specular', 'specular'),
                ('blended', 'Blended', 'blended'),
                ('external', 'External', 'external'),
                ('null', 'Null', 'null'),
                ('fastsss', 'Fast SSS', 'fastsss'),
            ]
        },
    ]
    indigo_material_emission = bpy.props.PointerProperty(type = indigo_material_emission)
    indigo_material_colour = bpy.props.PointerProperty(type = indigo_material_colour)
    indigo_material_bumpmap = bpy.props.PointerProperty(type = indigo_material_bumpmap)
    indigo_material_normalmap = bpy.props.PointerProperty(type = indigo_material_normalmap)
    indigo_material_displacement = bpy.props.PointerProperty(type = indigo_material_displacement)
    indigo_material_exponent = bpy.props.PointerProperty(type = indigo_material_exponent) #legacy
    indigo_material_roughness = bpy.props.PointerProperty(type = indigo_material_roughness) #new
    indigo_material_fresnel_scale = bpy.props.PointerProperty(type = indigo_material_fresnel_scale)
    indigo_material_blendmap = bpy.props.PointerProperty(type = indigo_material_blendmap)
    indigo_material_transmittance = bpy.props.PointerProperty(type = indigo_material_transmittance)
    indigo_material_absorption = bpy.props.PointerProperty(type = indigo_material_absorption)
    indigo_material_absorption_layer = bpy.props.PointerProperty(type = indigo_material_absorption_layer)
    indigo_material_specular = bpy.props.PointerProperty(type = indigo_material_specular)
    indigo_material_diffuse = bpy.props.PointerProperty(type = indigo_material_diffuse)
    indigo_material_phong = bpy.props.PointerProperty(type = indigo_material_phong)
    indigo_material_coating = bpy.props.PointerProperty(type = indigo_material_coating)
    indigo_material_doublesidedthin = bpy.props.PointerProperty(type = indigo_material_doublesidedthin)
    indigo_material_blended = bpy.props.PointerProperty(type = indigo_material_blended)
    indigo_material_external = bpy.props.PointerProperty(type = indigo_material_external)
    indigo_material_null = bpy.props.PointerProperty(type = indigo_material_null)
    indigo_material_fastsss = bpy.props.PointerProperty(type = indigo_material_fastsss)
    
    def get_name(self, blender_mat):
        if self.type == 'external':
            # print('IS EXTERNAL MAT: %s/%s' % (blender_mat.name, self.indigo_material_external.material_name))
            return self.indigo_material_external.material_name
        
        return blender_mat.name
    
    # xml element factory
    
    def factory(self, obj, mat, scene):
        out_elements = []
        
        # Gather elements from features compatible with current mat type
        if self.type in MATERIAL_FEATURES.keys():
            for feature in MATERIAL_FEATURES[self.type]:
                fpg = getattr(self, 'indigo_material_%s'%feature)
                out_elements.extend( fpg.get_output(obj, self, mat, scene) )
        
        return out_elements