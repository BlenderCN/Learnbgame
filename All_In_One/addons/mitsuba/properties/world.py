# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

from .. import MitsubaAddon
from copy import deepcopy

from extensions_framework import declarative_property_group

from ..properties.texture import (ColorTextureParameter,BumpTextureParameter,SpectrumTextureParameter, FloatTextureParameter)
from ..export import ParamSet

param_scattCoeff = SpectrumTextureParameter('sigmaS', 'Scattering Coefficient', 'Scattering value', default=(0.8, 0.8, 0.8))
param_absorptionCoefficient = SpectrumTextureParameter('sigmaA', 'Absorption Coefficient', 'Absorption value', default=(0.0, 0.0, 0.0))
param_extinctionCoeff = SpectrumTextureParameter('sigmaT', 'Extinction Coefficient', 'Extinction value', default=(0.8, 0.8, 0.8))
param_albedo = SpectrumTextureParameter('albedo', 'Albedo', 'Albedo value', default=(0.01, 0.01, 0.01))

def dict_merge(*args):
	vis = {}
	for vis_dict in args:
		vis.update(deepcopy(vis_dict))
	return vis

def texture_append_visibility(vis_main, textureparam_object, vis_append):
	for prop in textureparam_object.properties:
		if 'attr' in prop.keys():
			if not prop['attr'] in vis_main.keys():
				vis_main[prop['attr']] = {}
			for vk, vi in vis_append.items():
				vis_main[prop['attr']][vk] = vi
	return vis_main

def MediumParameter(attr, name):
	return [
		{
			'attr': '%s_medium' % attr,
			'type': 'string',
			'name': '%s_medium' % attr,
			'description': '%s medium; blank means vacuum' % attr,
			'save_in_preset': True
		},
		{
			'type': 'prop_search',
			'attr': attr,
			'src': lambda s,c: s.scene.mitsuba_media,
			'src_attr': 'media',
			'trg': lambda s,c: c.mitsuba_mat_medium,
			'trg_attr': '%s_medium' % attr,
			'name': name
		}
	]

@MitsubaAddon.addon_register_class
class mitsuba_medium_data(declarative_property_group):
	'''
	Storage class for Mitsuba medium data. The
	mitsuba_media object will store 1 or more of
	these in its CollectionProperty 'media'.
	'''
	
	ef_attach_to = []	
	
	controls = [
		'type',
		'metode',
		'material',
		'g',
		'useAlbSigmaT'
	] + \
		param_absorptionCoefficient.controls + \
		param_scattCoeff.controls + \
		param_extinctionCoeff.controls + \
		param_albedo.controls + \
	[
		'scale',
		'externalDensity',
		'density',			
		'object_pop',			 
		[ 0.9, [0.375,'albado_colorlabel', 'albado_color'], 'albedo_usegridvolume'],
		'albedo_gridVolumeType',	
		'convert',
	]	
	
	properties = [
		{
			'type': 'enum',
			'attr': 'type',
			'name': 'Type',
			'items': [
				('homogeneous', 'Homogeneous', 'homogeneous'),
				('heterogeneous', 'Heterogeneous', 'heterogeneous'),
			],
			'save_in_preset': True
		},
		{																		
			'type': 'string',
			'attr': 'material',
			'name': 'Preset name',
			'description' : 'Name of a material preset (def Ketchup; skin1, marble, potato, chicken1, apple)',
			'default': '',
			'save_in_preset': True
		},
		{																		
			'type': 'enum',
			'attr': 'metode',
			'name': 'Metode',
			'items': [
				('woodcock', 'Woodcock', 'woodcock'),
				('simpson', 'Simpson', 'simpson'),				
			],
			'save_in_preset': True
		},		
		{
			'type': 'string',
			'subtype': 'FILE_PATH',
			'attr': 'density',
			'name': 'Density file',
			'description': 'Path to a grid volume density file (.vol)'
		},				
		{
			'attr': 'object' ,
			'type': 'string',
			'name': 'object',
			'description': 'Object of Domain type ' ,
			'save_in_preset': True
		},
		{
			'type': 'prop_search',
			'attr': 'object_pop',
			'src': lambda s,c: s.scene,
			'src_attr': 'objects',
			'trg': lambda s,c: c,			
			'trg_attr': 'object' ,
			'name': 'Objects'
		},		
		{		
			'type': 'float',
			'attr': 'g',
			'name': 'Asymmetry',
			'description': 'Scattering asymmetry RGB. -1 means back-scattering, 0 is isotropic, 1 is forwards scattering.',
			'default': 0.0,
			'min': -1.0,
			'soft_min': -1.0,
			'max': 1.0,
			'soft_max': 1.0,
			'precision': 4,
			'save_in_preset': True
		},
		{
			'type': 'text',
			'attr': 'albado_colorlabel' ,
			'name': 'Albado'
		},
		{
			'type': 'float_vector',
			'attr': 'albado_color' ,
			'name': '', #self.name,
			'description': 'The color for the albado ',
			'default': (0.01, 0.01, 0.01),
			'min': 0.0,
			'soft_min': 0.0,
			'max': 1.0,
			'soft_max': 1.0,
			'subtype': 'COLOR',
			'save_in_preset': True
		},
		{			
			'type': 'bool',
			'attr': 'useAlbSigmaT',
			'name': 'Use Albedo&SigmaT',
			'description': 'Use Albedo&SigmaT instead SigmatS&SigmaA',
			'default': False,
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'scale',
			'name' : 'Scale',
			'description' : 'Density scale',
			'default' : 1.0,
			'min': 0.1,
			'max': 50000.0,
			'save_in_preset': True
		},
		{
			'attr': 'albedo_usegridvolume',
			'type': 'bool',
			'name': 'H',
			'description': 'Coloring the texture by heat',
			'default': False,
			'toggle': True,
			'save_in_preset': True
		},
		{
			'type': 'enum',
			'attr': 'albedo_gridVolumeType',
			'name': 'Type',
			'items': [
				('heat', 'Heat', 'heat'),				
			],
			'save_in_preset': True
		},
		{
			'type': 'bool',
			'attr': 'externalDensity',
			'name' : 'External Density',			
			'default' : False,			
			'save_in_preset': True
		},
	] + \
		param_absorptionCoefficient.properties + \
		param_scattCoeff.properties + \
		param_extinctionCoeff.properties + \
		param_albedo.properties  
	
	visibility = dict_merge(
		{ 'useAlbSigmaT': { 'material': '' , 'type' : 'homogeneous'}  },
		{ 'material' : {'type' : 'homogeneous'} },		
		{ 'metode' : {'type' : 'heterogeneous'} },		
		{ 'density' : {'type' : 'heterogeneous' , 'externalDensity' : True} },
		{ 'albado_color' : {'type' : 'heterogeneous'} },
		{ 'externalDensity' : {'type' : 'heterogeneous'} },
		{ 'albado_colorlabel' : {'type' : 'heterogeneous'} },
		{ 'albedo_usegridvolume' : {'type' : 'heterogeneous'} },
		{ 'object_pop' : {'type' : 'heterogeneous' , 'externalDensity' : False } },
		{'albedo_gridVolumeType' : {'type' : 'heterogeneous', 'albedo_usegridvolume' : True} },		
		param_absorptionCoefficient.visibility,
		param_scattCoeff.visibility,
		param_extinctionCoeff.visibility,
		param_albedo.visibility
	)
	
	visibility = texture_append_visibility(visibility, param_extinctionCoeff, { 'material': '', 'useAlbSigmaT': True , 'type' : 'homogeneous'})
	visibility = texture_append_visibility(visibility, param_albedo, { 'material': '', 'useAlbSigmaT': True , 'type' : 'homogeneous' })	
	visibility = texture_append_visibility(visibility, param_scattCoeff, { 'material': '', 'useAlbSigmaT': False ,'type' : 'homogeneous'})
	visibility = texture_append_visibility(visibility, param_absorptionCoefficient, { 'material': '', 'useAlbSigmaT': False ,'type' : 'homogeneous'})
	
	def get_params(self):
		params = ParamSet()
		if self.material=='':
			if self.useAlbSigmaT != True:
				params.update(param_absorptionCoefficient.get_params(self))
				params.update(param_scattCoeff.get_params(self))
			else:
				params.update(param_extinctionCoeff.get_params(self))
				params.update(param_albedo.get_params(self))
		else:
			params.add_string('material', self.material)
		params.add_float('scale', self.scale)
		return params

@MitsubaAddon.addon_register_class
class mitsuba_media(declarative_property_group):
	'''
	Storage class for Mitsuba Material media.
	'''
	
	ef_attach_to = ['Scene']
	
	controls = [
		'media_select',
		['op_vol_add', 'op_vol_rem']
	]
	
	visibility = {}
	
	properties = [
		{
			'type': 'collection',
			'ptype': mitsuba_medium_data,
			'name': 'media',
			'attr': 'media',
			'items': [
				
			]
		},
		{
			'type': 'int',
			'name': 'media_index',
			'attr': 'media_index',
		},
		{
			'type': 'template_list',
			'name': 'media_select',
			'attr': 'media_select',
			'trg': lambda sc,c: c.mitsuba_media,
			'trg_attr': 'media_index',
			'src': lambda sc,c: c.mitsuba_media,
			'src_attr': 'media',
		},
		{
			'type': 'operator',
			'attr': 'op_vol_add',
			'operator': 'mitsuba.medium_add',
			'text': 'Add',
			'icon': 'ZOOMIN',
		},
		{
			'type': 'operator',
			'attr': 'op_vol_rem',
			'operator': 'mitsuba.medium_remove',
			'text': 'Remove',
			'icon': 'ZOOMOUT',
		},
	]
