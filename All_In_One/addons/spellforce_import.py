bl_info = {
	"name": "Import Spellforce Mesh Files (.msb)",
	"author": "leszekd25",
	"version": (1, 0, 0),
	"blender": (2, 78, 0),
	"location": "File > Import > Mesh File (.msb)",
	"description": "Import Spellforce Mesh Data",
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

def msbimport(infile, bDebugLogMSB):
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
		matdata["SFFlags"] = mat.texMain.flag
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
	

def getInputFilenameMSB(self, filename, bDebugLogMSB):
	checktype = filename.split('\\')[-1].split('.')[1]
	print ("------------",filename)
	if checktype.lower() != 'msb':
		print ("  Selected file = ", filename)
		raise (IOError, "The selected input file is not a *.msb file")
		#self.report({'INFO'}, ("Selected file:"+ filename))
	else:
		msbimport(filename, bDebugLogMSB)


class import_msb(bpy.types.Operator):
	'''Load a spellforce msb File'''
	bl_idname = "import_mesh.msb"
	bl_label = "Import MSB"
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
		getInputFilenameMSB(self, self.filepath, self.bDebugLogMSB)
		return {'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager
		wm.fileselect_add(self)
		return {'RUNNING_MODAL'}

def menu_func(self, context):
	self.layout.operator(import_msb.bl_idname, text="Spellforce Mesh (.msb)")

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_import.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
	register()