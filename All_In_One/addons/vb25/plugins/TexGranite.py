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
ID=   'TexGranite'
PLUG= 'TexGranite'
NAME= 'Granite'
DESC= "TexGranite."
PID=   17

PARAMS= (
	'uvwgen',
	'color1_tex',
	'color2_tex',
	'color3_tex',
	'filler_color_tex',
	'cell_size',
	'density',
	'mix_ratio',
	'spottyness',
	'randomness',
	'threshold',
	'creases',
)


def add_properties(rna_pointer):
	class TexGranite(bpy.types.PropertyGroup):

		# use_3d_mapping
		use_3d_mapping= BoolProperty(
			name= "use 3d mapping",
			description= "",
			default= True
		)
		
		#  color1_tex: acolor texture
		color1_tex= FloatVectorProperty(
			name= "Color 1",
			description= "Color 1",
			size=4,
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (1,0.4,0.15,1)
		)

		color1_tex_tex= StringProperty(
			name= "Color 1 texture ",
			description= "Color 1 texture",
			default= ""
		)

		#  color2_tex: acolor texture
		color2_tex= FloatVectorProperty(
			name= "Color 2",
			description= "Color 2",
			size=4,
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0.9,0.9,0.4,1)
		)

		color2_tex_tex= StringProperty(
			name= "Color 2 texture ",
			description= "Color 2 texture",
			default= ""
		)

		#  color3_tex: acolor texture
		color3_tex= FloatVectorProperty(
			name= "Color 3",
			description= "Color 3",
			size=4,
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0.02,0.004,0.004,1)
		)

		color3_tex_tex= StringProperty(
			name= "Color 3 texture ",
			description= "Color 3 texture",
			default= ""
		)

		# filler_color_tex: acolor texture
		filler_color_tex= FloatVectorProperty(
			name= "Filter Color",
			description= "Filter Color",
			size=4,
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0.14,0.05,0.05,1)
		)

		filler_color_tex_tex= StringProperty(
			name= "Filter Color texture ",
			description= "Filter Color texture",
			default= ""
		)

		#  cell_size: float = 0.15
		cell_size= FloatProperty(
			name= "Cell Size",
			description= "Cell Size",
			min= 0.0,
			max= 1000.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.15
		)

		# density: float = 1
		density= FloatProperty(
			name= "Density",
			description= "Density",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 1
		)

		#  mix_ratio: float = 0.5
		mix_ratio= FloatProperty(
			name= "Mix Ratio",
			description= "Mix Ratio",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.5
		)

		#  spottyness: float = 0.3
		spottyness= FloatProperty(
			name= "Spottyness",
			description= "Spottyness",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.3
		)

		#  randomness: float = 1
		randomness= FloatProperty(
			name= "Randomness",
			description= "Randomness",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 1
		)

		#  threshold: float = 0.5
		threshold= FloatProperty(
			name= "Threshold",
			description= "Threshold",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.5
		)

		#  creases: bool = true
		creases = BoolProperty(
			name= "Creases",
			description= "Creases",
			default= True
		)


	bpy.utils.register_class(TexGranite)

	rna_pointer.TexGranite= PointerProperty(
		name= "TexGranite",
		type=  TexGranite,
		description= "V-Ray TexGranite settings"
	)


def write(bus):
	scene= bus['scene']
	ofile= bus['files']['textures']

	slot=     bus['mtex']['slot']
	texture=  bus['mtex']['texture']
	tex_name= bus['mtex']['name']

	uvwgen= write_uvwgen(bus)

	TexGranite= getattr(texture.vray, PLUG)

	mapped_params= write_sub_textures(bus,
									  TexGranite,
									  ('color1_tex_tex', 'color2_tex_tex', 'color3_tex_tex', 'filler_color_tex_tex'))
	
	ofile.write("\n%s %s {"%(PLUG, tex_name))
	for param in PARAMS:
		if param == 'uvwgen':
			value= uvwgen

		elif param in ('color1_tex','color2_tex','color3_tex', 'filler_color_tex') and param+'_tex' in mapped_params:
			value= mapped_params[param+'_tex']
		else:
			value= getattr(TexGranite, param)
		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))
	ofile.write("\n}\n")

	return tex_name


'''
  GUI
'''
class VRAY_TP_TexGranite(ui.VRayTexturePanel, bpy.types.Panel):
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
		TexGranite= getattr(tex.vray, PLUG)

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexGranite, 'color1_tex')
		col.prop_search(TexGranite, 'color1_tex_tex',
						bpy.data, 'textures',
						text= "")
		if wide_ui:
			col= split.column(align= True)
		col.prop(TexGranite, 'color2_tex')
		col.prop_search(TexGranite, 'color2_tex_tex',
						bpy.data, 'textures',
						text= "")

		if wide_ui:
			col= split.column(align= True)
		col.prop(TexGranite, 'color3_tex')
		col.prop_search(TexGranite, 'color3_tex_tex',
						bpy.data, 'textures',
						text= "")

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexGranite, 'filler_color_tex')
		col.prop_search(TexGranite, 'filler_color_tex_tex',
						bpy.data, 'textures',
						text= "")
		
		split= layout.split()
		col= split.column()
		col.prop(TexGranite, 'cell_size')
		if wide_ui:
			col= split.column()
		col.prop(TexGranite, 'density')

		split= layout.split()
		col= split.column()
		col.prop(TexGranite, 'mix_ratio')
		col.prop(TexGranite, 'spottyness')
		col.prop(TexGranite, 'randomness')
		col.prop(TexGranite, 'threshold')
		col.prop(TexGranite, 'creases')


def GetRegClasses():
	return (
		VRAY_TP_TexGranite,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
