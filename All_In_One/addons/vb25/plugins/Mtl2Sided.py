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


TYPE= 'MATERIAL'
ID=   'Mtl2Sided'

NAME= 'Mtl2Sided'
UI=   "Two-sided"
DESC= "Mtl2Sided settings."

PARAMS= (
)


def add_properties(rna_pointer):
	class Mtl2Sided(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(Mtl2Sided)

	rna_pointer.Mtl2Sided= PointerProperty(
		name= "Mtl2Sided",
		type=  Mtl2Sided,
		description= "V-Ray Mtl2Sided settings"
	)

	Mtl2Sided.use= BoolProperty(
		name= "Two sided material",
		description= "Simple \"Two sided\" material. Use nodes for advanced control",
		default= False
	)

	Mtl2Sided.back= StringProperty(
		name= "Back material",
		description= "Back material. Same material if nothing is set",
		default= ""
	)

	Mtl2Sided.translucency_tex= StringProperty(
		name= "Back material",
		description= "Back material",
		default= ""
	)

	Mtl2Sided.control= EnumProperty(
		name= "Control",
		description= "Translucency type",
		items= (
			('SLIDER',  "Slider",  "."),
			('COLOR',   "Color",   "."),
			('TEXTURE', "Texture", ".")
		),
		default= 'SLIDER'
	)

	Mtl2Sided.translucency_tex_mult= FloatProperty(
		name= "Translucency texture multiplier",
		description= "Translucency texture multiplier",
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		precision= 3,
		default= 1.0
	)

	Mtl2Sided.translucency_color= FloatVectorProperty(
		name= "Translucency color",
		description= "Translucency between front and back",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0.5,0.5,0.5)
	)

	Mtl2Sided.translucency_slider= FloatProperty(
		name= "Translucency",
		description= "Translucency between front and back",
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		precision= 3,
		default= 0.5
	)

	Mtl2Sided.force_1sided= BoolProperty(
		name= "Force one-sided",
		description= "Make the sub-materials one-sided",
		default= True
	)

