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
import vb25.texture

from vb25.utils import *
from vb25.ui import ui


TYPE= 'BRDF'
ID=   'BRDFMirror'
PID=   6

NAME= 'BRDFMirror'
UI=   "Mirror"
DESC= "BRDFMirror."


PARAMS= (
	'color',
	'color_tex',
	'color_tex_mult',
	'transparency',
	'transparency_tex',
	'transparency_tex_mult',
	'cutoff',
	'back_side',
	'trace_reflections',
	'trace_depth',
	'reflect_exit_color',
	'reflect_dim_distance',
	'reflect_dim_distance_on',
	'reflect_dim_distance_falloff',
)

def add_properties(rna_pointer):
	class BRDFMirror(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(BRDFMirror)

	rna_pointer.BRDFMirror= PointerProperty(
		name= "BRDFMirror",
		type=  BRDFMirror,
		description= "V-Ray BRDFMirror settings"
	)

	# color
	BRDFMirror.color= FloatVectorProperty(
		name= "Color",
		description= "Mirror color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (1,1,1)
	)

	# color_tex
	BRDFMirror.color_tex= StringProperty(
		name= "Color texture",
		description= "",
		default= ""
	)

	BRDFMirror.map_color_tex= BoolProperty(
		name= "Color texture",
		description= "",
		default= False
	)

	# color_tex_mult
	BRDFMirror.color_tex_mult= FloatProperty(
		name= "Color texture multiplier",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	# transparency
	# BRDFMirror.transparency= FloatVectorProperty(
	# 	name= "Transparency",
	# 	description= "",
	# 	subtype= 'COLOR',
	# 	min= 0.0,
	# 	max= 1.0,
	# 	soft_min= 0.0,
	# 	soft_max= 1.0,
	# 	default= (0,0,0)
	# )

	BRDFMirror.transparency= FloatProperty(
		name= "Transparency",
		description= "BRDF transparency",
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= 0.0
	)

	# transparency_tex
	BRDFMirror.transparency_tex= StringProperty(
		name= "Transparency texture",
		description= "",
		default= ""
	)

	BRDFMirror.map_transparency_tex= BoolProperty(
		name= "Transparency texture",
		description= "",
		default= False
	)

	# transparency_tex_mult
	BRDFMirror.transparency_tex_mult= FloatProperty(
		name= "Transparency texture multiplier",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	# cutoff
	BRDFMirror.cutoff= FloatProperty(
		name= "Cutoff",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.01
	)

	# back_side
	BRDFMirror.back_side= BoolProperty(
		name= "Back side",
		description= "",
		default= False
	)

	# trace_reflections
	BRDFMirror.trace_reflections= BoolProperty(
		name= "Trace reflections",
		description= "",
		default= True
	)

	# trace_depth
	BRDFMirror.trace_depth= IntProperty(
		name= "Depth",
		description= "The maximum reflection depth (-1 is controlled by the global options)",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= -1
	)

	# reflect_exit_color
	BRDFMirror.reflect_exit_color= FloatVectorProperty(
		name= "Exit color",
		description= "The color to use when the maximum depth is reached",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0,0,0)
	)

	BRDFMirror.map_reflect_exit_color= BoolProperty(
		name= "Exit color texture",
		description= "The color to use when the maximum depth is reached",
		default= False
	)

	BRDFMirror.reflect_exit_color_mult= FloatProperty(
		name= "Exit color texture multiplier",
		description= "The color to use when the maximum depth is reached",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	# reflect_dim_distance
	BRDFMirror.reflect_dim_distance= FloatProperty(
		name= "Distance",
		description= "How much to dim reflection as length of rays increases",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1e+18
	)

	# reflect_dim_distance_on
	BRDFMirror.reflect_dim_distance_on= BoolProperty(
		name= "Dim distance",
		description= "True to enable dim distance",
		default= False
	)

	# reflect_dim_distance_falloff
	BRDFMirror.reflect_dim_distance_falloff= FloatProperty(
		name= "Falloff",
		description= "Fall off for the dim distance",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0
	)



'''
  OUTPUT
'''
def write(bus, VRayBRDF= None, base_name= None):
	ofile= bus['files']['materials']
	scene= bus['scene']

	brdf_name= "%s%s%s" % (base_name, ID, clean_string(VRayBRDF.name))

	BRDFMirror= getattr(VRayBRDF, ID)
	
	textures= {}
	for param in PARAMS:
		if param.endswith('_tex'):
			textures[param]= vb25.texture.write_subtexture(bus, getattr(BRDFMirror, param))
	
	ofile.write("\n%s %s {"%(ID, brdf_name))
	for param in PARAMS:
		if param.endswith('_tex'):
			if param in textures and textures[param]:
				value= textures[param]
			else:
				continue
		elif param == 'transparency':
			value= mathutils.Color([1.0 - BRDFMirror.transparency]*3)
		else:
			value= getattr(BRDFMirror, param)
		ofile.write("\n\t%s= %s;" % (param, a(scene, value)))
	ofile.write("\n}\n")

	return brdf_name



'''
  GUI
'''
def gui(context, layout, BRDFMirror):
	wide_ui= context.region.width > ui.narrowui
	
	split= layout.split()
	col= split.column(align=True)
	col.prop(BRDFMirror, 'color', text="")
	col.prop_search(BRDFMirror, 'color_tex',
					bpy.data, 'textures',
					text= "")
	if BRDFMirror.color_tex:
		col.prop(BRDFMirror, 'color_tex_mult', text="Mult")
	if wide_ui:
		col= split.column(align=True)
	col.prop(BRDFMirror, 'transparency', text="Reflection", slider= True)
	col.prop_search(BRDFMirror, 'transparency_tex',
					bpy.data, 'textures',
					text= "")
	if BRDFMirror.transparency_tex:
		col.prop(BRDFMirror, 'transparency_tex_mult', text="Mult")

	layout.separator()

	split= layout.split()
	col= split.column()
	col.prop(BRDFMirror, 'cutoff')
	col.prop(BRDFMirror, 'back_side')
	col.prop(BRDFMirror, 'trace_reflections')
	col.prop(BRDFMirror, 'reflect_exit_color')
	if wide_ui:
		col= split.column()
	col.prop(BRDFMirror, 'reflect_dim_distance_on')
	if BRDFMirror.reflect_dim_distance_on:
		col.prop(BRDFMirror, 'reflect_dim_distance')
		col.prop(BRDFMirror, 'reflect_dim_distance_falloff')

