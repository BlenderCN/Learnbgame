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
	"name": "Playblast",
	"author": "Cenek Strichel",
	"version": (1, 0, 0),
	"blender": (2, 79, 0),
	"location": "View 3D on camera",
	"description": "Make video preview and play",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}
	
	
import bpy
from bpy.types import Header, Panel
	
	
###################################	
# VIEW 3D HEADER #
###################################
def VIEW3D_HT_Playblast(self, context):
	
	
#	bl_space_type = 'VIEW_3D'


#	def draw(self, context):
		
	space = bpy.context.space_data
	
	# Normal view
	if(space.region_3d.view_perspective == 'CAMERA'): # only for camera
	
		layout = self.layout
		
		row = layout.row(align=True)
		row = layout.row(align=True)
		
		row.operator("scene.playblast", text = "Playblast", icon = "RENDER_ANIMATION")
			


class Playblast(bpy.types.Operator):

	'''Render Animation Preview'''
	bl_idname = "scene.playblast"
	bl_label = "Playblast"
	
	def execute(self, context):

		previous = bpy.context.scene.render.image_settings.file_format
		
		if(previous != "FFMPEG"):
			rd = bpy.context.scene.render
			rd.image_settings.file_format = "FFMPEG"
			rd.ffmpeg.format = "MPEG4"
			rd.ffmpeg.codec = "H264"

		try:
			bpy.ops.render.opengl(animation=True)
			bpy.ops.render.play_rendered_anim()
			
		except:
			self.report({'ERROR'}, "Scene has to be saved first!")
			
		if(previous != "FFMPEG"):
			bpy.context.scene.render.image_settings.file_format = previous

		return {'FINISHED'}
	
	
################################################################
# register #

def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_HT_header.prepend(VIEW3D_HT_Playblast)
	
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_HT_header(VIEW3D_HT_Playblast)
	
if __name__ == "__main__":
	register()