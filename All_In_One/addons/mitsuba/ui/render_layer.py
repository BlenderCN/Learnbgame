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

from bl_ui.properties_render_layer import RenderLayerButtonsPanel
from extensions_framework.ui import property_group_renderer

from .. import MitsubaAddon

class MitsubaRenderLayerPanel(RenderLayerButtonsPanel, property_group_renderer):
	'''
	Base class for render layer panels
	'''
	
	COMPAT_ENGINES = { 'MITSUBA_RENDER' }

@MitsubaAddon.addon_register_class
class MitsubaRenderLayer_PT_layers(MitsubaRenderLayerPanel):
	'''
	Render Layers UI panel
	'''
	
	bl_label = 'Layers'
	bl_options = {'HIDE_HEADER'}
	
	def draw(self, context):
		#Add in Blender's layer chooser, this taken from Blender's startup/properties_render_layer.py
		layout = self.layout
		
		scene = context.scene
		rd = scene.render
		
		row = layout.row()
		row.template_list("RENDERLAYER_UL_renderlayers", "", rd, "layers", rd.layers, "active_index", rows=2)
		
		col = row.column(align=True)
		col.operator("scene.render_layer_add", icon='ZOOMIN', text="")
		col.operator("scene.render_layer_remove", icon='ZOOMOUT', text="")
		
		row = layout.row()
		rl = rd.layers.active
		if rl:
			row.prop(rl, "name")
		
		row.prop(rd, "use_single_layer", text="", icon_only=True)

@MitsubaAddon.addon_register_class
class MitsubaRenderLayer_PT_layer_options(MitsubaRenderLayerPanel):
	'''
	Render Layers UI panel
	'''
	
	bl_label = 'Layers'
	bl_options = {'DEFAULT_CLOSED'}
	
	def draw(self, context): 
		#Add in Blender's layer stuff, this taken from Blender's startup/properties_render_layer.py
		layout = self.layout
		
		scene = context.scene
		rd = scene.render
		rl = rd.layers.active
		
		split = layout.split()
		
		col = split.column()
		col.prop(scene, "layers", text="Scene")
		col = split.column()
		col.prop(rl, "layers", text="Layer")
