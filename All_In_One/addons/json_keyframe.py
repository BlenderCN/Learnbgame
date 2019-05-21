bl_info = {
    "name": "JSON keyframe Format (.json)",
    "author": "CHC",
    "version": (0, 0, 1),
    "blender": (2, 63, 0),
    "location": "File > Import > JSON keyframe (.json)",
    "description": "Import JSON",
    "warning": "Alpha software",
    "category": "Import",
}

import os
import codecs


import pprint
from pprint import pprint

from bpy_extras.io_utils import unpack_list, unpack_face_list

import math
from math import sin, cos, radians

import bpy
from bpy.props import BoolProperty
from bpy.props import EnumProperty
from bpy.props import StringProperty

import struct
from struct import *

from mathutils import Vector, Matrix, Quaternion

import json


class THPSMDLImport(bpy.types.Operator):
	"""Export selection to THPS MDL"""

	bl_idname = "export_keyframe.json"
	bl_label = "Import JSON Keyframe"

	filepath = StringProperty(subtype='FILE_PATH')
	
	#public interface
	
	def execute(self, context):
		#self.filepath = bpy.path.ensure_ext(self.filepath, ".mdl")
		self.materialTable = {}
		bpy.context.scene.cursor_location = (0.0, 0.0, 0.0)
		self.ReadFrames()
		return {'FINISHED'}

	def invoke(self, context, event):
		#if not self.filepath:
		#	self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".mdl")
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
	def ReadFrames(self):
		scnfile = open(self.filepath, "rb")

		
		with open(self.filepath) as data_file:    
		    data = json.load(data_file)		
		selected_obj = bpy.context.scene.objects.active
		bone_poses = selected_obj.pose.bones
		key_col = data[5]
		for bone in key_col["objects"]:
			for frame in bone["keyframes"]:
				if bone["name"] in bone_poses:
					pose = bone_poses[bone["name"]]
					pose.rotation_quaternion = Quaternion((frame["rotation"][3], frame["rotation"][0], frame["rotation"][1], frame["rotation"][2]))
					pose.keyframe_insert(data_path = "rotation_quaternion", frame = frame["time"])
					pose.location = (frame["position"][0], frame["position"][1], frame["position"][2])
					pose.keyframe_insert(data_path = "location", frame = frame["time"])
					print("Inserting keyframe frame: {}".format(frame["time"]))
				#if bone["name"] in bpy.data.armatures[0].bones:
					#blender_bone = selected_obj.bones[bone["name"]]
					#print("Armature: {}".format(blender_bone))
					#blender_bone.location = (frame["position"][0], frame["position"][1], frame["position"][2])
					#blender_bone.keyframe_insert(data_path = "location", frame = frame["time"], index= -1)
def menu_func(self, context):
    self.layout.operator(THPSMDLImport.bl_idname, text="JSON Keyframe (.json)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()
