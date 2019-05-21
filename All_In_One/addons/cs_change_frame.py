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
	"name": "Change Frame",
	"author": "Cenek Strichel",
	"version": (1, 0, 4),
	"blender": (2, 79, 0),
	"location": "Add 'view3d.change_frame_drag' to Input Preferences under 3D View (Global)",
	"description": "Change frame by dragging",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}


import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, EnumProperty
from bpy.types import AddonPreferences, Operator

class ChangeFrame(bpy.types.Operator):
	
	
	"""Change frame with dragging"""
	bl_idname = "view3d.change_frame_drag"
	bl_label = "Change Frame Drag"
	bl_options = {"UNDO_GROUPED", "INTERNAL"}

	autoSensitivity = BoolProperty( name = "Auto Sensitivity" )
	defaultSensitivity = FloatProperty( name = "Sensitivity", default = 5 )
	renderOnly = BoolProperty( name = "Render Only", default = True )
	
	
	mouseEnum = [
	("LeftMouse", "Left Mouse", "", "", 0),
    ("MiddleMouse", "Middle Mouse", "", "", 1),
    ("RightMouse", "Right Mouse", "", "", 2)
    ]
	
	mouseSetting = EnumProperty( name = "End Drag", description = "", items=mouseEnum, default = "RightMouse" )


	global frameOffset
	global mouseOffset
	global sensitivity
	global previousManipulator
	global previousOnlyRender


	def modal(self, context, event):
	
		user_preferences = context.user_preferences
		addon_prefs = user_preferences.addons[__name__].preferences
	
		# set mouse up button
		mouseEnd = ''
		if(self.mouseSetting == 'LeftMouse'):
			mouseEnd = 'LEFTMOUSE'
			
		elif(self.mouseSetting == 'RightMouse'):
			mouseEnd = 'RIGHTMOUSE'
			
		elif(self.mouseSetting == 'MiddleMouse'):
			mouseEnd = 'MIDDLEMOUSE'
			
			
		# change frame
		if event.type == 'MOUSEMOVE':
			
			delta = self.mouseOffset - event.mouse_x
			
			if( addon_prefs.boolSmoothDrag ):
				off = (-delta * self.sensitivity) + self.frameOffset
				bpy.context.scene.frame_current = int(off)
				bpy.context.scene.frame_subframe = off-int(off)
				
			else:
				bpy.context.scene.frame_current = (-delta * self.sensitivity) + self.frameOffset
				
		# end of modal
		elif event.type == mouseEnd and event.value == 'RELEASE':
			
			# previous viewport setting
			bpy.context.space_data.show_manipulator = self.previousManipulator
			
			if(self.renderOnly):
				bpy.context.space_data.show_only_render = self.previousOnlyRender

			# cursor back
			bpy.context.window.cursor_set("DEFAULT")
			
			# snap back
			if( addon_prefs.boolSmoothSnap ):
				bpy.context.scene.frame_subframe = 0
			
			return {'FINISHED'}
			
		return {'RUNNING_MODAL'}


	def invoke(self, context, event):
		
		user_preferences = context.user_preferences
		addon_prefs = user_preferences.addons[__name__].preferences
		
		# hide viewport helpers
		self.previousManipulator = bpy.context.space_data.show_manipulator
		bpy.context.space_data.show_manipulator = False
		
		if(self.renderOnly):
			self.previousOnlyRender = bpy.context.space_data.show_only_render
			bpy.context.space_data.show_only_render = True
		
		
		# start modal
		if( addon_prefs.boolSmoothDrag ):
			self.frameOffset = bpy.context.scene.frame_current_final
		else:
			self.frameOffset = bpy.context.scene.frame_current 
			
		self.mouseOffset = event.mouse_x
		
		# cursor
		bpy.context.window.cursor_set("SCROLL_X")
		
		context.window_manager.modal_handler_add(self)
		
		found = False
		
		# auto sensitivity
		if(self.autoSensitivity):
			if context.area.type == 'VIEW_3D':
				
				ratio = 1024 / context.area.width
				self.sensitivity = (ratio / 10)
				
				# finding end of frame range
				if(bpy.context.scene.use_preview_range):
					endFrame = bpy.context.scene.frame_preview_end
				else:
					endFrame = bpy.context.scene.frame_end

				self.sensitivity *= (endFrame/ 100)

				found = True

		# default
		if(not found):
			self.sensitivity = self.defaultSensitivity / 100
			
		return {'RUNNING_MODAL'}


class ChangeFrameDragAddonPreferences(AddonPreferences):

	bl_idname = __name__

	boolSmoothDrag = BoolProperty( name="Smooth Drag",default=True )
	boolSmoothSnap = BoolProperty( name="Snap after drag",default=True )
	
	def draw(self, context):
	
		layout = self.layout
		
		layout.prop(self, "boolSmoothDrag")
		
		if(self.boolSmoothDrag):
			layout.prop(self, "boolSmoothSnap")

		
		
###########################################################
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()