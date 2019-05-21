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

ID=   'SettingsRaycaster'

NAME= 'Raycaster'
DESC= "Raycaster options"

PARAMS= (
	'maxLevels',
	'minLeafSize',
	'faceLevelCoef',
	'dynMemLimit',
	'embreeUse',
	'embreeUseMB',
	'embreeHighPrec',
	'embreeLowMemory',
	'embreeRayPackets',
)


def add_properties(rna_pointer):
	class SettingsRaycaster(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(SettingsRaycaster)

	rna_pointer.SettingsRaycaster= PointerProperty(
		name= "Raycaster",
		type=  SettingsRaycaster,
		description= "Raycaster settings"
	)

	SettingsRaycaster.maxLevels= IntProperty(
		name= "Max. tree depth",
		description= "Maximum BSP tree depth",
		min= 50,
		max= 100,
		default= 80
	)

	SettingsRaycaster.minLeafSize= FloatProperty(
		name= "Min. leaf size",
		description= "Minimum size of a leaf node",
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= 0.0
	)

	SettingsRaycaster.faceLevelCoef= FloatProperty(
		name= "Face/level",
		description= "Maximum amount of triangles in a leaf node",
		min= 0.0,
		max= 10.0,
		soft_min= 0.0,
		soft_max= 10.0,
		default= 1.0
	)

	SettingsRaycaster.dynMemLimit= IntProperty(
		name= "Dynamic memory limit",
		description= "RAM limit for the dynamic raycasters (0 = auto)",
		min= 0,
		max= 100000,
		default= 0
	)

	SettingsRaycaster.embreeUse= BoolProperty(
		name="embreeUse",
		description="Enable/Disable using the embree ray caster",
		default=False
	)
	SettingsRaycaster.embreeUseMB= BoolProperty(
		name="embreeUseMB",
		description="Enable/disable using the embree ray caster for motion blur",
		default=False
	)
	SettingsRaycaster.embreeHighPrec= BoolProperty(
		name="embreeHighPrec",
		description="Enable/disable high precision intersection",
		default=False
	)
	SettingsRaycaster.embreeLowMemory= BoolProperty(
		name="embreeLowMemory",
		description="Try to conserve memory, using potentially slower algorithms",
		default=False
	)
	SettingsRaycaster.embreeRayPackets= BoolProperty(
		name="embreeRayPackets",
		description="Turn on the packet ray casting",
		default=False
	)


def write(bus):
	ofile=  bus['files']['scene']
	scene=  bus['scene']

	rna_pointer= getattr(scene.vray, ID)
	ofile.write("\n%s %s {" % (ID,ID))
	for param in PARAMS:
		value= getattr(rna_pointer, param)
		ofile.write("\n\t%s= %s;"%(param, p(value)))
	ofile.write("\n}\n")
