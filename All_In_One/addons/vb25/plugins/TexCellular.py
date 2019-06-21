#
# V-Ray/Blender
#
# http://vray.cgdo.ru
#
# Author: Andrey M. Izrantsev (aka bdancer)
# E-Mail: izrantsev@cgdo.ru
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# All Rights Reserved. V-Ray(R) is a registered trademark of Chaos Software.
#



# Blender module
import bpy
from bpy.props import *

# V-Ray/Blender modules
from vb25.utils   import *
from vb25.ui      import ui
from vb25.plugins import *
from vb25.texture import *
from vb25.uvwgen  import *


TYPE   = 'TEXTURE'
ID     = 'TexCellular'
PLUG   = 'TexCellular'

NAME   = 'Cellular'
DESC   = "TexCellular"

PID    = 16

PARAMS = (
  'uvwgen',
	'center_color',
	'edge_color',
	'bg_color',
	'size',
	'spread',
	'density',
	'type',
	'low',
	'middle',
	'high',
	'fractal',
	'fractal_iterations',
	'fractal_roughness',
#	'components',
)


def add_properties(rna_pointer):
	class TexCellular(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(TexCellular)

	rna_pointer.TexCellular= PointerProperty(
		name= "TexCellular",
		type=  TexCellular,
		description= "V-Ray TexCellular settings"
	)

	# use_3d_mapping
	TexCellular.use_3d_mapping= BoolProperty(
		name= "use 3d mapping",
		description= "",
		default= True
	)

	# center_color: acolor texture
	TexCellular.center_color = FloatVectorProperty(
		name= "Center Color",
		description= "Center Color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (1,1,1)
	)

	TexCellular.center_color_tex= StringProperty(
		name= "Center Color texture",
		description= "Center Color texture",
		default= ""
	)

	# edge_color: acolor texture
	TexCellular.edge_color = FloatVectorProperty(
		name= "Edge Color",
		description= "Edge Color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0.5,0.5,0.5)
	)

	TexCellular.edge_color_tex= StringProperty(
		name= "Edge Color texture",
		description= "Edge Color texture",
		default= ""
	)

	# bg_color: acolor texture
	TexCellular.bg_color = FloatVectorProperty(
		name= "BG Color",
		description= "BG Color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0,0,0)
	)

	TexCellular.bg_color_tex= StringProperty(
		name= "BG Color texture",
		description= "BG Color texture",
		default= ""
	)

	# size: float = 0.2
	TexCellular.size= FloatProperty(
		name= "Cellular Size",
		description= "Cellular Size",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.2
	)

	# spread: float = 0.5
	TexCellular.spread= FloatProperty(
		name= "Spread",
		description= "Spread",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.5
	)

	# density: float = 0.25
	TexCellular.density= FloatProperty(
		name= "Density Amount",
		description= "Density Amount",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.25
	)

	# type: integer = 0, 0 = dots; 1 = chips; 2 = cells; 3 = chess cells; 4 = plasma
	TexCellular.type= EnumProperty(
		name= "Type",
		description= "Cellular type",
		items= (
			('DOTS',        "Dots",  ""), # 0
			('CHIPS',       "Chips", ""),
			('CELLS',       "Cells", ""),
			('CHESS_CELLS', "Chess Cells", ""),
			('PLASMA',      "Plasma", ""),
		),
		default= 'DOTS'
	)

	# low: float = 0, Low threshold (for the bg color)
	TexCellular.low= FloatProperty(
		name= "Low",
		description= "Low threshold (for the bg color)",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0
	)

	# middle: float = 0.5, Middle threshold (for the edge color)
	TexCellular.middle= FloatProperty(
		name= "Middle",
		description= "Middle threshold (for the edge color)",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.5
	)

	# high: float = 1, High threshold (for the center color)
	TexCellular.high= FloatProperty(
		name= "High",
		description= "High threshold (for the center color)",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	# fractal: bool = false
	TexCellular.fractal = BoolProperty(
		name= "Fractal",
		description= "Fractal",
		default= False
	)

	# fractal_iterations: float = 3, The number of fractal iterations
	TexCellular.fractal_iterations= FloatProperty(
		name= "Fractal Iterations",
		description= "Fractal Iterations",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 3
	)

	# fractal_roughness: float = 0, The fractal roughness (0.0f is very rough; 1.0 is smooth - i.e. no fractal)
	TexCellular.fractal_roughness= FloatProperty(
		name= "Fractal Roughness",
		description= "Fractal Roughness",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0
	)

	# TODOO
	# components: output vector texture, 
	# Outputs (F(1), F(2), F(3)) (the distances to the three closest points in the cellular context)
	# as a Vector


'''
  OUTPUT
'''
def write(bus):

	TYPE= {
		'DOTS':    0,
		'CHIPS':    1,
		'CELLS': 2,
		'CHESS_CELLS': 3,
		'PLASMA': 4,
	}

	scene= bus['scene']
	ofile= bus['files']['textures']

	slot=     bus['mtex']['slot']
	texture=  bus['mtex']['texture']
	tex_name= bus['mtex']['name']

	uvwgen= write_uvwgen(bus)

	TexCellular= getattr(texture.vray, PLUG)

	mapped_keys= ('center_color', 'edge_color', 'bg_color')
	mapped_params= write_sub_textures(bus,
					  TexCellular,
					  [key+'_tex' for key in mapped_keys])

	ofile.write("\n%s %s {"%(PLUG, tex_name))

	PLUGINS['TEXTURE']['TexCommon'].write(bus)

	for param in PARAMS:
		if param == 'uvwgen':
			value= uvwgen
		elif param == 'type':
			value=TYPE[TexCellular.type]
		elif param in mapped_keys and param+'_tex' in mapped_params:
			value= mapped_params[param+'_tex']
		else:
			value= getattr(TexCellular, param)
		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))

	ofile.write("\n}\n")

	return tex_name


'''
  GUI
'''
class VRAY_TP_TexCellular(ui.VRayTexturePanel, bpy.types.Panel):
	bl_label       = NAME
	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		tex = context.texture
		return tex and tex.type == 'VRAY' and tex.vray.type == ID and ui.engine_poll(cls, context)

	def draw(self, context):
		wide_ui = context.region.width > ui.narrowui
		layout  = self.layout

		tex= context.texture
		TexCellular= getattr(tex.vray, PLUG)

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexCellular, 'center_color', text="Center Color")
		col.prop_search(TexCellular, 'center_color_tex',
						bpy.data,    'textures',
						text= "")

		if wide_ui:
			col= split.column(align= True)
		col.prop(TexCellular, 'edge_color', text="Edge Color")
		col.prop_search(TexCellular, 'edge_color_tex',
						bpy.data,    'textures',
						text= "")

		if wide_ui:
			col= split.column(align= True)
		col.prop(TexCellular, 'bg_color', text="BG Color")
		col.prop_search(TexCellular, 'bg_color_tex',
						bpy.data,    'textures',
						text= "")


		split= layout.split()
		col= split.column(align=True)
		col.prop(TexCellular, 'size', text="Size")
		col.prop(TexCellular, 'spread', text="Spread")
		col.prop(TexCellular, 'density', text="Density")

		if not wide_ui:
			split= layout.split()
		col= split.column(align=True)
		col.prop(TexCellular, 'type')

		split= layout.split()
		row= split.row(align=True)
		row.prop(TexCellular, 'low')
		row.prop(TexCellular, 'middle')
		row.prop(TexCellular, 'high')

		split= layout.split()
		col = split.column(align=True)
		col.prop(TexCellular, 'fractal', text="Fractal")
		if TexCellular.fractal:
			col.prop(TexCellular, 'fractal_iterations', text="Fractal Iterations")
			col.prop(TexCellular, 'fractal_roughness', text="Fractal Roughness")


def GetRegClasses():
	return (
		VRAY_TP_TexCellular,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
