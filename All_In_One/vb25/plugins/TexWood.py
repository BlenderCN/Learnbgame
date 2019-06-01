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
ID=   'TexWood'
PLUG= 'TexWood'
NAME= 'Wood'
DESC= "TexWood."
PID=   11

PARAMS= (
	'uvwgen',
	'filler_color_tex',
	'vein_color_tex',
	'vein_spread',
	'layer_size',
	'randomness',
	'age',
	'grain_color_tex',
	'grain_contr',
	'grain_spacing',
	'center_u',
	'center_v',
	'amplitude_x',
	'amplitude_y',
	'ratio',
	'ripples_x',
	'ripples_y',
	'ripples_z',
	'depth_min',
	'depth_max',
)


def add_properties(rna_pointer):
	class TexWood(bpy.types.PropertyGroup):
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

		# filler_color_tex
		filler_color_tex= FloatVectorProperty(
			name= "Filler color",
			description= "Filler color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0.564694, 0.488278, 0.304942)
		)
		filler_color_tex_tex= StringProperty(
			name= "Filler texture",
			description= "Filler texture",
			default= ""
		)

		# vein_color_tex
		vein_color_tex= FloatVectorProperty(
			name= "Vein color",
			description= "Vein color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0.123518, 0.071829, 0.043644)
		)
		vein_color_tex_tex= StringProperty(
			name= "Vein texture",
			description= "Vein texture",
			default= ""
		)


		# vein_spread
		vein_spread= FloatProperty(
			name= "Vein spread",
			description= "Vein spread",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.25
		)

		# layer_size
		layer_size= FloatProperty(
			name= "Layer size",
			description= "Layer size",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.05
		)

		# randomness
		randomness= FloatProperty(
			name= "Randomness",
			description= "Randomness",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.5
		)

		# age
		age= FloatProperty(
			name= "Age",
			description= "Age",
			min= 0.0,
			max= 10000.0,
			soft_min= 0.0,
			soft_max= 100.0,
			precision= 3,
			default= 20
		)

		# grain_color_tex
		grain_color_tex= FloatVectorProperty(
			name= "Grain color",
			description= "Grain color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0.035282, 0.020518, 0.012467)
		)
		grain_color_tex_tex= StringProperty(
			name= "Grain texture",
			description= "Grain texture",
			default= ""
		)


		# grain_contr
		grain_contr= FloatProperty(
			name= "Grain contribution",
			description= "Grain contribution",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.5
		)

		# grain_spacing
		grain_spacing= FloatProperty(
			name= "Grain spacing",
			description= "Grain spacing",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.01
		)

		# center_u
		center_u= FloatProperty(
			name= "Center U",
			description= "Center U",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.5
		)

		# center_v
		center_v= FloatProperty(
			name= "Center V",
			description= "Center V",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= -0.5
		)

		# amplitude_x
		amplitude_x= FloatProperty(
			name= "Amplitude X",
			description= "Amplitude X",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0
		)

		# amplitude_y
		amplitude_y= FloatProperty(
			name= "Amplitude Y",
			description= "Amplitude Y",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0
		)

		# ratio
		ratio= FloatProperty(
			name= "Ratio",
			description= "Ratio",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.35
		)

		# ripples_x
		ripples_x= FloatProperty(
			name= "Ripples X",
			description= "Ripples X",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 1
		)

		# ripples_y
		ripples_y= FloatProperty(
			name= "Ripples Y",
			description= "Ripples Y",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 1
		)

		# ripples_z
		ripples_z= FloatProperty(
			name= "Ripples Z",
			description= "Ripples Z",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 1
		)

		# depth_min
		depth_min= FloatProperty(
			name= "Depth min",
			description= "",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0
		)

		# depth_max
		depth_max= FloatProperty(
			name= "Depth max",
			description= "",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 8
		)

	bpy.utils.register_class(TexWood)

	rna_pointer.TexWood= PointerProperty(
		name= "TexWood",
		type=  TexWood,
		description= "V-Ray TexWood settings"
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

	TexWood= getattr(texture.vray, PLUG)

	mapped_keys= ('filler_color_tex', 'vein_color_tex', 'grain_color_tex')
	mapped_params= write_sub_textures(bus,
									  TexWood,
									  [key+'_tex' for key in mapped_keys])

	ofile.write("\n%s %s {"%(PLUG, tex_name))

	PLUGINS['TEXTURE']['TexCommon'].write(bus)

	for param in PARAMS:
		if param == 'uvwgen':
			value= uvwgen

		elif param in mapped_keys and param+'_tex' in mapped_params:
			value= mapped_params[param+'_tex']

		else:
			value= getattr(TexWood, param)

		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))

	ofile.write("\n}\n")

	return tex_name


'''
  GUI
'''
class VRAY_TP_TexWood(ui.VRayTexturePanel, bpy.types.Panel):
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
		TexWood= getattr(tex.vray, PLUG)

		layout.label(text="Colors:")

		split= layout.split()
		row= split.row(align= True)
		row.prop(TexWood, 'filler_color_tex', text="")
		row.prop(TexWood, 'vein_color_tex', text="")
		row.prop(TexWood, 'grain_color_tex', text="")

		layout.label(text="Textures:")

		split= layout.split()
		row= split.row(align= True)
		row.prop_search(TexWood,  'filler_color_tex_tex',
						bpy.data, 'textures',
						text= "")
		row.prop_search(TexWood,  'vein_color_tex_tex',
						bpy.data, 'textures',
						text= "")
		row.prop_search(TexWood,  'grain_color_tex_tex',
						bpy.data, 'textures',
						text= "")

		layout.separator()

		layout.label(text="Ripples:")

		split= layout.split()
		row= split.row(align= True)
		row.prop(TexWood, 'ripples_x', text="X")
		row.prop(TexWood, 'ripples_y', text="Y")
		row.prop(TexWood, 'ripples_z', text="Z")

		layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(TexWood, 'age')
		col.prop(TexWood, 'vein_spread')
		if wide_ui:
			col= split.column()
		col.prop(TexWood, 'grain_contr')
		col.prop(TexWood, 'grain_spacing')

		split= layout.split()
		col= split.column()
		sub= col.column(align= True)
		sub.prop(TexWood, 'center_u')
		sub.prop(TexWood, 'center_v')
		if wide_ui:
			col= split.column()
		sub= col.column(align= True)
		sub.prop(TexWood, 'amplitude_x')
		sub.prop(TexWood, 'amplitude_y')

		split= layout.split()
		col= split.column()
		col.prop(TexWood, 'layer_size')
		col.prop(TexWood, 'ratio')
		if wide_ui:
			col= split.column()
		sub= col.column(align= True)
		sub.prop(TexWood, 'depth_min')
		sub.prop(TexWood, 'depth_max')

		split= layout.split()
		col= split.column()
		col.prop(TexWood, 'randomness')


def GetRegClasses():
	return (
		VRAY_TP_TexWood,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
