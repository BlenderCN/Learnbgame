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
ID=   'TexWater'
PLUG= 'TexWater'
NAME= 'Water'
DESC= "Water."
PID=   27

PARAMS= (
	'uvwgen',
	'height_mult',
	'wind_direction',
	'wind_magnitude',
	'wind_direction_mult',
	'choppy_mult',
	'movement_rate',
	'seed',
	'resolution',
	'patch_size',
)

def add_properties(rna_pointer):
	class TexWater(bpy.types.PropertyGroup):

		# use_3d_mapping
		use_3d_mapping  = BoolProperty(
			name        = "use 3d mapping",
			description = "",
			default     = True
		)

		# height_mult: float = 1, multiplier for the height of the water
		height_mult = FloatProperty(
			name        = "Height Mult",
			description = "multiplier for the height of the water",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 1
		)

		# wind_direction: float = 0, direction of the wind
		wind_direction  = FloatProperty(
			name        = "Wind Direction",
			description = "direction of the wind",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 0
		)

		# wind_magnitude: float = 0, magnitude of the wind
		wind_magnitude  = FloatProperty(
			name        = "Wind Magnitude",
			description = "magnitude of the wind",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 800
		)

		#  wind_direction_mult: float = 0
		wind_direction_mult = FloatProperty(
			name        = "Wind Direction Mult",
			description = "Wind Direction Mult",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 0
		)

		#  choppy_mult: float = 0
		choppy_mult = FloatProperty(
			name        = "Choppy Mult",
			description = "Choppy Mult",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 0
		)

		#  movement_rate: float = 1
		movement_rate = FloatProperty(
			name        = "Movement rate",
			description = "Movement rate",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 1.0
		)

		# seed: integer = 1, Used to produce different waters
		seed = IntProperty(
			name        = "Seed",
			description = "Used to produce different waters",
			min         = 0,
			max         = 100,
			soft_min    = 0,
			soft_max    = 10,
			default     = 1
		)

		# resolution: integer = 4, Resolution -> real resolution is 2^res
		resolution = IntProperty(
			name        = "Resolution",
			description = "Resolution -> real resolution is 2^res",
			min         = 0,
			max         = 10000,
			soft_min    = 0,
			soft_max    = 10,
			default     = 512
		)

		# patch_size: float = 128, Size of the patch -> real resolution is 2^res
		patch_size = FloatProperty(
			name        = "Size",
			description = "Size of the patch -> real resolution is 2^res",
			min         = 0.0,
			max         = 10000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 128
		)


	bpy.utils.register_class(TexWater)

	rna_pointer.TexWater = PointerProperty(
		name        = "TexWater",
		type        =  TexWater,
		description = "V-Ray TexWater settings"
	)


def write(bus):
	scene    = bus['scene']
	ofile    = bus['files']['textures']

	texture  = bus['mtex']['texture']
	tex_name = bus['mtex']['name']

	uvwgen   = write_uvwgen(bus)

	TexWater = getattr(texture.vray, PLUG)
	
	ofile.write("\n%s %s {"%(PLUG, tex_name))
	for param in PARAMS:
		if param == 'uvwgen':
			value = uvwgen
		else:
			value = getattr(TexWater, param)
		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))
	ofile.write("\n}\n")

	return tex_name

'''
  GUI
'''
class VRAY_TP_TexWater(ui.VRayTexturePanel, bpy.types.Panel):
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
		TexWater= getattr(tex.vray, PLUG)

		layout.prop(TexWater, 'height_mult', text="Height Multiplier")

		split = layout.split()
		col = split.column(align=True)
		col.prop(TexWater, 'wind_direction', text="Wind Direction")
		col.prop(TexWater, 'wind_magnitude', text="Wind Magnitude")
		col.prop(TexWater, 'wind_direction_mult', text="Wind Magnitude Multiplier")

		split = layout.split()
		col = split.column(align=True)
		col.prop(TexWater, 'choppy_mult', text="Choppy Multiplier")
		col.prop(TexWater, 'movement_rate', text="Rate")

		split = layout.split()
		col = split.column(align=True)
		col.prop(TexWater, 'resolution', text="Resolution")
		col.prop(TexWater, 'patch_size', text="Patch size")

		layout.prop(TexWater, 'seed', text="Seed")


def GetRegClasses():
	return (
		VRAY_TP_TexWater,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
