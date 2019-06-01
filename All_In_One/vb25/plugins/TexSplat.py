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
ID=   'TexSplat'
PLUG= 'TexSplat'
NAME= 'Splat'
DESC= "TexSplat."
PID=   10

PARAMS= (
	'color1',
	'color2',
	'size',
	'iterations',
	'threshold',
	'smoothing',
	'uvwgen',
)


def add_properties(rna_pointer):
	class TexSplat(bpy.types.PropertyGroup):
		# use_3d_mapping
		use_3d_mapping= BoolProperty(
			name= "use 3d mapping",
			description= "",
			default= True
		)

		# color1
		color1= FloatVectorProperty(
			name= "First color",
			description= "First color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (1,1,1)
		)

		color1_tex= StringProperty(
			name= "Color texture ",
			description= "Color texture",
			default= ""
		)

		# color2
		color2= FloatVectorProperty(
			name= "Second color",
			description= "Second color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0,0,0)
		)

		color2_tex= StringProperty(
			name= "Color texture ",
			description= "Color texture",
			default= ""
		)

		# size
		size= FloatProperty(
			name= "Size",
			description= "Size",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 1
		)

		# iterations
		iterations= IntProperty(
			name= "Iterations",
			description= "Number of iterations for the fractal generator",
			min= 0,
			max= 100,
			soft_min= 0,
			soft_max= 10,
			default= 4
		)

		# threshold
		threshold= FloatProperty(
			name= "Threshold",
			description= "Threshold",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.2
		)

		# smoothing
		smoothing= FloatProperty(
			name= "Smoothing",
			description= "Transition smoothing",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.02
		)

	bpy.utils.register_class(TexSplat)

	rna_pointer.TexSplat= PointerProperty(
		name= "TexSplat",
		type=  TexSplat,
		description= "V-Ray TexSplat settings"
	)


def write(bus):
	scene= bus['scene']
	ofile= bus['files']['textures']

	slot=     bus['mtex']['slot']
	texture=  bus['mtex']['texture']
	tex_name= bus['mtex']['name']

	uvwgen= write_uvwgen(bus)

	TexSplat= getattr(texture.vray, PLUG)

	mapped_params= write_sub_textures(bus,
									  TexSplat,
									  ('color1_tex', 'color2_tex'))

	ofile.write("\n%s %s {"%(PLUG, tex_name))

	PLUGINS['TEXTURE']['TexCommon'].write(bus)

	for param in PARAMS:
		if param == 'uvwgen':
			value= uvwgen

		elif param in ('color1','color2') and param+'_tex' in mapped_params:
			value= mapped_params[param+'_tex']

		else:
			value= getattr(TexSplat, param)

		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))

	ofile.write("\n}\n")

	return tex_name


'''
  GUI
'''
class VRAY_TP_TexSplat(ui.VRayTexturePanel, bpy.types.Panel):
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
		TexSplat= getattr(tex.vray, PLUG)

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexSplat, 'color1')
		col.prop_search(TexSplat, 'color1_tex',
						bpy.data, 'textures',
						text= "")
		if wide_ui:
			col= split.column(align= True)
		col.prop(TexSplat, 'color2')
		col.prop_search(TexSplat, 'color2_tex',
						bpy.data, 'textures',
						text= "")

		layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(TexSplat, 'size')
		col.prop(TexSplat, 'iterations')
		if wide_ui:
			col= split.column()
		col.prop(TexSplat, 'threshold')
		col.prop(TexSplat, 'smoothing')


def GetRegClasses():
	return (
		VRAY_TP_TexSplat,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
