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
	"name": "Get Step Length",
	"author": "Cenek Strichel",
	"version": (1, 0, 2),
	"blender": (2, 79, 0),
	"location": "View 3D > Tools",
	"description": "Compare step length for Quadruped",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}
	

import bpy
from bpy.props import BoolProperty, FloatVectorProperty, FloatProperty
from mathutils import *
from math import *


bpy.types.Object.Distance = bpy.props.FloatProperty( name = "Distance", description = "", default = 0.000 )
bpy.types.Object.Scale = bpy.props.FloatProperty( name = "Scale", description = "", default = 0.000 )


bpy.types.Scene.StepFirst = bpy.props.FloatVectorProperty( name = "StepFirst", description = "")
bpy.types.Scene.StepSecond = bpy.props.FloatVectorProperty( name = "StepSecond", description = "")
bpy.types.Scene.StepStart = bpy.props.BoolProperty( name = "StepStart", description = "", default = False)


class StepLengthPanel(bpy.types.Panel):
	
	
	bl_label = "Get Step Length"
	bl_idname = "STEP_LENGTH_PANEL"
	
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Tools"
	bl_context = "posemode"


	def draw(self, context):
		
		layout = self.layout
		obj = context.object
		scn = bpy.context.scene
		
		# label
		row = layout.row(align=True)
		if(obj.Distance == 0):
			row.label("Source:")

		else:
			row.label("Target:")
	
		# buttons start / end
		row = layout.row(align=True)
				
		if( scn.StepStart == False ):

			textFirst = "Start"
			if(obj.Distance > 0):
				textFirst = "New Start"
				
			row.operator("cenda.step_length", text=textFirst, icon = 'FRAME_PREV').firstStep = True
			
		else:
			
			textLast = "End"
			if(obj.Distance > 0):
				textLast = "New End"

			row.operator("cenda.step_length", text=textLast, icon='FRAME_NEXT').firstStep = False
		
		
		# refresh
		row.operator("cenda.step_length_reset", icon = 'FILE_REFRESH')
		row = layout.row(align=True)
		
		# labels
		box = layout.box()
		
		row = box.row(align=True)
		distRound = trunc(obj.Distance * 1000)
		row.label( "Distance: " + str(distRound / 1000) )
		
		row = box.row(align=True)
		scaleRound = trunc(obj.Scale * 1000)
		row.label( "Scale: " + str(scaleRound / 1000) )


# rename button	
class StepLength(bpy.types.Operator):
	
	"""Compute scale for length"""
	bl_label = "Step Length"
	bl_idname = "cenda.step_length"
	
	
	firstStep = BoolProperty(name="First Step",default=True)


	def execute(self, context ):

		scn = bpy.context.scene
		
		# FIRST STEP #
		if(self.firstStep):
			scn.StepFirst = Vector((bpy.context.active_pose_bone.location.x, bpy.context.active_pose_bone.location.y, bpy.context.active_pose_bone.location.z))
			scn.StepStart = True

		# SECOND STEP #
		else:
			# i dont want reference
			scn.StepSecond = Vector((bpy.context.active_pose_bone.location.x, bpy.context.active_pose_bone.location.y, bpy.context.active_pose_bone.location.z))

			distance = Vector(scn.StepFirst).length + Vector(scn.StepSecond).length

			
			if(bpy.context.object.Distance == 0):
				bpy.context.object.Distance = distance
				
				
			else:	

				bpy.context.object.Scale =  bpy.context.object.Distance / distance	
				
			scn.StepStart = False
			

		return{'FINISHED'} 
	
	
# rename button	
class StepLengthReset(bpy.types.Operator):
	
	"""Reset value for new use"""
	bl_label = "Reset"
	bl_idname = "cenda.step_length_reset"
	
	def execute(self, context ):
		
		bpy.context.object.Distance = 0
		bpy.context.object.Scale = 0
	#	bpy.types.Scene.StepFirst == Vector((0,0,0))
	#	bpy.types.Scene.StepSecond == Vector((0,0,0))
		
		bpy.context.scene.StepStart = False
		
		return{'FINISHED'}
	
			
################################################################
# register #	
def register():
	bpy.utils.register_module(__name__)
	
def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()