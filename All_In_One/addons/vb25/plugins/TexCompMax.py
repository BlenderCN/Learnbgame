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
ID=   'TexCompMax'
PLUG= 'TexCompMax'
NAME= 'Comp Max'
DESC= "Comp Max."
PID=   32

PARAMS= (
	'sourceA',
	'sourceB',
	'operator',
)


def add_properties(rna_pointer):
	class TexCompMax(bpy.types.PropertyGroup):

		#  sourceA: acolor texture, Left hand side texture.
		sourceA = FloatVectorProperty(
			name        = "Source A",
			description = "Left hand side texture",
			subtype     = 'COLOR',
			size        = 4,
			min         = 0.0,
			max         = 1.0,
			soft_min    = 0.0,
			soft_max    = 1.0,
			default     = (1,1,1,1)
		)

		sourceA_tex = StringProperty(
			name        = "Source A Texture",
			description = "Source A Texture",
			default     = ""
		)

		#  sourceB: acolor texture, Right hand side texture.
		sourceB = FloatVectorProperty(
			name        = "Source B",
			description = "Right hand side texture",
			subtype     = 'COLOR',
			size        = 4,
			min         = 0.0,
			max         = 1.0,
			soft_min    = 0.0,
			soft_max    = 1.0,
			default     = (1, 1, 1, 1)
		)

		sourceB_tex = StringProperty(
			name        = "Source B Texture",
			description = "Source B Texture",
			default     = ""
		)
		
		#  operator: integer = 0, 0:Add, 1:Subtract, 2:Difference, 3:Multiply, 4:Divide, 5:Minimum, 6:Maximum
		operator = EnumProperty(
			name        = "Operator",
			description = "Operator",
			items       = (
						  ('ADD',   "Add",        ""), 
						  ('SUB',   "Subtract",   ""),
						  ('DIFF',  "Difference", ""),
						  ('MULT',  "Multiply",   ""),
						  ('DIV',   "Divide",     ""),
						  ('MIN',   "Minimum",    ""),
						  ('MAX',   "Maximum",    ""),
			),
			default = 'ADD'
		)		

		

	bpy.utils.register_class(TexCompMax)

	rna_pointer.TexCompMax= PointerProperty(
		name        = "TexCompMax",
		type        =  TexCompMax,
		description = "V-Ray TexCompMax settings"
	)


def write(bus):

	OPERATOR = {
		'ADD':  0,
		'SUB':  1,
		'DIFF': 2,
		'MULT': 3,
		'DIV':  4,
		'MIN':  5,
		'MAX':  6,
	}


	scene = bus['scene']
	ofile = bus['files']['textures']

	slot     = bus['mtex']['slot']
	texture  = bus['mtex']['texture']
	tex_name = bus['mtex']['name']

	TexCompMax= getattr(texture.vray, PLUG)

	mapped_keys= ('sourceA', 'sourceB')
	mapped_params= write_sub_textures(bus,
					  TexCompMax,
					  [key+'_tex' for key in mapped_keys])
	
	ofile.write("\n%s %s {"%(PLUG, tex_name))
	for param in PARAMS:
		if param == 'operator':
			value=OPERATOR[TexCompMax.operator]
		elif param in mapped_keys and param+'_tex' in mapped_params:
			value= mapped_params[param+'_tex']
		else:
			value= getattr(TexCompMax, param)
		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))
	ofile.write("\n}\n")

	return tex_name

'''
  GUI
'''
class VRAY_TP_TexCompMax(ui.VRayTexturePanel, bpy.types.Panel):
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
		TexCompMax= getattr(tex.vray, PLUG)

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexCompMax, 'sourceA', text="Source A")
		col.prop_search(TexCompMax, 'sourceA_tex',
						bpy.data,    'textures',
						text= "")

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexCompMax, 'sourceB', text="Source B")
		col.prop_search(TexCompMax, 'sourceB_tex',
						bpy.data,   'textures',
						text= "")

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexCompMax, 'operator', text="Operator")


def GetRegClasses():
	return (
		VRAY_TP_TexCompMax,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
