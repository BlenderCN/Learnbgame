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
from vb25.shaders import *
from vb25.ui import ui


TYPE= 'CAMERA'
ID=   'SettingsCameraDof'

NAME= 'Depth of field'
DESC= "V-Ray SettingsCameraDof settings."

PARAMS= (
)


def add_properties(rna_pointer):
	class SettingsCameraDof(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(SettingsCameraDof)

	rna_pointer.SettingsCameraDof= PointerProperty(
		name= "SettingsCameraDof",
		type=  SettingsCameraDof,
		description= "Camera's DoF settings"
	)

	SettingsCameraDof.on= BoolProperty(
		name= "DOF",
		description= "Use depth of field",
		default= False
	)

	SettingsCameraDof.sides_on= BoolProperty(
		name="This option allows you to simulate the polygonal shape of the aperture of real-world cameras.",
		description="Enable Bokeh effects",
		default= False
	)

	SettingsCameraDof.sides_num= IntProperty(
		name="Number",
		description="Number of sides",
		min=1, max=100,
		default=5
	)

	SettingsCameraDof.subdivs= IntProperty(
		name="Subdivs",
		description="Controls the quality of the DOF effect",
		min=1, max=100,
		default=8
	)

	SettingsCameraDof.anisotropy= FloatProperty(
		name="Anisotropy",
		description="This allows the stretching of the bokeh effect horizontally or vertically",
		min=0.0, max=1.0,
		soft_min=0.0, soft_max=1.0,
		default=0.0
	)

	SettingsCameraDof.focal_dist= FloatProperty(
		name="Focal distance",
		description="Determines the distance from the camera at which objects will be in perfect focus",
		min=0.0, max=1000.0,
		soft_min=0.0, soft_max=10.0,
		default=200.0
	)

	SettingsCameraDof.aperture= FloatProperty(
		name="Aperture",
		description="The size of the virtual camera aperture, in world units",
		min=0.0, max=100.0,
		soft_min=0.0, soft_max=10.0,
		default=5.0
	)

	SettingsCameraDof.center_bias= FloatProperty(
		name="Center bias",
		description="This determines the uniformity of the DOF effect",
		min=0.0, max=100.0,
		soft_min=0.0, soft_max=10.0,
		default=0.0
	)

	SettingsCameraDof.rotation= FloatProperty(
		name="Rotation",
		description="Specifies the orientation of the aperture shape",
		min=0.0, max=10.0,
		soft_min=0.0, soft_max=10.0,
		default=0.0
	)

