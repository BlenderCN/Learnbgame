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
from vb25.utils import *
from vb25.ui.ui import *


def LampCouldBeVisible(lamp):
	if lamp.type == 'AREA':
		return True
	if lamp.type == 'POINT':
		if lamp.vray.radius:
			return True
		return False
	if lamp.type == 'HEMI':
		return True
	return False


class VRAY_DP_context_lamp(VRayLampPanel, bpy.types.Panel):
	bl_label       = ""
	bl_options     = {'HIDE_HEADER'}

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	def draw(self, context):
		layout= self.layout

		ob= context.object
		lamp= context.lamp
		space= context.space_data
		wide_ui= context.region.width > narrowui

		if wide_ui:
			split= layout.split(percentage=0.65)
			if ob:
				split.template_ID(ob, 'data')
				split.separator()
			elif lamp:
				split.template_ID(space, 'pin_id')
				split.separator()
		else:
			if ob:
				layout.template_ID(ob, 'data')
			elif lamp:
				layout.template_ID(space, 'pin_id')

		if wide_ui:
			layout.prop(lamp, 'type', expand=True)
		else:
			layout.prop(lamp, 'type')


class VRAY_DP_light(VRayLampPanel, bpy.types.Panel):
	bl_label       = "Lamp"

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	def draw(self, context):
		wide_ui= context.region.width > narrowui
		layout= self.layout

		ob= context.object
		lamp= context.lamp
		VRayLamp= lamp.vray

		split= layout.split()
		col= split.column()
		if not ((lamp.type == 'SUN' and VRayLamp.direct_type == 'SUN') or (lamp.type == 'AREA' and VRayLamp.lightPortal != 'NORMAL')):
			col.row().prop(VRayLamp, 'color_type', expand=True)
			if wide_ui:
				col= split.column()
			if VRayLamp.color_type == 'RGB':
				sub= col.row(align= True)
				sub.prop(lamp, 'color', text="")
				sub.operator('vray.set_kelvin_color', text="", icon= 'COLOR', emboss= False).data_path= "object.data.color"
			else:
				col.prop(VRayLamp, 'temperature', text="K")

			layout.separator()

		split= layout.split()
		col= split.column()
		if lamp.type == 'AREA':
			col.prop(VRayLamp,'lightPortal', text="Mode")
		if not ((lamp.type == 'SUN' and VRayLamp.direct_type == 'SUN') or (lamp.type == 'AREA' and VRayLamp.lightPortal != 'NORMAL')):
			col.prop(VRayLamp,'units', text="Units")
		if not ((lamp.type == 'SUN' and VRayLamp.direct_type == 'SUN') or (lamp.type == 'AREA' and VRayLamp.lightPortal != 'NORMAL')):
			col.prop(VRayLamp,'intensity', text="Intensity")
		col.prop(VRayLamp,'subdivs')
		col.prop(VRayLamp,'causticSubdivs', text="Caustics")
		col.prop(VRayLamp,'causticMult', text="Caustics Mult")

		if wide_ui:
			col= split.column()

		col.prop(VRayLamp,'enabled', text="On")
		if LampCouldBeVisible(lamp):
			col.prop(VRayLamp,'invisible')
		col.prop(VRayLamp,'affectDiffuse')
		col.prop(VRayLamp,'affectSpecular')
		col.prop(VRayLamp,'affectReflections')
		col.prop(VRayLamp,'noDecay')

		if(lamp.type == 'AREA'):
			col.prop(VRayLamp,'doubleSided')

		if((lamp.type == 'AREA') or (lamp.type == 'POINT' and VRayLamp.radius > 0)):
			col.prop(VRayLamp,'storeWithIrradianceMap')


class VRAY_DP_light_shape(VRayLampPanel, bpy.types.Panel):
	bl_label       = "Shape"

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	def draw(self, context):
		wide_ui= context.region.width > narrowui
		layout= self.layout

		ob        = context.object
		lamp      = context.lamp
		vl        = lamp.vray
		VRayLight = lamp.vray
		VRayScene = context.scene.vray

		if lamp.type == 'AREA':
			layout.prop(lamp,'shape', expand=True)
			layout.separator()
			#  use_rect_tex: bool = false
			#  tex_resolution: integer = 512
			#  tex_adaptive: float = 1

		elif lamp.type == 'SUN':
			layout.prop(vl,'direct_type', expand=True)
			layout.separator()

		elif lamp.type == 'SPOT':
			layout.prop(vl,'spot_type', expand=True)
			layout.separator()

		split= layout.split()
		col= split.column()
		if lamp.type == 'AREA':
			if lamp.shape == 'SQUARE':
				col.prop(lamp,'size')
			else:
				col.prop(lamp,'size', text="Size X")
				if wide_ui:
					col= split.column()
				col.prop(lamp,'size_y')

		elif lamp.type == 'POINT':
			col.row().prop(vl, 'omni_type', expand=True)
			col.separator()
			if vl.omni_type == 'OMNI':
				col.prop(vl,'radius')
				if vl.radius > 0:
					col.prop(vl,'sphere_segments')
			else:
				col.prop(vl, 'decay')
				col.prop(vl, 'ambientShade')

		elif lamp.type == 'SUN':
			if vl.direct_type == 'DIRECT':
				col.prop(vl,'fallsize')
			else:
				split= layout.split()
				col= split.column()
				col.prop(vl,'sky_model')

				split= layout.split()
				col= split.column()
				col.prop(vl,'turbidity')
				col.prop(vl,'ozone')
				col.prop(vl,'intensity_multiplier', text= "Intensity")
				col.prop(vl,'size_multiplier', text= "Size")
				if wide_ui:
					col= split.column()
				col.prop(vl,'horiz_illum')
				col.prop(vl,'water_vapour')

				split= layout.split()
				col= split.column()
				col.operator('vray.add_sky', icon='TEXTURE')

		elif lamp.type == 'SPOT':
			if vl.spot_type == 'SPOT':
				col.prop(lamp,'distance')
				col.prop(vl,'decay')
				if wide_ui:
					col= split.column()
				col.prop(lamp,'spot_size', text="Size")
				col.prop(lamp,'spot_blend', text="Blend")
			else:
				col.prop(vl,'ies_file', text="File")
				layout.separator()

			if vl.spot_type == 'IES':
				split= layout.split()
				col= split.column()
				col.prop(vl,'ies_light_shape')
				sub = col.column()
				sub.active = vl.ies_light_shape
				sub.prop(vl,'ies_light_shape_lock', text="Use width")
				if wide_ui:
					col= split.column()
				sub = col.column()
				sub.active = vl.ies_light_shape
				sub.prop(vl,'ies_light_width')
				if not vl.ies_light_shape_lock:
					sub.prop(vl,'ies_light_length')
					sub.prop(vl,'ies_light_height')
				sub.prop(vl,'ies_light_diameter')


		elif lamp.type == 'HEMI':
			split = layout.split()
			col   = split.column()
			col.prop(VRayLight, 'dome_spherical')

			split = layout.split()
			col   = split.column()
			col.prop(VRayLight, 'dome_rayDistanceMode')
			if wide_ui:
				col= split.column()
			if VRayLight.dome_rayDistanceMode:
				col.prop(VRayLight, 'dome_rayDistance')

			layout.separator()

			split = layout.split()
			col   = split.column()
			col.prop(VRayLight, 'tex_resolution')
			if wide_ui:
				col= split.column()
			col.prop(VRayLight, 'tex_adaptive')

			if VRayScene.SettingsCaustics.on:
				split = layout.split()
				col   = split.column()
				col.prop(VRayLight, 'dome_targetRadius')
				if wide_ui:
					col= split.column()
				col.prop(VRayLight, 'dome_emitRadius')


class VRAY_DP_light_shadows(VRayLampPanel, bpy.types.Panel):
	bl_label   = "Shadows"
	bl_options = {'DEFAULT_CLOSED'}

	COMPAT_ENGINES= {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	def draw_header(self, context):
		vl= context.lamp.vray
		self.layout.prop(vl,'shadows', text="")

	def draw(self, context):
		wide_ui= context.region.width > narrowui
		layout= self.layout

		ob= context.object
		lamp= context.lamp
		vl= lamp.vray

		layout.active = vl.shadows

		split= layout.split()
		col= split.column()
		col.prop(vl,'shadowColor', text="")
		if lamp.type == 'SUN' and vl.direct_type == 'DIRECT':
			col.prop(vl,'shadowShape', text="Shape")
		if wide_ui:
			col= split.column()
		col.prop(vl,'shadowBias', text="Bias")

		if lamp.type == 'SPOT':
			if vl.spot_type == 'IES':
				col.prop(vl,'soft_shadows')
			else:
				col.prop(vl,'shadowRadius', text="Radius")
		else:
			if lamp.type in ('POINT','SUN'):
				col.prop(vl,'shadowRadius', text="Radius")




class VRAY_DP_light_advanced(VRayLampPanel, bpy.types.Panel):
	bl_label   = "Advanced"
	bl_options = {'DEFAULT_CLOSED'}

	COMPAT_ENGINES= {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	def draw(self, context):
		wide_ui= context.region.width > narrowui
		layout= self.layout

		ob= context.object
		lamp= context.lamp
		vl= lamp.vray

		split= layout.split()
		col= split.column()
		col.prop(vl,'diffuse_contribution', text="Diffuse cont.")
		col.prop(vl,'specular_contribution', text="Specular cont.")
		col.prop(vl,'cutoffThreshold', text="Cutoff")

		if wide_ui:
			col= split.column()
		col.prop(vl,'nsamples')
		col.prop(vl,'bumped_below_surface_check', text="Bumped surface check")
		col.prop(vl,'ignoreLightNormals')
		col.prop(vl,'areaSpeculars')


class VRAY_DP_include_exclude(VRayLampPanel, bpy.types.Panel):
	bl_label   = "Include / Exclude"
	bl_options = {'DEFAULT_CLOSED'}

	COMPAT_ENGINES= {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	def draw_header(self, context):
		VRayLamp= context.lamp.vray
		self.layout.prop(VRayLamp, 'use_include_exclude', text="")

	def draw(self, context):
		wide_ui= context.region.width > narrowui
		layout= self.layout

		VRayLamp= context.lamp.vray

		layout.active= VRayLamp.use_include_exclude

		split= layout.split()
		col= split.column()
		col.prop(VRayLamp, 'include_exclude', text="")
		col.prop_search(VRayLamp, 'include_objects',  context.scene, 'objects', text="Objects")
		col.prop_search(VRayLamp, 'include_groups',   bpy.data,      'groups',  text="Groups")


def GetRegClasses():
	return (
		VRAY_DP_context_lamp,
		VRAY_DP_light,
		VRAY_DP_light_shape,
		VRAY_DP_light_shadows,
		VRAY_DP_light_advanced,
		VRAY_DP_include_exclude,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
