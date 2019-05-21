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

ID=   'ZDEPTH'
NAME= 'ZDepth'
PLUG= 'RenderChannelZDepth'
DESC= ""
PID=  8

PARAMS= (
	'name',
	'depth_from_camera',
	'depth_black',
	'depth_white',
	'depth_clamp',
	'filtering'
)


''' Blender modules '''
import bpy
from bpy.props import *

''' vb modules '''
from vb25.utils import *


def add_properties(parent_struct):
	class RenderChannelZDepth(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(RenderChannelZDepth)
	
	parent_struct.RenderChannelZDepth= PointerProperty(
		name= "Z-Depth",
		type=  RenderChannelZDepth,
		description= "V-Ray render channel \"Z-Depth\" settings"
	)

	RenderChannelZDepth.name= StringProperty(
		name= "Name",
		description= "Render channel name",
		maxlen= 64,
		default= "ZDepth"
	)

	RenderChannelZDepth.depth_from_camera= BoolProperty(
		name= "From camera",
		description= "",
		default= False
	)

	RenderChannelZDepth.depth_black= FloatProperty(
		name= "Black distance",
		description= "",
		min= 0.0,
		max= 100000.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0
	)

	RenderChannelZDepth.depth_white= FloatProperty(
		name= "White distance",
		description= "",
		min= 0.0,
		max= 100000.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1000
	)

	RenderChannelZDepth.depth_clamp= BoolProperty(
		name= "Clamp",
		description= "",
		default= True
	)

	RenderChannelZDepth.filtering= BoolProperty(
		name= "Filtering",
		description= "",
		default= True
	)



'''
  OUTPUT
'''
def write(ofile, render_channel, sce= None, name= None):
	channel_name= render_channel.name
	if name is not None:
		channel_name= name

	ofile.write("\n%s %s {"%(PLUG, clean_string(channel_name)))
	for param in PARAMS:
		if param == 'name':
			value= "\"%s\"" % channel_name
		else:
			value= getattr(render_channel, param)
		ofile.write("\n\t%s= %s;"%(param, p(value)))
	ofile.write("\n}\n")



'''
  GUI
'''
def draw(rna_pointer, layout, wide_ui):
	split= layout.split()
	col= split.column()
	col.prop(rna_pointer, 'depth_black', text="Black dist")
	col.prop(rna_pointer, 'depth_white', text="White dist")
	if wide_ui:
		col = split.column()
	col.prop(rna_pointer, 'depth_from_camera')
	col.prop(rna_pointer, 'depth_clamp')
	col.prop(rna_pointer, 'filtering')
