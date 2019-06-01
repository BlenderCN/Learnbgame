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
ID=   'TexSnow'
PLUG= 'TexSnow'
NAME= 'Snow'
DESC= "TexSnow."
PID=   24

PARAMS= (
	'uvwgen',
	'snow_tex',
	'surface_tex',
	'threshold',
	'depth_decay',
	'thickness',
)


def add_properties(rna_pointer):
	class TexSnow(bpy.types.PropertyGroup):

		# use_3d_mapping
		use_3d_mapping= BoolProperty(
			name= "use 3d mapping",
			description= "",
			default= True
		)

		#  snow_tex: acolor texture
		snow_tex = FloatVectorProperty(
			name= "Snow",
			description= "Color 1",
			subtype= 'COLOR',
			size=4,
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (1,1,1,1)
		)

		snow_tex_tex= StringProperty(
			name= "Snow Texture",
			description= "Snow Texture",
			default= ""
		)

		#  surface_tex: acolor texture
		surface_tex = FloatVectorProperty(
			name= "Surface",
			description= "Surface",
			subtype= 'COLOR',
			size=4,
			min= 0.0,
			max= 1.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= (0,0,0,0)
		)

		surface_tex_tex= StringProperty(
			name= "Surface Texture",
			description= "Surface Texture",
			default= ""
		)
		
		#  threshold: float texture
		threshold= FloatProperty(
			name= "Threshold",
			description= "Threshold",
			min= 0.0,
			max= 1000.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 1
		)

		threshold_tex= StringProperty(
			name= "Threshold Texture",
			description= "Threshold Texture",
			default= ""
		)

		#  depth_decay: float texture
		depth_decay= FloatProperty(
			name= "Depth Decay",
			description= "Depth Decay",
			min= 0.0,
			max= 1000.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 4
		)

		depth_decay_tex= StringProperty(
			name= "Depth Decay Texture",
			description= "Depth Decay Texture",
			default= ""
		)

		#  thickness: float texture
		thickness= FloatProperty(
			name= "Thickness",
			description= "Thickness",
			min= 0.0,
			max= 1000.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 3,
			default= 0.2
		)
		
		thickness_tex= StringProperty(
			name= "Thickness Texture",
			description= "Thickness Texture",
			default= ""
		)

	bpy.utils.register_class(TexSnow)

	rna_pointer.TexSnow= PointerProperty(
		name= "TexSnow",
		type=  TexSnow,
		description= "V-Ray TexSnow settings"
	)


def write(bus):
	scene= bus['scene']
	ofile= bus['files']['textures']

	slot=     bus['mtex']['slot']
	texture=  bus['mtex']['texture']
	tex_name= bus['mtex']['name']

	uvwgen= write_uvwgen(bus)

	TexSnow= getattr(texture.vray, PLUG)

	mapped_keys= ('snow_tex', 'surface_tex', 'threshold', 'depth_decay', 'thickness')
	mapped_params= write_sub_textures(bus,
					  TexSnow,
					  [key+'_tex' for key in mapped_keys])
	
	ofile.write("\n%s %s {"%(PLUG, tex_name))
	for param in PARAMS:
		if param == 'uvwgen':
			value= uvwgen
		elif param in mapped_keys and param+'_tex' in mapped_params:
			value= mapped_params[param+'_tex']
		else:
			value= getattr(TexSnow, param)
		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))
	ofile.write("\n}\n")

	return tex_name

'''
  GUI
'''
class VRAY_TP_TexSnow(ui.VRayTexturePanel, bpy.types.Panel):
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
		TexSnow= getattr(tex.vray, PLUG)

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexSnow, 'snow_tex', text="Color 1")
		col.prop_search(TexSnow, 'snow_tex_tex',
						bpy.data,    'textures',
						text= "")

		if wide_ui:
			col= split.column(align= True)
		col.prop(TexSnow, 'surface_tex', text="Color 2")
		col.prop_search(TexSnow, 'surface_tex_tex',
						bpy.data,    'textures',
						text= "")

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexSnow, 'threshold')
		col.prop_search(TexSnow, 'threshold_tex',
						bpy.data,    'textures',
						text= "")

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexSnow, 'depth_decay')
		col.prop_search(TexSnow, 'depth_decay_tex',
						bpy.data,    'textures',
						text= "")

		split= layout.split()
		col= split.column(align= True)
		col.prop(TexSnow, 'thickness')
		col.prop_search(TexSnow, 'thickness_tex',
						bpy.data,    'textures',
						text= "")


def GetRegClasses():
	return (
		VRAY_TP_TexSnow,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
