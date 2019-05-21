bl_info = {
    "name": "JSON Model Format (.json)",
    "author": "CHC",
    "version": (0, 0, 1),
    "blender": (2, 63, 0),
    "location": "File > Import > JSON Model (.json)",
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

from mathutils import Vector, Matrix

import json


class THPSMDLImport(bpy.types.Operator):
	"""Export selection to THPS MDL"""

	bl_idname = "export_scene.mdl"
	bl_label = "Import JSON scene"

	filepath = StringProperty(subtype='FILE_PATH')
	
	#public interface
	
	def execute(self, context):
		#self.filepath = bpy.path.ensure_ext(self.filepath, ".mdl")
		self.materialTable = {}
		bpy.context.scene.cursor_location = (0.0, 0.0, 0.0)
		self.ReadScene()
		return {'FINISHED'}

	def invoke(self, context, event):
		#if not self.filepath:
		#	self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".mdl")
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
		
	#private
	def ReadMaterial(self, material_data):
		material = bpy.data.materials.new(material_data["name"])
		print("The Path: {}".format("/Users/chc/code/assettool/jizzy/" + material_data["name"]))
		textures = []
		for t in material_data["textures"]:
			tex = bpy.data.textures.new(t["name"], type ="IMAGE")
			path = "/Users/chc/code/assettool/jizzy/" + t["name"] + ".png"
			img = bpy.data.images.load(path)
			tex.image = img

			mtex = material.texture_slots.add()
			mtex.texture_coords = 'UV';
			mtex.use_map_alpha = True
			mtex.texture = tex
			material.use_transparency = True
			material.transparency_method = 'Z_TRANSPARENCY'

		self.materialTable[material_data["checksum"]] = material
		return material
	def ReadScene(self):
		scnfile = open(self.filepath, "rb")

		
		with open(self.filepath) as data_file:    
		    data = json.load(data_file)
		print("JSON Loaded")
		print("---------------")
		print("File: {}".format(self.filepath))
		print("Num Meshes: {}".format(len(data["meshes"])))
		materials = []
		for m in data["materials"]:
			self.ReadMaterial(m)
		nobj = self.ReadMesh(data["meshes"][0])
		mat = self.FindMaterialByChecksum(data["meshes"][0]["material_checksum"])
		if mat:
			nobj.data.materials.append(mat)
		#self.ReadMaterial(nobj, data["materials"], data["meshes"][0])
#		for x in data["meshes"]:
#			self.ReadMesh(x)
		return 0
	def ConvertToVector(self, data):
		ret = []
		for v in data:
			ret.append(Vector([v[0],v[1],v[2]]))
		return ret
	def FindMaterialByChecksum(self, checksum):
		return self.materialTable[checksum]
	def FindBoneByName(self, bones, name):
		for bone in bones:
			if bone['name'] == name:
				return bone
		return 0
	def ReadMesh(self, mesh):
		print("Name: {}".format(mesh["name"]))
		print("Num Verts: {}".format(len(mesh["vertices"])))
		print("Num Indices: {}".format(len(mesh["indices"][0])))

		scn = bpy.context.scene

		for o in scn.objects:
			o.select = False
		


		blenmesh = bpy.data.meshes.new(mesh["name"])
		blenmesh.vertices.add(len(mesh["vertices"]))
		blenmesh.vertices.foreach_set("co", unpack_list(mesh["vertices"]))
		blenmesh.tessfaces.add(len(mesh["indices"][0]))
		# Add faces
		blenmesh.tessfaces.foreach_set("vertices_raw", unpack_face_list(mesh["indices"][0]))

		uvlay = blenmesh.tessface_uv_textures.new()

		for i, f in enumerate(uvlay.data):
			index = mesh["indices"][0][i]
			for j, uv in enumerate(f.uv):
				uv[0] = mesh["uvs"][index[j]][0]
				uv[1] = mesh["uvs"][index[j]][1]

		#add object to scene
		blenmesh.update()
		blenmesh.validate()
		nobj = bpy.data.objects.new(mesh["name"], blenmesh)
		scn.objects.link(nobj)


		#print("Skel: {}".format(mesh["skeleton"]))

		# Create Armature and Object
		bpy.ops.object.add(type='ARMATURE', enter_editmode=True)
		object = bpy.context.object
		object.name = 'armguy'
		armature = object.data
		armature.name = 'armguy'

		#create bones
		for the_bone in mesh["skeleton"]:
			nobj.vertex_groups.new(name=the_bone["name"])
			bone = armature.edit_bones.new(the_bone["name"])
			bone.tail = Vector([0,0,0.1]) # if you won't do it, the bone will have zero lenghtand will be removed immediately by Blender

		#map parents
		for the_bone in mesh["skeleton"]:
			if 'parent' in the_bone:
				armature.edit_bones[the_bone['name']].parent = armature.edit_bones[the_bone['parent']]
				parent = self.FindBoneByName(mesh["skeleton"], the_bone['parent'])

		for the_bone in mesh["skeleton"]:
			matrix = Matrix(the_bone["matrix"])
			matrix.transpose()
			matrix = matrix.inverted()
			armature.edit_bones[the_bone['name']].transform(matrix)

		for vidx in range(0, len(mesh["vertices"])):
			bones = mesh["bone_indices"][0][vidx]
			weights = mesh["weights"][0][vidx]
			print("Vertex: {}".format(vidx))
			print("Data: {} {}".format(bones, weights))
			for widx in range(0, len(weights)):
				bone_idx = bones[widx]
				if bone_idx == 0:
					break
				weight = weights[widx]
				nobj.vertex_groups[bone_idx].add([vidx], weight, 'ADD')
#		for vwidx, wval in enumerate(mesh["weights"][0]):
#			bones = mesh["bone_indices"][0][vwidx]
#			print("Vertex: {}".format(vwidx))
#			print("Data: {} {}".format(bones, wval))
#			for vwsidx, vwsval in enumerate(wval):
#				bone_idx = bones[vwsidx]
#				the_bone = mesh["skeleton"][bone_idx]
#				print("Bone: {} ({}): {}".format(bone_idx, the_bone["name"], vwsval))
#				nobj.vertex_groups[bone_idx].add([vwidx], vwsval, 'ADD')
		return nobj


def menu_func(self, context):
    self.layout.operator(THPSMDLImport.bl_idname, text="JSON Mesh (.json)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()
