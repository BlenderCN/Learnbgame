import gc
import math
import os
import struct

import traceback

import bpy, bpy.props, bpy.ops
import mathutils

from io_scene_valvesource import import_smd as vs_import_smd, utils as vs_utils

from advancedfx import utils as afx_utils

class GAgrImporter:
	onlyBones = False
	smd = None
	qc = None

class SmdImporterEx(vs_import_smd.SmdImporter):
	bl_idname = "advancedfx.smd_importer_ex"
	
	qc = None
	smd = None

	# Properties used by the file browser
	filepath : bpy.props.StringProperty(name="File Path", description="File filepath used for importing the SMD/VTA/DMX/QC file", maxlen=1024, default="", options={'HIDDEN'})
	files : bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN'})
	directory : bpy.props.StringProperty(maxlen=1024, default="", subtype='FILE_PATH', options={'HIDDEN'})
	filter_folder : bpy.props.BoolProperty(name="Filter Folders", description="", default=True, options={'HIDDEN'})
	filter_glob : bpy.props.StringProperty(default="*.smd;*.vta;*.dmx;*.qc;*.qci", options={'HIDDEN'})

	# Custom properties
	doAnim : bpy.props.BoolProperty(name="importer_doanims", default=True)
	makeCamera : bpy.props.BoolProperty(name="importer_makecamera",description="importer_makecamera_tip",default=False)
	append : bpy.props.EnumProperty(name="importer_bones_mode",description="importer_bones_mode_desc",items=(
		('VALIDATE',"importer_bones_validate","importer_bones_validate_desc"),
		('APPEND',"importer_bones_append","importer_bones_append_desc"),
		('NEW_ARMATURE',"importer_bones_newarm","importer_bones_newarm_desc")),
		default='APPEND')
	upAxis : bpy.props.EnumProperty(name="Up Axis",items=vs_utils.axes,default='Z',description="importer_up_tip")
	rotMode : bpy.props.EnumProperty(name="importer_rotmode",items=( ('XYZ', "Euler", ''), ('QUATERNION', "Quaternion", "") ),default='XYZ',description="importer_rotmode_tip")
	boneMode : bpy.props.EnumProperty(name="importer_bonemode",items=(('NONE','Default',''),('ARROWS','Arrows',''),('SPHERE','Sphere','')),default='SPHERE',description="importer_bonemode_tip")
	
	def execute(self, context):
		self.existingBones = []
		self.num_files_imported = 0
		self.readQC(self.filepath, False, False, False, 'XYZ', outer_qc = True)
		GAgrImporter.qc = self.qc
		GAgrImporter.smd = self.smd
		return {'FINISHED'}
		
	def readPolys(self):
		if GAgrImporter.onlyBones:
			return
		super(SmdImporterEx, self).readPolys()
	
	def readShapes(self):
		if GAgrImporter.onlyBones:
			return
		super(SmdImporterEx, self).readShapes()


def ReadString(file):
	buf = bytearray()
	while True:
		b = file.read(1)
		if len(b) < 1:
			return None
		elif b == b"\0":
			return buf.decode("utf-8")
		else:
			buf.append(b[0])

def ReadBool(file):
	buf = file.read(1)
	if(len(buf) < 1):
		return None
	return struct.unpack('<?', buf)[0]

def ReadInt(file):
	buf = file.read(4)
	if(len(buf) < 4):
		return None
	return struct.unpack('<i', buf)[0]
	
def ReadFloat(file):
	buf = file.read(4)
	if(len(buf) < 4):
		return None
	return struct.unpack('<f', buf)[0]

def ReadDouble(file):
	buf = file.read(8)
	if(len(buf) < 8):
		return None
	return struct.unpack('<d', buf)[0]
	
def ReadVector(file, quakeFormat = False):
	x = ReadFloat(file)
	if x is None:
		return None
	y = ReadFloat(file)
	if y is None:
		return None
	z = ReadFloat(file)
	if z is None:
		return None
		
	if math.isinf(x) or math.isinf(y) or math.isinf(z):
		x = 0
		y = 0
		z = 0
	
	return mathutils.Vector((-y,x,z)) if quakeFormat else mathutils.Vector((x,y,z))

def ReadQAngle(file):
	x = ReadFloat(file)
	if x is None:
		return None
	y = ReadFloat(file)
	if y is None:
		return None
	z = ReadFloat(file)
	if z is None:
		return None
	
	if math.isinf(x) or math.isinf(y) or math.isinf(z):
		x = 0
		y = 0
		z = 0
	
	return afx_utils.QAngle(x,y,z)

def ReadQuaternion(file, quakeFormat = False):
	x = ReadFloat(file)
	if x is None:
		return None
	y = ReadFloat(file)
	if y is None:
		return None
	z = ReadFloat(file)
	if z is None:
		return None
	w = ReadFloat(file)
	if w is None:
		return None
	
	if math.isinf(x) or math.isinf(y) or math.isinf(z) or math.isinf(w):
		w = 1
		x = 0
		y = 0
		z = 0
	
	return mathutils.Quaternion((w,-y,x,z)) if quakeFormat else mathutils.Quaternion((w,x,y,z))

def ReadAgrVersion(file):
	buf = file.read(14)
	if len(buf) < 14:
		return None
	
	cmp = b"afxGameRecord\0"
	
	if buf != cmp:
		return None
	
	return ReadInt(file)

class AgrDictionary:
	def __init__(self):
		self.dict = {}
		self.peeked = None
	
	def Read(self,file):
		if self.peeked is not None:
			oldPeeked = self.peeked
			self.peeked = None
			return oldPeeked
		
		idx = ReadInt(file)
		
		if idx is None:
			return None
		
		if -1 == idx:
			str = ReadString(file)
			if str is None:
				return None
			self.dict[len(self.dict)] = str
			return str
			
		return self.dict[idx]
		
	def Peekaboo(self,file,what):
		if self.peeked is None:
			self.peeked = self.Read(file)
			
		if(what == self.peeked):
			self.peeked = None
			return True
		
		return False
		
class ModelData:
	def __init__(self,qc,smd):
		self.qc = qc
		self.smd = smd
		self.curves = []

class ModelHandle:
	def __init__(self,objNr,modelName):
		self.objNr = objNr
		self.modelName = modelName
		self.modelData = False
		self.lastRenderOrigin = None
		self.lastRenderRotQuat = None
	
#	
#	def __hash__(self):
#		return hash((self.handle, self.modelName))
#	
#	def __eq__(self, other):
#		return (self.handle, self.modelName) == (other.handle, other.modelName)

class CameraData:
	def __init__(self,o,c):
		self.o = o
		self.c = c
		self.curves = []

class AgrTimeConverter:
	def __init__(self,context):
		self.fps = context.scene.render.fps
		self.time = 0
		self.frameTime = 0
		self.newTime = 0
		self.errorCount = 0
		self.maxError = None
		
	def Frame(self,frameTime):
		self.time = self.newTime
		self.frameTime = frameTime
		
		if 0 != frameTime:
			fps = 1.0/frameTime
			error = self.fps -fps
			if (0>= error) or (0.001 < error):
				self.errorCount = self.errorCount + 1
				if (self.maxError is None) or (abs(self.maxError) < abs(error)):
					self.maxError = error
					
	def FrameEnd(self):
		self.newTime = self.time + self.frameTime
		
	def GetTime(self):
		return 1.0 + self.time * self.fps

class AgrImporter(bpy.types.Operator, vs_utils.Logger):
	bl_idname = "advancedfx.agrimporter"
	bl_label = "HLAE afxGameRecord (.agr)"
	bl_options = {'UNDO'}
	
	# Properties used by the file browser
	filepath: bpy.props.StringProperty(subtype="FILE_PATH")
	filename_ext: ".agr"
	filter_glob: bpy.props.StringProperty(default="*.agr", options={'HIDDEN'})

	# Custom properties
	
	assetPath: bpy.props.StringProperty(
		name="Asset Path",
		description="Directory path containing the (decompiled) assets in a folder structure as in the pak01_dir.pak.",
		default="",
		#subtype = 'DIR_PATH'
	)

	interKey: bpy.props.BoolProperty(
		name="Add interpolated key frames",
		description="Create interpolated key frames for frames in-between the original key frames.",
		default=False)

	global_scale: bpy.props.FloatProperty(
		name="Scale",
		description="Scale everything by this value",
		min=0.000001, max=1000000.0,
		soft_min=0.001, soft_max=1.0,
		default=0.0254,
	)
	
	scaleInvisibleZero: bpy.props.BoolProperty(
		name="Scale invisible to zero",
		description="If set entities will scaled to zero when not visible.",
		default=False,
	)
	
	onlyBones: bpy.props.BoolProperty(
		name="Bones (skeleton) only",
		description="Import only bones (skeletons) (faster).",
		default=False)
		
	# class properties
	valveMatrixToBlender = mathutils.Matrix.Rotation(math.pi/2,4,'Z')
	blenderCamUpQuat = mathutils.Quaternion((math.cos(0.5 * math.radians(90.0)), math.sin(0.5* math.radians(90.0)), 0.0, 0.0))
	
	def execute(self, context):
		try:
			bpy.utils.register_class(SmdImporterEx)
			ok = self.readAgr(context)
		finally:
			bpy.utils.unregister_class(SmdImporterEx)
		
		for area in context.screen.areas:
			if area.type == 'VIEW_3D':
				space = area.spaces.active
				#space.grid_lines = 64
				#space.grid_scale = self.global_scale * 512
				#space.grid_subdivisions = 8
				space.clip_end = self.global_scale * 56756
		
		self.errorReport("Error report")
		
		return {'FINISHED'}
		
	
	def invoke(self, context, event):
		bpy.context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
	
	def importModel(self, context, modelHandle):
		filePath = self.assetPath.rstrip("/\\") + "/" +modelHandle.modelName
		filePath = os.path.splitext(filePath)[0]
		filePath = filePath + "/" + os.path.basename(filePath) + ".qc"
		filePath = filePath.replace("/", "\\")
		
		GAgrImporter.qc = None
		GAgrImporter.smd = None
		GAgrImporter.onlyBones = self.onlyBones
		modelData = None
		
		try:
			bpy.ops.advancedfx.smd_importer_ex(filepath=filePath, doAnim=False)
			modelData = ModelData(GAgrImporter.qc,GAgrImporter.smd)
		except:
			self.error("Failed to import \""+filePath+"\".")
			return None
		finally:
			GAgrImporter.qc = None
			GAgrImporter.smd = None
			
		# Update name:
		name = modelHandle.modelName.rsplit('/',1)
		name = name[len(name) -1]
		name = (name[:30] + '..') if len(name) > 30 else name
		name = "afx." +str(modelHandle.objNr)+ " " + name
		modelData.qc.a.name = name
		
		a = modelData.smd.a
		
		# Fix rotation:
		if a.rotation_mode != 'QUATERNION':
			a.rotation_mode = 'QUATERNION'
		for bone in a.pose.bones:
			if bone.rotation_mode != 'QUATERNION':
				bone.rotation_mode = 'QUATERNION'
				
		# Scale:
		
		a.scale[0] = self.global_scale
		a.scale[1] = self.global_scale
		a.scale[2] = self.global_scale
		
		# Create actions and their curves (boobs):
		#vs_utils.select_only(a)
		
		a.animation_data_create()
		action = bpy.data.actions.new(name="game_data")
		a.animation_data.action = action

		modelData.curves.append(action.fcurves.new("hide_render"))
		
		# We are lazy, so we use frame 0 to set as not visible (initially) / hide_render 1:
		afx_utils.AddKey_Visible(self.interKey, modelData.curves[0].keyframe_points, 0.0, False)
		
		for i in range(3):
			modelData.curves.append(action.fcurves.new("location",index = i))
		
		for i in range(4):
			modelData.curves.append(action.fcurves.new("rotation_quaternion",index = i))
		
		num_bones = len(a.pose.bones)
		
		for i in range(num_bones):
			bone = a.pose.bones[modelData.smd.boneIDs[i]]
			
			bone_string = "pose.bones[\"{}\"].".format(bone.name)
			
			for j in range(3):
				modelData.curves.append(action.fcurves.new(bone_string + "location",index = j))
			
			for j in range(4):
				modelData.curves.append(action.fcurves.new(bone_string + "rotation_quaternion",index = j))
				
		# Create visiblity driver:
		
		for child in a.children:
			d = child.driver_add('hide_render').driver
			d.type = 'AVERAGE'
			v = d.variables.new()
			v.name = 'hide_render'
			v.targets[0].id = a
			v.targets[0].data_path = 'hide_render'
			
		if self.scaleInvisibleZero:
			
			ds = a.driver_add('scale')
			
			for df in ds:
				d = df.driver
				d.type = 'AVERAGE'
				v = d.variables.new()
				v.name = 'hide_render'
				v.targets[0].id = a
				v.targets[0].data_path = 'hide_render'
				m = df.modifiers.new('GENERATOR')
				m.coefficients[0] = self.global_scale
				m.coefficients[1] = -self.global_scale
				m.poly_order = 1
				m.mode = 'POLYNOMIAL'
				m.use_additive = False
				
		
		return modelData
		
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
	
	def readAgr(self,context):
		file = None
		
		try:
			file = open(self.filepath, 'rb')
			
			if file is None:
				self.error('Could not open file.')
				return False
			
			file.seek(0, 2)
			fileSize = file.tell()
			file.seek(0, 0)
			
			context.window_manager.progress_begin(0.0, 1.0)
			
			version = ReadAgrVersion(file)
			
			if version is None:
				self.error('Invalid file format.')
				return False
				
			if 4 != version:
				self.error('Version '+str(version)+' is not supported!')
				return False
				
			timeConverter = AgrTimeConverter(context)
			dict = AgrDictionary()
			handleToLastModelHandle = {}
			unusedModelHandles = []
			lastCameraQuat = None
			camData = None
			
			stupidCount = 0
			
			objNr = 0
			
			while True:
			
				if 0 < fileSize and 0 == stupidCount % 100:
					val = float(file.tell())/float(fileSize)
					context.window_manager.progress_update(val)
					print("AGR Import %f%%" % (100*val))
				
				stupidCount = stupidCount +1
				
				if 4096 <= stupidCount:
					stupidCount = 0
					gc.collect()
					#break
				
				node0 = dict.Read(file)
				
				if node0 is None:
					break
					
				elif 'afxFrame' == node0:
					frameTime = ReadFloat(file)
					
					timeConverter.Frame(frameTime)
					
					afxHiddenOffset = ReadInt(file)
					if afxHiddenOffset:
						curOffset = file.tell()
						file.seek(afxHiddenOffset -4, 1)
						
						numHidden = ReadInt(file)
						for i in range(numHidden):
							handle = ReadInt(file)
							
							modelHandle = handleToLastModelHandle.pop(handle, None)
							if modelHandle is not None:
								# Make ent invisible:
								modelData =  modelHandle.modelData
								if modelData: # this can happen if the model could not be loaded
									curves = modelData.curves
									#vs_utils.select_only(modelData.smd.a)
									afx_utils.AddKey_Visible(self.interKey, curves[0].keyframe_points, timeConverter.GetTime(), False)
								
								unusedModelHandles.append(modelHandle)
								print("Marking %i (%s) as hidden/reusable." % (modelHandle.objNr,modelHandle.modelName))
							
						file.seek(curOffset,0)
						
				elif 'afxFrameEnd' == node0:
					timeConverter.FrameEnd()
					
				elif 'afxHidden' == node0:
					# skipped, because will be handled earlier by afxHiddenOffset
					
					numHidden = ReadInt(file)
					for i in range(numHidden):
						handle = ReadInt(file)
				
				elif 'deleted' == node0:
					handle = ReadInt(file)
					
					modelHandle = handleToLastModelHandle.pop(handle, None)
					if modelHandle is not None:
						# Make removed ent invisible:
						modelData = modelHandle.modelData
						if modelData: # this can happen if the model could not be loaded
							curves = modelData.curves
							#vs_utils.select_only( modelData.smd.a )
							afx_utils.AddKey_Visible(self.interKey, curves[0].keyframe_points, timeConverter.GetTime(), False)
						
						unusedModelHandles.append(modelHandle)
						print("Marking %i (%s) as deleted/reusable." % (modelHandle.objNr,modelHandle.modelName))
				
				elif 'entity_state' == node0:
					visible = None
					modelData = None
					handle = ReadInt(file)
					if dict.Peekaboo(file,'baseentity'):
						
						modelName = dict.Read(file)
						
						visible = ReadBool(file)
						
						renderOrigin = ReadVector(file, quakeFormat=True)
						renderAngles = ReadQAngle(file)
						
						renderOrigin = renderOrigin * self.global_scale
						renderRotQuat = renderAngles.to_quaternion()
						
						modelHandle = handleToLastModelHandle.get(handle, None)
						
						if (modelHandle is not None) and (modelHandle.modelName != modelName):
							# Switched model, make old model invisible:
							modelData = modelHandle.modelData
							if modelData: # this can happen if the model could not be loaded
								curves = modelData.curves
								#vs_utils.select_only( modelData.smd.a )
								afx_utils.AddKey_Visible(self.interKey, curves[0].keyframe_points, timeConverter.GetTime(), False)
							
							modelHandle = None
						
						if modelHandle is None:
							
							# Check if we can reuse s.th. and if not create new one:
							
							bestIndex = 0
							bestLength = 0
							
							for idx,val in enumerate(unusedModelHandles):
								if (val.modelName == modelName) and ((modelHandle is None) or ((modelHandle.lastRenderOrigin -renderOrigin).length < bestLength)):
									modelHandle = val
									bestLength = (modelHandle.lastRenderOrigin -renderOrigin).length
									bestIndex = idx
							
							if modelHandle is not None:
								# Use the one we found:
								del unusedModelHandles[bestIndex]
								print("Reusing %i (%s)." % (modelHandle.objNr,modelHandle.modelName))
							else:
								# If not then create a new one:
								objNr = objNr + 1
								modelHandle = ModelHandle(objNr, modelName)
								print("Creating %i (%s)." % (modelHandle.objNr,modelHandle.modelName))
							
							handleToLastModelHandle[handle] = modelHandle
							
						modelHandle.lastRenderOrigin = renderOrigin
						
						# make sure we take the shortest path:
						if modelHandle.lastRenderRotQuat is not None:
							dot = modelHandle.lastRenderRotQuat.dot(renderRotQuat)
							if dot < 0:
								renderRotQuat.negate()
						modelHandle.lastRenderRotQuat = renderRotQuat
						
						modelData = modelHandle.modelData
						if modelData is False:
							# We have not tried to import the model for this (new) handle yet, so try to import it:
							modelData = self.importModel(context, modelHandle)
							modelHandle.modelData = modelData
						
						if modelData is not None:
							
							curves = modelData.curves
							
							#vs_utils.select_only( modelData.smd.a )
							
							afx_utils.AddKey_Visible(self.interKey, curves[0].keyframe_points, timeConverter.GetTime(), visible)
							
							afx_utils.AddKey_Location(self.interKey, curves[1+0].keyframe_points, curves[1+1].keyframe_points, curves[1+2].keyframe_points, timeConverter.GetTime(), renderOrigin)
							
							afx_utils.AddKey_Rotation(self.interKey, curves[1+3].keyframe_points, curves[1+4].keyframe_points, curves[1+5].keyframe_points, curves[1+6].keyframe_points, timeConverter.GetTime(), renderRotQuat)
					
					if dict.Peekaboo(file,'baseanimating'):
						#skin = ReadInt(file)
						#body = ReadInt(file)
						#sequence  = ReadInt(file)
						hasBoneList = ReadBool(file)
						if hasBoneList:
							numBones = ReadInt(file)
							
							for i in range(numBones):
								#pos = file.tell()
								vec = ReadVector(file, quakeFormat=False)
								quat = ReadQuaternion(file, quakeFormat=False)
								
								if (modelData is None):
									continue
								
								#if not(True == visible):
								#	# Only key-frame if visible
								#	continue
								
								if(i < len(modelData.smd.boneIDs)):
									bone = modelData.smd.a.pose.bones[modelData.smd.boneIDs[i]]
									
									#self.warning(str(pos)+": "+str(i)+"("+bone.name+"): "+str(vec)+" "+str(quat))
									
									matrix = mathutils.Matrix.Translation(vec) @ quat.to_matrix().to_4x4()
									
									if bone.parent:
										matrix = bone.parent.matrix @ matrix
									else:
										matrix = self.valveMatrixToBlender @ matrix
									
									bone.matrix = matrix
									
									curves = modelData.curves
									
									#vs_utils.select_only( modelData.smd.a )
									
									afx_utils.AddKey_Location(self.interKey, curves[8+i*7+0].keyframe_points, curves[8+i*7+1].keyframe_points, curves[8+i*7+2].keyframe_points, timeConverter.GetTime(), bone.location)
									
									afx_utils.AddKey_Rotation(self.interKey, curves[8+i*7+3].keyframe_points, curves[8+i*7+4].keyframe_points, curves[8+i*7+5].keyframe_points, curves[8+i*7+6].keyframe_points, timeConverter.GetTime(), bone.rotation_quaternion)
					
					dict.Peekaboo(file,'/')
					
					viewModel = ReadBool(file)
					
					#if modelData is not None:
					#	for fc in modelData.curves:
					#		fc.update()
					
				elif 'afxCam' == node0:
					
					if camData is None:
						camData = self.createCamera(context,"afxCam")
					
						if camData is None:
							self.error("Failed to create camera.")
							return False
					
					
					renderOrigin = ReadVector(file, quakeFormat=True)
					renderAngles = ReadQAngle(file)
					
					fov = ReadFloat(file)
					
					lens = camData.c.sensor_width / (2.0 * math.tan(math.radians(fov) / 2.0))
					
					renderOrigin = renderOrigin * self.global_scale
					renderRotQuat = renderAngles.to_quaternion() @ self.blenderCamUpQuat
					
					# make sure we take the shortest path:
					if lastCameraQuat is not None:
						dot = lastCameraQuat.dot(renderRotQuat)
						if dot < 0:
							renderRotQuat.negate()
					lastCameraQuat = renderRotQuat
					
					curves = camData.curves
					
					#vs_utils.select_only( camData.o )
					
					afx_utils.AddKey_Location(self.interKey, curves[0].keyframe_points, curves[1].keyframe_points, curves[2].keyframe_points, timeConverter.GetTime(), renderOrigin)
					
					afx_utils.AddKey_Rotation(self.interKey, curves[3].keyframe_points, curves[4].keyframe_points, curves[5].keyframe_points, curves[6].keyframe_points, timeConverter.GetTime(), renderRotQuat)

					afx_utils.AddKey_Value(self.interKey, curves[7].keyframe_points, timeConverter.GetTime(), lens)
				
				else:
					self.warning('Unknown packet at '+str(file.tell()))
					return False
					
			
			if 0 < timeConverter.errorCount:
				self.warning("FPS mismatch was detected %i times. The maximum error was %f. Solution: Make sure to set the Blender project FPS correctly before importing." % (timeConverter.errorCount, timeConverter.maxError))
			
			context.window_manager.progress_end()
			
		finally:
			if file is not None:
				file.close()
		
		return True
