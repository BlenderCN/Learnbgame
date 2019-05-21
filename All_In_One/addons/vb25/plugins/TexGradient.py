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
ID=   'TexGradient'
PLUG= 'TexGradient'
NAME= 'Gradient'
DESC= "TexGradient."
PID=   7

PARAMS= (
	'color1',
	'color2',
	'color3',
	'has_textures',
	'middle',
	'type',
	'noise_amount',
	'noise_size',
	'noise_type',
	'noise_iterations',
	'noise_phase',
	'noise_low',
	'noise_high',
	'noise_smooth',
	'uvwgen',
)


def add_properties(rna_pointer):
	class TexGradient(bpy.types.PropertyGroup):
		# color1
		color1= FloatVectorProperty(
			name= "color1",
			description= "First color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0,0,0)
		)

		color1_tex= StringProperty(
			name= "First color texture",
			description= "First color texture",
			default= ""
		)

		# color2
		color2= FloatVectorProperty(
			name= "color2",
			description= "Middle color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0.5,0.5,0.5)
		)

		color2_tex= StringProperty(
			name= "Second color texture",
			description= "Second color texture",
			default= ""
		)

		# color3
		color3= FloatVectorProperty(
			name= "color3",
			description= "End color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (1,1,1)
		)

		color3_tex= StringProperty(
			name= "Third color texture",
			description= "Third color texture",
			default= ""
		)

		# has_textures
		has_textures= BoolProperty(
			name= "has textures",
			description= "This affects bump mapping, following a peculiarity in the 3ds Max implementation",
			default= False
		)

		# middle
		middle= FloatProperty(
			name= "Middle position",
			description= "Middle color position",
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			precision= 3,
			default= 0.5
		)

		# type
		type= EnumProperty(
			name= "Type",
			description= "Gradient type",
			items= (
				('LINEAR', "Linear", "Linear."),
				('RADIAL', "Radial", "Radial."),
			),
			default= 'LINEAR'
		)

		# noise_amount
		noise_amount= FloatProperty(
			name= "Amount",
			description= "Noise amount",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0
		)

		# noise_size
		noise_size= FloatProperty(
			name= "Size",
			description= "Noise size",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 1
		)

		# noise_type
		noise_type= EnumProperty(
			name= "Type",
			description= "Noise type",
			items= (
				('REGULAR',    "Regular",    ""), # 0
				('FRACTAL',    "Fractal",    ""),
				('TRUBULENCE', "Turbulence", ""),
			),
			default= 'REGULAR'
		)

		# noise_iterations
		noise_iterations= FloatProperty(
			name= "Iterations",
			description= "Noise iterations",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 4
		)

		# noise_phase
		noise_phase= FloatProperty(
			name= "Phase",
			description= "Noise phase",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0
		)

		# noise_low
		noise_low= FloatProperty(
			name= "Low",
			description= "Noise low threshold",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0
		)

		# noise_high
		noise_high= FloatProperty(
			name= "High",
			description= "Noise high threshold",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 1
		)

		# noise_smooth
		noise_smooth= FloatProperty(
			name= "Smooth",
			description= "Threshold smoothing",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0
		)

	bpy.utils.register_class(TexGradient)

	rna_pointer.TexGradient= PointerProperty(
		name= "TexGradient",
		type=  TexGradient,
		description= "V-Ray TexGradient settings"
	)


def write(bus):
	TYPE= {
		'LINEAR': 0,
		'RADIAL': 1,
	}

	scene= bus['scene']
	ofile= bus['files']['textures']

	slot=     bus['mtex']['slot']
	texture=  bus['mtex']['texture']
	tex_name= bus['mtex']['name']

	uvwgen= write_uvwgen(bus)

	TexGradient= getattr(texture.vray, PLUG)

	mapped_keys= ('color1', 'color2', 'color3')
	mapped_params= write_sub_textures(bus,
									  TexGradient,
									  [key+'_tex' for key in mapped_keys])

	ofile.write("\n%s %s {"%(PLUG, tex_name))

	PLUGINS['TEXTURE']['TexCommon'].write(bus)

	for param in PARAMS:
		if param == 'uvwgen':
			value= uvwgen

		elif param in mapped_keys and param+'_tex' in mapped_params:
			value= mapped_params[param+'_tex']

		elif param == 'type':
			value= TYPE[TexGradient.type]

		else:
			value= getattr(TexGradient, param)

		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))
	ofile.write("\n}\n")

	return tex_name


'''
  GUI
'''
class VRAY_TP_TexGradient(ui.VRayTexturePanel, bpy.types.Panel):
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
		TexGradient= getattr(tex.vray, PLUG)

		layout.prop(TexGradient, 'type', expand= True)

		layout.label(text="Colors:")

		split= layout.split()
		row= split.row(align= True)
		row.prop(TexGradient, 'color1', text="")
		row.prop(TexGradient, 'color2', text="")
		row.prop(TexGradient, 'color3', text="")

		layout.label(text="Textures:")

		split= layout.split()
		row= split.row(align= True)
		row.prop_search(TexGradient, 'color1_tex',
						bpy.data,    'textures',
						text= "")
		row.prop_search(TexGradient, 'color2_tex',
						bpy.data,    'textures',
						text= "")
		row.prop_search(TexGradient, 'color3_tex',
						bpy.data,    'textures',
						text= "")

		layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(TexGradient, 'middle')

		layout.separator()

		box= layout.box()

		split= box.split()
		row= split.row(align= True)
		row.label(text="Noise:")
		row.prop(TexGradient, 'noise_amount')

		split= box.split()
		split.active= TexGradient.noise_amount > 0.0
		col= split.column()
		col.prop(TexGradient, 'noise_type')
		col.prop(TexGradient, 'noise_size')
		if wide_ui:
			col= split.column()
		col.prop(TexGradient, 'noise_iterations')
		col.prop(TexGradient, 'noise_phase')

		split= box.split()
		split.active= TexGradient.noise_amount > 0.0
		row= split.row(align= True)
		row.prop(TexGradient, 'noise_low')
		row.prop(TexGradient, 'noise_high')
		row.prop(TexGradient, 'noise_smooth')

		# col.prop(TexGradient, 'has_textures')


def GetRegClasses():
	return (
		VRAY_TP_TexGradient,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
