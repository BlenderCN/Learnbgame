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
from vb25.utils import *
from vb25.ui    import ui


TYPE= 'TEXTURE'

ID=   'TexSky'
NAME= 'Sky'
PLUG= 'TexSky'
DESC= "Sky texture."
PID=  3

PARAMS= (
	#'transform',
	#'target_transform',
	'turbidity',
	'ozone',
	'water_vapour',
	'intensity_multiplier',
	'size_multiplier',
	#'up_vector',
	'invisible',
	'horiz_illum',
	'sky_model',
	'sun'
)


def add_properties(VRayTexture):
	class TexSky(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(TexSky)

	VRayTexture.TexSky= PointerProperty(
		name= "TexSky",
		type=  TexSky,
		description= "V-Ray TexSky settings"
	)

	TexSky.auto_sun= BoolProperty(
		name= "Take settings from Sun",
		description= "Take settings from Sun automatically",
		default= True
	)

	TexSky.turbidity= FloatProperty(
		name= "Turbidity",
		description= "TODO",
		min= 2.0,
		max= 100.0,
		soft_min= 2.0,
		soft_max= 10.0,
		precision= 3,
		default= 3.0
	)

	TexSky.ozone= FloatProperty(
		name= "Ozone",
		description= "TODO",
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		precision= 3,
		default= 0.35
	)

	TexSky.water_vapour= FloatProperty(
		name= "Water vapour",
		description= "TODO",
		min= 0.0,
		max= 10.0,
		soft_min= 0.0,
		soft_max= 2.0,
		precision= 3,
		default= 2
	)

	TexSky.intensity_multiplier= FloatProperty(
		name= "Intensity mult.",
		description= "TODO",
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		precision= 3,
		default= 1
	)

	TexSky.size_multiplier= FloatProperty(
		name= "Size mult.",
		description= "TODO",
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		precision= 3,
		default= 1
	)

	TexSky.invisible= BoolProperty(
		name= "Invisible",
		description= "TODO",
		default= False
	)

	TexSky.sun= StringProperty(
		name= "Sun",
		description= "Sun lamp",
		default= ""
	)

	TexSky.horiz_illum= FloatProperty(
		name= "Horiz illumination",
		description= "TODO",
		min= 0.0,
		max= 100000.0,
		soft_min= 0.0,
		soft_max= 10000.0,
		precision= 0,
		default= 25000
	)

	TexSky.sky_model= EnumProperty(
		name= "Sky model",
		description= "Sky model",
		items= (
			('CIEOVER',"CIE Overcast",""),
			('CIECLEAR',"CIE Clear",""),
			('PREETH',"Preetham et al.","")
		),
		default= 'PREETH'
	)


def write(bus):
	SKY_MODEL= {
		'CIEOVER'  : 2,
		'CIECLEAR' : 1,
		'PREETH'   : 0
	}

	scene= bus['scene']
	ofile= bus['files']['textures']

	slot=     bus['mtex']['slot']
	texture=  bus['mtex']['texture']
	tex_name= bus['mtex']['name']

	TexSky= getattr(texture.vray, PLUG)

	# Find Sun lamp
	sun_light= None
	if TexSky.auto_sun:
		for ob in [ob for ob in scene.objects if ob.type == 'LAMP']:
			if ob.data.type == 'SUN' and ob.data.vray.direct_type == 'SUN':
				sun_light= get_name(ob,prefix='LA')
				break
	else:
		if TexSky.sun:
			sun_light= get_name(get_data_by_name(scene, 'objects', TexSky.sun), prefix='LA')

	# Write output
	ofile.write("\n%s %s {"%(PLUG, tex_name))
	for param in PARAMS:
		if param == 'sky_model':
			ofile.write("\n\t%s= %s;"%(param, SKY_MODEL[TexSky.sky_model]))
		elif param == 'sun':
			if sun_light is None:
				continue
			ofile.write("\n\t%s= %s;"%(param, sun_light))
		else:
			ofile.write("\n\t%s= %s;"%(param, a(scene, getattr(TexSky, param))))
	ofile.write("\n}\n")

	return tex_name



'''
  GUI
'''
class VRAY_TP_TexSky(ui.VRayTexturePanel, bpy.types.Panel):
	bl_label = NAME

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		tex= context.texture
		if not tex:
			return False
		vtex= tex.vray
		engine= context.scene.render.engine
		return ((tex and tex.type == 'VRAY' and vtex.type == ID) and (engine in __class__.COMPAT_ENGINES))
	
	def draw(self, context):
		tex= context.texture
		TexSky= getattr(tex.vray, PLUG)
		
		wide_ui= context.region.width > ui.narrowui

		layout= self.layout

		split= layout.split()
		col= split.column()
		col.prop(TexSky, 'auto_sun')

		split= layout.split()
		split.active= not TexSky.auto_sun
		col= split.column()
		col.prop(TexSky, 'sky_model')
		if not TexSky.auto_sun:
			col.prop_search(TexSky, 'sun', context.scene, 'objects')

		split= layout.split()
		split.active= not TexSky.auto_sun
		col= split.column()
		col.prop(TexSky, 'turbidity')
		col.prop(TexSky, 'ozone')
		col.prop(TexSky, 'intensity_multiplier')
		col.prop(TexSky, 'size_multiplier')
		if wide_ui:
			col= split.column()
		col.prop(TexSky, 'invisible')
		col.prop(TexSky, 'horiz_illum')
		col.prop(TexSky, 'water_vapour')


def GetRegClasses():
	return (
		VRAY_TP_TexSky,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
