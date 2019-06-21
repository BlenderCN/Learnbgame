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
ID=   'TexMix'
PLUG= 'TexMix'
NAME= 'Mix'
DESC= "Mix."
PID=   31

PARAMS= (
	'color1',
	'color2',
	'mix_map',
	'mix_amount',
	'transition_upper',
	'transition_lower',
	'use_curve'
)

def add_properties(rna_pointer):
	class TexMix(bpy.types.PropertyGroup):

		#  color1: acolor texture = AColor(1, 1, 1, 1), First color
		color1 = FloatVectorProperty(
			name        = "First color",
			description = "First color",
			subtype     = 'COLOR',
			size        = 4,
			min         = 0.0,
			max         = 1.0,
			soft_min    = 0.0,
			soft_max    = 1.0,
			default     = (1,1,1,1)
		)

		color1_tex = StringProperty(
			name        = "First color Texture",
			description = "First color Texture",
			default     = ""
		)

		#  color2: acolor texture = AColor(0, 0, 0, 0), Second color
		color2 = FloatVectorProperty(
			name        = "Second color",
			description = "Second color",
			subtype     = 'COLOR',
			size        = 4,
			min         = 0.0,
			max         = 1.0,
			soft_min    = 0.0,
			soft_max    = 1.0,
			default     = (0, 0, 0, 0)
		)

		color2_tex = StringProperty(
			name        = "Second color Texture",
			description = "Second color Texture",
			default     = ""
		)

		#  mix_map: acolor texture = AColor(0.5, 0.5, 0.5, 1), Mix amount texture
		mix_map = FloatVectorProperty(
			name        = "Mix amount texture",
			description = "Mix amount texture",
			subtype     = 'COLOR',
			size        = 4,
			min         = 0.0,
			max         = 1.0,
			soft_min    = 0.0,
			soft_max    = 1.0,
			default     = (0.5, 0.5, 0.5, 1)
		)

		mix_map_tex = StringProperty(
			name        = "Mix amount Texture",
			description = "Mix amount Texture",
			default     = ""
		)
		
		#  mix_amount: float = 0, Mix amount
		mix_amount = FloatProperty(
			name        = "Mix amount",
			description = "Mix amount",
			min         = 0.0,
			max         = 100.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 0
		)

		#  transition_upper: float = 0.7, Transition zone - upper
		transition_upper = FloatProperty(
			name        = "Upper",
			description = "Transition zone - upper",
			min         = 0.0,
			max         = 100.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 0.7
		)

		#  transition_lower: float = 0.3, Transition zone - lower
		transition_lower = FloatProperty(
			name        = "Lower",
			description = "Transition zone - lower",
			min         = 0.0,
			max         = 100.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 0.3
		)

		# use_curve: integer = 0, If true the blend curve is used
		use_curve = IntProperty(
			name        = "Curve",
			description = "If true the blend curve is used",
			min         = 0,
			max         = 100,
			default     = 0
		)

		

	bpy.utils.register_class(TexMix)

	rna_pointer.TexMix = PointerProperty(
		name        = "TexMix",
		type        =  TexMix,
		description = "V-Ray TexMix settings"
	)


def write(bus):
	scene = bus['scene']
	ofile = bus['files']['textures']

	slot     = bus['mtex']['slot']
	texture  = bus['mtex']['texture']
	tex_name = bus['mtex']['name']

	TexMix = getattr(texture.vray, PLUG)

	mapped_keys   = ('color1', 'color2', 'mix_map')
	mapped_params = write_sub_textures(bus,
									  TexMix,
									  [key+'_tex' for key in mapped_keys])
	
	ofile.write("\n%s %s {"%(PLUG, tex_name))
	for param in PARAMS:
		if param in mapped_keys and param+'_tex' in mapped_params:
			value= mapped_params[param+'_tex']
		else:
			value= getattr(TexMix, param)
		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))
	ofile.write("\n}\n")

	return tex_name

'''
  GUI
'''
class VRAY_TP_TexMix(ui.VRayTexturePanel, bpy.types.Panel):
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
		TexMix= getattr(tex.vray, PLUG)

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexMix, 'color1', text="First")
		col.prop_search(TexMix, 'color1_tex',
						bpy.data,    'textures',
						text= "")

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexMix, 'color2', text="Second")
		col.prop_search(TexMix, 'color2_tex',
						bpy.data,    'textures',
						text= "")

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexMix, 'mix_map', text="Mix")
		col.prop_search(TexMix, 'mix_map_tex',
						bpy.data,    'textures',
						text= "")

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexMix, 'mix_amount', text="Mix Amount")
		col.prop(TexMix, 'transition_lower', text="Transition Lower")
		col.prop(TexMix, 'transition_upper', text="Transition Upper")
		col.prop(TexMix, 'use_curve', text="Use Curve")


def GetRegClasses():
	return (
		VRAY_TP_TexMix,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
