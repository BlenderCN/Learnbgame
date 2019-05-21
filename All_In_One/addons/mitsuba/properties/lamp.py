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

from extensions_framework import declarative_property_group
from ..properties.world import MediumParameter
from ..export import ParamSet
from extensions_framework.validate import Logic_Operator, Logic_OR as LO

@MitsubaAddon.addon_register_class
class mitsuba_lamp(declarative_property_group):
	ef_attach_to = ['Lamp']
	
	controls = [
		'samplingWeight',
		'envmap_type',
		'envmap_file',
		'inside_medium',
		'radius',
		'medium'
	]
	
	visibility = {
		'envmap_type': { 'type': 'ENV' },
		'envmap_file': { 'type': 'ENV', 'envmap_type' : 'envmap' },
		'medium' : { 'inside_medium': True }
	}
	
	properties = [
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
			'type': 'enum',
			'attr': 'envmap_type',
			'name': 'Environment map type',
			'description': 'Environment map type',
			'default': 'constant',
			'items': [
				('constant', 'Constant background source', 'constant'),
				('envmap', 'HDRI environment map', 'envmap')
			],
			'save_in_preset': True
		},
		{
			'type': 'string',
			'subtype': 'FILE_PATH',
			'attr': 'envmap_file',
			'name': 'HDRI Map',
			'description': 'EXR image to use for lighting (in latitude-longitude format)',
			'default': '',
			'save_in_preset': True
		},
		{
			'type': 'bool',
			'attr': 'inside_medium',
			'name': 'Located inside a medium',
			'description': 'Check if the lamp lies within a participating medium',
			'default': False,
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'radius',
			'name': 'Point Size',
			'description': 'For realism mitsuba uses small sphere as point Light aproximation',
			'default': 0.2,
			'min': 0.001,
			'max': 30.0,
		}
	] + MediumParameter('lamp', 'Lamp')

@MitsubaAddon.addon_register_class	
class mitsuba_lamp_sun(declarative_property_group):
	ef_attach_to = ['mitsuba_lamp']
	
	controls = [
		'sunsky_type',
		'albedo',
		'turbidity',
		'sunsky_advanced',
		'stretch',
		'skyScale',
		'sunScale',
		'sunRadiusScale',
		'resolution'
	]
	
	visibility = {
		'albedo':				{ 'sunsky_type': LO({'sky','sunsky'}) },
		'stretch':				{ 'sunsky_advanced': True, 'sunsky_type': LO(['sky','sunsky']) },
		'skyScale':				{ 'sunsky_advanced': True, 'sunsky_type': LO({'sky','sunsky'}) },
		'sunScale':				{ 'sunsky_advanced': True, 'sunsky_type': LO({'sun','sunsky'}) },
		'sunRadiusScale':		{ 'sunsky_advanced': True, 'sunsky_type': LO({'sun','sunsky'}) },
		'resolution':			{ 'sunsky_advanced': True }
	}
	
	properties = [
		{
			'type': 'enum',
			'attr': 'sunsky_type',
			'name': 'Sky Type',
			'default': 'sunsky',
			'items': [
				('sunsky', 'Sun & Sky', 'sunsky'),
				('sun', 'Sun Only', 'sun'),
				('sky', 'Sky Only', 'sky'),
			]
		},
		{
			'type': 'float',
			'attr': 'turbidity',
			'name': 'Turbidity',
			'default': 3,
			'min': 1.2,
			'soft_min': 1.2,
			'max': 30.0,
			'soft_max': 30.0,
		},
		{
			'type': 'float_vector',
			'attr': 'albedo',
			'subtype': 'COLOR',
			'description' : 'Specifes the ground albedo. (Default:0.15)',
			'name' : 'Ground Albedo',
			'default' : (0.15, 0.15, 0.15),
			'min': 0.0,
			'max': 1.0,
			'save_in_preset': True
		},
		{
			'type': 'bool',
			'attr': 'sunsky_advanced',
			'name': 'Advanced',
			'default': False
		},
		{
			'type': 'float',
			'attr': 'stretch',
			'name': 'Stretch Sky',
			'description': 'Stretch factor to extend emitter below the horizon, must be in [1,2]. Default{1}, i.e. not used}',
			'default': 1.0,
			'min': 1.0,
			'soft_min': 1.0,
			'max': 2.0,
			'soft_max': 2.0,
		},
		{
			'type': 'float',
			'attr': 'skyScale',
			'name': 'Sky Intensity',
			'description': 'This parameter can be used to scale the the amount of illumination emitted by the sky emitter. \default{1}',
			'default': 1.0,
			'min': 0.0,
			'soft_min': 0.0,
			'max': 10.0,
			'soft_max': 10.0
		},
		{
			'type': 'float',
			'attr': 'sunScale',
			'name': 'Sun Intensity',
			'description': 'This parameter can be used to scale the the amount of illumination emitted by the sky emitter. \default{1}',
			'default': 1.0,
			'min': 0.0,
			'soft_min': 0.0,
			'max': 10.0,
			'soft_max': 10.0
		},
		{
			'type': 'float',
			'attr': 'sunRadiusScale',
			'name': 'Sun Radius',
			'description': 'Scale factor to adjust the radius of the sun, while preserving its power. Set to 0 to turn it into a directional light source',
			'default': 1.0,
			'min': 0.0,
			'soft_min': 0.0,
			'max': 10.0,
			'soft_max': 10.0
		},
		{
			'attr': 'resolution',
			'type': 'int',
			'name' : 'Resolution',
			'description' : 'Specifies the horizontal resolution of the precomputed image that is used to represent the sun/sky environment map \default{512, i.e. 512x256}',
			'default' : 512,
			'min': 128,
			'max': 2048,
			'save_in_preset': True
		}
	]
	
	def get_paramset(self, lamp_object):
		params = ParamSet()
		
		params.add_float('turbidity', self.turbidity)
		if self.sunsky_advanced and self.sunsky_type != 'sun':
			params.add_float('stretch', self.stretch)
			params.add_color('albedo', self.albedo)
		if self.sunsky_advanced and self.sunsky_type == 'sky':
			params.add_float('scale', self.skyScale)
		elif self.sunsky_advanced and self.sunsky_type == 'sun':
			params.add_float('scale', self.sunScale)
			params.add_float('sunRadiusScale', self.sunScale)
		elif self.sunsky_advanced and self.sunsky_type == 'sunsky':
			params.add_float('skyScale', self.skyScale)
			params.add_float('sunScale', self.sunScale)
			params.add_float('sunRadiusScale', self.sunRadiusScale)
		if self.sunsky_advanced:
			params.add_integer('resolution', self.resolution)
		
		#if self.sunsky_advanced and self.sunsky_type != 'sun':
			#params.add_float('horizonbrightness', self.horizonbrightness)
			#params.add_float('horizonsize', self.horizonsize)
		
		return params
