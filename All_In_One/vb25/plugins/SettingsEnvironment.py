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
import mathutils
from bpy.props import *

''' vb modules '''
from vb25.ui      import ui
from vb25.plugins import *
from vb25.utils   import *
from vb25.shaders import *
from vb25.texture import *
from vb25.uvwgen  import *


TYPE= 'SETTINGS'
ID=   'SettingsEnvironment'

NAME= 'Environment Effects'
DESC= "Environment effects."

PARAMS= {
	'SettingsEnvironment': (
		'num_environment_objects', # integer = 0, Used for implementing image planes
	),

	'EnvironmentFog' : (
		'gizmos',
		'emission',
		'emission_tex',
		'emission_mult',
		'emission_mult_tex',
		'color',
		'color_tex',
		'distance',
		'density',
		'density_tex',
		'use_height',
		'height',
		'subdivs',
		'yup',
		'fade_out_mode',
		'fade_out_radius',
		'per_object_fade_out_radius',
		'use_fade_out_tex',
		'fade_out_tex',
		'edge_fade_out',
		'fade_out_type',
		'scatter_gi',
		'scatter_bounces',
		'simplify_gi',
		'step_size',
		'max_steps',
		'tex_samples',
		'cutoff_threshold',
		'light_mode',
		'lights',
		'use_shade_instance',
		'affect_background',
		'affect_reflections',
		'affect_refractions',
		'affect_shadows',
		'affect_gi',
		'affect_camera',
	),

	'VolumeVRayToon': (
		'lineColor',
		'widthType',
		'lineWidth',
		'opacity',
		'hideInnerEdges',
		'normalThreshold',
		'overlapThreshold',
		'traceBias',
		'doSecondaryRays',
		'excludeType',
		'excludeList',
		# 'lineColor_tex',
		# 'lineWidth_tex',
		# 'opacity_tex',
		# 'distortion_tex',
	),

	'SphereFade': (
		#'gizmos',
		'empty_color',
		'affect_alpha',
		'falloff'
	),
}


def add_properties(rna_pointer):
	class SphereFade(bpy.types.PropertyGroup):
		loc_only = BoolProperty(
			name        = "Use Location Only",
			description = "Use only location (ignore scale and rotation)",
			default     = False
		)
	bpy.utils.register_class(SphereFade)

	class VolumeVRayToon(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(VolumeVRayToon)

	class EnvironmentFog(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(EnvironmentFog)

	class EnvironmentEffect(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(EnvironmentEffect)

	class VRayEffects(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(VRayEffects)

	rna_pointer.EnvironmentFog= PointerProperty(
		name= "EnvironmentFog",
		type=  EnvironmentFog,
		description= "EnvironmentFog settings"
	)

	rna_pointer.SphereFade= PointerProperty(
		name= "SphereFade",
		type=  SphereFade,
		description= "SphereFade settings"
	)

	rna_pointer.VolumeVRayToon= PointerProperty(
		name= "VolumeVRayToon",
		type=  VolumeVRayToon,
		description= "VolumeVRayToon settings"
	)

	rna_pointer.VRayEffects= PointerProperty(
		name= "Environment Effects",
		type=  VRayEffects,
		description= "V-Ray environment effects settings"
	)

	VRayEffects.effects= CollectionProperty(
		name= "Environment Effect",
		type=  EnvironmentEffect,
		description= "V-Ray environment effect"
	)

	VRayEffects.use= BoolProperty(
		name= "Use effects",
		description= "Use effects",
		default= False
	)

	VRayEffects.effects_selected= IntProperty(
		name= "Selected Environment Effect",
		description= "Selected environment effect",
		default= -1,
		min= -1,
		max= 100
	)

	EnvironmentEffect.type= EnumProperty(
		name= "Type",
		description= "Distributed rendering network type",
		items= (
			('TOON', "Toon", "Object outline (toon style)."),
			('FOG',  "Fog",  "Environment / object fog."),
			('SFADE',  "SphereFade",  "Sphere Fade.")
		),
		default= 'FOG'
	)

	EnvironmentEffect.use= BoolProperty(
		name= "",
		description= "Use effect",
		default= True
	)

	EnvironmentEffect.EnvironmentFog= PointerProperty(
		name= "EnvironmentFog",
		type=  EnvironmentFog,
		description= "V-Ray EnvironmentFog settings"
	)

	EnvironmentEffect.VolumeVRayToon= PointerProperty(
		name= "VolumeVRayToon",
		type=  VolumeVRayToon,
		description= "V-Ray VolumeVRayToon settings"
	)

	EnvironmentEffect.SphereFade= PointerProperty(
		name= "SphereFade",
		type=  SphereFade,
		description= "SphereFade settings"
	)

	EnvironmentFog.emission= FloatVectorProperty(
		name= "Emission",
		description= "Fog emission color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0,0,0)
	)

	EnvironmentFog.emission_mult= FloatProperty(
		name= "Emission mult",
		description= "Emission mult",
		min= 0.0,
		max= 100000.0,
		soft_min= 0.0,
		soft_max= 100.0,
		precision= 3,
		default= 1.0
	)

	EnvironmentFog.emission_mult_tex= FloatProperty(
		name= "Emission texture mult",
		description= "Emission texture mult",
		min= 0.0,
		max= 100000.0,
		soft_min= 0.0,
		soft_max= 100.0,
		precision= 3,
		default= 1
	)

	EnvironmentFog.color= FloatVectorProperty(
		name= "Color",
		description= "Fog color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (1.0,1.0,1.0)
	)

	EnvironmentFog.distance= FloatProperty(
		name= "Distance",
		description= "Distance between fog particles",
		min= 0.0,
		max= 10000.0,
		soft_min= 0.0,
		soft_max= 100.0,
		precision= 3,
		default= 0.2
	)

	EnvironmentFog.density= FloatProperty(
		name= "Density",
		description= "A multiplier for the Fog distance parameter that allows a texture to be used for the density of the fog",
		min= 0.0,
		max= 1000.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	EnvironmentFog.density_tex = StringProperty(
		name        = "Density Texture",
		description = "",
		default     = ""
	)

	EnvironmentFog.emission_tex = StringProperty(
		name        = "Emission Texture",
		description = "",
		default     = ""
	)

	EnvironmentFog.use_height= BoolProperty(
		name= "Use height",
		description= "Whether or not the height should be taken into account",
		default= False
	)

	EnvironmentFog.height= FloatProperty(
		name= "Height",
		description= "Fog starting point along the Z-axis",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 100
	)

	EnvironmentFog.subdivs= IntProperty(
		name= "Subdivs",
		description= "Fog subdivision",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 8
	)

	EnvironmentFog.affect_background= BoolProperty(
		name= "Affect background",
		description= "Affect background",
		default= True
	)

	EnvironmentFog.yup= BoolProperty(
		name= "Y-up",
		description= "If true, y is the up axis, not z",
		default= False
	)

	EnvironmentFog.fade_out_mode= EnumProperty(
		name= "Fade out mode",
		description= "Fade out mode",
		items= (
			('SUBSTRACT', "Substract", ""),
			('MULT',      "Multiply",  ""),
		),
		default= 'MULT'
	)

	EnvironmentFog.fade_out_radius= FloatProperty(
		name= "Fade out radius",
		description= "Fade out effect for the edges",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0
	)

	EnvironmentFog.per_object_fade_out_radius= BoolProperty(
		name= "Per object fade out radius",
		description= "Fade out effect for the edges per object",
		default= False
	)

	EnvironmentFog.use_fade_out_tex= BoolProperty(
		name= "Use fade out tex",
		description= "True if the fade_out_tex should be used for fade out computation",
		default= False
	)

	EnvironmentFog.edge_fade_out= FloatProperty(
		name= "Edge fade out",
		description= "Used with the fade_out_tex, mimics Maya fluid's edge dropoff attribute",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0
	)

	EnvironmentFog.fade_out_type= IntProperty(
		name= "Fade out type",
		description= "0 - used for the gradients and the grid falloff(fadeout);1 - used for the sphere, cone and double cone types;2 - used for the cube type, the computations are done in the TexMayaFluidProcedural plug-in;",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 0
	)

	EnvironmentFog.scatter_gi= BoolProperty(
		name= "Scatter GI",
		description= "Scatter global illumination",
		default= True
	)

	EnvironmentFog.scatter_bounces= IntProperty(
		name= "Scatter bounces",
		description= "Number of GI bounces calculated inside the fog",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 8
	)

	EnvironmentFog.simplify_gi= BoolProperty(
		name= "Simplify GI",
		description= "Simplify global illumination",
		default= False
	)

	EnvironmentFog.step_size= FloatProperty(
		name= "Step size",
		description= "Size of one step through the volume",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	EnvironmentFog.max_steps= IntProperty(
		name= "Max steps",
		description= "Maximum number of steps through the volume",
		min= 0,
		max= 10000,
		soft_min= 0,
		soft_max= 10000,
		default= 1000
	)

	EnvironmentFog.tex_samples= IntProperty(
		name= "Texture samples",
		description= "Number of texture samples for each step through the volume",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 4
	)

	EnvironmentFog.cutoff_threshold= FloatProperty(
		name= "Cutoff",
		description= "Controls when the raymarcher will stop traversing the volume",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.001
	)

	EnvironmentFog.light_mode= EnumProperty(
		name= "Light mode",
		description= "Light mode",
		items= (
			('ADDGIZMO',"Add to per-gizmo lights",""),
			('INTERGIZMO',"Intersect with per-gizmo lights",""),
			('OVERGIZMO',"Override per-gizmo lights",""),
			('PERGIZMO',"Use per-gizmo lights",""),
			('NO',"No lights","")
		),
		default= 'PERGIZMO'
	)

	EnvironmentFog.lights= StringProperty(
		name= "Lights",
		description= "",
		default= ""
	)

	EnvironmentFog.use_shade_instance= BoolProperty(
		name= "Use shade instance",
		description= "True if the shade instance should be used when sampling textures",
		default= False
	)

	EnvironmentFog.objects= StringProperty(
		name= "Objects",
		description= "",
		default= ""
	)

	EnvironmentFog.groups= StringProperty(
		name= "Groups",
		description= "",
		default= ""
	)
	# affect_background
	EnvironmentFog.affect_background= BoolProperty(
		name= "Affect background",
		description= "Affect background",
		default= True
	)

	# affect_reflections
	EnvironmentFog.affect_reflections= BoolProperty(
		name= "Affect reflections",
		description= "true if the fog is visible to reflection rays",
		default= True
	)

	# affect_refractions
	EnvironmentFog.affect_refractions= BoolProperty(
		name= "Affect refractions",
		description= "true if the fog is visible to refraction rays",
		default= True
	)

	# affect_shadows
	EnvironmentFog.affect_shadows= BoolProperty(
		name= "Affect shadows",
		description= "true if the fog affects shadow rays",
		default= True
	)

	# affect_gi
	EnvironmentFog.affect_gi= BoolProperty(
		name= "Affect GI",
		description= "true if the fog affects GI rays",
		default= True
	)

	# affect_camera
	EnvironmentFog.affect_camera= BoolProperty(
		name= "Affect camera",
		description= "true if the fog affects primary camera rays",
		default= True
	)

	VolumeVRayToon.use= BoolProperty(
		name= "Use",
		description= "Render outline",
		default= False
	)

	VolumeVRayToon.override_material= BoolProperty(
		name= "Override material",
		description= "Override outline set in materials",
		default= False
	)

	# lineColor
	VolumeVRayToon.lineColor= FloatVectorProperty(
		name= "Color",
		description= "The color of cartoon line",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0,0,0)
	)

	# widthType
	VolumeVRayToon.widthType= EnumProperty(
		name= "Type",
		description= "",
		items= (
			('WORLD', "World",  "World units."),
			('PIXEL', "Pixels", "Pixels.")
		),
		default= 'PIXEL'
	)

	# lineWidth
	VolumeVRayToon.lineWidth= FloatProperty(
		name= "Width",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 5,
		default= 1.5
	)

	# opacity
	VolumeVRayToon.opacity= FloatProperty(
		name= "Opacity",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	# hideInnerEdges
	VolumeVRayToon.hideInnerEdges= BoolProperty(
		name= "Hide inner edges",
		description= "",
		default= True
	)

	# normalThreshold
	VolumeVRayToon.normalThreshold= FloatProperty(
		name= "Normal thresh",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.7
	)

	# overlapThreshold
	VolumeVRayToon.overlapThreshold= FloatProperty(
		name= "Overlap thresh",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.95
	)

	# traceBias
	VolumeVRayToon.traceBias= FloatProperty(
		name= "Bias",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.2
	)

	# doSecondaryRays
	VolumeVRayToon.doSecondaryRays= BoolProperty(
		name= "Do sec. rays",
		description= "Do reflections / refractons",
		default= False
	)

	# excludeType
	VolumeVRayToon.excludeType= EnumProperty(
		name= "Include / exclude",
		description= "",
		items= (
			('INCLUDE', "Include", "Include objects."),
			('EXCLUDE', "Exclude", "Exclude objects.")
		),
		default= 'EXCLUDE'
	)

	# excludeList
	VolumeVRayToon.excludeList_objects= StringProperty(
		name= "excludeList",
		description= "",
		default= ""
	)

	VolumeVRayToon.excludeList_groups= StringProperty(
		name= "excludeList",
		description= "",
		default= ""
	)

	# lineColor_tex
	VolumeVRayToon.map_lineColor_tex= BoolProperty(
		name= "lineColor tex",
		description= "",
		default= False
	)

	VolumeVRayToon.lineColor_tex_mult= FloatProperty(
		name= "lineColor tex",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	# lineWidth_tex
	VolumeVRayToon.map_lineWidth_tex= BoolProperty(
		name= "lineWidth tex",
		description= "",
		default= False
	)

	VolumeVRayToon.lineWidth_tex_mult= FloatProperty(
		name= "lineWidth tex",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	# opacity_tex
	VolumeVRayToon.map_opacity_tex= BoolProperty(
		name= "opacity tex",
		description= "",
		default= False
	)

	VolumeVRayToon.opacity_tex_mult= FloatProperty(
		name= "opacity tex",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	# distortion_tex
	VolumeVRayToon.map_distortion_tex= BoolProperty(
		name= "distortion tex",
		description= "",
		default= False
	)

	VolumeVRayToon.distortion_tex_mult= FloatProperty(
		name= "distortion tex",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	SphereFade.use = BoolProperty(
		name        = "",
		description = "",
		default     = False
	)

	SphereFade.affect_alpha = BoolProperty(
		name        = "Affect Alpha",
		description = "Affect Alpha",
		default     = False
	)

	SphereFade.empty_color= FloatVectorProperty(
		name= "Empty Color",
		description= "",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0.5,0.5,0.5)
	)

	SphereFade.falloff= FloatProperty(
		name= "Falloff",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.2
	)

	SphereFade.gizmos_objects= StringProperty(
		name= "Gizmo",
		description= "",
		default= ""
	)

	SphereFade.gizmos_groups= StringProperty(
		name= "Gizmo group",
		description= "",
		default= ""
	)



'''
  Write plugins settings to file
'''
def write_VolumeVRayToon_from_material(bus):
	WIDTHTYPE= {
		'PIXEL': 0,
		'WORLD': 1,
	}

	ofile= bus['files']['environment']
	scene= bus['scene']

	ob= bus['node']['object']
	ma= bus['material']['material']

	VRayMaterial= ma.vray

	VolumeVRayToon= VRayMaterial.VolumeVRayToon

	toon_name= clean_string("MT%s%s" % (ob.name, ma.name))

	ofile.write("\nVolumeVRayToon %s {" % toon_name)
	ofile.write("\n\tcompensateExposure= 1;")
	for param in PARAMS['VolumeVRayToon']:
		if param == 'excludeType':
			value= 1
		elif param == 'excludeList':
			value= "List(%s)" % get_name(ob, prefix='OB')
		elif param == 'widthType':
			value= WIDTHTYPE[VolumeVRayToon.widthType]
		else:
			value= getattr(VolumeVRayToon, param)
		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))
	ofile.write("\n}\n")

	return toon_name


def write_SphereFadeGizmo(bus, SphereFade, ob):
	scene= bus['scene']
	ofile= bus['files']['environment']

	tm = mathutils.Matrix.Translation(ob.matrix_world.translation)

	if not SphereFade.loc_only:
		sca  = ob.matrix_world.to_scale()
		tm[0][0] = sca[0]
		tm[1][1] = sca[1]
		tm[2][2] = sca[2]

	vray = ob.vray
	name= "MG%s" % get_name(ob, prefix='EMPTY')
	ofile.write("\nSphereFadeGizmo %s {" % name)
	ofile.write("\n\ttransform= %s;" % a(scene, transform(tm)))
	if ob.type == 'EMPTY':
		ofile.write("\n\tradius=%s;" % ob.empty_draw_size)
	elif vray.MtlRenderStats.use:
		ofile.write("\n\tradius=%s;" % vray.fade_radius)
	ofile.write("\n\tinvert=0;")
	ofile.write("\n}\n")
	return name


def write_SphereFade(bus, effect, gizmos):
	scene= bus['scene']
	ofile= bus['files']['environment']

	name= "ESF%s" % clean_string(effect.name)

	ofile.write("\nSphereFade %s {" % name)
	ofile.write("\n\tgizmos= List(%s);" % ','.join(gizmos))
	for param in PARAMS['SphereFade']:
		value= getattr(effect.SphereFade, param)
		ofile.write("\n\t%s= %s;"%(param, a(scene,value)))

	ofile.write("\n}\n")


def write(bus):
	ofile= bus['files']['environment']
	scene= bus['scene']

	VRayScene= scene.vray
	VRayExporter= VRayScene.exporter

	def write_EnvFogMeshGizmo(bus, ob):
		name= "MG%s" % get_name(ob, prefix='OB')

		ofile.write("\nEnvFogMeshGizmo %s {" % name)
		ofile.write("\n\tgeometry= %s;" % get_name(ob.data if VRayExporter.use_instances else ob, prefix='ME'))
		ofile.write("\n\ttransform= %s;" % a(scene, transform(ob.matrix_world)))
		#ofile.write("\n\tlights= List(%s);" % )
		#ofile.write("\n\tfade_out_radius= %s;" % )
		ofile.write("\n}\n")

		return name

	def write_EnvironmentFog_from_material(ofile,volume,material):
		LIGHT_MODE= {
			'ADDGIZMO':    4,
			'INTERGIZMO':  3,
			'OVERGIZMO':   2,
			'PERGIZMO':    1,
			'NO':          0
		}

		plugin= 'EnvironmentFog'
		name= "%s_%s" % (plugin,material)

		ofile.write("\n%s %s {"%(plugin,name))
		ofile.write("\n\tgizmos= List(%s);" % ','.join(volume[material]['gizmos']))
		for param in volume[material]['params']:
			if param == 'light_mode':
				value= LIGHT_MODE[volume[material]['params'][param]]
			elif param in ('density_tex','fade_out_tex','emission_mult_tex'):
				value= "%s::out_intensity" % volume[material]['params'][param]
			else:
				value= volume[material]['params'][param]
			ofile.write("\n\t%s= %s;"%(param, a(scene,value)))
		ofile.write("\n}\n")

		return name

	def write_EnvironmentFog(bus, effect, gizmos):
		LIGHT_MODE= {
			'ADDGIZMO':    4,
			'INTERGIZMO':  3,
			'OVERGIZMO':   2,
			'PERGIZMO':    1,
			'NO':          0
		}
		FADE_OUT_MODE= {
			'MULT':      0,
			'SUBSTRACT': 1,
		}

		EnvironmentFog= effect.EnvironmentFog

		density_tex       = None
		density_tex_voxel = False
		if EnvironmentFog.density_tex:
			if EnvironmentFog.density_tex in bpy.data.textures:
				if bpy.data.textures[EnvironmentFog.density_tex].type == 'VOXEL_DATA':
					density_tex_voxel = True
			density_tex = write_subtexture(bus, EnvironmentFog.density_tex)

		emission_tex = None
		if EnvironmentFog.emission_tex:
			emission_tex = write_subtexture(bus, EnvironmentFog.emission_tex)

		if emission_tex:
			emission_tex_mult_name = "%sMult" % emission_tex
			ofile.write("\nTexAColorOp %s {" % emission_tex_mult_name)
			ofile.write("\n\tcolor_a=%s;" % emission_tex)
			ofile.write("\n\tmult_a=%.3f;" % EnvironmentFog.emission_mult)
			ofile.write("\n}\n")
			emission_tex = emission_tex_mult_name

		name= "EEF%s" % clean_string(effect.name)

		ofile.write("\nEnvironmentFog %s {" % name)
		for param in PARAMS['EnvironmentFog']:
			value = None

			if param.endswith('_tex') or param.endswith('_mult'):
				if param == 'density_tex' and density_tex:
					value = "%s"%(density_tex)
					if not density_tex_voxel:
						value += "::out_intensity"
				elif param == 'emission_tex' and emission_tex:
					value = "%s"%(emission_tex)
				else:
					continue
			elif param == 'emission':
				value = "%s * %.3f" % (p(EnvironmentFog.emission), EnvironmentFog.emission_mult)
			elif param == 'fade_out_mode':
				value= FADE_OUT_MODE[EnvironmentFog.fade_out_mode]
			elif param == 'light_mode':
				value= LIGHT_MODE[EnvironmentFog.light_mode]
			elif param == 'gizmos':
				value= "List(%s)" % ','.join(gizmos)
			elif param == 'lights':
				light_object_list= [get_name(ob, prefix='LA') for ob in generate_object_list(EnvironmentFog.lights) if object_visible(bus,ob)]
				if not len(light_object_list):
					continue
				value= "List(%s)" % ','.join(light_object_list)
			else:
				value= getattr(EnvironmentFog, param)

			if value is not None:
				ofile.write("\n\t%s=%s;"%(param, a(scene, value)))
		ofile.write("\n}\n")

		return name

	def write_VolumeVRayToon(bus, effect, objects):
		EXCLUDETYPE= {
			'EXCLUDE': 0,
			'INCLUDE': 1,
		}
		WIDTHTYPE= {
			'PIXEL': 0,
			'WORLD': 1,
		}

		VolumeVRayToon= effect.VolumeVRayToon

		name= "EVT%s" % clean_string(effect.name)

		ofile.write("\nVolumeVRayToon %s {" % name)
		ofile.write("\n\tcompensateExposure= 1;")
		for param in PARAMS['VolumeVRayToon']:
			if param == 'excludeType':
				value= EXCLUDETYPE[VolumeVRayToon.excludeType]
			elif param == 'widthType':
				value= WIDTHTYPE[VolumeVRayToon.widthType]
			elif param == 'excludeList':
				value= "List(%s)" % ','.join(objects)
			else:
				value= getattr(VolumeVRayToon, param)
			ofile.write("\n\t%s= %s;"%(param, a(scene, value)))
		ofile.write("\n}\n")

		return name

	VRayScene=   scene.vray
	VRayEffects= VRayScene.VRayEffects

	# Processing Effects
	volumes= []
	if VRayEffects.use:
		for effect in VRayEffects.effects:
			if effect.use:
				if effect.type == 'FOG':
					EnvironmentFog= effect.EnvironmentFog
					gizmos= [write_EnvFogMeshGizmo(bus, ob) for ob in generate_object_list(EnvironmentFog.objects, EnvironmentFog.groups) if object_visible(bus,ob)]
					# if gizmos:
					# 	volumes.append(write_EnvironmentFog(bus, effect, gizmos))
					volumes.append(write_EnvironmentFog(bus, effect, gizmos))

				elif effect.type == 'TOON':
					VolumeVRayToon= effect.VolumeVRayToon

					excludeList= generate_object_list(VolumeVRayToon.excludeList_objects, VolumeVRayToon.excludeList_groups)
					toon_objects= [get_name(ob, prefix='OB') for ob in excludeList]

					if not VolumeVRayToon.override_material:
						if VolumeVRayToon.excludeType == 'EXCLUDE':
							toon_objects.extend( [ get_name(ob, prefix='OB') for ob in bus['effects']['toon']['objects'] ] )

					volumes.append(write_VolumeVRayToon(bus, effect, toon_objects))

				elif effect.type == 'SFADE':
					SphereFade= effect.SphereFade
					gizmos= [write_SphereFadeGizmo(bus, SphereFade, ob) for ob in generate_object_list(SphereFade.gizmos_objects, SphereFade.gizmos_groups) if object_visible(bus,ob)]
					write_SphereFade(bus, effect, gizmos)

	volumes.reverse()
	volumes.extend(bus['effects']['toon']['effects'])

	world=     scene.world
	VRayWorld= world.vray

	if VRayWorld:
		VRayScene=    scene.vray
		VRayExporter= VRayScene.exporter

		defaults= {
			'env_bg':         (a(scene,"AColor(%.6f,%.6f,%.6f,1.0)"%tuple(VRayWorld.bg_color)),         0, 'NONE'),
			'env_gi':         (a(scene,"AColor(%.6f,%.6f,%.6f,1.0)"%tuple(VRayWorld.gi_color)),         0, 'NONE'),
			'env_reflection': (a(scene,"AColor(%.6f,%.6f,%.6f,1.0)"%tuple(VRayWorld.reflection_color)), 0, 'NONE'),
			'env_refraction': (a(scene,"AColor(%.6f,%.6f,%.6f,1.0)"%tuple(VRayWorld.refraction_color)), 0, 'NONE'),
		}

		bus['env_textures']= {}
		for i,slot in enumerate(world.texture_slots):
			if slot and slot.texture and slot.texture.type in TEX_TYPES:
				VRaySlot= slot.texture.vray_slot

				for key in defaults:
					if getattr(VRaySlot, 'use_map_'+key):
						factor= getattr(VRaySlot, key+'_factor')

						if key not in bus['env_textures']: # First texture
							bus['env_textures'][key]= []
							if factor < 1.0 or VRaySlot.blend_mode != 'NONE' or slot.use_stencil:
								bus['env_textures'][key].append(defaults[key])

						bus['mtex']= {}
						bus['mtex']['env']=     True
						bus['mtex']['mapto']=   key
						bus['mtex']['slot']=    slot
						bus['mtex']['texture']= slot.texture
						bus['mtex']['factor']=  factor
						bus['mtex']['name']=    clean_string("WT%.2iSL%sTE%s" % (i,
																				 slot.name,
																				 slot.texture.name))

						# Write texture
						if write_texture(bus):
							bus['env_textures'][key].append( [stack_write_texture(bus),
															  slot.use_stencil,
															  VRaySlot.blend_mode] )

		if VRayExporter.debug:
			if len(bus['env_textures']):
				print_dict(scene, "World texture stack", bus['env_textures'])

		for key in bus['env_textures']:
			if len(bus['env_textures'][key]):
				bus['env_textures'][key]= write_TexOutput(bus, stack_write_textures(bus, stack_collapse_layers(bus['env_textures'][key])), key)

		if VRayExporter.debug:
			if len(bus['env_textures']):
				print_dict(scene, "World textures", bus['env_textures'])

		ofile.write("\nSettingsEnvironment SettingsEnvironment {")
		if 'env_bg' in bus['env_textures']:
			ofile.write("\n\tbg_tex=%s;" % bus['env_textures']['env_bg'])
		else:
			ofile.write("\n\tbg_tex=%s;"      % a(scene, VRayWorld.bg_color))
			ofile.write("\n\tbg_tex_mult=%s;" % a(scene, VRayWorld.bg_color_mult))

		if 'env_gi' in bus['env_textures']:
			ofile.write("\n\tgi_tex=%s;" % bus['env_textures']['env_gi'])
		elif VRayWorld.gi_override:
			ofile.write("\n\tgi_tex=%s;"      % a(scene, VRayWorld.gi_color))
			ofile.write("\n\tgi_tex_mult=%s;" % a(scene, VRayWorld.gi_color_mult))

		if 'env_reflection' in bus['env_textures']:
			ofile.write("\n\treflect_tex=%s;" % bus['env_textures']['env_reflection'])
		elif VRayWorld.reflection_override:
			ofile.write("\n\treflect_tex=%s;"      % a(scene, VRayWorld.reflection_color))
			ofile.write("\n\treflect_tex_mult=%s;" % a(scene, VRayWorld.reflection_color_mult))

		if 'env_refraction' in bus['env_textures']:
			ofile.write("\n\trefract_tex=%s;" % bus['env_textures']['env_refraction'])
		elif VRayWorld.refraction_override:
			ofile.write("\n\trefract_tex=%s;"      % a(scene, VRayWorld.refraction_color))
			ofile.write("\n\trefract_tex_mult=%s;" % a(scene, VRayWorld.refraction_color_mult))

		ofile.write("\n\tglobal_light_level=%s;" % a(scene, "Color(1.0,1.0,1.0)*%.3f" % (VRayWorld.global_light_level)))

		ofile.write("\n\tenvironment_volume=List(%s);" % (','.join(volumes)))
		ofile.write("\n}\n")


def WriteSphereFade(bus):
	scene = bus['scene']

	VRayScene = scene.vray
	VRayEffects = VRayScene.VRayEffects

	if not VRayEffects.use:
		return

	for effect in VRayEffects.effects:
		if not effect.use:
			continue

		if not effect.type == 'SFADE':
			continue

		SphereFade = effect.SphereFade

		for ob in generate_object_list(SphereFade.gizmos_objects, SphereFade.gizmos_groups):
			if object_visible(bus,ob):
				write_SphereFadeGizmo(bus, SphereFade, ob)

'''
  GUI
'''
def influence(context, layout, slot):
	VRaySlot= slot.texture.vray_slot

	# 	split= layout.split()
	# 	col= split.column()
	# 	col.label(text="Volume:")
	# 	split= layout.split()
	# 	col= split.column()
	# 	ui.factor_but(col, VRaySlot, 'map_color_tex',    'color_tex_mult',    "Color")
	# 	ui.factor_but(col, VRaySlot, 'map_density_tex',  'density_tex_mult',  "Density")
	# 	if wide_ui:
	# 		col= split.column()
	# 	ui.factor_but(col, VRaySlot, 'map_emission_tex', 'emission_tex_mult', "Emission")


def draw_EnvironmentFog(context, layout, rna_pointer):
	wide_ui= context.region.width > ui.narrowui

	EnvironmentFog= rna_pointer.EnvironmentFog

	split= layout.split()
	col= split.column()
	col.prop_search(EnvironmentFog, 'objects',
					context.scene,  'objects',
					text="Objects")
	col.prop_search(EnvironmentFog, 'groups',
					bpy.data,       'groups',
					text="Groups")

	layout.separator()

	layout.prop_search(EnvironmentFog, 'density_tex',  bpy.data, 'textures', text = "Density Texture")
	layout.prop_search(EnvironmentFog, 'emission_tex', bpy.data, 'textures', text = "Emission Texture")

	layout.separator()

	split= layout.split()
	col= split.column()
	col.prop(EnvironmentFog, 'color')
	if wide_ui:
		col= split.column()
	col.prop(EnvironmentFog, 'emission')
	col.prop(EnvironmentFog, 'emission_mult', text = "Mult")

	layout.separator()

	split= layout.split()
	col= split.column()
	col.prop(EnvironmentFog, 'distance')
	col.prop(EnvironmentFog, 'density')
	col.prop(EnvironmentFog, 'subdivs')
	col.prop(EnvironmentFog, 'scatter_gi')
	if EnvironmentFog.scatter_gi:
		col.prop(EnvironmentFog, 'scatter_bounces')
	col.prop(EnvironmentFog, 'use_height')
	if EnvironmentFog.use_height:
		col.prop(EnvironmentFog, 'height')
	if wide_ui:
		col= split.column()
	#col.prop(EnvironmentFog, 'fade_out_type')
	col.prop(EnvironmentFog, 'fade_out_radius')
	col.prop(EnvironmentFog, 'affect_background')
	col.prop(EnvironmentFog, 'use_shade_instance')
	col.prop(EnvironmentFog, 'simplify_gi')

	layout.separator()

	split= layout.split()
	col= split.column()
	col.prop(EnvironmentFog, 'light_mode')
	col.prop(EnvironmentFog, 'fade_out_mode')

	split= layout.split()
	col= split.column()
	col.prop_search(EnvironmentFog, 'lights',
					context.scene,  'objects',
					text="Lights")

	layout.separator()

	split= layout.split()
	col= split.column()
	col.prop(EnvironmentFog, 'step_size')
	col.prop(EnvironmentFog, 'max_steps')
	if wide_ui:
		col= split.column()
	col.prop(EnvironmentFog, 'tex_samples')
	col.prop(EnvironmentFog, 'cutoff_threshold')

	#col.prop(EnvironmentFog, 'per_object_fade_out_radius')
	#col.prop(EnvironmentFog, 'yup')

	layout.separator()

	split= layout.split()
	col= split.column()
	col.prop(EnvironmentFog, 'affect_shadows')
	col.prop(EnvironmentFog, 'affect_gi')
	col.prop(EnvironmentFog, 'affect_camera')
	if wide_ui:
		col= split.column()
	col.prop(EnvironmentFog, 'affect_reflections')
	col.prop(EnvironmentFog, 'affect_refractions')


def draw_VolumeVRayToon(context, layout, rna_pointer):
	wide_ui= context.region.width > ui.narrowui

	VolumeVRayToon= rna_pointer.VolumeVRayToon

	split= layout.split()
	col= split.column()
	col.prop(VolumeVRayToon, 'lineColor', text="")
	col.prop(VolumeVRayToon, 'widthType')
	col.prop(VolumeVRayToon, 'lineWidth')
	col.prop(VolumeVRayToon, 'opacity')
	if wide_ui:
		col= split.column()
	col.prop(VolumeVRayToon, 'normalThreshold')
	col.prop(VolumeVRayToon, 'overlapThreshold')
	col.prop(VolumeVRayToon, 'hideInnerEdges')
	col.prop(VolumeVRayToon, 'doSecondaryRays')
	col.prop(VolumeVRayToon, 'traceBias')

	# col.prop(VolumeVRayToon, 'lineColor_tex')
	# col.prop(VolumeVRayToon, 'lineWidth_tex')
	# col.prop(VolumeVRayToon, 'opacity_tex')
	# col.prop(VolumeVRayToon, 'distortion_tex')

	if not str(type(rna_pointer)) == "<class 'vb25.plugins.VRayMaterial'>": # Very ugly :(
		layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(VolumeVRayToon, 'override_material')

		split= layout.split()
		col= split.column()
		col.prop(VolumeVRayToon, 'excludeType', text="")
		col.prop_search(VolumeVRayToon, 'excludeList_objects',
						context.scene,  'objects',
						text="Objects")
		col.prop_search(VolumeVRayToon, 'excludeList_groups',
						bpy.data,       'groups',
						text="Groups")

def draw_SphereFade(context, layout, rna_pointer):
	wide_ui= context.region.width > ui.narrowui

	SphereFade= rna_pointer.SphereFade

	split= layout.split()
	col= split.column()
	col.prop(SphereFade, 'empty_color')
	col.prop(SphereFade, 'affect_alpha')
	col.prop(SphereFade, 'falloff')
	col.prop(SphereFade, 'loc_only')

	#col= split.column()
	col.prop_search(SphereFade, 'gizmos_objects',
					context.scene,  'objects',
					text="Objects")
	col.prop_search(SphereFade, 'gizmos_groups',
					bpy.data,       'groups',
					text="Groups")


def gui(context, layout, VRayEffects):
	wide_ui= context.region.width > ui.narrowui

	split= layout.split()
	row= split.row()
	row.template_list("VRayListUse", "",
					  VRayEffects, 'effects',
					  VRayEffects, 'effects_selected',
					  rows= 3)
	col= row.column(align=True)
	col.operator('vray.effect_add',	   text="", icon="ZOOMIN")
	col.operator('vray.effect_remove', text="", icon="ZOOMOUT")

	if VRayEffects.effects_selected >= 0:
		layout.separator()

		effect= VRayEffects.effects[VRayEffects.effects_selected]

		split= layout.split()
		col= split.column()
		col.prop(effect, 'name')
		col.prop(effect, 'type')

		layout.separator()

		if effect.type == 'FOG':
			draw_EnvironmentFog(context, layout, effect)

		elif effect.type == 'TOON':
			draw_VolumeVRayToon(context, layout, rna_pointer)
		else:
			split= layout.split()
			col= split.column()
			col.label(text="Strange, but this effect type doesn\'t exist...")


# elif VRayMaterial.type == 'VOL':
# 	return {
# 		'color_tex':    (a(scene,"AColor(%.6f,%.6f,%.6f,1.0)"%tuple(ma.diffuse_color)),           0, 'NONE'),
# 		'emission_tex': (a(scene,"AColor(%.6f,%.6f,%.6f,1.0)"%tuple(EnvironmentFog.emission)),    0, 'NONE'),
# 		'density_tex':  (a(scene,"AColor(%.6f,%.6f,%.6f,1.0)"%tuple([EnvironmentFog.density]*3)), 0, 'NONE'),
# 	}

# elif VRayMaterial.type == 'VOL':
# 	bus['node']['volume']= {}
# 	for param in OBJECT_PARAMS['EnvironmentFog']:
# 		if param == 'color':
# 			value= ma.diffuse_color
# 		else:
# 			value= getattr(VRayMaterial.EnvironmentFog,param)
# 		object_params['volume'][param]= value
# 	for param in ('color_tex','emission_tex','density_tex'):
# 		if param in textures['mapto']:
# 			object_params['volume'][param]= textures['mapto'][param]
# 	return None


# if object_params['volume'] is not None:
# 	if ma_name not in types['volume'].keys():
# 		types['volume'][ma_name]= {}
# 		types['volume'][ma_name]['params']= object_params['volume']
# 		types['volume'][ma_name]['gizmos']= []
# 	if ob not in types['volume'][ma_name]:
# 		types['volume'][ma_name]['gizmos'].append(write_EnvFogMeshGizmo(files['nodes'], node_name, node_geometry, node_matrix))
# 	return
