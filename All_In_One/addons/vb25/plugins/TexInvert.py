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


TYPE = 'TEXTURE'
ID   = 'TexInvert'
PLUG = 'TexInvert'
NAME = 'Invert'
DESC = "Invert."
PID  =  26

PARAMS= (
	'texture',
	'invert_alpha',
)


def add_properties(rna_pointer):
	class TexInvert(bpy.types.PropertyGroup):

		texture = StringProperty(
			name        = "Invert Texture",
			description = "Invert Texture",
			default     = ""
		)

		invert_alpha = BoolProperty(
			name        = "Invert Alpha",
			description = "",
			default     = True
		)

		

	bpy.utils.register_class(TexInvert)

	rna_pointer.TexInvert = PointerProperty(
		name        = "TexInvert",
		type        =  TexInvert,
		description = "V-Ray TexInvert settings"
	)


def write(bus):
	scene    = bus['scene']
	ofile    = bus['files']['textures']

	slot     = bus['mtex']['slot']
	texture  = bus['mtex']['texture']
	tex_name = bus['mtex']['name']

	TexInvert = getattr(texture.vray, PLUG)

	mapped_keys   = ('texture')
	mapped_params = write_sub_textures(bus,
									  TexInvert,
									  ['texture' for key in mapped_keys])
	
	ofile.write("\n%s %s {"%(PLUG, tex_name))
	for param in PARAMS:
		if param == 'uvwgen':
			value = uvwgen
		elif param == 'texture':
			value = mapped_params['texture']
		else:
			value = getattr(TexInvert, param)
		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))
	ofile.write("\n}\n")

	return tex_name

'''
  GUI
'''

class VRAY_TP_TexInvert(ui.VRayTexturePanel, bpy.types.Panel):
	bl_label       = NAME
	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		tex= context.texture
		return tex and tex.type == 'VRAY' and tex.vray.type == ID and ui.engine_poll(cls, context)

	def draw(self, context):
		wide_ui   = context.region.width > ui.narrowui
		layout    = self.layout

		tex       = context.texture
		TexInvert = getattr(tex.vray, PLUG)

		split     = layout.split()
		col       = split.column(align= True)
		col.prop_search(TexInvert, 'texture',
							bpy.data,    'textures',
							text= "")

		col.prop(TexInvert, 'invert_alpha', text="Invert Alpha")


def GetRegClasses():
	return (
		VRAY_TP_TexInvert,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
