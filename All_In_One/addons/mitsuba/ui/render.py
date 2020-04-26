# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy

from bl_ui.properties_render import RenderButtonsPanel
from extensions_framework.ui import property_group_renderer

from .. import MitsubaAddon

class MitsubaRenderPanel(RenderButtonsPanel, property_group_renderer):
	'''
	Base class for render engine settings panels
	'''
	
	COMPAT_ENGINES = { 'MITSUBA_RENDER' }

@MitsubaAddon.addon_register_class
class MitsubaRender_PT_output(MitsubaRenderPanel):
	bl_label = "Output"
	COMPAT_ENGINES = {'MITSUBA_RENDER'}
	
	display_property_groups = [
		( ('scene',) )
	]
	
	def draw(self, context):
		layout = self.layout
		
		rd = context.scene.render
		
		layout.prop(rd, "filepath", text="")

@MitsubaAddon.addon_register_class
class MitsubaRender_PT_active_film(MitsubaRenderPanel):
	bl_label = "Active Camera Film Settings"
	COMPAT_ENGINES = {'MITSUBA_RENDER'}
	
	display_property_groups = [
		( ('scene', 'camera', 'data'), 'mitsuba_film' )
	]
	
	def draw(self, context):
		layout = self.layout
		film = context.scene.camera.data.mitsuba_film
		layout.prop(film, "fileFormat")
		layout.prop(film, "pixelFormat", expand=True)
		if film.fileFormat == 'openexr':
			layout.prop(film, "componentFormat", expand=True)
		super().draw(context)

@MitsubaAddon.addon_register_class
class MitsubaRender_PT_setup_preset(MitsubaRenderPanel):
	'''
	Engine settings presets UI Panel
	'''
	
	bl_label = 'Mitsuba Engine Presets'
	
	def draw(self, context):
		row = self.layout.row(align=True)
		row.menu("MITSUBA_MT_presets_engine", text=bpy.types.MITSUBA_MT_presets_engine.bl_label)
		row.operator("mitsuba.preset_engine_add", text="", icon="ZOOMIN")
		row.operator("mitsuba.preset_engine_add", text="", icon="ZOOMOUT").remove_active = True
		
		super().draw(context)

@MitsubaAddon.addon_register_class
class MitsubaRender_PT_engine(MitsubaRenderPanel):
	'''
	Engine settings UI Panel
	'''
	
	bl_label = 'Mitsuba Engine Settings'
	
	display_property_groups = [
		( ('scene',), 'mitsuba_engine' )
	]
	
	def draw(self, context):
		super().draw(context)
		
		row = self.layout.row(align=True)
		rd = context.scene.render

@MitsubaAddon.addon_register_class
class MitsubaRender_PT_integrator(MitsubaRenderPanel):
	'''
	Integrator settings UI Panel
	'''
	
	bl_label = 'Mitsuba Integrator Settings'
	
	display_property_groups = [
		( ('scene',), 'mitsuba_integrator' )
	]

@MitsubaAddon.addon_register_class
class MitsubaRender_PT_adaptive(MitsubaRenderPanel):
	'''
	Adaptive settings UI Panel
	'''
	
	bl_label = 'Use Adaptive Integrator'
	bl_options = {'DEFAULT_CLOSED'}
	display_property_groups = [
		( ('scene',), 'mitsuba_adaptive' )
	]
	
	def draw_header(self, context):
		self.layout.prop(context.scene.mitsuba_adaptive, "use_adaptive", text="")
	
	def draw(self, context):
		self.layout.active = (context.scene.mitsuba_adaptive.use_adaptive)
		return super().draw(context)

@MitsubaAddon.addon_register_class
class MitsubaRender_PT_irrcache(MitsubaRenderPanel):
	'''
	Sampler settings UI Panel
	'''
	
	bl_label = 'Use Irradiance Cache'
	bl_options = {'DEFAULT_CLOSED'}
	display_property_groups = [
		( ('scene',), 'mitsuba_irrcache' )
	]
	
	def draw_header(self, context):
		self.layout.prop(context.scene.mitsuba_irrcache, "use_irrcache", text="")
	
	def draw(self, context):
		self.layout.active = (context.scene.mitsuba_irrcache.use_irrcache)
		return super().draw(context)

@MitsubaAddon.addon_register_class
class MitsubaRender_PT_sampler(MitsubaRenderPanel):
	'''
	Sampler settings UI Panel
	'''
	
	bl_label = 'Mitsuba Sampler Settings'
	
	display_property_groups = [
		( ('scene',), 'mitsuba_sampler' )
	]

@MitsubaAddon.addon_register_class
class MitsubaRender_PT_testing(MitsubaRenderPanel):
	bl_label = 'Mitsuba Test/Debugging Options'
	bl_options = {'DEFAULT_CLOSED'}
	
	display_property_groups = [
		( ('scene',), 'mitsuba_testing' )
	]
