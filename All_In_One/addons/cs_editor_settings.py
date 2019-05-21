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
	"name": "Set Editor Settings",
	"author": "Cenek Strichel",
	"version": (1, 0, 3),
	"blender": (2, 8, 0),
	"location": "screen.set_editor_settings hotkey",
	"description": "Set settings for all active editors",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}


import bpy
from bpy.props import StringProperty, BoolProperty


# change object mode by selection			
class SetEditorSettings(bpy.types.Operator):

	'''Set Editor Settings'''
	bl_idname = "screen.set_editor_settings"
	bl_label = "Set Editor Settings"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		
		# Render setting
		bpy.context.scene.render.tile_y = 32
		bpy.context.scene.render.tile_x = 32

		# UV editor
		bpy.context.scene.tool_settings.snap_uv_element = 'VERTEX' 
		
		# View 3D header
		bpy.context.scene.tool_settings.snap_element = 'VERTEX'
		bpy.context.scene.tool_settings.use_mesh_automerge = True
		
		# paint weight
		if ((2, 79, 4) <= bpy.app.version) :
			for b in bpy.data.brushes :
				b.use_frontface = True
		else:
			bpy.context.scene.tool_settings.weight_paint.use_normal = True
				
				
		bpy.context.scene.tool_settings.use_auto_normalize = True

		# areas #
		for area in bpy.context.screen.areas: # iterate through areas in current screen

			for space in area.spaces: # iterate through spaces in current VIEW_3D area

				if(space.type == 'DOPESHEET_EDITOR'):
					space.show_sliders = True

				elif(space.type == 'GRAPH_EDITOR'):
					space.show_sliders = True
					space.use_only_selected_curves_handles = True
					space.use_only_selected_keyframe_handles = False
					
				elif(space.type == 'VIEW_3D'):
					space.use_occlude_geometry = True
					space.show_relationship_lines = False
					space.lock_camera_and_layers = False

				elif(space.type == 'IMAGE_EDITOR'):
					space.uv_editor.show_other_objects = True
					
				elif(space.type == 'TIMELINE'):
					space.show_frame_indicator = True

			
		print("All editors setted")
		
		return {'FINISHED'}
	
	
def menu_func(self, context):
	self.layout.separator()
	self.layout.operator( SetEditorSettings.bl_idname, icon="PREFERENCES" )
			
				
################################################################
# register #
############
def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file.append(menu_func)
	
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file.remove(menu_func)
	
if __name__ == "__main__":
	register()