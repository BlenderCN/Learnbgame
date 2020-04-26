import bpy

import mathutils
from . material import Spectrum
from .. extensions_framework import util as efutil

from .. import export
from . import register_properties_dict


Spe_BG = Spectrum('env_bg', rgb=True, uniform=True, blackbody=True)

@register_properties_dict
class Indigo_Lamp_Sun_Properties(bpy.types.PropertyGroup, export.xml_builder):
    properties = [
        {
            'type': 'float',
            'attr': 'turbidity',
            'name': 'Turbidity',
            'description': 'Turbidity',
            'min': 1.0,
            'max': 10.0,
            'default': 2.0
        },
        {
            'type': 'enum',
            'attr': 'model',
            'name': 'Sunsky Model',
            'description': 'SunSky Model',
            'default': 'captured-simulation',
            'items': [
                ('original', 'Original', 'Use original model'),
                ('extra_atmospheric', 'Extra-Atmospheric', 'Use extra-atmospheric ("space") model'),
                ('captured-simulation', 'Captured simulation', 'Use realistic data')
            ]
        },
        {
            'type': 'bool',
            'attr': 'uselayers',
            'name': 'Use light layers',
            'description': 'Place sun and sky on separate light layers',
            'default': False
        },
        {
            'type': 'string',
            'attr': 'sunlayer',
            'name': 'Sun light layer',
            'default': ''
        },
        {
            'type': 'prop_search',
            'attr': 'sun_lightlayer_chooser',
            'src': lambda s,c: s.scene.indigo_lightlayers,
            'src_attr': 'lightlayers',
            'trg': lambda s,c: s.lamp.indigo_lamp_sun,
            'trg_attr': 'sunlayer',
            'name': 'Sun'
        },
        {
            'type': 'string',
            'attr': 'skylayer',
            'name': 'Sky light layer',
            'default': ''
        },
        {
            'type': 'prop_search',
            'attr': 'sky_lightlayer_chooser',
            'src': lambda s,c: s.scene.indigo_lightlayers,
            'src_attr': 'lightlayers',
            'trg': lambda s,c: s.lamp.indigo_lamp_sun,
            'trg_attr': 'skylayer',
            'name': 'Sky'
        },
    ]
    
    # xml_builder members
    
    def build_xml_element(self, obj, scene):
        xml = self.Element('material')
        xml_format = {
            'name': [obj.name],
            'sunsky': self.get_format(obj, scene)
        }
        self.build_subelements(obj, xml_format, xml)
        return xml
    
    def get_format(self, obj, scene):
        fmt = {
            'sundir': '',
            'turbidity': '',
            'extra_atmospheric': ['false'],
            'model': ['original']
        }
        
        m = obj.matrix_world.transposed()
        
        fmt['sundir'] = [m[2][0], m[2][1], m[2][2]]
        
        fmt['turbidity'] = [self.turbidity]
        
        if self.model == 'extra_atmospheric':
            fmt['extra_atmospheric'] = ['true']
            fmt['model'] = ['original']
        else:
            fmt['extra_atmospheric'] = ['false']
            fmt['model'] = [self.model]
        
        if self.uselayers and not scene.indigo_lightlayers.ignore:
            
            lls = scene.indigo_lightlayers.enumerate()
            valid_layers = lls.keys()
            
            sun_layer = self.sunlayer
            fmt['sun_layer'] = [lls[sun_layer]] if sun_layer in valid_layers else [0]
            sky_layer = self.skylayer
            fmt['sky_layer'] = [lls[sky_layer]] if sky_layer in valid_layers else [0]
        
        return fmt
    
@register_properties_dict
class Indigo_Lamp_Hemi_Properties(bpy.types.PropertyGroup, export.xml_builder):
    properties = [
        {
            'type': 'enum',
            'attr': 'type',
            'name': 'Lamp type',
            'description': 'Type of lighting to export',
            'items': [
                ('background', 'Background colour', 'A non-directional, uniform background colour'),
                ('env_map', 'HDRI environment map', 'Use image based lighting')
            ]
        },
        {
            'type': 'string',
            'subtype': 'FILE_PATH',
            'attr': 'env_map_path',
            'name': 'Env Map',
            'description': '(HDRI) Image to use as environment map',
        },
        {
            'type': 'enum',
            'attr': 'env_map_type',
            'name': 'Env map type',
            'description': 'The type of the environment map',
            'items': [
                ('spherical', 'Spherical', 'spherical'),
                ('spherical_environment', 'Spherical Environment', 'spherical_environment')
            ]
        },
        {
            'type': 'float',
            'attr': 'env_map_gain_val',
            'name': 'Gain',
            'description': 'Gain value to apply to environment',
            'min': 0.0,
            'max': 1.0,
            'default': 1.0
        },
        {
            'type': 'int',
            'attr': 'env_map_gain_exp',
            'name': '*10^',
            'description': 'Gain exponent to apply to environment',
            'min': -30,
            'max': 30,
            'default': 0
        },
        {
            'type': 'float',
            'attr': 'env_bg_SP_rgb_gain_val',
            'name': 'Gain',
            'description': 'Gain value to apply to environment',
            'min': 0.0,
            'max': 10000.0,
            'default': 1.0
        },
        {
            'type': 'int',
            'attr': 'env_map_width',
            'name': 'Width',
            'description': 'Width (and height) of spherical env map',
            'min': 0,
            'max': 20000,
            'default': 640
        },
        
        
        {
            'type': 'string',
            'attr': 'layer',
            'name': 'Light layer',
            'default': ''
        },
        {
            'type': 'prop_search',
            'attr': 'lightlayer_chooser',
            'src': lambda s,c: s.scene.indigo_lightlayers,
            'src_attr': 'lightlayers',
            'trg': lambda s,c: s.lamp.indigo_lamp_hemi,
            'trg_attr': 'layer',
            'name': 'Light layer'
        },
    ] + \
    Spe_BG.properties
    
    # xml_builder members
    
    def build_xml_element(self, obj, scene):
        xml = self.Element('material')
        xml_format = {
            'name': [obj.name],
        }
        if self.type == 'background':
            xml_format['diffuse'] = self.get_background_format(obj, scene)
        
        if self.type == 'env_map':
            xml_format['diffuse'] = self.get_env_map_format(obj, scene)
        
        self.build_subelements(obj, xml_format, xml)
        return xml
    
    def get_background_spectrum(self):
        if self.env_bg_SP_type == 'rgb':
            from .. export.materials.spectra import rgb
            return rgb([i*self.env_bg_SP_rgb_gain_val for i in self.env_bg_SP_rgb], gain=[1])
        elif self.env_bg_SP_type == 'uniform':
            from .. export.materials.spectra import uniform
            return uniform([
                self.env_bg_SP_uniform_val * \
                10**self.env_bg_SP_uniform_exp
            ])
        elif self.env_bg_SP_type == 'blackbody':
            from .. export.materials.spectra import blackbody
            return blackbody(
                [self.env_bg_SP_blackbody_temp],
                [self.env_bg_SP_blackbody_gain]
            )
    
    def get_background_format(self, obj, scene):
        fmt = {
            'albedo_spectrum': self.get_background_spectrum(),
            'base_emission': { 'constant': self.get_background_spectrum() },
        }
        
        if self.layer != '' and not scene.indigo_lightlayers.ignore:
            
            lls = scene.indigo_lightlayers.enumerate()
            valid_layers = lls.keys()
            
            fmt['layer'] = [lls[self.layer]] if self.layer in valid_layers else [0]
        
        return fmt
    
    def get_env_map_format(self, obj, scene):
        
        # TODO; re-implement spherical/angular and spherical width ?
        
        trans = mathutils.Matrix.Identity(3)
        
        trans[0][0:3] = 0.0, 1.0, 0.0
        trans[1][0:3] = -1.0, 0.0, 0.0
        trans[2][0:3] = 0.0, 0.0, 1.0
        
        mat = obj.matrix_world.to_3x3()
        mat = mat * trans
        
        rq = mat.to_quaternion().to_axis_angle()
        
        #rmr = []
        #for row in tbt.col:
        #    rmr.extend(row)
        
        fmt = {
            'texture': {
                'path': [efutil.path_relative_to_export(self.env_map_path)],
                'exponent': [1.0],    # TODO; make configurable?
                'tex_coord_generation': {
                    self.env_map_type: {
                        'rotation': {
                            #'matrix': rmr
                            'axis_rotation': {
                                'axis': list(rq[0]),
                                'angle': [-rq[1]]
                            }
                        }
                    }
                },
            },
            'base_emission': {
                'constant': {
                    'uniform': {
                        'value': [self.env_map_gain_val * 10**self.env_map_gain_exp]
                    }
                }
            },
            'emission': {
                'texture': {
                    'texture_index': [0]
                }
            }
        }
        
        if self.layer != '' and not scene.indigo_lightlayers.ignore:
            
            lls = scene.indigo_lightlayers.enumerate()
            valid_layers = lls.keys()
            
            fmt['layer'] = [lls[self.layer]] if self.layer in valid_layers else [0]
        
        return fmt