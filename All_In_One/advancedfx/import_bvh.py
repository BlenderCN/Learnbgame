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


# <summary> searches a list of words for a word by lower case comparison </summary>
# <param name="words"> list to search </param>
# <param name="word"> word to find </param>
# <returns> less than 0 if not found, otherwise the first list index </returns>
def FindWordL(words, word):
	i = 0
	word = word.lower()
	while i < len(words):
		if words[i].lower() == word:
			return i
		i += 1
	return -1


# <summary> Scans the file till a line containing a lower case match of filterWord is found </summary>
# <param name="file"> file to read from </param>
# <param name="filterWord"> word to find </param>
# <returns> False on fail, otherwise same as ReadLineWords for this line </returns>
def ReadLineWordsFilterL(file, filterWord):
	while True:
		words = ReadLineWords(file)
		if 0 < len(words):
			if 0 <= FindWordL(words, filterWord):
				return words
		else:
			return False


# <summary> Scans the file till the channels line and reads channel information </summary>
# <param name="file"> file to read from </param>
# <returns> False on fail, otherwise channel indexes as follows: [Xposition, Yposition, Zposition, Zrotation, Xrotation, Yrotation] </returns>
def ReadChannels(file):
	words = ReadLineWordsFilterL(file, 'CHANNELS')
	
	if not words:
		return False

	channels = [\
	FindWordL(words, 'Xposition'),\
	FindWordL(words, 'Yposition'),\
	FindWordL(words, 'Zposition'),\
	FindWordL(words, 'Zrotation'),\
	FindWordL(words, 'Xrotation'),\
	FindWordL(words, 'Yrotation')\
	]
	
	idx = 0
	while idx < 6:
		channels[idx] -= 2
		idx += 1
			
	for channel in channels:
		if not (0 <= channel and channel < 6):
			return False
			
	return channels
	

def ReadRootName(file):
	words = ReadLineWordsFilterL(file, 'ROOT')
	
	if not words or len(words)<2:
		return False
		
	return words[1]
	
	
def ReadFrames(file):
	words = ReadLineWordsFilterL(file, 'Frames:')
	
	if not words or len(words)<2:
		return -1
		
	return int(words[1])

def ReadFrameTime(file):
	words = ReadLineWordsFilterL(file, 'Time:')
	
	if not words or len(words)<3:
		return -1
		
	return float(words[2])
	

def ReadFrame(file, channels):
	line = ReadLineWords(file)
	
	if len(line) < 6:
		return False;
	
	Xpos = float(line[channels[0]])
	Ypos = float(line[channels[1]])
	Zpos = float(line[channels[2]])
	Zrot = float(line[channels[3]])
	Xrot = float(line[channels[4]])
	Yrot = float(line[channels[5]])
	
	return [Xpos, Ypos, Zpos, Zrot, Xrot, Yrot]
	
class CameraData:
	def __init__(self,o):
		self.o = o
		self.curves = []

class BvhImporter(bpy.types.Operator, vs_utils.Logger):
	bl_idname = "advancedfx.bvhimporter"
	bl_label = "HLAE old Cam IO (.bvh)"
	bl_options = {'UNDO'}
	
	# Properties used by the file browser
	filepath: bpy.props.StringProperty(subtype="FILE_PATH")
	filename_ext: ".bvh"
	filter_glob: bpy.props.StringProperty(default="*.bvh", options={'HIDDEN'})

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

	cameraFov: bpy.props.FloatProperty(
		name="FOV",
		description="Camera engine FOV",
		min=1.0, max=179.0,
		default=90,
	)
	
	scaleFov: bpy.props.BoolProperty(
		name="Scale FOV",
		description="If to scale FOV by aspect ratio (required i.e. for CS:GO and Alien Swarm).",
		default=True,
	)

	screenWidth: bpy.props.FloatProperty(
		name="Screen Width",
		description="Only relevant when Scale FOV is set.",
		min=1.0, max=65536.0,
		default=16.0,
	)

	screenHeight: bpy.props.FloatProperty(
		name="Screen Height",
		description="Only relevant when Scale FOV is set.",
		min=1.0, max=65536.0,
		default=9.0,
	)
	
	# class properties
	blenderCamUpQuat = mathutils.Quaternion((math.cos(0.5 * math.radians(90.0)), math.sin(0.5* math.radians(90.0)), 0.0, 0.0))
	
	def execute(self, context):
		ok = self.readBvh(context)
		
		self.errorReport("Error report")
		
		return {'FINISHED'}
	
	def invoke(self, context, event):
		bpy.context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
	
	def createCamera(self, context, camName):
		
		camBData = bpy.data.cameras.new(camName)
		o = bpy.data.objects.new(camName, camBData)

		context.scene.collection.objects.link(o)

		#vs_utils.select_only(o)
			
		camData = CameraData(o)
			
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
	
	def readBvh(self, context):
		fps = context.scene.render.fps
		
		camData = self.createCamera(context,"BvhCam")
		
		if camData is None:
			self.error("Failed to create camera.")
			return False
		
		#vs_utils.select_only(camData.o)
		camData.o.data.angle = self.calcCameraFov()
		
		file = None
		
		try:
			file = open(self.filepath, 'rU')
			
			rootName = ReadRootName(file)
			if not rootName:
				self.error('Failed parsing ROOT.')
				return False
				
			print('ROOT:', rootName)

			channels = ReadChannels(file)
			if not channels:
				self.error('Failed parsing CHANNELS.')
				return False
				
			frames = ReadFrames(file);
			if frames < 0:
				self.error('Failed parsing Frames.')
				return False
				
			if 0 == frames: frames = 1
			
			frames = float(frames)
				
			frameTime = ReadFrameTime(file)
			if not frameTime:
				self.error('Failed parsing Frame Time.')
				return False
				
			frameCount = int(0)
			
			lastQuat = None
			
			while True:
				frame = ReadFrame(file, channels)
				if not frame:
					break
				
				frameCount += 1
				
				BTT = (float(frameTime) * float(frameCount-1))

				BYP = -frame[0]
				BZP =  frame[1]
				BXP = -frame[2]

				BZR = -frame[3]
				BXR = -frame[4]
				BYR =  frame[5]
				
				time = BTT
				time = 1.0 + time * fps
				
				renderOrigin = mathutils.Vector((-BYP,BXP,BZP)) * self.global_scale
				
				curves = camData.curves
				
				afx_utils.AddKey_Location(self.interKey, curves[0+0].keyframe_points, curves[0+1].keyframe_points, curves[0+2].keyframe_points, time, renderOrigin)
				
				qAngle = afx_utils.QAngle(BXR,BYR,BZR)
				
				quat = qAngle.to_quaternion() @ self.blenderCamUpQuat
				
				# Make sure we travel the short way:
				if lastQuat:
					dp = lastQuat.dot(quat)
					if dp < 0:
						quat.negate()
				
				lastQuat = quat
				
				afx_utils.AddKey_Rotation(self.interKey, curves[0+3].keyframe_points, curves[0+4].keyframe_points, curves[0+5].keyframe_points, curves[0+6].keyframe_points, time, quat)
			
			if not frameCount == frames:
				self.error("Frames are missing in BVH file.")
				return False
			
		finally:
			if file is not None:
				file.close()
		
		return True
