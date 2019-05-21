# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****


bl_info = {
	"name": "Render Debug",
	"author": "Cenek Strichel",
	"version": (1, 0, 3),
	"blender": (2, 79, 0),
	"location": "Render settings panel",
	"description": "Warnings dialog before render",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}


import bpy
from bpy.types import Header, Panel


class RenderDebugPanel(bpy.types.Panel):
	
	"""Render debug information"""
	bl_label = "Render Debug"
	bl_idname = "RENDER_debug_panel"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "render"


	def draw(self, context):
		
		layout = self.layout
		
		# warning tests #
		w_simplify = context.scene.render.use_simplify
		w_resolution = True if bpy.context.scene.render.resolution_percentage < 100 else False
		
		# just info
		w_device = True if context.scene.cycles.device == 'GPU' else False
		w_transparent = True if context.scene.cycles.film_transparent == False else False
		w_layer = False
		
		for i in range(0,20):    
			if(bpy.context.scene.layers[i] == False):
				w_layer = True
				break

		# warning #
		if( w_simplify or w_resolution or w_device or w_layer or w_transparent ):
	
			# Fix button only for error#	
			if( w_simplify or w_resolution ):
				
				box = layout.box()
				row = box.row()	
				
				row.operator("screen.fix_render_settings")
				
				# Problem! #
				if( w_simplify ):
					row = box.row()
					row.label(" Simplify is Enabled", icon="ERROR")
			      
				if( w_resolution ):
					row = box.row()
					row.label(" Render resolution is below 100%", icon="ERROR")
				
			# Only Warning #
			box = layout.box()

			if( w_layer ):
				row = box.row()
				row.label(" All render layers are not visible", icon="QUESTION")
				
			if( w_device ):
				row = box.row()
				row.label(" Render device is GPU", icon="QUESTION")
				
			if( w_transparent ):
				row = box.row()
				row.label(" Transparent is Disabled", icon="QUESTION")
				
		# ok dialog #
		else:
			row = box.row()
			row.label("Everything is OK", icon="INFO")
				
				
class FixRenderSettings(bpy.types.Operator):

	bl_idname = "screen.fix_render_settings"
	bl_label = "Fix"

	def execute(self, context):
		
		if( context.scene.render.resolution_percentage < 100 ):
			context.scene.render.resolution_percentage = 100
			
		context.scene.render.use_simplify = False

		return {'FINISHED'}
	
	

def VIEW3D_HT_RenderDebug(self, context):
	
	space = bpy.context.space_data
		
	# Normal view
	if(space.region_3d.view_perspective != 'CAMERA'): # only for camera
		
		layout = self.layout
		
		# warning tests #
		w_simplify = context.scene.render.use_simplify
		w_resolution = True if bpy.context.scene.render.resolution_percentage < 100 else False
		
		if( w_simplify or w_resolution ):

			row = layout.row(align=True)
			row.separator()
			row.operator("screen.show_render_debug", text = "", icon = "ERROR")
		
		
class ShowDebug(bpy.types.Operator):

	bl_idname = "screen.show_render_debug"
	bl_label = "Show Render Debug"

	def execute(self, context):
	
		for area in bpy.context.screen.areas: # iterate through areas in current screen
			if area.type == 'PROPERTIES':
				for space in area.spaces: # iterate through all founded panels
					if space.type == 'PROPERTIES':	
						space.context = 'RENDER'

		return {'FINISHED'}	
	
			
################################################################
# register #
############
def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_HT_header.prepend(VIEW3D_HT_RenderDebug)
	
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_HT_header(VIEW3D_HT_RenderDebug)
	
if __name__ == "__main__":
	register()