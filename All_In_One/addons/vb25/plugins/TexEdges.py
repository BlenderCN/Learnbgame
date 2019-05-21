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

ID=	  'TexEdges'
NAME= 'Edge'
PLUG= 'TexEdges'
DESC= "Wire frame texture."
PID=   4

PARAMS= (
	'edges_tex',		 # acolor texture = AColor(1, 1, 1, 1)
	'bg_tex',			 # acolor texture = AColor(0, 0, 0, 1)
	'show_hidden_edges', # bool = false
	'width_type',		 # integer = 0, 0: World units, 1: Pixels
	# 'world_width',	 # float = 1
	# 'pixel_width',	 # float = 1
)


def add_properties(VRayTexture):
	class TexEdges(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(TexEdges)
	
	VRayTexture.TexEdges= PointerProperty(
		name= "TexEdges",
		type=  TexEdges,
		description= "V-Ray TexEdges settings"
	)

	TexEdges.edges_tex= FloatVectorProperty(
		name= "Edges color",
		description= "Edges color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (1,1,1)
	)

	TexEdges.edges_tex_tex= StringProperty(
		name= "Edges texture",
		description= "Edges texture",
		default= ""
	)

	TexEdges.bg_tex= FloatVectorProperty(
		name= "Background color",
		description= "Background color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0,0,0)
	)

	TexEdges.bg_tex_tex= StringProperty(
		name= "Background texture",
		description= "Background texture",
		default= ""
	)

	TexEdges.show_hidden_edges= BoolProperty(
		name= "Show hidden edges",
		description= "Show hidden edges",
		default= False
	)
	
	TexEdges.width_type= EnumProperty(
		name= "Width type",
		description= "Width type: world units or pixels",
		items= (
			('WORLD', "World", ""),
			('PIXEL', "Pixel", "")
		),
		default= 'PIXEL'
	)

	TexEdges.width= FloatProperty(
		name= "Width",
		description= "Edge width",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 5,
		default= 1.0
	)


def write(bus):
	WIDTH_TYPE= {
		'PIXEL' : 1,
		'WORLD' : 0
	}

	scene= bus['scene']
	ofile= bus['files']['textures']

	slot=     bus['mtex']['slot']
	texture=  bus['mtex']['texture']
	tex_name= bus['mtex']['name']

	write_uvwgen(bus)

	TexEdges= getattr(texture.vray, PLUG)

	uvwgen= write_uvwgen(bus)

	mapped_params= write_sub_textures(bus,
									  TexEdges,
									  ('edges_tex_tex', 'bg_tex_tex'))

	# Write output
	ofile.write("\n%s %s {" % (PLUG, tex_name))
	for param in PARAMS:
		if param == 'width_type':
			ofile.write("\n\t%s= %s;"%(param, WIDTH_TYPE[TexEdges.width_type]))
			if TexEdges.width_type == 'PIXEL':
				_param= 'pixel_width'
			else:
				_param= 'world_width'
			ofile.write("\n\t%s= %s;"%(_param, a(scene, getattr(TexEdges, 'width'))))

		elif param in ('edges_tex', 'bg_tex'):
			tex_key= param+'_tex'
			if tex_key in mapped_params:
				value= mapped_params[tex_key]
			else:
				value= getattr(TexEdges, param)
			ofile.write("\n\t%s= %s;" % (param, a(scene, value)))

		else:
			ofile.write("\n\t%s= %s;"%(param, a(scene, getattr(TexEdges, param))))
	ofile.write("\n}\n")

	return tex_name



'''
  GUI
'''
class VRAY_TP_TexEdges(ui.VRayTexturePanel, bpy.types.Panel):
	bl_label = NAME

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		tex= context.texture
		if not tex:
			return False
		vtex= tex.vray
		engine= context.scene.render.engine
		return ((tex.type == 'VRAY' and vtex.type == ID) and (engine in __class__.COMPAT_ENGINES))
	
	def draw(self, context):
		tex= context.texture
		TexEdges= getattr(tex.vray, PLUG)
		
		wide_ui= context.region.width > ui.narrowui

		layout= self.layout

		split= layout.split()
		col= split.column()
		sub= col.column(align= True)
		sub.prop(TexEdges, 'edges_tex')
		sub.prop_search(TexEdges, 'edges_tex_tex',
						bpy.data, 'textures',
						text= "")
		if wide_ui:
			col= split.column()
		sub= col.column(align= True)
		sub.prop(TexEdges, 'bg_tex')
		sub.prop_search(TexEdges, 'bg_tex_tex',
						bpy.data, 'textures',
						text= "")

		layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(TexEdges, 'show_hidden_edges')
		if wide_ui:
			col= split.column()
		col.prop(TexEdges, 'width_type', text="Type")
		col.prop(TexEdges, 'width')


def GetRegClasses():
	return (
		VRAY_TP_TexEdges,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
