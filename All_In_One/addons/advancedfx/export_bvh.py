import gc
import math
import os
import struct

import bpy, bpy.props, bpy.ops
import mathutils

from io_scene_valvesource import utils as vs_utils

from .utils import QAngle

# <summary> Formats a float value to be suitable for bvh output </summary>
def FloatToBvhString(value):
	return "{0:f}".format(value)

def WriteHeader(file, frames, frameTime):
	file.write("HIERARCHY\n")
	file.write("ROOT MdtCam\n")
	file.write("{\n")
	file.write("\tOFFSET 0.00 0.00 0.00\n")
	file.write("\tCHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation\n")
	file.write("\tEnd Site\n")
	file.write("\t{\n")
	file.write("\t\tOFFSET 0.00 0.00 -1.00\n")
	file.write("\t}\n")
	file.write("}\n")
	file.write("MOTION\n")
	file.write("Frames: "+str(frames)+"\n")
	file.write("Frame Time: "+FloatToBvhString(frameTime)+"\n")
	
class BvhExporter(bpy.types.Operator, vs_utils.Logger):
	bl_idname = "advancedfx.bvhexporter"
	bl_label = "HLAE old Cam IO (.bvh)"
	bl_options = {'UNDO'}
	
	# Properties used by the file browser
	filepath: bpy.props.StringProperty(subtype="FILE_PATH")
	filename_ext: ".bvh"
	filter_glob: bpy.props.StringProperty(default="*.bvh", options={'HIDDEN'})

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
		
		if obj is None:
			self.error("No object selected.")
			return False
		
		lastRot = None
		
		unRot = mathutils.Matrix.Rotation(math.radians(-90.0 if "CAMERA" == obj.type else 0.0), 4, 'X')
		
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
				rot = mat.to_euler('XZY') if lastRot is None else mat.to_euler('XZY', lastRot)
				lastRot = rot
				
				loc = mathutils.Vector((loc[1],-loc[0],loc[2]))
				
				X = -loc[1] * self.global_scale
				Y =  loc[2] * self.global_scale
				Z = -loc[0] * self.global_scale
				
				qAngleVec = mathutils.Vector((rot[0],rot[2],rot[1]))
				
				ZR = -math.degrees(qAngleVec[2])
				XR = -math.degrees(qAngleVec[0])
				YR = math.degrees(qAngleVec[1])
				
				S = "" +FloatToBvhString(X) +" " +FloatToBvhString(Y) +" " +FloatToBvhString(Z) +" " +FloatToBvhString(ZR) +" " +FloatToBvhString(XR) +" " +FloatToBvhString(YR) + "\n"
				file.write(S)
			
		finally:
			if file is not None:
				file.close()
		
		scene.frame_set(frame_current)
		
		return True
