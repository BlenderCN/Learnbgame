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
ID=   'EXTRATEX'
NAME= 'ExtraTex'
PLUG= 'RenderChannelExtraTex'
DESC= ""
PID=  1

PARAMS= (
	'name',
	'consider_for_aa',
	'affect_matte_objects',
	'texmap',
	'filtering'
)


''' Blender modules '''
import bpy
from bpy.props import *

''' vb modules '''
from vb25.utils import *
from vb25.shaders import *


class RenderChannelExtraTex(bpy.types.PropertyGroup):
	pass
bpy.utils.register_class(RenderChannelExtraTex)

def add_properties(parent_struct):
	parent_struct.RenderChannelExtraTex= PointerProperty(
		name= "ExtraTex",
		type=  RenderChannelExtraTex,
		description= "V-Ray render channel \"ExtraTex\" settings"
	)

	RenderChannelExtraTex.name= StringProperty(
		name= "Name",
		description= "",
		default= "ExtraTex"
	)

	RenderChannelExtraTex.consider_for_aa= BoolProperty(
		name= "Consider for AA",
		description= "",
		default= True
	)

	RenderChannelExtraTex.affect_matte_objects= BoolProperty(
		name= "Affect matte objects",
		description= "",
		default= True
	)

	RenderChannelExtraTex.texmap= StringProperty(
		name= "Texture",
		description= "",
		default= ""
	)

	RenderChannelExtraTex.filtering= BoolProperty(
		name= "Filtering",
		description= "",
		default= True
	)
	


'''
  OUTPUT
'''
def write(bus, render_channel, sce= None, name= None):
	ofile= bus['files']['scene']
	scene= bus['scene']

	channel_name= name if name is not None else render_channel.name

	if render_channel.texmap not in bpy.data.textures:
		return
	
	# Store mtex context
	context_mtex = None
	if 'mtex' in bus:
		context_mtex = bus['mtex']

	bus['mtex']= {}
	bus['mtex']['env']=     True # This is needed!
	bus['mtex']['slot']=    None
	bus['mtex']['texture']= bpy.data.textures[render_channel.texmap]
	bus['mtex']['factor']=  1.0
	bus['mtex']['mapto']=   None
	bus['mtex']['name']=    clean_string("EXTRATE%s" % (render_channel.texmap))

	texmap= write_texture(bus)

	# Restore mtex context
	if context_mtex:
		bus['mtex'] = context_mtex

	ofile.write("\n%s %s {"%(PLUG, clean_string(channel_name)))
	for param in PARAMS:
		if param == 'name':
			value= "\"%s\"" % channel_name
		elif param == 'texmap':
			value= texmap
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
	col.prop_search(rna_pointer, 'texmap', bpy.data, 'textures')

	split= layout.split()
	col= split.column()
	col.prop(rna_pointer, 'filtering')
	if wide_ui:
		col = split.column()
	col.prop(rna_pointer, 'consider_for_aa')
	col.prop(rna_pointer, 'affect_matte_objects')

