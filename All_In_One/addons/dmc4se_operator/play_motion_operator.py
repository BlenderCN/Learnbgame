import os
import bpy
import random
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import (CollectionProperty, StringProperty, BoolProperty, EnumProperty, FloatProperty)
from . import glb

class PlayMotionOperator(bpy.types.Operator):
	bl_idname = "dmc4se.play_motion"
	bl_label = "Play Motion"
	
	index = bpy.props.IntProperty(default=-1)
	op = bpy.props.StringProperty(default="PLAY")
	
	def execute(self, context):
		motion = context.scene.motion
		model = context.scene.model
		op = self.op
		if op == 'PAUSE':
			self.pause(context)
			return {"FINISHED"}
		if op == 'PLAY':
			if self.index not in glb.all_motions:
				self.index = self.find_next()
		elif op == 'NEXT':
			self.index = self.find_next()
		elif op == 'PREV':
			self.index = self.find_prev()
		else:
			return {'FINISHED'}
		
		actions = glb.all_motions[self.index]
		max_frame = 0
		for action in actions:
			armt = context.scene.objects[action.target_user]
			armt.animation_data.action = action
			max_frame = max(max_frame, action.frame_range[1])
		context.scene.frame_current = 1
		context.scene.frame_end = max_frame
		self.play(context)
			
		return {"FINISHED"}
	
	def play(self, context):
		if not context.screen.is_animation_playing:
			bpy.ops.screen.animation_play()
		context.scene.motion_index = self.index
	
	def pause(self, context):
		if context.screen.is_animation_playing:
			bpy.ops.screen.animation_cancel()
	
	def find_next(self):
		for index in glb.motion_indices:
			if index > self.index:
				return index
		return glb.motion_indices[-1]
	
	def find_prev(self):
		prev_index = glb.motion_indices[0]
		for index in glb.motion_indices:
			if index >= self.index:
				break
			prev_index = index
		return prev_index
			