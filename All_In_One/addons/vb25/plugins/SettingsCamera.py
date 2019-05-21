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


TYPE= 'CAMERA'
ID=   'SettingsCamera'

NAME= 'Camera'
DESC= "V-Ray SettingsCamera settings"

PARAMS= (
)


def add_properties(rna_pointer):
	class SettingsCamera(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(SettingsCamera)

	rna_pointer.SettingsCamera= PointerProperty(
		name= "SettingsCamera",
		type=  SettingsCamera,
		description= "V-Ray camera settings"
	)

	SettingsCamera.type= EnumProperty(
		name= "Type",
		description= "Camera type",
		items=(
			('DEFAULT',            "Default", ""),
			('SPHERIFICAL',        "Spherifical", ""),
			('CYLINDRICAL_POINT',  "Cylindrical (point)", ""),
			('CYLINDRICAL_ORTHO',  "Cylindrical (ortho)", ""),
			('BOX',                "Box", ""),
			('FISH_EYE',           "Fish-eye", ""),
			('WARPED_SPHERICAL',   "Warped spherical", ""),
			('ORTHOGONAL',         "Orthogonal", ""),
			('PINHOLE',            "Pinhole", ""),
		),
		default= 'DEFAULT'
	)

	SettingsCamera.auto_fit= BoolProperty(
		name= "Auto-fit",
		description= "The auto-fit option of the fish-eye camera",
		default= True
	)

	SettingsCamera.height= FloatProperty(
		name= "Height",
		description= "Height of the cylindrical (ortho) camera",
		min=0.0, max=10000.0,
		soft_min=0.0, soft_max=10.0,
		default=400.0
	)

	SettingsCamera.dist= FloatProperty(
		name="Distance",
		description="Distance to the sphere center",
		min=0.0, max=1000.0,
		soft_min=0.0, soft_max=10.0,
		default=2.0
	)

	SettingsCamera.curve= FloatProperty(
		name="Curve",
		description="Controls the way the rendered images is warped",
		min=0.0, max=10.0,
		soft_min=0.0, soft_max=10.0,
		default=1.0
	)


def write(bus):
	TYPE = {
		'DEFAULT':           0,
		'SPHERIFICAL':       1,
		'CYLINDRICAL_POINT': 2,
		'CYLINDRICAL_ORTHO': 3,
		'BOX':               4,
		'FISH_EYE':          5,
		'WARPED_SPHERICAL':  6,
		'ORTHOGONAL':        7,
		'PINHOLE':           8,
	}

	ofile  = bus['files']['scene']
	scene  = bus['scene']
	camera = bus['camera']

	VRayCamera     = camera.data.vray
	SettingsCamera = VRayCamera.SettingsCamera
	CameraPhysical = VRayCamera.CameraPhysical

	fov = VRayCamera.fov if VRayCamera.override_fov else camera.data.angle

	aspect = scene.render.resolution_x / scene.render.resolution_y
	orthoWidth = camera.data.ortho_scale

	if aspect < 1.0:
		fov = fov * aspect
		orthoWidth = float(orthoWidth) * aspect

	ofile.write("\n// Camera: %s" % (camera.name))
	ofile.write("\nSettingsCamera CA%s {" % clean_string(camera.name))
	if camera.data.type == 'ORTHO':
		ofile.write("\n\ttype=0;")
		ofile.write("\n\theight=%s;" % a(scene, orthoWidth))
	else:
		ofile.write("\n\ttype=%i;" % TYPE[SettingsCamera.type])
	ofile.write("\n\tfov=-1;")
	ofile.write("\n}\n")
