bl_info = {
	"name": "Export Spellforce Animation files (.bob)",
	"author": "leszekd25",
	"version": (1, 0, 0),
	"blender": (2, 78, 0),
	"location": "File > Export > Animation File (.bob)",
	"description": "Export Spellforce Animation Data",
	"warning": "totally untested",
	"category": "Learnbgame",
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

def bobexport(infile, bDebugLogMSB):
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
			self.positions_max_time = 0
			self.rotations = []
			self.rotations_time = []
			self.rotations_max_time = 0
		def add_rotation(self, t, q):
			self.rotations.append(q)
			self.rotations_time.append(t)
			self.rotations_max_time = max(self.rotations_max_time, t)
		def add_position(self, t, p):
			self.positions.append(p)
			self.positions_time.append(t)
			self.positions_max_time = max(self.positions_max_time, t)
			
			
	object = bpy.context.object
	if object.type != "ARMATURE":
		print("WRONG OBJECT SELECTED")
		return
	
	bpy.ops.object.mode_set(mode = 'EDIT')
	
	bone_names = {}
	for i in range(len(object.data.edit_bones)):
		print('pose.bones["'+object.data.edit_bones[i].name+'"].')
		bone_names['pose.bones["'+object.data.edit_bones[i].name+'"].'] = i
	bone_anim = []
	for i in range(len(object.data.edit_bones)):
		bone_anim.append(AnimationBoneData())
	
	#pre-processing
	max_time_pos = []
	max_time_rot = []
	max_time = 0
	
	bone_pos_count = []
	bone_rot_count = []
	for i in range(len(object.data.edit_bones)):
		bone_pos_count.append(0)
		bone_rot_count.append(0)
	for fc in object.animation_data.action.fcurves:
		if fc.data_path.endswith(('location')):
			bone_n = fc.data_path[:-8]
			bone_i = bone_names[bone_n]
			bone_pos_count[bone_i] += len(fc.keyframe_points)
		elif fc.data_path.endswith(('rotation_quaternion')):
			bone_n = fc.data_path[:-19]
			bone_i = bone_names[bone_n]
			bone_rot_count[bone_i] += len(fc.keyframe_points)
			
		
	for fc in object.animation_data.action.fcurves:
		if fc.data_path.endswith(('location')):
			bone_n = fc.data_path[:-8]
			bone_i = bone_names[bone_n]
			array_pos = []
			array_time = []
			entries = bone_pos_count[bone_i]//3
			array_index = -1
			if len(array_pos) == 0:
				for i in range(entries):
					array_pos.append([0, 0, 0])
					array_time.append(0)
			for i in range(len(fc.keyframe_points)):
				key = fc.keyframe_points[i]
				array_pos[i % entries][fc.array_index] = key.co[1]
				array_time[i % entries] = key.co[0] / 25
				array_index = fc.array_index
			if len(bone_anim[bone_i].positions) == 0:
				for i in range(entries):
					bone_anim[bone_i].add_position(array_time[i], array_pos[i])
			else:
				for i in range(entries):
					bone_anim[bone_i].positions[i][array_index] = array_pos[i][array_index]
		elif fc.data_path.endswith(('rotation_quaternion')):
			bone_n = fc.data_path[:-19]
			bone_i = bone_names[bone_n]
			array_rot = []
			array_time = []
			entries = bone_rot_count[bone_i]//4
			array_index = -1
			for i in range(entries):
				array_rot.append([0, 0, 0, 0])
				array_time.append(0)
			for i in range(len(fc.keyframe_points)):
				key = fc.keyframe_points[i]
				array_rot[i % entries][fc.array_index] = key.co[1]
				array_time[i % entries] = key.co[0] / 25
				array_index = fc.array_index
			if len(bone_anim[bone_i].rotations) == 0:
				for i in range(entries):
					bone_anim[bone_i].add_rotation(array_time[i], array_rot[i])
			else:
				for i in range(entries):
					bone_anim[bone_i].rotations[i][array_index] = array_rot[i][array_index]
		
		
	bpy.ops.object.mode_set(mode = 'OBJECT')
	
	bobfile = open(infile+".bob",'wb')
	if (DEBUGLOG):
		logpath = infile.replace(".bob", ".txt")
		print("logpath:",logpath)
		logf = open(logpath,'w')
	
	outdata1 = pack("H", 256)
	bobfile.write(outdata1)
	outdata2 = pack("I", len(bone_anim))
	bobfile.write(outdata2)
	for i in range(len(bone_anim)):
		bone = bone_anim[i]
		outdata3 = pack("IffII", 0, 1.0, bone.rotations_max_time, 3, len(bone.rotations))
		bobfile.write(outdata3)
		for j in range(len(bone.rotations)):
			outdata4 = pack("fffff", bone.rotations[j][0], bone.rotations[j][1], bone.rotations[j][2], bone.rotations[j][3], bone.rotations_time[j])
			bobfile.write(outdata4)
		outdata3 = pack("IffII", 0, 1.0, bone.positions_max_time, 3, len(bone.positions))
		bobfile.write(outdata3)
		for j in range(len(bone.positions)):
			outdata4 = pack("ffff", bone.positions[j][0], bone.positions[j][1], bone.positions[j][2], bone.positions_time[j])
			bobfile.write(outdata4)
	
	bobfile.close()
		
			
	bpy.context.scene.update()
					
	

def getInputFilenameBOB(self, filename, bDebugLogMSB):
	#something here?
	bobexport(filename, bDebugLogMSB)


class export_bob(bpy.types.Operator):
	'''Load a spellforce msb File'''
	bl_idname = "export_animation.bob"
	bl_label = "Export BOB"
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
	self.layout.operator(export_bob.bl_idname, text="Spellforce Animation (.bob)")

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
	register()