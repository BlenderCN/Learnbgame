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
ID=   'MtlOverride'
PID=   110

NAME= 'Override'
UI=   "Override"
DESC= "MtlOverride settings."

PARAMS= (
)


def add_properties(rna_pointer):
	class MtlOverride(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(MtlOverride)

	rna_pointer.MtlOverride= PointerProperty(
		name= "MtlOverride",
		type=  MtlOverride,
		description= "V-Ray MtlOverride settings"
	)

	MtlOverride.use= BoolProperty(
		name= "Use override material",
		description= "Use override material",
		default= False
	)

	MtlOverride.gi_mtl= StringProperty(
		name= "GI material",
		description= "The gi material",
		default= ""
	)

	MtlOverride.reflect_mtl= StringProperty(
		name= "Reflection material",
		description= "The reflection material",
		default= ""
	)

	MtlOverride.refract_mtl= StringProperty(
		name= "Refraction material",
		description= "The refraction material",
		default= ""
	)

	MtlOverride.shadow_mtl= StringProperty(
		name= "Shadow material",
		description= "The shadow material",
		default= ""
	)

	MtlOverride.environment_override= StringProperty(
		name= "Environment override",
		description= "Environment override texture",
		default= ""
	)

	MtlOverride.environment_priority= IntProperty(
		name= "Environment priority",
		description= "Environment override priority (used when several materials override it along a ray path)",
		min= 0,
		max= 100,
		default= 0
	)

