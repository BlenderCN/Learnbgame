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

ID=   'SettingsUnitsInfo'

NAME= 'Units'
DESC= "Units options"

PARAMS= (
	'meters_scale',
	'photometric_scale',
)


def add_properties(rna_pointer):
	class SettingsUnitsInfo(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(SettingsUnitsInfo)

	rna_pointer.SettingsUnitsInfo= PointerProperty(
		name= "Units",
		type=  SettingsUnitsInfo,
		description="Units settings"
	)

	SettingsUnitsInfo.photometric_scale= FloatProperty(
		name= "Photometric scale",
		description= "Photometric scale",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 1.0,
		precision= 4,
		default= 0.001
	)

	SettingsUnitsInfo.meters_scale= FloatProperty(
		name= "Meters scale",
		description= "Meters scale",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1.0
	)

def write(bus):
	ofile=  bus['files']['scene']
	scene=  bus['scene']

	VRayScene= scene.vray
	SettingsUnitsInfo= VRayScene.SettingsUnitsInfo
	
	ofile.write("\nSettingsUnitsInfo SettingsUnitsInfo {")
	# ofile.write("\n\tmeters_scale= %i;" % SettingsUnitsInfo.meters_scale)
	ofile.write("\n\tmeters_scale= %.4f;" % scene.unit_settings.scale_length)
	# ofile.write("\n\tphotometric_scale= %.4f;" % SettingsUnitsInfo.photometric_scale)
	ofile.write("\n\tphotometric_scale= 0.01;")
	ofile.write("\n}\n")

