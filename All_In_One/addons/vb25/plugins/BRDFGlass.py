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
ID=   'BRDFGlass'
PID=   9

NAME= 'BRDFGlass'
UI=   "Glass"
DESC= "BRDFGlass."

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
)



def add_properties(rna_pointer):
	class BRDFGlass(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(BRDFGlass)
	
	rna_pointer.BRDFGlass= PointerProperty(
		name= "BRDFGlass",
		type=  BRDFGlass,
		description= "V-Ray BRDFGlass settings"
	)

	#  color: color = Color(1, 1, 1)
	BRDFGlass.color= FloatVectorProperty(
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
	BRDFGlass.color_tex= StringProperty(
		name= "Color texture",
		description= "",
		default= ""
	)


	#   color_tex_mult: float = 1
	BRDFGlass.color_tex_mult= FloatProperty(
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
	BRDFGlass.transparency= FloatVectorProperty(
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
	BRDFGlass.transparency_tex= StringProperty(
		name= "Transparency",
		description= "",
		default= ""
	)

	#   transparency_tex_mult: float = 1
	BRDFGlass.transparency_tex_mult= FloatProperty(
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
	BRDFGlass.ior= FloatProperty(
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
	BRDFGlass.ior_tex= StringProperty(
		name= "IOR Texture",
		description= "IOR Texture",
		default= ""
	)

	#  cutoff: float = 0.01
	BRDFGlass.cutoff= FloatProperty(
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
	BRDFGlass.affect_shadows= BoolProperty(
		name= "Affect Shadows",
		description= "",
		default= False
	)

	#  affect_alpha: integer = 0, Specifies how render channels are propagated through the glass (0 - only the color channel; 1 - color and alpha; 2 - all channels
	BRDFGlass.affect_alpha= EnumProperty(
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
	BRDFGlass.trace_refractions= BoolProperty(
		name= "Trace Refractions",
		description= "",
		default= True
	)

	#  trace_depth: integer = -1, The maximum refraction bounces (-1 is controlled by the global options)
	BRDFGlass.trace_depth= IntProperty(
		name= "Trace Depth",
		description= "The maximum refraction bounces (-1 is controlled by the global options)",
		min= 0,
		max= 100,
		default= -1
	)

	#  exit_color_on: bool = false
	BRDFGlass.exit_color_on= BoolProperty(
		name= "Exit color on",
		description= "",
		default= False
	)

	#  reflect_exit_color: acolor texture = AColor(0, 0, 0, 0), The color to use when the maximum depth is reached
	BRDFGlass.reflect_exit_color= FloatVectorProperty(
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

	BRDFGlass.reflect_exit_color_tex= StringProperty(
		name= "Reflect exit color texture",
		description= "Reflect exit color texture",
		default= ""
	)

	#  refract_exit_color: acolor texture = AColor(0, 0, 0, 0), The color to use when maximum depth is reached when exit_color_on is true
	BRDFGlass.refract_exit_color= FloatVectorProperty(
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

	BRDFGlass.refract_exit_color_tex= StringProperty(
		name= "Refract exit color texture",
		description= "Refract exit color texture",
		default= ""
	)

	#  volume: plugin





'''
  OUTPUT
'''
def write(bus, VRayBRDF= None, base_name= None):

	AFFECT_ALPHA= {
		'COL':  0,
		'RERF': 1,
		'All': 2,
	}

	ofile= bus['files']['materials']
	scene= bus['scene']

	BRDFGlass= getattr(VRayBRDF, ID)

	brdf_name= "%s%s%s" % ('BRDFGlass', ID, clean_string(VRayBRDF.name))

	ofile.write("\n%s %s {" % ('BRDFGlass', brdf_name))
	for param in PARAMS:
		if param.endswith('_tex'):
			continue
		elif (param == 'affect_alpha'):
			value= AFFECT_ALPHA[BRDFGlass.affect_alpha]
		else:
			value= getattr(BRDFGlass, param)
		ofile.write("\n\t%s= %s;" % (param, a(scene, value)))
	ofile.write("\n}\n")

	return brdf_name



'''
  GUI
'''
def gui(context, layout, BRDFGlass):
	wide_ui= context.region.width > ui.narrowui

	layout.label(text="Color:")
	split= layout.split()
	
	row= split.row(align=True)
	
	row.prop(BRDFGlass, 'color', text="")
	row.prop_search(BRDFGlass, 'color_tex',
					bpy.data, 'textures',
					text= "")
	if BRDFGlass.color_tex:
		row.prop(BRDFGlass, 'color_tex_mult', text="Mult")

	layout.label(text="Transparency:")
	split= layout.split()
	if wide_ui:
		row= split.row(align=True)
	row.prop(BRDFGlass, 'transparency', text= "", slider= True)
	row.prop_search(BRDFGlass, 'transparency_tex',
					bpy.data, 'textures',
					text= "")
	if BRDFGlass.transparency_tex:
		row.prop(BRDFGlass, 'transparency_tex_mult', text="Mult")


	split= layout.split()
	col= split.column(align=True)
	col.prop(BRDFGlass, 'ior')
	col.prop_search(BRDFGlass, 'ior_tex',
					bpy.data, 'textures',
					text= "")
	col.prop(BRDFGlass, 'affect_shadows')
	if BRDFGlass.affect_shadows:
		col.prop(BRDFGlass, 'affect_alpha')

	col.prop(BRDFGlass, 'trace_refractions')
	if BRDFGlass.trace_refractions:
		col.prop(BRDFGlass, 'trace_depth')

	col.prop(BRDFGlass, 'exit_color_on')

	if BRDFGlass.exit_color_on:
		col.prop(BRDFGlass, 'reflect_exit_color')
		col.prop_search(BRDFGlass, 'reflect_exit_color_tex',
											bpy.data, 'textures',
											text= "")

		col.prop(BRDFGlass, 'refract_exit_color')
		col.prop_search(BRDFGlass, 'refract_exit_color_tex',
											bpy.data, 'textures',
											text= "")

