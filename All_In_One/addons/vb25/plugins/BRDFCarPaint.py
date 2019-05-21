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
ID=   'BRDFCarPaint'
PID=   4
MAIN_BRDF= True

NAME= 'BRDFCarPaint'
UI=   "Car"
DESC= "BRDFCarPaint."


PARAMS= (
	'base_color',
	'base_reflection',
	'base_glossiness',
	'flake_color',
	'flake_glossiness',
	'flake_orientation',
	'flake_density',
	'flake_scale',
	'flake_size',
	'flake_map_size',
	'flake_filtering_mode',
	'flake_seed',
	'flake_uvwgen',
	'coat_color',
	'coat_strength',
	'coat_glossiness',
	# 'coat_bump_float',
	# 'coat_bump_color',
	# 'coat_bump_amount',
	# 'coat_bump_type',
	'traceReflections',
	'doubleSided',
	'subdivs',
	'cutoff_threshold',
	'mapping_type',
	'mapping_channel',
)

def add_properties(rna_pointer):
	class BRDFCarPaint(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(BRDFCarPaint)

	rna_pointer.BRDFCarPaint= PointerProperty(
		name= "BRDFCarPaint",
		type=  BRDFCarPaint,
		description= "V-Ray BRDFCarPaint settings"
	)

	# base_color
	BRDFCarPaint.base_color= FloatVectorProperty(
		name= "Base color",
		description= "",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0.3,0.4,0.5)
	)

	BRDFCarPaint.base_color_tex= StringProperty(
		name= "Base color texture",
		description= "Base color texture",
		default= ""
	)

	BRDFCarPaint.map_base_color= BoolProperty(
		name= "Base color texture",
		description= "",
		default= False
	)

	BRDFCarPaint.base_color_mult= FloatProperty(
		name= "Base color texture multiplier",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	# base_reflection
	BRDFCarPaint.base_reflection= FloatProperty(
		name= "Base reflection",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.5
	)

	BRDFCarPaint.map_base_reflection= BoolProperty(
		name= "base reflection",
		description= "",
		default= False
	)

	BRDFCarPaint.base_reflection_mult= FloatProperty(
		name= "base reflection",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	# base_glossiness
	BRDFCarPaint.base_glossiness= FloatProperty(
		name= "base glossiness",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.6
	)

	BRDFCarPaint.map_base_glossiness= BoolProperty(
		name= "base glossiness",
		description= "",
		default= False
	)

	BRDFCarPaint.base_glossiness_mult= FloatProperty(
		name= "base glossiness",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	# flake_color
	BRDFCarPaint.flake_color= FloatVectorProperty(
		name= "flake color",
		description= "",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0.3,0.4,0.8)
	)

	BRDFCarPaint.flake_color_tex= StringProperty(
		name= "Flake color texture",
		description= "Base color texture",
		default= ""
	)

	BRDFCarPaint.map_flake_color= BoolProperty(
		name= "flake color",
		description= "",
		default= False
	)

	BRDFCarPaint.flake_color_mult= FloatProperty(
		name= "flake color",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	# flake_glossiness
	BRDFCarPaint.flake_glossiness= FloatProperty(
		name= "flake glossiness",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.8
	)

	BRDFCarPaint.map_flake_glossiness= BoolProperty(
		name= "flake glossiness",
		description= "",
		default= False
	)

	BRDFCarPaint.flake_glossiness_mult= FloatProperty(
		name= "flake glossiness",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	# flake_orientation
	BRDFCarPaint.flake_orientation= FloatProperty(
		name= "flake orientation",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.3
	)

	BRDFCarPaint.map_flake_orientation= BoolProperty(
		name= "flake orientation",
		description= "",
		default= False
	)

	BRDFCarPaint.flake_orientation_mult= FloatProperty(
		name= "flake orientation",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	# flake_density
	BRDFCarPaint.flake_density= FloatProperty(
		name= "flake density",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.5
	)

	# flake_scale
	BRDFCarPaint.flake_scale= FloatProperty(
		name= "flake scale",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.01
	)

	# flake_size
	BRDFCarPaint.flake_size= FloatProperty(
		name= "flake size",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.5
	)

	# flake_map_size
	BRDFCarPaint.flake_map_size= IntProperty(
		name= "flake map size",
		description= "The size of the internal flakes map",
		min= 0,
		max= 10000,
		soft_min= 0,
		soft_max= 10000,
		default= 1024
	)

	# flake_filtering_mode
	BRDFCarPaint.flake_filtering_mode= IntProperty(
		name= "flake filtering mode",
		description= "Flake filtering mode (0 - simple; 1 - directional)",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 1
	)

	# flake_seed
	BRDFCarPaint.flake_seed= IntProperty(
		name= "flake seed",
		description= "The random seed for the flakes",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 1
	)

	# flake_uvwgen

	# coat_color
	BRDFCarPaint.coat_color= FloatVectorProperty(
		name= "coat color",
		description= "",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (1,1,1)
	)

	BRDFCarPaint.coat_color_tex= StringProperty(
		name= "Coat color texture",
		description= "Base color texture",
		default= ""
	)

	BRDFCarPaint.map_coat_color= BoolProperty(
		name= "coat color",
		description= "",
		default= False
	)

	BRDFCarPaint.coat_color_mult= FloatProperty(
		name= "coat color",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	# coat_strength
	BRDFCarPaint.coat_strength= FloatProperty(
		name= "coat strength",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.05
	)

	BRDFCarPaint.map_coat_strength= BoolProperty(
		name= "coat strength",
		description= "",
		default= False
	)

	BRDFCarPaint.coat_strength_mult= FloatProperty(
		name= "coat strength",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	# coat_glossiness
	BRDFCarPaint.coat_glossiness= FloatProperty(
		name= "coat glossiness",
		description= "The glossiness of the coat layer",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	BRDFCarPaint.map_coat_glossiness= BoolProperty(
		name= "coat glossiness",
		description= "The glossiness of the coat layer",
		default= False
	)

	BRDFCarPaint.coat_glossiness_mult= FloatProperty(
		name= "coat glossiness",
		description= "The glossiness of the coat layer",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	# coat_bump_float
	BRDFCarPaint.map_coat_bump_float= BoolProperty(
		name= "coat bump float",
		description= "Bump texture for the coat layer",
		default= False
	)

	BRDFCarPaint.coat_bump_float_mult= FloatProperty(
		name= "coat bump float",
		description= "Bump texture for the coat layer",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	# coat_bump_color
	BRDFCarPaint.map_coat_bump_color= BoolProperty(
		name= "coat bump color",
		description= "Bump texture for the coat layer (color version)",
		default= False
	)

	BRDFCarPaint.coat_bump_color_mult= FloatProperty(
		name= "coat bump color",
		description= "Bump texture for the coat layer (color version)",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	# coat_bump_amount
	BRDFCarPaint.map_coat_bump_amount= BoolProperty(
		name= "coat bump amount",
		description= "Bump amount for the coat layer",
		default= False
	)

	BRDFCarPaint.coat_bump_amount_mult= FloatProperty(
		name= "coat bump amount",
		description= "Bump amount for the coat layer",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	# coat_bump_type
	BRDFCarPaint.coat_bump_type= IntProperty(
		name= "coat bump type",
		description= "The type of bump mapping (see BRDFBump for more details)",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 0
	)

	# traceReflections
	BRDFCarPaint.traceReflections= BoolProperty(
		name= "Trace reflections",
		description= "",
		default= True
	)

	# doubleSided
	BRDFCarPaint.doubleSided= BoolProperty(
		name= "Double-sided",
		description= "",
		default= True
	)

	# subdivs
	BRDFCarPaint.subdivs= IntProperty(
		name= "Subdivs",
		description= "",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 8
	)

	# cutoff_threshold
	BRDFCarPaint.cutoff_threshold= FloatProperty(
		name= "Cutoff",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.001
	)

	# mapping_type
	BRDFCarPaint.mapping_type= EnumProperty(
		name= "Mapping type",
		description= "The mapping method for the flakes",
		items= (
			('EXPLICIT',  "Explicit", "Explicit mapping channel"),
			('TRIPLANAR', "Object",   "Triplanar projection in object space"),
		),
		default= 'EXPLICIT'
	)

	# mapping_channel
	BRDFCarPaint.mapping_channel= IntProperty(
		name= "Mapping channel",
		description= "The mapping channel when the mapping_type is 0",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 1
	)



'''
  OUTPUT
'''
def mapto(bus, BRDFLayered= None):
	scene= bus['scene']
	ma=    bus['material']['material']

	VRayMaterial= ma.vray

	BRDFVRayMtl=  BRDFLayered.BRDFCarPaint if BRDFLayered else VRayMaterial.BRDFCarPaint

	defaults= {}

	defaults['bump']         = ("AColor(0.0,0.0,0.0,1.0)", 0, 'NONE')
	defaults['normal']       = ("AColor(0.0,0.0,0.0,1.0)", 0, 'NONE')
	defaults['displacement'] = ("AColor(0.0,0.0,0.0,1.0)", 0, 'NONE')

	return defaults


def write(bus, VRayBRDF= None, base_name= None):
	MAPPING_TYPE= {
		'EXPLICIT':  0,
		'TRIPLANAR': 1,
	}

	ofile= bus['files']['materials']
	scene= bus['scene']
	ma=    bus['material']['material']

	brdf_name= "%s%s%s" % (ID, get_name(ma, prefix='MA'), bus['material']['orco_suffix'])
	if base_name:
		brdf_name= "%s%s%s" % (base_name, ID, bus['material']['orco_suffix'])
	if VRayBRDF:
		brdf_name+= clean_string(VRayBRDF.name)

	BRDFCarPaint= getattr(VRayBRDF, ID) if VRayBRDF else ma.vray.BRDFCarPaint

	# Color values if param is not textured
	mapped_params= mapto(bus, VRayBRDF)
	
	ofile.write("\n%s %s {"%(ID, brdf_name))
	for param in PARAMS:
		if param == 'mapping_type':
			value= MAPPING_TYPE[BRDFCarPaint.mapping_type]
		elif param == 'flake_uvwgen':
			value= bus['defaults']['uvwgen'];
		else:
			value= getattr(BRDFCarPaint, param)
		ofile.write("\n\t%s= %s;" % (param, a(scene, value)))
	ofile.write("\n}\n")

	return brdf_name



'''
  GUI
'''
def influence(context, layout, slot):
	wide_ui= context.region.width > ui.narrowui

	VRaySlot= slot.texture.vray_slot

	split= layout.split()
	col= split.column()
	col.label(text="Diffuse:")
	split= layout.split()
	col= split.column()
	ui.factor_but(col, VRaySlot, 'map_base',  'base_mult',  "Base")
	if wide_ui:
		col= split.column()
	ui.factor_but(col, VRaySlot, 'map_coat',  'coat_mult',  "Coat")
	ui.factor_but(col, VRaySlot, 'map_flake', 'flake_mult', "Flake")


def gui(context, layout, BRDFCarPaint, material= None):
	wide_ui= context.region.width > ui.narrowui

	layout.label(text="Coat:")
	split= layout.split()
	col= split.column()
	sub= col.column(align=True)
	sub.prop(BRDFCarPaint, 'coat_color', text="")
	if not material:
		sub.prop_search(BRDFCarPaint, 'coat_color_tex',
						bpy.data, 'textures',
						text= "")
	if wide_ui:
		col= split.column()
	col.prop(BRDFCarPaint, 'coat_strength', text="Strength")
	col.prop(BRDFCarPaint, 'coat_glossiness', text="Glossiness")
	# col.prop(BRDFCarPaint, 'coat_bump_float')
	# col.prop(BRDFCarPaint, 'coat_bump_color')
	# col.prop(BRDFCarPaint, 'coat_bump_amount')
	# col.prop(BRDFCarPaint, 'coat_bump_type')

	layout.label(text="Flake:")
	split= layout.split()
	col= split.column()
	sub= col.column(align=True)
	sub.prop(BRDFCarPaint, 'flake_color', text="")
	if not material:
		sub.prop_search(BRDFCarPaint, 'flake_color_tex',
						bpy.data, 'textures',
						text= "")
	col.prop(BRDFCarPaint, 'flake_glossiness', text="Glossiness")
	col.prop(BRDFCarPaint, 'flake_orientation', text="Orientation")
	col.prop(BRDFCarPaint, 'flake_density', text="Density")
	col.prop(BRDFCarPaint, 'flake_seed', text="Seed")
	if wide_ui:
		col= split.column()
	col.prop(BRDFCarPaint, 'flake_scale', text="Scale")
	col.prop(BRDFCarPaint, 'flake_size', text="Size")
	col.prop(BRDFCarPaint, 'flake_map_size', text="Map size")
	col.prop(BRDFCarPaint, 'flake_filtering_mode', text="Filtering")
	# col.prop(BRDFCarPaint, 'flake_uvwgen')
	col.prop(BRDFCarPaint, 'mapping_type', text="Type")
	if BRDFCarPaint.mapping_type == 'EXPLICIT':
		col.prop(BRDFCarPaint, 'mapping_channel', text="Channel")

	layout.label(text="Base:")
	split= layout.split()
	col= split.column()
	sub= col.column(align=True)
	sub.prop(BRDFCarPaint, 'base_color', text="")
	if not material:
		sub.prop_search(BRDFCarPaint, 'base_color_tex',
						bpy.data, 'textures',
						text= "")
	if wide_ui:
		col= split.column()
	col.prop(BRDFCarPaint, 'base_reflection', text="Reflection")
	col.prop(BRDFCarPaint, 'base_glossiness', text="Glossiness")

	layout.separator()

	split= layout.split()
	col= split.column()
	col.prop(BRDFCarPaint, 'subdivs')
	col.prop(BRDFCarPaint, 'cutoff_threshold')
	if wide_ui:
		col= split.column()
	col.prop(BRDFCarPaint, 'doubleSided')
	col.prop(BRDFCarPaint, 'traceReflections')

