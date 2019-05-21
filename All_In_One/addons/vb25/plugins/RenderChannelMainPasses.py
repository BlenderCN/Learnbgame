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
ID=   'MAINPASSES'
NAME= 'Main Passes'
PLUG= 'RenderChannelMainPasses'
DESC= "TODO"
PID=  2

PARAMS= None

PARAM_MAP= {
	'RGB':                 1,
	'Diffuse':           101,
	'Reflect':           102,
	'Refract':           103,
	'Self Illumination': 104,
	'Shadow':            105,
	'Specular':          106,
	'Lightning':         107,
	'GI':                108,
	'Caustics':          109,
	'Raw GI':            110,
	'Raw Lightning':     111,
	'Raw Shadow':        112,
	'Velocity':          113,

	'Reflection Filter': 118,
	'Raw Reflection':    119,
	'Refraction Filter': 120,
	'Raw Refraction':    121,
	'Real Color':        122,
	
	'Background':          124,
	'Alpha':               125,
	'Wire Color':          127,
	'Matte Shadow':        128,
	'Total Lightning':     129,
	'Raw Total Lightning': 130,
	'Bump Normal':         131,
	'Samplerate':          132,
	'SSS':                 133,
}


''' Blender modules '''
import bpy
from bpy.props import *

''' vb modules '''
from vb25.utils import *


class RenderChannelMainPasses(bpy.types.PropertyGroup):
	pass
bpy.utils.register_class(RenderChannelMainPasses)

def add_properties(parent_struct):
	parent_struct.RenderChannelMainPasses= PointerProperty(
		type= RenderChannelMainPasses,
		name= NAME,
		description= "V-Ray main render channels"
	)

	RenderChannelMainPasses.name= StringProperty(
		name= "Name",
		description= "Channel name",
		default= NAME
	)

	for key in PARAM_MAP:
		chan_name= key.replace(' ','_')
		chan_name= chan_name.lower()
		chan_id= PARAM_MAP[key]

		setattr(RenderChannelMainPasses, 'channel_%s' % chan_name, bpy.props.BoolProperty(
			attr= 'channel_%s' % chan_name,
			name= "%s" % key,
			description= "%s channel" % key,
			default= False)
		)

		setattr(RenderChannelMainPasses, '%s_cm' % chan_name, bpy.props.BoolProperty(
			name= "Color mapping",
			description= "Apply color mapping to \"%s\" channel" % key,
			default= False)
		)

		setattr(RenderChannelMainPasses, '%s_aa' % chan_name, bpy.props.BoolProperty(
			name= "Consider for AA",
			description= "Apply AA to \"%s\" channel" % key,
			default= False)
		)

		setattr(RenderChannelMainPasses, '%s_filt' % chan_name, bpy.props.BoolProperty(
			name= "Filtering",
			description= "Apply filtering to \"%s\" channel" % key,
			default= True)
		)
	


'''
  OUTPUT
'''
def write(ofile, render_channel, sce= None, name= None):
	channel_name= render_channel.name
	if name is not None:
		channel_name= name

	for key in PARAM_MAP:
		chan_name= key.replace(' ','_')
		chan_prop= chan_name.lower()

		chan_id= PARAM_MAP[key]
		chan_cm= getattr(render_channel, '%s_cm' % chan_prop)
		chan_filt= getattr(render_channel, '%s_aa' % chan_prop)
		chan_aa= getattr(render_channel, '%s_filt' % chan_prop)
		
		if(getattr(render_channel, 'channel_%s' % chan_prop)):
			ofile.write("\nRenderChannelColor %s {" % (clean_string("%s_%s" % (channel_name,chan_name))))
			ofile.write("\n\tname= \"%s\";" % chan_name)
			ofile.write("\n\talias= %d;" % chan_id)
			ofile.write("\n\tcolor_mapping= %d;"%(chan_cm))
			ofile.write("\n\tconsider_for_aa= %d;"%(chan_aa))
			ofile.write("\n\tfiltering= %d;"%(chan_filt))
			ofile.write("\n}\n")



'''
  GUI
'''
def draw(rna_pointer, layout, wide_ui):
	def channel_but(layout, channel, cm, aa, filt):
		split= layout.split()
		col= split.column()
		col.prop(rna_pointer, channel)
		if wide_ui:
			col= split.row()
		else:
			col= col.row()
		if getattr(rna_pointer, channel):
			col.prop(rna_pointer, cm, text="CM")
			col.prop(rna_pointer, aa, text="AA")
			col.prop(rna_pointer, filt, text="F")

	for key in sorted(PARAM_MAP):
		chan_name= key.replace(' ','_')
		chan_name= chan_name.lower()
		chan_prop= "channel_%s" % chan_name

		chan_id= PARAM_MAP[key]
		chan_cm= '%s_cm' % chan_name
		chan_aa= '%s_aa' % chan_name
		chan_filt= '%s_filt' % chan_name

		channel_but(layout, chan_prop, chan_cm, chan_aa, chan_filt)
