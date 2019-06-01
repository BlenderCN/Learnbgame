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


''' Python modules '''
import os
import sys
import math

''' Blender modules '''
import bpy
from bpy.props import *

''' vb modules '''
from vb25.utils import *
from vb25       import dbg


PLUGINS_DIRS = []
PLUGINS= {
	'BRDF':          {},
	'CAMERA':        {},
	'GEOMETRY':      {},
	'LIGHT':         {},
	'MATERIAL':      {},
	'OBJECT':        {},
	'RENDERCHANNEL': {},
	'SETTINGS':      {},
	'SLOT':          {},
	'TEXTURE':       {},
	'WORLD':         {},

	'NODE':          {},
}


# Load settings to the RNA Pointer
def load_plugins(plugins, rna_pointer):
	for key in plugins:
		plugins[key].add_properties(rna_pointer)

def gen_material_menu_items(plugins):
	plugs= [plugins[plug] for plug in plugins if hasattr(plugins[plug], 'PID') and hasattr(plugins[plug], 'MAIN_BRDF')]

	# We need to sort plugins by PID so that adding new plugins
	# won't mess enum indexes in existing scenes
	plugs= sorted(plugs, key=lambda plug: plug.PID)

	enum_items= []
	for plugin in plugs:
		if hasattr(plugin,'ID'):
			ui_label= plugin.UI if hasattr(plugin,'UI') else plugin.NAME
			enum_items.append((plugin.ID, ui_label, plugin.DESC))

	return enum_items

def gen_menu_items(plugins, none_item= True):
	plugs= [plugins[plug] for plug in plugins if hasattr(plugins[plug], 'PID')]

	# We need to sort plugins by PID so that adding new plugins
	# won't mess enum indexes in existing scenes
	plugs= sorted(plugs, key=lambda plug: plug.PID)

	enum_items= []
	if none_item:
		enum_items.append(('NONE', "None", ""))
	for plugin in plugs:
		if hasattr(plugin,'ID'):
			ui_label= plugin.UI if hasattr(plugin,'UI') else plugin.NAME
			enum_items.append((plugin.ID, ui_label, plugin.DESC))

	# print("<Debug information. Remove this from release!>")
	# for item in enum_items:
	# 	print(" ", item)

	return enum_items


base_dir= get_vray_exporter_path()
if base_dir is not None:
	plugins_dir= os.path.join(base_dir,"plugins")

	if not plugins_dir in sys.path:
		PLUGINS_DIRS.append(plugins_dir)
		sys.path.append(plugins_dir)

	plugins_files= [fname[:-3] for fname in os.listdir(plugins_dir) if fname and fname.endswith(".py") and not fname == "__init__.py"]
	plugins= [__import__(fname) for fname in plugins_files]

	for plugin in plugins:
		PLUGINS[plugin.TYPE][plugin.ID]= plugin

else:
	debug(None, "Plugins not found!", error= True)


def add_properties():
	class VRayCamera(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(VRayCamera)

	class VRayObject(bpy.types.PropertyGroup):
		overrideWithScene = BoolProperty(
			name        = "Override With VRScene Asset",
			description = "Override with *.vrscene asset",
			default     = False
		)

		scenePrefix = StringProperty(
			name        = "Prefix",
			description = "Scene object name prefix"
		)

		sceneFilepath = StringProperty(
			name        = "File Path",
			subtype     = 'FILE_PATH',
			description = "Path to a *.vrscene file"
		)

		sceneDirpath = StringProperty(
			name        = "Directory Path",
			subtype     = 'DIR_PATH',
			description = "Path to a directory with *.vrscene files"
		)

		sceneReplace = BoolProperty(
			name        = "Override Current Scene Objects",
			description = "Replace objects in the root scene",
			default     = False
		)

		sceneUseTransform = BoolProperty(
			name        = "Use Transform",
			description = "Use Empty transform as scene transform",
			default     = True
		)

		sceneAddNodes = BoolProperty(
			name        = "Add Nodes",
			description = "Add nodes from the included files",
			default     = True
		)

		sceneAddMaterials = BoolProperty(
			name        = "Add Materials",
			description = "Add materials from the included files",
			default     = True
		)

		sceneAddLights = BoolProperty(
			name        = "Add Lights",
			description = "Add lights from the included files",
			default     = True
		)

		sceneAddCameras = BoolProperty(
			name        = "Add Cameras",
			description = "Add cameras from the included files",
			default     = False
		)

		sceneAddEnvironment = BoolProperty(
			name        = "Add Environment",
			description = "Add environment from the included files",
			default     = False
		)

		fade_radius= FloatProperty(
			name= "Sphere fade radius",
			description= "Sphere fade gizmo radiusBeam radius",
			min= 0.0,
			max= 10000.0,
			soft_min= 0.0,
			soft_max= 100.0,
			precision= 3,
			default= 1.0
		)
	bpy.utils.register_class(VRayObject)

	class VRayMesh(bpy.types.PropertyGroup):
		override = BoolProperty(
			name        = "Override",
			description = "Override mesh",
			default     = False
		)

		override_type = EnumProperty(
			name        = "Override",
			description = "Override geometry type",
			items = (
				('VRAYPROXY', "VRayProxy", ""),
				('VRAYPLANE', "VRayPlane", ""),
			),
			default = 'VRAYPROXY'
		)

	bpy.utils.register_class(VRayMesh)

	class VRayMaterial(bpy.types.PropertyGroup):
		dontOverride = BoolProperty(
			name        = "Don't Override",
			description = "Don't override material",
			default     = False
		)

		nodetree = StringProperty(
			name        = "Node Tree",
			description = "Name of the shader node tree for material",
			default     = ""
		)
	bpy.utils.register_class(VRayMaterial)

	class VRayLight(bpy.types.PropertyGroup):
		nodetree = StringProperty(
			name        = "Node Tree",
			description = "Name of the shader node tree for lamp",
			default     = ""
		)

		dome_targetRadius= FloatProperty(
			name= "Target Radius",
			description= "Target Radius",
			min= 0.0,
			max= 10000.0,
			soft_min= 0.0,
			soft_max= 200.0,
			precision= 3,
			default= 100
		)

		dome_emitRadius= FloatProperty(
			name= "Emit Radius",
			description= "Emit Radius",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 150
		)

		dome_spherical= BoolProperty(
			name= "Spherical",
			description= "Use sphere instead of half-sphere",
			default= False
		)

		dome_rayDistanceMode= BoolProperty(
			name= "Use Ray Distance",
			description= "When enabled the distance at which shadow rays are traced will be limited to the value of \"Ray Distance\" parameter",
			default= False
		)

		dome_rayDistance= FloatProperty(
			name= "Ray Distance",
			description= "specifies the maximum distance to which shadow rays are going to be traced",
			min= 0.0,
			max= 10000000.0,
			soft_min= 50000.0,
			soft_max= 200000.0,
			precision= 2,
			default= 100000.0
		)

		# Move to Light plugin
		enabled= BoolProperty(
			name= "Enabled",
			description= "Turns the light on and off",
			default= True
		)

		units= EnumProperty(
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

		fallsize= FloatProperty(
			name= "Beam radius",
			description= "Beam radius, 0.0 if the light has no beam radius",
			min= 0.0,
			max= 10000.0,
			soft_min= 0.0,
			soft_max= 100.0,
			precision= 3,
			default= 1.0
		)

		omni_type= EnumProperty(
			name= "Omni type",
			description= "Omni light type",
			items= (
				('OMNI',    "Omni",    ""),
				('AMBIENT', "Ambient", ""),
			),
			default= 'OMNI'
		)

		ambientShade= FloatProperty(
			name= "Ambient Shade",
			description= "Ambient Shade",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 2.0,
			precision= 3,
			default= 1.0
		)

		direct_type= EnumProperty(
			name= "Direct type",
			description= "Direct light type",
			items= (
				('DIRECT', "Direct", ""),
				('SUN',    "Sun",    ""),
			),
			default= 'DIRECT'
		)

		spot_type= EnumProperty(
			name= "Spot type",
			description= "Spot light subtype",
			items= (
				('SPOT', "Spot", ""),
				('IES',  "IES",  ""),
			),
			default= 'SPOT'
		)

		shadowShape = EnumProperty(
			name = "Shadow Shape",
			description = "Shadow shape",
			items = (
				('0', "Box", ""),
				('1', "Sphere", ""),
			),
			default = '1'
		)

		shadows= BoolProperty(
			name= "Shadows",
			description= "Produce shadows",
			default= True
		)

		affectDiffuse= BoolProperty(
			name= "Affect diffuse",
			description= "Produces diffuse lighting",
			default= True
		)

		affectSpecular= BoolProperty(
			name= "Affect specular",
			description= "Produces specular hilights",
			default= True
		)

		affectReflections= BoolProperty(
			name= "Affect reflections",
			description= "Appear in reflections",
			default= False
		)

		shadowColor= FloatVectorProperty(
			name= "Shadow color",
			description= "The shadow color. Anything but black is not physically accurate",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0.0,0.0,0.0)
		)

		shadowBias= FloatProperty(
			name= "Shadow bias",
			description= "Shadow offset from the surface. Helps to prevent polygonal shadow artifacts on low-poly surfaces",
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			precision= 3,
			default= 0.0
		)

		shadowSubdivs= IntProperty(
			name= "Shadow subdivs",
			description= "This value controls the number of samples V-Ray takes to compute area shadows. Lower values mean more noisy results, but will render faster. Higher values produce smoother results but take more time",
			min= 0,
			max= 256,
			default= 8
		)

		shadowRadius= FloatProperty(
			name= "Shadow radius",
			description= "Shadow radius",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0
		)

		decay= FloatProperty(
			name= "Decay",
			description= "Light decay",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 4.0,
			precision= 3,
			default= 2
		)

		cutoffThreshold= FloatProperty(
			name= "Cutoff threshold",
			description= "Light cut-off threshold (speed optimization). If the light intensity for a point is below this threshold, the light will not be computed",
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 0.1,
			precision= 3,
			default= 0.001
		)

		intensity= FloatProperty(
			name= "Intensity",
			description= "Light intensity",
			min= 0.0,
			max= 10000000.0,
			soft_min= 0.0,
			soft_max= 100.0,
			precision= 4,
			default= 30
		)

		subdivs= IntProperty(
			name= "Subdivs",
			description= "This controls the number of samples for the area shadow. More subdivs produce area shadows with better quality but render slower",
			min= 0,
			max= 256,
			default= 8
		)

		storeWithIrradianceMap= BoolProperty(
			name= "Store with irradiance map",
			description= "When this option is on and GI calculation is set to Irradiance map V-Ray will calculate the effects of the VRayLightRect and store them in the irradiance map",
			default= False
		)

		invisible= BoolProperty(
			name= "Invisible",
			description= "This setting controls whether the shape of the light source is visible in the render result",
			default= False
		)

		noDecay= BoolProperty(
			name= "No decay",
			description= "When this option is on the intensity will not decay with distance",
			default= False
		)

		doubleSided= BoolProperty(
			name= "Double-sided",
			description= "This option controls whether light is beamed from both sides of the plane",
			default= False
		)

		lightPortal= EnumProperty(
			name= "Light portal mode",
			description= "Specifies if the light is a portal light",
			items= (
				('NORMAL',"Normal light",""),
				('PORTAL',"Portal",""),
				('SPORTAL',"Simple portal","")
			),
			default= 'NORMAL'
		)

		radius= FloatProperty(
			name= "Radius",
			description= "Sphere light radius",
			min= 0.0,
			max= 10000.0,
			soft_min= 0.0,
			soft_max= 1.0,
			precision= 3,
			default= 0.0
		)

		sphere_segments= IntProperty(
			name= "Sphere segments",
			description= "Controls the quality of the light object when it is visible either directly or in reflections",
			min= 0,
			max= 100,
			default= 20
		)

		bumped_below_surface_check= BoolProperty(
			name= "Bumped below surface check",
			description= "If the bumped normal should be used to check if the light dir is below the surface",
			default= False
		)

		nsamples= IntProperty(
			name= "Motion blur samples",
			description= "Motion blur samples",
			min= 0,
			max= 10,
			default= 0
		)

		diffuse_contribution= FloatProperty(
			name= "Diffuse contribution",
			description= "A multiplier for the effect of the light on the diffuse",
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			precision= 3,
			default= 1
		)

		specular_contribution= FloatProperty(
			name= "Specular contribution",
			description= "A multiplier for the effect of the light on the specular",
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			precision= 3,
			default= 1
		)

		areaSpeculars= BoolProperty(
			name= "Area speculars",
			description= "When this parameter is enabled, the specular highlights will be computed with the real light shape as defined in the .ies files",
			default= False
		)

		ignoreLightNormals= BoolProperty(
			name= "Ignore light normals",
			description= "When this option is off, more light is emitted in the direction of the source surface normal",
			default= True
		)

		tex_resolution= IntProperty(
			name= "Tex resolution",
			description= "Specifies the resolution at which the texture is sampled when the \"Tex Adaptive\" option is checked",
			min= 1,
			max= 20000,
			soft_max = 1024,
			default= 512
		)

		tex_adaptive= BoolProperty(
			name= "Tex adaptive",
			description= "When this option is checked V-Ray will use impotance sampling on the texture in order to produce better shadows",
			default= True
		)

		causticSubdivs= IntProperty(
			name= "Caustic subdivs",
			description= "Caustic subdivisions. Lower values mean more noisy results, but will render faster. Higher values produce smoother results but take more time",
			min= 0,
			default= 1000
		)

		causticMult= FloatProperty(
			name= "Caustics multiplier",
			description= "Caustics multiplier",
			min= 0.0,
			soft_min= 0.0,
			precision= 3,
			default= 1
		)

		ies_file= StringProperty(
			name= "IES file",
			subtype= 'FILE_PATH',
			description= "IES file"
		)

		soft_shadows= BoolProperty(
			name= "Soft shadows",
			description= "Use the shape of the light as described in the IES profile",
			default= True
		)

		turbidity= FloatProperty(
			name= "Turbidity",
			description= "This parameter determines the amount of dust in the air and affects the color of the sun and sky",
			min= 2.0,
			max= 100.0,
			soft_min= 2.0,
			soft_max= 6.0,
			precision= 3,
			default= 3.0
		)

		intensity_multiplier= FloatProperty(
			name= "Intensity multiplier",
			description= "This is an intensity multiplier for the Sun",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			precision= 4,
			default= 1.0
		)

		ozone= FloatProperty(
			name= "Ozone",
			description= "This parameter affects the color of the sun light",
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			precision= 3,
			default= 0.35
		)

		water_vapour= FloatProperty(
			name= "Water vapour",
			description= "Water vapour",
			min= 0.0,
			max= 10.0,
			soft_min= 0.0,
			soft_max= 2.0,
			precision= 3,
			default= 2
		)

		size_multiplier= FloatProperty(
			name= "Size",
			description= "This parameter controls the visible size of the sun",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 1
		)

		horiz_illum= FloatProperty(
			name= "Horiz illumination",
			description= "Specifies the intensity (in lx) of the illumination on horizontal surfaces coming from the Sky",
			min= 0.0,
			max= 100000.0,
			soft_min= 0.0,
			soft_max= 100000.0,
			precision= 0,
			default= 25000
		)

		sky_model= EnumProperty(
			name= "Sky model",
			description= "Allows you to specify the procedural model that will be used to generate the VRaySky texture",
			items= (
				('CIEOVER',"CIE Overcast",""),
				('CIECLEAR',"CIE Clear",""),
				('PREETH',"Preetham et al.","")
			),
			default= 'PREETH'
		)

		ies_light_shape = BoolProperty (
			name        = "Define shape",
			description = "IES light shape; if False the default light shape from IES profile is used",
			default     = False
		)

		ies_light_shape_lock = BoolProperty (
			name        = "Shape controls lock",
			description = "Change width, height and length simultaneously",
			default     = True
		)

		ies_light_width= FloatProperty(
			name        = "Width",
			description = "Light shape width",
			min         = 0,
			max         = 100,
			default     = 0
		)

		ies_light_length= FloatProperty(
			name        = "Length",
			description = "Light shape length",
			min         = 0,
			max         = 100,
			default     = 0
		)

		ies_light_height= FloatProperty(
			name        = "Height",
			description = "Light shape height",
			min         = 0,
			max         = 100,
			default     = 0
		)

		ies_light_diameter= FloatProperty(
			name        = "Diameter",
			description = "Light shape diameter",
			min         = 0,
			max         = 100,
			default     = 0
		)

	bpy.utils.register_class(VRayLight)

	class VRayWorld(bpy.types.PropertyGroup):
		# Move to World plugin
		bg_color= FloatVectorProperty(
			name= "Background color",
			description= "Background color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0.0,0.0,0.0)
		)

		bg_color_mult= FloatProperty(
			name= "Background color multiplier",
			description= "Background color multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 2.0,
			precision= 3,
			default= 1.0
		)

		gi_override= BoolProperty(
			name= "Override color for GI",
			description= "Override color for GI",
			default= False
		)

		gi_color= FloatVectorProperty(
			name= "GI color",
			description= "GI (skylight) color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0.0,0.0,0.0)
		)

		gi_color_mult= FloatProperty(
			name= "GI color multiplier",
			description= "GI color multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 2.0,
			precision= 3,
			default= 1.0
		)

		reflection_override= BoolProperty(
			name= "Override color for reflection",
			description= "Override color for reflection",
			default= False
		)

		reflection_color= FloatVectorProperty(
			name= "Reflection color",
			description= "Reflection (skylight) color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0.0,0.0,0.0)
		)

		reflection_color_mult= FloatProperty(
			name= "Reflection color multiplier",
			description= "Reflection color multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 2.0,
			precision= 3,
			default= 1.0
		)

		refraction_override= BoolProperty(
			name= "Override color for refraction",
			description= "Override color for refraction",
			default= False
		)

		refraction_color= FloatVectorProperty(
			name= "Refraction color",
			description= "Refraction (skylight) color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0.0,0.0,0.0)
		)

		refraction_color_mult= FloatProperty(
			name= "Refraction color multiplier",
			description= "Refraction color multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 2.0,
			precision= 3,
			default= 1.0
		)

		global_light_level= FloatProperty(
			name= "Global light level",
			description= "A global light level multiplier for all lights",
			min= 0.001,
			max= 1000.0,
			soft_min= 0.001,
			soft_max= 2.0,
			precision= 3,
			default= 1.0,
		)
	bpy.utils.register_class(VRayWorld)

	class VRayLightSlot(bpy.types.PropertyGroup):
		# Move to Slot plugin
		map_color= BoolProperty(
			name= "Color",
			description= "Color texture",
			default= True
		)

		color_mult= FloatProperty(
			name= "Color texture multiplier",
			description= "Color texture multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		map_shadowColor= BoolProperty(
			name= "Shadow",
			description= "Shadow color texture",
			default= False
		)

		shadowColor_mult= FloatProperty(
			name= "Shadow color texture multiplier",
			description= "Shadow color texture multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		map_intensity= BoolProperty(
			name= "Intensity",
			description= "Intensity texture",
			default= False
		)

		intensity_mult= FloatProperty(
			name= "Intensity texture multiplier",
			description= "Intensity texture multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)
	bpy.utils.register_class(VRayLightSlot)

	class VRaySlot(bpy.types.PropertyGroup):
		# Move to Slot plugin
		uvwgen= StringProperty(
			name= "UVW Generator",
			subtype= 'NONE',
			options= {'HIDDEN'},
			description= "UVW generator name",
			default= "UVWGenChannel_default"
		)

		blend_mode= EnumProperty(
			name= "Blend mode",
			description= "Blend mode",
			items= (
				('NONE',        "None",       ""),
				('OVER',        "Over",       ""),
				('IN',          "In",         ""),
				('OUT',         "Out",        ""),
				('ADD',         "Add",        ""),
				('SUBTRACT',    "Subtract",   ""),
				('MULTIPLY',    "Multiply",   ""),
				('DIFFERENCE',  "Difference", ""),
				('LIGHTEN',     "Lighten",    ""),
				('DARKEN',      "Darken",     ""),
				('SATURATE',    "Saturate",   ""),
				('DESATUREATE', "Desaturate", ""),
				('ILLUMINATE',  "Illuminate", ""),
			),
			default= 'OVER'
		)

		texture_rot= FloatProperty(
			name= "Rotation",
			description= "Texture rotation",
			subtype= 'ANGLE',
			min= -2.0 * math.pi,
			max=  2.0 * math.pi,
			soft_min= -math.pi,
			soft_max=  math.pi,
			default= 0.0
		)

		texture_rotation_h= FloatProperty(
			name= "Horiz. rotation",
			description= "Horizontal rotation",
			subtype= 'ANGLE',
			min= -2.0 * math.pi,
			max=  2.0 * math.pi,
			soft_min= -math.pi,
			soft_max=  math.pi,
			default= 0.0
		)

		texture_rotation_v= FloatProperty(
			name= "Vert. rotation",
			description= "Vertical rotation",
			subtype= 'ANGLE',
			min= -2.0 * math.pi,
			max=  2.0 * math.pi,
			soft_min= -math.pi,
			soft_max=  math.pi,
			default= 0.0
		)

		texture_rotation_w= FloatProperty(
			name= "W rotation",
			description= "W rotation",
			subtype= 'ANGLE',
			min= -2.0 * math.pi,
			max=  2.0 * math.pi,
			soft_min= -math.pi,
			soft_max=  math.pi,
			default= 0.0
		)

		'''
		  MAPTO
		'''
		map_diffuse= BoolProperty(
			name= "Diffuse",
			description= "Diffuse texture",
			default= True
		)

		map_diffuse_invert= BoolProperty(
			name= "Invert diffuse",
			description= "Invert diffuse texture",
			default= False
		)

		diffuse_mult= FloatProperty(
			name= "Diffuse texture multiplier",
			description= "Diffuse texture multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		map_displacement= BoolProperty(
			name= "Displacement",
			description= "Displacement texture",
			default= False
		)

		map_displacement_invert= BoolProperty(
			name= "Invert displacement texture",
			description= "Invert displacement texture",
			default= False
		)

		displacement_mult= FloatProperty(
			name= "Displacement texture multiplier",
			description= "Displacement texture multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		map_normal= BoolProperty(
			name= "Normal",
			description= "Normal texture",
			default= False
		)

		map_normal_invert= BoolProperty(
			name= "Invert normal texture",
			description= "Invert normal texture",
			default= False
		)

		normal_mult= FloatProperty(
			name= "Normal texture multiplier",
			description= "Normal texture multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		map_opacity= BoolProperty(
			name= "Opacity",
			description= "Opacity texture",
			default= False
		)

		map_opacity_invert= BoolProperty(
			name= "Invert opacity texture",
			description= "Invert opacity texture",
			default= False
		)

		opacity_mult= FloatProperty(
			name= "Opacity texture multiplier",
			description= "Opacity texture multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		map_roughness= BoolProperty(
			name= "Roughness",
			description= "Roughness texture",
			default= False
		)

		map_roughness_invert= BoolProperty(
			name= "Invert roughness texture",
			description= "Invert roughness texture",
			default= False
		)

		roughness_mult= FloatProperty(
			name= "Roughness texture multiplier",
			description= "Roughness texture multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		map_reflect= BoolProperty(
			name= "Reflection",
			description= "Reflection texture",
			default= False
		)

		map_reflect_invert= BoolProperty(
			name= "Invert reflection texture",
			description= "Invert reflection texture",
			default= False
		)

		map_reflect_invert= BoolProperty(
			name= "Invert reflection",
			description= "Invert reflection texture",
			default= False
		)

		reflect_mult= FloatProperty(
			name= "Reflection texture multiplier",
			description= "Reflection texture multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		map_reflect_glossiness= BoolProperty(
			name= "Reflection glossiness",
			description= "Reflection glossiness texture",
			default= False
		)

		map_reflect_glossiness_invert= BoolProperty(
			name= "Invert reflection glossiness texture",
			description= "Invert reflection glossiness texture",
			default= False
		)

		reflect_glossiness_mult= FloatProperty(
			name= "Reflection glossiness texture multiplier",
			description= "Reflection glossiness texture multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		map_hilight_glossiness= BoolProperty(
			name= "Hilight glossiness",
			description= "Hilight glossiness texture",
			default= False
		)

		map_hilight_glossiness_invert= BoolProperty(
			name= "Invert hilight_glossiness texture",
			description= "Invert hilight_glossiness texture",
			default= False
		)

		hilight_glossiness_mult= FloatProperty(
			name= "Hilight glossiness texture multiplier",
			description= "Hilight glossiness texture multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		map_anisotropy= BoolProperty(
			name= "Anisotropy",
			description= "Anisotropy texture",
			default= False
		)

		map_anisotropy_invert= BoolProperty(
			name= "Invert anisotropy texture",
			description= "Invert anisotropy texture",
			default= False
		)

		anisotropy_mult= FloatProperty(
			name= "Anisotropy texture multiplier",
			description= "Anisotropy texture multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		map_anisotropy_rotation= BoolProperty(
			name= "Anisotropy rotation",
			description= "Anisotropy rotation texture",
			default= False
		)

		map_anisotropy_rotation_invert= BoolProperty(
			name= "Invert anisotropy rotation texture",
			description= "Invert anisotropy rotation texture",
			default= False
		)

		anisotropy_rotation_mult= FloatProperty(
			name= "Anisotropy rotation texture multiplier",
			description= "Anisotropy rotation texture multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		map_fresnel_ior= BoolProperty(
			name= "Fresnel IOR",
			description= "Fresnel IOR texture",
			default= False
		)

		map_fresnel_ior_invert= BoolProperty(
			name= "Invert fresnel IOR texture",
			description= "Invert fresnel IOR texture",
			default= False
		)

		fresnel_ior_mult= FloatProperty(
			name= "Fresnel IOR texture multiplier",
			description= "Fresnel IOR texture multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		map_refract= BoolProperty(
			name= "Refraction",
			description= "Refraction texture",
			default= False
		)

		map_refract_invert= BoolProperty(
			name= "Invert refraction texture",
			description= "Invert refraction texture",
			default= False
		)

		refract_mult= FloatProperty(
			name= "Refraction texture multiplier",
			description= "Refraction texture multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		map_refract_ior= BoolProperty(
			name= "Refraction IOR",
			description= "Refraction IOR texture",
			default= False
		)

		map_refract_ior_invert= BoolProperty(
			name= "Invert refraction IOR texture",
			description= "Invert refraction IOR texture",
			default= False
		)

		refract_ior_mult= FloatProperty(
			name= "Refraction IOR texture multiplier",
			description= "Refraction IOR texture multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		map_refract_glossiness= BoolProperty(
			name= "Refraction glossiness",
			description= "Refraction glossiness texture",
			default= False
		)


		map_refract_glossiness_invert= BoolProperty(
			name= "Invert refraction glossiness texture",
			description= "Invert refraction glossiness texture",
			default= False
		)

		refract_glossiness_mult= FloatProperty(
			name= "Refraction glossiness texture multiplier",
			description= "Refraction glossiness texture multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		map_translucency_color= BoolProperty(
			name= "Translucency",
			description= "Translucency texture",
			default= False
		)

		map_translucency_color_invert= BoolProperty(
			name= "Invert translucency texture",
			description= "Invert translucency texture",
			default= False
		)

		translucency_color_mult= FloatProperty(
			name= "Translucency texture multiplier",
			description= "Translucency texture multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)


		'''
		  BRDFCarPaint
		'''
		map_coat= BoolProperty(
			name= "Overall color",
			description= "Overall color",
			default= False
		)

		coat_mult= FloatProperty(
			name= "Coat texture multiplier",
			description= "Coat texture multiplier",
			min=0.0,
			max=100.0,
			soft_min=0.0,
			soft_max=1.0,
			default=1.0
		)

		map_flake= BoolProperty(
			name= "Overall color",
			description= "Overall color",
			default= False
		)

		flake_mult= FloatProperty(
			name= "Flake texture multiplier",
			description= "Flake texture multiplier",
			min=0.0,
			max=100.0,
			soft_min=0.0,
			soft_max=1.0,
			default=1.0
		)

		map_base= BoolProperty(
			name= "Overall color",
			description= "Overall color",
			default= False
		)

		base_mult= FloatProperty(
			name= "Base texture multiplier",
			description= "Base texture multiplier",
			min=0.0,
			max=100.0,
			soft_min=0.0,
			soft_max=1.0,
			default=1.0
		)


		'''
		  BRDFSSS2Complex
		'''
		map_overall_color= BoolProperty(
			name= "Overall color",
			description= "Overall color",
			default= False
		)

		overall_color_mult= FloatProperty(
			name= "Overall color multiplier",
			description= "Overall color multiplier",
			min=0.0,
			max=100.0,
			soft_min=0.0,
			soft_max=1.0,
			default=1.0
		)

		map_diffuse_color= BoolProperty(
			name= "Diffuse color",
			description= "Diffuse color",
			default= False
		)

		diffuse_color_mult= FloatProperty(
			name= "Diffuse color multiplier",
			description= "Diffuse color multiplier",
			min=0.0,
			max=100.0,
			soft_min=0.0,
			soft_max=1.0,
			default=1.0
		)

		map_diffuse_amount= BoolProperty(
			name= "Diffuse amount",
			description= "Diffuse amount",
			default= False
		)

		diffuse_amount_mult= FloatProperty(
			name= "Diffuse amount multiplier",
			description= "Diffuse amount multiplie",
			min=0.0,
			max=100.0,
			soft_min=0.0,
			soft_max=1.0,
			default=1.0
		)

		map_sub_surface_color= BoolProperty(
			name= "Sub-surface color",
			description= "Sub-surface color",
			default= False
		)

		sub_surface_color_mult= FloatProperty(
			name= "Sub-surface color multiplier",
			description= "Sub-surface color multiplier",
			min=0.0,
			max=100.0,
			soft_min=0.0,
			soft_max=1.0,
			default=1.0
		)

		map_scatter_radius= BoolProperty(
			name= "Scatter radius",
			description= "Scatter radius",
			default= False
		)

		scatter_radius_mult= FloatProperty(
			name= "Scatter radius multiplier",
			description= "Scatter radius multiplier",
			min=0.0,
			max=100.0,
			soft_min=0.0,
			soft_max=1.0,
			default=1.0
		)

		map_specular_color= BoolProperty(
			name= "Specular color",
			description= "Specular color",
			default= False
		)

		specular_color_mult= FloatProperty(
			name= "Specular color multiplier",
			description= "Specular color multiplier",
			min=0.0,
			max=100.0,
			soft_min=0.0,
			soft_max=1.0,
			default=1.0
		)

		map_specular_amount= BoolProperty(
			name= "Specular amount",
			description= "Specular amoun",
			default= False
		)

		specular_amount_mult= FloatProperty(
			name= "Specular amount multiplier",
			description= "Specular amount multiplier",
			min=0.0,
			max=100.0,
			soft_min=0.0,
			soft_max=1.0,
			default=1.0
		)

		map_specular_glossiness= BoolProperty(
			name= "Specular glossiness",
			description= "Specular glossiness",
			default= False
		)

		specular_glossiness_mult= FloatProperty(
			name= "Specular glossiness multiplier",
			description= "Specular glossiness multiplier",
			min=0.0,
			max=100.0,
			soft_min=0.0,
			soft_max=1.0,
			default=1.0
		)


		'''
		  EnvironmentFog
		'''
		map_emission_tex= BoolProperty(
			name= "Emission",
			description= "Emission texture",
			default= False
		)

		emission_tex_mult= FloatProperty(
			name= "Emission texture multiplier",
			description= "Emission texture multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		map_color_tex= BoolProperty(
			name= "Color",
			description= "Color texture",
			default= False
		)

		color_tex_mult= FloatProperty(
			name= "Color texture multiplier",
			description= "Color texture multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		map_density_tex= BoolProperty(
			name= "Density",
			description= "Density texture",
			default= False
		)

		density_tex_mult= FloatProperty(
			name= "Density texture multiplier",
			description= "Density texture multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		map_fade_out_tex= BoolProperty(
			name= "Fade out",
			description= "Fade out texture",
			default= False
		)

		fade_out_tex_mult= FloatProperty(
			name= "Fade out texture multiplier",
			description= "Fade out texture multiplier",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		use_map_env_bg= BoolProperty(
			name= "Background",
			description= "Background",
			default= True
		)

		use_map_env_bg_invert= BoolProperty(
			name= "Invert background texture",
			description= "Invert background texture",
			default= False
		)

		env_bg_factor= FloatProperty(
			name= "Background texture multiplier",
			description= "Background texture multiplier",
			min= 0.0,
			max= 10000.0,
			soft_min= 0.0,
			soft_max= 2.0,
			precision= 3,
			default= 1.0
		)

		use_map_env_gi= BoolProperty(
			name= "GI",
			description= "Override for GI",
			default= False
		)

		use_map_env_gi_invert= BoolProperty(
			name= "Invert GI texture",
			description= "Invert GI texture",
			default= False
		)

		env_gi_factor= FloatProperty(
			name= "GI texture multiplier",
			description= "GI texture multiplier",
			min= 0.0,
			max= 10000.0,
			soft_min= 0.0,
			soft_max= 2.0,
			precision= 3,
			default= 1.0
		)

		use_map_env_reflection= BoolProperty(
			name= "Reflection",
			description= "Override for Reflection",
			default= False
		)

		use_map_env_reflection_invert= BoolProperty(
			name= "Invert reflection texture",
			description= "Invert reflection texture",
			default= False
		)

		env_reflection_factor= FloatProperty(
			name= "Reflection texture multiplier",
			description= "Reflection texture multiplier",
			min= 0.0,
			max= 10000.0,
			soft_min= 0.0,
			soft_max= 2.0,
			precision= 3,
			default= 1.0
		)

		use_map_env_refraction= BoolProperty(
			name= "Refraction",
			description= "Override for Refraction",
			default= False
		)

		use_map_env_refraction_invert= BoolProperty(
			name= "Invert refraction texture",
			description= "Invert refraction texture",
			default= False
		)

		env_refraction_factor= FloatProperty(
			name= "Refraction texture multiplier",
			description= "Refraction texture multiplier",
			min= 0.0,
			max= 10000.0,
			soft_min= 0.0,
			soft_max= 2.0,
			precision= 3,
			default= 1.0
		)
	bpy.utils.register_class(VRaySlot)

	VRaySlot.VRayLight= PointerProperty(
		name= "VRayLightSlot",
		type=  VRayLightSlot,
		description= "VRay lights texture slot settings"
	)

	class VRayTexture(bpy.types.PropertyGroup):
		type= EnumProperty(
			name= "Texture Type",
			description= "V-Ray texture type",
			items= (tuple(gen_menu_items(PLUGINS['TEXTURE']))),
			default= 'NONE'
		)
	bpy.utils.register_class(VRayTexture)

	class VRayRenderChannel(bpy.types.PropertyGroup):
		type= EnumProperty(
			name= "Channel Type",
			description= "Render channel type",
			items= (tuple(gen_menu_items(PLUGINS['RENDERCHANNEL']))),
			default= 'NONE'
		)

		use= BoolProperty(
			name= "",
			description= "Use render channel",
			default= True
		)
	bpy.utils.register_class(VRayRenderChannel)

	class VRayScene(bpy.types.PropertyGroup):
		render_channels= CollectionProperty(
			name= "Render Channels",
			type=  VRayRenderChannel,
			description= "V-Ray render channels"
		)

		render_channels_use= BoolProperty(
			name= "Use render channels",
			description= "Use render channels",
			default= False
		)

		render_channels_index= IntProperty(
			name= "Render Channel Index",
			default= -1,
			min= -1,
			max= 100
		)
	bpy.utils.register_class(VRayScene)

	class VRayFur(bpy.types.PropertyGroup):
		width= bpy.props.FloatProperty(
			name= "Width",
			description= "Hair thin",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 0.01,
			precision= 5,
			default= 0.0001
		)

		make_thinner= bpy.props.BoolProperty(
			name= "Make thinner",
			description= "Make hair thiner to the end [experimental]",
			default= False
		)

		thin_start= bpy.props.IntProperty(
			name= "Thin start segment",
			description= "Make hair thiner to the end",
			subtype= 'PERCENTAGE',
			min= 0,
			max= 100,
			soft_min= 0,
			soft_max= 100,
			default= 70
		)
	bpy.utils.register_class(VRayFur)

	class VRayParticleSettings(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(VRayParticleSettings)

	VRayParticleSettings.VRayFur= bpy.props.PointerProperty(
		name= "V-Ray Fur Settings",
		type=  VRayFur,
		description= "V-Ray Fur settings"
	)

	bpy.types.ParticleSettings.vray= bpy.props.PointerProperty(
		name= "V-Ray Particle Settings",
		type=  VRayParticleSettings,
		description= "V-Ray Particle settings"
	)

	bpy.types.Texture.vray= PointerProperty(
		name= "V-Ray Texture Settings",
		type=  VRayTexture,
		description= "V-Ray texture settings"
	)

	bpy.types.Texture.vray_slot= PointerProperty(
		name= "V-Ray Material Texture Slot",
		type=  VRaySlot,
		description= "V-Ray material texture slot settings"
	)

	bpy.types.Scene.vray= PointerProperty(
		name= "V-Ray Settings",
		type=  VRayScene,
		description= "V-Ray Renderer settings"
	)

	bpy.types.Material.vray= PointerProperty(
		name= "V-Ray Material Settings",
		type=  VRayMaterial,
		description= "V-Ray material settings"
	)

	bpy.types.Mesh.vray= PointerProperty(
		name= "V-Ray Mesh Settings",
		type=  VRayMesh,
		description= "V-Ray geometry settings"
	)

	bpy.types.Lamp.vray= PointerProperty(
		name= "V-Ray Lamp Settings",
		type=  VRayLight,
		description= "V-Ray lamp settings"
	)

	bpy.types.Curve.vray= PointerProperty(
		name= "V-Ray Curve Settings",
		type=  VRayMesh,
		description= "V-Ray geometry settings"
	)

	bpy.types.Camera.vray= PointerProperty(
		name= "V-Ray Camera Settings",
		type=  VRayCamera,
		description= "V-Ray Camera / DoF / Motion Blur settings"
	)

	bpy.types.Object.vray= PointerProperty(
		name= "V-Ray Object Settings",
		type=  VRayObject,
		description= "V-Ray Object Settings"
	)

	bpy.types.World.vray= PointerProperty(
		name= "V-Ray World Settings",
		type=  VRayWorld,
		description= "V-Ray world settings"
	)

	for pluginType in PLUGINS:
		for plugin in PLUGINS[pluginType]:
			if hasattr(PLUGINS[pluginType][plugin], 'register'):
				dbg.msg("%s.register()" % PLUGINS[pluginType][plugin].__name__)
				PLUGINS[pluginType][plugin].register()

	'''
	  Loading plugin properties
	'''
	load_plugins(PLUGINS['SETTINGS'],      VRayScene)
	load_plugins(PLUGINS['TEXTURE'],       VRayTexture)
	load_plugins(PLUGINS['GEOMETRY'],      VRayMesh)
	load_plugins(PLUGINS['CAMERA'],        VRayCamera)
	load_plugins(PLUGINS['MATERIAL'],      VRayMaterial)
	load_plugins(PLUGINS['RENDERCHANNEL'], VRayRenderChannel)
	load_plugins(PLUGINS['OBJECT'],        VRayObject)

	PLUGINS['SETTINGS']['SettingsEnvironment'].add_properties(VRayMaterial)
	PLUGINS['SETTINGS']['SettingsEnvironment'].add_properties(VRayObject)

	PLUGINS['MATERIAL']['MtlOverride'].add_properties(VRayObject)
	PLUGINS['MATERIAL']['MtlWrapper'].add_properties(VRayObject)
	PLUGINS['MATERIAL']['MtlRenderStats'].add_properties(VRayObject)

	PLUGINS['GEOMETRY']['LightMesh'].add_properties(VRayObject)
	PLUGINS['GEOMETRY']['LightMesh'].add_properties(VRayMaterial)
	PLUGINS['GEOMETRY']['GeomDisplacedMesh'].add_properties(VRayObject)
	PLUGINS['GEOMETRY']['GeomStaticSmoothedMesh'].add_properties(VRayObject)

	PLUGINS['BRDF']['BRDFBump'].add_properties(VRaySlot)
	PLUGINS['GEOMETRY']['GeomDisplacedMesh'].add_properties(VRaySlot)

	for key in PLUGINS['BRDF']:
		if key != 'BRDFBump':
			if key == 'BRDFLayered':
				load_plugins(PLUGINS['BRDF'], PLUGINS['BRDF']['BRDFLayered'].add_properties(VRayMaterial))
			else:
				PLUGINS['BRDF'][key].add_properties(VRayMaterial)


def remove_properties():
	global PLUGINS_DIRS

	for plugDir in PLUGINS_DIRS:
		if plugDir in sys.path:
			sys.path.remove(plugDir)
	PLUGINS_DIRS = []

	for pluginType in PLUGINS:
		for plugin in PLUGINS[pluginType]:
			if hasattr(PLUGINS[pluginType][plugin], 'unregister'):
				dbg.msg("%s.unregister()" % PLUGINS[pluginType][plugin].__name__)
				PLUGINS[pluginType][plugin].unregister()

	del bpy.types.Camera.vray
	del bpy.types.Lamp.vray
	del bpy.types.Material.vray
	del bpy.types.Mesh.vray
	del bpy.types.Object.vray
	del bpy.types.Scene.vray
	del bpy.types.Texture.vray
