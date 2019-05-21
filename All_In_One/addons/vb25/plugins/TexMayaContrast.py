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
ID=   'TexMayaContrast'
PLUG= 'TexMayaContrast'
NAME= 'Maya Contrast'
DESC= "Maya Contrast."
PID=   28

PARAMS= (
	'value',
	'contrast',
	'bias',
)

def add_properties(rna_pointer):
	class TexMayaContrast(bpy.types.PropertyGroup):

		#  value: acolor texture = AColor(0, 0, 0, 1)
		value = FloatVectorProperty(
			name        = "Value",
			description = "Value",
			subtype     = 'COLOR',
			size        = 4,
			min         = 0.0,
			max         = 1.0,
			soft_min    = 0.0,
			soft_max    = 1.0,
			default     = (0,0,0,1)
		)

		value_tex = StringProperty(
			name        = "Input Texture",
			description = "Input Texture",
			default     = ""
		)

		#  contrast: acolor texture = AColor(2, 2, 2, 1)
		contrast = FloatVectorProperty(
			name        = "Contrast",
			description = "Contrast",
			subtype     = 'COLOR',
			size        = 4,
			min         = 0.0,
			max         = 1.0,
			soft_min    = 0.0,
			soft_max    = 1.0,
			default     = (2, 2, 2, 1)
		)

		contrast_tex = StringProperty(
			name        = "Contrast Texture",
			description = "Contrast Texture",
			default     = ""
		)
		
		#  bias: acolor texture = AColor(0.5, 0.5, 0.5, 1)
		bias = FloatVectorProperty(
			name        = "Bias",
			description = "Bias",
			subtype     = 'COLOR',
			size        = 4,
			min         = 0.0,
			max         = 1.0,
			soft_min    = 0.0,
			soft_max    = 1.0,
			default     = (0.5, 0.5, 0.5, 1)
		)

		bias_tex = StringProperty(
			name        = "Bias Texture",
			description = "Bias Texture",
			default     = ""
		)
		

	bpy.utils.register_class(TexMayaContrast)

	rna_pointer.TexMayaContrast = PointerProperty(
		name        = "TexMayaContrast",
		type        =  TexMayaContrast,
		description = "V-Ray TexMayaContrast settings"
	)


def write(bus):
	scene = bus['scene']
	ofile = bus['files']['textures']

	slot     = bus['mtex']['slot']
	texture  = bus['mtex']['texture']
	tex_name = bus['mtex']['name']

#	uvwgen= write_uvwgen(bus)

	TexMayaContrast= getattr(texture.vray, PLUG)

	mapped_keys= ('value', 'contrast', 'bias')
	mapped_params= write_sub_textures(bus,
					  TexMayaContrast,
					  [key+'_tex' for key in mapped_keys])
	
	ofile.write("\n%s %s {"%(PLUG, tex_name))
	for param in PARAMS:
		if param == 'uvwgen':
			value= uvwgen
		elif param in mapped_keys and param+'_tex' in mapped_params:
			value= mapped_params[param+'_tex']
		else:
			value= getattr(TexMayaContrast, param)
		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))
	ofile.write("\n}\n")

	return tex_name

'''
  GUI
'''
class VRAY_TP_TexMayaContrast(ui.VRayTexturePanel, bpy.types.Panel):
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
		TexMayaContrast= getattr(tex.vray, PLUG)

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexMayaContrast, 'value', text="Value")
		col.prop_search(TexMayaContrast, 'value_tex',
						bpy.data,    'textures',
						text= "")

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexMayaContrast, 'contrast', text="Contrast")
		col.prop_search(TexMayaContrast, 'contrast_tex',
						bpy.data,    'textures',
						text= "")

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexMayaContrast, 'bias', text="Bias")
		col.prop_search(TexMayaContrast, 'bias_tex',
						bpy.data,    'textures',
						text= "")


def GetRegClasses():
	return (
		VRAY_TP_TexMayaContrast,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
