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

TYPE= 'RENDERCHANNEL'
ID=   'AO'
NAME= 'Ambient Occlusion'
PLUG= 'RenderChannelAO'
DESC= ""
PID=  0

PARAMS= (
	'name',
	'consider_for_aa',
	'affect_matte_objects',
	'filtering'
)

PARAMS_AO= (
	'radius',
	'falloff',
	'subdivs',
	'ignore_for_gi'
)


''' Blender modules '''
import bpy
from bpy.props import *

''' vb modules '''
from vb25.utils import *


class RenderChannelAO(bpy.types.PropertyGroup):
	pass
bpy.utils.register_class(RenderChannelAO)

def add_properties(parent_struct):
	parent_struct.RenderChannelAO= PointerProperty(
		type= RenderChannelAO,
		name= NAME,
		description= "V-Ray render channel \"%s\" settings" % NAME
	)

	RenderChannelAO.name= StringProperty(
		name= "Name",
		description= "",
		default= NAME
	)

	RenderChannelAO.consider_for_aa= BoolProperty(
		name= "Consider for AA",
		description= "",
		default= True
	)

	RenderChannelAO.affect_matte_objects= BoolProperty(
		name= "Affect matte objects",
		description= "",
		default= True
	)

	RenderChannelAO.filtering= BoolProperty(
		name= "Filtering",
		description= "",
		default= True
	)

	RenderChannelAO.radius= FloatProperty(
		name= "Radius",
		description= "AO radius",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 1.0,
		precision= 3,
		default= 0.1
	)

	RenderChannelAO.falloff= FloatProperty(
		name= "Falloff",
		description= "The speed of the transition between occluded and unoccluded areas",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 1.0,
		precision= 3,
		default= 0.0
	)

	RenderChannelAO.subdivs= IntProperty(
		name= "Subdivs",
		description= "",
		min= 1,
		max= 256,
		soft_min= 1,
		soft_max= 32,
		default= 8
	)



'''
  OUTPUT
'''
def write(ofile, render_channel, sce= None, name= None):
	channel_name= clean_string(render_channel.name)
	if name is not None:
		channel_name= name

	ao_tex_name= "TexDirt_%s" % clean_string(channel_name)

	ofile.write("\nTexDirt %s {"%(ao_tex_name))
	ofile.write("\n\twhite_color= AColor(1.0,1.0,1.0, 1.0);")
	ofile.write("\n\tblack_color= AColor(0.0,0.0,0.0, 1.0);")
	ofile.write("\n\tradius= %.3f;" % render_channel.radius)
	ofile.write("\n\tsubdivs= %d;" % render_channel.subdivs)
	ofile.write("\n\tfalloff= %d;" % render_channel.falloff)
	ofile.write("\n}\n")

	ofile.write("\nRenderChannelExtraTex %s {"%(clean_string(channel_name)))
	for param in PARAMS:
		if param == 'name':
			value= "\"%s\"" % channel_name
		else:
			value= getattr(render_channel, param)
		ofile.write("\n\t%s= %s;"%(param, p(value)))
	ofile.write("\n\ttexmap= %s;"%(ao_tex_name))
	ofile.write("\n}\n")



'''
  GUI
'''
def draw(rna_pointer, layout, wide_ui):
	split= layout.split()
	col= split.column()
	col.prop(rna_pointer, 'radius')
	col.prop(rna_pointer, 'subdivs')
	col.prop(rna_pointer, 'falloff')
	if wide_ui:
		col = split.column()
	col.prop(rna_pointer, 'filtering')
	col.prop(rna_pointer, 'consider_for_aa')
	col.prop(rna_pointer, 'affect_matte_objects')

