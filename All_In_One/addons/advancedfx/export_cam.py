import gc
import math
import os
import struct

import bpy, bpy.props, bpy.ops
import mathutils

from io_scene_valvesource import utils as vs_utils

# <summary> Formats a float value to be suitable for bvh output </summary>
def FloatToBvhString(value):
	return "{0:f}".format(value)

def WriteHeader(file, frames, frameTime):
	file.write("advancedfx Cam\n")
	file.write("version 1\n")
	file.write("scaleFov none\n")
	file.write("channels time xPosition yPosition zPositon xRotation yRotation zRotation fov\n")
	file.write("DATA\n")


class CamExporter(bpy.types.Operator, vs_utils.Logger):
	bl_idname = "advancedfx.camexporter"
	bl_label = "HLAE Camera IO (.cam)"
	bl_options = {'UNDO'}
	
	# Properties used by the file browser
	filepath: bpy.props.StringProperty(subtype="FILE_PATH")
	filename_ext: ".cam"
	filter_glob: bpy.props.StringProperty(default="*.cam", options={'HIDDEN'})

	# Custom properties
	global_scale: bpy.props.FloatProperty(
		name="Scale",
		description="Scale everything by this value",
		min=0.000001, max=1000000.0,
		soft_min=1.0, soft_max=1000.0,
		default=100.0,
	)
	
	frame_start: bpy.props.IntProperty(
		name="Start Frame",
		description="Starting frame to export",
		default=0,
	)
	frame_end: bpy.props.IntProperty(
		name="End Frame",
		description="End frame to export",
		default=0,
	)


	def execute(self, context):
		ok = self.writeBvh(context)
		
		self.errorReport("Error report")
		
		return {'FINISHED'}
	
	def invoke(self, context, event):
		self.frame_start = context.scene.frame_start
		self.frame_end = context.scene.frame_end
		
		bpy.context.window_manager.fileselect_add(self)
		
		return {'RUNNING_MODAL'}
	
	def writeBvh(self, context):
		scene = context.scene
		frame_current = scene.frame_current
		fps = context.scene.render.fps
		
		obj = context.active_object
		
		if (obj is None) or (obj.type != 'CAMERA'):
			self.error("No camera selected.")
			return False
			
		cam = obj.data
		
		lastRot = None
		
		unRot = mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'X')
		
		file = None
		
		try:
			file = open(self.filepath, "w", encoding="utf8", newline="\n")
			
			frameCount = self.frame_end -self.frame_start +1
			if frameCount < 0: frameCount = 0
			
			frameTime = 1.0
			if 0.0 != fps: frameTime = frameTime / fps
			
			WriteHeader(file, frameCount, frameTime)
		
			for frame in range(self.frame_start, self.frame_end + 1):
				scene.frame_set(frame)
				
				mat = obj.matrix_world
				mat = mat @ unRot
				
				loc = mat.to_translation()
				rot = mat.to_euler('YXZ') if lastRot is None else mat.to_euler('YXZ', lastRot)
				lastRot = rot
				
				loc = self.global_scale * mathutils.Vector((loc[1],-loc[0],loc[2]))
				
				qAngleVec = mathutils.Vector((math.degrees(rot[1]),-math.degrees(rot[0]),math.degrees(rot[2])))
				
				# lens = camData.c.sensor_width / (2.0 * math.tan(math.radians(fov) / 2.0))
				fov = math.degrees(2.0 * math.atan((cam.sensor_width / cam.lens) / 2.0))
				
				S = ""+FloatToBvhString((frame-1) * frameTime) +" " +FloatToBvhString(loc[0]) +" " +FloatToBvhString(loc[1]) +" " +FloatToBvhString(loc[2]) +" " +FloatToBvhString(qAngleVec[0]) +" " +FloatToBvhString(qAngleVec[1]) +" " +FloatToBvhString(qAngleVec[2]) +" " +FloatToBvhString(fov) + "\n"
				file.write(S)
			
		finally:
			if file is not None:
				file.close()
		
		scene.frame_set(frame_current)
		
		return True
