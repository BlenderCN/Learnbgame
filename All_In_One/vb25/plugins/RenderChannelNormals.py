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
ID=   'NORMALS'
NAME= 'Normals'
PLUG= 'RenderChannelNormals'
DESC= ""
PID=  4

PARAMS= (
	'name',
	'filtering'
)


''' Blender modules '''
import bpy
from bpy.props import *

''' vb modules '''
from vb25.utils import *


class RenderChannelNormals(bpy.types.PropertyGroup):
	pass
bpy.utils.register_class(RenderChannelNormals)

def add_properties(parent_struct):
	parent_struct.RenderChannelNormals= PointerProperty(
		name= "Normals",
		type=  RenderChannelNormals,
		description= "V-Ray render channel \"Normals\" settings"
	)

	RenderChannelNormals.name= StringProperty(
		name= "Name",
		description= "",
		default= "Normals"
	)

	RenderChannelNormals.filtering= BoolProperty(
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
	col.prop(rna_pointer, 'filtering')
	
