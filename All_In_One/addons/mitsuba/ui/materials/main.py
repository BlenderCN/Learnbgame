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
from ... import MitsubaAddon
from ...ui.materials import mitsuba_material_base

@MitsubaAddon.addon_register_class
class MATERIAL_PT_material_utils(mitsuba_material_base):
	'''
	Material Utils UI Panel
	'''
	
	bl_label	= 'Mitsuba Material Utils'
	bl_options = {'DEFAULT_CLOSED'}
	COMPAT_ENGINES	= { 'MITSUBA_RENDER' }
	
	def draw(self, context):
		row = self.layout.row(align=True)
		row.menu("MITSUBA_MT_presets_material", text=bpy.types.MITSUBA_MT_presets_material.bl_label)
		row.operator("mitsuba.preset_material_add", text="", icon="ZOOMIN")
		row.operator("mitsuba.preset_material_add", text="", icon="ZOOMOUT").remove_active = True
		
		
		row = self.layout.row(align=True)
		row.operator("mitsuba.convert_all_materials", icon='WORLD_DATA')
		row = self.layout.row(align=True)
		row.operator("mitsuba.convert_material", icon='MATERIAL_DATA')
		row = self.layout.row(align=True)
		row.operator("mitsuba.convert_all_materials_cycles", icon='WORLD_DATA')
		row = self.layout.row(align=True)
		row.operator("mitsuba.convert_material_cycles", icon='MATERIAL_DATA')

@MitsubaAddon.addon_register_class
class MATERIAL_PT_material_bsdf(mitsuba_material_base, bpy.types.Panel):
	'''
	Material BSDF UI Panel
	'''
	
	bl_label	= 'Mitsuba BSDF Material'
	COMPAT_ENGINES	= { 'MITSUBA_RENDER' }
	
	display_property_groups = [
		( ('material',), 'mitsuba_mat_bsdf' )
	]
	
	def draw_header(self, context):
		self.layout.prop(context.material.mitsuba_mat_bsdf, "use_bsdf", text="")
	
	def draw(self, context):
		layout = self.layout
		mat = context.material.mitsuba_mat_bsdf
		layout.active = (mat.use_bsdf)
		layout.prop(context.material.mitsuba_mat_bsdf, "type", text="")
		if mat.type != 'none':
			bsdf = getattr(mat, 'mitsuba_bsdf_%s' % mat.type)
			for p in bsdf.controls:
				self.draw_column(p, self.layout, mat, context,
					property_group=bsdf)
			bsdf.draw_callback(context)
		
		#return super().draw(context)
