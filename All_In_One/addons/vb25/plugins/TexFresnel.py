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

ID=   'TexFresnel'
NAME= 'Fresnel'
PLUG= 'TexFresnel'
DESC= "TODO."
PID=  2

PARAMS= (
	'fresnel_ior',
	'refract_ior',
	'white_color',
	'black_color'
)


def add_properties(VRayTexture):
	class TexFresnel(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(TexFresnel)

	VRayTexture.TexFresnel= PointerProperty(
		name= "TexFresnel",
		type=  TexFresnel,
		description= "V-Ray TexFresnel settings"
	)

	TexFresnel.fresnel_ior= FloatProperty(
		name= "Fresnel IOR",
		description= "Fresnel ior",
		min= 0.0,
		max= 10.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.55
	)

	TexFresnel.refract_ior= FloatProperty(
		name= "Refract IOR",
		description= "Refraction ior of the underlying surface; this is ignored if the surface has a volume shader (the volume IOR is used)",
		min= 0.0,
		max= 10.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.55
	)

	TexFresnel.white_color= FloatVectorProperty(
		name= "Front color",
		description= "Refraction (front) color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0.0,0.0,0.0)
	)

	TexFresnel.white_color_tex= StringProperty(
		name= "Front texture",
		description= "Front texture",
		default= ""
	)

	TexFresnel.black_color= FloatVectorProperty(
		name= "Side color",
		description= "Reflection (side) color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (1.0,1.0,1.0)
	)

	TexFresnel.black_color_tex= StringProperty(
		name= "Side texture",
		description= "Side texture",
		default= ""
	)



def write(bus):
	scene= bus['scene']
	ofile= bus['files']['textures']

	slot=     bus['mtex']['slot']
	texture=  bus['mtex']['texture']
	tex_name= bus['mtex']['name']

	TexFresnel= getattr(texture.vray, PLUG)

	mapped_keys= ('black_color', 'white_color')
	mapped_params= write_sub_textures(bus,
									  TexFresnel,
									  [key+'_tex' for key in mapped_keys])

	ofile.write("\n%s %s {"%(PLUG, tex_name))

	for param in PARAMS:
		if param in mapped_keys and param+'_tex' in mapped_params:
			value= mapped_params[param+'_tex']

		else:
			value= getattr(TexFresnel, param)

		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))

	ofile.write("\n}\n")

	return tex_name



'''
  GUI
'''
class VRAY_TP_TexFresnel(ui.VRayTexturePanel, bpy.types.Panel):
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
		wide_ui= context.region.width > ui.narrowui
		layout= self.layout
		
		tex= context.texture
		TexFresnel= tex.vray.TexFresnel
		
		split= layout.split()
		col= split.column(align= True)
		col.prop(TexFresnel, 'white_color')
		col.prop_search(TexFresnel, 'white_color_tex',
						bpy.data, 'textures',
						text= "")
		if wide_ui:
			col= split.column(align= True)
		col.prop(TexFresnel, 'black_color')
		col.prop_search(TexFresnel, 'black_color_tex',
						bpy.data, 'textures',
						text= "")

		layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(TexFresnel, 'fresnel_ior')
		if wide_ui:
			col= split.column()
		col.prop(TexFresnel, 'refract_ior')


def GetRegClasses():
	return (
		VRAY_TP_TexFresnel,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
