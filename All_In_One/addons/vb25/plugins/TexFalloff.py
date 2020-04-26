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

ID=   'TexFalloff'
PLUG= 'TexFalloff'
NAME= 'Falloff'
DESC= "TODO."
PID=  1

PARAMS= (
	'color1',
	'color2',
	'type',
	'direction_type',
	'fresnel_ior',
	'dist_extrapolate',
	'dist_near',
	'dist_far',
	'explicit_dir',
	'use_blend_input'
)


def add_properties(VRayTexture):
	class TexFalloff(bpy.types.PropertyGroup):
		color1= FloatVectorProperty(
			name= "Front color",
			description= "First color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (1,1,1)
		)

		color1_tex= StringProperty(
			name= "Front texture ",
			description= "Front texture",
			default= ""
		)

		color2= FloatVectorProperty(
			name= "Side color",
			description= "Second color",
			subtype= 'COLOR',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0,0,0)
		)

		color2_tex= StringProperty(
			name= "Side texture ",
			description= "Side texture",
			default= ""
		)

		type= EnumProperty(
			name= "Type",
			description= "Falloff type",
			items= (
				('TA',"Towards / Away",""),
				('PP',"Perpendicular / Parallel",""),
				('FRES',"Fresnel",""),
				('SHAD',"Shadow / Light",""),
				('DIST',"Distance blend","")
			),
			default= 'TA'
		)

		direction_type= EnumProperty(
			name= "Direction type",
			description= "Direction type",
			items= (
				('VIEWZ',   "View Z",           ""),
				('VIEWX',   "View X",           ""),
				('VIEWY',   "View Y",           ""),
				('EXPL',    "Explicit",         ""),
				('LX',      "Local X",          ""),
				('LY',      "Local Y",          ""),
				('LZ',      "Local Z",          ""),
				('WX',      "World X",          ""),
				('WY',      "World Y",          ""),
				('WZ',      "World Z",          ""),
			),
			default= 'VIEWZ'
		)

		fresnel_ior= FloatProperty(
			name= "Fresnel IOR",
			description= "IOR for the Fresnel falloff type",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 1.6
		)

		dist_extrapolate= BoolProperty(
			name= "Extrapolate distance",
			description= "Extrapolate for the distance blend falloff type",
			default= False
		)

		dist_near= FloatProperty(
			name= "Near distance",
			description= "Near distance for the distance blend falloff type",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0
		)

		dist_far= FloatProperty(
			name= "Far distance",
			description= "Far distance for the distance blend falloff type",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 100
		)

		explicit_dir= FloatVectorProperty(
			name= "Explicit direction",
			description= "Direction for the explicit direction type",
			subtype= 'DIRECTION',
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0,0,1)
		)

		use_blend_input= BoolProperty(
			name= "Use \"blend\" input",
			description= "TODO",
			default= False
		)
	bpy.utils.register_class(TexFalloff)
	
	VRayTexture.TexFalloff= PointerProperty(
		name= "TexFalloff",
		type=  TexFalloff,
		description= "V-Ray TexFalloff settings"
	)



def write(bus):
	TYPE= {
		'TA':   0,
		'PP':   1,
		'FRES': 2,
		'SHAD': 3,
		'DIST': 4
	}

	DIRECTION_TYPE= {
		'VIEWZ': 0,
		'VIEWX': 1,
		'VIEWY': 2,
		'EXPL':  3,
		'LX':    4,
		'LY':    5,
		'LZ':    6,
		'WX':    7,
		'WY':    8,
		'WZ':    9
	}

	ofile= bus['files']['textures']
	scene= bus['scene']

	slot=     bus['mtex']['slot']
	texture=  bus['mtex']['texture']
	tex_name= bus['mtex']['name']

	TexFalloff= getattr(texture.vray, PLUG)

	mapped_params= write_sub_textures(bus,
									  TexFalloff,
									  ('color1_tex', 'color2_tex'))

	ofile.write("\n%s %s {" % (PLUG, tex_name))

	PLUGINS['TEXTURE']['TexCommon'].write(bus)

	for param in PARAMS:
		if param == 'direction_type':
			value= DIRECTION_TYPE[TexFalloff.direction_type]

		elif param == 'type':
			value= TYPE[TexFalloff.type]

		elif param in ('color1','color2') and param+'_tex' in mapped_params:
			value= mapped_params[param+'_tex']

		else:
			value= getattr(TexFalloff, param)
		
		ofile.write("\n\t%s= %s;" % (param, a(scene, value)))
	ofile.write("\n}\n")

	return tex_name



'''
  GUI
'''
class VRAY_TP_TexFalloff(ui.VRayTexturePanel, bpy.types.Panel):
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
		wide_ui= context.region.width > ui.narrowui
		layout= self.layout

		tex= context.texture
		TexFalloff= getattr(tex.vray, PLUG)

		split= layout.split()
		col= split.column()
		sub= col.column(align= True)
		sub.prop(TexFalloff, 'color1')
		sub.prop_search(TexFalloff, 'color1_tex',
						bpy.data, 'textures',
						text= "")
		if wide_ui:
			col= split.column()
		sub= col.column(align= True)
		sub.prop(TexFalloff, 'color2')
		sub.prop_search(TexFalloff, 'color2_tex',
						bpy.data, 'textures',
						text= "")

		layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(TexFalloff, 'type')
		col.prop(TexFalloff, 'direction_type')

		split= layout.split()
		col= split.column()
		if TexFalloff.type == 'FRES':
			col.prop(TexFalloff, 'fresnel_ior')
		elif TexFalloff.type == 'DIST':
			col.prop(TexFalloff, 'dist_near')
			if wide_ui:
				col= split.column()
			col.prop(TexFalloff, 'dist_far')
			col.prop(TexFalloff, 'dist_extrapolate')


def GetRegClasses():
	return (
		VRAY_TP_TexFalloff,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
