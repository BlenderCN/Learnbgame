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
ID=   'CameraPhysical'

NAME= 'Physical camera'
DESC= "V-Ray CameraPhysical settings"

PARAMS= (
	'film_width',
	'focal_length',
	'zoom_factor',
	'distortion',
	'distortion_type',
	'f_number',
	'lens_shift',
	'shutter_speed',
	'shutter_angle',
	'shutter_offset',
	'latency',
	'ISO',
	'dof_display_threshold',
	'exposure',
	'vignetting',
	'blades_enable',
	'blades_num',
	'blades_rotation',
	'center_bias',
	'anisotropy',
	'use_dof',
	'use_moblur',
	'subdivs'
	#'lens_file',
	#'horizontal_shift'
)


def add_properties(rna_pointer):
	class CameraPhysical(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(CameraPhysical)

	rna_pointer.CameraPhysical= PointerProperty(
		name= "CameraPhysical",
		type=  CameraPhysical,
		description= "Physical Camera settings"
	)

	CameraPhysical.use= BoolProperty(
		name= "Enable physical camera",
		description= "Enable physical camera",
		default= False
	)

	CameraPhysical.specify_fov= BoolProperty(
		name= "Use FOV",
		description= "Use field of view instead of use the focal length, film width, scale etc",
		default= True
	)

	CameraPhysical.f_number= FloatProperty(
		name= "F-number",
		description= "Determines the width of the camera aperture and, indirectly, exposure",
		min=0.0, max=1000.0,
		soft_min=0.0, soft_max=10.0,
		default= 8.0
	)

	CameraPhysical.white_balance= FloatVectorProperty(
		name= "White balance",
		description= "White balance",
		default= (1.0, 1.0, 1.0),
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		step= 3,
		precision= 3,
		options= {'ANIMATABLE'},
		subtype= 'COLOR',
		size= 3
	)

	CameraPhysical.latency= FloatProperty(
		name="Latency",
		description="CCD matrix latency, in seconds",  # for video camera
		min=0.0, max=100.0,
		soft_min=0.0, soft_max=10.0,
		default=0.0
	)

	CameraPhysical.lens_shift= FloatProperty(
		name="Lens shift",
		description="Shift lenses for 2-point perspective",
		min=-1.0,
		max=1.0,
		soft_min=-1.0,
		soft_max=1.0,
		default=0.0
	)

	CameraPhysical.ISO= FloatProperty(
		name="ISO",
		description="The film power (i.e. sensitivity)",
		min=0.0,
		max=10000.0,
		soft_min=0.0,
		soft_max=100.0,
		default=200.0
	)

	CameraPhysical.shutter_speed= FloatProperty(
		name="Shutter speed",
		description="The shutter speed, in inverse seconds", # for still camera
		min= 1.0,
		max= 10000.0,
		soft_min=0.0,
		soft_max=1000.0,
		default=300.0
	)

	CameraPhysical.focal_length= FloatProperty(
		name="Focal length",
		description="Specifies the equivalen focal length of the camera lens",
		min=0.0,
		max=200.0,
		soft_min=0.0,
		soft_max=10.0,
		default=40.0
	)

	CameraPhysical.dof_display_threshold= FloatProperty(
		name="DOF threshold",
		description="Display threshold for depth-of-field",
		min=0.0,
		max=1.0,
		soft_min=0.0,
		soft_max=1.0,
		default=0.0
	)

	CameraPhysical.distortion= FloatProperty(
		name="Distortion",
		description="Specifies the distortion coefficient for the camera lens",
		min=-1.0,
		max=1.0,
		soft_min=0.0,
		soft_max=1.0,
		default=0.0
	)

	CameraPhysical.distortion_type= IntProperty(
		name="Distortion type",
		description="",
		min=0,
		max=2,
		default=0
	)

	CameraPhysical.zoom_factor= FloatProperty(
		name="Zoom factor",
		description="Zoom factor",
		min=0.0,
		max=10.0,
		soft_min=0.0,
		soft_max=10.0,
		default=1.0
	)

	CameraPhysical.film_width= FloatProperty(
		name="Film width",
		description="Specifies the horizontal size of the film gate in milimeters",
		min=0.0,
		max=200.0,
		soft_min=0.0,
		soft_max=10.0,
		default=36.0
	)

	CameraPhysical.vignetting= FloatProperty(
		name="Vignetting",
		description="The optical vignetting effect of real-world cameras",
		min=0.0,
		max=100.0,
		soft_min=0.0,
		soft_max=2.0,
		default=1.0
	)

	CameraPhysical.shutter_angle= FloatProperty(
		name="Shutter angle",
		description="Shutter angle (in degrees)", # for cinema camera
		min=0.0,
		max=1000.0,
		soft_min=0.0,
		soft_max=10.0,
		default=180.0
	)

	CameraPhysical.shutter_offset= FloatProperty(
		name="Shutter offset",
		description="Shutter offset (in degress)", # for cinema camera
		min=0.0,
		max=1000.0,
		soft_min=0.0,
		soft_max=10.0,
		default=0.0
	)

	CameraPhysical.exposure= BoolProperty(
		name="Exposure",
		description="When this option is on, the f-number, Shutter speed and ISO settings will affect the image brightness",
		default= True
	)

	CameraPhysical.guess_lens_shift= BoolProperty(
		name= "Auto lens shift",
		description= "Calculate lens shift automatically",
		default= False
	)

	CameraPhysical.type= EnumProperty(
		name="Type",
		description="The type of the physical camera",
		items=(
			('STILL',     "Still",     ""),
			('CINEMATIC', "Cinematic", ""),
			('VIDEO',     "Video",     "")
		),
		default= 'STILL'
	)

	CameraPhysical.blades_enable= BoolProperty(
		name="Bokeh effects",
		description="Defines the shape of the camera aperture",
		default= False
	)

	CameraPhysical.blades_num= IntProperty(
		name="Blades number",
		description="Number of blades",
		min=1,
		max=100,
		default=5
	)

	CameraPhysical.blades_rotation= FloatProperty(
		name="Blades rotation",
		description="Defines the rotation of the blades",
		min=0.0,
		max=360.0,
		soft_min=0.0,
		soft_max=10.0,
		default=0.0
	)

	CameraPhysical.center_bias= FloatProperty(
		name="Center bias",
		description="Defines a bias shape for the bokeh effects",
		min=0.0,
		max=100.0,
		soft_min=0.0,
		soft_max=10.0,
		default=0.0
	)

	CameraPhysical.anisotropy= FloatProperty(
		name="Anisotropy",
		description="Allows stretching of the bokeh effect horizontally or vertically to simulate anamorphic lenses",
		min=0.0,
		max=1.0,
		soft_min=0.0,
		soft_max=1.0,
		default=0.0
	)

	CameraPhysical.use_dof= BoolProperty(
		name="Depth of field",
		description="Turns on depth of field sampling",
		default= False
	)

	CameraPhysical.use_moblur= BoolProperty(
		name="Motion blur",
		description="Turns on motion blur sampling",
		default= False
	)

	CameraPhysical.subdivs= IntProperty(
		name="Subdivs",
		description="The number of samples for calculating depth of field and/or motion blur",
		min=1,
		max=100,
		default=6
	)


def get_lens_shift(ob):
	shift= 0.0
	constraint= None
	if len(ob.constraints) > 0:
		for co in ob.constraints:
			if co.type in ('TRACK_TO','DAMPED_TRACK','LOCKED_TRACK'):
				constraint= co
				break
	if constraint:
		constraint_ob= constraint.target
		if constraint_ob:
			z_shift= ob.matrix_world.to_translation()[2] - constraint_ob.matrix_world.to_translation()[2]
			l= get_distance(ob, constraint_ob)
			shift= -1.0 * z_shift / l
	else:
		rx= ob.rotation_euler[0]
		lsx= rx - math.pi / 2
		if math.fabs(lsx) > 0.0001:
			shift= math.tan(lsx)
		if math.fabs(shift) > math.pi:
			shift= 0.0
	return shift


def write(bus):
	TYPE= {
		'STILL':     0,
		'CINEMATIC': 1,
		'VIDEO':     2,
	}

	ofile=  bus['files']['camera']
	scene=  bus['scene']
	camera= bus['camera']

	VRayCamera=     camera.data.vray
	CameraPhysical= VRayCamera.CameraPhysical

	fov= VRayCamera.fov if VRayCamera.override_fov else camera.data.angle

	aspect= scene.render.resolution_x / scene.render.resolution_y

	if aspect < 1.0:
		fov= fov * aspect

	focus_distance= camera.data.dof_distance
	if camera.data.dof_object:
		focus_distance= get_distance(camera, camera.data.dof_object)

	if focus_distance < 0.001:
		focus_distance= 200.0

	if CameraPhysical.use:
		ofile.write("\n// Camera: %s" % (camera.name))
		ofile.write("\nCameraPhysical PhysicalCamera {")
		ofile.write("\n\ttype= %d;" % TYPE[CameraPhysical.type])
		ofile.write("\n\tspecify_focus= 1;")
		ofile.write("\n\tfocus_distance= %s;" % a(scene,focus_distance))
		ofile.write("\n\tspecify_fov= %i;" % CameraPhysical.specify_fov)
		ofile.write("\n\tfov= %s;" % a(scene,fov))
		ofile.write("\n\twhite_balance= %s;" % a(scene, CameraPhysical.white_balance))

		for param in PARAMS:
			if param == 'lens_shift' and CameraPhysical.guess_lens_shift:
				value= get_lens_shift(camera)
			else:
				value= getattr(CameraPhysical,param)
			ofile.write("\n\t%s= %s;"%(param, a(scene,value)))

		ofile.write("\n\thorizontal_offset= %s;" % a(scene, -camera.data.shift_x))
		ofile.write("\n\tvertical_offset= %s;"   % a(scene, -camera.data.shift_y))
		ofile.write("\n}\n")

