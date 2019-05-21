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


TYPE = 'CAMERA'
ID   = 'SettingsMotionBlur'

NAME = 'Motion Blur'
DESC = "V-Ray SettingsMotionBlur settings."

PARAMS = (
	'on',
	'geom_samples',
	'low_samples',
	'duration',
	'subdivs',
	'bias',
	'shutter_efficiency',
	'interval_center',
	'camera_motion_blur',
)


def add_properties(rna_pointer):
	class SettingsMotionBlur(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(SettingsMotionBlur)

	rna_pointer.SettingsMotionBlur= PointerProperty(
		name= "SettingsMotionBlur",
		type=  SettingsMotionBlur,
		description= "Camera's Motion Blur settings"
	)

	SettingsMotionBlur.on= BoolProperty(
		name="Motion blur",
		description="Turns motion blur on",
		default= False
	)

	SettingsMotionBlur.interval_center= FloatProperty(
		name="Interval center",
		description="Specifies the middle of the motion blur interval with respect to the frame",
		min=0.0, max=1.0,
		soft_min=0.0, soft_max=1.0,
		default=0.5
	)

	SettingsMotionBlur.duration= FloatProperty(
		name="Duration",
		description="Specifies the duration, in frames, during which the camera shutter is open",
		min=1.0, max=100.0,
		soft_min=1.0, soft_max=10.0,
		default=2.0
	)

	SettingsMotionBlur.bias= FloatProperty(
		name="Bias",
		description="This controls the bias of the motion blur effect",
		min=0.0, max=1.0,
		soft_min=0.0, soft_max=1.0,
		default=0.0
	)

	SettingsMotionBlur.shutter_efficiency= FloatProperty(
		name="Shutter Efficiency",
		description="Shutter efficiency",
		min=0.0, max=10.0,
		soft_min=0.0, soft_max=1.0,
		default=1.0
	)

	SettingsMotionBlur.subdivs= IntProperty(
		name="Subdivs",
		description="Determines the quality of the motion blur",
		min=1, max=100,
		default=6
	)

	SettingsMotionBlur.geom_samples= IntProperty(
		name="Geometry Samples",
		description="This determines the number of geometry segments used to approximate motion blur",
		min=1, max=100,
		default=2
	)

	SettingsMotionBlur.low_samples= IntProperty(
		name="Prepass Samples",
		description="This controls how many samples in time will be computed during irradiance map calculations",
		min=1, max=100,
		default=1
	)

	SettingsMotionBlur.camera_motion_blur= BoolProperty(
		name="Camera Motion Blur",
		description="Use camera motion blur",
		default=True
	)


def write(bus):
	ofile  = bus['files']['scene']
	scene  = bus['scene']
	camera = bus['camera']

	VRayCamera         = camera.data.vray
	SettingsMotionBlur = VRayCamera.SettingsMotionBlur

	if SettingsMotionBlur.on:
		ofile.write("\n%s %s {" % (ID,ID))
		for param in PARAMS:
			value = getattr(SettingsMotionBlur, param)
			ofile.write("\n\t%s= %s;"%(param, p(value)))
		ofile.write("\n}\n")
