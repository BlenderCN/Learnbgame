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

ID=   'MULTIMATTE'
NAME= 'MultiMatte'
PLUG= 'RenderChannelMultiMatte'
DESC= ""
PID=  3

PARAMS= (
	'name',
	'red_id',
	'green_id',
	'blue_id',
	'use_mtl_id',
	'affect_matte_objects'
)


''' Blender modules '''
import bpy
from bpy.props import *

''' vb modules '''
from vb25.utils import *


class RenderChannelMultiMatte(bpy.types.PropertyGroup):
    pass
bpy.utils.register_class(RenderChannelMultiMatte)

def add_properties(parent_struct):
	parent_struct.RenderChannelMultiMatte= PointerProperty(
		name= "MultiMatte",
		type=  RenderChannelMultiMatte,
		description= "V-Ray render channel \"MultiMatte\" settings"
	)

	RenderChannelMultiMatte.name= StringProperty(
		name= "Name",
		description= "Render channel name",
		maxlen= 64,
		default= "MultiMatte"
	)

	RenderChannelMultiMatte.red_id= IntProperty(
		name= "Red ID",
		description= "The object ID that will be written as the red channel (0 to disable the red channel)",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 0
	)

	RenderChannelMultiMatte.green_id= IntProperty(
		name= "Green ID",
		description= "The object ID that will be written as the green channel (0 to disable the green channel)",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 0
	)

	RenderChannelMultiMatte.blue_id= IntProperty(
		name= "Blue ID",
		description= "The object ID that will be written as the blue channel (0 to disable the blue channel)",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 0
	)

	RenderChannelMultiMatte.use_mtl_id= BoolProperty(
		name= "Use material ID",
		description= "Use the material IDs instead of the object IDs",
		default= False
	)

	RenderChannelMultiMatte.affect_matte_objects= BoolProperty(
		name= "Affect matte objects",
		description= "Affect Matte Objects",
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
	col.prop(rna_pointer, 'red_id')
	col.prop(rna_pointer, 'green_id')
	col.prop(rna_pointer, 'blue_id')
	if wide_ui:
		col = split.column()
	col.prop(rna_pointer, 'use_mtl_id')
	col.prop(rna_pointer, 'affect_matte_objects')
