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
ID=   'BRDFBlinn'
PID=   7

NAME= 'BRDFBlinn'
UI=   "Glossy"
DESC= "BRDFBlinn."

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
	'hilightGlossiness',
	'hilightGlossiness_tex',
	'hilightGlossiness_tex_mult',
	'reflectionGlossiness',
	'reflectionGlossiness_tex',
	'reflectionGlossiness_tex_mult',
	'subdivs',
	'glossyAsGI',
	'soften_edge',
	'interpolation_on',
	'imap_min_rate',
	'imap_max_rate',
	'imap_color_thresh',
	'imap_norm_thresh',
	'imap_samples',
	'anisotropy',
	# 'anisotropy_uvwgen',
	'anisotropy_rotation',
	'fix_dark_edges',
)


def add_properties(rna_pointer):
	class BRDFBlinn(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(BRDFBlinn)
	
	rna_pointer.BRDFBlinn= PointerProperty(
		name= "BRDFBlinn",
		type=  BRDFBlinn,
		description= "V-Ray BRDFBlinn settings"
	)

	BRDFBlinn.brdf_type= EnumProperty(
		name= "BRDF type",
		description= "This determines the type of BRDF (the shape of the hilight)",
		items= (
			('PHONG',"Phong","Phong hilight/reflections."),
			('BLINN',"Blinn","Blinn hilight/reflections."),
			('WARD',"Ward","Ward hilight/reflections.")
		),
		default= 'BLINN'
	)

	# color
	BRDFBlinn.color= FloatVectorProperty(
		name= "Color",
		description= "Reflection color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (1,1,1)
	)

	# color_tex
	BRDFBlinn.color_tex= StringProperty(
		name= "Color texture",
		description= "",
		default= ""
	)

	BRDFBlinn.map_color_tex= BoolProperty(
		name= "Color texture",
		description= "",
		default= False
	)

	# color_tex_mult
	BRDFBlinn.color_tex_mult= FloatProperty(
		name= "Color texture multiplier",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	# transparency
	# BRDFBlinn.transparency= FloatVectorProperty(
	# 	name= "Transparency",
	# 	description= "",
	# 	subtype= 'COLOR',
	# 	min= 0.0,
	# 	max= 1.0,
	# 	soft_min= 0.0,
	# 	soft_max= 1.0,
	# 	default= (0,0,0)
	# )

	BRDFBlinn.transparency= FloatProperty(
		name= "Transparency",
		description= "BRDF transparency",
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= 0.0
	)

	# transparency_tex
	BRDFBlinn.transparency_tex= StringProperty(
		name= "Transparency",
		description= "",
		default= ""
	)

	BRDFBlinn.map_transparency_tex= BoolProperty(
		name= "transparency tex",
		description= "",
		default= False
	)

	# transparency_tex_mult
	BRDFBlinn.transparency_tex_mult= FloatProperty(
		name= "transparency tex",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	# cutoff
	BRDFBlinn.cutoff= FloatProperty(
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
	BRDFBlinn.back_side= BoolProperty(
		name= "Back side",
		description= "",
		default= False
	)

	# trace_reflections
	BRDFBlinn.trace_reflections= BoolProperty(
		name= "Trace reflections",
		description= "",
		default= True
	)

	# trace_depth
	BRDFBlinn.trace_depth= IntProperty(
		name= "Depth",
		description= "The maximum reflection depth (-1 is controlled by the global options)",
		min= -1,
		max= 100,
		soft_min= -1,
		soft_max= 10,
		default= -1
	)

	# reflect_exit_color
	BRDFBlinn.reflect_exit_color= FloatVectorProperty(
		name= "Exit color",
		description= "The color to use when the maximum depth is reached",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0,0,0)
	)

	BRDFBlinn.map_reflect_exit_color= BoolProperty(
		name= "reflect exit color",
		description= "The color to use when the maximum depth is reached",
		default= False
	)

	BRDFBlinn.reflect_exit_color_mult= FloatProperty(
		name= "reflect exit color",
		description= "The color to use when the maximum depth is reached",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	# reflect_dim_distance
	BRDFBlinn.reflect_dim_distance= FloatProperty(
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
	BRDFBlinn.reflect_dim_distance_on= BoolProperty(
		name= "Dim distance",
		description= "True to enable dim distance",
		default= False
	)

	# reflect_dim_distance_falloff
	BRDFBlinn.reflect_dim_distance_falloff= FloatProperty(
		name= "Falloff",
		description= "Fall off for the dim distance",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0
	)

	# hilightGlossiness
	BRDFBlinn.hilightGlossiness= FloatProperty(
		name= "Hilight",
		description= "",
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		precision= 3,
		default= 1.0
	)

	# hilightGlossiness_tex
	BRDFBlinn.map_hilightGlossiness_tex= BoolProperty(
		name= "hilightGlossiness tex",
		description= "",
		default= False
	)

	# hilightGlossiness_tex_mult
	BRDFBlinn.hilightGlossiness_tex_mult= FloatProperty(
		name= "hilightGlossiness tex mult",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	# reflectionGlossiness
	BRDFBlinn.reflectionGlossiness= FloatProperty(
		name= "Glossiness",
		description= "",
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		precision= 3,
		default= 1.0
	)

	# reflectionGlossiness_tex
	BRDFBlinn.map_reflectionGlossiness_tex= BoolProperty(
		name= "reflectionGlossiness tex",
		description= "",
		default= False
	)

	# reflectionGlossiness_tex_mult
	BRDFBlinn.reflectionGlossiness_tex_mult= FloatProperty(
		name= "reflectionGlossiness tex mult",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	# subdivs
	BRDFBlinn.subdivs= IntProperty(
		name= "Subdivs",
		description= "",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 8
	)

	# glossyAsGI
	BRDFBlinn.glossyAsGI= EnumProperty(
		name= "Glossy rays as GI",
		description= "Specifies when to treat GI rays as glossy rays (0 - never; 1 - only for rays that are already GI rays; 2 - always",
		items= (
			('ALWAYS',"Always",""),
			('GI',"Only for GI rays",""),
			('NEVER',"Never","")
		),
		default= 'GI'
	)

	# soften_edge
	BRDFBlinn.soften_edge= FloatProperty(
		name= "Soften edge",
		description= "Soften edge of the BRDF at light/shadow transition",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0
	)

	# interpolation_on
	BRDFBlinn.interpolation_on= BoolProperty(
		name= "Interpolation",
		description= "",
		default= False
	)

	# imap_min_rate
	BRDFBlinn.imap_min_rate= IntProperty(
		name= "Min rate",
		description= "",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= -1
	)

	# imap_max_rate
	BRDFBlinn.imap_max_rate= IntProperty(
		name= "Max rate",
		description= "",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 1
	)

	# imap_color_thresh
	BRDFBlinn.imap_color_thresh= FloatProperty(
		name= "Color thresh",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.25
	)

	# imap_norm_thresh
	BRDFBlinn.imap_norm_thresh= FloatProperty(
		name= "Normal thresh",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.4
	)

	# imap_samples
	BRDFBlinn.imap_samples= IntProperty(
		name= "Samples",
		description= "",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 20
	)

	# anisotropy
	BRDFBlinn.anisotropy= FloatProperty(
		name= "Anisotropy",
		description= "Reflection anisotropy in the range (-1, 1)",
		min= -1.0,
		max=  1.0,
		soft_min= -1.0,
		soft_max=  1.0,
		precision= 3,
		default= 0.0
	)

	BRDFBlinn.map_anisotropy= BoolProperty(
		name= "Anisotropy",
		description= "Reflection anisotropy in the range (-1, 1)",
		default= False
	)

	BRDFBlinn.anisotropy_mult= FloatProperty(
		name= "anisotropy",
		description= "Reflection anisotropy in the range (-1, 1)",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	# anisotropy_uvwgen
	
	# anisotropy_rotation
	BRDFBlinn.anisotropy_rotation= FloatProperty(
		name= "Rotation",
		description= "Anisotropy rotation in the range [0, 1]",
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		precision= 3,
		default= 0.0
	)

	BRDFBlinn.map_anisotropy_rotation= BoolProperty(
		name= "anisotropy rotation",
		description= "Anisotropy rotation in the range [0, 1]",
		default= False
	)

	BRDFBlinn.anisotropy_rotation_mult= FloatProperty(
		name= "anisotropy rotation",
		description= "Anisotropy rotation in the range [0, 1]",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

	# fix_dark_edges
	BRDFBlinn.fix_dark_edges= BoolProperty(
		name= "Fix dark edges",
		description= "true to fix dark edges with glossy reflections; only set this to false for compatibility with older versions",
		default= True
	)



'''
  OUTPUT
'''
def write(bus, VRayBRDF= None, base_name= None):
	BRDF_TYPE= {
		'PHONG': 'BRDFPhong',
		'BLINN': 'BRDFBlinn',
		'WARD':  'BRDFWard',
	}
	GLOSSY_RAYS= {
		'NEVER':  0,
		'GI':     1,
		'ALWAYS': 2,
	}

	ofile= bus['files']['materials']
	scene= bus['scene']

	BRDFBlinn= getattr(VRayBRDF, ID)

	brdf_type= BRDF_TYPE[BRDFBlinn.brdf_type]

	brdf_name= "%s%s%s" % (brdf_type, ID, clean_string(VRayBRDF.name))

	ofile.write("\n%s %s {" % (brdf_type, brdf_name))
	for param in PARAMS:
		if brdf_type == 'BRDFPhong' and param in ('anisotropy', 'anisotropy_rotation'):
			continue
		elif param.endswith('_tex'):
			continue
		elif param == 'transparency':
			value= mathutils.Color([1.0 - BRDFBlinn.transparency]*3)
		elif param == 'glossyAsGI':
			value= GLOSSY_RAYS[BRDFBlinn.glossyAsGI]
		else:
			value= getattr(BRDFBlinn, param)
		ofile.write("\n\t%s= %s;" % (param, a(scene, value)))
	ofile.write("\n}\n")

	return brdf_name



'''
  GUI
'''
def gui(context, layout, BRDFBlinn):
	wide_ui= context.region.width > ui.narrowui

	split= layout.split()
	col= split.column(align=True)
	col.prop(BRDFBlinn, 'color', text="")
	col.prop_search(BRDFBlinn, 'color_tex',
					bpy.data, 'textures',
					text= "")
	if BRDFBlinn.color_tex:
		col.prop(BRDFBlinn, 'color_tex_mult', text="Mult")
	if wide_ui:
		col= split.column(align=True)
	col.prop(BRDFBlinn, 'transparency', text= "Reflection", slider= True)
	col.prop_search(BRDFBlinn, 'transparency_tex',
					bpy.data, 'textures',
					text= "")
	if BRDFBlinn.transparency_tex:
		col.prop(BRDFBlinn, 'transparency_tex_mult', text="Mult")

	layout.separator()

	split= layout.split()
	col= split.column()
	sub= col.column(align=True)
	sub.prop(BRDFBlinn, 'hilightGlossiness', slider= True)
	# sub.prop(BRDFBlinn, 'hilightGlossiness_tex')
	# sub.prop(BRDFBlinn, 'hilightGlossiness_tex_mult')
	sub.prop(BRDFBlinn, 'reflectionGlossiness', slider= True)
	# sub.prop(BRDFBlinn, 'reflectionGlossiness_tex')
	# sub.prop(BRDFBlinn, 'reflectionGlossiness_tex_mult')
	sub.prop(BRDFBlinn, 'subdivs')
	sub.prop(BRDFBlinn, 'trace_depth')
	if wide_ui:
		col= split.column()
	col.prop(BRDFBlinn, 'brdf_type', text="")
	if not BRDFBlinn.brdf_type == 'PHONG':
		sub= col.column(align=True)
		sub.prop(BRDFBlinn, 'anisotropy', slider= True)
		# sub.prop(BRDFBlinn, 'anisotropy_uvwgen')
		sub.prop(BRDFBlinn, 'anisotropy_rotation', slider= True)

	split= layout.split()
	col= split.column()
	col.prop(BRDFBlinn, 'cutoff')
	col.prop(BRDFBlinn, 'back_side')
	col.prop(BRDFBlinn, 'trace_reflections')
	col.prop(BRDFBlinn, 'reflect_exit_color')
	if wide_ui:
		col= split.column()
	col.prop(BRDFBlinn, 'reflect_dim_distance_on')
	if BRDFBlinn.reflect_dim_distance_on:
		col.prop(BRDFBlinn, 'reflect_dim_distance')
		col.prop(BRDFBlinn, 'reflect_dim_distance_falloff')

	split= layout.split()
	col= split.column()
	col.prop(BRDFBlinn, 'glossyAsGI')
	split= layout.split()
	col= split.column()
	col.prop(BRDFBlinn, 'soften_edge')
	if wide_ui:
		col= split.column()
	col.prop(BRDFBlinn, 'fix_dark_edges')

	split= layout.split()
	col= split.column()
	col.prop(BRDFBlinn, 'interpolation_on')
	if BRDFBlinn.interpolation_on:
		split= layout.split()
		col= split.column()
		col.prop(BRDFBlinn, 'imap_min_rate')
		col.prop(BRDFBlinn, 'imap_max_rate')
		col.prop(BRDFBlinn, 'imap_samples')
		if wide_ui:
			col= split.column()
		col.prop(BRDFBlinn, 'imap_color_thresh')
		col.prop(BRDFBlinn, 'imap_norm_thresh')


