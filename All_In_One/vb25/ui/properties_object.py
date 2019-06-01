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


''' Python modules '''
import os

''' Blender modules '''
import bpy
from bpy.props import *

''' vb modules '''
from vb25.utils import *
from vb25.ui.ui import *


def engine_poll(cls, context):
	rd= context.scene.render
	return (context.object and (context.object.type not in ('LAMP','CAMERA','ARMATURE'))) and (rd.engine in cls.COMPAT_ENGINES)


class VRAY_OBP_override(VRayObjectPanel, bpy.types.Panel):
	bl_label   = "Override"
	bl_options = {'DEFAULT_CLOSED'}

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		return engine_poll(__class__, context)

	def draw_header(self, context):
		ob= context.object
		plugin= ob.vray.MtlOverride
		self.layout.label(text="", icon='VRAY_LOGO_MONO')
		self.layout.prop(plugin, 'use', text="")

	def draw(self, context):
		wide_ui= context.region.width > narrowui

		ob= context.object

		MtlOverride= ob.vray.MtlOverride

		layout= self.layout
		layout.active= MtlOverride.use

		split= layout.split()
		col= split.column()
		col.prop_search(MtlOverride, 'gi_mtl',      bpy.data, 'materials', text= "GI")
		col.prop_search(MtlOverride, 'reflect_mtl', bpy.data, 'materials', text= "Reflection")
		col.prop_search(MtlOverride, 'refract_mtl', bpy.data, 'materials', text= "Refraction")
		col.prop_search(MtlOverride, 'shadow_mtl',  bpy.data, 'materials', text= "Shadow")

		layout.separator()
		split= layout.split()
		col= split.column()
		col.prop_search(MtlOverride, 'environment_override',  bpy.data, 'textures', text= "Environment")

		layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(MtlOverride, 'environment_priority')


class VRAY_OBP_wrapper(VRayObjectPanel, bpy.types.Panel):
	bl_label = "Wrapper"
	bl_options = {'DEFAULT_CLOSED'}

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		return engine_poll(__class__, context)

	def draw_header(self, context):
		ob= context.object
		plugin= ob.vray.MtlWrapper
		self.layout.label(text="", icon='VRAY_LOGO_MONO')
		self.layout.prop(plugin, 'use', text="")

	def draw(self, context):
		wide_ui= context.region.width > narrowui

		ob= context.object
		plugin= ob.vray.MtlWrapper

		layout= self.layout
		layout.active= plugin.use

		split= layout.split()
		col= split.column()
		col.prop(plugin, 'generate_gi')
		col.prop(plugin, 'receive_gi')
		if wide_ui:
			col= split.column()
		col.prop(plugin, 'generate_caustics')
		col.prop(plugin, 'receive_caustics')

		split= layout.split()
		col= split.column()
		col.prop(plugin, 'gi_quality_multiplier')

		split= layout.split()
		col= split.column()
		col.label(text="Matte properties")

		split= layout.split()
		colL= split.column()
		colL.prop(plugin, 'matte_surface')
		if wide_ui:
			colR= split.column()
		else:
			colR= colL
		colR.prop(plugin, 'alpha_contribution')
		if plugin.matte_surface:
			colR.prop(plugin, 'reflection_amount')
			colR.prop(plugin, 'refraction_amount')
			colR.prop(plugin, 'gi_amount')
			colR.prop(plugin, 'no_gi_on_other_mattes')

			colL.prop(plugin, 'affect_alpha')
			colL.prop(plugin, 'shadows')
			if plugin.shadows:
				colL.prop(plugin, 'shadow_tint_color')
				colL.prop(plugin, 'shadow_brightness')

		split= layout.split()
		col= split.column()
		col.label(text="Miscellaneous")

		split= layout.split()
		col= split.column()
		col.prop(plugin, 'gi_surface_id')
		col.prop(plugin, 'trace_depth')
		if wide_ui:
			col= split.column()
		col.prop(plugin, 'matte_for_secondary_rays')

		layout.prop(plugin, 'generate_render_elements')


class VRAY_OBP_render(VRayObjectPanel, bpy.types.Panel):
	bl_label = "Render"
	bl_options = {'DEFAULT_CLOSED'}

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		return engine_poll(__class__, context) and not context.object.vray.LightMesh.use

	def draw_header(self, context):
		ob= context.object
		plugin= ob.vray.MtlRenderStats
		self.layout.label(text="", icon='VRAY_LOGO_MONO')
		self.layout.prop(plugin, 'use', text="")

	def draw(self, context):
		wide_ui= context.region.width > narrowui

		ob= context.object
		VRayObject= ob.vray
		plugin= VRayObject.MtlRenderStats

		layout= self.layout
		layout.active= plugin.use

		layout.prop(VRayObject, 'fade_radius')

		split= layout.split()
		col= split.column()
		col.prop(plugin, 'visibility', text="Visible")

		split= layout.split()
		col= split.column()
		col.label(text="Visible to:")

		split= layout.split()
		sub= split.column()
		sub.active= plugin.visibility
		sub.prop(plugin, 'camera_visibility', text="Camera")
		sub.prop(plugin, 'gi_visibility', text="GI")
		sub.prop(plugin, 'shadows_visibility', text="Shadows")
		if wide_ui:
			sub= split.column()
			sub.active= plugin.visibility
		sub.prop(plugin, 'reflections_visibility', text="Reflections")
		sub.prop(plugin, 'refractions_visibility', text="Refractions")


class VRAY_OBP_displacement(VRayObjectPanel, bpy.types.Panel):
	bl_label = "Displacement"
	bl_options = {'DEFAULT_CLOSED'}

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		return engine_poll(__class__, context)

	def draw_header(self, context):
		ob= context.object
		VRayObject= ob.vray
		GeomDisplacedMesh= VRayObject.GeomDisplacedMesh
		self.layout.label(text="", icon='VRAY_LOGO_MONO')
		self.layout.prop(GeomDisplacedMesh, 'use', text="")

	def draw(self, context):
		wide_ui= context.region.width > narrowui

		ob= context.object
		VRayObject= ob.vray
		GeomDisplacedMesh= VRayObject.GeomDisplacedMesh

		layout= self.layout
		layout.active= GeomDisplacedMesh.use

		split= layout.split()
		col= split.column()
		col.prop(GeomDisplacedMesh, 'amount_type', text="Amount")
		if GeomDisplacedMesh.amount_type == 'OVER':
			col.prop(GeomDisplacedMesh, 'displacement_amount')
		else:
			col.prop(GeomDisplacedMesh, 'amount_mult')
		col.prop(GeomDisplacedMesh, 'displacement_shift', slider=True)
		col.prop(GeomDisplacedMesh, 'water_level', slider=True)
		col.prop(GeomDisplacedMesh, 'resolution')
		col.prop(GeomDisplacedMesh, 'precision')
		if wide_ui:
			col= split.column()
		col.prop(GeomDisplacedMesh, 'type')
		col.prop(GeomDisplacedMesh, 'keep_continuity')
		col.prop(GeomDisplacedMesh, 'filter_texture')
		if GeomDisplacedMesh.filter_texture:
			col.prop(GeomDisplacedMesh, 'filter_blur')
		col.prop(GeomDisplacedMesh, 'use_bounds')
		if GeomDisplacedMesh.use_bounds:
			sub= col.column(align= True)
			sub.prop(GeomDisplacedMesh, 'min_bound', text="Min", slider= True)
			sub.prop(GeomDisplacedMesh, 'max_bound', text="Max", slider= True)

		split= layout.split()
		col= split.column()
		col.prop(GeomDisplacedMesh, 'use_globals')
		if not GeomDisplacedMesh.use_globals:
			split= layout.split()
			col= split.column()
			col.prop(GeomDisplacedMesh, 'edge_length')
			col.prop(GeomDisplacedMesh, 'max_subdivs')
			if wide_ui:
				col= split.column()
			col.prop(GeomDisplacedMesh, 'view_dep')
			col.prop(GeomDisplacedMesh, 'tight_bounds')


class VRAY_OBP_lightmesh(VRayObjectPanel, bpy.types.Panel):
	bl_label = "Light"
	bl_options = {'DEFAULT_CLOSED'}

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		return engine_poll(__class__, context)

	def draw_header(self, context):
		ob= context.object
		VRayObject= ob.vray
		LightMesh= VRayObject.LightMesh
		self.layout.label(text="", icon='VRAY_LOGO_MONO')
		self.layout.prop(LightMesh, 'use', text="")

	def draw(self, context):
		wide_ui= context.region.width > narrowui

		ob= context.object
		VRayObject= ob.vray
		LightMesh= VRayObject.LightMesh

		layout= self.layout
		layout.active= LightMesh.use

		split= layout.split()
		col= split.column()
		col.row().prop(LightMesh, 'color_type', expand=True)
		if wide_ui:
			col= split.column()
		if LightMesh.color_type == 'RGB':
			sub= col.row(align= True)
			sub.prop(LightMesh, 'color', text="")
			sub.operator('vray.set_kelvin_color', text="", icon= 'COLOR', emboss= False).data_path= "object.vray.LightMesh.color"
		else:
			col.prop(LightMesh, 'temperature', text="K")

		layout.separator()

		split= layout.split()
		col= split.column()
		col.prop(LightMesh, 'lightPortal', text="Mode")
		if LightMesh.lightPortal == 'NORMAL':
			col.prop(LightMesh, 'units', text="Units")
			col.prop(LightMesh, 'intensity', text="Intensity")
		col.prop(LightMesh, 'subdivs')
		col.prop(LightMesh, 'causticSubdivs', text="Caustics")
		if wide_ui:
			col= split.column()
		col.prop(LightMesh, 'enabled', text="On")
		col.prop(LightMesh, 'invisible')
		col.prop(LightMesh, 'affectDiffuse')
		col.prop(LightMesh, 'affectSpecular')
		col.prop(LightMesh, 'affectReflections')
		col.prop(LightMesh, 'noDecay')
		col.prop(LightMesh, 'doubleSided')
		col.prop(LightMesh, 'storeWithIrradianceMap')

		layout.separator()
		layout.prop(LightMesh, 'use_include_exclude')

		if LightMesh.use_include_exclude:
			split= layout.split()
			col= split.column()
			col.prop(LightMesh, 'include_exclude')
			col.prop_search(LightMesh,     'include_objects',
							context.scene, 'objects',
							text="Objects")
			col.prop_search(LightMesh, 'include_groups',
							bpy.data,  'groups',
							text="Groups")


class VRAY_OBP_subdivision(VRayObjectPanel, bpy.types.Panel):
	bl_label   = "Subdivision"
	bl_options = {'DEFAULT_CLOSED'}

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		return engine_poll(__class__, context)

	def draw_header(self, context):
		ob= context.object
		VRayObject= ob.vray
		GeomStaticSmoothedMesh= VRayObject.GeomStaticSmoothedMesh
		self.layout.label(text="", icon='VRAY_LOGO_MONO')
		self.layout.prop(GeomStaticSmoothedMesh, 'use', text="")

	def draw(self, context):
		wide_ui= context.region.width > narrowui

		ob= context.object
		VRayObject= ob.vray
		GeomStaticSmoothedMesh= VRayObject.GeomStaticSmoothedMesh

		layout= self.layout
		layout.active= GeomStaticSmoothedMesh.use

		split= layout.split()
		col= split.column()
		col.prop(GeomStaticSmoothedMesh, 'static_subdiv')
		if wide_ui:
			col= split.column()
		col.prop(GeomStaticSmoothedMesh, 'use_globals')

		if not GeomStaticSmoothedMesh.use_globals:
			layout.separator()
			split= layout.split()
			col= split.column()
			col.prop(GeomStaticSmoothedMesh, 'edge_length')
			col.prop(GeomStaticSmoothedMesh, 'max_subdivs')
			if wide_ui:
				col= split.column()
			col.prop(GeomStaticSmoothedMesh, 'view_dep')



class VRAY_OBP_VRayPattern(VRayObjectPanel, bpy.types.Panel):
	bl_label   = "VRayPattern"
	bl_options = {'DEFAULT_CLOSED'}

	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDERER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		if not engine_poll(__class__, context):
			return False
		if not context.scene.vray.exporter.experimental:
			return False
		return True

	def draw_header(self, context):
		ob = context.object
		VRayObject = ob.vray
		GeomVRayPattern = VRayObject.GeomVRayPattern
		self.layout.label(text="", icon='VRAY_LOGO_MONO')
		self.layout.prop(GeomVRayPattern, 'use', text="")

	def draw(self, context):
		wide_ui = context.region.width > narrowui

		ob = context.object
		VRayObject = ob.vray
		GeomVRayPattern = VRayObject.GeomVRayPattern

		layout = self.layout
		layout.active = GeomVRayPattern.use

		split = layout.split()
		split.label(text="Pattern Object:")
		split.prop_search(GeomVRayPattern, 'pattern_object',
						  context.scene,   'objects',
						  text="")

		layout.separator()

		layout.prop(GeomVRayPattern, 'crop_size')
		layout.operator('vray.pattern_fit', icon='MOD_MESHDEFORM')
		# layout.prop(GeomVRayPattern, 'geometry_bias')
		layout.separator()

		split = layout.split()
		col = split.column()
		col.prop(GeomVRayPattern, 'height')
		if wide_ui:
			col = split.column()
		col.prop(GeomVRayPattern, 'shift')

		layout.separator()

		layout.prop(GeomVRayPattern, 'use_real_world')
		split = layout.split()
		col = split.column()
		col.prop(GeomVRayPattern, 'tiling_u', text="U")
		if wide_ui:
			col = split.column()
		col.prop(GeomVRayPattern, 'tiling_v', text="V")

		layout.label(text="Polygon ID:")
		split = layout.split()
		col = split.column()
		col.prop(GeomVRayPattern, 'polygon_id_from', text="From")
		if wide_ui:
			col = split.column()
		col.prop(GeomVRayPattern, 'polygon_id_to', text="To")

		layout.label(text="Random Segment Count:")
		split = layout.split()
		col = split.column()
		col.prop(GeomVRayPattern, 'random_segment_u', text="U")
		if wide_ui:
			col = split.column()
		col.prop(GeomVRayPattern, 'random_segment_v', text="V")

		layout.prop(GeomVRayPattern, 'random_segment_seed')

		layout.separator()

		split = layout.split()
		col = split.column()
		col.prop(GeomVRayPattern, 'render_base_object')
		if wide_ui:
			col = split.column()
		col.prop(GeomVRayPattern, 'render_pattern_object')


def GetRegClasses():
	return (
		VRAY_OBP_override,
		VRAY_OBP_wrapper,
		VRAY_OBP_render,
		VRAY_OBP_displacement,
		VRAY_OBP_lightmesh,
		VRAY_OBP_subdivision,
		VRAY_OBP_VRayPattern,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
