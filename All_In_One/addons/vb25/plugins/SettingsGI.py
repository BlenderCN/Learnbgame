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


TYPE= 'SETTINGS'
ID=   'SettingsGI'

NAME= 'Global Illumination'
DESC= "Global illumination settings"

PARAMS= (
)


def add_properties(parent_struct):
	class SettingsGI(bpy.types.PropertyGroup):
		on= BoolProperty(
			name= "Enable GI",
			description= "Enable Global Illumination",
			default= False
		)

		# ray_distance_on
		ray_distance_on= BoolProperty(
			name= "Limit ray distance",
			description= "Limit ray distance",
			default= False
		)

		# ray_distance
		ray_distance= FloatProperty(
			name= "Distance",
			description= "Ray distance limit",
			min= 0.0,
			max= 1000000.0,
			soft_min= 0.0,
			soft_max= 1000000.0,
			precision= 1,
			default= 100000
		)

		# ao_on
		ao_on= BoolProperty(
			name= "AO",
			description= "",
			default= False
		)

		# ao_amount
		ao_amount= FloatProperty(
			name= "Amount",
			description= "",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 2.0,
			precision= 3,
			default= 1.0
		)

		# ao_radius
		ao_radius= FloatProperty(
			name= "Radius",
			description= "",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			precision= 3,
			default= 0.2
		)

		# ao_subdivs
		ao_subdivs= IntProperty(
			name= "Subdivs",
			description= "",
			min= 0,
			max= 100,
			soft_min= 0,
			soft_max= 10,
			default= 8
		)

		primary_engine= EnumProperty(
			name= "Primary engine",
			description= "Primary diffuse bounces engines",
			items= (
				('IM', "Irradiance map",      ""), # 0
				('BF', "Brute force",         ""), # 2
				('LC', "Light cache",         ""), # 3
				('SH', "Spherical harmonics", ""), # 4
			),
			default= 'IM'
		)

		secondary_engine= EnumProperty(
			name= "Secondary engine",
			description= "Secondary diffuse bounces engines",
			items= (
				('NONE', "None",        ""), # 0
				('BF',   "Brute force", ""), # 2
				('LC',   "Light cache", "")  # 3
			),
			default= 'LC'
		)

		primary_multiplier= FloatProperty(
			name= "Primary multiplier",
			description= "This value determines how much primary diffuse bounces contribute to the final image illumination",
			min= 0.0,
			max= 10.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		secondary_multiplier= FloatProperty(
			name= "Secondary multiplier",
			description= "This determines the effect of secondary diffuse bounces on the scene illumination",
			min= 0.0,
			max= 10.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		refract_caustics= BoolProperty(
			name= "Refract caustics",
			description= "This allows indirect lighting to pass through transparent objects (glass etc)",
			default= 1
		)

		reflect_caustics= BoolProperty(
			name= "Reflect caustics",
			description= "This allows indirect light to be reflected from specular objects (mirrors etc)",
			default= 0
		)

		saturation= FloatProperty(
			name= "Saturation",
			description= "Controls the saturation of the GI",
			min= 0.0,
			max= 10.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		contrast= FloatProperty(
			name= "Contrast",
			description= "This parameter works together with Contrast base to boost the contrast of the GI solution",
			min= 0.0,
			max= 10.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		contrast_base= FloatProperty(
			name= "Contrast base",
			description= "This parameter determines the base for the contrast boost",
			min= 0.0,
			max= 10.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 0.5
		)

		spherical_harmonics= EnumProperty(
			name= "Spherical harmonics",
			description= "Bake or render spherical harmonics",
			items= (
				('BAKE',   "Bake",   ""),
				('RENDER', "Render", ""),
			),
			default= 'BAKE'
		)
	bpy.utils.register_class(SettingsGI)

	parent_struct.SettingsGI= PointerProperty(
		type= SettingsGI,
		name= NAME,
		description= DESC
	)


	class SphericalHarmonicsRenderer(bpy.types.PropertyGroup):
		file_name= StringProperty(
			name= "File",
			description= "This is the name of the *.vrsh file which contains the precomputed SH for this scene",
			subtype= 'FILE_PATH',
			default= "//lightmaps/harmonics.vrsh"
		)

		# precalc_light_per_frame
		precalc_light_per_frame= BoolProperty(
			name= "Precalc light per frame",
			description= "Reasonable when rendering animations. Depending on this option V-Ray calculates the lighting either once at the beginning of the rendering or precalculates it before every frame",
			default= True
		)

		# sample_environment
		sample_environment= BoolProperty(
			name= "Sample environment",
			description= "Turns on the environment sampling to add environment light contribution",
			default= True
		)

		# is_hemispherical
		is_hemispherical= BoolProperty(
			name= "Upper hemisphere only",
			description= "Depending on this option V-Ray samples either the whole sphere or only the upper hemisphere of the environment",
			default= True
		)

		# subdivs
		subdivs= IntProperty(
			name= "Subdivs",
			description= "The square of this parameter is proportional to the number of rays, sampled in the environment",
			min= 1,
			max= 1024,
			soft_min= 1,
			soft_max= 100,
			default= 30
		)

		# apply_filtering
		apply_filtering= BoolProperty(
			name= "Apply filtering",
			description= "Turns on the filtering of the spherical harmonics. This is useful to reduce the ringing artifacts (known as Gibbs phenomena in signal processing) by suppressing the high frequencies. This produces blurred SH which result in a smoother image",
			default= True
		)

		# filter_strength
		filter_strength= FloatProperty(
			name= "Filter strength",
			description= "The strength of high frequencies' suppression. Values near 0.0 slightly change the image while values near 1.0 smooth it a lot",
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			precision= 3,
			default= 0.5
		)
	bpy.utils.register_class(SphericalHarmonicsRenderer)

	SettingsGI.SphericalHarmonicsRenderer= PointerProperty(
		name= "Spherical Harmonics Renderer",
		type=  SphericalHarmonicsRenderer,
		description= "Spherical Harmonics Renderer settings"
	)



	class SphericalHarmonicsExporter(bpy.types.PropertyGroup):
		mode= EnumProperty(
			name= "Mode",
			description= "Allows you to select between four different modes of operation",
			items= (
				('OCC_SEL', "Occlusion (selected)",       ""),
				('OCC_ALL', "Occlusion",                  ""),
				('INT_SEL', "Interreflection (selected)", ""),
				('INT_ALL', "Interreflection",            ""),
			),
			default= 'OCC_ALL'
		)

		# bands
		bands= IntProperty(
			name= "Bands",
			description= "",
			min= 0,
			max= 100,
			soft_min= 0,
			soft_max= 10,
			default= 4
		)

		# subdivs
		subdivs= IntProperty(
			name= "Subdivs",
			description= "Controls the number of samples taken in order to create the spherical harmonics. Higher values produce better results but take longer to render",
			min= 1,
			max= 1024,
			soft_min= 1,
			soft_max= 100,
			default= 50
		)

		# bounces
		bounces= IntProperty(
			name= "Bounces",
			description= "This option is only available when one of the interreflection methods is selected. It controls the number of secondary bounces that are going to be traced",
			min= 1,
			max= 100,
			soft_min= 1,
			soft_max= 10,
			default= 1
		)

		# ray_bias
		ray_bias= FloatProperty(
			name= "Ray bias",
			description= "",
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 0.1,
			precision= 4,
			default= 0.0001
		)

		# file_name
		file_name= StringProperty(
			name= "File",
			subtype= 'FILE_PATH',
			description= "",
			default= "//lightmaps/harmonics.vrsh"
		)

		# file_format
		file_format= EnumProperty(
			name= "Format",
			description= "This is the output file format. It could be *.xml for general purposes, V-Ray internal format *.vrsh designed to be used in \"Spherical Harmoics\" GI engine or both of them",
			items= (
				('XML',  "*.xml",  ""),
				('VRSH', "*.vrsh", ""),
			),
			default= 'VRSH'
		)

		# per_normal
		per_normal= EnumProperty(
			name= "Distribute",
			description= "Spherical harmonics can be created either for each vertex of the geometry or for each normal, this option allows you to choose between those two modes. For round objects it is better to use per Vertex mode while for objects with large flat surfaces the per Normal mode is better and faster",
			items= (
				('NORMAL', "Per normal", ""),
				('VERTEX', "Per vertex", ""),
			),
			default= 'NORMAL'
		)

		# hit_recording
		hit_recording= BoolProperty(
			name= "Use hit recording",
			description= "Enabling it speeds up the calculations by storing a lot of information in the RAM",
			default= False
		)

		# object_space
		object_space= EnumProperty(
			name= "Transform",
			description= "",
			items= (
				('WORLD',  "World Space",  ""),
				('OBJECT', "Object Space", ""),
			),
			default= 'WORLD'
		)

		# node
		node= StringProperty(
			name= "Node",
			description= "Node to bake",
			default= ""
		)
	bpy.utils.register_class(SphericalHarmonicsExporter)

	SettingsGI.SphericalHarmonicsExporter= PointerProperty(
		name= "Spherical Harmonics Exporter",
		type=  SphericalHarmonicsExporter,
		description= "Spherical Harmonics Exporter settings"
	)



	class SettingsDMCGI(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(SettingsDMCGI)

	SettingsGI.SettingsDMCGI= PointerProperty(
		name= "DMC GI",
		type=  SettingsDMCGI,
		description= "DMC GI settings"
	)

	SettingsDMCGI.depth= IntProperty(
		name= "Secondary bounces",
		description= "The number of light bounces that will be computed",
		min= 1,
		max= 100,
		default= 3
	)

	SettingsDMCGI.subdivs= IntProperty(
		name= "Subdivs",
		description= "The number of samples used to approximate GI",
		min= 1,
		max= 500,
		default= 8
	)


	class SettingsIrradianceMap(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(SettingsIrradianceMap)

	SettingsGI.SettingsIrradianceMap= PointerProperty(
		name= "Irradiance Map",
		type=  SettingsIrradianceMap,
		description= "Irradiance Map settings"
	)

	SettingsIrradianceMap.preset= EnumProperty(
		name= "Preset",
		description= "Build-in presets",
		items= (
			('VLOW',"Very low",""),
			('LOW',"Low",""),
			('MEDIUM',"Medium",""),
			('MEDIUM_ANIM',"Medium animation",""),
			('HIGH',"High",""),
			('HIGH_ANIM',"High animation",""),
			('VHIGH',"Very high","")
		),
		default= "HIGH"
	)

	SettingsIrradianceMap.mode= EnumProperty(
		name= "Irradiance map mode",
		description= "Irradiance map mode",
		items= (
			('SINGLE',"Single frame","A new irradiance map is created for each frame."),
			('INC',"Multiframe incremental","At the start of the rendering, the irradiance map is deleted, and then each frame incrementally adds to the irradiance map in memory."),
			('FILE',"From file","The irradiance map is loaded from a file."),
			('ADD',"Add to current map","A new irradiance map is created and added to the one in memory."),
			('INC',"Incremental add to current map","Each frame adds incrementally to the irradiance map in memory; the old map is not deleted."),
			('BUCKET',"Bucket mode","Each render region (bucket) calculates its own irradiance map independently of the rest."),
			('ANIM_PRE',"Animation (prepass)","Separate irradiance map is rendered and saved with a different name for each frame; no final image is rendered."),
			('ANIM_REND',"Animation (rendering)","Final rendering of animation using saved per-frame irradiance maps.")
		),
		default= "SINGLE"
	)

	SettingsIrradianceMap.lookup_mode= EnumProperty(
		name= "Sample lookup",
		description= "Method of choosing suitable points from the irradiance map to be used as basis for the interpolation",
		items= (
			('QUAD',"Quad-balanced",""),
			('NEAREST',"Nearest",""),
			('OVERLAP',"Overlapping",""),
			('DENSITY',"Density-based","")
		),
		default= "OVERLAP"
	)

	SettingsIrradianceMap.interpolation_mode= EnumProperty(
		name= "Interpolation type",
		description= "Method for interpolating the GI value from the samples in the irradiance map",
		items= (
			('VORONOI',"Least squares with Voronoi weights",""),
			('DELONE',"Delone triangulation",""),
			('LEAST',"Least squares fit",""),
			('WEIGHTED',"Weighted average","")
		),
		default= "LEAST"
	)

	SettingsIrradianceMap.detail_scale= EnumProperty(
		name= "Detail enhancement scale",
		description= "Build-in presets",
		items= (
			('SCREEN', "Screen", "Radius in pixels."),
			('WORLD',  "World",  "Radius in Blender Units.")
		),
		default= 'WORLD'
	)

	SettingsIrradianceMap.min_rate= IntProperty(
		name= "Min rate",
		description= "This value determines the resolution for the first GI pass",
		min= -10,
		max= 1,
		default= -3
	)

	SettingsIrradianceMap.max_rate= IntProperty(
		name= "Max rate",
		description= "This value determines the resolution of the last GI pass",
		min= -10,
		max= 1,
		default= 0
	)

	SettingsIrradianceMap.color_threshold= FloatProperty(
		name= "Color threshold",
		description= "This parameter controls how sensitive the irradiance map algorithm is to changes in indirect lighting",
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= 0.30
	)

	SettingsIrradianceMap.normal_threshold= FloatProperty(
		name= "Normal threshold",
		description= "This parameter controls how sensitive the irradiance map is to changes in surface normals and small surface details",
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= 0.10
	)

	SettingsIrradianceMap.distance_threshold= FloatProperty(
		name= "Distance threshold",
		description= "This parameter controls how sensitive the irradiance map is to distance between surfaces",
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= 0.10
	)

	SettingsIrradianceMap.show_calc_phase= BoolProperty(
		name= "Show calc. phase",
		description= "Show irradiance map calculations",
		default= 1
	)

	SettingsIrradianceMap.show_direct_light= BoolProperty(
		name= "Show direct light",
		description= "Show direct light",
		default= 1
	)

	SettingsIrradianceMap.show_samples= BoolProperty(
		name= "Show samples",
		description= "Show irradiance map samples",
		default= 0
	)

	SettingsIrradianceMap.subdivs= IntProperty(
		name= "Hemispheric subdivs",
		description= "This controls the quality of individual GI samples",
		min= 1,
		max= 500,
		default= 50
	)

	SettingsIrradianceMap.interp_samples= IntProperty(
		name= "Interpolation samples",
		description= "The number of GI samples that will be used to interpolate the indirect illumination at a given point",
		min= 1,
		max= 100,
		default= 20
	)

	SettingsIrradianceMap.interp_frames= IntProperty(
		name= "Interpolation frames",
		description= "The number of frames that will be used to interpolate GI when the \"Mode\" is set to \"Animation (rendering)\"",
		min= 1,
		max= 50,
		default= 2
	)

	SettingsIrradianceMap.calc_interp_samples= IntProperty(
		name= "Calc. pass interpolation samples",
		description= "The number of already computed samples that will be used to guide the sampling algorithm",
		min= 1,
		max= 30,
		default= 10
	)

	SettingsIrradianceMap.detail_enhancement= BoolProperty(
		name= "Detail enhancement",
		description= "Detail enhancement is a method for bringing additional detail to the irradiance map in the case where there are small details in the image",
		default= 0
	)

	SettingsIrradianceMap.detail_subdivs_mult= FloatProperty(
		name= "Detail enhancement subdivs mult",
		description= "The number of samples taken for the high-precision sampling as a percentage of the irradiance map Hemispheric subdivs",
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= 0.30
	)

	SettingsIrradianceMap.detail_radius= FloatProperty(
		name= "Detail enhancement radius",
		description= "This determines the radius for the detail enhancement effect",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 1.0,
		precision= 3,
		default= 0.2
	)

	SettingsIrradianceMap.multipass= BoolProperty(
		name= "Multipass",
		description= "When checked, this will cause V-Ray to use all irradiance map samples computed so far",
		default= 0
	)

	SettingsIrradianceMap.multiple_views= BoolProperty(
		name= "Use camera path",
		description= "When this option is on, V-Ray will calculate the irradiance map samples for the entire camera path, instead of just the current view",
		default= 0
	)

	SettingsIrradianceMap.randomize_samples= BoolProperty(
		name= "Randomize samples",
		description= "When it is checked, the image samples will be randomly jittered",
		default= 1
	)

	SettingsIrradianceMap.check_sample_visibility= BoolProperty(
		name= "Check sample visibility",
		description= "This will cause V-Ray to use only those samples from the irradiance map, which are directly visible from the interpolated point",
		default= 0
	)

	SettingsIrradianceMap.file= StringProperty(
		name= "Irradiance map file name",
		subtype= 'FILE_PATH',
		description= "Irradiance map file name",
		default= "//lightmaps/im.vrmap"
	)

	SettingsIrradianceMap.auto_save= BoolProperty(
		name= "Auto save irradiance map",
		description= "Automatically save the irradiance map to the specified file at the end of the rendering",
		default= 0
	)

	SettingsIrradianceMap.auto_save_file= StringProperty(
		name= "Irradiance map auto save file",
		subtype= 'FILE_PATH',
		description= "Irradiance map auto save file",
		default= "//lightmaps/im.vrmap"
	)


	class SettingsLightCache(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(SettingsLightCache)

	SettingsGI.SettingsLightCache= PointerProperty(
		name= "Light Cache",
		type=  SettingsLightCache,
		description= "Light Cache settings"
	)

	SettingsLightCache.mode= EnumProperty(
		name= "Light cache mode",
		description= "Light cache mode",
		items= (
			('SINGLE',"Single frame",""),
			('FILE',"From file",""),
			('FLY',"Fly-through",""),
			('PPT',"Progressive path tracing","")
		),
		default= 'SINGLE'
	)

	SettingsLightCache.subdivs= IntProperty(
		name= "Subdivs",
		description= "This determines how many paths are traced from the camera. The actual number of paths is the square of the subdivs",
		min= 1,
		max= 65535,
		default= 1000
	)

	SettingsLightCache.world_scale= EnumProperty(
		name= "Light cache scale mode",
		description= "This parameter determines the units of the \"Sample size\" and the \"Filter size\"",
		items= (
			('SCREEN',  "Screen", ""),
			('WORLD',   "World", ""),
		),
		default= 'SCREEN'
	)

	SettingsLightCache.sample_size= FloatProperty(
		name= "Sample size",
		description= "This determines the spacing of the samples in the light cache",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 1.0,
		precision= 4,
		default= 0.02
	)

	SettingsLightCache.num_passes= IntProperty(
		name= "Number of passes",
		description= "The light cache is computed in several passes, which are then combined into the final light cache",
		min= 1,
		max= 1000,
		default= 4
	)

	SettingsLightCache.num_passes_auto= BoolProperty(
		name= "Auto num. passes",
		description= "Set number of passes to threads number",
		default= 1
	)

	SettingsLightCache.retrace_enabled= BoolProperty(
		name= "Retrace",
		description= "Enable retrace of light cache",
		default= False
	)

	SettingsLightCache.retrace_threshold= FloatProperty(
		name= "Retrace treshold",
		description= "Retrace treshold, relative to the light cache sample size",
		min= 0.0,
		max= 10.0,
		soft_min= 0.0,
		soft_max= 1.0,
		precision= 3,
		default= 1.0
	)

	SettingsLightCache.depth= IntProperty(
		name= "Depth",
		description= "Light cache depth",
		min= 1,
		max= 1000,
		soft_min= 1,
		soft_max= 100,
		default= 100
	)

	SettingsLightCache.show_calc_phase= BoolProperty(
		name= "Show calc phase",
		description= "Turning this option on will show the paths that are traced",
		default= 1
	)

	SettingsLightCache.store_direct_light= BoolProperty(
		name= "Store direct light",
		description= "With this option, the light cache will also store and interpolate direct light",
		default= 1
	)

	SettingsLightCache.adaptive_sampling= BoolProperty(
		name= "Adaptive sampling",
		description= "When this option is on, V-Ray will store additional information about the incoming light for each light cache sample, and try to put more samples into the directions from which more light coming",
		default= 0
	)

	SettingsLightCache.filter= BoolProperty(
		name= "Filter",
		description= "Enable render-time filter for the light cache",
		default= 1
	)

	SettingsLightCache.filter_type= EnumProperty(
		name= "Filter type",
		description= "The filter determines how irradiance is interpolated from the samples in the light cache",
		items= (
			('NONE',    "None",    ""),
			('NEAREST', "Nearest", ""),
			('FIXED',   "Fixed",   "")
		),
		default= "NEAREST"
	)

	SettingsLightCache.filter_samples= IntProperty(
		name= "Samples",
		description= "How many of the nearest samples to look up from the light cache",
		min= 1,
		max= 1000,
		default= 10
	)

	SettingsLightCache.filter_size= FloatProperty(
		name= "Size",
		description= "The size of the filter",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= 0.02
	)

	SettingsLightCache.prefilter= BoolProperty(
		name= "Pre-filter",
		description= "Filter light cache sampler before rendering",
		default= 0
	)

	SettingsLightCache.prefilter_samples= IntProperty(
		name= "Samples",
		description= "Number of samples",
		min= 1,
		max= 1000,
		default= 40
	)

	SettingsLightCache.multiple_views= BoolProperty(
		name= "Use camera path",
		description= "When this option is on, V-Ray will calculate the light cache samples for the entire camera path, instead of just the current view, in the same way as this is done for the Fly-through mode",
		default= 0
	)

	SettingsLightCache.use_for_glossy_rays= BoolProperty(
		name= "Use for glossy rays",
		description= "If this option is on, the light cache will be used to compute lighting for glossy rays as well, in addition to normal GI rays",
		default= 0
	)

	SettingsLightCache.file= StringProperty(
		name= "Light cache file name",
		subtype= 'FILE_PATH',
		description= "Light cache file name",
		default= "//lightmaps/lc.vrmap"
	)

	SettingsLightCache.auto_save= BoolProperty(
		name= "Auto save light cache",
		description= "Light cache file name",
		default= 0
	)

	SettingsLightCache.auto_save_file= StringProperty(
		name= "Light cache auto save file",
		subtype= 'FILE_PATH',
		description= "Light cache auto save file",
		default= "//lightmaps/lc.vrmap"
	)


	class SettingsPhotonMap(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(SettingsPhotonMap)

	SettingsGI.SettingsPhotonMap= PointerProperty(
		name= "Photon Map",
		type=  SettingsPhotonMap,
		description= "Photon Map settings"
	)

	SettingsPhotonMap.convex_hull_estimate= BoolProperty(
		name= "Convex hull estimate",
		description= "TODO",
		default= 0
	)

	SettingsPhotonMap.prefilter= BoolProperty(
		name= "Convert to irradiance map",
		description= "This will cause V-Ray to precompute the irradiance at the photon hit points stored in the photon map",
		default= 0
	)

	SettingsPhotonMap.prefilter_samples= IntProperty(
		name= "Interpolate samples",
		description= "This controls how many irradiance samples will be taken from the photon map once it is converted to an irradiance map",
		min= 1,
		max= 100,
		default= 10
	)

	SettingsPhotonMap.store_direct_light= BoolProperty(
		name= "Store direct light",
		description= "Store direct illumination in the photon map as well",
		default= 1
	)

	SettingsPhotonMap.auto_search_distance= BoolProperty(
		name= "Auto search distance",
		description= "Try to compute a suitable distance within which to search for photons",
		default= 1
	)

	SettingsPhotonMap.search_distance= FloatProperty(
		name= "Search distance",
		description= "Photon search distance",
		min= 0.0,
		max= 1000.0,
		soft_min= 0.0,
		soft_max= 100.0,
		default= 20.0
	)

	SettingsPhotonMap.retrace_corners= FloatProperty(
		name= "Retrace corners",
		description= "When this is greater than 0.0, V-Ray will use brute force GI near corners, instead of the photon map, in order to obtain a more accurate result and to avoid splotches in these areas. ",
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= 0.0
	)

	SettingsPhotonMap.retrace_bounces= IntProperty(
		name= "Retrace bounces",
		description= "Controls how many bounces will be made when retracing corners",
		min= 1,
		max= 100,
		default= 10
	)

	SettingsPhotonMap.bounces= IntProperty(
		name= "Bounces",
		description= "The number of light bounces approximated by the photon map",
		min= 1,
		max= 1000,
		default= 10
	)

	SettingsPhotonMap.multiplier= FloatProperty(
		name= "Multiplier",
		description= "This allows you to control the brightness of the photon map",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		default= 1.0
	)

	SettingsPhotonMap.max_photons= IntProperty(
		name= "Max photons",
		description= "This option specifies how many photons will be taken into consideration when approximating the irradiance at the shaded point",
		min= 1,
		max= 10000,
		default= 30
	)

	SettingsPhotonMap.max_density= FloatProperty(
		name= "Max density",
		description= "This parameter allows you to limit the resolution (and thus the memory) of the photon map",
		min= 0.0,
		max= 1000.0,
		soft_min= 0.0,
		soft_max= 100.0,
		default= 0.0
	)


def write(bus):
	ofile=  bus['files']['scene']
	scene=  bus['scene']

	VRayScene=             scene.vray
	VRayExporter=          VRayScene.exporter
	SettingsDMCSampler=    VRayScene.SettingsDMCSampler
	SettingsGI=            VRayScene.SettingsGI
	SettingsIrradianceMap= SettingsGI.SettingsIrradianceMap
	SettingsLightCache=    SettingsGI.SettingsLightCache
	SettingsDMCGI=         SettingsGI.SettingsDMCGI

	PRIMARY_ENGINE= {
		'IM':  0,
		'PM':  1,
		'BF':  2,
		'LC':  3,
		'SH':  4,
	}

	SECONDARY_ENGINE= {
		'NONE':  0,
		'PM':    1,
		'BF':    2,
		'LC':    3,
	}

	WORLD_SCALE= {
		'SCREEN':  0,
		'WORLD':   1
	}
	
	IM_MODE= {
		'SINGLE':	 0,
		'INC':		 1,
		'FILE':		 2,
		'ADD':		 3,
		'ADD_INC':	 4,
		'BUCKET':	 5,
		'ANIM_PRE':	 6,
		'ANIM_REND': 7,
	}

	INTERPOLATION_MODE= {
		'VORONOI':	 0,
		'LEAST':	 1,
		'DELONE':	 2,
		'WEIGHTED':	 3,
	}

	LOOKUP_MODE= {
		'QUAD':		0,
		'NEAREST':	1,
		'OVERLAP':	2,
		'DENSITY':	3,
	}

	FILTER_TYPE= {
		'NONE':	   0,
		'NEAREST': 1,
		'FIXED':   2,
	}

	LC_MODE= {
		'SINGLE':  0,
		'FLY':	   1,
		'FILE':	   2,
		'PPT':	   3,
	}

	if SettingsGI.on:
		if SettingsGI.primary_engine == 'SH' and SettingsGI.spherical_harmonics == 'BAKE':
			SH_MODE= {
				'OCC_SEL': 0,
				'OCC_ALL': 1,
				'INT_SEL': 2,
				'INT_ALL': 3,
			}
			FILE_FORMAT= {
				'XML': "xml",
				'VRSH': "vrsh",
			}

			SphericalHarmonicsExporter= SettingsGI.SphericalHarmonicsExporter

			ofile.write("\nSphericalHarmonicsExporter SphericalHarmonicsExporter {")
			ofile.write("\n\tmode= %i;" % SH_MODE[SphericalHarmonicsExporter.mode])
			ofile.write("\n\tbands= %s;" % p(SphericalHarmonicsExporter.bands))
			ofile.write("\n\tsubdivs= %s;" % p(SphericalHarmonicsExporter.subdivs))
			ofile.write("\n\tbounces= %s;" % p(SphericalHarmonicsExporter.bounces))
			ofile.write("\n\tray_bias= %s;" % p(SphericalHarmonicsExporter.ray_bias))
			ofile.write("\n\tfile_name= \"%s\";" % create_dir_from_filepath(bpy.path.abspath(SphericalHarmonicsExporter.file_name)))
			ofile.write("\n\tfile_format= \"%s\";" % FILE_FORMAT[SphericalHarmonicsExporter.file_format])
			ofile.write("\n\tper_normal= %s;" % p(SphericalHarmonicsExporter.per_normal))
			ofile.write("\n\thit_recording= %s;" % p(SphericalHarmonicsExporter.hit_recording))
			ofile.write("\n\tobject_space= %s;" % p(SphericalHarmonicsExporter.object_space))
			if SphericalHarmonicsExporter.node:
				node= get_data_by_name(scene, 'objects', SphericalHarmonicsExporter.node)
				if node:
					ofile.write("\n\tnode= %s;" % get_name(node, prefix='OB'))
			ofile.write("\n}\n")

		else:
			lc_auto_save_path = get_path(SettingsLightCache.auto_save_file)
			if SettingsLightCache.auto_save:
				create_dir_from_filepath(lc_auto_save_path)

			im_auto_save_path = get_path(SettingsIrradianceMap.auto_save_file)
			if SettingsIrradianceMap.auto_save:
				create_dir_from_filepath(im_auto_save_path)

			ofile.write("\nSettingsGI SettingsGI {")
			ofile.write("\n\ton= 1;")
			ofile.write("\n\tprimary_engine= %s;" % PRIMARY_ENGINE[SettingsGI.primary_engine])
			ofile.write("\n\tsecondary_engine= %s;" % SECONDARY_ENGINE[SettingsGI.secondary_engine])
			ofile.write("\n\tprimary_multiplier= %.3f;" % SettingsGI.primary_multiplier)
			ofile.write("\n\tsecondary_multiplier= %.3f;" % SettingsGI.secondary_multiplier)
			ofile.write("\n\treflect_caustics= %i;" % SettingsGI.reflect_caustics)
			ofile.write("\n\trefract_caustics= %i;" % SettingsGI.refract_caustics)
			ofile.write("\n\tsaturation= %.3f;" % SettingsGI.saturation)
			ofile.write("\n\tcontrast= %.3f;" % SettingsGI.contrast)
			ofile.write("\n\tcontrast_base= %.3f;" % SettingsGI.contrast_base)
			ofile.write("\n\tray_distance_on= %s;" % p(SettingsGI.ray_distance_on))
			ofile.write("\n\tray_distance= %s;" % p(SettingsGI.ray_distance))
			ofile.write("\n\tao_on= %s;" % p(SettingsGI.ao_on))
			ofile.write("\n\tao_amount= %s;" % p(SettingsGI.ao_amount))
			ofile.write("\n\tao_radius= %s;" % p(SettingsGI.ao_radius))
			ofile.write("\n\tao_subdivs= %s;" % p(SettingsGI.ao_subdivs))
			ofile.write("\n}\n")

			ofile.write("\nSettingsIrradianceMap SettingsIrradianceMap {")
			ofile.write("\n\tmin_rate= %i;" % SettingsIrradianceMap.min_rate)
			ofile.write("\n\tmax_rate= %i;" % SettingsIrradianceMap.max_rate)
			ofile.write("\n\tsubdivs= %i;" % SettingsIrradianceMap.subdivs)
			ofile.write("\n\tinterp_samples= %i;" % SettingsIrradianceMap.interp_samples)
			ofile.write("\n\tinterp_frames= %i;" % SettingsIrradianceMap.interp_frames)
			ofile.write("\n\tcalc_interp_samples= %i;" % SettingsIrradianceMap.calc_interp_samples)
			ofile.write("\n\tcolor_threshold= %.6f;" % SettingsIrradianceMap.color_threshold)
			ofile.write("\n\tnormal_threshold= %.6f;" % SettingsIrradianceMap.normal_threshold)
			ofile.write("\n\tdistance_threshold= %.6f;" % SettingsIrradianceMap.distance_threshold)
			ofile.write("\n\tdetail_enhancement= %i;" % SettingsIrradianceMap.detail_enhancement)
			ofile.write("\n\tdetail_radius= %.6f;" % SettingsIrradianceMap.detail_radius)
			ofile.write("\n\tdetail_subdivs_mult= %.6f;" % SettingsIrradianceMap.detail_subdivs_mult)
			ofile.write("\n\tdetail_scale= %i;" % WORLD_SCALE[SettingsIrradianceMap.detail_scale])
			ofile.write("\n\tinterpolation_mode= %i;" % INTERPOLATION_MODE[SettingsIrradianceMap.interpolation_mode])
			ofile.write("\n\tlookup_mode= %i;" % LOOKUP_MODE[SettingsIrradianceMap.lookup_mode])
			ofile.write("\n\tshow_calc_phase= %i;" % SettingsIrradianceMap.show_calc_phase)
			ofile.write("\n\tshow_direct_light= %i;" % SettingsIrradianceMap.show_direct_light)
			ofile.write("\n\tshow_samples= %i;" % SettingsIrradianceMap.show_samples)
			ofile.write("\n\tmultipass= %i;" % SettingsIrradianceMap.multipass)
			ofile.write("\n\tcheck_sample_visibility= %i;" % SettingsIrradianceMap.check_sample_visibility)
			ofile.write("\n\trandomize_samples= %i;" % SettingsIrradianceMap.randomize_samples)
			ofile.write("\n\tmode= %d;" % IM_MODE[SettingsIrradianceMap.mode])
			ofile.write("\n\tauto_save= %d;" % SettingsIrradianceMap.auto_save)
			ofile.write("\n\tauto_save_file= \"%s\";" % im_auto_save_path)
			ofile.write("\n\tfile= \"%s\";" % get_full_filepath(bus, None, SettingsIrradianceMap.file))
			ofile.write("\n\tmultiple_views= %d;" % SettingsIrradianceMap.multiple_views)
			ofile.write("\n\tdont_delete= false;")
			ofile.write("\n}\n")

			ofile.write("\nSettingsDMCGI SettingsDMCGI {")
			ofile.write("\n\tsubdivs= %i;" % SettingsDMCGI.subdivs)
			ofile.write("\n\tdepth= %i;" % SettingsDMCGI.depth)
			ofile.write("\n}\n")

			ofile.write("\nSettingsLightCache SettingsLightCache {")
			if VRayExporter.draft:
				ofile.write("\n\tsubdivs= %.0f;" % (SettingsLightCache.subdivs * 0.2))
			else:
				ofile.write("\n\tsubdivs= %.0f;" % (SettingsLightCache.subdivs * SettingsDMCSampler.subdivs_mult))
			ofile.write("\n\tsample_size= %.6f;" % SettingsLightCache.sample_size)
			ofile.write("\n\tnum_passes= %i;"% (scene.render.threads if SettingsLightCache.num_passes_auto else SettingsLightCache.num_passes))
			ofile.write("\n\tdepth= %i;" % SettingsLightCache.depth)
			ofile.write("\n\tfilter_type= %i;" % (FILTER_TYPE[SettingsLightCache.filter_type] if SettingsLightCache.filter else 0))
			ofile.write("\n\tfilter_samples= %i;" % (SettingsLightCache.filter_samples if SettingsLightCache.filter else 1))
			ofile.write("\n\tfilter_size= %.6f;" % SettingsLightCache.filter_size)
			ofile.write("\n\tprefilter= %i;" % SettingsLightCache.prefilter)
			ofile.write("\n\tprefilter_samples= %i;" % SettingsLightCache.prefilter_samples)
			ofile.write("\n\tshow_calc_phase= %i;" % SettingsLightCache.show_calc_phase)
			ofile.write("\n\tstore_direct_light= %i;" % SettingsLightCache.store_direct_light)
			ofile.write("\n\tuse_for_glossy_rays= %i;" % SettingsLightCache.use_for_glossy_rays)
			ofile.write("\n\tworld_scale= %i;" % WORLD_SCALE[SettingsLightCache.world_scale])
			ofile.write("\n\tadaptive_sampling= %i;" % SettingsLightCache.adaptive_sampling)
			ofile.write("\n\tmode= %d;" % LC_MODE[SettingsLightCache.mode])
			ofile.write("\n\tauto_save= %d;" % SettingsLightCache.auto_save)
			ofile.write("\n\tauto_save_file= \"%s\";" % lc_auto_save_path)
			ofile.write("\n\tfile= \"%s\";" % get_full_filepath(bus, None, SettingsLightCache.file))
			ofile.write("\n\tdont_delete= false;")
			ofile.write("\n\tmultiple_views= %d;" % SettingsLightCache.multiple_views)
			ofile.write("\n\tretrace_enabled= %d;" % SettingsLightCache.retrace_enabled)
			ofile.write("\n\tretrace_threshold= %.3f;" % SettingsLightCache.retrace_threshold)			
			ofile.write("\n}\n")
