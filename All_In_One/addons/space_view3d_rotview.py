# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

__bpydoc__ = """\
The RotView addon serves the purpose of setting fixed rotation values for each of the
right/left/front/back/top/bottom views.


Documentation

First go to User Preferences->Addons and enable the RotView addon in the 3D View category.
To change the rotation in realtime first press one of the numerical keypad
view shortcuts to switch into a view and set the rotation
value with the slider (doubleclick for keyboard input) or use the <-90 and 90-> buttons to
switch to the next multiple of 90 degrees value.  Button 0 goes back to zero rotation.
The rotation value of each of the views will be remembered when switching into it again from
the numerical keypad.

REMARK - when first enabling the addon, when in an affected view already, rotation will not work.
		 Enable the view again with numerical keypad shortcut.
		 
REMARK - will not work when switching view through the View menu
"""


bl_info = {
	"name": "RotView",
	"author": "Gert De Roost",
	"version": (0, 1, 5),
	"blender": (2, 6, 3),
	"location": "View3D > UI",
	"description": "Set fixed view rotation values",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Learnbgame",
}

if "bpy" in locals():
	import imp


import bpy
from mathutils import *
import math


activated = 0
frontrot = 0
backrot = 0
rightrot = 0
leftrot = 0
toprot = 0
bottomrot = 0
inview = 0
oldangle = 0
oldview = 0
adapt = 0
viewstring = ["", "FRONT", "BACK", "RIGHT", "LEFT", "TOP", "BOTTOM"]
viewnum = 1

bpy.types.Scene.Angle = bpy.props.FloatProperty(
		name = "Rotation angle", 
		description = "Enter rotation angle",
		default = 0,
		min = -360,
		max = 360)


class RotViewPanel(bpy.types.Panel):
	bl_label = "RotView"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	

	def draw_header(self, context):
		
		global activated
		
		layout = self.layout
		
		if not(activated):
			layout.operator("view3d.rotview", text="Activate")
	   
	def draw(self, context):
		
		global frontrot, backrot, rightrot, leftrot, toprot, bottomrot, matrot
		global oldangle, inview
		
		scn = bpy.context.scene
		layout = self.layout
		
		if activated:
			layout.label(viewstring[viewnum])
			
			layout.prop(scn, "Angle")
			
			row = layout.row()
			row.operator("view.minus90",
				text="<-90")
			row.operator("view.nill",
				text="0")
			row.operator("view.plus90",
				text="90->")
		
		
		if viewnum == 1:
			frontrot = scn.Angle
			matrotX = Matrix.Rotation(math.radians(90), 3, 'X')
			matrotY = Matrix.Rotation(math.radians(-scn.Angle), 3, 'Y')
			matrotZ = Matrix.Rotation(math.radians(0), 3, 'Z')
			quat = matrotX.to_quaternion()
			quat.rotate(matrotY)
			quat.rotate(matrotZ)
		elif viewnum == 2:
			backrot = scn.Angle
			matrotX = Matrix.Rotation(math.radians(90), 3, 'X')
			matrotY = Matrix.Rotation(math.radians(-scn.Angle), 3, 'Y')
			matrotZ = Matrix.Rotation(math.radians(180), 3, 'Z')
			quat = matrotX.to_quaternion()
			quat.rotate(matrotY)
			quat.rotate(matrotZ)
		elif viewnum == 3:
			rightrot = scn.Angle
			matrotX = Matrix.Rotation(math.radians(scn.Angle), 3, 'X')
			matrotY = Matrix.Rotation(math.radians(90), 3, 'Y')
			matrotZ = Matrix.Rotation(math.radians(90), 3, 'Z')
			quat = matrotZ.to_quaternion()
			quat.rotate(matrotY)
			quat.rotate(matrotX)
		elif viewnum == 4:
			leftrot = scn.Angle
			matrotX = Matrix.Rotation(math.radians(-scn.Angle), 3, 'X')
			matrotY = Matrix.Rotation(math.radians(-90), 3, 'Y')
			matrotZ = Matrix.Rotation(math.radians(-90), 3, 'Z')
			quat = matrotZ.to_quaternion()
			quat.rotate(matrotY)
			quat.rotate(matrotX)
		elif viewnum == 5:
			toprot = scn.Angle
			matrotX = Matrix.Rotation(math.radians(0), 3, 'X')
			matrotY = Matrix.Rotation(math.radians(0), 3, 'Y')
			matrotZ = Matrix.Rotation(math.radians(scn.Angle), 3, 'Z')
			quat = matrotX.to_quaternion()
			quat.rotate(matrotY)
			quat.rotate(matrotZ)
		elif viewnum == 6:
			bottomrot = scn.Angle
			matrotX = Matrix.Rotation(math.radians(180), 3, 'X')
			matrotY = Matrix.Rotation(math.radians(0), 3, 'Y')
			matrotZ = Matrix.Rotation(math.radians(-scn.Angle), 3, 'Z')
			quat = matrotX.to_quaternion()
			quat.rotate(matrotY)
			quat.rotate(matrotZ)
			
		if (inview == 1) and scn.Angle != oldangle:
			bpy.context.space_data.region_3d.view_rotation = quat
#			matrix = bpy.context.space_data.region_3d.view_matrix.to_3x3()
#			matrix.rotate(matrot)
#			bpy.context.space_data.region_3d.view_matrix = matrix.to_4x4()
#			bpy.context.region.tag_redraw()
			oldangle = scn.Angle
			
		if inview == 2:
			bpy.context.space_data.region_3d.view_rotation = quat
			inview = 0
			


class Minus90(bpy.types.Operator):
	bl_idname = "view.minus90"
	bl_label = ""
	bl_description = "To next 90 degrees multiple"


	def invoke(self, context, event):
		scn = bpy.context.scene
		if (scn.Angle // 90) == (scn.Angle / 90):
			if scn.Angle == -360:
				scn.Angle = 270
			else:
				scn.Angle -= 90
		else:
			scn.Angle = (scn.Angle // 90) * 90
		return {'FINISHED'}

class Plus90(bpy.types.Operator):
	bl_idname = "view.plus90"
	bl_label = ""
	bl_description = "To previous 90 degrees multiple"


	def invoke(self, context, event):
		scn = bpy.context.scene
		if scn.Angle == 360:
			scn.Angle = -270
		else:
			scn.Angle = ((scn.Angle // 90) + 1) * 90
		return {'FINISHED'}
	
class Nill(bpy.types.Operator):
	bl_idname = "view.nill"
	bl_label = ""
	bl_description = "Set rotation to 0"


	def invoke(self, context, event):
		scn = bpy.context.scene
		scn.Angle = 0
		return {'FINISHED'}
	

class RotView(bpy.types.Operator):
	bl_idname = "view3d.rotview"
	bl_label = "RotView"
	bl_description = "Set fixed view rotation values"
	bl_options = {"REGISTER"}


	def invoke(self, context, event):
		
		global activated
		
		activated = 1
		
		do_rotview(self)
		
		context.window_manager.modal_handler_add(self)
		self._handle = context.region.callback_add(redraw, (), 'POST_VIEW')
		
		return {'RUNNING_MODAL'}

	def modal(self, context, event):
		
		global frontrot, backrot, rightrot, leftrot, toprot, bottomrot
		global quat
		global inview, adapt, viewnum
		
		scn = bpy.context.scene
		if event.type == "MIDDLEMOUSE":
			inview = 0
			if viewnum == 1:
				matrotX = Matrix.Rotation(math.radians(90), 3, 'X')
				matrotY = Matrix.Rotation(math.radians(0), 3, 'Y')
				matrotZ = Matrix.Rotation(math.radians(0), 3, 'Z')
				quat = matrotX.to_quaternion()
				quat.rotate(matrotY)
				quat.rotate(matrotZ)
			elif viewnum == 2:
				matrotX = Matrix.Rotation(math.radians(90), 3, 'X')
				matrotY = Matrix.Rotation(math.radians(0), 3, 'Y')
				matrotZ = Matrix.Rotation(math.radians(180), 3, 'Z')
				quat = matrotX.to_quaternion()
				quat.rotate(matrotY)
				quat.rotate(matrotZ)
			elif viewnum == 3:
				matrotX = Matrix.Rotation(math.radians(0), 3, 'X')
				matrotY = Matrix.Rotation(math.radians(90), 3, 'Y')
				matrotZ = Matrix.Rotation(math.radians(90), 3, 'Z')
				quat = matrotZ.to_quaternion()
				quat.rotate(matrotY)
				quat.rotate(matrotX)
			elif viewnum == 4:
				matrotX = Matrix.Rotation(math.radians(0), 3, 'X')
				matrotY = Matrix.Rotation(math.radians(-90), 3, 'Y')
				matrotZ = Matrix.Rotation(math.radians(-90), 3, 'Z')
				quat = matrotZ.to_quaternion()
				quat.rotate(matrotY)
				quat.rotate(matrotX)
			elif viewnum == 5:
				matrotX = Matrix.Rotation(math.radians(0), 3, 'X')
				matrotY = Matrix.Rotation(math.radians(0), 3, 'Y')
				matrotZ = Matrix.Rotation(math.radians(0), 3, 'Z')
				quat = matrotX.to_quaternion()
				quat.rotate(matrotY)
				quat.rotate(matrotZ)
			elif viewnum == 6:
				matrotX = Matrix.Rotation(math.radians(180), 3, 'X')
				matrotY = Matrix.Rotation(math.radians(0), 3, 'Y')
				matrotZ = Matrix.Rotation(math.radians(0), 3, 'Z')
				quat = matrotX.to_quaternion()
				quat.rotate(matrotY)
				quat.rotate(matrotZ)
			bpy.context.space_data.region_3d.view_rotation = quat
		elif event.type == "NUMPAD_1":
			print (event.value)
			if not(event.ctrl):
				viewnum = 1
				scn.Angle = frontrot
				adapt = 1
				matrotX = Matrix.Rotation(math.radians(90), 3, 'X')
				matrotY = Matrix.Rotation(math.radians(-scn.Angle), 3, 'Y')
				matrotZ = Matrix.Rotation(math.radians(0), 3, 'Z')
				quat = matrotX.to_quaternion()
				quat.rotate(matrotY)
				quat.rotate(matrotZ)
				inview = 1
				bpy.context.region.tag_redraw()
			else:
				viewnum = 2
				scn.Angle = backrot
				adapt = 1
				matrotX = Matrix.Rotation(math.radians(90), 3, 'X')
				matrotY = Matrix.Rotation(math.radians(-scn.Angle), 3, 'Y')
				matrotZ = Matrix.Rotation(math.radians(180), 3, 'Z')
				quat = matrotX.to_quaternion()
				quat.rotate(matrotY)
				quat.rotate(matrotZ)
				inview = 1
				bpy.context.region.tag_redraw()
			return {"PASS_THROUGH"}
		elif event.type == "NUMPAD_3":
			if not(event.ctrl):
				viewnum = 3
				scn.Angle = rightrot
				adapt = 1
				matrotX = Matrix.Rotation(math.radians(scn.Angle), 3, 'X')
				matrotY = Matrix.Rotation(math.radians(90), 3, 'Y')
				matrotZ = Matrix.Rotation(math.radians(90), 3, 'Z')
				quat = matrotZ.to_quaternion()
				quat.rotate(matrotY)
				quat.rotate(matrotX)
				inview = 1
				bpy.context.region.tag_redraw()
			else:
				viewnum = 4
				scn.Angle = leftrot
				adapt = 1
				matrotX = Matrix.Rotation(math.radians(-scn.Angle), 3, 'X')
				matrotY = Matrix.Rotation(math.radians(-90), 3, 'Y')
				matrotZ = Matrix.Rotation(math.radians(-90), 3, 'Z')
				quat = matrotZ.to_quaternion()
				quat.rotate(matrotY)
				quat.rotate(matrotX)
				inview = 1
				bpy.context.region.tag_redraw()
			return {"PASS_THROUGH"}
		elif event.type == "NUMPAD_7":
			if not(event.ctrl):
				viewnum = 5
				scn.Angle = toprot
				adapt = 1
				matrotX = Matrix.Rotation(math.radians(0), 3, 'X')
				matrotY = Matrix.Rotation(math.radians(0), 3, 'Y')
				matrotZ = Matrix.Rotation(math.radians(scn.Angle), 3, 'Z')
				quat = matrotX.to_quaternion()
				quat.rotate(matrotY)
				quat.rotate(matrotZ)
				inview = 1
				bpy.context.region.tag_redraw()
			else:
				viewnum = 6
				scn.Angle = bottomrot
				adapt = 1
				matrotX = Matrix.Rotation(math.radians(180), 3, 'X')
				matrotY = Matrix.Rotation(math.radians(0), 3, 'Y')
				matrotZ = Matrix.Rotation(math.radians(-scn.Angle), 3, 'Z')
				quat = matrotX.to_quaternion()
				quat.rotate(matrotY)
				quat.rotate(matrotZ)
				inview = 1
				bpy.context.region.tag_redraw()
			return {"PASS_THROUGH"}
		
		return {"PASS_THROUGH"}



def register():
	bpy.utils.register_module(__name__)


def unregister():
	bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
	register()






	







def do_rotview(self):
	
	global regionui

	for region in bpy.context.area.regions:
		if region.type == "UI":
			regionui = region


def redraw():	

	global adapt

	if adapt:
		adapt = 0
		bpy.context.space_data.region_3d.view_rotation = quat



