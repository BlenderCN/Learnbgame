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
ID=   'TexMarbleMax'
PLUG= 'TexMarbleMax'
NAME= 'Marble'
DESC= "TexMarbleMax."
PID=   9

PARAMS= (
	'color1',
	'color2',
	'size',
	'vein_width',
	'uvwgen',
)


def add_properties(rna_pointer):
	class TexMarbleMax(bpy.types.PropertyGroup):
		# color1
		color1= FloatVectorProperty(
			name= "First color",
			description= "First color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (1,1,1)
		)

		color1_tex= StringProperty(
			name= "First texture ",
			description= "First texture",
			default= ""
		)

		# color2
		color2= FloatVectorProperty(
			name= "Second color",
			description= "Second color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0,0,0)
		)

		color2_tex= StringProperty(
			name= "Second texture ",
			description= "Second texture",
			default= ""
		)

		# size
		size= FloatProperty(
			name= "Size",
			description= "Size",
			min= 0.0,
			max= 1000.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 1.0
		)

		# vein_width
		vein_width= FloatProperty(
			name= "Vein width",
			description= "Vein width",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.02
		)

	bpy.utils.register_class(TexMarbleMax)

	rna_pointer.TexMarbleMax= PointerProperty(
		name= "TexMarbleMax",
		type=  TexMarbleMax,
		description= "V-Ray TexMarbleMax settings"
	)


def write(bus):
	scene= bus['scene']
	ofile= bus['files']['textures']

	slot=     bus['mtex']['slot']
	texture=  bus['mtex']['texture']
	tex_name= bus['mtex']['name']

	uvwgen= write_uvwgen(bus)

	TexMarbleMax= getattr(texture.vray, PLUG)

	mapped_params= write_sub_textures(bus,
									  TexMarbleMax,
									  ('color1_tex', 'color2_tex'))
	
	ofile.write("\n%s %s {"%(PLUG, tex_name))
	for param in PARAMS:
		if param == 'uvwgen':
			value= uvwgen

		elif param in ('color1','color2') and param+'_tex' in mapped_params:
			value= mapped_params[param+'_tex']

		else:
			value= getattr(TexMarbleMax, param)
		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))
	ofile.write("\n}\n")

	return tex_name


'''
  GUI
'''
class VRAY_TP_TexMarbleMax(ui.VRayTexturePanel, bpy.types.Panel):
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
		TexMarbleMax= getattr(tex.vray, PLUG)

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexMarbleMax, 'color1')
		col.prop_search(TexMarbleMax, 'color1_tex',
						bpy.data, 'textures',
						text= "")
		if wide_ui:
			col= split.column(align= True)
		col.prop(TexMarbleMax, 'color2')
		col.prop_search(TexMarbleMax, 'color2_tex',
						bpy.data, 'textures',
						text= "")

		layout.separator()
		
		split= layout.split()
		col= split.column()
		col.prop(TexMarbleMax, 'size')
		if wide_ui:
			col= split.column()
		col.prop(TexMarbleMax, 'vein_width')


def GetRegClasses():
	return (
		VRAY_TP_TexMarbleMax,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
