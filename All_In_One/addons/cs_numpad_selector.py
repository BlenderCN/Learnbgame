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


bl_info = {
	"name": "Numpad Selector",
	"category": "Cenda Tools",
	"author": "Cenek Strichel",
	"version": (1, 0, 2),
	"blender": (2, 79, 0),
	"description": "Selecting bones with numeric keys",
	"location": "Armature Properties + Set hotkey with 'view3d.num_select'",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
}


import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty
from bpy.types import AddonPreferences, Operator


class NumpadSelectorAddonPreferences(AddonPreferences):

	bl_idname = __name__

	boolCameraView = BoolProperty( name="Camera View when not Initialized", default=False )
	
	def draw(self, context):
	
		layout = self.layout
		layout.prop(self, "boolCameraView")
		
		
class NumControlPanel(bpy.types.Panel):
	
	"""Creates a Panel in the scene context of the properties editor"""
	bl_label = "Numpad Selector"
	bl_idname = "NUMCONTROL_PT_layout"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "data"
	
	@classmethod
	def poll(cls, context):
		return context.object.type == 'ARMATURE'

	manipulatorsEnum = [
	("NoChange", "No Change", "", "", 0),
    ("Translate", "Translate", "", "MAN_TRANS", 1),
    ("Rotate", "Rotate", "", "MAN_ROT", 2),
    ("Scale", "Scale", "", "MAN_SCALE", 3),
    ("TranslateRotate", "Translate & Rotate", "", 4),
	("RotateScale", "Rotate & Scale", "", 5),
	("ScaleTranslate", "Scale & Translate", "", 6)
    ]

	# R = Repeat, M = Manipulator, D = Double, S = Spare
	
	# 0
	bpy.types.Object.Num0 = bpy.props.StringProperty( name = "Num 0", default = "", description = "" )
	bpy.types.Object.Num0R = bpy.props.StringProperty( name = "Num 0 Repeat", default = "", description = "")
	bpy.types.Object.Num0M = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num0MR = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num0D = bpy.props.StringProperty( name = "Num 0 Double", default = "", description = "")
	bpy.types.Object.Num0MD = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num0AutoIKN = bpy.props.BoolProperty( name = "Auto IK N", description = "", default = False )
	bpy.types.Object.Num0AutoIKR = bpy.props.BoolProperty( name = "Auto IK R", description = "", default = False )
	bpy.types.Object.Num0AutoIKD = bpy.props.BoolProperty( name = "Auto IK D", description = "", default = False )
	bpy.types.Object.Num0S = bpy.props.StringProperty( name = "Num 0 Spare", default = "", description = "")
	bpy.types.Object.Num0AutoIKS = bpy.props.BoolProperty( name = "Auto IK S", description = "", default = False )
	bpy.types.Object.Num0MS = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	
	bpy.types.Object.Num0SR = bpy.props.StringProperty( name = "Num 0 Spare Repeat", default = "", description = "")
	bpy.types.Object.Num0MSR = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num0AutoIKSR = bpy.props.BoolProperty( name = "Auto IK SR", description = "", default = False )
	
	# 1
	bpy.types.Object.Num1 = bpy.props.StringProperty(name = "Num 1", default = "", description = "")
	bpy.types.Object.Num1R = bpy.props.StringProperty(name = "Num 1 Repeat", default = "", description = "")
	bpy.types.Object.Num1M = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num1MR = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num1D = bpy.props.StringProperty( name = "Num 1 Double", default = "", description = "")
	bpy.types.Object.Num1MD = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num1AutoIKN = bpy.props.BoolProperty( name = "Auto IK N", description = "", default = False )
	bpy.types.Object.Num1AutoIKR = bpy.props.BoolProperty( name = "Auto IK R", description = "", default = False )
	bpy.types.Object.Num1AutoIKD = bpy.props.BoolProperty( name = "Auto IK D", description = "", default = False )
	bpy.types.Object.Num1S = bpy.props.StringProperty( name = "Num 1 Spare", default = "", description = "")
	bpy.types.Object.Num1AutoIKS = bpy.props.BoolProperty( name = "Auto IK S", description = "", default = False )
	bpy.types.Object.Num1MS = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	
	bpy.types.Object.Num1SR = bpy.props.StringProperty( name = "Num 1 Spare Repeat", default = "", description = "")
	bpy.types.Object.Num1MSR = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num1AutoIKSR = bpy.props.BoolProperty( name = "Auto IK SR", description = "", default = False )
	
	# 2
	bpy.types.Object.Num2 = bpy.props.StringProperty(name = "Num 2", default = "", description = "")
	bpy.types.Object.Num2R = bpy.props.StringProperty(name = "Num 2 Repeat", default = "", description = "")
	bpy.types.Object.Num2M = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num2MR = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num2D = bpy.props.StringProperty( name = "Num 2 Double", default = "", description = "")
	bpy.types.Object.Num2MD = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num2AutoIKN = bpy.props.BoolProperty( name = "Auto IK N", description = "", default = False )
	bpy.types.Object.Num2AutoIKR = bpy.props.BoolProperty( name = "Auto IK R", description = "", default = False )
	bpy.types.Object.Num2AutoIKD = bpy.props.BoolProperty( name = "Auto IK D", description = "", default = False )
	bpy.types.Object.Num2S = bpy.props.StringProperty( name = "Num 2 Spare", default = "", description = "")
	bpy.types.Object.Num2AutoIKS = bpy.props.BoolProperty( name = "Auto IK S", description = "", default = False )
	bpy.types.Object.Num2MS = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	
	bpy.types.Object.Num2SR = bpy.props.StringProperty( name = "Num 2 Spare Repeat", default = "", description = "")
	bpy.types.Object.Num2MSR = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num2AutoIKSR = bpy.props.BoolProperty( name = "Auto IK SR", description = "", default = False )
	
	# 3
	bpy.types.Object.Num3 = bpy.props.StringProperty(name = "Num 3", default = "", description = "")
	bpy.types.Object.Num3R = bpy.props.StringProperty(name = "Num 3 Repeat", default = "", description = "")
	bpy.types.Object.Num3M = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num3MR = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num3D = bpy.props.StringProperty( name = "Num 3 Double", default = "", description = "")
	bpy.types.Object.Num3MD = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num3AutoIKN = bpy.props.BoolProperty( name = "Auto IK N", description = "", default = False )
	bpy.types.Object.Num3AutoIKR = bpy.props.BoolProperty( name = "Auto IK R", description = "", default = False )
	bpy.types.Object.Num3AutoIKD = bpy.props.BoolProperty( name = "Auto IK D", description = "", default = False )
	bpy.types.Object.Num3S = bpy.props.StringProperty( name = "Num 3 Spare", default = "", description = "")
	bpy.types.Object.Num3AutoIKS = bpy.props.BoolProperty( name = "Auto IK S", description = "", default = False )
	bpy.types.Object.Num3MS = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	
	bpy.types.Object.Num3SR = bpy.props.StringProperty( name = "Num 3 Spare Repeat", default = "", description = "")
	bpy.types.Object.Num3MSR = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num3AutoIKSR = bpy.props.BoolProperty( name = "Auto IK SR", description = "", default = False )
	
	# 4
	bpy.types.Object.Num4 = bpy.props.StringProperty(name = "Num 4", default = "", description = "")
	bpy.types.Object.Num4R = bpy.props.StringProperty(name = "Num 4 Repeat", default = "", description = "")
	bpy.types.Object.Num4M = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num4MR = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num4D = bpy.props.StringProperty( name = "Num 4 Double", default = "", description = "")
	bpy.types.Object.Num4MD = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num4AutoIKN = bpy.props.BoolProperty( name = "Auto IK N", description = "", default = False )
	bpy.types.Object.Num4AutoIKR = bpy.props.BoolProperty( name = "Auto IK R", description = "", default = False )
	bpy.types.Object.Num4AutoIKD = bpy.props.BoolProperty( name = "Auto IK D", description = "", default = False )
	bpy.types.Object.Num4S = bpy.props.StringProperty( name = "Num 4 Spare", default = "", description = "")
	bpy.types.Object.Num4AutoIKS = bpy.props.BoolProperty( name = "Auto IK S", description = "", default = False )
	bpy.types.Object.Num4MS = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	
	bpy.types.Object.Num4SR = bpy.props.StringProperty( name = "Num 4 Spare Repeat", default = "", description = "")
	bpy.types.Object.Num4MSR = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num4AutoIKSR = bpy.props.BoolProperty( name = "Auto IK SR", description = "", default = False )
	
	# 5
	bpy.types.Object.Num5 = bpy.props.StringProperty(name = "Num 5", default = "", description = "")
	bpy.types.Object.Num5R = bpy.props.StringProperty(name = "Num 5 Repeat", default = "", description = "")
	bpy.types.Object.Num5M = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num5MR = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num5D = bpy.props.StringProperty( name = "Num 5 Double", default = "", description = "")
	bpy.types.Object.Num5MD = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num5AutoIKN = bpy.props.BoolProperty( name = "Auto IK N", description = "", default = False )
	bpy.types.Object.Num5AutoIKR = bpy.props.BoolProperty( name = "Auto IK R", description = "", default = False )
	bpy.types.Object.Num5AutoIKD = bpy.props.BoolProperty( name = "Auto IK D", description = "", default = False )
	bpy.types.Object.Num5S = bpy.props.StringProperty( name = "Num 5 Spare", default = "", description = "")
	bpy.types.Object.Num5AutoIKS = bpy.props.BoolProperty( name = "Auto IK S", description = "", default = False )
	bpy.types.Object.Num5MS = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	
	bpy.types.Object.Num5SR = bpy.props.StringProperty( name = "Num 5 Spare Repeat", default = "", description = "")
	bpy.types.Object.Num5MSR = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num5AutoIKSR = bpy.props.BoolProperty( name = "Auto IK SR", description = "", default = False )
	
	# 6
	bpy.types.Object.Num6 = bpy.props.StringProperty(name = "Num 6", default = "", description = "")
	bpy.types.Object.Num6R = bpy.props.StringProperty(name = "Num 6 Repeat", default = "", description = "")
	bpy.types.Object.Num6M = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num6MR = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num6D = bpy.props.StringProperty( name = "Num 6 Double", default = "", description = "")
	bpy.types.Object.Num6MD = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num6AutoIKN = bpy.props.BoolProperty( name = "Auto IK N", description = "", default = False )
	bpy.types.Object.Num6AutoIKR = bpy.props.BoolProperty( name = "Auto IK R", description = "", default = False )
	bpy.types.Object.Num6AutoIKD = bpy.props.BoolProperty( name = "Auto IK D", description = "", default = False )
	bpy.types.Object.Num6S = bpy.props.StringProperty( name = "Num 6 Spare", default = "", description = "")
	bpy.types.Object.Num6AutoIKS = bpy.props.BoolProperty( name = "Auto IK S", description = "", default = False )
	bpy.types.Object.Num6MS = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	
	bpy.types.Object.Num6SR = bpy.props.StringProperty( name = "Num 6 Spare Repeat", default = "", description = "")
	bpy.types.Object.Num6MSR = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num6AutoIKSR = bpy.props.BoolProperty( name = "Auto IK SR", description = "", default = False )
	
	# 7
	bpy.types.Object.Num7 = bpy.props.StringProperty(name = "Num 7", default = "", description = "")
	bpy.types.Object.Num7R = bpy.props.StringProperty(name = "Num 7 Repeat", default = "", description = "")
	bpy.types.Object.Num7M = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num7MR = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num7D = bpy.props.StringProperty( name = "Num 7 Double", default = "", description = "")
	bpy.types.Object.Num7MD = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num7AutoIKN = bpy.props.BoolProperty( name = "Auto IK N", description = "", default = False )
	bpy.types.Object.Num7AutoIKR = bpy.props.BoolProperty( name = "Auto IK R", description = "", default = False )
	bpy.types.Object.Num7AutoIKD = bpy.props.BoolProperty( name = "Auto IK D", description = "", default = False )
	bpy.types.Object.Num7S = bpy.props.StringProperty( name = "Num 7 Spare", default = "", description = "")
	bpy.types.Object.Num7AutoIKS = bpy.props.BoolProperty( name = "Auto IK S", description = "", default = False )
	bpy.types.Object.Num7MS = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	
	bpy.types.Object.Num7SR = bpy.props.StringProperty( name = "Num 7 Spare Repeat", default = "", description = "")
	bpy.types.Object.Num7MSR = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num7AutoIKSR = bpy.props.BoolProperty( name = "Auto IK SR", description = "", default = False )
	
	# 8
	bpy.types.Object.Num8 = bpy.props.StringProperty(name = "Num 8", default = "", description = "")
	bpy.types.Object.Num8R = bpy.props.StringProperty(name = "Num 8 Repeat", default = "", description = "")
	bpy.types.Object.Num8M = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num8MR = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num8D = bpy.props.StringProperty( name = "Num 8 Double", default = "", description = "")
	bpy.types.Object.Num8MD = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num8AutoIKN = bpy.props.BoolProperty( name = "Auto IK N", description = "", default = False )
	bpy.types.Object.Num8AutoIKR = bpy.props.BoolProperty( name = "Auto IK R", description = "", default = False )
	bpy.types.Object.Num8AutoIKD = bpy.props.BoolProperty( name = "Auto IK D", description = "", default = False )
	bpy.types.Object.Num8S = bpy.props.StringProperty( name = "Num 8 Spare", default = "", description = "")
	bpy.types.Object.Num8AutoIKS = bpy.props.BoolProperty( name = "Auto IK S", description = "", default = False )
	bpy.types.Object.Num8MS = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	
	bpy.types.Object.Num8SR = bpy.props.StringProperty( name = "Num 8 Spare Repeat", default = "", description = "")
	bpy.types.Object.Num8MSR = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num8AutoIKSR = bpy.props.BoolProperty( name = "Auto IK SR", description = "", default = False )
	
	# 9
	bpy.types.Object.Num9 = bpy.props.StringProperty(name = "Num 9", default = "", description = "")
	bpy.types.Object.Num9R = bpy.props.StringProperty(name = "Num 9 Repeat", default = "", description = "")
	bpy.types.Object.Num9M = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num9MR = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num9D = bpy.props.StringProperty( name = "Num 9 Double", default = "", description = "")
	bpy.types.Object.Num9MD = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num9AutoIKN = bpy.props.BoolProperty( name = "Auto IK N", description = "", default = False )
	bpy.types.Object.Num9AutoIKR = bpy.props.BoolProperty( name = "Auto IK R", description = "", default = False )
	bpy.types.Object.Num9AutoIKD = bpy.props.BoolProperty( name = "Auto IK D", description = "", default = False )
	bpy.types.Object.Num9S = bpy.props.StringProperty( name = "Num 9 Spare", default = "", description = "")
	bpy.types.Object.Num9AutoIKS = bpy.props.BoolProperty( name = "Auto IK S", description = "", default = False )
	bpy.types.Object.Num9MS = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	
	bpy.types.Object.Num9SR = bpy.props.StringProperty( name = "Num 9 Spare Repeat", default = "", description = "")
	bpy.types.Object.Num9MSR = bpy.props.EnumProperty( name = "Manipulator", description = "", items=manipulatorsEnum )
	bpy.types.Object.Num9AutoIKSR = bpy.props.BoolProperty( name = "Auto IK SR", description = "", default = False )
	
	bpy.types.Object.Initialize = bpy.props.BoolProperty( name = "Initialize", description = "", default = False )
	
	
	def draw(self, context):
		
		layout = self.layout
		obj = context.object
		
		
		# I need create some value first
		if( obj.Initialize == False ):
			
			box = layout.box()
			c = box.column()
			c.operator("view3d.num_select_reset", text = "Initialize")

		else:

			for i in range(10) :
				
				box = layout.box()
				box.label( "Num "+str(i) )

				# Normal
				c = layout.column()
				split = box.split(percentage=0.47)
				c = split.column()
				c.prop(obj, ("Num"+str(i)), text = "Normal" )
				
				split = split.split( align = True )
				c = split.column( align = True )
				
				selectFill = c.operator("view3d.num_select_fill", text="", icon = 'HAND')
				selectFill.index = str(i)
				selectFill.multipleSelection = True
				
				c = split.column(align = True)
				c.prop(obj, ("Num"+str(i)+"M"), text = "" )
				c = split.column(align = True)
				c.prop(obj, ("Num"+str(i)+"AutoIKN"), text = "Auto IK" )
				
				
				# Spare
				split = box.split(percentage=0.47)
				c = split.column()
				c.prop(obj, ("Num"+str(i)+"S"), text = "Spare" )
				
				split = split.split(align = True)
				c = split.column(align = True)
				
				selectFill = c.operator("view3d.num_select_fill", text="", icon = 'EYEDROPPER')
				selectFill.index = (str(i)+"S")
				selectFill.multipleSelection = False
				
				c = split.column(align = True)
				c.prop(obj, ("Num"+str(i)+"MS"), text = "" )
				c = split.column(align = True)
				c.prop(obj, ("Num"+str(i)+"AutoIKS"), text = "Auto IK" )
				
				
				# Spare Repeat
				split = box.split(percentage=0.47)
				c = split.column()
				c.prop(obj, ("Num"+str(i)+"SR"), text = "Spare Repeat" )
				
				split = split.split(align = True)
				c = split.column(align = True)
				
				selectFill = c.operator("view3d.num_select_fill", text="", icon = 'EYEDROPPER')
				selectFill.index = (str(i)+"SR")
				selectFill.multipleSelection = False
				
				c = split.column(align = True)
				c.prop(obj, ("Num"+str(i)+"MSR"), text = "" )
				c = split.column(align = True)
				c.prop(obj, ("Num"+str(i)+"AutoIKSR"), text = "Auto IK" )
				
				
				# Separator
				c.separator()
				c.separator()
				
				
				# Repeat
				split = box.split(percentage=0.47)
				c = split.column()
				c.prop(obj, ("Num"+str(i)+"R"), text = "Repeat" )
				
				split = split.split(align = True)
				c = split.column(align = True)
				
				selectFill = c.operator("view3d.num_select_fill", text="", icon = 'EYEDROPPER')
				selectFill.index = (str(i)+"R")
				selectFill.multipleSelection = False
				
				c = split.column(align = True)
				c.prop(obj, ("Num"+str(i)+"MR"), text = "" )
				c = split.column(align = True)
				c.prop(obj, ("Num"+str(i)+"AutoIKR"), text = "Auto IK" )
				
				# Double
				split = box.split(percentage=0.47)
				c = split.column()
				c.prop(obj, ("Num"+str(i)+"D"), text = "Double" )
				
				split = split.split(align = True)
				c = split.column(align = True)
				
				selectFill = c.operator("view3d.num_select_fill", text="", icon = 'HAND')
				selectFill.index = (str(i)+"D")
				selectFill.multipleSelection = True
				
				c = split.column(align = True)
				c.prop(obj, ("Num"+str(i)+"MD"), text = "" )
				c = split.column(align = True)
				c.prop(obj, ("Num"+str(i)+"AutoIKD"), text = "Auto IK" )

				# Separator
				c.separator()
					
			box = layout.box()
			box.label("Settings")	
			split = box.split()
			c = split.row(align = True)
			c.operator("view3d.num_select_default", text = "Fill Default Animal").preset = 0
			c.operator("view3d.num_select_default", text = "Fill Default Human").preset = 1
			
			c = box.column()
			c.operator("view3d.num_select_reset", text = "Clear")
			
			
# selecting by num	
class NumControlSelect(bpy.types.Operator):

	"""Creates a Panel in the scene context of the properties editor"""
	bl_label = "Numeric Selector"
	bl_idname = "view3d.num_select"
	
	numKeysEnum = [
	("Num0", "Num 0", "", "", 0),
    ("Num1", "Num 1", "", "", 1),
	("Num2", "Num 2", "", "", 2),
	("Num3", "Num 3", "", "", 3),
	("Num4", "Num 4", "", "", 4),
	("Num5", "Num 5", "", "", 5),
	("Num6", "Num 6", "", "", 6),
	("Num7", "Num 7", "", "", 7),
	("Num8", "Num 8", "", "", 8),
	("Num9", "Num 9", "", "", 9),
	("Num0D", "Num 0 Double", "", "", 10),
    ("Num1D", "Num 1 Double", "", "", 11),
	("Num2D", "Num 2 Double", "", "", 12),
	("Num3D", "Num 3 Double", "", "", 13),
	("Num4D", "Num 4 Double", "", "", 14),
	("Num5D", "Num 5 Double", "", "", 15),
	("Num6D", "Num 6 Double", "", "", 16),
	("Num7D", "Num 7 Double", "", "", 17),
	("Num8D", "Num 8 Double", "", "", 18),
	("Num9D", "Num 9 Double", "", "", 19)
    ]

	numKey = EnumProperty( name = "Num Key", description = "", items = numKeysEnum )	
	
	
	def execute(self, context):
		
		ob = bpy.context.object
		
		for i in range(10) :
			
			num = str(i)
			
			try:
				# NORMAL & REPEAT
				if(self.numKey == 'Num'+num):
				
					repeat, spare = SelectBone(
					self, 
					ob, 
					(ob["Num"+num]), 
					(ob["Num"+num+"R"]),
					(ob["Num"+num+"M"]), 
					(ob["Num"+num+"MR"]), 
					(ob["Num"+num+"S"]), 
					(ob["Num"+num+"MS"]),
					(ob["Num"+num+"SR"]),
					(ob["Num"+num+"MSR"])
					 )
					if(spare and repeat):
						AutoIKSetting(ob["Num"+num+"AutoIKSR"])
					elif(spare):
						AutoIKSetting(ob["Num"+num+"AutoIKS"])		
					elif(repeat):
						AutoIKSetting(ob["Num"+num+"AutoIKR"])
					else:
						AutoIKSetting(ob["Num"+num+"AutoIKN"])
					
				# DOUBLE	
				elif(self.numKey == ('Num'+num+'D') ):
					
					repeat, spare = SelectBone(
					self,
					ob,
					(ob["Num"+num+"D"]),
					(ob["Num"+num+"D"]),
					(ob["Num"+num+"MD"]),
					(ob["Num"+num+"MD"]),
					(ob["Num"+num+"S"]),
					(ob["Num"+num+"MS"]),
					(ob["Num"+num+"S"]),
					(ob["Num"+num+"MS"])
					 )
					
					AutoIKSetting(ob["Num"+num+"AutoIKD"])
					
			except:
				
				try:
					if( not ob.Initialized ):
						self.report({'ERROR'}, "Bone selector was not initialized\nUse Initialize in the Armature setting")
					else:
						self.report({'WARNING'}, "Bone was not found")
						
				except:
					
					user_preferences = context.user_preferences
					addon_prefs = user_preferences.addons[__name__].preferences
					
					if(addon_prefs.boolCameraView):
						bpy.ops.screen.show_camera_view()
					else:
						self.report({'ERROR'}, "Bone selector was not initialized\nUse Initialize in the Armature setting")	
					
				
		# for AutoIK toggle	(my another addon)	
		# redraw 
		for area in bpy.context.screen.areas:
			if area.type == 'VIEW_3D':
				area.tag_redraw()
				
		return {'FINISHED'}

		
def AutoIKSetting( state = False ):
	bpy.context.object.data.use_auto_ik = state

			
			
# selecting metod		
def SelectBone( self, ob, boneName, boneNameRepeat, manipulator, manipulatorRepeat, boneSpare, manipulatorSpare, boneSpareRepeat, manipulatorSpareRepeat ) :
	
	finalBone = ""
	finalManipulator = ""
	repeatKey = False
	spare = False

	
	# normal select
	if( bpy.context.active_pose_bone.name != boneName ) :
		finalBone = boneName
		finalManipulator = manipulator
		repeatKey = False
		
	# repeat select
	else :
		finalBone = boneNameRepeat
		finalManipulator = manipulatorRepeat
		repeatKey = True
	
	# contains multiple bones?
	multipleBones = False	
	if ";" in finalBone:
		multipleBones = True
	
	# spare
	if( not multipleBones and finalBone != "" and ob.pose.bones[ finalBone ].bone.hide ):
		
		if(bpy.context.active_pose_bone.name == boneSpare):
			finalBone = boneSpareRepeat
			finalManipulator = manipulatorSpareRepeat
			repeatKey = True
			
		else:	
			finalBone = boneSpare
			finalManipulator = manipulatorSpare
			
		spare = True

	# if bone is not exist
	if( (ob.pose.bones.get( finalBone ) is None) and not multipleBones ):
		
		if( len(finalBone) == 0 ) :
			self.report({'WARNING'}, "Bone is not defined")
			
	else:
			
		# deselect bone if some is selected
		if( len(bpy.context.selected_pose_bones) > 0):
			bpy.ops.pose.select_all(action='TOGGLE')
		
		# multiple bones
		if(multipleBones):
			allBones = finalBone.split(";")
			for ab in allBones :		
				if(len(ab) > 0): # ";" ending
					ob.pose.bones[ ab ].bone.select = True
					ob.data.bones.active = ob.pose.bones[ ab ].bone
		
		# one bone	
		else:
			ob.pose.bones[ finalBone ].bone.select = True
			ob.data.bones.active = ob.pose.bones[ finalBone ].bone
		
		# manipulator	
		if(finalManipulator == 1):
			bpy.context.space_data.transform_manipulators = {'TRANSLATE'}
			
		elif(finalManipulator == 2):
			bpy.context.space_data.transform_manipulators = {'ROTATE'}
			
		elif(finalManipulator == 3):
			bpy.context.space_data.transform_manipulators = {'SCALE'}
			
		elif(finalManipulator == 4):
			bpy.context.space_data.transform_manipulators = {'TRANSLATE', 'ROTATE'}
		
		elif(finalManipulator == 5):
			bpy.context.space_data.transform_manipulators = {'ROTATE', 'SCALE'}
			
		elif(finalManipulator == 6):
			bpy.context.space_data.transform_manipulators = {'SCALE', 'TRANSLATE'}
			
		
	return [ repeatKey, spare ]


#############################
# HELPER METHODS ###########################################################################################
#############################
#
# pick bone from scene
#
class NumControlSelectPick(bpy.types.Operator):


	"""Pick selected object(s) (hand icon support multiple selection)"""
	bl_label = "Fill numeric"
	bl_idname = "view3d.num_select_fill"
	
	index = StringProperty( name = "index" )
	multipleSelection = BoolProperty( name = "multipleSelection", default = False )
	
	
	def execute(self, context):
		
		selectedBone = ""
		bones = bpy.context.selected_pose_bones
		
		# Multiple selection is not allowed for all
		if(self.multipleSelection and len(bones) > 1):
			for b in bones :
				selectedBone += b.name +";"
	
		else:		
			selectedBone = bpy.context.active_pose_bone.name
		
		
		for i in range(10) :
			
			num = str(i)

			if(self.index == num):
				bpy.context.object['Num'+num] = selectedBone
				
			elif(self.index == (num+'R') ):
				bpy.context.object['Num'+num+'R'] = selectedBone
				
			elif(self.index == (num+'D') ):
				bpy.context.object['Num'+num+'D'] = selectedBone	
					
			elif(self.index == (num+'S') ):
				bpy.context.object['Num'+num+'S'] = selectedBone	
				
			elif(self.index == (num+'SR') ):
				bpy.context.object['Num'+num+'SR'] = selectedBone	
				
		return {'FINISHED'}
	

class NumControlSelectReset(bpy.types.Operator):

	"""Reset values for first use"""
	bl_label = "Init value"
	bl_idname = "view3d.num_select_reset"
	
	def execute(self, context):
	
		context.object.Initialize = True
		
		# RESET #
		# 0
		context.object.Num0 = ""
		context.object.Num0R = ""
		context.object.Num0D = ""
		context.object.Num0S = ""
		context.object.Num0M = 'NoChange'
		context.object.Num0MR = 'NoChange'
		context.object.Num0MD = 'NoChange'
		context.object.Num0MS = 'NoChange'
		context.object.Num0AutoIKN = False
		context.object.Num0AutoIKR = False
		context.object.Num0AutoIKD = False
		context.object.Num0AutoIKS = False
		
		context.object.Num0SR = ""
		context.object.Num0MSR = 'NoChange'
		context.object.Num0AutoIKSR = False

		
		# 1
		context.object.Num1 = ""
		context.object.Num1R = ""
		context.object.Num1D = ""
		context.object.Num1S = ""
		context.object.Num1M = 'NoChange'
		context.object.Num1MR = 'NoChange'
		context.object.Num1MD = 'NoChange'
		context.object.Num1MS = 'NoChange'
		context.object.Num1AutoIKN = False
		context.object.Num1AutoIKR = False
		context.object.Num1AutoIKD = False
		context.object.Num1AutoIKS = False
		
		context.object.Num1SR = ""
		context.object.Num1MSR = 'NoChange'
		context.object.Num1AutoIKSR = False
		
		
		# 2
		context.object.Num2 = ""
		context.object.Num2R = ""
		context.object.Num2D = ""
		context.object.Num2S = ""
		context.object.Num2M = 'NoChange'
		context.object.Num2MR = 'NoChange'
		context.object.Num2MD = 'NoChange'
		context.object.Num2MS = 'NoChange'
		context.object.Num2AutoIKN = False
		context.object.Num2AutoIKR = False
		context.object.Num2AutoIKD = False
		context.object.Num2AutoIKS = False
		
		context.object.Num2SR = ""
		context.object.Num2MSR = 'NoChange'
		context.object.Num2AutoIKSR = False
		
		
		# 3
		context.object.Num3 = ""
		context.object.Num3R = ""
		context.object.Num3D = ""
		context.object.Num3S = ""
		context.object.Num3M = 'NoChange'
		context.object.Num3MR = 'NoChange'
		context.object.Num3MD = 'NoChange'
		context.object.Num3MS = 'NoChange'
		context.object.Num3AutoIKN = False
		context.object.Num3AutoIKR = False
		context.object.Num3AutoIKD = False
		context.object.Num3AutoIKS = False
		
		context.object.Num3SR = ""
		context.object.Num3MSR = 'NoChange'
		context.object.Num3AutoIKSR = False
		
		
		# 4
		context.object.Num4 = ""
		context.object.Num4R = ""
		context.object.Num4D = ""
		context.object.Num4S = ""
		context.object.Num4M = 'NoChange'
		context.object.Num4MR = 'NoChange'
		context.object.Num4MD = 'NoChange'
		context.object.Num4MS = 'NoChange'
		context.object.Num4AutoIKN = False
		context.object.Num4AutoIKR = False
		context.object.Num4AutoIKD = False
		context.object.Num4AutoIKS = False
		
		context.object.Num4SR = ""
		context.object.Num4MSR = 'NoChange'
		context.object.Num4AutoIKSR = False
		
		
		# 5
		context.object.Num5 = ""
		context.object.Num5R = ""
		context.object.Num5D = ""
		context.object.Num5S = ""
		context.object.Num5M = 'NoChange'
		context.object.Num5MR = 'NoChange'
		context.object.Num5MD = 'NoChange'
		context.object.Num5MS = 'NoChange'
		context.object.Num5AutoIKN = False
		context.object.Num5AutoIKR = False
		context.object.Num5AutoIKD = False
		context.object.Num5AutoIKS = False
		
		context.object.Num5SR = ""
		context.object.Num5MSR = 'NoChange'
		context.object.Num5AutoIKSR = False
		
		
		# 6
		context.object.Num6 = ""
		context.object.Num6R = ""
		context.object.Num6D = ""
		context.object.Num6S = ""
		context.object.Num6M = 'NoChange'
		context.object.Num6MR = 'NoChange'
		context.object.Num6MD = 'NoChange'
		context.object.Num6MS = 'NoChange'
		context.object.Num6AutoIKN = False
		context.object.Num6AutoIKR = False
		context.object.Num6AutoIKD = False
		context.object.Num6AutoIKS = False
		
		context.object.Num6SR = ""
		context.object.Num6MSR = 'NoChange'
		context.object.Num6AutoIKSR = False
		
		
		# 7
		context.object.Num7 = ""
		context.object.Num7R = ""
		context.object.Num7D = ""
		context.object.Num7S = ""
		context.object.Num7M = 'NoChange'
		context.object.Num7MR = 'NoChange'
		context.object.Num7MD = 'NoChange'
		context.object.Num7MS = 'NoChange'
		context.object.Num7AutoIKN = False
		context.object.Num7AutoIKR = False
		context.object.Num7AutoIKD = False
		context.object.Num7AutoIKS = False
		
		context.object.Num7SR = ""
		context.object.Num7MSR = 'NoChange'
		context.object.Num7AutoIKSR = False
		
		
		# 8
		context.object.Num8 = ""
		context.object.Num8R = ""
		context.object.Num8D = ""
		context.object.Num8S = ""
		context.object.Num8M = 'NoChange'
		context.object.Num8MR = 'NoChange'
		context.object.Num8MD = 'NoChange'
		context.object.Num8MS = 'NoChange'
		context.object.Num8AutoIKN = False
		context.object.Num8AutoIKR = False
		context.object.Num8AutoIKD = False
		context.object.Num8AutoIKS = False
		
		context.object.Num8SR = ""
		context.object.Num8MSR = 'NoChange'
		context.object.Num8AutoIKSR = False
		
		
		# 9
		context.object.Num9 = ""
		context.object.Num9R = ""
		context.object.Num9D = ""
		context.object.Num9S = ""
		context.object.Num9M = 'NoChange'
		context.object.Num9MR = 'NoChange'
		context.object.Num9MD = 'NoChange'
		context.object.Num9MS = 'NoChange'
		context.object.Num9AutoIKN = False
		context.object.Num9AutoIKR = False
		context.object.Num9AutoIKD = False
		context.object.Num9AutoIKS = False

		context.object.Num9SR = ""
		context.object.Num9MSR = 'NoChange'
		context.object.Num9AutoIKSR = False
		
		return {'FINISHED'}

	
# Set default
class NumControlSelectDefault(bpy.types.Operator):

	"""Set default values"""
	bl_label = "Fill Default"
	bl_idname = "view3d.num_select_default"
	
	preset = IntProperty( name = "preset", default = 0 )
	
	def execute(self, context):
		
		# reset first
		bpy.ops.view3d.num_select_reset()
		
		# ANIMAL #
		if(self.preset == 0):
			
			# 0
			bpy.context.object.Num0 = "Pelvis"
			bpy.context.object.Num0R = ""
			bpy.context.object.Num0D = ""
			
			# 1
			bpy.context.object.Num1 = "BackLeg_R"
			bpy.context.object.Num1R = "BackLegAnkle_R"
			bpy.context.object.Num1D = "BackLegLowerPV_R"
			
			# 2
			bpy.context.object.Num2 = "Hips"
			bpy.context.object.Num2R = "Spine1"
			bpy.context.object.Num2D = "Hips"
			
			# 3
			bpy.context.object.Num3 = "BackLeg_L"
			bpy.context.object.Num3R = "BackLegAnkle_L"
			bpy.context.object.Num3D = "BackLegLowerPV_L"
			
			# 4
			bpy.context.object.Num4 = "FrontLeg_R"
			bpy.context.object.Num4R = "FrontLegAnkle_R"
			bpy.context.object.Num4D = "FrontLegLowerPV_R"			
			
			# 5
			bpy.context.object.Num5 = "Chest"
			bpy.context.object.Num5R = "Spine2"
			bpy.context.object.Num5D = "Chest"
			
			# 6
			bpy.context.object.Num6 = "FrontLeg_L"
			bpy.context.object.Num6R = "FrontLegAnkle_L"
			bpy.context.object.Num6D = "FrontLegLowerPV_L"

			# 7
			bpy.context.object.Num7 = "FrontLegUpper_R"
			bpy.context.object.Num7R = "BackLegUpper_R"
			bpy.context.object.Num7D = "FrontLegUpper_R"
			
			# 8
			bpy.context.object.Num8 = "Head"
			bpy.context.object.Num8R = "Neck"
			bpy.context.object.Num8D = "Head"
			
			# 9
			bpy.context.object.Num9 = "FrontLegUpper_L"
			bpy.context.object.Num9R = "BackLegUpper_L"
			bpy.context.object.Num9D = "FrontLegUpper_L"
			
		# HUMAN #
		elif(self.preset == 1):
			
			# 0
			bpy.context.object.Num0 = "LegRoll_L"
			bpy.context.object.Num0R = "LegRoll_R"
			
		#	bpy.context.object.Num0M = 'TranslateRotate'
		#	bpy.context.object.Num0MR = 'TranslateRotate'
		#	bpy.context.object.Num0MD = 'TranslateRotate'
			
			# 1
			bpy.context.object.Num1 = "Leg_R"
			bpy.context.object.Num1R = "LegPV_R"
			bpy.context.object.Num1D = "LegTip_R"
			
		#	bpy.context.object.Num1M = 'TranslateRotate'
		#	bpy.context.object.Num1MR = 'TranslateRotate'
		#	bpy.context.object.Num1MD = 'Translate'
			
			# 2
			bpy.context.object.Num2 = "Pelvis"
			bpy.context.object.Num2R = "Hips"
			bpy.context.object.Num2D = "Spine"
			
		#	bpy.context.object.Num2M = 'TranslateRotate'
		#	bpy.context.object.Num2MR = 'TranslateRotate'
		#	bpy.context.object.Num2MD = 'TranslateRotate'
			
			# 3
			bpy.context.object.Num3 = "Leg_L"
			bpy.context.object.Num3R = "LegPV_L"
			bpy.context.object.Num3D = "LegTip_L"
			
		#	bpy.context.object.Num3M = 'TranslateRotate'
		#	bpy.context.object.Num3MR = 'TranslateRotate'
		#	bpy.context.object.Num3MD = 'Translate'
			
			# 4
			bpy.context.object.Num4 = "Hand_R"
			bpy.context.object.Num4R = "LowerArm_R"
			bpy.context.object.Num4D = "Digits_R"
			
		#	bpy.context.object.Num4M = 'Rotate'
		#	bpy.context.object.Num4MR = 'TranslateRotate'
		#	bpy.context.object.Num4MD = 'Rotate'
			
			bpy.context.object.Num4AutoIKN = True
		#	bpy.context.object.Num4MS = 'Translate'
			bpy.context.object.Num4S = 'ArmIK_R'
			bpy.context.object.Num4SR = "ArmPV_R"
			
			# 5
			bpy.context.object.Num5 = "Chest"
			bpy.context.object.Num5R = "Spine"
			bpy.context.object.Num5D = "Chest"
			
		#	bpy.context.object.Num5M = 'TranslateRotate'
		#	bpy.context.object.Num5MR = 'TranslateRotate'
		#	bpy.context.object.Num5MD = 'TranslateRotate'
			
			# 6
			bpy.context.object.Num6 = "Hand_L"
			bpy.context.object.Num6R = "LowerArm_L"
			bpy.context.object.Num6D = "Digits_L"
			
		#	bpy.context.object.Num6M = 'Rotate'
		#	bpy.context.object.Num6MR = 'TranslateRotate'
		#	bpy.context.object.Num6MD = 'Rotate'
			
			bpy.context.object.Num6AutoIKN = True
		#	bpy.context.object.Num6MS = 'Translate'
			bpy.context.object.Num6S = 'ArmIK_L'
			bpy.context.object.Num6SR = "ArmPV_L"

			# 7
			bpy.context.object.Num7 = "UpperArm_R"
			bpy.context.object.Num7R = "Clavicle_R"
			bpy.context.object.Num7D = "UpperArm_R"
			
		#	bpy.context.object.Num7M = 'Rotate'
		#	bpy.context.object.Num7MR = 'Rotate'
		#	bpy.context.object.Num7MD = 'Rotate'
			
			# 8
			bpy.context.object.Num8 = "Head"
			bpy.context.object.Num8R = "Neck"
			bpy.context.object.Num8D = "Head"
			
		#	bpy.context.object.Num8M = 'Rotate'
		#	bpy.context.object.Num8MR = 'Rotate'
		#	bpy.context.object.Num8MD = 'Rotate'
			
			# 9
			bpy.context.object.Num9 = "UpperArm_L"
			bpy.context.object.Num9R = "Clavicle_L"
			bpy.context.object.Num9D = "UpperArm_L"
			
		#	bpy.context.object.Num9M = 'Rotate'
		#	bpy.context.object.Num9MR = 'Rotate'
		#	bpy.context.object.Num9MD = 'Rotate'
			
		return {'FINISHED'}
		

############################################################################################
def register():
	bpy.utils.register_module(__name__)

	'''
	wm = bpy.context.window_manager
	km = wm.keyconfigs.addon.keymaps.new(name='Pose', space_type='EMPTY')
	
	kmi = km.keymap_items.new(NumControlSelect.bl_idname, 'NUMPAD_0', 'PRESS' )
	addon_keymaps.append((km, kmi))
	
	kmi = km.keymap_items.new(NumControlSelect.bl_idname, 'NUMPAD_1', 'PRESS' )
	addon_keymaps.append((km, kmi))
	
	kmi = km.keymap_items.new(NumControlSelect.bl_idname, 'NUMPAD_2', 'PRESS' )
	addon_keymaps.append((km, kmi))
	
	kmi = km.keymap_items.new(NumControlSelect.bl_idname, 'NUMPAD_3', 'PRESS' )
	addon_keymaps.append((km, kmi))
	
	kmi = km.keymap_items.new(NumControlSelect.bl_idname, 'NUMPAD_4', 'PRESS' )
	addon_keymaps.append((km, kmi))
	
	kmi = km.keymap_items.new(NumControlSelect.bl_idname, 'NUMPAD_5', 'PRESS' )
	addon_keymaps.append((km, kmi))
	
	kmi = km.keymap_items.new(NumControlSelect.bl_idname, 'NUMPAD_6', 'PRESS' )
	addon_keymaps.append((km, kmi))
	
	kmi = km.keymap_items.new(NumControlSelect.bl_idname, 'NUMPAD_7', 'PRESS' )
	addon_keymaps.append((km, kmi))
	
	kmi = km.keymap_items.new(NumControlSelect.bl_idname, 'NUMPAD_8', 'PRESS' )
	addon_keymaps.append((km, kmi))
	
	kmi = km.keymap_items.new(NumControlSelect.bl_idname, 'NUMPAD_9', 'PRESS' )
	addon_keymaps.append((km, kmi))
	
	kmi = km.keymap_items.new(NumControlSelect.bl_idname, 'NUMPAD_0', 'DOUBLE_CLICK' )
	addon_keymaps.append((km, kmi))
	
	kmi = km.keymap_items.new(NumControlSelect.bl_idname, 'NUMPAD_1', 'DOUBLE_CLICK' )
	addon_keymaps.append((km, kmi))
	
	kmi = km.keymap_items.new(NumControlSelect.bl_idname, 'NUMPAD_2', 'DOUBLE_CLICK' )
	addon_keymaps.append((km, kmi))
	
	kmi = km.keymap_items.new(NumControlSelect.bl_idname, 'NUMPAD_3', 'DOUBLE_CLICK' )
	addon_keymaps.append((km, kmi))
	
	kmi = km.keymap_items.new(NumControlSelect.bl_idname, 'NUMPAD_4', 'DOUBLE_CLICK' )
	addon_keymaps.append((km, kmi))
	
	kmi = km.keymap_items.new(NumControlSelect.bl_idname, 'NUMPAD_5', 'DOUBLE_CLICK' )
	addon_keymaps.append((km, kmi))
	
	kmi = km.keymap_items.new(NumControlSelect.bl_idname, 'NUMPAD_6', 'DOUBLE_CLICK' )
	addon_keymaps.append((km, kmi))
	
	kmi = km.keymap_items.new(NumControlSelect.bl_idname, 'NUMPAD_7', 'DOUBLE_CLICK' )
	addon_keymaps.append((km, kmi))
	
	kmi = km.keymap_items.new(NumControlSelect.bl_idname, 'NUMPAD_8', 'DOUBLE_CLICK' )
	addon_keymaps.append((km, kmi))
	
	kmi = km.keymap_items.new(NumControlSelect.bl_idname, 'NUMPAD_9', 'DOUBLE_CLICK' )
	addon_keymaps.append((km, kmi))
	'''

def unregister():
	'''
	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()
	'''
	bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
	register()
