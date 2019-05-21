bl_info = {
	"name": "Import Spellforce Mesh Files with Skeleton (.msb, .bor)",
	"author": "leszekd25",
	"version": (1, 0, 0),
	"blender": (2, 78, 0),
	"location": "File > Import > Mesh File (.msb + .bor)",
	"description": "Import Spellforce Mesh+Skeleton Data",
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

def msbimport(infile, bDebugLogMSB, bImportSkeleton):
	global DEBUGLOG
	DEBUGLOG = bDebugLogMSB
	print ("--------------------------------------------------")
	print ("---------SCRIPT EXECUTING PYTHON IMPORTER---------")
	print ("--------------------------------------------------")
	print (" DEBUG Log:",bDebugLogMSB)
	#print ("Importing file: ", infile)

	bone_array = []
	
	class SFVertex:
		def __init__(self):
			self.pos=[0, 0, 0]
			self.normal = [0, 0, 0]
			self.col = [0, 0, 0, 0]
			self.uv = [0, 0]
			self.ind = 0
		def __init__(self, data):
			self.pos = [data[0], data[1], data[2]]
			self.normal = [data[3], data[4], data[5]]
			self.col = [data[6], data[7], data[8], data[9]]
			self.uv = [data[10], 1.0-data[11]]
			self.ind = data[12]
	
	class SFTriangle:
		def __init__(self):
			self.indices = [0, 0, 0, 0]
			self.material = 0
			self.group = 0
		def __init__(self, data, offset, mat):
			self.indices = [data[0]+offset, data[1]+offset, data[2]+offset, 0]
			self.material = mat
			self.group = 0
	
	class SFMeshBuffer:
		def __init__(self):
			self.vertices = []
			self.triangles = []
			self.material = None
			
	class SFMesh:
		def __init__(self):
			self.meshbuffers = []
		
	class SFMap:
		def __init__(self):
			self.texID = -1       #32 bit
			self.unknown1 = 0     #8 bit
			self.texUVMode = 0    #8 bit
			self.unused = 0       #16 bit
			self.texRenderMode = 0#8 bit
			self.texAlpha = 1     #8 bit
			self.flag = 7         #8 bit
			self.depthbias = 0    #8 bit
			self.tiling = 1.0   #float
			self.texName = ""     #64 char string
		def set(self, table):
			print(table)
			self.texID = table[0]     #always -1?
			self.unknown1 = table[1]  #idk
			self.texUVMode = table[2] #probably always 0
			self.unused = table[3]    #anything goes here
			self.texRenderMode = table[4]   #depends, usually 0
			self.texAlpha = table[5]/255
			self.flag = table[6]      #should be 7 except noted otherwise
			self.depthbias = table[7] #always 0?
			self.tiling = table[8]    #always 1.0?
			ntable = []
			for c in table[9]:
				if c == 0:
					break
				ntable.append(c)
			self.texName = str(bytearray(ntable), "utf-8")
			
	
	class SFMaterial:
		def __init__(self):
			self.texMain = SFMap()
			self.texSecondary = SFMap()
			self.diffCol = []
			self.emitCol = []
			self.specCol = []
	
	class SFStateVector:
		def __init__(self):
			self.translation = mathutils.Vector((0, 0, 0))
			self.orientation = mathutils.Quaternion((1.0, 0.0, 0.0, 0.0))
		def to_CS(self):
			new_CS = SFCoordinateSystem()
			new_CS.translation = self.translation
			new_CS.orientation = self.orientation.to_matrix()
			return new_CS
	
	class SFCoordinateSystem:
		def __init__(self):
			self.translation = mathutils.Vector((0, 0, 0))
			self.orientation = mathutils.Matrix.Identity(3)
		def to_SV(self):
			new_SV = SFStateVector()
			new_SV.translation = self.translation
			new_SV.orientation = self.orientation.normalized().to_quaternion()
			return new_SV
		def multiply_with_vector(self, vec):
			new_vec = [0, 0, 0]
			new_vec[0] = self.orientation[0][0]*vec[0]+self.orientation[1][0]*vec[1]+self.orientation[2][0]*vec[2]
			new_vec[1] = self.orientation[0][1]*vec[0]+self.orientation[1][1]*vec[1]+self.orientation[2][1]*vec[2]
			new_vec[2] = self.orientation[0][2]*vec[0]+self.orientation[1][2]*vec[1]+self.orientation[2][2]*vec[2]
			return mathutils.Vector(new_vec)
		def inverted(self):
			new_cs = SFCoordinateSystem()
			new_cs.orientation = self.orientation.inverted()
			new_cs.translation = new_cs.multiply_with_vector(mathutils.Vector((-self.translation[0], -self.translation[1], -self.translation[2])))
			return new_cs
	
	def SF_MultiplyCoordinateSystems(cs1, cs2):
		new_cs = SFCoordinateSystem()
		translation = [0,  0,  0]
		translation[0] = cs1.orientation[0][0]*cs2.translation[0]+cs1.orientation[1][0]*cs2.translation[1]+cs1.orientation[2][0]*cs2.translation[2]+cs1.translation[0]
		translation[1] = cs1.orientation[0][1]*cs2.translation[0]+cs1.orientation[1][1]*cs2.translation[1]+cs1.orientation[2][1]*cs2.translation[2]+cs1.translation[1]
		translation[2] = cs1.orientation[0][2]*cs2.translation[0]+cs1.orientation[1][2]*cs2.translation[1]+cs1.orientation[2][2]*cs2.translation[2]+cs1.translation[2]
		orientation = mathutils.Matrix.Identity(3)
		orientation[0][0] = cs1.orientation[0][0]*cs2.orientation[0][0]+cs1.orientation[1][0]*cs2.orientation[0][1]+cs1.orientation[2][0]*cs2.orientation[0][2]
		orientation[0][1] = cs1.orientation[0][1]*cs2.orientation[0][0]+cs1.orientation[1][1]*cs2.orientation[0][1]+cs1.orientation[2][1]*cs2.orientation[0][2]
		orientation[0][2] = cs1.orientation[0][2]*cs2.orientation[0][0]+cs1.orientation[1][2]*cs2.orientation[0][1]+cs1.orientation[2][2]*cs2.orientation[0][2]
		orientation[1][0] = cs1.orientation[0][0]*cs2.orientation[1][0]+cs1.orientation[1][0]*cs2.orientation[1][1]+cs1.orientation[2][0]*cs2.orientation[1][2]
		orientation[1][1] = cs1.orientation[0][1]*cs2.orientation[1][0]+cs1.orientation[1][1]*cs2.orientation[1][1]+cs1.orientation[2][1]*cs2.orientation[1][2]
		orientation[1][2] = cs1.orientation[0][2]*cs2.orientation[1][0]+cs1.orientation[1][2]*cs2.orientation[1][1]+cs1.orientation[2][2]*cs2.orientation[1][2]
		orientation[2][0] = cs1.orientation[0][0]*cs2.orientation[2][0]+cs1.orientation[1][0]*cs2.orientation[2][1]+cs1.orientation[2][0]*cs2.orientation[2][2]
		orientation[2][1] = cs1.orientation[0][1]*cs2.orientation[2][0]+cs1.orientation[1][1]*cs2.orientation[2][1]+cs1.orientation[2][1]*cs2.orientation[2][2]
		orientation[2][2] = cs1.orientation[0][2]*cs2.orientation[2][0]+cs1.orientation[1][2]*cs2.orientation[2][1]+cs1.orientation[2][2]*cs2.orientation[2][2]
		new_cs.translation = mathutils.Vector(translation)
		new_cs.orientation = orientation
		return new_cs
	
	def Matrix4FromCS(cs):
		mat = mathutils.Matrix.Translation(cs.translation)
		mat2 = mathutils.Matrix.Identity(3)
		mat2.rotate(cs.orientation.to_quaternion())
		mat2 = mat2.to_4x4()
		return mat*mat2
	
	class SkinVertex:
		def __init__(self):
			self.id = -1
			self.pos = None
			self.weight = 0
	
	class SF_Bone:
		def __init__(self):
			self.id = -1
			self.parent = -1
			self.name = ""
			self.ba_channels = [None]
			self.active_channels = 1
			self.sv = SFStateVector()
			self.blender_set = False
			self.cs_invref = SFCoordinateSystem()
			self.cs_global = SFCoordinateSystem()
			self.cs_skinning = SFCoordinateSystem()
			self.blender_vertices = []
			self.blender_length = 0
		def update_sv(self, t):
			if self.active_channels == 1:
				self.ba_channels[0].update_sv(t)
				self.sv = self.ba_channels[0].sv
			#todo: what if more channels?
		def mix_channels(self): #todo: do this
			return
		def set_animation(self, anim, w, too, toa, tob, av):
			self.ba_channel[0]=anim  #todo: proper channel check
			anim.set_start_time(too)
			anim.sv.translation = anim.interpolate_translation(toa)
			anim.sv.orientation = anim.interpolate_orientation(toa)
			anim.weight = w
			anim.time_of_origin = too
			anim.time_of_activation = toa
			anim.time_of_blnding = tob
			anim.time_of_state = toa
			self.update_sv(toa)
	
	class SF_Skeleton:
		def __init__(self):
			self.bones = []
		def update_statevectors(self, t):
			for b in self.bones:
				b.update_sv(t)
			for b in self.bones:
				b.cs_global = b.sv.to_CS()
				if b.parent != -1:
					b.cs_global = SF_MultiplyCoordinateSystems(self.bones[b.parent].cs_global, b.cs_global)
				b.cs_skinning = SF_MultiplyCoordinateSystems(b.cs_global, b.cs_invref)
		def initialize_bones(self):
			for b in self.bones:
				b.cs_global = self.calculate_bone_cs(b.id)
				b.cs_invref = b.cs_global.inverted()
				b.cs_skinning = SFCoordinateSystem()
		def calculate_bone_cs(self, index):
			b = self.bones[index]
			cs = b.sv.to_CS()
			while b.parent != -1:
				b = self.bones[b.parent]
				cs = SF_MultiplyCoordinateSystems(b.sv.to_CS(), cs)
			return cs
		def build_mesh(self):
			for i in range(3):
				skelmesh = bpy.data.meshes.new("Skeleton mesh "+str(i))
				skelmesh.vertices.add(len(self.bones)*3)
				skelmesh.tessfaces.add(len(self.bones)*2)
				cur_v = 0
				cur_f = 0
				for bone in self.bones:
					parent = self.bones[bone.parent]
					cs = bone.cs_global
					#if bone.parent != -1:
					vAxis = cs.orientation[i].normalized()
					skelmesh.vertices[cur_v+0].co = cs.translation+vAxis*0.1
					skelmesh.vertices[cur_v+1].co = cs.translation-vAxis*0.1
					#else:
					#	skelmesh.vertices[cur_v+0].co = mathutils.Vector((0.1, 0, 0))
					#	skelmesh.vertices[cur_v+1].co = mathutils.Vector((0.1, 0, 0))
					skelmesh.vertices[cur_v+2].co = cs.translation
					skelmesh.tessfaces[cur_f+0].vertices_raw = [cur_v+0, cur_v+1, cur_v+2, 0]
					skelmesh.tessfaces[cur_f+1].vertices_raw = [cur_v+0, cur_v+2, cur_v+1, 0]
					cur_v+=3
					cur_f+=2
				final_mesh = bpy.data.objects.new(name = "Skel mesh "+str(i), object_data = skelmesh)
				skelmesh.update()
				bpy.context.scene.objects.link(final_mesh)
				bpy.context.scene.update()
	
	msbfile = open(infile,'rb')
	if (DEBUGLOG):
		logpath = infile.replace(".msb", ".txt")
		print("logpath:",logpath)
		logf = open(logpath,'w')

	def printlog(strdata):
		if (DEBUGLOG):
			logf.write(strdata)
			
	model = SFMesh()
	
	indata = unpack("4H", msbfile.read(8))
	modelnum=indata[1]
	
	total_v = 0
	total_t = 0
	
	for t in range(modelnum):
		model.meshbuffers.append(SFMeshBuffer())
		indata2 = unpack("2I", msbfile.read(8))
		print(t, indata2[0], indata2[1])
		for i in range(indata2[0]):
			model.meshbuffers[t].vertices.append(SFVertex(unpack("6f4B2f2H", msbfile.read(40))))
		for i in range(indata2[1]):
			model.meshbuffers[t].triangles.append(SFTriangle(unpack("4H", msbfile.read(8)), total_v, t))
		mat = SFMaterial()
		unpack("1H", msbfile.read(2))
		mat.texMain.set(unpack("1i2B1H4B1f64s", msbfile.read(80)))
		mat.texSecondary.set(unpack("1i2B1H4B1f64s", msbfile.read(80)))
		mat.diffCol = list(unpack("4B", msbfile.read(4)))
		mat.emitCol = list(unpack("4B", msbfile.read(4)))
		mat.specCol = list(unpack("4B", msbfile.read(4)))
		#divide colors by 255
		model.meshbuffers[t].material = mat
		#not important data
		indata6 = unpack("8f", msbfile.read(32))
		indata7 = []
		if t == modelnum-1:
			indata7 = unpack("6f", msbfile.read(24))
		else:
			indata7 = unpack("2B", msbfile.read(2))
		total_v += len(model.meshbuffers[t].vertices)
		total_t += len(model.meshbuffers[t].triangles)
		#FIX HERE: if a model contains garbage (0 vertices, 0 faces), blender fails to load whole mesh
		#fix for equipment_weapon_spear01
		if indata2[0] == 0 and indata2[1] == 0:
			del model.meshbuffers[-1]
			modelnum -= 1
	
	#create materials
	tex = None
	texind = 0
	texnames = []
	textures = []
	materials = []
	for t in range(modelnum):
		tex = None
		texname = model.meshbuffers[t].material.texMain.texName
		if not(texname in texnames):
			texind = len(texnames)
			texnames.append(texname)
			tex = bpy.data.textures.new(name = texname, type = 'IMAGE')
			image = None
			imagepath=os.path.split(infile)[0] + "\\" + texname + ".dds"
			image = bpy.data.images.load(imagepath)
			if image is not None:
				tex.image = image
			textures.append(tex)
		else:
			texind = texnames.index(texname)
			tex = textures[ind]
		mat = model.meshbuffers[t].material
		materialname = "Material "+str(t+1)
		matdata = bpy.data.materials.new(materialname)
		matdata.use_transparency = True
		matdata.specular_intensity = -10000.0
		matdata.alpha = 0.0
		matdata.diffuse_color = [mat.diffCol[2]/255,  mat.diffCol[1]/255,  mat.diffCol[0]/255]
		matdata.specular_color = [mat.specCol[2]/255, mat.specCol[1]/255, mat.specCol[0]/255]
		matdata["SFRenderMode"] = mat.texMain.texRenderMode
		mtex = matdata.texture_slots.add()
		mtex.texture = tex
		mtex.texture_coords = 'UV'
		mtex.use_map_color_diffuse = True
		mtex.use_map_alpha = True
		mtex.alpha_factor = mat.texMain.texAlpha
		mtex.uv_layer = model.meshbuffers[t].material.texMain.texName#"Material "+str(t+1)
		materials.append(matdata)
	
	#FIX THIS PART: if there are vertices a file does not reference (even though they're not needed), blender crashes
	#fix building_human_tower_crossbow
	vlist = []
	flist = []
	vmax = 0
	vinds = []
	for t in range(modelnum):
		for v in model.meshbuffers[t].vertices:
			vlist.append(v)
			vinds.append(v.ind)
			vmax = max(vmax,v.ind)
		for f in model.meshbuffers[t].triangles:
			flist.append(f)
	vinds.sort()
	i=0
	j=0
	while True:
		while vinds[i] != j:
			vlist.append(SFVertex([0, 0, 0, 0, 0, 1, 255 ,255 ,255 ,255 ,0, 0, j]))
			j+=1
			if j >= len(vinds):
				break
		i+=vinds.count(vinds[i])
		j+=1
		if max(i,j) >= len(vinds):
			break
			
		
	real_inds = {}     #reordering dict
	for i in range(len(vlist)):
		real_inds[vlist[i].ind] = i
	real_verts = []    #good vertices order
	for i in range(len(real_inds.keys())):
		real_verts.append(vlist[real_inds[i]])
	real_faces = []    #faces indexed according to good vertices order, compared to SFData
	for i in range(len(flist)):
		real_faces.append(SFTriangle([vlist[flist[i].indices[0]].ind, vlist[flist[i].indices[1]].ind, vlist[flist[i].indices[2]].ind], 0, flist[i].material))
	real_texcoords = []
	for i in range(len(flist)):
		real_texcoords.append([[vlist[flist[i].indices[0]].uv[0], vlist[flist[i].indices[0]].uv[1]],[vlist[flist[i].indices[1]].uv[0], vlist[flist[i].indices[1]].uv[1]],[vlist[flist[i].indices[2]].uv[0], vlist[flist[i].indices[2]].uv[1]]])
	
	objName = (os.path.split(infile)[1].replace(".msb",""))
	
	me_ob = bpy.data.meshes.new(objName)
	me_ob.vertices.add(len(real_verts))
	me_ob.tessfaces.add(total_t)
	for i in range(len(real_verts)):
		v = real_verts[i]
		me_ob.vertices[i].co = v.pos
		me_ob.vertices[i].normal = v.normal
	for i in range(len(real_faces)):
		f = real_faces[i]
		me_ob.tessfaces[i].vertices_raw = f.indices
	
	for t in range(modelnum):
		me_ob.materials.append(materials[t])
		me_ob.uv_textures.new(name=model.meshbuffers[t].material.texMain.texName)
	
	for i in range(len(real_faces)):
		uv_layer = me_ob.tessface_uv_textures[real_faces[i].material]
		uv_layer.data[me_ob.tessfaces[i].index].uv1 = mathutils.Vector((real_texcoords[i][0][0], real_texcoords[i][0][1]))
		uv_layer.data[me_ob.tessfaces[i].index].uv2 = mathutils.Vector((real_texcoords[i][1][0], real_texcoords[i][1][1]))
		uv_layer.data[me_ob.tessfaces[i].index].uv3 = mathutils.Vector((real_texcoords[i][2][0], real_texcoords[i][2][1]))
		me_ob.tessfaces[i].material_index = real_faces[i].material
	
	final_mesh = bpy.data.objects.new(name = objName, object_data = me_ob)
	final_mesh.active_material = materials[0]
	
	me_ob.update()
	bpy.context.scene.objects.link(final_mesh)
	bpy.context.scene.update()
	
	if bImportSkeleton:
		infile2 = infile.replace(".msb", ".bor")
		
		print ("--------------------------------------------------")
		print ("---------SCRIPT EXECUTING PYTHON IMPORTER---------")
		print ("--------------------------------------------------")
		print (" DEBUG Log:",bDebugLogMSB)
		print ("Importing file: ", infile2)
		
		skeleton = SF_Skeleton()
		borfile = open(infile2, 'r',)
		while True:
			line = borfile.readline().strip()
			if line == "[AnimData]":
				borfile.readline()
				data = borfile.readline().strip().split()
				num_of_bones = int(data[2])
				data = borfile.readline().strip().split()
				num_of_sv = int(data[2])
				for i in range(num_of_bones):
					b = SF_Bone()
					borfile.readline()
					borfile.readline()
					data = borfile.readline().strip().split()
					bname = ""
					for k in range(2,len(data)):
						bname = bname+data[k].replace('"','')
						if k != len(data)-1:
							bname += " "
					b.name = bname
					data = borfile.readline().strip().split()
					b.id = int(data[2])
					data = borfile.readline().strip().split()
					b.parent = int(data[2])
					borfile.readline()
					borfile.readline()
					data = borfile.readline().strip().split()   #not needed?
					data = borfile.readline().strip().split()
					b.sv.translation = mathutils.Vector((float(data[2].replace(",","")), float(data[3].replace(",","")), float(data[4].replace(",",""))))
					data = borfile.readline().strip().split()
					b.sv.orientation.w = float(data[2])
					data = borfile.readline().strip().split()
					b.sv.orientation.x = float(data[2].replace(",",""))
					b.sv.orientation.y = float(data[3].replace(",",""))
					b.sv.orientation.z = float(data[4].replace(",",""))
					b.blender_length = b.sv.translation.length
					print(i, b.sv.translation, b.sv.orientation)
					file = borfile.readline().strip()
					while file != "}":
						skinvertex = SkinVertex()
						borfile.readline()
						data = borfile.readline().strip().split()
						id = int(data[2])
						data = borfile.readline().strip().split()
						pos = mathutils.Vector((float(data[2].replace(",","")), float(data[3].replace(",","")), float(data[4].replace(",",""))))
						data = borfile.readline().strip().split()
						w = float(data[2])
						borfile.readline()
						borfile.readline()
						skinvertex.id = id
						skinvertex.weight = w
						skinvertex.pos = pos
						b.blender_vertices.append(skinvertex)
						file = borfile.readline().strip()
					skeleton.bones.append(b)
					borfile.readline()
					borfile.readline()
					borfile.readline()
				break
		skeleton.initialize_bones()
		#skeleton.build_mesh()        # debug function
		
		armdata = bpy.data.armatures.new("armaturedata")
		ob_new = bpy.data.objects.new(os.path.split(infile2)[1].replace(".bor"," - skeleton"), armdata)
		bpy.context.scene.objects.link(ob_new)
		ob_new["SFReferenceName"] = os.path.split(infile2)[1]
		for i in bpy.context.scene.objects:
			i.select = False #deselect all objects
		ob_new.select = True
		bpy.context.scene.objects.active = ob_new
		
		if bpy.ops.object.mode_set.poll():
			bpy.ops.object.mode_set(mode='EDIT')
		
		for i in range(len(skeleton.bones)):
			bone = skeleton.bones[i]
			newparent = None
			newbone = ob_new.data.edit_bones.new(bone.name)
			newbone.head = [0, 0, 0]
			if bone.parent != -1:
				newparent = ob_new.data.edit_bones[bone.parent]
				newbone.parent = newparent
			newbone.head = [0, 0, 0]
			newbone.tail = [0, 0.1, 0]
			newbone.use_inherit_rotation = True
			newbone.use_inherit_scale = False
			newbone.use_local_location = False
			
		bpy.ops.object.mode_set(mode = 'POSE')
		print(ob_new.pose.bones.keys())
		
		for i in range(len(skeleton.bones)):
			bone = skeleton.bones[i]
			posebone = ob_new.pose.bones[bone.name]
			posebone.rotation_mode = 'QUATERNION'
			posebone.location = bone.sv.translation
			posebone.rotation_quaternion = bone.sv.orientation
			
		#transform vertices...
		ob_new.select = False
		final_mesh.select = True
		
		
		for i in range(len(me_ob.vertices)):
			me_ob.vertices[i].co = [0, 0, 0]
			
		bpy.ops.object.mode_set(mode = 'EDIT')
		for bone in skeleton.bones:
			for v in bone.blender_vertices:
				print(v.id)
				me_ob.vertices[v.id].co = [me_ob.vertices[v.id].co[0]+v.pos[0]*v.weight, me_ob.vertices[v.id].co[1]+v.pos[1]*v.weight, me_ob.vertices[v.id].co[2]+v.pos[2]*v.weight]
				
		bpy.ops.object.mode_set(mode = 'OBJECT')
		for bone in skeleton.bones:
			group = final_mesh.vertex_groups.new(bone.name)
			print(bone.name)
			for v in bone.blender_vertices:
				group.add([v.id], v.weight, "ADD")
				
		final_mesh.data.update()
			
	bpy.context.scene.update()
	
	if(bImportSkeleton):
		final_mesh.select = False
		ob_new.select = False
		final_mesh.select = True
		ob_new.select = True
		bpy.ops.object.parent_set(type="ARMATURE")
					
	

def getInputFilenameMSB(self, filename, bDebugLogMSB, bImportSkeleton):
	checktype = filename.split('\\')[-1].split('.')[1]
	print ("------------",filename)
	if checktype.lower() != 'msb':
		print ("  Selected file = ", filename)
		raise (IOError, "The selected input file is not a *.msb file")
		#self.report({'INFO'}, ("Selected file:"+ filename))
	else:
		msbimport(filename, bDebugLogMSB, bImportSkeleton)


class import_msb(bpy.types.Operator):
	'''Load a spellforce msb File'''
	bl_idname = "import_mesh_skeleton.msb"
	bl_label = "Import MSB/BOR"
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
	
	bImportSkeleton = BoolProperty(
			name="Import Skeleton",
			description="Check this if you want to also import skeleton"
						"Skeleton must have the same filename as mesh",
			default=True,
			)

	def execute(self, context):
		getInputFilenameMSB(self, self.filepath, self.bDebugLogMSB, self.bImportSkeleton)
		return {'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager
		wm.fileselect_add(self)
		return {'RUNNING_MODAL'}

def menu_func(self, context):
	self.layout.operator(import_msb.bl_idname, text="Spellforce Mesh/Skeleton (.msb/.bor)")

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_import.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
	register()