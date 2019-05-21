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
	"name": "Quick Motion Paths",
	"author": "Cenek Strichel",
	"version": (1, 0, 1),
	"blender": (2, 79, 0),
	"location": "Tools > Quick Motion Paths",
	"description": "Show motion path",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}
	

import bpy


class RenamePanel(bpy.types.Panel):
	
	bl_label = "Quick Motion Paths"
	bl_idname = "MOTIONPATH_PANEL"
	
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Tools"
	bl_context = "posemode"


	def draw(self, context):
		
		layout = self.layout
		# button
		
		pchan = context.active_pose_bone
		mpath = pchan.motion_path if pchan else None
		
		if mpath:
			row = layout.row(align=True)
			row.operator("pose.paths_update", text="Update", icon = 'FILE_REFRESH')
			row.operator("pose.paths_clear", text="Clear", icon='X')
		else:	
			layout.operator("cenda.motion_pats", icon = 'ANIM_DATA')
		

# rename button	
class QuickMotionPath(bpy.types.Operator):
	
	"""Create motion path by preview range"""
	bl_label = "Calculate"
	bl_idname = "cenda.motion_pats"
	

	def execute(self, context ):
		
		if(bpy.context.scene.use_preview_range):
			startFrame = bpy.context.scene.frame_preview_start
			endFrame = bpy.context.scene.frame_preview_end
		else:
			startFrame = bpy.context.scene.frame_start
			endFrame = bpy.context.scene.frame_end
				
		bpy.ops.pose.paths_calculate(start_frame=startFrame, end_frame=endFrame, bake_location='TAILS')
		
		return{'FINISHED'} 
	
			
################################################################
# register #	
def register():
	bpy.utils.register_module(__name__)
	
def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()