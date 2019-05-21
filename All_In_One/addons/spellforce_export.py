bl_info = {
	"name": "Export Spellforce Mesh Files (.msb)",
	"author": "leszekd25",
	"version": (1, 0, 0),
	"blender": (2, 78, 0),
	"location": "File > Export > Mesh File (.msb)",
	"description": "Export Spellforce Mesh Data (static only)",
	"warning": "totally untested",
	"category": "Import-Export",
}
 
"""
just testing export tool for blender
let's hope it works
also this is just a modification of unreal .psk export add-on
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
 
def msbexport(infile, bDebugLogMSB): #single model static mesh (equipment, decorations)
	global DEBUGLOG
	DEBUGLOG = bDebugLogMSB
	print ("--------------------------------------------------")
	print ("---------SCRIPT EXECUTING PYTHON IMPORTER---------")
	print ("--------------------------------------------------")
	print (" DEBUG Log:",bDebugLogMSB)
	print ("Importing file: ", infile)
	
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
		def get(self):
			charray = []
			for i in range(64):
				if i >= len(self.texName):
					charray.append(0)
				else:
					charray.append(ord(self.texName[i]))
			charray = bytes(charray)
			return pack("1i2B1H4B1f64s", self.texID, self.unknown1, self.texUVMode, self.unused, self.texRenderMode, self.texAlpha, self.flag, self.depthbias, self.tiling, charray)
			
	
	class SFMaterial:
		def __init__(self):
			self.texMain = SFMap()
			self.texSecondary = SFMap()
			self.diffCol = []
			self.emitCol = []
			self.specCol = []
	
	class BLModel:
		def __init__(self):
			self.vertices = []
			self.vert_unique = []
			self.vert_reindex = []
			self.faces = []
			self.material = SFMaterial()
			self.bbox = [10000, 10000, 10000, -10000, -10000, -10000]
   
	class BLVertex:
		def __init__(self):
			self.ind = -1
			self.uv = [0, 0]
		def equal(self, v):
			return (self.ind == v.ind and self.uv[0] == v.uv[0] and self.uv[1] == v.uv[1])
	
	object = bpy.context.object
	obname=object.name
	mesh = object.data
	
	msbfile = open(infile+".msb",'wb')
	if (DEBUGLOG):
		logpath = infile.replace(".msb", ".txt")
		print("logpath:",logpath)
		logf = open(logpath,'w')
	
	print("PHASE 1 and 2")
	models = []
	modelnum = len(mesh.materials)
	for i in range(modelnum):
		models.append(BLModel())
	for poly in mesh.polygons:	
		mat = poly.material_index
		f = []
		for loop_index in range(poly.loop_start, poly.loop_start+poly.loop_total):
			uv_layer = mesh.uv_layers[mesh.materials[mat].texture_slots[0].uv_layer].data
			v=BLVertex()
			v.ind = mesh.loops[loop_index].vertex_index
			v.uv = uv_layer[loop_index].uv
			models[mat].vertices.append(v)
			f.append(len(models[mat].vertices)-1)
		models[mat].faces.append(f)
	print("PHASE 3, 4")
	for i in range(modelnum):
		models[i].vert_unique = []
		for k in range(len(models[i].vertices)):
			unique = True
			for l in range(len(models[i].vert_unique)):
				if models[i].vertices[k].equal(models[i].vertices[models[i].vert_unique[l]]):
					unique = False
					break
			if unique:
				models[i].vert_unique.append(k)
		models[i].vert_reindex = []
		for k in range(len(models[i].vertices)):
			for l in range(len(models[i].vert_unique)):
				if models[i].vertices[k].equal(models[i].vertices[models[i].vert_unique[l]]):
					models[i].vert_reindex.append(l)
		for n in range(len(models[i].faces)):
			for k in range(3):
				models[i].faces[n][k] = models[i].vert_reindex[models[i].faces[n][k]]
	print("PHASE 5")
	for i in range(modelnum):
		for k in range(len(models[i].vert_unique)):
			vind = models[i].vertices[models[i].vert_unique[k]].ind
			vpos = mesh.vertices[vind].co
			vnormal = mesh.vertices[vind].normal
			vcol = [255, 255, 255, 255]
			vuv = models[i].vertices[models[i].vert_unique[k]].uv
			v = SFVertex([vpos[0], vpos[1], vpos[2], vnormal[0], vnormal[1], vnormal[2], vcol[0], vcol[1], vcol[2], vcol[3], vuv[0], vuv[1], vind])
			models[i].vert_unique[k] = v
	for i in range(modelnum):
		bl_material = mesh.materials[i]
		models[i].material.diffCol = [int(bl_material.diffuse_color[2]*255),int(bl_material.diffuse_color[1]*255),int(bl_material.diffuse_color[0]*255),0]
		models[i].material.specCol = [int(bl_material.specular_color[2]*255),int(bl_material.specular_color[1]*255),int(bl_material.specular_color[0]*255),0]
		models[i].material.emitCol = [0, 0, 0, 0]
		if bl_material.get("SFRenderMode") is not None:
			models[i].material.texMain.texRenderMode = bl_material["SFRenderMode"]
		else:
			models[i].material.texMain.texRenderMode = 0
		if bl_material.get("SFFlags") is not None:
			models[i].material.texMain.flag = bl_material["SFFlags"]
		else:
			models[i].material.texMain.flag = 7
		models[i].material.texMain.texAlpha = int(bl_material.texture_slots[0].alpha_factor*255)
		models[i].material.texMain.texName = bl_material.texture_slots[0].name
	for i in range(modelnum):
		for v in models[i].vert_unique:
			models[i].bbox[0] = min(models[i].bbox[0], v.pos[0])
			models[i].bbox[1] = min(models[i].bbox[1], v.pos[1])
			models[i].bbox[2] = min(models[i].bbox[2], v.pos[2])
			models[i].bbox[3] = max(models[i].bbox[3], v.pos[0])
			models[i].bbox[4] = max(models[i].bbox[4], v.pos[1])
			models[i].bbox[5] = max(models[i].bbox[5], v.pos[2])
	bbox = [10000, 10000, 10000, 10000, 10000, 10000]
	for i in range(modelnum):
		bbox[0] = min(bbox[0], models[i].bbox[0])
		bbox[1] = min(bbox[1], models[i].bbox[1])
		bbox[2] = min(bbox[2], models[i].bbox[2])
		bbox[3] = min(bbox[3], models[i].bbox[3])
		bbox[4] = min(bbox[4], models[i].bbox[4])
		bbox[5] = min(bbox[5], models[i].bbox[5])
	
	outdata = pack("BBHBB", 0, 2, modelnum, 0, 0)
	msbfile.write(outdata)
	for i in range(modelnum):
		outdata2 = pack("2b4H", 0, 2, len(models[i].vert_unique), 0, len(models[i].faces), 0)
		msbfile.write(outdata2)
		print(len(models[i].vert_unique))
		for k in range(len(models[i].vert_unique)):
			v = models[i].vert_unique[k]
			outdata3 = pack('6f4B2fI', v.pos[0], v.pos[1], v.pos[2], v.normal[0], v.normal[1], v.normal[2], v.col[0], v.col[1], v.col[2], v.col[3], v.uv[0], v.uv[1], v.ind)
			msbfile.write(outdata3)
		print(len(models[i].faces))
		for k in range(len(models[i].faces)):
			f = models[i].faces[k]
			outdata4 = pack("4H", f[0], f[1], f[2], i)
			msbfile.write(outdata4)
		msbfile.write(pack("2B", 0, 2))
		msbfile.write(models[i].material.texMain.get())
		msbfile.write(models[i].material.texSecondary.get())
		msbfile.write(pack("4B", models[i].material.diffCol[0],  models[i].material.diffCol[1],  models[i].material.diffCol[2],  models[i].material.diffCol[3]))
		msbfile.write(pack("4B", models[i].material.emitCol[0],  models[i].material.emitCol[1],  models[i].material.emitCol[2],  models[i].material.emitCol[3]))
		msbfile.write(pack("4B", models[i].material.specCol[0],  models[i].material.specCol[1],  models[i].material.specCol[2],  models[i].material.specCol[3]))
		msbfile.write(pack("6f", models[i].bbox[0], models[i].bbox[1],models[i].bbox[2],models[i].bbox[3],models[i].bbox[4],models[i].bbox[5]))
		msbfile.write(pack("2f", 1.0, 0.0))
	msbfile.write(pack("6f", bbox[0],bbox[1],bbox[2],bbox[3],bbox[4],bbox[5]))
	msbfile.close()
	
	bpy.context.scene.update()
 
def getInputFilenameMSB(self, filename, bDebugLogMSB):
	#something here?
	msbexport(filename, bDebugLogMSB)
 
 
class export_msb(bpy.types.Operator):
	'''Load a spellforce msb File'''
	bl_idname = "export_mesh.msb"
	bl_label = "Export MSB"
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
	self.layout.operator(export_msb.bl_idname, text="Spellforce Mesh (.msb)")
 
def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_export.append(menu_func)
 
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_export.remove(menu_func)
 
if __name__ == "__main__":
	register()