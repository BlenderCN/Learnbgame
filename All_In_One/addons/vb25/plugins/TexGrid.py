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
ID=   'TexGrid'
PLUG= 'TexGrid'
NAME= 'Grid'
DESC= "TexGrid."
PID=   19

PARAMS= (
	'uvwgen',
	'line_color',
	'fill_color',
	'u_width',
	'v_width'
)

def add_properties(rna_pointer):
	class TexGrid(bpy.types.PropertyGroup):

		# use_3d_mapping
		use_3d_mapping= BoolProperty(
			name= "use 3d mapping",
			description= "",
			default= True
		)

		#  line_color: acolor texture
		line_color = FloatVectorProperty(
			name= "Line Color",
			description= "Line Color",
			subtype= 'COLOR',
			size=4,
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0,0,0,1)
		)

		line_color_tex= StringProperty(
			name= "Line Color Texture",
			description= "Line Color Texture",
			default= ""
		)

		#  fill_color: acolor texture
		fill_color = FloatVectorProperty(
			name= "Fill Color",
			description= "Fill Color",
			subtype= 'COLOR',
			size=4,
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (1,1,1,1)
		)

		fill_color_tex= StringProperty(
			name= "Fill Color Texture",
			description= "Fill Color Texture",
			default= ""
		)
		
		#  u_width: float = 0.1
		u_width= FloatProperty(
			name= "U width",
			description= "U width",
			min= 0.0,
			max= 1000.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.1
		)

		#  v_width: float = 0.1
		v_width= FloatProperty(
			name= "V width",
			description= "V width",
			min= 0.0,
			max= 1000.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.1
		)
		

	bpy.utils.register_class(TexGrid)

	rna_pointer.TexGrid= PointerProperty(
		name= "TexGrid",
		type=  TexGrid,
		description= "V-Ray TexGrid settings"
	)


def write(bus):
	scene= bus['scene']
	ofile= bus['files']['textures']

	slot=     bus['mtex']['slot']
	texture=  bus['mtex']['texture']
	tex_name= bus['mtex']['name']

	uvwgen= write_uvwgen(bus)

	TexGrid= getattr(texture.vray, PLUG)

	mapped_keys= ('line_color', 'fill_color')
	mapped_params= write_sub_textures(bus,
					  TexGrid,
					  [key+'_tex' for key in mapped_keys])
	
	ofile.write("\n%s %s {"%(PLUG, tex_name))
	for param in PARAMS:
		if param == 'uvwgen':
			value= uvwgen
		elif param in mapped_keys and param+'_tex' in mapped_params:
			value= mapped_params[param+'_tex']
		else:
			value= getattr(TexGrid, param)
		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))
	ofile.write("\n}\n")

	return tex_name


'''
  GUI
'''
class VRAY_TP_TexGrid(ui.VRayTexturePanel, bpy.types.Panel):
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
		TexGrid= getattr(tex.vray, PLUG)

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexGrid, 'line_color', text="Line Color")
		col.prop_search(TexGrid, 'line_color_tex',
						bpy.data,    'textures',
						text= "")

		if wide_ui:
			col= split.column(align= True)
		col.prop(TexGrid, 'fill_color', text="Fill Color")
		col.prop_search(TexGrid, 'fill_color_tex',
						bpy.data,    'textures',
						text= "")

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexGrid, 'u_width')
		col.prop(TexGrid, 'v_width')


def GetRegClasses():
	return (
		VRAY_TP_TexGrid,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
