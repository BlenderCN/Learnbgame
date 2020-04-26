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
ID=   'VELOCITY'
NAME= 'Velocity'
PLUG= 'RenderChannelVelocity'
DESC= ""
PID=  7

PARAMS= (
	'name',
	'clamp_velocity',
	'max_velocity',
	'max_velocity_last_frame',
	'ignore_z',
	'filtering'
)


''' Blender modules '''
import bpy
from bpy.props import *

''' vb modules '''
from vb25.utils import *


class RenderChannelVelocity(bpy.types.PropertyGroup):
	pass
bpy.utils.register_class(RenderChannelVelocity)

def add_properties(parent_struct):
	parent_struct.RenderChannelVelocity= PointerProperty(
		name= "Velocity",
		type=  RenderChannelVelocity,
		description= "V-Ray render channel \"Velocity\" settings"
	)

	RenderChannelVelocity.name= StringProperty(
		name= "Name",
		description= "",
		default= "Velocity"
	)

	RenderChannelVelocity.clamp_velocity= BoolProperty(
		name= "Clamp",
		description= "",
		default= True
	)

	RenderChannelVelocity.max_velocity= FloatProperty(
		name= "Max velocity",
		description= "Max velocity",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	RenderChannelVelocity.max_velocity_last_frame= FloatProperty(
		name= "Max velocity last frame",
		description= "Max velocity last frame",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0
	)

	RenderChannelVelocity.ignore_z= BoolProperty(
		name= "Ignore Z",
		description= "",
		default= True
	)

	RenderChannelVelocity.filtering= BoolProperty(
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
	col.prop(rna_pointer, 'max_velocity')
	col.prop(rna_pointer, 'max_velocity_last_frame', text="Max last")
	if wide_ui:
		col = split.column()
	col.prop(rna_pointer, 'clamp_velocity')
	col.prop(rna_pointer, 'ignore_z')
	col.prop(rna_pointer, 'filtering')

