'''

  V-Ray/Blender

  http://vray.cgdo.ru

  Author: Andrey M. Izrantsev (aka bdancer)
  E-Mail: izrantsev@cgdo.ru

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

  All Rights Reserved. V-Ray(R) is a registered trademark of Chaos Software.

'''


''' Blender modules '''
import bpy
from bpy.props import *

''' vb modules '''
from vb25.utils import *


TYPE= 'GEOMETRY'
ID=   'LightMesh'

NAME= 'LightMesh'
UI=   "Mesh light"
DESC= "LightMesh settings"

PARAMS= (
	'enabled',
	# 'transform',
	'color',
	# 'color_tex',
	# 'shadows',
	# 'shadowColor',
	# 'shadowColor_tex',
	# 'shadowBias',
	# 'photonSubdivs',
	'causticSubdivs',
	# 'diffuseMult',
	# 'causticMult',
	# 'cutoffThreshold',
	'affectDiffuse',
	'affectSpecular',
	# 'bumped_below_surface_check',
	# 'nsamples',
	# 'diffuse_contribution',
	# 'specular_contribution',
	# 'channels',
	# 'channels_raw',
	# 'channels_diffuse',
	# 'channels_specular',
	'units',
	'intensity',
	# 'intensity_tex',
	'subdivs',
	'storeWithIrradianceMap',
	'invisible',
	'affectReflections',
	'noDecay',
	'doubleSided',
	'lightPortal',
	'geometry',
	# 'ignoreLightNormals',
	# 'tex',
	# 'use_tex',
	# 'tex_resolution',
	# 'cache_tex'
)


def add_properties(rna_pointer):
	class LightMesh(bpy.types.PropertyGroup):
		color= FloatVectorProperty(
			name= "Color",
			description= "Light color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (1.0,1.0,1.0)
		)

		color_type= EnumProperty(
			name= "Color type",
			description= "Color type",
			items= (
				('RGB',    "RGB", ""),
				('KELVIN', "K",   ""),
			),
			default= 'RGB'
		)

		temperature= IntProperty(
			name= "Temperature",
			description= "Kelvin temperature",
			min= 1000,
			max= 40000,
			step= 100,
			default= 5000
		)

		use_include_exclude= BoolProperty(
			name= "Use Include / Exclude",
			description= "Use Include / Exclude",
			default= False
		)

		include_exclude= EnumProperty(
			name= "Type",
			description= "Include or exclude object from lightning",
			items= (
				('EXCLUDE',"Exclude",""),
				('INCLUDE',"Include",""),
			),
			default= 'EXCLUDE'
		)

		include_objects= StringProperty(
			name= "Include objects",
			description= "Include objects: name{;name;etc}"
		)

		include_groups= StringProperty(
			name= "Include groups",
			description= "Include groups: name{;name;etc}"
		)
	bpy.utils.register_class(LightMesh)

	rna_pointer.LightMesh= PointerProperty(
		name= "LightMesh",
		type=  LightMesh,
		description= "Mesh light settings"
	)

	LightMesh.use= BoolProperty(
		name= "Use mesh light",
		description= "Use mesh light",
		default= False
	)

	LightMesh.enabled= BoolProperty(
		name= "Enabled",
		description= "Light\'s on/off state",
		default= True
	)

	LightMesh.lightPortal= EnumProperty(
		name= "Light portal mode",
		description= "Specifies if the light is a portal light",
		items= (
			('NORMAL',"Normal light",""),
			('PORTAL',"Portal",""),
			('SPORTAL',"Simple portal","")
		),
		default= 'NORMAL'
	)

	LightMesh.units= EnumProperty(
		name= "Intensity units",
		description= "Units for the intensity",
		items= (
			('DEFAULT',"Default",""),
			('LUMENS',"Lumens",""),
			('LUMM',"Lm/m/m/sr",""),
			('WATTSM',"Watts",""),
			('WATM',"W/m/m/sr","")
		),
		default= 'DEFAULT'
	)

	LightMesh.intensity= FloatProperty(
		name= "Intensity",
		description= "Light intensity",
		min= 0.0,
		max= 10000000.0,
		soft_min= 0.0,
		soft_max= 100.0,
		precision= 2,
		default= 30
	)

	LightMesh.causticSubdivs= IntProperty(
		name= "Caustic subdivs",
		description= "Caustic subdivs",
		min= 1,
		max= 10000,
		default= 1000
	)

	LightMesh.subdivs= IntProperty(
		name= "Subdivs",
		description= "The number of samples V-Ray takes to compute lighting",
		min= 0,
		max= 256,
		default= 8
	)

	LightMesh.noDecay= BoolProperty(
		name= "No decay",
		description= "TODO",
		default= False
	)

	LightMesh.affectReflections= BoolProperty(
		name= "Affect reflections",
		description= "true if the light appears in reflections and false otherwise",
		default= True
	)

	LightMesh.invisible= BoolProperty(
		name= "Invisible",
		description= "TODO",
		default= False
	)

	LightMesh.storeWithIrradianceMap= BoolProperty(
		name= "Store with Irradiance Map",
		description= "TODO",
		default= False
	)

	LightMesh.affectDiffuse= BoolProperty(
		name= "Affect diffuse",
		description= "true if the light produces diffuse lighting and false otherwise",
		default= True
	)

	LightMesh.affectSpecular= BoolProperty(
		name= "Affect specular",
		description= "true if the light produces specular hilights and false otherwise",
		default= True
	)

	LightMesh.doubleSided= BoolProperty(
		name= "Double-sided",
		description= "TODO",
		default= False
	)



def write(bus):
	LIGHT_PORTAL= {
		'NORMAL':  0,
		'PORTAL':  1,
		'SPORTAL': 2,
	}

	UNITS= {
		'DEFAULT' : 0,
		'LUMENS'  : 1,
		'LUMM'    : 2,
		'WATTSM'  : 3,
		'WATM'    : 4,
	}

	scene= bus['scene']
	ofile= bus['files']['lights']

	ob=    bus['node']['object']

	VRayObject= ob.vray
	LightMesh=  VRayObject.LightMesh

	if not VRayObject.LightMesh.use:
		return False
	
	textures= bus.get('textures', {})

	ofile.write("\nLightMesh %s {" % get_name(ob, prefix='LA'))
	ofile.write("\n\ttransform= %s;" % a(scene,transform(bus['node']['matrix'])))
	for param in PARAMS:
		if param == 'color':
			if LightMesh.color_type == 'RGB':
				color= LightMesh.color
			else:
				color= kelvin_to_rgb(LightMesh.temperature)
			ofile.write("\n\tcolor= %s;" % a(scene, "Color(%.6f,%.6f,%.6f)"%(tuple(color))))
			if 'diffuse' in textures:
				ofile.write("\n\ttex= %s;" % textures['diffuse'])
				ofile.write("\n\tuse_tex= 1;")
		elif param == 'geometry':
			ofile.write("\n\t%s= %s;"%(param, bus['node']['geometry']))
		elif param == 'units':
			ofile.write("\n\t%s= %i;"%(param, UNITS[LightMesh.units]))
		elif param == 'lightPortal':
			ofile.write("\n\t%s= %i;"%(param, LIGHT_PORTAL[LightMesh.lightPortal]))
		else:
			ofile.write("\n\t%s= %s;"%(param, a(scene,getattr(LightMesh,param))))
	ofile.write("\n}\n")

	return True
