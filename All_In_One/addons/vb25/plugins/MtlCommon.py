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
from vb25.ui import ui
from vb25.plugins import *


TYPE= 'MATERIAL'
ID=   'Material'

NAME= 'General material setings'
DESC= "General V-Ray material settings."


PARAMS= (
)


def add_properties(rna_pointer):
	material_types= gen_material_menu_items(PLUGINS['BRDF'])
	
	rna_pointer.type= EnumProperty(
		name= "Type",
		description= "Material type",
		items= (tuple(material_types)),
		default= material_types[0][0]
	)

	rna_pointer.material_id_number= IntProperty(
		name= "Material ID",
		description= "Material ID",
		min= 0,
		max= 1024,
		soft_min= 0,
		soft_max= 10,
		default= 0
	)

	rna_pointer.material_id_color= FloatVectorProperty(
		name= "Color",
		description= "Material ID color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (1.0,1.0,1.0)
	)

	rna_pointer.round_edges = BoolProperty(
		name        = "Round edges",
		description = "Round edges",
		default     = False
	)

	rna_pointer.radius = FloatProperty(
		name        = "Rounding radius",
		description = "Rounding radius",
		precision   = 3,
		min         = 0.0,
		max         = 100.0,
		soft_min    = 0.0,
		soft_max    = 1.0,
		default     = 0.0
	)
