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
ID=   'TexMaskMax'
PLUG= 'TexMaskMax'
NAME= 'Mask Max'
DESC= "Mask Max."
PID=   29

PARAMS= (
	'texture',
	'mask',
	'invert_mask',
)


def add_properties(rna_pointer):
	class TexMaskMax(bpy.types.PropertyGroup):

		#  texture: acolor texture = AColor(1, 1, 1, 1), The base texture
		texture = FloatVectorProperty(
			name        = "Value",
			description = "Value",
			subtype     = 'COLOR',
			size        = 4,
			min         = 0.0,
			max         = 1.0,
			soft_min    = 0.0,
			soft_max    = 1.0,
			default     = (1,1,1,1)
		)

		texture_tex = StringProperty(
			name        = "Input Texture",
			description = "Input Texture",
			default     = ""
		)

		#  mask: acolor texture = AColor(1, 1, 1, 1), The mask texture
		mask = FloatVectorProperty(
			name        = "Contrast",
			description = "Contrast",
			subtype     = 'COLOR',
			size        = 4,
			min         = 0.0,
			max         = 1.0,
			soft_min    = 0.0,
			soft_max    = 1.0,
			default     = (1, 1, 1, 1)
		)

		mask_tex = StringProperty(
			name        = "Contrast Texture",
			description = "Contrast Texture",
			default     = ""
		)
		
		#  invert_mask: bool = false, true to invert the mask
		invert_mask  = BoolProperty(
			name        = "Invert mask",
			description = "",
			default     = True
		)

		

	bpy.utils.register_class(TexMaskMax)

	rna_pointer.TexMaskMax= PointerProperty(
		name= "TexMaskMax",
		type=  TexMaskMax,
		description= "V-Ray TexMaskMax settings"
	)


def write(bus):
	scene = bus['scene']
	ofile = bus['files']['textures']

	slot     = bus['mtex']['slot']
	texture  = bus['mtex']['texture']
	tex_name = bus['mtex']['name']

	TexMaskMax= getattr(texture.vray, PLUG)

	mapped_keys= ('texture', 'mask')
	mapped_params= write_sub_textures(bus,
				   TexMaskMax,
				   [key+'_tex' for key in mapped_keys])
	
	ofile.write("\n%s %s {"%(PLUG, tex_name))
	for param in PARAMS:
		if param == 'uvwgen':
			value= uvwgen
		elif param in mapped_keys and param+'_tex' in mapped_params:
			value= mapped_params[param+'_tex']
		else:
			value= getattr(TexMaskMax, param)
		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))
	ofile.write("\n}\n")

	return tex_name

'''
  GUI
'''
class VRAY_TP_TexMaskMax(ui.VRayTexturePanel, bpy.types.Panel):
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
		TexMaskMax= getattr(tex.vray, PLUG)

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexMaskMax, 'texture', text="Texture")
		col.prop_search(TexMaskMax, 'texture_tex',
						bpy.data,    'textures',
						text= "")

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexMaskMax, 'mask', text="Mask")
		col.prop_search(TexMaskMax, 'mask_tex',
						bpy.data,    'textures',
						text= "")

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexMaskMax, 'invert_mask', text="Invert")


def GetRegClasses():
	return (
		VRAY_TP_TexMaskMax,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
