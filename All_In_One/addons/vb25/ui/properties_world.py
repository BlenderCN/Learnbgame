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
from vb25.ui.ui import *
from vb25.plugins import *


class VRAY_WP_environment(VRayWorldPanel, bpy.types.Panel):
	bl_label = "Environment"

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	def draw(self, context):
		layout= self.layout

		VRayWorld= context.world.vray

		split= layout.split()
		col= split.column()
		col.label(text="Background:")

		row= layout.row(align=True)
		row.prop(VRayWorld, 'bg_color_mult', text="Mult", slider=True)
		row.prop(VRayWorld, 'bg_color', text="")

		split= layout.split()
		col= split.column()
		col.label(text="Override:")

		split= layout.split()
		col= split.column()
		factor_but(col, VRayWorld, 'gi_override',         'gi_color_mult',         color= 'gi_color',         label= "GI")
		factor_but(col, VRayWorld, 'reflection_override', 'reflection_color_mult', color= 'reflection_color', label= "Reflection")
		factor_but(col, VRayWorld, 'refraction_override', 'refraction_color_mult', color= 'refraction_color', label= "Refraction")

		layout.separator()
		layout.prop(VRayWorld, 'global_light_level', slider= True)


class VRAY_WP_effects(VRayWorldPanel, bpy.types.Panel):
	bl_label   = "Effects"
	bl_options = {'DEFAULT_CLOSED'}

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	def draw_header(self, context):
		VRayScene= context.scene.vray
		self.layout.prop(VRayScene.VRayEffects, 'use', text="")

	def draw(self, context):
		layout= self.layout

		wide_ui= context.region.width > narrowui

		VRayScene= context.scene.vray
		VRayEffects= VRayScene.VRayEffects

		layout.active= VRayEffects.use

		split= layout.split()
		row= split.row()
		row.template_list("VRayListUse", "",
						  VRayEffects, 'effects',
						  VRayEffects, 'effects_selected',
						  rows= 4)
		col= row.column()
		sub= col.row()
		subsub= sub.column(align=True)
		subsub.operator('vray.effect_add',    text="", icon="ZOOMIN")
		subsub.operator('vray.effect_remove', text="", icon="ZOOMOUT")
		sub= col.row()
		subsub= sub.column(align=True)
		subsub.operator("vray.effect_up",   icon='MOVE_UP_VEC',   text="")
		subsub.operator("vray.effect_down", icon='MOVE_DOWN_VEC', text="")

		if VRayEffects.effects_selected >= 0:
			layout.separator()

			effect= VRayEffects.effects[VRayEffects.effects_selected]

			if wide_ui:
				split= layout.split(percentage=0.2)
			else:
				split= layout.split()
			col= split.column()
			col.label(text="Name:")
			if wide_ui:
				col= split.column()
			row= col.row(align=True)
			row.prop(effect, 'name', text="")

			if wide_ui:
				split= layout.split(percentage=0.2)
			else:
				split= layout.split()
			col= split.column()
			col.label(text="Type:")
			if wide_ui:
				col= split.column()
			col.prop(effect, 'type', text="")

			layout.separator()

			# Box border
			box = layout.box()
			box.active = effect.use

			if effect.type == 'FOG':
				PLUGINS['SETTINGS']['SettingsEnvironment'].draw_EnvironmentFog(context, box, effect)

			elif effect.type == 'TOON':
				PLUGINS['SETTINGS']['SettingsEnvironment'].draw_VolumeVRayToon(context, box, effect)

			elif effect.type == 'SFADE':
				PLUGINS['SETTINGS']['SettingsEnvironment'].draw_SphereFade(context, box, effect)


def GetRegClasses():
	return (
		VRAY_WP_environment,
		VRAY_WP_effects,
	)


def register():
	from bl_ui import properties_world
	properties_world.WORLD_PT_context_world.COMPAT_ENGINES.add('VRAY_RENDER')
	del properties_world

	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	from bl_ui import properties_world
	try:
		properties_world.WORLD_PT_context_world.COMPAT_ENGINES.remove('VRAY_RENDER')
	except:
		pass
	del properties_world

	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
