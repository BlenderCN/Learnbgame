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
ID=   'TexLeather'
PLUG= 'TexLeather'
NAME= 'Leather'
DESC= "TexLeather."
PID=   23

PARAMS= (
	'uvwgen',
	'cell_color',
	'cell_color_tex',
	'cell_color_tex_mult',
	'creases',
	'crease_color',
	'crease_color_tex',
	'size',
	'density',
	'spottyness',
	'randomness',
	'threshold',
)




def add_properties(rna_pointer):
	class TexLeather(bpy.types.PropertyGroup):

		# use_3d_mapping
		use_3d_mapping= BoolProperty(
			name= "use 3d mapping",
			description= "",
			default= True
		)

		#  cell_color: color = Color(1, 1, 1)
		cell_color = FloatVectorProperty(
			name= "Cell Color",
			description= "Cell Color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (1,1,1)
		)

		#  cell_color_tex: acolor texture
		cell_color_tex = FloatVectorProperty(
			name= "Cell Color",
			description= "Cell Color",
			subtype= 'COLOR',
			size=4,
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0,0,0,1)
		)

		cell_color_tex_tex= StringProperty(
			name= "Cell Texture",
			description= "Cell Color Texture",
			default= ""
		)

		#  cell_color_tex_mult: float = 1
		cell_color_tex_mult= FloatProperty(
			name= "Cell color texture mult",
			description= "Cell color texture mult",
			min= 0.0,
			max= 1000.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 1
		)

		#  creases: bool = true
		creases= BoolProperty(
			name= "Creases",
			description= "",
			default= True
		)

		#  crease_color: color = Color(0, 0, 0)
		crease_color = FloatVectorProperty(
			name= "Creases Color",
			description= "Creases Color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0,0,0)
		)

		#  crease_color_tex: acolor texture
		crease_color_tex = FloatVectorProperty(
			name= "Creases Color",
			description= "Creases Color",
			subtype= 'COLOR',
			size=4,
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0,0,0,1)
		)

		crease_color_tex_tex= StringProperty(
			name= "Crease Color Texture",
			description= "Crease Color Texture",
			default= ""
		)
		
		#  crease_color_tex_mult: float = 1
		crease_color_tex_mult= FloatProperty(
			name= "Crease Color Texture mult",
			description= "Crease Color Texture mult",
			min= 0.0,
			max= 1000.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 1
		)

		#  size: float = 0.5
		size= FloatProperty(
			name= "Size",
			description= "Size",
			min= 0.0,
			max= 1000.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.5
		)

		#  density: float = 1
		density= FloatProperty(
			name= "Density",
			description= "Density",
			min= 0.0,
			max= 1000.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 1
		)

		#  spottyness: float = 0.1
		spottyness= FloatProperty(
			name= "Spottyness",
			description= "Spottyness",
			min= 0.0,
			max= 1000.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.1
		)

		#  randomness: float = 0.5
		randomness= FloatProperty(
			name= "Randomness",
			description= "Randomness",
			min= 0.0,
			max= 1000.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.5
		)

		#  threshold: float = 0.83
		threshold= FloatProperty(
			name= "Threshold",
			description= "Threshold",
			min= 0.0,
			max= 1000.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.83
		)


	bpy.utils.register_class(TexLeather)

	rna_pointer.TexLeather= PointerProperty(
		name= "TexLeather",
		type=  TexLeather,
		description= "V-Ray TexLeather settings"
	)


def write(bus):
	scene= bus['scene']
	ofile= bus['files']['textures']

	slot=     bus['mtex']['slot']
	texture=  bus['mtex']['texture']
	tex_name= bus['mtex']['name']

	uvwgen= write_uvwgen(bus)

	TexLeather= getattr(texture.vray, PLUG)

	mapped_keys= ('cell_color_tex', 'crease_color_tex')
	mapped_params= write_sub_textures(bus,
					  TexLeather,
					  [key+'_tex' for key in mapped_keys])
	
	ofile.write("\n%s %s {"%(PLUG, tex_name))
	for param in PARAMS:
		if param == 'uvwgen':
			value= uvwgen
		elif param in mapped_keys and param+'_tex' in mapped_params:
			value= mapped_params[param+'_tex']
		else:
			value= getattr(TexLeather, param)
		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))
	ofile.write("\n}\n")

	return tex_name

'''
  GUI
'''
class VRAY_TP_TexLeather(ui.VRayTexturePanel, bpy.types.Panel):
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
		TexLeather= getattr(tex.vray, PLUG)

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexLeather, 'cell_color', text="Cell Color")
		col.prop(TexLeather, 'cell_color_tex', text="Cell Color")
		col.prop_search(TexLeather, 'cell_color_tex_tex',
						bpy.data,    'textures',
						text= "")
		if TexLeather.cell_color_tex:
			col.prop(TexLeather, 'cell_color_tex_mult')

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexLeather, 'creases')

		split= layout.split()
		col= split.column(align= True)

		if TexLeather.creases:
#			if wide_ui:
#			col= split.column(align= True)
			col.prop(TexLeather, 'crease_color', text="Crease Color")
			col.prop(TexLeather, 'crease_color_tex', text="Crease Color")
			col.prop_search(TexLeather, 'crease_color_tex_tex',
							bpy.data,    'textures',
							text= "")
			if TexLeather.crease_color_tex:
				col.prop(TexLeather, 'crease_color_tex_mult')

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexLeather, 'size', text="Size")
		col.prop(TexLeather, 'density', text="Density")
		col.prop(TexLeather, 'spottyness', text="Spottyness")
		col.prop(TexLeather, 'randomness', text="Randomness")
		col.prop(TexLeather, 'threshold', text="Threshold")
		

#  cell_color: color = Color(1, 1, 1)
#  cell_color_tex: acolor texture
#  cell_color_tex_mult: float = 1

#  creases: bool = true
#  crease_color: color = Color(0, 0, 0)
#  crease_color_tex: acolor texture
#  crease_color_tex_mult: float = 1



#  size: float = 0.5
#  density: float = 1
#  spottyness: float = 0.1
#  randomness: float = 0.5
#  threshold: float = 0.83


def GetRegClasses():
	return (
		VRAY_TP_TexLeather,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
