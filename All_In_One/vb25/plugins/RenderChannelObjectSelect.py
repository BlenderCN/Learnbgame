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

ID=   'OBJECTSELECT'
NAME= 'Object Select'
PLUG= 'RenderChannelObjectSelect'
DESC= ""
PID=  5

PARAMS= (
	'name',
	'id',
	'use_mtl_id',
	'affect_matte_objects',
	'consider_for_aa'
)


''' Blender modules '''
import bpy
from bpy.props import *

''' vb modules '''
from vb25.utils import *


class RenderChannelObjectSelect(bpy.types.PropertyGroup):
    pass
bpy.utils.register_class(RenderChannelObjectSelect)

def add_properties(parent_struct):
	parent_struct.RenderChannelObjectSelect= PointerProperty(
		name= "Object select",
		type=  RenderChannelObjectSelect,
		description= "V-Ray render channel \"Object select\" settings"
	)

	RenderChannelObjectSelect.name= StringProperty(
		name= "Name",
		description= "Render channel name",
		maxlen= 64,
		default= "ObjectSelect"
	)

	RenderChannelObjectSelect.id= IntProperty(
		name= "ID",
		description= "The object/material ID that will be extracted",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 100,
		default= 0
	)

	RenderChannelObjectSelect.use_mtl_id= BoolProperty(
		name= "Use material ID",
		description= "Use the material IDs instead of the object IDs",
		default= False
	)

	RenderChannelObjectSelect.affect_matte_objects= BoolProperty(
		name= "Affect matte objects",
		description= "False to not affect Matte Objects",
		default= True
	)

	RenderChannelObjectSelect.consider_for_aa= BoolProperty(
		name= "Consider for AA",
		description= "TODO",
		default= False
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
	col.prop(rna_pointer, 'id')
	col.prop(rna_pointer, 'use_mtl_id')
	if wide_ui:
		col = split.column()
	col.prop(rna_pointer, 'affect_matte_objects')
	col.prop(rna_pointer, 'consider_for_aa')
