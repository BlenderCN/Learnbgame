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
from vb25.utils   import *
from vb25.ui      import ui
from vb25.plugins import *
from vb25.texture import *
from vb25.uvwgen  import *


TYPE= 'TEXTURE'
ID=   'TexCloth'
PLUG= 'TexCloth'

NAME= 'Cloth'
DESC= "TexCloth."

PID=   13

PARAMS= (
	'uvwgen',
	'gap_color',
	'u_color',
	'v_color',
	'u_width',
	'v_width',
	'u_wave',
	'v_wave',
	'randomness',
	'width_spread',
	'bright_spread',
)


def add_properties(rna_pointer):
	class TexCloth(bpy.types.PropertyGroup):
		# gap_color
		gap_color= FloatVectorProperty(
			name= "Gap",
			description= "Gap color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0.1,0.1,0.1)
		)

		gap_color_tex= StringProperty(
			name= "gap color",
			description= "",
			default= ""
		)

		# u_color
		u_color= FloatVectorProperty(
			name= "U",
			description= "U color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0.5,0.5,0.5)
		)

		u_color_tex= StringProperty(
			name= "u color",
			description= "",
			default= ""
		)

		# v_color
		v_color= FloatVectorProperty(
			name= "V",
			description= "V color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (1,1,1)
		)

		v_color_tex= StringProperty(
			name= "v color",
			description= "",
			default= ""
		)

		# u_width
		u_width= FloatProperty(
			name= "U width",
			description= "U width",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			default= 1.0
		)

		u_width_tex= StringProperty(
			name= "u width",
			description= "",
			default= ""
		)

		# v_width
		v_width= FloatProperty(
			name= "V width",
			description= "V width",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			default= 1.0
		)

		v_width_tex= StringProperty(
			name= "v width",
			description= "",
			default= ""
		)

		# u_wave
		u_wave= FloatProperty(
			name= "U wave",
			description= "U wave",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			default= 1.0
		)

		u_wave_tex= StringProperty(
			name= "u wave",
			description= "",
			default= ""
		)

		# v_wave
		v_wave= FloatProperty(
			name= "V wave",
			description= "V wave",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 100.0,
			default= 1.0
		)

		v_wave_tex= StringProperty(
			name= "v wave",
			description= "",
			default= ""
		)

		# randomness
		randomness= FloatProperty(
			name= "Randomness",
			description= "Randomness",
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 0.0
		)

		randomness_tex= StringProperty(
			name= "randomness",
			description= "",
			default= ""
		)

		# width_spread
		width_spread= FloatProperty(
			name= "Width spread",
			description= "Width spread",
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		width_spread_tex= StringProperty(
			name= "width spread",
			description= "",
			default= ""
		)

		# bright_spread
		bright_spread= FloatProperty(
			name= "Bright spread",
			description= "Bright spread",
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		bright_spread_tex= StringProperty(
			name= "bright spread",
			description= "",
			default= ""
		)

	bpy.utils.register_class(TexCloth)

	rna_pointer.TexCloth= PointerProperty(
		name= "TexCloth",
		type=  TexCloth,
		description= "V-Ray TexCloth settings"
	)


'''
  OUTPUT
'''
def write(bus):
	scene= bus['scene']
	ofile= bus['files']['textures']

	slot=     bus['mtex']['slot']
	texture=  bus['mtex']['texture']
	tex_name= bus['mtex']['name']

	uvwgen= write_uvwgen(bus)

	TexCloth= getattr(texture.vray, PLUG)

	ofile.write("\n%s %s {"%(PLUG, tex_name))

	PLUGINS['TEXTURE']['TexCommon'].write(bus)

	for param in PARAMS:
		if param == 'uvwgen':
			value= uvwgen
		else:
			value= getattr(TexCloth, param)
		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))

	ofile.write("\n}\n")

	return tex_name


'''
  GUI
'''
class VRAY_TP_TexCloth(ui.VRayTexturePanel, bpy.types.Panel):
	bl_label       = NAME
	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		tex= context.texture
		return tex and tex.type == 'VRAY' and tex.vray.type == ID and ui.engine_poll(cls, context)

	def draw(self, context):
		wide_ui= context.region.width > ui.narrowui
		layout= self.layout

		tex= context.texture
		TexCloth= getattr(tex.vray, PLUG)

		split= layout.split()
		col= split.column()
		col.prop(TexCloth, 'gap_color', text= "")
		if wide_ui:
			col= split.column()
		col.prop(TexCloth, 'randomness', slider= True)

		split= layout.split()
		col= split.column()
		sub= col.column(align= True)
		sub.prop(TexCloth, 'u_color')
		sub.prop(TexCloth, 'u_width', text="Width")
		sub.prop(TexCloth, 'u_wave', text="Wave")
		if wide_ui:
			col= split.column()
		sub= col.column(align= True)
		sub.prop(TexCloth, 'v_color')
		sub.prop(TexCloth, 'v_width', text="Width")
		sub.prop(TexCloth, 'v_wave', text="Wave")

		split= layout.split()
		col= split.column()
		col.prop(TexCloth, 'width_spread', slider= True)
		if wide_ui:
			col= split.column()
		col.prop(TexCloth, 'bright_spread', slider= True)


def GetRegClasses():
	return (
		VRAY_TP_TexCloth,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
