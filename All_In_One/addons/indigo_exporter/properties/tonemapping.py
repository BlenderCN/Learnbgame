import bpy
import os

from .. extensions_framework import util as efutil

from .. core.util import getResourcesPath
from .. export import xml_builder, indigo_log

from . import register_properties_dict

CRF_CACHE = {}

def find_crfs(self, context):
    try:
        crf_path = os.path.join(getResourcesPath(context.scene), 'data', 'camera_response_functions')
        if not os.path.exists(crf_path):
            return []
        
        if crf_path in CRF_CACHE.keys():
            return CRF_CACHE[crf_path]
        
        crfs = os.listdir(crf_path)
        crfs = [('data/camera_response_functions/' + crf, crf[:-4], crf[:-4]) for crf in crfs if crf != 'source.txt' and crf[0] != '.']
        CRF_CACHE[crf_path] = crfs
        return crfs
    except:
        return []
    
@register_properties_dict
class Indigo_Tonemapping_Properties(bpy.types.PropertyGroup, xml_builder):
    properties = [
        {
            'type': 'enum',
            'attr': 'tonemap_type',
            'name': 'Tonemapping Type',
            'description': 'Tonemapping Type',
            'default': 'reinhard',
            'items': [
                ('reinhard', 'Reinhard', 'reinhard'),
                ('linear', 'Linear', 'linear'),
                ('camera', 'Camera', 'camera'),
                ('filmic', 'Filmic', 'filmic'),
            ],
        },
        {
            'type': 'float',
            'attr': 'gamma',
            'name': 'Gamma Correction',
            'description': 'Gamma Correction factor',
            'default': 2.2,
            'min': 0.01,
            'soft_min': 0.01,
            'max': 5,
            'soft_max': 5,
        },
        {
            'type': 'text',
            'attr': 'reinhard_label',
            'name': 'Reinhard Tonemapping Settings:'
        },
        {
            'type': 'float',
            'attr': 'filmic_scale',
            'name': 'Scale',
            'description': 'Scale',
            'default': 1,
            'min': 0.0,
            'max': 999999,
        },
        {
            'type': 'float',
            'attr': 'reinhard_burn',
            'name': 'Burn',
            'description': 'Burn',
            'default': 6,
            'min': 0.1,
            'soft_min': 0.1,
            'max': 10,
            'soft_max': 10,
        },
        {
            'type': 'float',
            'attr': 'reinhard_pre',
            'name': 'Pre',
            'description': 'Pre Scale',
            'default': 4,
            'min': 0,
            'soft_min': 0,
            'max': 50,
            'soft_max': 50,
        },
        {
            'type': 'float',
            'attr': 'reinhard_post',
            'name': 'Post',
            'description': 'Post Scale',
            'default': 1.2,
            'min': 0,
            'soft_min': 0,
            'max': 50,
            'soft_max': 50,
        },
        {
            'type': 'text',
            'attr': 'linear_label',
            'name': 'Linear Tonemapping Settings:'
        },
        {
            'type': 'float',
            'attr': 'linear_unit',
            'name': 'Scale',
            'description': 'Scale',
            'default': 1,
            'min': 1,
            'soft_min': 1,
            'max': 9.999,
            'soft_max': 9.999,
            'compute': lambda c,self: self.linear_unit * pow(10, self.linear_exp)
        },
        {
            'type': 'int',
            'attr': 'linear_exp',
            'name': '*10^',
            'description': 'Exponent',
            'default': 0,
            'min': -30,
            'max': 30
        },
        {
            'type': 'text',
            'attr': 'camera_label',
            'name': 'Camera Tonemapping Settings:'
        },
        {
            'type': 'enum',
            'attr': 'camera_response_type',
            'name': 'Camera reponse type',
            'items': [
                ('preset', 'Preset', 'Use preset from indigo installation'),
                ('file', 'File', 'Specify camera response data file'),
            ],
            'default': 'preset',
            'expand': True
        },
        {
            'type': 'float',
            'attr': 'camera_ev',
            'name': 'EV Adjust',
            'description': 'Exposure Value Adjustment',
            'default': 0,
            'min': -20,
            'soft_min': -20,
            'max': 20,
            'soft_max': 20,
        },
        {
            'type': 'string',
            'attr': 'camera_response_file',
            'name': 'Response data',
            'description': 'Camera response function data file',
            'subtype': 'FILE_PATH',
        },
        {
            'type': 'enum',
            'attr': 'camera_response_preset',
            'name': 'Preset',
            'items': find_crfs
        },
    ]
    
    # xml_builder members
    
    def build_xml_element(self, scene):
        xml = self.Element('tonemapping')
        
        # format needs to be entirely generated at export time
        if self.tonemap_type == 'reinhard':
            xml_format = {
                'reinhard': {
                    'pre_scale': 'reinhard_pre',
                    'post_scale': 'reinhard_post',
                    'burn': 'reinhard_burn',
                }
            }
        elif self.tonemap_type == 'linear':
            xml_format = {
                'linear': {
                    'scale': 'linear_unit',
                }
            }
        elif self.tonemap_type == 'camera':
            if self.camera_response_type == 'preset':
                crf = [self.camera_response_preset]
            elif self.camera_response_file!="" and os.path.exists(efutil.filesystem_path(self.camera_response_file)):
                crf = 'camera_response_file'
            else:
                indigo_log('WARNING: Invalid camera tonemapping, using default dscs315.txt')
                crf = ['data/camera_response_functions/dscs315.txt']
            xml_format = {
                'camera': {
                    'response_function_path': crf,
                    'ev_adjust': 'camera_ev',
                    'film_iso': [scene.camera.data.indigo_camera.iso]
                }
            }
        elif self.tonemap_type == 'filmic':
            xml_format = {
                'filmic': {
                    'scale': 'filmic_scale',
                }
            }
        else:
            xml_format = {}
        
        self.build_subelements(scene, xml_format, xml)
        
        return xml