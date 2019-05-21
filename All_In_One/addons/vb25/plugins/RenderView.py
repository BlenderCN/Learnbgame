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
ID=   'RenderView'

NAME= 'Render view'
DESC= "Render view settings."

PARAMS= (
)


def add_properties(rna_pointer):
	class RenderView(bpy.types.PropertyGroup):
		clip_near = BoolProperty(
			name = "Clip Near",
			description = "Clip near",
			default = False
		)

		clip_far = BoolProperty(
			name = "Clip Far",
			description = "Clip far",
			default = False
		)
	bpy.utils.register_class(RenderView)

	rna_pointer.RenderView= PointerProperty(
		name= "RenderView",
		type=  RenderView,
		description= "V-Ray RenderView settings"
	)


def write(bus):
	ofile  = bus['files']['camera']
	scene  = bus['scene']
	camera = bus['camera']

	VRayScene = scene.vray
	VRayBake  = VRayScene.VRayBake
	RTEngine  = VRayScene.RTEngine

	VRayCamera     = camera.data.vray
	RenderView     = VRayScene.RenderView
	SettingsCamera = VRayCamera.SettingsCamera

	if not VRayBake.use:
		fov = VRayCamera.fov if VRayCamera.override_fov else camera.data.angle

		aspect = float(scene.render.resolution_x) / float(scene.render.resolution_y)
		orthoWidth = camera.data.ortho_scale

		if aspect < 1.0:
			fov        = fov * aspect
			orthoWidth = float(orthoWidth) * aspect

		tm = camera.matrix_world.normalized()

		ofile.write("\n// Camera: %s" % (camera.name))
		ofile.write("\nRenderView CameraView {")
		ofile.write("\n\ttransform=%s;" % a(scene, transform(tm)))
		ofile.write("\n\tfov=%s;" % a(scene, fov))
		if SettingsCamera.type not in ('SPHERIFICAL','BOX'):
			ofile.write("\n\tclipping=%i;" % (RenderView.clip_near or RenderView.clip_far))
			if RenderView.clip_near:
				ofile.write("\n\tclipping_near=%s;" % a(scene, camera.data.clip_start))
			if RenderView.clip_far:
				ofile.write("\n\tclipping_far=%s;" % a(scene, camera.data.clip_end))
		if camera.data.type == 'ORTHO':
			ofile.write("\n\torthographic=1;")
			ofile.write("\n\torthographicWidth=%s;" % a(scene, orthoWidth))
		ofile.write("\n}\n")
