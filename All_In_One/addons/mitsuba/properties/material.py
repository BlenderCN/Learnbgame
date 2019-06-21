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

import bpy, math
from copy import deepcopy

from .. import MitsubaAddon

from extensions_framework import declarative_property_group
from extensions_framework import util as efutil
from extensions_framework.validate import Logic_OR as O, Logic_Operator as LO
from ..properties.texture import (ColorTextureParameter,BumpTextureParameter,SpectrumTextureParameter, FloatTextureParameter)
from ..export import ParamSet
from ..outputs import MtsLog

from ..properties.world import MediumParameter

class BoolParameter(object):
	name				= None
	default				= False
	attr 				= None
	controls			= None
	visibility			= None
	properties			= None
	
	
	def __init__(self,attr, name, description, default = False):
		self.name = name 
		self.attr = attr
		self.default = default
		self.description = description
		
		self.controls = self.get_controls()
		self.visibility = self.get_visibility()
		self.properties = self.get_properties()
		
	def get_controls(self):
		return [ self.attr ]
	
	def get_properties(self):
		return [
			{
				'type': 'bool',
				'attr': '%s' %self.attr,
				'name': '%s' %self.name,
				'description' : '%s' %self.description,
				'default': self.default,
				'save_in_preset': True
			}
			]
	def get_visibility(self):
		return None




param_reflectance = ColorTextureParameter('reflectance', 'Reflectance', 'Diffuse reflectance value', default=(0.5, 0.5, 0.5))
param_transmittance = ColorTextureParameter('transmittance', 'Diffuse Transmittance', 'Diffuse transmittance value', default=(0.5, 0.5, 0.5))
param_opacityMask = ColorTextureParameter('opacity', 'Opacity Mask', 'Opacity mask value', default=(0.5, 0.5, 0.5))
param_diffuseReflectance = ColorTextureParameter('diffuseReflectance', 'Diffuse Reflectance', 'Diffuse reflectance value', default=(0.5, 0.5, 0.5))
param_specularReflectance = ColorTextureParameter('specularReflectance', 'Specular Reflectance', 'Specular reflectance value', default=(1.0, 1.0, 1.0))
param_specularTransmittance = ColorTextureParameter('specularTransmittance', 'Specular Transmittance', 'Specular transmittance value', default=(1.0, 1.0, 1.0)) # fixes only 'specularTransmittance' to long name error 
param_bumpHeight = BumpTextureParameter('bump', 'Bump Texture', 'Bump height texture', default=1.0)
param_scattCoeff = SpectrumTextureParameter('sigmaS', 'Scattering Coefficient', 'Scattering value', default=(0.8, 0.8, 0.8))
param_absorptionCoefficient = SpectrumTextureParameter('sigmaA', 'Absorption Coefficient', 'Absorption value', default=(0.0, 0.0, 0.0))
param_extinctionCoeff = SpectrumTextureParameter('sigmaT', 'Extinction Coefficient', 'Extinction value', default=(0.8, 0.8, 0.8))
param_albedo = SpectrumTextureParameter('albedo', 'Albedo', 'Albedo value', default=(0.01, 0.01, 0.01))
param_alphaRoughness = FloatTextureParameter('alpha', 'Roughness', 'Roughness value', default=0.2)
param_alphaRoughnessU = FloatTextureParameter('alphaU', 'Roughness U', 'Anisotropic roughness tangent value', default=0.1)
param_alphaRoughnessV = FloatTextureParameter('alphaV', 'Roughness V', 'Anisotropic roughness bitangent value', default=0.1)
param_phongExponent = FloatTextureParameter('exponent', 'Exponent', 'Phong Exponent', default=30, max=1000)
param_weightBlend = FloatTextureParameter('weight', 'Factor', 'Blending factor', default=0.2)
param_useTwoSidedMatherials = BoolParameter('use_two_sided_bsdf','Use Two Sided BSDF','This parameter selects between using the same material for both sides or not',default=False)

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

@MitsubaAddon.addon_register_class
class mitsuba_mat_bsdf(declarative_property_group):
	'''
	Storage class for Mitsuba Material settings.
	This class will be instantiated within a Blender Material
	object.
	'''
	
	ef_attach_to = ['Material']
	
	controls = [
		'type'
	]
	
	properties = [
		{
			'type': 'bool',
			'attr': 'use_bsdf',
			'name': 'Use BSDF',
			'default': True,
			'save_in_preset': True
		},
		{
			'type': 'enum',
			'attr': 'type',
			'name': 'Type',
			'description': 'Specifes the type of BSDF material',
			'items': [
				('diffuse', 'Diffuse', 'diffuse'),
				('dielectric', 'Dielectric', 'dielectric'),
				('conductor', 'Conductor', 'conductor'),
				('plastic', 'Plastic', 'plastic'),
				('coating', 'Dielectric coating', 'coating'),
				('bump', 'Bump map modifier', 'bump'),
				('phong','Modified Phong BRDF', 'phong'),
				('ward', 'Anisotropic Ward BRDF', 'ward'),
				('mixturebsdf', 'Mixture material', 'mixturebsdf'),
				('blendbsdf', 'Blended material', 'blendbsdf'),
				('mask', 'Opacity mask', 'mask'),
				('twosided', 'Two-sided BRDF adapter', 'twosided'),
				('irawan','Irawan & Marschner Woven cloth BRDF', 'irawan'),
				('hk', 'Hanrahan-Krueger BSDF', 'hk'),
				('difftrans', 'Diffuse transmitter', 'difftrans'),
				('none', 'Passthrough material', 'none')
			],
			'default': 'diffuse',
			'save_in_preset': True
		}
	]
	
	def get_params(self):
		sub_type = getattr(self, 'mitsuba_bsdf_%s' % self.type)
		return sub_type.get_params()

@MitsubaAddon.addon_register_class
class mitsuba_bsdf_diffuse(declarative_property_group):	
	ef_attach_to = ['mitsuba_mat_bsdf']
		
	controls = param_reflectance.controls + \
		param_alphaRoughness.controls + \
		param_useTwoSidedMatherials.controls + \
	[
		'useFastApprox'
	] 
	
	properties = [
		{
			'type': 'bool',
			'attr': 'useFastApprox',
			'name': 'Use Fast Approximation',
			'description' : 'This parameter selects between the full version of the model or a fast approximation',
			'default': False,
			'save_in_preset': True
		}
		
	] + \
	param_useTwoSidedMatherials.properties + \
	param_reflectance.properties + \
	param_alphaRoughness.properties
	
	
	visibility = dict_merge(
		param_reflectance.visibility,
		param_alphaRoughness.visibility
	)
	
	def get_params(self):
		params = ParamSet()		
		params.update(param_reflectance.get_params(self))
		if self.alpha > 0 or (self.alpha_usetexture and self.alpha_texturename != ''):
			params.update(param_alphaRoughness.get_params(self))
			params.add_bool('useFastApprox', self.useFastApprox)
		return params

@MitsubaAddon.addon_register_class
class mitsuba_bsdf_dielectric(declarative_property_group):
	ef_attach_to = ['mitsuba_mat_bsdf']
	
	controls = [
		'thin',
		['intIOR', 'extIOR']
	] + \
		param_specularReflectance.controls + \
		param_specularTransmittance.controls + \
	[
		'distribution'
	] + \
		param_alphaRoughness.controls + \
		param_alphaRoughnessU.controls + \
		param_alphaRoughnessV.controls
	
	properties = [
		{
			'type': 'enum',
			'attr': 'distribution',
			'name': 'Roughness Model',
			'description': 'Specifes the type of microfacet normal distribution used to model the surface roughness',
			'items': [
				('none', 'None', 'none'),
				('beckmann', 'Beckmann', 'beckmann'),
				('ggx', 'Ggx', 'ggx'),
				('phong', 'Phong', 'phong'),
				('as', 'Anisotropic', 'as')
			],
			'default': 'none',
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'intIOR',
			'name' : 'Int. IOR',
			'description' : 'Interior index of refraction (e.g. air=1, glass=1.5 approximately)',
			'default' : 1.5,
			'min': 1.0,
			'max': 10.0,
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'extIOR',
			'name' : 'Ext. IOR',
			'description' : 'Exterior index of refraction (e.g. air=1, glass=1.5 approximately)',
			'default' : 1,
			'min': 1.0,
			'max': 10.0,
			'save_in_preset': True
		},
		{
			'type': 'bool',
			'attr': 'thin',
			'name': 'Thin Dielectric',
			'description': 'If set to true, thin dielectric material that is embedded inside another dielectri will be used (e.g. glass surrounded by air).',
			'default': False,
			'save_in_preset': True
		}
	] + \
		param_specularReflectance.properties + \
		param_specularTransmittance.properties + \
		param_alphaRoughness.properties + \
		param_alphaRoughnessU.properties + \
		param_alphaRoughnessV.properties
	
	visibility = dict_merge(
		{
			'distribution' : {'thin' : False}
		},
		param_specularReflectance.visibility,
		param_specularTransmittance.visibility,
		param_alphaRoughness.visibility,
		param_alphaRoughnessU.visibility,
		param_alphaRoughnessV.visibility
	)
	visibility = texture_append_visibility(visibility, param_alphaRoughness, { 'thin' : False, 'distribution' : O(['beckmann','ggx','phong'])})
	visibility = texture_append_visibility(visibility, param_alphaRoughnessU, { 'thin' : False, 'distribution' : 'as'})
	visibility = texture_append_visibility(visibility, param_alphaRoughnessV, { 'thin' : False, 'distribution' : 'as'})
	
	def get_params(self):
		params = ParamSet()
		params.add_float('intIOR', self.intIOR)
		params.add_float('extIOR', self.extIOR)
		params.update(param_specularReflectance.get_params(self))
		params.update(param_specularTransmittance.get_params(self))
		if self.distribution != 'none' and not self.thin:
			params.add_string('distribution', self.distribution)
			if (self.distribution == 'as'):
				params.update(param_alphaRoughnessU.get_params(self))
				params.update(param_alphaRoughnessV.get_params(self))
			else:
				params.update(param_alphaRoughness.get_params(self))
		return params

@MitsubaAddon.addon_register_class
class mitsuba_bsdf_conductor(declarative_property_group):
	ef_attach_to = ['mitsuba_mat_bsdf']
	
	controls = [
		'material',
		'eta', 'k',
		'extEta'
	] + \
		param_specularReflectance.controls + \
	[
		'distribution'
	] + \
		param_alphaRoughness.controls + \
		param_alphaRoughnessU.controls + \
		param_useTwoSidedMatherials.controls + \
		param_alphaRoughnessV.controls
	
	properties = [
		{
			'type': 'enum',
			'attr': 'distribution',
			'name': 'Roughness Model',
			'description': 'Specifes the type of microfacet normal distribution used to model the surface roughness',
			'items': [
				('none', 'None', 'none'),
				('beckmann', 'Beckmann', 'beckmann'),
				('ggx', 'Ggx', 'ggx'),
				('phong', 'Phong', 'phong'),
				('as', 'Anisotropic', 'as')
			],
			'default': 'none',
			'save_in_preset': True
		},
		{
			'type': 'string',
			'attr': 'material',
			'name': 'Material Name',
			'description' : 'Name of a material preset (Cu=copper)',
			'default': '',
			'save_in_preset': True
		},
		{
			'type': 'float_vector',
			'attr': 'eta',
			'name' : 'IOR',
			'description' : 'Per-channel index of refraction of the conductor (real part)',
			'default' : (0.370, 0.370, 0.370),
			'min': 0.1,
			'max': 10.0,
			'expand' : False,
			'save_in_preset': True
		},
		{
			'type': 'float_vector',
			'attr': 'k',
			'name' : 'Absorption Coefficient',
			'description' : 'Per-channel absorption coefficient of the conductor (imaginary part)',
			'default' : (2.820, 2.820, 2.820),
			'min': 1.0,
			'max': 10.0,
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'extEta',
			'name' : 'Ext. Eta',
			'description' : 'Index of refraction of the surrounding dielectric (e.g. air=1, glass=1.5 approximately)',
			'default' : 1,
			'min': 1.0,
			'max': 10.0,
			'save_in_preset': True
		}
	] + \
		param_specularReflectance.properties + \
		param_alphaRoughness.properties + \
		param_alphaRoughnessU.properties + \
		param_useTwoSidedMatherials.properties + \
		param_alphaRoughnessV.properties
	
	visibility = dict_merge(
		{
			'eta' : { 'material' : '' },
			'k' : { 'material' : '' }
		},
		param_specularReflectance.visibility,
		param_alphaRoughness.visibility,
		param_alphaRoughnessU.visibility,
		param_alphaRoughnessV.visibility
	)
	visibility = texture_append_visibility(visibility, param_alphaRoughness, { 'distribution' : O(['beckmann','ggx','phong'])})
	visibility = texture_append_visibility(visibility, param_alphaRoughnessU, { 'distribution' : 'as'})
	visibility = texture_append_visibility(visibility, param_alphaRoughnessV, { 'distribution' : 'as'})
	
	def get_params(self):
		params = ParamSet()
		if self.material=='':
			params.add_color('eta', self.eta)
			params.add_color('k', self.k)
		else:
			params.add_string('material', self.material)
		params.add_float('extEta', self.extEta)
		params.update(param_specularReflectance.get_params(self))
		if self.distribution != 'none':
			params.add_string('distribution', self.distribution)
			if (self.distribution == 'as'):
				params.update(param_alphaRoughnessU.get_params(self))
				params.update(param_alphaRoughnessV.get_params(self))
			else:
				params.update(param_alphaRoughness.get_params(self))
		return params

@MitsubaAddon.addon_register_class
class mitsuba_bsdf_plastic(declarative_property_group):
	ef_attach_to = ['mitsuba_mat_bsdf']
	
	controls = [
		['intIOR', 'extIOR']
	] + \
		param_diffuseReflectance.controls + \
		param_specularReflectance.controls + \
	[
		'nonlinear',
		'distribution'
	] + \
		param_useTwoSidedMatherials.controls + \
		param_alphaRoughness.controls
	
	properties = [
		{
			'type': 'enum',
			'attr': 'distribution',
			'name': 'Roughness Model',
			'description': 'Specifes the type of microfacet normal distribution used to model the surface roughness',
			'items': [
				('none', 'None', 'none'),
				('beckmann', 'Beckmann', 'beckmann'),
				('ggx', 'Ggx', 'ggx'),
				('phong', 'Phong', 'phong')
			],
			'default': 'none',
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'intIOR',
			'name' : 'Int. IOR',
			'description' : 'Interior index of refraction (e.g. air=1, glass=1.5 approximately)',
			'default' : 1.5,
			'min': 1.0,
			'max': 10.0,
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'extIOR',
			'name' : 'Ext. IOR',
			'description' : 'Exterior index of refraction (e.g. air=1, glass=1.5 approximately)',
			'default' : 1,
			'min': 1.0,
			'max': 10.0,
			'save_in_preset': True
		},
		{			
			'type': 'bool',
			'attr': 'nonlinear',
			'name': 'Use Internal Scattering',
			'description': 'Support for nonlinear color shifs',
			'default': False,
			'save_in_preset': True
		}
	] + \
		param_diffuseReflectance.properties + \
		param_specularReflectance.properties + \
		param_useTwoSidedMatherials.properties + \
		param_alphaRoughness.properties
	
	visibility = dict_merge(
		param_diffuseReflectance.visibility,
		param_specularReflectance.visibility,
		param_alphaRoughness.visibility
	)
	visibility = texture_append_visibility(visibility, param_alphaRoughness, { 'distribution' : O(['beckmann','ggx','phong'])})
	
	def get_params(self):
		params = ParamSet()
		params.add_float('intIOR', self.intIOR)
		params.add_float('extIOR', self.extIOR)
		params.update(param_diffuseReflectance.get_params(self))
		params.update(param_specularReflectance.get_params(self))
		if self.distribution != 'none':
			params.add_string('distribution', self.distribution)
			params.update(param_alphaRoughness.get_params(self))
		params.add_bool('nonlinear', self.nonlinear)
		return params

def CoatingProperty():
	return [
		{
			'type': 'string',
			'attr': 'ref_name',
			'name': 'Material Reference Name',
			'description': 'Coated Material',
			'save_in_preset': True
		},
		{
			'type': 'prop_search',
			'attr': 'mat_list',
			'src': lambda s,c: s.object,
			'src_attr': 'material_slots',
			'trg': lambda s,c: c.mitsuba_bsdf_coating,
			'trg_attr': 'ref_name',
			'name': 'Coated Material'
		}
	]

@MitsubaAddon.addon_register_class
class mitsuba_bsdf_coating(declarative_property_group):
	ef_attach_to = ['mitsuba_mat_bsdf']
	
	controls = [
		'mat_list',
		['intIOR', 'extIOR'],
		'thickness'
	] + \
		param_absorptionCoefficient.controls + \
	[
		'distribution'
	] + \
	param_useTwoSidedMatherials.controls + \
	param_alphaRoughness.controls
	
	properties = [
		{
			'type': 'enum',
			'attr': 'distribution',
			'name': 'Roughness Model',
			'description': 'Specifes the type of microfacet normal distribution used to model the surface roughness',
			'items': [
				('none', 'None', 'none'),
				('beckmann', 'Beckmann', 'beckmann'),
				('ggx', 'Ggx', 'ggx'),
				('phong', 'Phong', 'phong')
			],
			'default': 'none',
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'thickness',
			'name' : 'Thickness',
			'description' : 'Denotes the thickness of the coating layer',
			'default' : 1.0,
			'min': 0.0,
			'max': 15.0,
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'extIOR',
			'name' : 'Ext. IOR',
			'description' : 'Exterior index of refraction (e.g. air=1, glass=1.5 approximately)',
			'default' : 1,
			'min': 1.0,
			'max': 10.0,
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'intIOR',
			'name' : 'Int. IOR',
			'description' : 'Interior index of refraction (e.g. air=1, glass=1.5 approximately)',
			'default' : 1.5,
			'min': 1.0,
			'max': 10.0,
			'save_in_preset': True
		}
	] + \
		CoatingProperty() + \
		param_absorptionCoefficient.properties + \
		param_useTwoSidedMatherials.properties + \
		param_alphaRoughness.properties
	
	visibility = dict_merge(
		param_absorptionCoefficient.visibility,
		param_alphaRoughness.visibility
	)
	visibility = texture_append_visibility(visibility, param_alphaRoughness, { 'distribution' : O(['beckmann','ggx','phong'])})
	
	def get_params(self):
		params = ParamSet()
		params.add_float('intIOR', self.intIOR)
		params.add_float('extIOR', self.extIOR)
		params.add_float('thickness', self.thickness)
		params.update(param_absorptionCoefficient.get_params(self))
		if self.distribution != 'none':
			params.add_string('distribution', self.distribution)
			params.update(param_alphaRoughness.get_params(self))
		params.add_reference('material', "bsdf", getattr(self, "ref_name"))
		return params

@MitsubaAddon.addon_register_class
class mitsuba_bsdf_phong(declarative_property_group):
	ef_attach_to = ['mitsuba_mat_bsdf']
	
	controls = param_phongExponent.controls + \
		param_diffuseReflectance.controls + \
		param_useTwoSidedMatherials.controls + \
		param_specularReflectance.controls
	
	properties = param_phongExponent.properties + \
		param_diffuseReflectance.properties + \
		param_useTwoSidedMatherials.properties + \
		param_specularReflectance.properties
	
	visibility = dict_merge(
		param_phongExponent.visibility, 
		param_diffuseReflectance.visibility, 
		param_specularReflectance.visibility
	)
	
	def get_params(self):
		params = ParamSet()
		params.update(param_phongExponent.get_params(self))
		params.update(param_diffuseReflectance.get_params(self))
		params.update(param_specularReflectance.get_params(self))
		return params

@MitsubaAddon.addon_register_class
class mitsuba_bsdf_irawan(declarative_property_group):
	ef_attach_to = ['mitsuba_mat_bsdf']
	
	controls = [
		'filename',
		'kdMultiplier',
		'ksMultiplier',
		['repeatU', 'repeatV'],
		'kd',
		'ks',
		'warp_kd',
		'warp_ks',
		'weft_kd',
		'weft_ks'
	]
	
	properties = [
		{
			'type': 'string',
			'subtype': 'FILE_PATH',
			'attr': 'filename',
			'name': 'Cloth Data',
			'description': 'Path to a weave pattern description'
		},
		{
			'type': 'float',
			'attr': 'repeatU',
			'name': 'U Scale',
			'default': 120.0,
			'min': -100.0,
			'soft_min': -100.0,
			'max': 200.0,
			'soft_max': 200.0,
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'repeatV',
			'name': 'V Scale',
			'default': 80.0,
			'min': -100.0,
			'soft_min': -100.0,
			'max': 200.0,
			'soft_max': 200.0,
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'ksMultiplier',
			'description' : 'Multiplicative factor of the specular component',
			'name' : 'ksMultiplier',
			'default' : 4.34,
			'min': 0.0,
			'max': 10.0,
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'kdMultiplier',
			'description' : 'Multiplicative factor of the diffuse component',
			'name' : 'kdMultiplier',
			'default' : 0.00553,
			'min': 0.0,
			'max': 10.0,
			'save_in_preset': True
		},
		{
			'type': 'float_vector',
			'attr': 'kd',
			'subtype': 'COLOR',
			'description' : 'Diffuse color',
			'name' : 'Diffuse color',
			'default' : (0.5, 0.5, 0.5),
			'min': 0.0,
			'max': 1.0,
			'save_in_preset': True
		},
		{
			'type': 'float_vector',
			'attr': 'ks',
			'subtype': 'COLOR',
			'description' : 'Specular color',
			'name' : 'Specular color',
			'default' : (0.5, 0.5, 0.5),
			'min': 0.0,
			'max': 1.0,
			'save_in_preset': True
		},
		{
			'type': 'float_vector',
			'attr': 'warp_kd',
			'subtype': 'COLOR',
			'description' : 'Diffuse color',
			'name' : 'warp_kd',
			'default' : (0.5, 0.5, 0.5),
			'min': 0.0,
			'max': 1.0,
			'save_in_preset': True
		},
		{
			'type': 'float_vector',
			'attr': 'warp_ks',
			'subtype': 'COLOR',
			'description' : 'Specular color',
			'name' : 'warp_ks',
			'default' : (0.5, 0.5, 0.5),
			'min': 0.0,
			'max': 1.0,
			'save_in_preset': True
		},
		{
			'type': 'float_vector',
			'attr': 'weft_kd',
			'subtype': 'COLOR',
			'description' : 'Diffuse color',
			'name' : 'weft_kd',
			'default' : (0.5, 0.5, 0.5),
			'min': 0.0,
			'max': 1.0,
			'save_in_preset': True
		},
		{
			'type': 'float_vector',
			'attr': 'weft_ks',
			'subtype': 'COLOR',
			'description' : 'Specular color',
			'name' : 'weft_ks',
			'default' : (0.5, 0.5, 0.5),
			'min': 0.0,
			'max': 1.0,
			'save_in_preset': True
		}
	]
	
	def get_params(self):
		params = ParamSet()
		#file_relative		= efutil.path_relative_to_export(file_library_path) if obj.library else efutil.path_relative_to_export(file_path)
		params.add_string('filename', efutil.path_relative_to_export(self.filename))
		params.add_float('ksMultiplier', self.ksMultiplier)
		params.add_float('kdMultiplier', self.kdMultiplier)
		params.add_float('repeatU', self.repeatU)
		params.add_float('repeatV', self.repeatV)
		params.add_color('kd', self.kd)
		params.add_color('ks', self.ks)
		params.add_color('warp_kd', self.warp_kd)
		params.add_color('warp_ks', self.warp_ks)
		params.add_color('weft_kd', self.weft_kd)
		params.add_color('weft_ks', self.weft_ks)
		return params

def BumpProperty():
	return [
		{
			'attr': 'ref_name',
			'type': 'string',
			'name': 'Material Reference Name',
			'description': 'Bump Material',
			'save_in_preset': True
		},
		{
			'type': 'prop_search',
			'attr': 'mat_list',
			'src': lambda s,c: s.object,
			'src_attr': 'material_slots',
			'trg': lambda s,c: c.mitsuba_bsdf_bump,
			'trg_attr': 'ref_name',
			'name': 'Bump Material'
		}
	]

@MitsubaAddon.addon_register_class
class mitsuba_bsdf_bump(declarative_property_group):
	ef_attach_to = ['mitsuba_mat_bsdf']
	
	controls = [
		'mat_list'
	] + \
		param_bumpHeight.controls + \
	[
		'scale'
	]
	
	properties = [
		{
			'type': 'float',
			'attr': 'diffuseAmount',
			'name' : 'Diffuse Amount',
			'description' : 'Diffuse reflection lobe multiplier',
			'default' : 0.8,
			'min': 0.0,
			'max': 1.0,
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'scale',
			'name' : 'Strength',
			'description' : 'Bump strength multiplier',
			'default' : 1.0,
			'min': 0.001,
			'max': 100.0,
			'save_in_preset': True
		}
	] + \
		param_bumpHeight.properties + \
		BumpProperty()
	
	def get_params(self):
		params = ParamSet()
		params.update(param_bumpHeight.get_params(self))
		params.add_float('scale', self.scale)
		params.add_reference('material', "bsdf", getattr(self, "ref_name"))
		return params

@MitsubaAddon.addon_register_class
class mitsuba_bsdf_mask(declarative_property_group):
	ef_attach_to = ['mitsuba_mat_bsdf']
	
	controls = [
		'mat_list',
	] + \
		param_opacityMask.controls
	
	properties = [
		{
			'type': 'string',
			'attr': 'ref_name',
			'name': 'Material Reference Name',
			'description': 'Opacity Material',
			'save_in_preset': True
		},
		{
			'type': 'prop_search',
			'attr': 'mat_list',
			'src': lambda s,c: s.object,
			'src_attr': 'material_slots',
			'trg': lambda s,c: c.mitsuba_bsdf_mask,
			'trg_attr': 'ref_name',
			'name': 'Opacity Material'
		}
	] + \
		param_opacityMask.properties 
	
	visibility = param_opacityMask.visibility 
	
	def get_params(self):
		params = ParamSet()
		params.update(param_opacityMask.get_params(self))
		params.add_reference('material', "bsdf", getattr(self, "ref_name"))
		return params

@MitsubaAddon.addon_register_class
class mitsuba_bsdf_hk(declarative_property_group):
	ef_attach_to = ['mitsuba_mat_bsdf']
	
	controls = [
		'material',
		'useAlbSigmaT'
	] + \
		param_scattCoeff.controls + \
		param_absorptionCoefficient.controls + \
		param_extinctionCoeff.controls + \
		param_albedo.controls + \
	[
		'thickness',
		'g'
	]
	
	properties = [
		{
			'type': 'string',
			'attr': 'material',
			'name': 'Material Name',
			'description' : 'Name of a material preset (def Ketchup; skin1, marble, potato, chicken1, apple)',
			'default': '',
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
			'attr': 'thickness',
			'type': 'float',
			'name' : 'Thickness',
			'description' : 'Denotes the thickness of the layer',
			'default' : 1,
			'min': 0.0,
			'max': 20.0,
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'g',
			'name' : 'Phase Function',
			'description' : 'Phase function',
			'default' : 0.0,
			'min': -0.999999,
			'max': 0.999999,
			'save_in_preset': True
		}
	] + \
		param_absorptionCoefficient.properties + \
		param_scattCoeff.properties + \
		param_extinctionCoeff.properties + \
		param_albedo.properties
	
	visibility = dict_merge(
		{
			'useAlbSigmaT': { 'material': '' }
		},
		param_absorptionCoefficient.visibility,
		param_scattCoeff.visibility,
		param_extinctionCoeff.visibility,
		param_albedo.visibility
	)
	
	visibility = texture_append_visibility(visibility, param_absorptionCoefficient, { 'material': '', 'useAlbSigmaT': False })
	visibility = texture_append_visibility(visibility, param_scattCoeff, { 'material': '', 'useAlbSigmaT': False })
	visibility = texture_append_visibility(visibility, param_extinctionCoeff, { 'material': '', 'useAlbSigmaT': True })
	visibility = texture_append_visibility(visibility, param_albedo, { 'material': '', 'useAlbSigmaT': True })
	
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
		params.add_float('thickness', self.thickness)
		params.add_float('g', self.g)
		return params

@MitsubaAddon.addon_register_class
class mitsuba_bsdf_ward(declarative_property_group):
	ef_attach_to = ['mitsuba_mat_bsdf']
	
	controls = [
		'variant'
	] + \
		param_alphaRoughnessU.controls + \
		param_alphaRoughnessV.controls + \
		param_diffuseReflectance.controls + \
		param_useTwoSidedMatherials.controls + \
		param_specularReflectance.controls
	
	properties = [
		{
			'type': 'enum',
			'attr': 'variant',
			'name': 'Ward Model',
			'description': 'Determines the variant of the Ward model tou se',
			'items': [
				('ward', 'Ward', 'ward'),
				('ward-duer', 'Ward-duer', 'ward-duer'),
				('balanced', 'Balanced', 'balanced')
			],
			'default': 'balanced',
			'save_in_preset': True
		}
	] + \
		param_alphaRoughnessU.properties + \
		param_alphaRoughnessV.properties + \
		param_diffuseReflectance.properties + \
		param_useTwoSidedMatherials.properties + \
		param_specularReflectance.properties
	
	visibility = dict_merge(
		param_alphaRoughnessU.visibility,
		param_alphaRoughnessV.visibility,
		param_diffuseReflectance.visibility,
		param_specularReflectance.visibility
	)
	
	def get_params(self):
		params = ParamSet()
		params.update(param_diffuseReflectance.get_params(self))
		params.update(param_specularReflectance.get_params(self))
		params.update(param_alphaRoughnessU.get_params(self))
		params.update(param_alphaRoughnessV.get_params(self))
		params.add_string('variant', self.variant)
		return params

@MitsubaAddon.addon_register_class
class mitsuba_bsdf_difftrans(declarative_property_group):
	ef_attach_to = ['mitsuba_mat_bsdf']
	
	controls = param_transmittance.controls
	
	properties = param_transmittance.properties
	
	visibility = param_transmittance.visibility
	
	def get_params(self):
		params = ParamSet()
		params.update(param_transmittance.get_params(self))
		return params

class WeightedMaterialParameter:
	def __init__(self, name, readableName, propertyGroup):
		self.name = name
		self.readableName = readableName
		self.propertyGroup = propertyGroup
	
	def get_controls(self):
		return [ ['%s_material' % self.name, .7, '%s_weight' % self.name ]]
	
	def get_properties(self):
		return [
			{
				'type': 'string',
				'attr': '%s_name' % self.name,
				'name': '%s material name' % self.name,
				'save_in_preset': True
			},
			{
				'type': 'float',
				'attr': '%s_weight' % self.name,
				'name': 'Weight',
				'min': 0.0,
				'max': 1.0,
				'default' : 0.0,
				'save_in_preset': True
			},
			{
				'type': 'prop_search',
				'attr': '%s_material' % self.name,
				'src': lambda s, c: s.object,
				'src_attr': 'material_slots',
				'trg': lambda s,c: getattr(c, self.propertyGroup),
				'trg_attr': '%s_name' % self.name,
				'name': '%s:' % self.readableName
			}
		]

param_mat = []
for i in range(1, 6):
	param_mat.append(WeightedMaterialParameter("mat%i" % i, "Material %i" % i, "mitsuba_bsdf_mixturebsdf"));

def mitsuba_bsdf_mixturebsdf_visibility():
	result = {}
	for i in range(2, 6):
		result["mat%i_material" % i] = {'nElements' : LO({'gte' : i})}
		result["mat%i_weight" % i] = {'nElements' : LO({'gte' : i})}
	return result

@MitsubaAddon.addon_register_class
class mitsuba_bsdf_mixturebsdf(declarative_property_group):
	ef_attach_to = ['mitsuba_mat_bsdf']
	
	controls = [
		'nElements'
	] + param_useTwoSidedMatherials.controls + \
	 sum(map(lambda x: x.get_controls(), param_mat), [])
	
	properties = [
		{
			'type': 'int',
			'attr': 'nElements',
			'name' : 'Components',
			'description' : 'Number of mixture components',
			'default' : 2,
			'min': 2,
			'max': 5,
			'save_in_preset': True
		}
	] + param_useTwoSidedMatherials.properties + \
	sum(map(lambda x: x.get_properties(), param_mat), [])
	
	visibility = mitsuba_bsdf_mixturebsdf_visibility()
	
	def get_params(self):
		params = ParamSet()
		weights = ""
		for i in range(1,self.nElements+1):
			weights += str(getattr(self, "mat%i_weight" % i)) + " "
			params.add_reference('material', "mat%i" % i, getattr(self, "mat%i_name" % i))
		params.add_string('weights', weights)
		return params

@MitsubaAddon.addon_register_class
class mitsuba_bsdf_blendbsdf(declarative_property_group):
	ef_attach_to = ['mitsuba_mat_bsdf']
	
	controls = param_weightBlend.controls + [
		'mat_list1',
		'mat_list2'
	] + param_useTwoSidedMatherials.controls 
	
	properties = param_weightBlend.properties + [
		{
			'type': 'float',
			'attr': 'weight',
			'name': 'Blend factor',
			'min': 0.0,
			'max': 1.0,
			'default' : 0.0,
			'save_in_preset': True
		},
		{
			'type': 'string',
			'attr': 'mat1_name',
			'name': 'First material name',
			'save_in_preset': True
		},
		{
			'type': 'string',
			'attr': 'mat2_name',
			'name': 'Second material name',
			'save_in_preset': True
		},
		{
			'type': 'prop_search',
			'attr': 'mat_list1',
			'src': lambda s,c: s.object,
			'src_attr': 'material_slots',
			'trg': lambda s,c: c.mitsuba_bsdf_blendbsdf,
			'trg_attr': 'mat1_name',
			'name': 'Material 1 reference'
		},
		{
			'type': 'prop_search',
			'attr': 'mat_list2',
			'src': lambda s,c: s.object,
			'src_attr': 'material_slots',
			'trg': lambda s,c: c.mitsuba_bsdf_blendbsdf,
			'trg_attr': 'mat2_name',
			'name': 'Material 2 reference'
		}
	] + param_useTwoSidedMatherials.properties
	
	visibility = param_weightBlend.visibility
	
	def get_params(self):
		params = ParamSet()
		params.update(param_weightBlend.get_params(self))
		params.add_reference('material', "bsdf1", self.mat1_name)
		params.add_reference('material', "bsdf2", self.mat2_name)
		return params

@MitsubaAddon.addon_register_class
class mitsuba_bsdf_twosided(declarative_property_group):
	ef_attach_to = ['mitsuba_mat_bsdf']
	
	controls = [
		'mat_list1',
		'mat_list2'
	]
	
	properties = [
		{
			'type': 'string',
			'attr': 'mat1_name',
			'name': 'First material name',
			'save_in_preset': True
		},
		{
			'type': 'string',
			'attr': 'mat2_name',
			'name': 'Second material name',
			'save_in_preset': True
		},
		{
			'type': 'prop_search',
			'attr': 'mat_list1',
			'src': lambda s,c: s.object,
			'src_attr': 'material_slots',
			'trg': lambda s,c: c.mitsuba_bsdf_twosided,
			'trg_attr': 'mat1_name',
			'name': 'Material 1 reference'
		},
		{
			'type': 'prop_search',
			'attr': 'mat_list2',
			'src': lambda s,c: s.object,
			'src_attr': 'material_slots',
			'trg': lambda s,c: c.mitsuba_bsdf_twosided,
			'trg_attr': 'mat2_name',
			'name': 'Material 2 reference'
		}
	]
	
	def get_params(self):
		params = ParamSet()
		params.add_reference('material', "bsdf1", self.mat1_name)
		if self.mat2_name != '':
			params.add_reference('material', "bsdf2", self.mat2_name)
		return params

@MitsubaAddon.addon_register_class
class mitsuba_mat_subsurface(declarative_property_group):
	ef_attach_to = ['Material']
	
	controls = [
		'type'
	] 
	
	properties = [
		{
			'type': 'bool',
			'attr': 'use_subsurface',
			'name': 'Use Subsurface',
			'default': False,
			'save_in_preset': True
		},
		{
			'type': 'enum',
			'attr': 'type',
			'name': 'Type',
			'description': 'Specifes the type of Subsurface material',
			'items': [
				('dipole', 'Dipole Subsurface', 'dipole'),
				('participating', 'Participating Media', 'participating')			
			],
			'default': 'dipole',
			'save_in_preset': True
		}
	]
	
	def get_params(self):
		sub_type = getattr(self, 'mitsuba_sss_%s' % self.type)
		return sub_type.get_params()

@MitsubaAddon.addon_register_class
class mitsuba_sss_dipole(declarative_property_group):
	ef_attach_to = ['mitsuba_mat_subsurface']
	
	controls = [
		'material',
		'useAlbSigmaT'
	] + \
		param_absorptionCoefficient.controls + \
		param_scattCoeff.controls + \
		param_extinctionCoeff.controls + \
		param_albedo.controls + \
	[
		'scale',
		'intIOR',
		'extIOR',
		'irrSamples'
	] 
	
	properties = [
		{
			'type': 'string',
			'attr': 'material',
			'name': 'Preset name',
			'description' : 'Name of a material preset (def Ketchup; skin1, marble, potato, chicken1, apple)',
			'default': '',
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
			'min': 0.0001,
			'max': 50000.0,
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'intIOR',
			'name' : 'Int. IOR',
			'description' : 'Interior index of refraction (e.g. air=1, glass=1.5 approximately)',
			'default' : 1.5,
			'min': 1.0,
			'max': 10.0,
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'extIOR',
			'name' : 'Ext. IOR',
			'description' : 'Exterior index of refraction (e.g. air=1, glass=1.5 approximately)',
			'default' : 1,
			'min': 1.0,
			'max': 10.0,
			'save_in_preset': True
		},
		{
			'type': 'int',
			'attr': 'irrSamples',
			'name' : 'irrSamples',
			'description' : 'Number of samples',
			'default' : 16,
			'min': 2,
			'max': 128,
			'save_in_preset': True
		}
	] + \
		param_absorptionCoefficient.properties + \
		param_scattCoeff.properties + \
		param_extinctionCoeff.properties + \
		param_albedo.properties
	
	visibility = dict_merge(
		{
			'useAlbSigmaT': { 'material': '' }
		},
		param_absorptionCoefficient.visibility,
		param_scattCoeff.visibility,
		param_extinctionCoeff.visibility,
		param_albedo.visibility
	)
	
	visibility = texture_append_visibility(visibility, param_absorptionCoefficient, { 'material': '', 'useAlbSigmaT': False })
	visibility = texture_append_visibility(visibility, param_scattCoeff, { 'material': '', 'useAlbSigmaT': False })
	visibility = texture_append_visibility(visibility, param_extinctionCoeff, { 'material': '', 'useAlbSigmaT': True })
	visibility = texture_append_visibility(visibility, param_albedo, { 'material': '', 'useAlbSigmaT': True })
	
	def get_params(self):
		params = ParamSet()
		if self.material=='':
			params.add_float('intIOR', self.intIOR)
			params.add_float('extIOR', self.extIOR)
			if self.useAlbSigmaT != True:
				params.update(param_absorptionCoefficient.get_params(self))
				params.update(param_scattCoeff.get_params(self))
			else:
				params.update(param_extinctionCoeff.get_params(self))
				params.update(param_albedo.get_params(self))
		else:
			params.add_string('material', self.material)
		params.add_float('scale', self.scale)
		params.add_integer('irrSamples', self.irrSamples)
		return params

@MitsubaAddon.addon_register_class
class mitsuba_sss_participating(declarative_property_group):
	ef_attach_to = ['mitsuba_mat_subsurface']
	
	controls = ['interior'] 
	
	properties = [
		{
			'attr': 'interior_medium' ,
			'type': 'string',
			'name': 'interior_medium',
			'description': 'Interior medium; blank means vacuum' ,
			'save_in_preset': True
		},
		{
			'type': 'prop_search',
			'attr': 'interior',
			'src': lambda s,c: s.scene.mitsuba_media,
			'src_attr': 'media',
			'trg': lambda s,c: c.mitsuba_sss_participating,
			'trg_attr': 'interior_medium' ,
			'name': 'Interior medium'
		}
	]
		
	def get_params(self):
		params = ParamSet()	
		return params	

@MitsubaAddon.addon_register_class
class mitsuba_mat_extmedium(declarative_property_group):
	'''
	Storage class for Mitsuba Material settings.
	This class will be instantiated within a Blender Material
	object.
	'''	
	ef_attach_to = ['Material']
	
	controls = [
		'type'
	]
	
	properties = [
		{
			'type': 'bool',
			'attr': 'use_extmedium',
			'name': 'Use Exterior Medium',
			'description': 'Activate this property if the material specifies a transition from one participating medium to another.',
			'default': False,
			'save_in_preset': True
		},
		{
			'type': 'enum',
			'attr': 'type',
			'name': 'Type',
			'description': 'Specifes the type of Subsurface material',
			'items': [
				('participating', 'Participating Media', 'participating'),		
			],
			'default': 'participating',
			'save_in_preset': True
		}
	]
	
	def get_params(self):
		sub_type = getattr(self, 'mitsuba_extmed_%s' % self.type)
		return sub_type.get_params()

@MitsubaAddon.addon_register_class
class mitsuba_extmed_participating(declarative_property_group):		 
	ef_attach_to = ['mitsuba_mat_extmedium']
	controls = ['exterior'] 
		
	properties = [
		{
			'attr': 'exterior_medium' ,
			'type': 'string',
			'name': 'exterior_medium',
			'description': 'Exterior medium; blank means vacuum' ,
			'save_in_preset': True
		},
		{
			'type': 'prop_search',
			'attr': 'exterior',
			'src': lambda s,c: s.scene.mitsuba_media,
			'src_attr': 'media',
			'trg': lambda s,c: c.mitsuba_extmed_participating,
			'trg_attr': 'exterior_medium' ,
			'name': 'Exterior medium'
		}
	]
		
	def get_params(self):
		params = ParamSet()	
		return params	


@MitsubaAddon.addon_register_class
class mitsuba_mat_emitter(declarative_property_group):
	'''
	Storage class for Mitsuba Material emitter settings.
	This class will be instantiated within a Blender Material
	object.
	'''
	
	ef_attach_to = ['Material']
	
	controls = [
		'color',
		'intensity',
		'samplingWeight',
	]
	
	properties = [
		{
			'type': 'bool',
			'attr': 'use_emitter',
			'name': 'Use Emitter',
			'default': False,
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'intensity',
			'name': 'Intensity',
			'description': 'Specifies the intensity of the light source',
			'default': 10.0,
			'min': 1e-3,
			'soft_min': 1e-3,
			'max': 1e5,
			'soft_max': 1e5,
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'samplingWeight',
			'name': 'Sampling weight',
			'description': 'Relative amount of samples to place on this light source (e.g. the "importance")',
			'default': 1.0,
			'min': 1e-3,
			'soft_min': 1e-3,
			'max': 1e3,
			'soft_max': 1e3,
			'save_in_preset': True
		},
		{
			'attr': 'color',
			'type': 'float_vector',
			'subtype': 'COLOR',
			'description' : 'Color of the emitted light',
			'name' : 'Color',
			'default' : (1.0, 1.0, 1.0),
			'min': 0.0,
			'max': 1.0,
			'save_in_preset': True
		},
	]
	
	def get_params(self):
		params = ParamSet()
		params.update(param_diffuseReflectance.get_params(self))
		params.update(param_specularReflectance.get_params(self))
		params.add_color('intensity', 
			[self.color[0] * self.intensity, self.color[1] * self.intensity, self.color[2] * self.intensity])
		params.add_float('samplingWeight', self.samplingWeight)
		return params
