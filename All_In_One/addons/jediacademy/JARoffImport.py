import bpy
import math
import struct

### The new operator ###
class Operator(bpy.types.Operator):
	#everything is scaled down by this factor
	SCALE = 10
	bl_idname = "import_scene.ja_roff"
	bl_label = "Import JA ROFF (.rof)"
	
	#gets set by the file select window - internal Blender Magic or whatever.
	filepath = bpy.props.StringProperty(name="File Path", description="File path used for importing the ROFF file", maxlen= 1024, default="")
	
	def execute(self, context):
		self.ImportStart()
		return {'FINISHED'}

	def invoke(self, context, event):
		windowMan = context.window_manager
		#sets self.properties.filename and runs self.execute()
		windowMan.fileselect_add(self)
		return {'RUNNING_MODAL'}
	
	def ImportStart(self):
		filename = bpy.path.ensure_ext( self.filepath, ".rof" )
		objlist = bpy.context.selected_objects
		if len(objlist) != 1:
			self.report({"ERROR"}, "Please select exactly one object!")
			return
		obj = objlist[0]
		try:
			file = open(filename, "rb")
			# I don't know what the last 4 bytes are, they (nearly) always contain (int) 0 (once it was 7, once 8...)
			ident, version, frames, frameDuration = struct.unpack("4s3i4x", file.read(20))
			if ident != b"ROFF":
				self.report({"ERROR"}, "That's no ROFF file!")
				return
			if version != 2:
				self.report({"ERROR"}, "Wrong ROFF version, only 2 is supported! (file is "+str(version)+")")
				return
			if obj.rotation_mode != "XYZ":
				self.report({"ERROR"}, "Object's rotation mode is not XYZ, I can't handle that, sorry.! (It's "+obj.rotation_mode+")")
				return
			
			scn = bpy.context.scene
			scn.frame_start = 0
			scn.frame_end = frames
			scn.frame_current = 0
			scn.render.fps = 1000/frameDuration # supposedly read-only?
			
			# add keyframe at frame 0 with current position
			
			obj.keyframe_insert("location")
			obj.keyframe_insert("rotation_euler")
			
			for frame in range(frames):
				# set the current frame
				scn.frame_current = frame + 1
				# I don't know what the last 8 bytes are, they always contain 0xFFFFFFFF00000000 (-1 & 0) - I trash them.
				dx, dy, dz, droty, drotz, drotx = struct.unpack("6f8x", file.read(32))
				
				# translate the object (it's the only selected object so the operators operate on it)
				bpy.ops.transform.translate( value = (dx/self.SCALE, dy/self.SCALE, dz/self.SCALE) )
				
				# rotate the object - unsure how to do the rotations using bpy.ops.transform.rotate
				# (Blender now uses Radians. Deal with it.)
				drot = drotx, droty, drotz
				obj.rotation_euler[0] = obj.rotation_euler[0] + math.radians(drotx)
				obj.rotation_euler[1] = obj.rotation_euler[1] + math.radians(droty)
				obj.rotation_euler[2] = obj.rotation_euler[2] + math.radians(drotz)
				
				# save keyframe
				obj.keyframe_insert("location")
				obj.keyframe_insert("rotation_euler")
			
			#back to frame 0
			scn.frame_current = 0
			#set the interpolation to linear
			for curve in obj.animation_data.action.fcurves:
				for point in curve.keyframe_points:
					point.interpolation = "LINEAR"
		except IOError:
			self.report({"ERROR"}, "Couldn't open file!")
			return

def menu_func(self, context):
    self.layout.operator(Operator.bl_idname, text="JA ROFF (.rof)")