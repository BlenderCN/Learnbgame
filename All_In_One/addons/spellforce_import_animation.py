bl_info = {
	"name": "Import Spellforce Animation files (.bob)",
	"author": "leszekd25",
	"version": (1, 0, 0),
	"blender": (2, 78, 0),
	"location": "File > Import > Animation File (.bob)",
	"description": "Import Spellforce Animation Data",
	"warning": "totally untested",
	"category": "Import-Export",
}

"""
just testing import tool for blender
let's hope it works
also this is just a modification of unreal .psk import add-on
"""

import bpy
import mathutils
import math
import os.path
# XXX Yuck! 'from foo import *' is really bad!
from mathutils import *
from math import *
from bpy.props import *
from string import *
from struct import *
from math import *
from bpy.props import *

from bpy_extras.io_utils import unpack_list, unpack_face_list
from bpy_extras.image_utils import load_image

def bobimport(infile, bDebugLogMSB):
	global DEBUGLOG
	DEBUGLOG = bDebugLogMSB
	print ("--------------------------------------------------")
	print ("---------SCRIPT EXECUTING PYTHON IMPORTER---------")
	print ("--------------------------------------------------")
	print (" DEBUG Log:",bDebugLogMSB)
	#print ("Importing file: ", infile)

	class AnimationBoneData:
		def __init__(self):
			self.positions = []
			self.positions_time = []
			self.rotations = []
			self.rotations_time = []
		def add_rotation(self, t, q):
			self.rotations.append(q)
			self.rotations_time.append(t)
		def add_position(self, t, p):
			self.positions.append(p)
			self.positions_time.append(t)
			
			
	object = bpy.context.object
	if object.type != "ARMATURE":
		print("WRONG OBJECT SELECTED")
		return
	
		
	anim_bones = []
	
	msbfile = open(infile,'rb')
	if (DEBUGLOG):
		logpath = infile.replace(".bob", ".txt")
		print("logpath:",logpath)
		logf = open(logpath,'w')

	def printlog(strdata):
		if (DEBUGLOG):
			logf.write(strdata)

	indata = unpack("H", msbfile.read(2))
	indata = unpack("I", msbfile.read(4))
	print(indata[0])
	bonecount = indata[0]
	
	for i in range(bonecount):
		print(i)
		anim_data = AnimationBoneData()
		indata2 = unpack("IffII", msbfile.read(20))
		anim_rot_count = indata2[4]
		print(anim_rot_count)
		for j in range(anim_rot_count):
			indata3 = unpack("fffff", msbfile.read(20))
			q = mathutils.Quaternion([indata3[0], indata3[1], indata3[2], indata3[3]])
			print(j, q, indata3[4])
			anim_data.add_rotation(indata3[4], q)
		indata2 = unpack("IffII", msbfile.read(20))
		anim_pos_count = indata2[4]
		print(anim_pos_count)
		for j in range(anim_pos_count):
			indata3 = unpack("ffff", msbfile.read(16))
			p = mathutils.Vector([indata3[0], indata3[1], indata3[2]])
			print(p, indata3[3])
			anim_data.add_position(indata3[3], p)
		anim_bones.append(anim_data)
	
	msbfile.close()
	
	b_skel = object.pose
	
	if bonecount != len(b_skel.bones):
		print("BONES DON'T MATCH")
		return
	
	for i in range(bonecount):
		for j in range(len(anim_bones[i].positions)):
			b_skel.bones[i].location = anim_bones[i].positions[j]
			b_skel.bones[i].keyframe_insert(data_path = "location", frame = anim_bones[i].positions_time[j] * 25)
		for j in range(len(anim_bones[i].rotations)):
			b_skel.bones[i].rotation_quaternion = anim_bones[i].rotations[j]
			b_skel.bones[i].keyframe_insert(data_path = "rotation_quaternion", frame = anim_bones[i].rotations_time[j] * 25)
			
	bpy.context.scene.update()
					
	

def getInputFilenameBOB(self, filename, bDebugLogMSB):
	checktype = filename.split('\\')[-1].split('.')[1]
	print ("------------",filename)
	if checktype.lower() != 'bob':
		print ("  Selected file = ", filename)
		raise (IOError, "The selected input file is not a *.bob file")
		#self.report({'INFO'}, ("Selected file:"+ filename))
	else:
		bobimport(filename, bDebugLogMSB)


class import_bob(bpy.types.Operator):
	'''Load a spellforce msb File'''
	bl_idname = "import_animation.bob"
	bl_label = "Import BOB"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_options = {'UNDO'}

	# List of operator properties, the attributes will be assigned
	# to the class instance from the operator settings before calling.
	filepath = StringProperty(
			subtype='FILE_PATH',
			)

	bDebugLogMSB = BoolProperty(
			name="Debug Log.txt",
			description="Log the output of raw format. It will save in "
						"current file dir. Note this just for testing",
			default=False,
			)


	def execute(self, context):
		getInputFilenameBOB(self, self.filepath, self.bDebugLogMSB)
		return {'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager
		wm.fileselect_add(self)
		return {'RUNNING_MODAL'}

def menu_func(self, context):
	self.layout.operator(import_bob.bl_idname, text="Spellforce Animation (.bob)")

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_import.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
	register()