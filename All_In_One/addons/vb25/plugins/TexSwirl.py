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
ID     = 'TexSwirl'
PLUG   = 'TexSwirl'

NAME   = 'Swirl'
DESC   = "TexSwirl"

PID    = 15

PARAMS = (
	'uvwgen',
	'color1',
	'color2',
	'swirl_intensity',
	'color_contrast',
	'swirl_amount',
	'constant_detail',
	'center_x',
	'center_y',
	'random_seed',
	'twist',
)

def add_properties(rna_pointer):
	class TexSwirl(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(TexSwirl)

	rna_pointer.TexSwirl= PointerProperty(
		name= "TexSwirl",
		type=  TexSwirl,
		description= "V-Ray TexSwirl settings"
	)

	TexSwirl.color1= FloatVectorProperty(
		name= "Color 1",
		description= "First color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (1,1,1)
	)

	# color2
	TexSwirl.color2= FloatVectorProperty(
		name= "Color 2",
		description= "Second color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0,0,0)
	)

	# swirl_intensity
	TexSwirl.swirl_intensity= FloatProperty(
		name= "Swirl Intensity",
		description= "Swirl Intensity",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 2
	)

	# color_contrast
	TexSwirl.color_contrast= FloatProperty(
		name= "Color Contrast",
		description= "Color Contrast",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.4
	)

	# swirl_amount
	TexSwirl.swirl_amount= FloatProperty(
		name= "Swirl Amount",
		description= "Swirl Amount",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	# constant_detail
	TexSwirl.constant_detail= IntProperty(
		name= "Constant Detail",
		description= "Constant Detail",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 4
	)

	# center_x
	TexSwirl.center_x= FloatProperty(
		name= "Center X",
		description= "Center Position X",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= -0.5
	)

	# center_y
	TexSwirl.center_y= FloatProperty(
		name= "Center Y",
		description= "Center Position Y",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= -0.5
	)

	# random_seed
	TexSwirl.random_seed= FloatProperty(
		name= "Random Seed",
		description= "Random Seed",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0
	)

	# twist
	TexSwirl.twist= FloatProperty(
		name= "Twist",
		description= "Twist",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
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

	TexSwirl= getattr(texture.vray, PLUG)

	ofile.write("\n%s %s {"%(PLUG, tex_name))

	PLUGINS['TEXTURE']['TexCommon'].write(bus)

	for param in PARAMS:
		if param == 'uvwgen':
			value= uvwgen
		else:
			value= getattr(TexSwirl, param)
		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))

	ofile.write("\n}\n")

	return tex_name


'''
  GUI
'''
class VRAY_TP_TexSwirl(ui.VRayTexturePanel, bpy.types.Panel):
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
		TexSwirl= getattr(tex.vray, PLUG)

		split= layout.split()
		col= split.column()
		col.prop(TexSwirl, 'color1', text="")
		if wide_ui:
			col= split.column()
		col.prop(TexSwirl, 'color2', text="")

		split= layout.split()
		col= split.column(align=True)
		col.prop(TexSwirl, 'swirl_amount', text="Amount")
		col.prop(TexSwirl, 'swirl_intensity', text="Intensity")
		col.prop(TexSwirl, 'color_contrast', text="Color Contrast")
		if not wide_ui:
			split= layout.split()
		col= split.column(align=True)
		col.prop(TexSwirl, 'twist')
		col.prop(TexSwirl, 'constant_detail')

		split= layout.split()
		row= split.row(align=True)
		row.prop(TexSwirl, 'center_x')
		row.prop(TexSwirl, 'center_y')

		split= layout.split()
		col= split.column()
		col.prop(TexSwirl, 'random_seed', text="Seed")


def GetRegClasses():
	return (
		VRAY_TP_TexSwirl,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
