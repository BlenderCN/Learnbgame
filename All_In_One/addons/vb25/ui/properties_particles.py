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

''' vb modules '''
from vb25.ui.ui import *


class VRAY_PP_hair(VRayParticlePanel, bpy.types.Panel):
	bl_label       = "Fur"
	bl_options     = {'DEFAULT_CLOSED'}

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		return super().poll(context) and context.particle_system.settings.type == 'HAIR'

	def draw(self, context):
		wide_ui= context.region.width > narrowui
		layout= self.layout

		particle_settings= context.particle_system.settings

		VRayFur= particle_settings.vray.VRayFur

		split= layout.split()
		col= split.column()
		col.prop(VRayFur, 'width', text="Fur Width")
		# if wide_ui:
		# 	col= split.column()
		# col.prop(VRayFur, 'make_thinner')
		# if VRayFur.make_thinner:
		# 	col.prop(VRayFur, 'thin_start', text= "Segment", slider= True)


def GetRegClasses():
	return (
		VRAY_PP_hair,
	)


def register():
	from bl_ui import properties_particle
	for member in dir(properties_particle):
		subclass= getattr(properties_particle, member)
		try:
			subclass.COMPAT_ENGINES.add('VRAY_RENDER')
			subclass.COMPAT_ENGINES.add('VRAY_RENDER_PREVIEW')
		except:
			pass
	del properties_particle

	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	from bl_ui import properties_particle
	for member in dir(properties_particle):
		subclass= getattr(properties_particle, member)
		try:
			subclass.COMPAT_ENGINES.remove('VRAY_RENDER')
			subclass.COMPAT_ENGINES.remove('VRAY_RENDER_PREVIEW')
		except:
			pass
	del properties_particle

	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)

	del bpy.types.ParticleSettings.vray
