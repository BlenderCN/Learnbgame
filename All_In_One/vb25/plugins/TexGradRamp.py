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
ID=   'TexGradRamp'
NAME= 'Gradient Ramp'
PLUG= 'TexGradRamp'
DESC= "TexGradRamp"
PID=   6

PARAMS= (
	'positions',
	'colors',
	'texture_map',
	'gradient_type',
	'interpolation',
	'noise_amount',
	'noise_type',
	'noise_size',
	'noise_phase',
	'noise_levels',
	'noise_treshold_low',
	'noise_treshold_high',
	'noise_smooth',
	'uvwgen',
)

def add_properties(rna_pointer):
	class TexGradRamp(bpy.types.PropertyGroup):
		# positions

		# colors

		# texture_map
		texture_map= StringProperty(
			name= "Source texture",
			description= "Texture for \"Mapped\" gradient type",
			default= ""
		)

		# gradient_type
		gradient_type= EnumProperty(
			name= "Gradient type",
			description= "Gradient type",
			items= (
				('FOUR_CORNER', "Four corner", "Four corner"), # 0
				('BOX',         "Box",         "Box"),
				('DIAGONAL',    "Diagonal",    "Diagonal"),
				('LIGHTING',    "Lighting",    "Lighting"),
				('LINEAR',      "Linear",      "Linear"),
				('MAPPED',      "Mapped",      "Mapped"),
				('NORMAL',      "Normal",      "normal"),
				('PONG',        "Pong",        "Pong"),
				('RADIAL',      "Radial",      "Radial"),
				('SPIRAL',      "Spiral",      "Spiral"),
				('SWEEP',       "Sweep",       "Sweep"),
				('TARTAN',      "Tartan",      "Tartan"),
			),
			default= 'FOUR_CORNER'
		)

		# interpolation
		interpolation= EnumProperty(
			name= "Interpolation",
			description= "Interpolation",
			items= (
				('NONE',    "None",          "None"), # 0
				('LINEAR',  "Linear",        "Linear"),
				('EXPUP',   "Exponent Up",   "Exponent Up"),
				('EXPDOWN', "Exponent Down", "Exponent Down"),
				('SMOOTH',  "Smooth",        "Smooth"),
				('BUMP',    "Bump",          "Bump"),
				('SPIKE',   "Spike",         "Spike"),
			),
			default= 'LINEAR'
		)

		# noise_amount
		noise_amount= FloatProperty(
			name= "Amount",
			description= "Distortion noise amount",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0
		)

		# noise_type
		noise_type= EnumProperty(
			name= "Type",
			description= "Noise type",
			items= (
				('REGULAR',    "Regular",    ""), # 0
				('FRACTAL',    "Fractal",    ""),
				('TRUBULENCE', "Turbulence", ""),
			),
			default= 'REGULAR'
		)

		# noise_size
		noise_size= FloatProperty(
			name= "Size",
			description= "default = 1.0",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 1
		)

		# noise_phase
		noise_phase= FloatProperty(
			name= "Phase",
			description= "default = 0.0",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0
		)

		# noise_levels
		noise_levels= FloatProperty(
			name= "Iterations",
			description= "default = 4.0",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 4
		)

		# noise_treshold_low
		noise_treshold_low= FloatProperty(
			name= "Low",
			description= "default = 0.0f",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0
		)

		# noise_treshold_high
		noise_treshold_high= FloatProperty(
			name= "High",
			description= "default = 1.0f",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0
		)

		# noise_smooth
		noise_smooth= FloatProperty(
			name= "Smooth",
			description= "default = 0.0f",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0
		)

	bpy.utils.register_class(TexGradRamp)

	rna_pointer.TexGradRamp= PointerProperty(
		name= "TexGradRamp",
		type=  TexGradRamp,
		description= "V-Ray TexGradRamp settings"
	)


def write(bus):
	GRADIENT_TYPE= {
		'FOUR_CORNER': 0,
		'BOX':         1,
		'DIAGONAL':    2,
		'LIGHTING':    3,
		'LINEAR':      4,
		'MAPPED':      5,
		'NORMAL':      6,
		'PONG':        7,
		'RADIAL':      8,
		'SPIRAL':      9,
		'SWEEP':      10,
		'TARTAN':     11,
	}
	INTERPOLATION= {
		'NONE':    0,
		'LINEAR':  1,
		'EXPUP':   2,
		'EXPDOWN': 3,
		'SMOOTH':  4,
		'BUMP':    5,
		'SPIKE':   6,
	}
	NOISE_TYPE= {
		'REGULAR':    0,
		'FRACTAL':    1,
		'TRUBULENCE': 2
	}
	
	scene= bus['scene']
	ofile= bus['files']['textures']

	slot=     bus['mtex']['slot']
	texture=  bus['mtex']['texture']
	tex_name= bus['mtex']['name']

	uvwgen= write_uvwgen(bus)

	if texture.color_ramp:
		ramp_col= []
		for i,element in enumerate(texture.color_ramp.elements):
			tex_acolor= "%sC%i"%(tex_name,i)
			ofile.write("\nTexAColor %s {" % (tex_acolor))
			ofile.write("\n\ttexture= %s;" % ("AColor(%.3f,%.3f,%.3f,%.3f)" % tuple(element.color)))
			ofile.write("\n}\n")
			ramp_col.append(tex_acolor)

	TexGradRamp= getattr(texture.vray, PLUG)
	ofile.write("\n%s %s {"%(PLUG, tex_name))
	for param in PARAMS:
		if param == 'uvwgen':
			value= uvwgen
		elif param == 'noise_type':
			value= NOISE_TYPE[TexGradRamp.noise_type]
		elif param == 'gradient_type':
			value= GRADIENT_TYPE[TexGradRamp.gradient_type]
		elif param == 'interpolation':
			value= INTERPOLATION[TexGradRamp.interpolation]
		elif param == 'positions':
			if not texture.color_ramp:
				value= "ListFloat(1.0,0.0)"
			else:
				ramp_pos= []
				for element in texture.color_ramp.elements:
					ramp_pos.append("%.3f"%(element.position))
				value= "ListFloat(%s)" % (",".join(ramp_pos))
		elif param == 'colors':
			if not texture.color_ramp:
				value= "List(Color(1.0,1.0,1.0),Color(0.0,0.0,0.0))"
			else:
				value= "List(%s)" % (",".join(ramp_col))
		elif param == 'texture_map':
			continue
		else:
			value= getattr(TexGradRamp, param)
		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))

	PLUGINS['TEXTURE']['TexCommon'].write(bus)

	ofile.write("\n}\n")

	return tex_name


'''
  GUI
'''
class VRAY_TP_TexGradRamp(ui.VRayTexturePanel, bpy.types.Panel):
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
		TexGradRamp= getattr(tex.vray, PLUG)

		# layout.template_color_ramp(TexGradRamp, 'ramp_elements')
		
		layout.prop(tex,'use_color_ramp')
		if tex.use_color_ramp:
			layout.template_color_ramp(tex, 'color_ramp')

		layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(TexGradRamp, 'gradient_type')
		col.prop(TexGradRamp, 'interpolation')

		if TexGradRamp.gradient_type == 'MAPPED':
			layout.separator()
			
			split= layout.split()
			row= split.row(align= True)
			row.label(text="Source map:")
			row.prop_search(TexGradRamp, 'texture_map',
							bpy.data,    'textures',
							text= "")

		layout.separator()

		box= layout.box()

		split= box.split()
		row= split.row(align= True)
		row.label(text="Noise:")
		row.prop(TexGradRamp, 'noise_amount')

		split= box.split()
		split.active= TexGradRamp.noise_amount > 0.0
		col= split.column()
		col.prop(TexGradRamp, 'noise_type')
		col.prop(TexGradRamp, 'noise_size')
		if wide_ui:
			col= split.column()
		col.prop(TexGradRamp, 'noise_levels')
		col.prop(TexGradRamp, 'noise_phase')

		split= box.split()
		split.active= TexGradRamp.noise_amount > 0.0
		row= split.row(align= True)
		row.prop(TexGradRamp, 'noise_treshold_low')
		row.prop(TexGradRamp, 'noise_treshold_high')
		row.prop(TexGradRamp, 'noise_smooth')


def GetRegClasses():
	return (
		VRAY_TP_TexGradRamp,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
