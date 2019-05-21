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
	"name": "Camera Shot",
	"author": "Cenek Strichel",
	"version": (1, 0, 0),
	"blender": (2, 79, 0),
	"location": "Timeline header",
	"description": "Change shot by marker",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}

import bpy
import time

from bpy.props import StringProperty, IntProperty, BoolProperty
from bpy.types import Header, Panel




# GUI ###############################################################
class TIMELINE_HT_header_camShot(Header):
	
	bl_space_type = 'TIMELINE'


	def draw(self, context):

		layout = self.layout

		if(len(bpy.context.scene.timeline_markers) > 1):
			
			row = layout.row(align=True)
			row = layout.row(align=True)
			
			row.operator( "scene.change_cam_shot" , icon = "FRAME_PREV", text = "").forward = False
			row.operator( "scene.change_cam_shot" , icon = "FRAME_NEXT", text = "").forward = True
			
		
				
class ChangeCamShot(bpy.types.Operator):


	bl_label = "Change Cam Shot"
	bl_idname = "scene.change_cam_shot"

	forward = BoolProperty(name="Forward", default=True)
	
	
	def execute(self, context):
		
		# change only preview
		bpy.context.scene.use_preview_range = True
		
		markers = bpy.context.scene.timeline_markers

		myList = [int(m.frame) for m in markers]
		myList = sorted(myList)

		# FORWARD #
		if(self.forward):
			
			for index in range( len(myList) ):

				if myList[index] > bpy.context.scene.frame_preview_start :

					# start 
					bpy.context.scene.frame_current = myList[index]
					bpy.context.scene.frame_preview_start = myList[index]

					# end
					if(len(myList) > index+1):
						bpy.context.scene.frame_preview_end = myList[index+1]
						bpy.context.scene.frame_preview_end -= 1
						
					else:
						bpy.context.scene.frame_preview_end = bpy.context.scene.frame_preview_start + 200
					
					# HACK
					if( (bpy.context.scene.frame_preview_start) != (myList[index]) ):
						bpy.ops.scene.change_cam_shot(forward=True)
								
					break
				
		# BACKWARD #
		else:

			for index in reversed(range( len(myList) )):

				if myList[index] < bpy.context.scene.frame_preview_start :
					
					# start 
					bpy.context.scene.frame_current = myList[index]
					bpy.context.scene.frame_preview_start = myList[index]
					
					# end
					if(len(myList) > index+1):
						bpy.context.scene.frame_preview_end = myList[index+1]
						
					bpy.context.scene.frame_preview_end -= 1
					
					break	

		# frame timeline
		for area in bpy.context.screen.areas:
			if area.type == 'TIMELINE':
				for region in area.regions:
					if region.type == 'WINDOW':
						ctx = bpy.context.copy()
						ctx[ 'area'] = area
						ctx['region'] = region

						bpy.ops.time.view_all(ctx)
								
						break
			
			
		return{'FINISHED'}

	
	
################################################################
# register #

def register():
	bpy.utils.register_module(__name__)
	
def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()