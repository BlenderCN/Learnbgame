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
ID=   'TexChecker'
PLUG= 'TexChecker'

NAME= 'Checker'
DESC= "TexChecker."

PID=   14

PARAMS= (
	'uvwgen',
	'white_color',
	'black_color',
	'contrast',
)


def add_properties(rna_pointer):
	class TexChecker(bpy.types.PropertyGroup):
		# white_color
		white_color= FloatVectorProperty(
			name= "White color",
			description= "The white checker color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (1,1,1)
		)

		white_color_tex= StringProperty(
			name= "White color",
			description= "The white checker color",
			default= ""
		)

		# black_color
		black_color= FloatVectorProperty(
			name= "Black color",
			description= "The black checker color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0,0,0)
		)

		black_color_tex= StringProperty(
			name= "Black color",
			description= "The black checker color",
			default= ""
		)

		# contrast
		contrast= FloatProperty(
			name= "Contrast",
			description= "Contrast value",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 2.0,
			precision= 3,
			default= 1.0
		)

		contrast_tex= StringProperty(
			name= "Contrast",
			description= "Contrast value",
			default= ""
		)

	bpy.utils.register_class(TexChecker)

	rna_pointer.TexChecker= PointerProperty(
		name= "TexChecker",
		type=  TexChecker,
		description= "V-Ray TexChecker settings"
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

	TexChecker= getattr(texture.vray, PLUG)

	ofile.write("\n%s %s {"%(PLUG, tex_name))

	PLUGINS['TEXTURE']['TexCommon'].write(bus)

	for param in PARAMS:
		if param == 'uvwgen':
			value= uvwgen
		else:
			value= getattr(TexChecker, param)
		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))

	ofile.write("\n}\n")

	return tex_name


'''
  GUI
'''
class VRAY_TP_TexChecker(ui.VRayTexturePanel, bpy.types.Panel):
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
		TexChecker= getattr(tex.vray, PLUG)

		split= layout.split()
		col= split.column()
		col.prop(TexChecker, 'white_color', text="")
		if wide_ui:
			col= split.column()
		col.prop(TexChecker, 'black_color', text="")

		split= layout.split()
		col= split.column()
		col.prop(TexChecker, 'contrast', slider= True)


def GetRegClasses():
	return (
		VRAY_TP_TexChecker,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
