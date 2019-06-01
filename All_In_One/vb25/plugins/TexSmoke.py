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
ID=   'TexSmoke'
PLUG= 'TexSmoke'
NAME= 'Smoke'
DESC= "TexSmoke."
PID=   22

PARAMS= (
	'uvwgen',
	'color1',
	'color2',
	'size',
	'iterations',
	'phase',
	'exponent'
)




def add_properties(rna_pointer):
	class TexSmoke(bpy.types.PropertyGroup):

		# use_3d_mapping
		use_3d_mapping= BoolProperty(
			name= "use 3d mapping",
			description= "",
			default= True
		)

		#  color1: acolor texture = AColor(1, 1, 1, 1), First color
		color1 = FloatVectorProperty(
			name= "Color 1",
			description= "Color 1",
			subtype= 'COLOR',
			size=4,
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (1,1,1,1)
		)

		color1_tex= StringProperty(
			name= "Color 1 Texture",
			description= "Smoke Texture",
			default= ""
		)

		#  color2: acolor texture = AColor(0, 0, 0, 0), Second color
		color2 = FloatVectorProperty(
			name= "Color 2",
			description= "Color 2",
			subtype= 'COLOR',
			size=4,
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0,0,0,0)
		)

		color2_tex= StringProperty(
			name= "Color 2 Texture",
			description= "Color 2 Texture",
			default= ""
		)
		
		#  size: float = 1, Size
		size= FloatProperty(
			name= "Size",
			description= "Size",
			min= 0.0,
			max= 1000.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 1
		)

		#  iterations: integer = 5, Iterations
		iterations= IntProperty(
			name= "Iterations",
			description= "Iterations",
			min= 0,
			max= 100,
			default= 5
		)

		#  phase: float = 0, Phase
		phase= FloatProperty(
			name= "Phase",
			description= "Phase",
			min= 0.0,
			max= 1000.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0
		)

		#  exponent: float = 1.5, Exponent
		exponent= FloatProperty(
			name= "Exponent",
			description= "Exponent",
			min= 0.0,
			max= 1000.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 1.5
		)


	bpy.utils.register_class(TexSmoke)

	rna_pointer.TexSmoke= PointerProperty(
		name= "TexSmoke",
		type=  TexSmoke,
		description= "V-Ray TexSmoke settings"
	)


def write(bus):
	scene= bus['scene']
	ofile= bus['files']['textures']

	slot=     bus['mtex']['slot']
	texture=  bus['mtex']['texture']
	tex_name= bus['mtex']['name']

	uvwgen= write_uvwgen(bus)

	TexSmoke= getattr(texture.vray, PLUG)

	mapped_keys= ('color1', 'color2')
	mapped_params= write_sub_textures(bus,
					  TexSmoke,
					  [key+'_tex' for key in mapped_keys])
	
	ofile.write("\n%s %s {"%(PLUG, tex_name))
	for param in PARAMS:
		if param == 'uvwgen':
			value= uvwgen
		elif param in mapped_keys and param+'_tex' in mapped_params:
			value= mapped_params[param+'_tex']
		else:
			value= getattr(TexSmoke, param)
		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))
	ofile.write("\n}\n")

	return tex_name

'''
  GUI
'''
class VRAY_TP_TexSmoke(ui.VRayTexturePanel, bpy.types.Panel):
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
		TexSmoke= getattr(tex.vray, PLUG)

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexSmoke, 'color1', text="Color 1")
		col.prop_search(TexSmoke, 'color1_tex',
						bpy.data,    'textures',
						text= "")

		if wide_ui:
			col= split.column(align= True)
		col.prop(TexSmoke, 'color2', text="Color 2")
		col.prop_search(TexSmoke, 'color2_tex',
						bpy.data,    'textures',
						text= "")

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexSmoke, 'size', text="Size")
		col.prop(TexSmoke, 'iterations', text="Iterations")
		col.prop(TexSmoke, 'phase', text="Phase")
		col.prop(TexSmoke, 'exponent', text="Exponent")


#  color1: acolor texture = AColor(1, 1, 1, 1), First color
#  color2: acolor texture = AColor(0, 0, 0, 0), Second color
#  size: float = 1, Size
#  iterations: integer = 5, Iterations
#  phase: float = 0, Phase
#  exponent: float = 1.5, Exponent


def GetRegClasses():
	return (
		VRAY_TP_TexSmoke,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
