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
ID=   'TexRock'
PLUG= 'TexRock'
NAME= 'Rock'
DESC= "TexRock."
PID=   12

PARAMS= (
	'uvwgen',
	'color1_tex',
	'color2_tex',
	'grain_size',
	'diffusion',
	'mix_ratio',
)


def add_properties(rna_pointer):
	class TexRock(bpy.types.PropertyGroup):
		# use_3d_mapping
		use_3d_mapping= BoolProperty(
			name= "use 3d mapping",
			description= "",
			default= True
		)

		# wrap
		wrap= BoolProperty(
			name= "Wrap",
			description= "",
			default= True
		)

		# color1_tex
		color1_tex= FloatVectorProperty(
			name= "First color",
			description= "First color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (1,1,1)
		)

		color1_tex_tex= StringProperty(
			name= "color1 tex",
			description= "",
			default= ""
		)

		# color2_tex
		color2_tex= FloatVectorProperty(
			name= "Second color",
			description= "Second color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0,0,0)
		)
		color2_tex_tex= StringProperty(
			name= "color2 tex",
			description= "",
			default= ""
		)

		# grain_size
		grain_size= FloatProperty(
			name= "Grain size",
			description= "",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.01
		)

		# diffusion
		diffusion= FloatProperty(
			name= "Diffusion",
			description= "",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 1
		)

		# mix_ratio
		mix_ratio= FloatProperty(
			name= "Mix ratio",
			description= "",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.5
		)

	bpy.utils.register_class(TexRock)

	rna_pointer.TexRock= PointerProperty(
		name= "TexRock",
		type=  TexRock,
		description= "V-Ray TexRock settings"
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

	TexRock= getattr(texture.vray, PLUG)

	mapped_keys= ('color1_tex', 'color2_tex')
	mapped_params= write_sub_textures(bus,
									  TexRock,
									  [key+'_tex' for key in mapped_keys])

	ofile.write("\n%s %s {"%(PLUG, tex_name))

	PLUGINS['TEXTURE']['TexCommon'].write(bus)

	for param in PARAMS:
		if param == 'uvwgen':
			value= uvwgen

		elif param in mapped_keys and param+'_tex' in mapped_params:
			value= mapped_params[param+'_tex']

		else:
			value= getattr(TexRock, param)

		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))

	ofile.write("\n}\n")

	return tex_name


'''
  GUI
'''
class VRAY_TP_TexRock(ui.VRayTexturePanel, bpy.types.Panel):
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
		TexRock= getattr(tex.vray, PLUG)

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexRock, 'color1_tex')
		col.prop_search(TexRock,  'color1_tex_tex',
						bpy.data, 'textures',
						text= "")
		if wide_ui:
			col= split.column(align= True)
		col.prop(TexRock, 'color2_tex')
		col.prop_search(TexRock,  'color2_tex_tex',
						bpy.data, 'textures',
						text= "")

		layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(TexRock, 'grain_size')
		col.prop(TexRock, 'diffusion')
		if wide_ui:
			col= split.column()
		col.prop(TexRock, 'mix_ratio')


def GetRegClasses():
	return (
		VRAY_TP_TexRock,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
