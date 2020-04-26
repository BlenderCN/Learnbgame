import re, os, zipfile
from copy import deepcopy

import bpy        #@UnresolvedImport
import xml.etree.cElementTree as ET

#from indigo import IndigoAddon
from . material import MaterialChannel


Cha_Medium  = MaterialChannel('medium_type', spectrum=True, texture=True,  shader=True,  switch=False, spectrum_types={'rgb':True, 'rgbgain':True, 'uniform':True, 'blackbody': True, 'rgb_default':(0.0,0.0,0.0)}, label='Medium Settings')

Med_SSS_Scatter = MaterialChannel('sss_scatter', spectrum=True, texture=False, shader=False, switch=False, spectrum_types={'rgb':True, 'rgbgain':True, 'uniform':True})
Med_SSS_Phase = MaterialChannel('sss_phase_hg', spectrum=True, texture=False, shader=False, switch=False, spectrum_types={'rgb':True, 'rgbgain':True, 'uniform':True})
Med_Medium_Basic = MaterialChannel('medium_type', spectrum=True, texture=False, shader=False, switch=False, spectrum_types={'rgb':True, 'rgbgain':True, 'uniform':True}, master_colour=True)

#from .. import export
from . import register_properties_dict
    
@register_properties_dict
class Indigo_Material_Medium_Data_Properties(bpy.types.PropertyGroup):
    properties = [
        {
            'type': 'string',
            'attr': 'name',
            'name': ''
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
        {
            'type': 'enum',
            'attr': 'medium_type',
            'name': 'Medium Type',
            'description': 'Medium Type',
            'default': 'basic',
            'items': [
                ('basic', 'Basic', 'basic'),
                ('dermis', 'Dermis', 'dermis'),
                ('epidermis', 'Epidermis', 'epidermis'),
              #  ('atmosphere', 'Atmosphere', 'atmosphere'),
            ]
        },
        {
            'type': 'bool',
            'attr': 'sss',
            'name': 'Subsurface scattering',
            'description': 'SSS',
            'default': False,
        },
        {
            'type': 'bool',
            'attr': 'fast_sss',
            'name': 'Fast SSS',
            'description': 'Enable fast SSS',
            'default': False,
        },
        {
            'type': 'enum',
            'attr': 'sss_phase_function',
            'name': 'Phase Function',
            'description': 'Phase Function',
            'default': 'uniform',
            'items': [
                ('uniform', 'Uniform', 'uniform'),
                ('hg', 'Henyey Greenstein', 'hg')
            ]
        },
        {
            'type': 'float',
            'attr': 'medium_ior',
            'name': 'IOR',
            'description': 'IOR',
            'slider': True,
            'default': 1.5,
            'min': 0.0,
            'max': 20.0,
            'precision': 6
        },
        {
            'type': 'float',
            'attr': 'medium_cauchy_b',
            'name': 'Cauchy B',
            'description': 'Cauchy B',
            'default': 0.0,
            'slider': True,
            'min': 0.0,
            'max': 1.0,
            'precision': 6
        },
        {
            'type': 'float',
            'attr': 'medium_haemoglobin',
            'name': 'Haemoglobin',
            'description': 'Haemoglobin',
            'slider': True,
            'default': 0.001,
            'min': 0.0,
            'max': 1.0
        },
        {
            'type': 'float',
            'attr': 'medium_melanin',
            'name': 'Melanin',
            'description': 'Melanin',
            'slider': True,
            'default': 0.15,
            'min': 0.0,
            'max': 1.0
        },
        {
            'type': 'float',
            'attr': 'medium_eumelanin',
            'name': 'Eumelanin',
            'description': 'Eumelanin',
            'slider': True,
            'default': 0.001,
            'min': 0.0,
            'max': 1.0
        },
        {
            'type': 'float',
            'attr': 'medium_turbidity',
            'name': 'Turbidity',
            'description': 'Turbidity',
            'slider': True,
            'default': 2.2,
            'min': 1.0,
            'max': 10.0
        },
        {
            'type': 'string',
            'attr': 'center',
            'name': 'center'
        },
        {
            'type': 'float',
            'attr': 'medium_posx',
            'name': 'X:',
            'description': 'Position X',
            'default': 0,
            'min': 0.0,
            'max': 360.0
        },
        {
            'type': 'float',
            'attr': 'medium_posy',
            'name': 'Y:',
            'description': 'Position Y',
            'default': 0,
            'min': 0.0,
            'max': 360.0
        },
        {
            'type': 'float',
            'attr': 'medium_posz',
            'name': 'Z',
            'description': 'Position Z',
            'default': 0,
            'min': 0.0,
            'max': 360.0
        },
    ] + Cha_Medium.properties    + \
        Med_Medium_Basic.properties + \
        Med_SSS_Scatter.properties + \
        Med_SSS_Phase.properties
        
    
@register_properties_dict
class Indigo_Material_Medium_Properties(bpy.types.PropertyGroup):
    properties = [
        {
            'type': 'collection',
            'ptype': Indigo_Material_Medium_Data_Properties,
            'name': 'medium',
            'attr': 'medium',
            'items': []
        },
        {
            'type': 'int',
            'name': 'medium_index',
            'attr': 'medium_index',
        },
         {
            'type': 'template_list',
            'listtype_name': 'UI_UL_list',
            'list_id': 'mediumlist',
            'name': 'medium_select',
            'attr': 'medium_select',
            'trg': lambda s, c: s.scene.indigo_material_medium,
            'trg_attr': 'medium_index',
            'src': lambda s, c: s.scene.indigo_material_medium,
            'src_attr': 'medium',
        },
        {
            'type': 'operator',
            'attr': 'op_me_add',
            'operator': 'indigo.medium_add',
            'text': 'Add',
            'icon': 'ZOOMIN',
        },
        {
            'type': 'operator',
            'attr': 'op_me_remove',
            'operator': 'indigo.medium_remove',
            'text': 'Remove',
            'icon': 'ZOOMOUT',
        },
    ]
    
    
    def enumerate(self):
        en = {
            'default': 0,
        }
        idx = 1
        for name, me in lambda s,c: s.scene.indigo_material_medium.items():
              en[name] = idx
              idx += 1
        return en