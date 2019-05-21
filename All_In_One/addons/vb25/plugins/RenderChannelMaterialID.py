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
ID=   'MATERIALID'
NAME= 'Material ID'
PLUG= 'RenderChannelMaterialID'
DESC= ""
PID=  11

PARAMS= (
	'name'
)


''' Blender modules '''
import bpy
from bpy.props import *

''' vb modules '''
from vb25.utils import *


def add_properties(parent_struct):
	class RenderChannelMaterialID(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(RenderChannelMaterialID)
	
	parent_struct.RenderChannelMaterialID= PointerProperty(
		name= "Material ID",
		type=  RenderChannelMaterialID,
		description= "V-Ray render channel \"Material ID\" settings"
	)

	RenderChannelMaterialID.name= StringProperty(
		name= "Name",
		description= "",
		default= "Material ID"
	)



'''
  OUTPUT
'''
def write(ofile, render_channel, sce= None, name= None):
	channel_name= render_channel.name
	if name is not None:
		channel_name= name

	ofile.write("\nRenderChannelColor %s {" % clean_string(channel_name))
	ofile.write("\n\tname=\"%s\";" % clean_string(channel_name))
	ofile.write("\n\talias=115;")
	ofile.write("\n\tconsider_for_aa=0;")
	ofile.write("\n}\n")


def draw(rna_pointer, layout, wide_ui):
	pass
