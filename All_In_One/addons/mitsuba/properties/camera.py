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
from extensions_framework import util as efutil

from ..export import ParamSet

def MediumParameter(attr, name):
	return [
		{
			'attr': '%s_medium' % attr,
			'type': 'string',
			'name': '%s_medium' % attr,
			'description': '%s; blank means vacuum' % name,
			'save_in_preset': True
		},
		{
			'type': 'prop_search',
			'attr': attr,
			'src': lambda s,c: s.scene.mitsuba_media,
			'src_attr': 'media',
			'trg': lambda s,c: c.mitsuba_camera,
			'trg_attr': '%s_medium' % attr,
			'name': name
		}
	]

@MitsubaAddon.addon_register_class
class mitsuba_camera(declarative_property_group):
	ef_attach_to = ['Camera']
	
	controls = [
		'exterior'
	]
	
	properties = [
		{
			'type': 'bool',
			'attr': 'useDOF',
			'name': 'Use camera DOF',
			'description': 'Camera DOF',
			'default': False,
			'save_in_preset': True
		},
		{
			'attr': 'apertureRadius',
			'type': 'float',
			'description' : 'DOF Aperture Radius',
			'name' : 'Aperture Radius',
			'default' : 0.03,
			'min': 0.01,
			'max': 1.0,
			'save_in_preset': True
		}
	] + MediumParameter('exterior', 'Exterior medium')

@MitsubaAddon.addon_register_class
class mitsuba_film(declarative_property_group):
	ef_attach_to = ['Camera']
	
	def file_formats(self, context):
		if (self.fileFormat == 'openexr') or (self.fileFormat == 'rgbe'):
			return [
				('rgb', 'RGB', 'rgb'),
				('rgba', 'RGBA', 'rgba'),
			]
		if self.fileFormat == 'jpeg':
			return [
				('rgb', 'RGB', 'rgb'),
				('luminance', 'BW', 'luminance'),
			]
		else:
			return [
				('rgb', 'RGB', 'rgb'),
				('rgba', 'RGBA', 'rgba'),
				('luminance', 'BW', 'luminance'),
				('luminanceAlpha', 'BWA', 'luminanceAlpha'),
			]
	
	def set_type(self, context):
		if self.fileFormat == 'openexr':
			self.type = 'hdrfilm'
			self.fileExtension = 'exr'
		elif self.fileFormat == "rgbe":
			self.type = 'hdrfilm'
			self.fileExtension = 'rgbe'
		else:
			self.type = 'ldrfilm'
			if self.fileFormat == 'jpeg':
				self.fileExtension = 'jpg'
			else:
				self.fileExtension = 'png'
	
	controls = [
		'tonemapMethod',
		'gamma',
		'exposure',
		'key',
		'burn',
		'rfilter',
		'stddev',
		'B',
		'C',
		'lobes',
		'highQualityEdges',
		'statistics',
		'banner',
		'attachLog',
	]
	
	visibility = {
		'tonemapMethod': { 'type': 'ldrfilm' },
		'gamma': { 'type': 'ldrfilm' },
		'exposure': { 'type': 'ldrfilm', 'tonemapMethod': 'gamma' },
		'key': { 'type': 'ldrfilm', 'tonemapMethod': 'reinhard' },
		'burn': { 'type': 'ldrfilm', 'tonemapMethod': 'reinhard' },
		'stddev': { 'rfilter': 'gaussian' },
		'B': { 'rfilter': 'mitchell' },
		'C': { 'rfilter': 'mitchell' },
		'lobes': { 'rfilter': 'lanczos' },
		'attachLog': { 'type': 'hdrfilm' },
	}
	
	properties = [
		{
			'type': 'string',
			'attr': 'type',
			'name': 'Type',
			'default': 'ldrfilm',
			'save_in_preset': True
		},
		{
			'type': 'string',
			'attr': 'fileExtension',
			'name': 'File Extension',
			'default': 'png',
			'save_in_preset': True
		},
		{
			'type': 'enum',
			'attr': 'fileFormat',
			'name': 'File Format',
			'description': 'Denotes the desired output file format',
			'items': [
				('png', 'PNG', 'png'),
				('jpeg', 'JPEG', 'jpeg'),
				('openexr', 'OpenEXR', 'openexr'),
				('rgbe', 'Radiance', 'rgbe')
			],
			'default': 'png',
			'update': set_type,
			'save_in_preset': True
		},
		{
			'type': 'enum',
			'attr': 'pixelFormat',
			'name': 'Pixel Format',
			'description': 'Specifies the desired pixel format',
			'items': file_formats,
			'save_in_preset': True
		},
		{
			'type': 'enum',
			'attr': 'componentFormat',
			'name': 'Component Format',
			'description': 'Specifies the desired floating point component format used for OpenEXR output',
			'items': [
				('float16', 'Float16', 'float16'),
				('float32', 'Float32', 'float32'),
			],
			'default': 'float16',
			'save_in_preset': True
		},
		{
			'type': 'enum',
			'attr': 'tonemapMethod',
			'name': 'Tonemap Method',
			'description': 'Method used to tonemap recorded radiance values',
			'items': [
				('gamma', 'Exposure and Gamma', 'gamma'),
				('reinhard', 'Reinhard Tonemapping', 'reinhard'),
			],
			'default': 'gamma',
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'gamma',
			'name' : 'Gamma',
			'description' : 'The gamma curve applied to correct the output image, where the special value -1 indicates sRGB. (Default: -1)',
			'default' : -1.0,
			'min': -10.0,
			'max': 10.0,
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'exposure',
			'name' : 'Exposure',
			'description' : 'specifies an exposure factor in f-stops that is applied to the image before gamma correction (scaling the radiance values by 2^exposure ). (Default: 0, i.e. do not change the exposure)',
			'default' : 0.0,
			'min': -10.0,
			'max': 10.0,
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'key',
			'name' : 'Key',
			'description' : 'Specifies whether a low-key or high-key image is desired. (Default: 0.18, corresponding to a middle-grey)',
			'default' : 0.18,
			'min': 0.0,
			'max': 1.0,
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'burn',
			'name' : 'Burn',
			'description' : 'Specifies how much highlights can burn out. (Default: 0, i.e. map all luminance values into the displayable range)',
			'default' : 0.0,
			'min': 0.0,
			'max': 1.0,
			'save_in_preset': True
		},
		{
			'type': 'enum',
			'attr': 'rfilter',
			'name': 'Reconstruction Filter',
			'description': 'Reconstruction filter method used generate final output image (default: gaussian)',
			'items': [
				('box', 'Box filter', 'box'),
				('tent', 'Tent filter', 'tent'),
				('gaussian', 'Gaussian filter', 'gaussian'),
				('mitchell', 'Mitchell-Netravali filter', 'mitchell'),
				('catmullrom', 'Catmull-Rom filter', 'catmullrom'),
				('lanczos', 'Lanczos Sinc filter', 'lanczos'),
			],
			'default': 'gaussian',
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'stddev',
			'name' : 'Standard Deviation',
			'description' : 'Standard Deviation. (Default: 0.5)',
			'default' : 0.5,
			'min': 0.1,
			'max': 10,
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'B',
			'name' : 'B Parameter',
			'description' : 'B parameter. (Default: 0.33)',
			'default' : 0.333333,
			'min': 0,
			'max': 10,
			'save_in_preset': True
		},
		{
			'type': 'float',
			'attr': 'C',
			'name' : 'C Parameter',
			'description' : 'C parameter. (Default: 0.33)',
			'default' : 0.333333,
			'min': 0,
			'max': 10,
			'save_in_preset': True
		},
		{
			'type': 'int',
			'attr': 'lobes',
			'name' : 'Lobes',
			'description' : 'Specifies the amount of filter side-lobes. (Default: 3)',
			'default' : 3,
			'min': 1,
			'max': 10,
			'save_in_preset': True
		},
		{
			'type': 'bool',
			'attr': 'highQualityEdges',
			'name': 'High Quality Edges',
			'description': 'If enabled, regions slightly outside of the film plane will also be sampled',
			'default': False,
			'save_in_preset': True
		},
		{
			'type': 'bool',
			'attr': 'banner',
			'name': 'Mitsuba Logo',
			'description': 'Render will containg small Mitsuba logo',
			'default': True,
			'save_in_preset': True
		},
		{
			'type': 'bool',
			'attr': 'statistics',
			'name': 'Render Statistics',
			'description': 'Render will containg render statistics',
			'default': True,
			'save_in_preset': True
		},
		{
			'type': 'bool',
			'attr': 'attachLog',
			'name': 'Attach Log',
			'description': 'Mitsuba can optionally attach the entire rendering log file as a metadata field so that this information is permanently saved',
			'default': True,
			'save_in_preset': True
		},
	]
	
	def get_params(self):
		params = ParamSet()
		params.add_string('fileFormat', self.fileFormat)
		params.add_string('pixelFormat', self.pixelFormat)
		if self.fileFormat == 'openexr' or self.fileFormat == 'rgbe':
			params.add_string('componentFormat', self.componentFormat)
			params.add_bool('attachLog', self.attachLog)
		if self.type == 'ldrfilm':
			params.add_string('tonemapMethod', self.tonemapMethod)
			params.add_float('gamma', self.gamma)
			if self.tonemapMethod == 'reinhard':
				params.add_float('key', self.key)
				params.add_float('burn', self.burn)
			else:
				params.add_float('exposure', self.exposure)
		params.add_bool('banner', self.banner)
		params.add_bool('highQualityEdges', self.highQualityEdges)
		if self.statistics:
			params.add_string('label[10,10]', 'Integrator:$integrator[\'type\'], $film[\'width\']x$film[\'height\'],$sampler[\'sampleCount\']spp, rendertime:$scene[\'renderTime\'],memory:$scene[\'memUsage\']' )
		return params
