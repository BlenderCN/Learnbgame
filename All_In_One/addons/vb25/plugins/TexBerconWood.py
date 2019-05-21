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
ID=   'TexBerconWood'
PLUG= 'TexBerconWood'
NAME= 'Bercon Wood'
DESC= "Bercon Wood."
PID=   35

PARAMS= (
	'uvwgen',
	'noise_color1',
	'noise_color2',
	'noise_color3',
	'noise_map1',
	'noise_map2',
	'noise_map3',
	'wood_size',
	'low_tresh',
	'high_tresh',
	'wood_type',
	'trunk_str',
	'trunk_freq',
	'radial_z',
	'angle_str',
	'angle_freq',
	'angle_rad',
	'grain_str',
	'grain_freq',
	'grain_lock',
	'width_var',
	'gain_var',
	'rand_seed',
	'wood_skew',
	'samples',
	'dist_map',
	'dist_map2',
	'dist_str',
	'use_dist',
	'tex_size',
	'tex_low',
	'tex_high',
	'tex_skew',
	'tex_width_var',
	'tex_gain_var',
	'tex_trunk_str',
	'tex_trunk_freq',
	'tex_radial_str',
	'tex_radial_freq',
	'tex_z_str',
	'tex_ang_str',
	'tex_ang_freq',
	'tex_ang_rad',
	'tex_grain_str',
	'tex_grain_freq',
#	'use_curve_input', - TODO
#	'curve_output',    - TODO
#	'curve_input',     - TODO
)





def add_properties(rna_pointer):
	class TexBerconWood(bpy.types.PropertyGroup):

		# use_3d_mapping
		use_3d_mapping  = BoolProperty(
			name        = "use 3d mapping",
			description = "",
			default     = True
		)

		#  noise_color1: color = Color(0, 0, 0), noise color 1
		noise_color1 = FloatVectorProperty(
			name        = "noise color 1",
			description = "noise color 1",
			subtype     = 'COLOR',
			min         = 0.0,
			max         = 1.0,
			soft_min    = 0.0,
			soft_max    = 1.0,
			default     = (0,0,0)
		)

		#  noise_color2: color = Color(0, 0, 0), noise color 2
		noise_color2 = FloatVectorProperty(
			name        = "noise color 2",
			description = "noise color 2",
			subtype     = 'COLOR',
			min         = 0.0,
			max         = 1.0,
			soft_min    = 0.0,
			soft_max    = 1.0,
			default     = (0,0,0)
		)

		#  noise_color3: color = Color(0, 0, 0), noise color 3
		noise_color3 = FloatVectorProperty(
			name        = "noise color 3",
			description = "noise color 3",
			subtype     = 'COLOR',
			min         = 0.0,
			max         = 1.0,
			soft_min    = 0.0,
			soft_max    = 1.0,
			default     = (0,0,0)
		)

		#  noise_map1: acolor texture, unlimited list, noise map 1
		noise_map1 = StringProperty(
			name        = "noise map 1 texture ",
			description = "noise map 1 texture",
			default     = ""
		)

		#  noise_map2: acolor texture, unlimited list, noise map 2
		noise_map2 = StringProperty(
			name        = "noise map 2 texture ",
			description = "noise map 2 texture",
			default     = ""
		)

		#  noise_map3: acolor texture, unlimited list, noise map 3
		noise_map3 = StringProperty(
			name        = "noise map 3 texture ",
			description = "noise map 3 texture",
			default     = ""
		)

		#  wood_size: float = 3, wood size
		wood_size = FloatProperty(
			name        = "Wood Size",
			description = "Wood Size",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 3
		)

		#  low_tresh: float = 0.3, low treshold
		low_tresh = FloatProperty(
			name        = "low treshold",
			description = "low treshold",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 0.3
		)

		#  high_tresh: float = 1, high treshold
		high_tresh = FloatProperty(
			name        = "high treshold",
			description = "high treshold",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 1
		)

		#  wood_type: integer = 0, 0:Radial wood, 1:Perlin wood, 2:Simplex wood, 3:Linear wood
		wood_type = EnumProperty(
		name        = "Type",
		description = "Cellular type",
		items       = (
					  ('RADIAL',   "Radial wood",  ""), # 0
					  ('PERLIN',   "Perlin wood",  ""),
					  ('SIMPLEX',  "Simplex wood", ""),
					  ('LINEAR',   "Linear wood",  ""),
		),
		default     = 'RADIAL'
		)

		#  trunk_str: float = 1, trunk strength
		trunk_str = FloatProperty(
			name        = "trunk strength",
			description = "trunk strength",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 1
		)

		#  trunk_freq: float = 0.04, trunk frequency
		trunk_freq = FloatProperty(
			name        = "trunk frequency",
			description = "trunk frequency",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 0.04
		)

		#  radial_str: float = 0.25, radial strength
		radial_str = FloatProperty(
			name        = "radial strength",
			description = "radial strength",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 0.25
		)

		#  radial_freq: float = 0.1, radial frequency
		radial_freq = FloatProperty(
			name        = "radial frequency",
			description = "radial frequency",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 0.1
		)

		#  radial_z: float = 0.01, radial Z frequency
		radial_z = FloatProperty(
			name        = "radial Z frequency",
			description = "radial Z frequency",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 0.01
		)

		#  angle_str: float = 0.1, angle strength
		angle_str = FloatProperty(
			name        = "angle strength",
			description = "angle strength",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 0.1
		)

		#  angle_freq: float = 1, angle frequency
		angle_freq = FloatProperty(
			name        = "angle frequency",
			description = "angle frequency",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 1
		)

		#  angle_rad: float = 15, angle radius
		angle_rad = FloatProperty(
			name        = "angle radius",
			description = "angle radius",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 15
		)

		#  grain_str: float = 0.2, grain strength
		grain_str = FloatProperty(
			name        = "grain strength",
			description = "grain strength",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 0.2
		)

		#  grain_freq: float = 5, grain frequency
		grain_freq = FloatProperty(
			name        = "grain frequency",
			description = "grain frequency",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 5
		)

		#  grain_lock: bool = false, grain lock
		grain_lock = BoolProperty(
			name        = "grain lock",
			description = "",
			default     = False
		)

		#  width_var: float = 0.5, width variation
		width_var = FloatProperty(
			name        = "width variation",
			description = "width variation",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 0.5
		)

		#  gain_var: float = 0.75, gain variation
		gain_var = FloatProperty(
			name        = "gain variation",
			description = "gain variation",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 0.75
		)

		#  rand_seed: float = 12.345, random seed
		rand_seed = FloatProperty(
			name        = "random seed",
			description = "random seed",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 12.345
		)

		#  wood_skew: float = 0.75, wood skew
		wood_skew = FloatProperty(
			name        = "wood skew",
			description = "wood skew",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 0.75
		)

		#  samples: integer = 4, samples
		samples = IntProperty(
            name        = "samples",
            description = "samples",
            min         = 0,
            max         = 100,
            soft_min    = 0,
            soft_max    = 10,
            default     = 4
        )


		#  dist_map: acolor texture, unlimited list, distortion map
		dist_map = StringProperty(
			name        = "distortion map",
			description = "distortion map",
			default     = ""
		)

		#  dist_map2: acolor texture, unlimited list, distortion map 2
		dist_map2 = StringProperty(
			name        = "distortion map 2",
			description = "distortion map 2",
			default     = ""
		)

		#  dist_str: float = 0.1, distortion strength
		dist_str = FloatProperty(
			name        = "distortion strength",
			description = "distortion strength",
			min         = 0.0,
			max         = 1000.0,
			soft_min    = 0.0,
			soft_max    = 10.0,
			precision   = 3,
			default     = 0.1
		)

		#  use_dist: bool = false, use distortion
		use_dist = BoolProperty(
			name        = "use distortion",
			description = "",
			default     = False
		)

		#  tex_size: acolor texture, texture for the size
		tex_size = StringProperty(
			name        = "texture for the size",
			description = "texture for the size",
			default     = ""
		)

		#  tex_low: acolor texture, texture for low treshhold
		tex_low = StringProperty(
			name        = "texture for low treshhold",
			description = "texture for low treshhold",
			default     = ""
		)

		#  tex_high: acolor texture, texture for high greshhold
		tex_high = StringProperty(
			name        = "texture for high greshhold",
			description = "texture for high greshhold",
			default     = ""
		)

		#  tex_skew: acolor texture, texture for skew
		tex_skew = StringProperty(
			name        = "texture for skew",
			description = "texture for skew",
			default     = ""
		)

		#  tex_width_var: acolor texture, texture for width variation
		tex_width_var = StringProperty(
			name        = "texture for width variation",
			description = "texture for width variation",
			default     = ""
		)

		#  tex_gain_var: acolor texture, texture for gain variation
		tex_gain_var = StringProperty(
			name        = "texture for gain variation",
			description = "texture for gain variation",
			default     = ""
		)

		#  tex_trunk_str: acolor texture, texture for trunk strength
		tex_trunk_str = StringProperty(
			name        = "texture for trunk strength",
			description = "texture for trunk strength",
			default     = ""
		)

		#  tex_trunk_freq: acolor texture, texture for trunk frequency
		tex_trunk_freq = StringProperty(
			name        = "texture for trunk frequency",
			description = "texture for trunk frequency",
			default     = ""
		)

		#  tex_radial_str: acolor texture, texture for radial strength
		tex_radial_str = StringProperty(
			name        = "texture for radial strength",
			description = "texture for radial strength",
			default     = ""
		)

		#  tex_radial_freq: acolor texture, texture for radial frequency
		tex_radial_freq = StringProperty(
			name        = "texture for radial frequency",
			description = "texture for radial frequency",
			default     = ""
		)

		#  tex_z_str: acolor texture, texture for radial z strength
		tex_z_str = StringProperty(
			name        = "texture for radial z strength",
			description = "texture for radial z strength",
			default     = ""
		)

		#  tex_ang_str: acolor texture, texture for angular strength
		tex_ang_str = StringProperty(
			name        = "texture for angular strength",
			description = "texture for angular strength",
			default     = ""
		)

		#  tex_ang_freq: acolor texture, texture for angular frequency
		tex_ang_freq = StringProperty(
			name        = "texture for angular frequency",
			description = "texture for angular frequency",
			default     = ""
		)

		#  tex_ang_rad: acolor texture, texture for angular radius
		tex_ang_rad = StringProperty(
			name        = "texture for angular radius",
			description = "texture for angular radius",
			default     = ""
		)

		#  tex_grain_str: acolor texture, texture for grain strength
		tex_grain_str = StringProperty(
			name        = "texture for grain strength",
			description = "texture for grain strength",
			default     = ""
		)

		#  tex_grain_freq: acolor texture, texture for grain frequency
		tex_grain_freq = StringProperty(
			name        = "texture for grain frequency",
			description = "texture for grain frequency",
			default     = ""
		)

		#  TODO
		#  use_curve_input: bool = false
		#  curve_output: output float texture, Calculated blend amount to be tranformed by the bezier curve!
		#  curve_input: float texture = 0.5, If curve is used the output value will be taken from this texture
		
	bpy.utils.register_class(TexBerconWood)

	rna_pointer.TexBerconWood = PointerProperty(
		name        = "TexBerconWood",
		type        =  TexBerconWood,
		description = "V-Ray TexBerconWood settings"
	)


def write(bus):


	WOOD_TYPE = {
		'RADIAL':  0,
		'PERLIN':  1,
		'SIMPLEX': 2,
		'LINEAR':  3,
	}

	scene = bus['scene']
	ofile = bus['files']['textures']

	slot     = bus['mtex']['slot']
	texture  = bus['mtex']['texture']
	tex_name = bus['mtex']['name']

	uvwgen = write_uvwgen(bus)

	TexBerconWood = getattr(texture.vray, PLUG)

	mapped = (  'noise_map1',     'noise_map2',     'noise_map3',
				'dist_map',       'dist_map2',      'tex_size',
				'tex_low',        'tex_high',       'tex_skew',
				'tex_width_var',  'tex_gain_var',   'tex_trunk_str',
				'tex_trunk_freq', 'tex_radial_str', 'tex_radial_freq',
				'tex_z_str',      'tex_ang_str',    'tex_ang_freq',
				'tex_ang_rad',    'tex_grain_str',  'tex_grain_freq')

	mapped_params = write_sub_textures(bus,
									   TexBerconWood,
									   mapped)

	print(len(mapped_params))
	
	ofile.write("\n%s %s {"%(PLUG, tex_name))
	for param in PARAMS:
		if param == 'uvwgen':
			value= uvwgen

		elif param == 'wood_type':
			value=WOOD_TYPE[TexBerconWood.wood_type]

		elif param in mapped:
			if param in mapped_params:
				value= mapped_params[param]	
			else:
				continue			

		else:
			value= getattr(TexBerconWood, param)
		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))
	ofile.write("\n}\n")

	return tex_name


'''
  GUI
'''
class VRAY_TP_TexBerconWood(ui.VRayTexturePanel, bpy.types.Panel):
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
		TexBerconWood= getattr(tex.vray, PLUG)

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexBerconWood, 'wood_type')

		layout.separator()

		layout.label(text="Noise Color:")
		split = layout.split()
		col= split.column(align= True)
		col.prop(TexBerconWood, 'noise_color1', text="Color 1")
		col.prop_search(TexBerconWood, 'noise_map1',
						bpy.data, 'textures',
						text= "")

		if wide_ui:
			col= split.column(align= True)
		col.prop(TexBerconWood, 'noise_color2', text="Color 2")
		col.prop_search(TexBerconWood, 'noise_map2',
						bpy.data, 'textures',
						text= "")

		if wide_ui:
			col= split.column(align= True)
		col.prop(TexBerconWood, 'noise_color3', text="Color 3")
		col.prop_search(TexBerconWood, 'noise_map3',
						bpy.data, 'textures',
						text= "")

		# wood size\width group
		split= layout.split()
		col= split.column(align= True)
		col.prop(TexBerconWood, 'wood_size', text="Wood Size")
		col.prop_search(TexBerconWood, 'tex_size',
						bpy.data, 'textures',
						text= "")

		split= layout.split()

		col= split.column(align= True)
		col.prop(TexBerconWood, 'width_var', text="Width Variation")
		col.prop_search(TexBerconWood, 'tex_width_var',
						bpy.data, 'textures',
						text= "")
		
		split= layout.split()		
		row = split.row()
		
		# tresh group
		split = row.column()
		col= split.column(align= True)
		col.label(text="Treshold:")
		col.prop(TexBerconWood, 'low_tresh', text="Low")
		col.prop_search(TexBerconWood, 'tex_low',
						bpy.data, 'textures',
						text= "")
		col.separator()
		col.prop(TexBerconWood, 'high_tresh', text="High")
		col.prop_search(TexBerconWood, 'tex_high',
						bpy.data, 'textures',
						text= "")
		
		# trunk group
		split = row.column()
		col= split.column(align= True)
		col.label("Trunk:")

		col.prop(TexBerconWood, 'trunk_str', text="Strength")
		col.prop_search(TexBerconWood, 'tex_trunk_str',
						bpy.data, 'textures',
						text= "")

		col.separator()

		col.prop(TexBerconWood, 'trunk_freq', text="Frequency")
		col.prop_search(TexBerconWood, 'tex_trunk_freq',
						bpy.data, 'textures',
						text= "")

		split= layout.split()		
		row = split.row()

		# radial group
		split = row.column()
		col= split.column(align= True)
		col.label("Radial:")

		col.prop(TexBerconWood, 'radial_str', text="Strength")
		col.prop_search(TexBerconWood, 'tex_radial_str',
						bpy.data, 'textures',
						text= "")

		col.separator()

		col.prop(TexBerconWood, 'radial_freq', text="Frequency")
		col.prop_search(TexBerconWood, 'tex_radial_freq',
						bpy.data, 'textures',
						text= "")

		col.separator()

		col.prop(TexBerconWood, 'radial_z', text="Z Strength")
		col.prop_search(TexBerconWood, 'tex_z_str',
						bpy.data, 'textures',
						text= "")

		# angle group
		split = row.column()
		col= split.column(align= True)
		col.label("Angle:")

		col.prop(TexBerconWood, 'angle_str', text="Strength")
		col.prop_search(TexBerconWood, 'tex_ang_str',
						bpy.data, 'textures',
						text= "")

		col.separator()

		col.prop(TexBerconWood, 'angle_freq', text="Frequency")
		col.prop_search(TexBerconWood, 'tex_ang_freq',
						bpy.data, 'textures',
						text= "")

		col.separator()

		col.prop(TexBerconWood, 'angle_rad', text="Radius")
		col.prop_search(TexBerconWood, 'tex_ang_rad',
						bpy.data, 'textures',
						text= "")

		# grain group
		split= layout.split()
		col= split.column(align= True)
		col.prop(TexBerconWood, 'grain_lock')
		split= layout.split()
		col= split.column(align= True)
		if TexBerconWood.grain_lock:
			col.prop(TexBerconWood, 'grain_str')
			col.prop_search(TexBerconWood, 'tex_grain_str',
							bpy.data, 'textures',
							text= "")

			if wide_ui:
				col= split.column(align= True)
			col.prop(TexBerconWood, 'grain_freq')
			col.prop_search(TexBerconWood, 'tex_grain_freq',
							bpy.data, 'textures',
							text= "")

		# gain\skew group
		split= layout.split()
		col= split.column(align= True)
		col.prop(TexBerconWood, 'gain_var')
		col.prop_search(TexBerconWood, 'tex_gain_var',
						bpy.data, 'textures',
						text= "")

		if wide_ui:
			col= split.column(align= True)
		col.prop(TexBerconWood, 'wood_skew')
		col.prop_search(TexBerconWood, 'tex_skew',
						bpy.data, 'textures',
						text= "")

		# dist group
		split= layout.split()
		col= split.column(align= True)
		col.prop(TexBerconWood, 'use_dist')
		split= layout.split()
		col= split.column(align= True)
		if TexBerconWood.use_dist:
			col.prop_search(TexBerconWood, 'dist_map',
							bpy.data, 'textures',
							text= "")
			col.prop_search(TexBerconWood, 'dist_map2',
							bpy.data, 'textures',
							text= "")
			if wide_ui:
				col= split.column(align= True)
			col.prop(TexBerconWood, 'dist_str')

		# other
		split= layout.split()
		col= split.column(align= True)
		col.prop(TexBerconWood, 'samples', text="Samples")
		split= layout.split()
		col= split.column(align= True)
		col.prop(TexBerconWood, 'rand_seed', text="Random Seed")


def GetRegClasses():
	return (
		VRAY_TP_TexBerconWood,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
