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


TYPE= 'SETTINGS'

ID=   'INCLUDER'
NAME= 'Includer'
DESC= "List includes *.vrscene"

PARAMS= (
)

def add_properties(rna_pointer):
	class Includer(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(Includer)

	rna_pointer.Includer= PointerProperty(
		name= "Includes",
		type=  Includer,
		description= "Inclede files *.vrscene"
	)

	Includer.use = BoolProperty(
		name        = "Use Includer",
		description = "Add additional *.vrscene files",
		default     = False
	)

	Includer.setting= BoolProperty(
		name= "",
		description= "Use scene Settings",
		default= True
	)

	Includer.camera= BoolProperty(
		name= "",
		description= "Use camera",
		default= True
	)

	Includer.materials= BoolProperty(
		name= "",
		description= "Use materials",
		default= True
	)

	Includer.environment= BoolProperty(
		name= "",
		description= "Use environment",
		default= True
	)

	Includer.lights= BoolProperty(
		name= "",
		description= "Use lights",
		default= True
	)

	Includer.textures= BoolProperty(
		name= "",
		description= "Use textures",
		default= True
	)

	Includer.colorMapping_standalone= BoolProperty(
		name= "",
		description= "Use Color Mapping standalone",
		default= True
	)

	Includer.geometry= BoolProperty(
		name= "",
		description= "Use scene geometry",
		default= True
	)

	Includer.scene_nodes= BoolProperty(
		name= "",
		description= "Use Vray nodes",
		default= True
	)
	

	class IncluderList(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(IncluderList)

	Includer.nodes= CollectionProperty(
		name= "Scene Name",
		type=  IncluderList,
		description= "Custom name scene"
	)

	Includer.nodes_selected= IntProperty(
		name= "Scene Index",
		default= -1,
		min= -1,
		max= 100
	)

	IncluderList.scene= StringProperty(
		name= "Filepath",
		subtype= 'FILE_PATH',
		description= "Path to a *.vrscene file"
	)

	IncluderList.use= BoolProperty(
		name= "",
		description= "Use scene",
		default= True
	)


