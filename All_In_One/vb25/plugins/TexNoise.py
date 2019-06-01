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

ID=   'TexNoiseMax'
NAME= 'Noise'
PLUG= 'TexNoiseMax'
DESC= "3ds max like noise texture."
PID=  5

PARAMS= (
	'color1',
	'color2',
	'size',
	'phase',
	'iterations',
	'low',
	'high',
	'type',
	'uvwgen',
)


def add_properties(rna_pointer):
	class TexNoiseMax(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(TexNoiseMax)

	rna_pointer.TexNoiseMax= PointerProperty(
		name= "TexNoiseMax",
		type=  TexNoiseMax,
		description= "V-Ray TexNoiseMax settings"
	)

	# use_3d_mapping
	TexNoiseMax.use_3d_mapping= BoolProperty(
		name= "use 3d mapping",
		description= "",
		default= True
	)

	# color1
	TexNoiseMax.color1= FloatVectorProperty(
		name= "Color 1",
		description= "First color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (1,1,1)
	)

	TexNoiseMax.color1_tex= StringProperty(
		name= "Color 1 texture",
		description= "Color 1 texture",
		default= ""
	)

	# color2
	TexNoiseMax.color2= FloatVectorProperty(
		name= "Color 2",
		description= "Second color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0,0,0)
	)

	TexNoiseMax.color2_tex= StringProperty(
		name= "Color 2 texture",
		description= "Color 2 texture",
		default= ""
	)


	# size
	TexNoiseMax.size= FloatProperty(
		name= "Size",
		description= "Size",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	# phase
	TexNoiseMax.phase= FloatProperty(
		name= "Phase",
		description= "Phase",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0
	)

	# iterations
	TexNoiseMax.iterations= FloatProperty(
		name= "Iterations",
		description= "Number of iterations for the fractal generator",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 3
	)

	# low
	TexNoiseMax.low= FloatProperty(
		name= "Low",
		description= "Low threshold",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0
	)

	# high
	TexNoiseMax.high= FloatProperty(
		name= "High",
		description= "High threshold",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	# type
	TexNoiseMax.type= EnumProperty(
		name= "Type",
		description= "Noise type",
		items= (
			('REGULAR',    "Regular",    ""), # 0
			('FRACTAL',    "Fractal",    ""),
			('TRUBULENCE', "Turbulence", ""),
		),
		default= 'REGULAR'
	)


def write(bus):
	TYPE= {
		'REGULAR':    0,
		'FRACTAL':    1,
		'TRUBULENCE': 2,
	}
	PLACEMENT_TYPE= {
		'FULL':  0,
		'CROP':  1,
		'PLACE': 2,
	}

	scene= bus['scene']
	ofile= bus['files']['textures']

	slot=     bus['mtex']['slot']
	texture=  bus['mtex']['texture']
	tex_name= bus['mtex']['name']

	uvwgen= write_uvwgen(bus)

	TexNoiseMax= getattr(texture.vray, PLUG)

	mapped_keys= ('color1', 'color2')
	mapped_params= write_sub_textures(bus,
									  TexNoiseMax,
									  [key+'_tex' for key in mapped_keys])

	ofile.write("\n%s %s {"%(PLUG, tex_name))

	PLUGINS['TEXTURE']['TexCommon'].write(bus)

	for param in PARAMS:
		if param == 'type':
			value= TYPE[TexNoiseMax.type]

		elif param == 'placement_type':
			value= PLACEMENT_TYPE[TexNoiseMax.placement_type]

		elif param == 'uvwgen':
			value= uvwgen

		elif param in mapped_keys and param+'_tex' in mapped_params:
			value= mapped_params[param+'_tex']

		else:
			value= getattr(TexNoiseMax, param)
		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))

	ofile.write("\n}\n")

	return tex_name


'''
  GUI
'''
class VRAY_TP_TexNoiseMax(ui.VRayTexturePanel, bpy.types.Panel):
	bl_label       = NAME
	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		tex= context.texture
		if not tex:
			return False
		engine= context.scene.render.engine
		return ((tex and tex.type == 'VRAY' and tex.vray.type == ID) and (ui.engine_poll(__class__, context)))

	def draw(self, context):
		wide_ui= context.region.width > ui.narrowui
		layout= self.layout

		tex= context.texture
		TexNoiseMax= getattr(tex.vray, PLUG)

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexNoiseMax, 'color1')
		col.prop_search(TexNoiseMax, 'color1_tex',
						bpy.data,    'textures',
						text= "")
		if wide_ui:
			col= split.column(align= True)
		col.prop(TexNoiseMax, 'color2')
		col.prop_search(TexNoiseMax, 'color2_tex',
						bpy.data,    'textures',
						text= "")

		split= layout.split()
		col= split.column()
		col.prop(TexNoiseMax, 'type')
		col.prop(TexNoiseMax, 'size')
		col.prop(TexNoiseMax, 'iterations')
		if wide_ui:
			col= split.column()
		col.prop(TexNoiseMax, 'low')
		col.prop(TexNoiseMax, 'high')
		col.prop(TexNoiseMax, 'phase')


def GetRegClasses():
	return (
		VRAY_TP_TexNoiseMax,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
