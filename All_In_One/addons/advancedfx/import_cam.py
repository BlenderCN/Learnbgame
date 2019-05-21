import gc
import math
import os
import struct

import bpy, bpy.props, bpy.ops
import mathutils

from io_scene_valvesource import utils as vs_utils

from advancedfx import utils as afx_utils

# <summary> reads a line from file and separates it into words by splitting whitespace </summary>
# <param name="file"> file to read from </param>
# <returns> list of words </returns>
def ReadLineWords(file):
	line = file.readline()
	words = [ll for ll in line.split() if ll]
	return words

def AlienSwarm_FovScaling(width, height, fov):
	
	if 0 == height:
		return fov
	
	engineAspectRatio = width / height;
	defaultAscpectRatio = 4.0 / 3.0;
	ratio = engineAspectRatio / defaultAscpectRatio;
	halfAngle = 0.5 * fov * (2.0 * math.pi / 360.0);
	t = ratio * math.tan(halfAngle);
	return 2.0 * math.atan(t) / (2.0 *  math.pi / 360.0);

class CameraData:
	def __init__(self,o,c):
		self.o = o
		self.c = c
		self.curves = []

class CamImporter(bpy.types.Operator, vs_utils.Logger):
	bl_idname = "advancedfx.camimporter"
	bl_label = "HLAE Camera IO (.cam)"
	bl_options = {'UNDO'}
	
	# Properties used by the file browser
	filepath: bpy.props.StringProperty(subtype="FILE_PATH")
	filename_ext: ".cam"
	filter_glob: bpy.props.StringProperty(default="*.cam", options={'HIDDEN'})

	# Custom properties
	
	interKey: bpy.props.BoolProperty(
		name="Add interpolated key frames",
		description="Create interpolated key frames for frames in-between the original key frames.",
		default=False)
	
	global_scale: bpy.props.FloatProperty(
		name="Scale",
		description="Scale everything by this value",
		min=0.000001, max=1000000.0,
		soft_min=0.001, soft_max=1.0,
		default=0.01,
	)
	
	# class properties
	blenderCamUpQuat = mathutils.Quaternion((math.cos(0.5 * math.radians(90.0)), math.sin(0.5* math.radians(90.0)), 0.0, 0.0))
	
	def execute(self, context):
		ok = self.readCam(context)
		
		self.errorReport("Error report")
		
		return {'FINISHED'}
	
	def invoke(self, context, event):
		bpy.context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
	
	def createCamera(self, context, camName):
		
		camBData = bpy.data.cameras.new(camName)
		o = bpy.data.objects.new(camName, camBData)
		c = bpy.data.cameras[o.name]

		context.scene.collection.objects.link(o)

		#vs_utils.select_only(o)
			
		camData = CameraData(o,c)
			
		# Rotation mode:
		if o.rotation_mode != 'QUATERNION':
			o.rotation_mode = 'QUATERNION'
				
		
		# Create actions and their curves (boobs):
		
		o.animation_data_create()
		action = bpy.data.actions.new(name="game_data")
		o.animation_data.action = action
		
		for i in range(3):
			camData.curves.append(action.fcurves.new("location",index = i))
		
		for i in range(4):
			camData.curves.append(action.fcurves.new("rotation_quaternion",index = i))
			
		c.animation_data_create()
		action = bpy.data.actions.new(name="game_data")
		c.animation_data.action = action
			
		camData.curves.append(action.fcurves.new("lens"))
			
		return camData
	
	# <returns> Camera FOV in radians </returns>
	def calcCameraFov(self):
		fov = math.radians(self.cameraFov)
	
		if self.scaleFov:
			defaultAspectRatio = 4.0/3.0
			engineAspectRatio = (self.screenWidth / self.screenHeight) if 0 != self.screenHeight else defaultAspectRatio
			ratio = engineAspectRatio / defaultAspectRatio
			halfAngle = fov * 0.5
			fov = math.atan(math.tan(halfAngle) * ratio) * 2.0
		
		return fov
	
	def readCam(self, context):
		fps = context.scene.render.fps
		
		width = context.scene.render.pixel_aspect_x * context.scene.render.resolution_x
		height = context.scene.render.pixel_aspect_y * context.scene.render.resolution_y
		
		camData = self.createCamera(context,"afxCam")
		
		if camData is None:
			self.error("Failed to create camera.")
			return False
		
		#vs_utils.select_only( camData.o )
		
		file = None
		
		try:
			file = open(self.filepath, 'rU')
			
			version = 0
			scaleFov = 'none'
			
			words = ReadLineWords(file)
			
			if not(2 <= len(words) and 'advancedfx' == words[0] and 'Cam' == words[1]):
				self.error('Not an valid advancedfx Cam file.')
				return False
			
			while True:
				words = ReadLineWords(file)
				
				if(1 <= len(words)):
					if 'DATA' == words[0]:
						break;
					if 'version' == words[0] and 2 <= len(words):
						version = int(words[1])
					if 'scaleFov' == words[0] and 2 <= len(words):
						scaleFov = words[1]
			
			if(1 != version):
				self.error("Invalid version, only 1 is supported.")
				return False
				
			if not(scaleFov in ['none', 'alienSwarm']):
				self.error("Unsupported scaleFov value.")
				return False

			lastTime = None
			lastQuat = None
			
			while True:
				words = ReadLineWords(file)
				
				if not( 8 <= len(words)):
					break
					
				time = float(words[0])
				
				if not lastTime:
					lastTime = time
					
				orgTime = time
					
				time = time -lastTime
				
				time = 1.0 + time * fps
				
				renderOrigin = mathutils.Vector((-float(words[2]),float(words[1]),float(words[3]))) * self.global_scale
				qAngle = afx_utils.QAngle(float(words[5]),float(words[6]),float(words[4]))
				
				quat = qAngle.to_quaternion() @ self.blenderCamUpQuat
				
				# Make sure we travel the short way:
				if lastQuat:
					dp = lastQuat.dot(quat)
					if dp < 0:
						quat.negate()
				
				lastQuat = quat
				
				fov = float(words[7])
				
				if 'alienSwarm' == scaleFov:
					fov = AlienSwarm_FovScaling(width, height, fov)
				
				lens = camData.c.sensor_width / (2.0 * math.tan(math.radians(fov) / 2.0))
				
				curves = camData.curves
				
				afx_utils.AddKey_Location(self.interKey, curves[0+0].keyframe_points, curves[0+1].keyframe_points, curves[0+2].keyframe_points, time, renderOrigin)
				
				afx_utils.AddKey_Rotation(self.interKey, curves[0+3].keyframe_points, curves[0+4].keyframe_points, curves[0+5].keyframe_points, curves[0+6].keyframe_points, time, quat)
				
				afx_utils.AddKey_Value(self.interKey, curves[0+7].keyframe_points, time, lens)
			
		finally:
			if file is not None:
				file.close()
		
		return True
