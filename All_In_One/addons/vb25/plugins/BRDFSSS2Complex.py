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
from vb25.ui import ui


TYPE= 'BRDF'
ID=   'BRDFSSS2Complex'
PID=   2
MAIN_BRDF= True

NAME= 'BRDFSSS2Complex'
UI=   "SSS"
DESC= "Fast SSS 2 BRDF settings"

PARAMS= (
	'prepass_rate',
	'interpolation_accuracy',
	'scale',
	'ior',
	#'overall_color',
	#'diffuse_color',
	#'diffuse_amount',
	#'sub_surface_color',
	#'scatter_radius',
	'scatter_radius_mult',
	'phase_function',
	#'specular_color',
	#'specular_amount',
	#'specular_glossiness',
	'specular_subdivs',
	'cutoff_threshold',
	'trace_reflections',
	'reflection_depth',
	'single_scatter',
	'subdivs',
	'refraction_depth',
	'front_scatter',
	'back_scatter',
	'scatter_gi',
	'prepass_blur'
	#'channels'
)


def add_properties(rna_pointer):
	class VRAY_MT_preset_sss(bpy.types.Menu):
		bl_label= "SSS Presets"
		preset_subdir= os.path.join("..", "startup", "vb25", "presets", "sss")
		preset_operator = "script.execute_preset"
		draw = bpy.types.Menu.draw_preset
	bpy.utils.register_class(VRAY_MT_preset_sss)

	class BRDFSSS2Complex(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(BRDFSSS2Complex)

	rna_pointer.BRDFSSS2Complex= PointerProperty(
		name= "BRDFSSS2Complex",
		type=  BRDFSSS2Complex,
		description= "V-Ray BRDFSSS2Complex settings"
	)

	BRDFSSS2Complex.prepass_rate= IntProperty(
		name= "Prepass rate",
		description= "Sampling density for the illumination map",
		min= -10,
		max= 10,
		default= -1
	)

	BRDFSSS2Complex.interpolation_accuracy= FloatProperty(
		name= "Interpolation accuracy",
		description= "Interpolation accuracy for the illumination map; normally 1.0 is fine",
		min= 0.0,
		max= 10.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	BRDFSSS2Complex.scale= FloatProperty(
		name= "Scale",
		description= "Values below 1.0 will make the object look as if it is bigger. Values above 1.0 will make it look as if it is smalle",
		min= 0.0,
		max= 1000.0,
		soft_min= 0.0,
		soft_max= 1000.0,
		precision= 4,
		default= 1
	)

	BRDFSSS2Complex.ior= FloatProperty(
		name= "IOR",
		description= '',
		min= 0.0,
		max= 30.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.5
	)

	BRDFSSS2Complex.diffuse_amount= FloatProperty(
		name= "Diffuse amount",
		description= '',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		precision= 3,
		default= 0.0
	)

	BRDFSSS2Complex.scatter_radius= FloatVectorProperty(
		name= "Scatter radius",
		description= '',
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0.92,0.52,0.175)
	)

	BRDFSSS2Complex.scatter_radius_mult= FloatProperty(
		name= "Scatter radius",
		description= '',
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	BRDFSSS2Complex.overall_color= FloatVectorProperty(
		name= "Overall color",
		description= '',
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (1.0,1.0,1.0)
	)

	BRDFSSS2Complex.diffuse_color= FloatVectorProperty(
		name= "Diffuse color",
		description= '',
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0.5,0.5,0.5)
	)

	BRDFSSS2Complex.sub_surface_color= FloatVectorProperty(
		name= "Sub surface color",
		description= '',
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0.5,0.5,0.5)
	)

	BRDFSSS2Complex.phase_function= FloatProperty(
		name= "Phase function",
		description= '',
		min= -1.0,
		max= 1.0,
		soft_min= -1.0,
		soft_max= 1.0,
		precision= 3,
		default= 0
	)

	BRDFSSS2Complex.specular_color= FloatVectorProperty(
		name= "Specular color",
		description= "Specular color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (1.0,1.0,1.0)
	)

	BRDFSSS2Complex.specular_subdivs= IntProperty(
		name= "Specular subdivs",
		description= "Specular subdivs",
		min= 1,
		max= 1024,
		soft_min= 1,
		soft_max= 64,
		default= 8
	)

	BRDFSSS2Complex.specular_amount= FloatProperty(
		name= "Specular amount",
		description= "Specular amount",
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		precision= 3,
		default= 1
	)

	BRDFSSS2Complex.specular_glossiness= FloatProperty(
		name= "Specular glossiness",
		description= '',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		precision= 3,
		default= 0.6
	)

	BRDFSSS2Complex.cutoff_threshold= FloatProperty(
		name= "Cutoff",
		description= '',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		precision= 3,
		default= 0.01
	)

	BRDFSSS2Complex.trace_reflections= BoolProperty(
		name= "Trace reflections",
		description= "TODO",
		default= True
	)

	BRDFSSS2Complex.reflection_depth= IntProperty(
		name= "Reflection depth",
		description= '',
		min= 0,
		max= 10,
		default= 5
	)

	BRDFSSS2Complex.single_scatter= EnumProperty(
		name= "Single scatter",
		description= '',
		items= (
			('NONE',"None",""),
			('SIMPLE',"Simple",""),
			('SOLID',"Raytraced (solid)",""),
			('REFR',"Raytraced (refractive)","")
		),
		default= "SIMPLE"
	)

	BRDFSSS2Complex.subdivs= IntProperty(
		name= "Subdivs",
		description= '',
		min= 1,
		max= 1024,
		soft_min= 1,
		soft_max= 32,
		default= 8
	)

	BRDFSSS2Complex.refraction_depth= IntProperty(
		name= "Refraction depth",
		description= '',
		min= 0,
		max= 10,
		default= 5
	)

	BRDFSSS2Complex.front_scatter= BoolProperty(
		name= "Front scatter",
		description= '',
		default= True
	)

	BRDFSSS2Complex.back_scatter= BoolProperty(
		name= "Back scatter",
		description= '',
		default= True
	)

	BRDFSSS2Complex.scatter_gi= BoolProperty(
		name= "Scatter GI",
		description= '',
		default= False
	)

	BRDFSSS2Complex.prepass_blur= FloatProperty(
		name= "Prepass blur",
		description= '',
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.2
	)


def mapto(bus, BRDFLayered= None):
	scene= bus['scene']
	ma=    bus['material']['material']

	defaults= {}

	VRayMaterial=    ma.vray
	BRDFSSS2Complex= BRDFLayered.BRDFSSS2Complex if BRDFLayered else VRayMaterial.BRDFSSS2Complex

	if BRDFLayered:
		defaults['overall_color']=   (a(scene,"AColor(%.6f,%.6f,%.6f,1.0)"%tuple(BRDFSSS2Complex.overall_color)), 0, 'NONE')
	else:
		defaults['overall_color']=   (a(scene,"AColor(%.6f,%.6f,%.6f,1.0)"%tuple(ma.diffuse_color)), 0, 'NONE')

	defaults['sub_surface_color']=   (a(scene,"AColor(%.6f,%.6f,%.6f,1.0)"%tuple(BRDFSSS2Complex.sub_surface_color)),  0, 'NONE')
	defaults['scatter_radius']=      (a(scene,"AColor(%.6f,%.6f,%.6f,1.0)"%tuple(BRDFSSS2Complex.scatter_radius)),     0, 'NONE')
	defaults['diffuse_color']=       (a(scene,"AColor(%.6f,%.6f,%.6f,1.0)"%tuple(BRDFSSS2Complex.diffuse_color)),      0, 'NONE')
	defaults['diffuse_amount']=      (a(scene,"AColor(%.6f,%.6f,%.6f,1.0)"%tuple([BRDFSSS2Complex.diffuse_amount]*3)), 0, 'NONE')
	defaults['specular_color']=      (a(scene,"AColor(%.6f,%.6f,%.6f,1.0)"%tuple(BRDFSSS2Complex.specular_color)),     0, 'NONE')
	defaults['specular_amount']=     (a(scene,"AColor(0.0,0.0,0.0,1.0)"), 0, 'NONE')
	defaults['specular_glossiness']= (a(scene,"AColor(0.0,0.0,0.0,1.0)"), 0, 'NONE')

	defaults['normal']=       ("AColor(0.0,0.0,0.0,1.0)", 0, 'NONE')
	defaults['bump']=         ("AColor(0.0,0.0,0.0,1.0)", 0, 'NONE')
	defaults['displacement']= ("AColor(0.0,0.0,0.0,1.0)", 0, 'NONE')

	return defaults


def write(bus, VRayBRDF= None, base_name= None):
	SINGLE_SCATTER= {
		'NONE':   0,
		'SIMPLE': 1,
		'SOLID':  2,
		'REFR':   3,
	}

	scene= bus['scene']
	ofile= bus['files']['materials']

	ma=       bus['material']['material']
	textures= bus['textures']

	brdf_name= "%s%s%s" % (ID, get_name(ma, prefix='MA'), bus['material']['orco_suffix'])
	if base_name:
		brdf_name= "%s%s%s" % (base_name, ID, bus['material']['orco_suffix'])
	if VRayBRDF:
		brdf_name+= clean_string(VRayBRDF.name)

	BRDFSSS2Complex= getattr(VRayBRDF, ID) if VRayBRDF else ma.vray.BRDFSSS2Complex

	defaults= mapto(bus, VRayBRDF)

	ofile.write("\nBRDFSSS2Complex %s {" % brdf_name)

	for key in ('overall_color','diffuse_color','sub_surface_color','scatter_radius','specular_color'):
		ofile.write("\n\t%s= %s;" % (key, a(scene,textures[key]) if key in textures else defaults[key][0]))

	for key in ('specular_amount','specular_glossiness','diffuse_amount'):
		ofile.write("\n\t%s= %s;" % (key, "%s::out_intensity" % textures[key] if key in textures else a(scene,getattr(BRDFSSS2Complex,key))))

	for param in PARAMS:
		if param == 'single_scatter':
			value= SINGLE_SCATTER[BRDFSSS2Complex.single_scatter]
		else:
			value= getattr(BRDFSSS2Complex,param)
		ofile.write("\n\t%s= %s;"%(param, a(scene,value)))

	ofile.write("\n}\n")

	return brdf_name



def influence(context, layout, slot):
	wide_ui= context.region.width > ui.narrowui

	VRaySlot= slot.texture.vray_slot

	split= layout.split()
	col= split.column()
	col.label(text="SSS:")
	split= layout.split()
	col= split.column()
	ui.factor_but(col, VRaySlot, 'map_overall_color',     'overall_color_mult',     "Overall")
	ui.factor_but(col, VRaySlot, 'map_sub_surface_color', 'sub_surface_color_mult', "Sub-surface")
	if wide_ui:
		col= split.column()
	ui.factor_but(col, VRaySlot, 'map_scatter_radius',    'scatter_radius_mult',    "Scatter")

	layout.separator()

	split= layout.split()
	col= split.column()
	ui.factor_but(col, VRaySlot, 'map_diffuse_color',  'diffuse_color_mult',  "Diffuse")
	ui.factor_but(col, VRaySlot, 'map_diffuse_amount', 'diffuse_amount_mult', "Amount")
	if wide_ui:
		col= split.column()
	ui.factor_but(col, VRaySlot, 'map_specular_color',      'specular_color_mult',      "Specular")
	ui.factor_but(col, VRaySlot, 'map_specular_amount',     'specular_amount_mult',     "Amount")
	ui.factor_but(col, VRaySlot, 'map_specular_glossiness', 'specular_glossiness_mult', "Glossiness")


def gui(context, layout, BRDFSSS2Complex, material= None):
	wide_ui= context.region.width > ui.narrowui

	split= layout.split()
	col= split.column()
	col.label(text="General:")

	split= layout.split()
	col= split.column()
	col.menu('VRAY_MT_preset_sss', text="Presets")

	split= layout.split()
	col= split.column()
	col.prop(BRDFSSS2Complex, 'prepass_rate')
	col.prop(BRDFSSS2Complex, 'scale')
	if wide_ui:
		col= split.column()
	col.prop(BRDFSSS2Complex, 'ior')
	col.prop(BRDFSSS2Complex, 'interpolation_accuracy', text='Accuracy')

	layout.separator()

	split= layout.split()
	col= split.column()
	if material:
		col.prop(material, 'diffuse_color', text="Overall color")
	else:
		col.prop(BRDFSSS2Complex, 'overall_color')
	if wide_ui:
		col= split.column()
	col.prop(BRDFSSS2Complex, 'diffuse_color')
	split= layout.split()
	col= split.column()
	if wide_ui:
		col= split.column()
	col.prop(BRDFSSS2Complex, 'diffuse_amount', text="Amount")

	split= layout.split()
	col= split.column()
	col.prop(BRDFSSS2Complex, 'sub_surface_color')
	col.prop(BRDFSSS2Complex, 'phase_function')
	if wide_ui:
		col= split.column()
	col.prop(BRDFSSS2Complex, 'scatter_radius', text="Scatter color")
	col.prop(BRDFSSS2Complex, 'scatter_radius_mult', text="Radius")

	split= layout.split()
	col= split.column()
	col.label(text='Specular layer:')
	split= layout.split()
	col= split.column()
	col.prop(BRDFSSS2Complex, 'specular_color', text='')
	col.prop(BRDFSSS2Complex, 'specular_subdivs', text='Subdivs', slider= True)
	if wide_ui:
		col= split.column()
	col.prop(BRDFSSS2Complex, 'specular_amount', text='Amount')
	col.prop(BRDFSSS2Complex, 'specular_glossiness', text='Glossiness')
	col.prop(BRDFSSS2Complex, 'cutoff_threshold')

	split= layout.split()
	col= split.column()
	col.prop(BRDFSSS2Complex, 'trace_reflections')
	if BRDFSSS2Complex.trace_reflections:
		if wide_ui:
			col= split.column()
		col.prop(BRDFSSS2Complex, 'reflection_depth')

	layout.separator()

	split= layout.split()
	col= split.column()
	col.prop(BRDFSSS2Complex, 'single_scatter')

	split= layout.split()
	col= split.column()
	col.prop(BRDFSSS2Complex, 'subdivs', slider= True)
	col.prop(BRDFSSS2Complex, 'refraction_depth')
	col.prop(BRDFSSS2Complex, 'prepass_blur')
	if wide_ui:
		col= split.column()
	col.prop(BRDFSSS2Complex, 'front_scatter')
	col.prop(BRDFSSS2Complex, 'back_scatter')
	col.prop(BRDFSSS2Complex, 'scatter_gi')
