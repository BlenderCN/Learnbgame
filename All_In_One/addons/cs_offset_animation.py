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
	"name": "Offset Animation",
	"author": "Cenek Strichel",
	"version": (1, 0, 5),
	"blender": (2, 79, 0),
	"location": "Animation (Tools Panel) > Offset Animation",
	"description": "Offset for animated object and bones",
	"category": "Cenda Tools",
	"wiki_url": "https://github.com/CenekStrichel/CendaTools/wiki",
	"tracker_url": "https://github.com/CenekStrichel/CendaTools/issues"
	}
	

import bpy

from bpy.props import BoolProperty, FloatVectorProperty, FloatProperty, IntProperty
from mathutils import *
from math import *


## PANEL ##############################################################
class OffsetAnimationPanel(bpy.types.Panel):
	
	
	bl_label = "Offset"
	bl_idname = "OFFSET_ANIMATION_PANEL"
	
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Animation"
	
	bpy.types.Scene.showSetOffset = BoolProperty(name="ShowSetOffset",default=False) # is reference setted?
	bpy.types.Scene.autokeySetting = BoolProperty(name="AutoKey",default=True) # previous setting for autokey
	
	bpy.types.Scene.UseRange = BoolProperty(name="Use Range",default=False) 
	bpy.types.Scene.StartRange = IntProperty(name = "Start", default = 10)
	bpy.types.Scene.EndRange = IntProperty(name = "End", default = 50)
	
	
	def draw(self, context):
		
		layout = self.layout
		scn = context.scene
		
		# First button
		row = layout.row(align=True)
		row.operator("anim.offset_animation_set", icon = "OUTLINER_DATA_ARMATURE" ,text="Reference").reference = True
		
		# Second button
		row = layout.row(align=True)
		row.operator("anim.offset_animation_set", icon = "POSE_DATA", text="Offset").reference = False
		
		if( context.scene.showSetOffset ):
			row.enabled = True
		else:
			row.enabled = False	

		box = layout.box()
		row = box.row(align=True)
		
		row.prop( scn, "UseRange" )
		
		if(scn.UseRange):

			row = box.row(align=True)

			row.prop( scn, "StartRange" )
			row.operator("anim.offset_pick_time", text="", icon = 'EYEDROPPER').start = True
			
			row = box.row(align=True)
			row.prop( scn, "EndRange" )
			row.operator("anim.offset_pick_time", text="", icon = 'EYEDROPPER').start = False
		
		
class PickRangeTime(bpy.types.Operator):
	
	"""Pick time from Timeline"""
	bl_idname = "anim.offset_pick_time"
	bl_label = "Offset Animation Pick"

	start = BoolProperty(name="Start",default=True)

	def execute(self, context):
		
		scn = context.scene
		
		if(self.start):
			scn.StartRange = scn.frame_current
			
		else:
			scn.EndRange = scn.frame_current
		
		return {'FINISHED'}
	
				
################################################################
class OffsetAnimationSet(bpy.types.Operator):


	bl_idname = "anim.offset_animation_set"
	bl_label = "Offset Animation Set"

	reference = BoolProperty(name="Reference",default=True) #  setting reference
	
	
	def execute(self, context):
	
		# you need bone with action
		if(context.object.animation_data.action == None):
			self.report({'ERROR'},"No Action for Offset Found")
			return {'FINISHED'}
	
		# BONES #	
		if bpy.context.active_object.type == 'ARMATURE':
		
			armature = bpy.context.active_object.data

			for bone in armature.bones:
				
				bonePose = bpy.context.object.pose.bones[ bone.name ]
				
				currentLocation = bonePose.location
				currentRotation = Vector (( bonePose.rotation_euler[0], bonePose.rotation_euler[1], bonePose.rotation_euler[2] ))
				currentQRotation = Vector (( bonePose.rotation_quaternion[0], bonePose.rotation_quaternion[1], bonePose.rotation_quaternion[2], bonePose.rotation_quaternion[3] ))
				currentScale = Vector (( bonePose.scale[0], bonePose.scale[1], bonePose.scale[2] ))

				if(self.reference):
					SaveOffset( currentLocation, currentRotation, currentScale, currentQRotation, bonePose )
					
				else:
					ApplyOffset( currentLocation, currentRotation, currentScale, currentQRotation, bonePose )
					
		# OBJECTS #
		else:
			
			bonePose = bpy.context.active_object
				
			currentLocation = bonePose.location
			currentRotation = Vector (( bonePose.rotation_euler[0], bonePose.rotation_euler[1], bonePose.rotation_euler[2] ))
			currentQRotation = Vector (( bonePose.rotation_quaternion[0], bonePose.rotation_quaternion[1], bonePose.rotation_quaternion[2], bonePose.rotation_quaternion[3] ))
			currentScale = Vector (( bonePose.scale[0], bonePose.scale[1], bonePose.scale[2] ))

			if(self.reference):
				SaveOffset( currentLocation, currentRotation, currentScale, currentQRotation, bonePose )
				
			else:
				ApplyOffset( currentLocation, currentRotation, currentScale, currentQRotation, bonePose )
		
		
		####################################################
		# Post setting
		####################################################
		if(self.reference):
			
			bpy.types.Scene.autokeySetting = context.scene.tool_settings.use_keyframe_insert_auto
			context.scene.tool_settings.use_keyframe_insert_auto = False

			bpy.types.Scene.showSetOffset = True
			
		else:

			context.scene.tool_settings.use_keyframe_insert_auto = bpy.types.Scene.autokeySetting
			
			bpy.types.Scene.showSetOffset = False


		RedrawTimeline()
			
		# update motions paths if displayed
		try:
			
			if bpy.context.active_object.type == 'ARMATURE':
				bpy.ops.pose.paths_update()
			else:
				bpy.ops.object.paths_update()
				
		except:
			pass

		return {'FINISHED'}


def SaveOffset( currentLocation, currentRotation, currentScale, currentQRotation, bonePose ):
	
	# BONES #
	if bpy.context.active_object.type == 'ARMATURE':
		
		bpy.types.PoseBone.LocStart = bpy.props.FloatVectorProperty(name="LocStart")
		bonePose.LocStart = currentLocation

		bpy.types.PoseBone.RotStart = bpy.props.FloatVectorProperty(name="RotStart")
		bonePose.RotStart = currentRotation
		
		bpy.types.PoseBone.QRotStart = bpy.props.FloatVectorProperty(name="QRotStart", size = 4)
		bonePose.QRotStart = currentQRotation
		
		bpy.types.PoseBone.SclStart = bpy.props.FloatVectorProperty(name="SclStart")
		bonePose.SclStart = currentScale
	
	# OBJECT #	
	else:
		
		bpy.types.Object.LocStart = bpy.props.FloatVectorProperty(name="LocStart")
		bonePose.LocStart = currentLocation

		bpy.types.Object.RotStart = bpy.props.FloatVectorProperty(name="RotStart")
		bonePose.RotStart = currentRotation
		
		bpy.types.Object.QRotStart = bpy.props.FloatVectorProperty(name="QRotStart", size = 4)
		bonePose.QRotStart = currentQRotation
		
		bpy.types.Object.SclStart = bpy.props.FloatVectorProperty(name="SclStart")
		bonePose.SclStart = currentScale		
		
		
def ApplyOffset( currentLocation, currentRotation, currentScale, currentQRotation, bonePose ):

	# location
	locDifference = ( Vector(bonePose.LocStart) - Vector( currentLocation ) )
	
	# rotation
	rotDifference = ( Vector(bonePose.RotStart) - Vector( currentRotation ) )	
	qRotDifference = ( Vector(bonePose.QRotStart) - Vector( currentQRotation ) )
	
	# scale
	sclDifference = ( Vector(bonePose.SclStart) - Vector( currentScale ) )

	# do offset
	OffsetAnimation( locDifference, rotDifference, qRotDifference, sclDifference, bonePose )

	del bonePose["LocStart"]
	del bonePose["RotStart"]
	del bonePose["QRotStart"]
	del bonePose["SclStart"]
	
										
## ONLY FOR SET OFFSET ##############################################################
def OffsetAnimation( locDifference, rotDifference, qRotDifference, sclDifference, bonePose ):
	 
	
	scn = bpy.context.scene
	obj = bpy.context.object
	
	# get current action
	action = obj.animation_data.action
	
	locIndex = 0
	rotIndex = 0
	rotQIndex = 0
	sclIndex = 0
	
	
	# Current action
	if ( (obj.animation_data is not None) and (obj.animation_data.action is not None) ):
		
		# num of channels
		numCurves = len( action.fcurves )

		for i in range(numCurves):
			
			fcurveDataPath = action.fcurves[ i ].data_path

			###################################################	
			# BONE #
			###################################################
			if(bpy.context.active_pose_bone != None):
				
				try:
					# find bone by name
					if( (bonePose.name) == ( str(fcurveDataPath).split("\"")[1] ) ):
				
						# LOCATION # - TODO - Rewrite duplicity code
						if ( ".location" in fcurveDataPath ):
							
							numKeyframes = len( action.fcurves[ i ].keyframe_points )
							offset = locDifference[ locIndex ]
							locIndex += 1
							
							CurveOffset(action, i, offset, numKeyframes)
						
						
						# ROTATION #
						elif ( ".rotation_euler" in fcurveDataPath ):

							numKeyframes = len( action.fcurves[ i ].keyframe_points )
							offset = rotDifference[ rotIndex ]
							rotIndex += 1
		
							CurveOffset(action, i, offset, numKeyframes)


						# Q ROTATION #
						elif ( ".rotation_quaternion" in fcurveDataPath ):

							numKeyframes = len( action.fcurves[ i ].keyframe_points )
							offset = qRotDifference[ rotQIndex ]
							rotQIndex += 1

							CurveOffset(action, i, offset, numKeyframes)
								
								
						# SCALE #
						elif ( ".scale" in fcurveDataPath ):
								
							numKeyframes = len( action.fcurves[ i ].keyframe_points )
							offset = sclDifference[ sclIndex ]
							sclIndex += 1

							CurveOffset(action, i, offset, numKeyframes)
							
				except:			
					print("Can not find data path: " + str(fcurveDataPath) )


	
			###################################################		
			# OBJECT #
			###################################################
			else:

				# LOCATION #
				if ( "location" in fcurveDataPath ):
					
					numKeyframes = len( action.fcurves[ i ].keyframe_points )
					offset = locDifference[ locIndex ]
					locIndex += 1
					
					CurveOffset(action, i, offset, numKeyframes)
				
				
				# ROTATION #
				elif ( "rotation_euler" in fcurveDataPath ):

					numKeyframes = len( action.fcurves[ i ].keyframe_points )
					offset = rotDifference[ rotIndex ]
					rotIndex += 1

					CurveOffset(action, i, offset, numKeyframes)
						
						
				# Q ROTATION #
				elif ( "rotation_quaternion" in fcurveDataPath ):

					numKeyframes = len( action.fcurves[ i ].keyframe_points )
					offset = qRotDifference[ rotQIndex ]
					rotQIndex += 1

					CurveOffset(action, i, offset, numKeyframes)


				# SCALE #
				elif ( "scale" in fcurveDataPath ):
						
					numKeyframes = len( action.fcurves[ i ].keyframe_points )
					offset = sclDifference[ sclIndex ]
					sclIndex += 1

					CurveOffset(action, i, offset, numKeyframes)	


def CurveOffset(action, index, offset, numKeyframes):
	
	scn = bpy.context.scene
	
	for j in range(numKeyframes):
		
		key = action.fcurves[ index ].keyframe_points[ j ]
		
		if( scn.UseRange ):
			if( (key.co.x >= scn.StartRange) and (key.co.x <= scn.EndRange) ):
				key.co.y -= offset
				key.handle_left.y -= offset
				key.handle_right.y -= offset
		else:
			key.co.y -= offset
			key.handle_left.y -= offset
			key.handle_right.y -= offset
			
				
# autokey is turned off, so I have to redraw autokey button
def RedrawTimeline():
	
	# redraw autokey state
	for area in bpy.context.screen.areas:
		if area.type == 'TIMELINE':
			area.tag_redraw()
			
						
################################################################
# register #
	
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()