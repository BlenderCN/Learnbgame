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
ID=   'BRDFGlassGlossy'
PID=   10

NAME= 'BRDFGlassGlossy'
UI=   "GlassGlossy"
DESC= "BRDFGlassGlossy."

PARAMS= (
	'color',
	'color_tex',
	'color_tex_mult',
	'transparency',
	'transparency_tex',
	'transparency_tex_mult',
	'ior',
	'ior_tex',
	'cutoff',
	'affect_shadows',
	'affect_alpha',
	'trace_refractions',
	'trace_depth',
	'exit_color_on',
	'reflect_exit_color',
	'refract_exit_color',
#	'volume',
	'glossiness'
	'glossiness_tex',
	'glossiness_tex_mult',
	'subdivs',
	'dispersion_on',
	'dispersion',
	'interpolation_on',
	'imap_min_rate',
	'imap_max_rate',
	'imap_color_thresh',
	'imap_norm_thresh',
	'imap_samples',
)



def add_properties(rna_pointer):
	class BRDFGlassGlossy(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(BRDFGlassGlossy)
	
	rna_pointer.BRDFGlassGlossy= PointerProperty(
		name= "BRDFGlassGlossy",
		type=  BRDFGlassGlossy,
		description= "V-Ray BRDFGlassGlossy settings"
	)

	#  color: color = Color(1, 1, 1)
	BRDFGlassGlossy.color= FloatVectorProperty(
		name= "Color",
		description= "Reflection color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (1,1,1)
	)

	#   color_tex: acolor texture
	BRDFGlassGlossy.color_tex= StringProperty(
		name= "Color texture",
		description= "",
		default= ""
	)


	#   color_tex_mult: float = 1
	BRDFGlassGlossy.color_tex_mult= FloatProperty(
		name= "Color texture multiplier",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	#  transparency: color = Color(0, 0, 0)
	BRDFGlassGlossy.transparency= FloatVectorProperty(
		name= "Transparency",
		description= "Transparency color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0,0,0)
	)

	#   transparency_tex: acolor texture
	BRDFGlassGlossy.transparency_tex= StringProperty(
		name= "Transparency",
		description= "",
		default= ""
	)

	#   transparency_tex_mult: float = 1
	BRDFGlassGlossy.transparency_tex_mult= FloatProperty(
		name= "Transparency Texture",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	#  ior: float = 1.55, IOR for the glass; this is ignored if the surface has a volume shader (the volume IOR is used).
	BRDFGlassGlossy.ior= FloatProperty(
		name= "IOR",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.55
	)

	#  ior_tex: float texture
	BRDFGlassGlossy.ior_tex= StringProperty(
		name= "IOR Texture",
		description= "IOR Texture",
		default= ""
	)

	#  cutoff: float = 0.01
	BRDFGlassGlossy.cutoff= FloatProperty(
		name= "Cutoff",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.01
	)

	#  affect_shadows: bool = false
	BRDFGlassGlossy.affect_shadows= BoolProperty(
		name= "Affect Shadows",
		description= "",
		default= False
	)

	#  affect_alpha: integer = 0, Specifies how render channels are propagated through the glass (0 - only the color channel; 1 - color and alpha; 2 - all channels
	BRDFGlassGlossy.affect_alpha= EnumProperty(
		name= "Affect Channels",
		description= "Which channels affect",
		items= (
			('COL',  "Color Only",   "The transperency will affect only the RGB channel of the final render."),
			('RERF', "Color+Alpha",  "This will cause the material to transmit the alpha of the refracted objects, instead of displaying an opaque alpha.."),
			('ALL',  "All Channels", "All channels and render elements will be affected by the transperency of the material.")
		),
		default= 'COL'
	)

	#  trace_refractions: bool = true
	BRDFGlassGlossy.trace_refractions= BoolProperty(
		name= "Trace Refractions",
		description= "",
		default= True
	)

	#  trace_depth: integer = -1, The maximum refraction bounces (-1 is controlled by the global options)
	BRDFGlassGlossy.trace_depth= IntProperty(
		name= "Trace Depth",
		description= "The maximum refraction bounces (-1 is controlled by the global options)",
		min= 0,
		max= 100,
		default= -1
	)

	#  exit_color_on: bool = false
	BRDFGlassGlossy.exit_color_on= BoolProperty(
		name= "Exit color on",
		description= "",
		default= False
	)

	#  reflect_exit_color: acolor texture = AColor(0, 0, 0, 0), The color to use when the maximum depth is reached
	BRDFGlassGlossy.reflect_exit_color= FloatVectorProperty(
		name= "Reflect exit color",
		description= "",
		size=4,
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0,0,0,0)
	)

	BRDFGlassGlossy.reflect_exit_color_tex= StringProperty(
		name= "Reflect exit color texture",
		description= "Reflect exit color texture",
		default= ""
	)

	#  refract_exit_color: acolor texture = AColor(0, 0, 0, 0), The color to use when maximum depth is reached when exit_color_on is true
	BRDFGlassGlossy.refract_exit_color= FloatVectorProperty(
		name= "Refract Exit Color",
		description= "",
		size=4,
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0,0,0,0)
	)

	BRDFGlassGlossy.refract_exit_color_tex= StringProperty(
		name= "Refract exit color texture",
		description= "Refract exit color texture",
		default= ""
	)

	#  volume: plugin
	#  TODOO

	#  glossiness: float = 0.8
	BRDFGlassGlossy.glossiness= FloatProperty(
		name= "Glossiness",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.8
	)

	#  glossiness_tex: float texture
	BRDFGlassGlossy.glossiness_tex= FloatProperty(
		name= "Glossiness texture",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.8
	)

	#  glossiness_tex_mult: float = 1
	BRDFGlassGlossy.glossiness_tex_mult= FloatProperty(
		name= "Glossiness texture multiplier",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	#  subdivs: integer = 8
	BRDFGlassGlossy.subdivs= IntProperty(
		name= "Subdivs",
		description= "Subdivs",
		min= 0,
		max= 100,
		default= 8
	)

	#  dispersion_on: integer = 0
	BRDFGlassGlossy.dispersion_on= IntProperty(
		name= "Dispersion on",
		description= "Dispersion on",
		min= 0,
		max= 100,
		default= 0
	)

	#  dispersion: float = 1
	BRDFGlassGlossy.dispersion= FloatProperty(
		name= "Dispersion",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	#  interpolation_on: integer = 0
	BRDFGlassGlossy.interpolation_on= IntProperty(
		name= "Interpolation on",
		description= "Interpolation on",
		min= 0,
		max= 100,
		default= 0
	)

	#  imap_min_rate: integer = -1
	BRDFGlassGlossy.imap_min_rate= IntProperty(
		name= "Imap min rate",
		description= "Imap min rate",
		min= 0,
		max= 100,
		default= -1
	)

	#  imap_max_rate: integer = 1
	BRDFGlassGlossy.imap_max_rate= IntProperty(
		name= "Imap max rate",
		description= "Imap max rate",
		min= 0,
		max= 100,
		default= 1
	)

	#  imap_color_thresh: float = 0.25
	BRDFGlassGlossy.imap_color_thresh= FloatProperty(
		name= "Imap color thresh",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.25
	)

	#  imap_norm_thresh: float = 0.4
	BRDFGlassGlossy.imap_norm_thresh= FloatProperty(
		name= "Imap norm thresh",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.4
	)

	#  imap_samples: integer = 20
	BRDFGlassGlossy.imap_samples= IntProperty(
		name= "Imap samples",
		description= "Imap samples",
		min= 0,
		max= 100,
		default= 20
	)



'''
  OUTPUT
'''
def write(bus, VRayBRDF= None, base_name= None):

	AFFECT_ALPHA= {
		'COL':  0,
		'RERF': 1,
		'All':  2,
	}

	ofile= bus['files']['materials']
	scene= bus['scene']

	BRDFGlassGlossy= getattr(VRayBRDF, ID)

	brdf_name= "%s%s%s" % ('BRDFGlassGlossy', ID, clean_string(VRayBRDF.name))

	ofile.write("\n%s %s {" % ('BRDFGlassGlossy', brdf_name))
	for param in PARAMS:
		if param.endswith('_tex'):
			continue
		elif (param == 'affect_alpha'):
			value= AFFECT_ALPHA[BRDFGlassGlossy.affect_alpha]
		else:
			value= getattr(BRDFGlassGlossy, param)
		ofile.write("\n\t%s= %s;" % (param, a(scene, value)))
	ofile.write("\n}\n")

	return brdf_name



'''
  GUI
'''
def gui(context, layout, BRDFGlassGlossy):
	wide_ui= context.region.width > ui.narrowui

	layout.label(text="Color:")
	split= layout.split()
	
	row= split.row(align=True)
	
	row.prop(BRDFGlassGlossy, 'color', text="")
	row.prop_search(BRDFGlassGlossy, 'color_tex',
					bpy.data, 'textures',
					text= "")
	if BRDFGlassGlossy.color_tex:
		row.prop(BRDFGlassGlossy, 'color_tex_mult', text="Mult")

	layout.label(text="Transparency:")
	split= layout.split()
	if wide_ui:
		row= split.row(align=True)
	row.prop(BRDFGlassGlossy, 'transparency', text= "", slider= True)
	row.prop_search(BRDFGlassGlossy, 'transparency_tex',
					bpy.data, 'textures',
					text= "")
	if BRDFGlassGlossy.transparency_tex:
		row.prop(BRDFGlassGlossy, 'transparency_tex_mult', text="Mult")


	split= layout.split()
	col= split.column(align=True)
	col.prop(BRDFGlassGlossy, 'ior')
	col.prop_search(BRDFGlassGlossy, 'ior_tex',
					bpy.data, 'textures',
					text= "")
	col.prop(BRDFGlassGlossy, 'affect_shadows')
	if BRDFGlassGlossy.affect_shadows:
		col.prop(BRDFGlassGlossy, 'affect_alpha')

	col.prop(BRDFGlassGlossy, 'trace_refractions')
	if BRDFGlassGlossy.trace_refractions:
		col.prop(BRDFGlassGlossy, 'trace_depth')

	col.prop(BRDFGlassGlossy, 'exit_color_on')

	if BRDFGlassGlossy.exit_color_on:
		col.prop(BRDFGlassGlossy, 'reflect_exit_color')
		col.prop_search(BRDFGlassGlossy, 'reflect_exit_color_tex',
											bpy.data, 'textures',
											text= "")

		col.prop(BRDFGlassGlossy, 'refract_exit_color')
		col.prop_search(BRDFGlassGlossy, 'refract_exit_color_tex',
											bpy.data, 'textures',
											text= "")

	split= layout.split()
	col= split.column(align=True)

	col.prop(BRDFGlassGlossy, 'glossiness')
	col.prop_search(BRDFGlassGlossy, 'glossiness_tex',
					bpy.data, 'textures',
					text= "")
	if BRDFGlassGlossy.glossiness_tex:
		col.prop(BRDFGlassGlossy, 'glossiness_tex_mult')

	split= layout.split()
	col= split.column(align=True)

	col.prop(BRDFGlassGlossy, 'subdivs')

	col.prop(BRDFGlassGlossy, 'dispersion_on')
	col.prop(BRDFGlassGlossy, 'dispersion')
	
	col.prop(BRDFGlassGlossy, 'interpolation_on')
	col.prop(BRDFGlassGlossy, 'imap_min_rate')
	col.prop(BRDFGlassGlossy, 'imap_max_rate')
	col.prop(BRDFGlassGlossy, 'imap_color_thresh')
	col.prop(BRDFGlassGlossy, 'imap_norm_thresh')
	col.prop(BRDFGlassGlossy, 'imap_samples')


#  glossiness: float = 0.8
#  glossiness_tex: float texture
#  glossiness_tex_mult: float = 1
#  subdivs: integer = 8
#  dispersion_on: integer = 0
#  dispersion: float = 1
#  interpolation_on: integer = 0
#  imap_min_rate: integer = -1
#  imap_max_rate: integer = 1
#  imap_color_thresh: float = 0.25
#  imap_norm_thresh: float = 0.4
#  imap_samples: integer = 20
