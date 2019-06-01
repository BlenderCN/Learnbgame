#==============================================================
"""

Blender Shenmue Model Import Addon
Copyright Benjamin Collins 2016,2018

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software 
without restriction, including without limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons
to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

"""
#==============================================================

#Blender Addon Definition
bl_info = {
	"name" : "Shenmue Model Format",
	"author" : "Benjamin Collins",
	"version" : (0,0,1),
	"blender" : (2,74,0),
	"location" : "File > Import",
	"description" : "Import Shenmue mesh data",
	"category": "Learnbgame",
}

#Import Libraries
import os
import bpy

#Import User Libraries
from .matrix_44 import Mat4
from .bitstream import BitStream

#Import Blender Classes
from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy_extras.image_utils import load_image

#Define Global Constants
BIT_0 = 0x01
BIT_1 = 0x02
BIT_2 = 0x04
BIT_3 = 0x08
BIT_4 = 0x10
BIT_5 = 0x20
BIT_6 = 0x40
BIT_7 = 0x80

#==============================================================
"""
Main
Register addon so that the option to import .nj files
appears in the menu from File -> Import
"""
#==============================================================

#Callback fro when Import .nj is called
def menu_func_import(self, context):
	self.layout.operator(ImportMT5.bl_idname, text="Shenmue Model (.mt5)")

#Append .nj option to File > Import
def register():
	bpy.utils.register_class(ImportMT5)
	bpy.types.INFO_MT_file_import.append(menu_func_import)

#Remove .nj option to File > Import
def unregister():
	bpy.utils.unregister_class(ImportMT5)
	bpy.types.INFO_MT_file_import.remove(menu_func_import)

#Main function for Blender to apply register
if __name__ == "__main__":
	register()

#==============================================================
"""
Class Import Mt5
Object which implements importing and drawing mesh
"""
#==============================================================


#Class that Blender Interfaces with
class ImportMT5(Operator, ImportHelper):

	#Properties for import file extension
	bl_idname = "import.shenmue"
	bl_label = "Import Shenmue"

	filename_ext = ".mt5"
	filter_glob = StringProperty(default="*.mt5", options={'HIDDEN'})

	#Execute is run when a file is selected for import
	def execute(self, context):
		#Create ninja chunk model
		mt5 = ShenmueModel(self.filepath)

		#Read and load textures
		mt5.loadTextureList()

		#Parse model to mesh list
		mt5.readModelList()
		mt5.close()

		#Get array of meshes
		meshList = mt5.getMeshlist()

		# Return cancel if no meshes
		if not len(meshList):
			return {'CANCELLED'}

		# Create object and add mesh to scene
		for i in range(len(meshList)):
			obj = bpy.data.objects.new("HcModel[%d]"%i, meshList[i])
			scene = bpy.context.scene
			scene.objects.link(obj)

		return {'FINISHED'}

#==============================================================
"""
Class Shenmue Model
Interface for parsing and rendering Shenmue Models
"""
#==============================================================

class ShenmueModel:

	def __init__(self, filepath):
		self.fp = filepath
		self.bs = BitStream(filepath)
		self.iff = self.bs.readUInt()
		self.texOfs = self.bs.readUInt()
		self.mdlOfs = self.bs.readUInt()

		self.vertex_pointer = 0
		self.vertexList = []
		self.normalList = []

		self.imgList  = []
		self.meshList = []

	def loadTextureList(self):

		#Get base directory of model
		dirName = os.path.dirname(self.fp)
		dirName += "/"

		texBase = os.path.basename(self.fp)
		texBase = os.path.splitext(texBase)[0]

		self.bs.seek_set(self.texOfs)
		texd = self.bs.readUInt()
		texLen = self.bs.readUInt()
		nbTex = self.bs.readUInt()

		for i in range(nbTex):
			#Check for png extension of texture Name
			texName = "%s_%02d" % (texBase, i)
			texPath = dirName + texName + ".png"

			#If no texture exists, continue
			if not os.path.exists(texPath):
				self.imgList.append(None)
				continue

			print(texPath)
			#Create new blender texture
			blTex = bpy.data.textures.new(texName, type='IMAGE')
			blTex.image = load_image(texPath)
			self.imgList.append(blTex)

		return 1

	def readModelList(self):
		self.bs.seek_set(self.mdlOfs)
		self.readNodeTree()
		return 1

	def readNodeTree(self, ptx = None, pvp = 0):
		node = self.bs.readNode()
		mtx = self.createMatrix(node, ptx)

		model = None

		if node['model']:
			self.bs.seek_set(node['model'])
			model = self.bs.readModel()

			if model['vertex']:
				self.bs.seek_set(model['vertex'])
				self.readVertexList(model['nbVertex'], mtx)

			if model['polygon']:
				self.bs.seek_set(model['polygon'])
				self.readPolygonList(pvp)

		passOn = self.vertex_pointer
		if model is not None:
			passOn += model['nbVertex']

		if node['child']:
			self.bs.seek_set(node['child'])
			self.readNodeTree(mtx, passOn)

		if(node['sibling']):
			self.bs.seek_set(node['sibling'])
			self.readNodeTree(ptx, pvp)

		return 1

	def createMatrix(self, node, ptx):
		mtx = Mat4()

		mtx.scale(node['scl'])

		mtx.rotate(node['rot'])

		mtx.translate(node['pos'])

		if ptx is not None:
			mtx.multiply(ptx.getMatrix())

		return mtx

	def readVertexList(self, nbVertex, mtx):

		#Save vertex pointer
		self.vertex_pointer = len(self.vertexList)

		#Add each entry into the vertex list
		for i in range(nbVertex):
			pos = self.bs.readVec3()
			pos = mtx.apply(pos)
			tmp = pos[1]
			pos[1] = pos[2]
			pos[2] = tmp
			self.vertexList.append(pos)
			norm = self.bs.readVec3()
			self.normalList.append(norm)

		return 1

	def readPolygonList(self, pvp):
		#Material definition
		mat = {}

		#Boolean for tracking status
		polygonStart = False

		while True:
			#Read dword as two shorts
			cnkhead = self.bs.readUShort()
			cnkflag = self.bs.readUShort()

			#Terminate Polygon strip signature
			if cnkhead == 0x8000 and cnkflag == 0xFFFF:
				return

			#Material definition signature
			elif cnkhead == 0x000e and cnkflag == 0x0008:
				mat['diffuse'] = self.bs.readColor()

			#Polygonstart definition signature
			elif cnkflag == 0x0010:
				if cnkhead == 0x0002 or cnkhead == 0x0003:
					polygonStart = True

			#Check for strip list to start
			elif polygonStart:

				#index, u, v format
				if cnkhead == 0x0009:
					mat['texId'] = cnkflag

				#index, u, v format
				if cnkhead == 0x0011:
					polygonStart = False
					self.readStripList(mat, pvp, True)

				#index only format
				elif cnkhead == 0x0013:
					polygonStart = False
					self.readStripList(mat, pvp)

				#index, u, v, u1, v1
				elif cnkhead == 0x001c:
					polygonStart = False
					self.readStripList(mat, pvp, True, True)

			#Check pointer offset from dword
			if self.bs.tell() % 4 == 2:
				self.bs.seek_cur(0x02)

		return 1

	def readStripList(self, mat, pvp, hasUv0 = False, hasUv1 = False):
		stripList = []
		nbStrips = self.bs.readUShort()

		for i in range(nbStrips):
			strip = []
			stripLen = abs(self.bs.readShort())

			for k in range(stripLen):
				#Read string indice
				indice = {'idx' : self.bs.readShort()}

				#If index is less than zero, seek from parent pointer
				if indice['idx'] < 0:
					indice['idx'] += pvp

				#Otherwise seek from the current position in list
				else:
					indice['idx'] += self.vertex_pointer

				# Read UV values
				if hasUv0:
					u = self.bs.readShort() / 0x3ff
					v = self.bs.readShort() / 0x3ff
					indice['uv'] = [u, v]

				#Possibly vertex color, not implemented
				if hasUv1:
					self.bs.seek_cur(0x04)

				#Append indice to strip
				strip.append(indice)
			#Append strip to strip list
			stripList.append(strip)

		#Create mesh from striplist
		self.createMesh(mat, stripList)
		return 1

	def createMesh(self, mat, stripList):
		# Vertex map
		vmap   = {}
		# Vertex position list
		vlist  = []
		# Uv mappings list
		uvlist = []
		# Triangle strip list
		plist  = []

		#Loop through each strip
		for strip in stripList:
			strip = self.mapIndexList(strip, vmap, vlist, uvlist)

			#Convert strips into triangles
			for i in range(len(strip) - 2):
				a = strip[i + 0]
				b = strip[i + 1]
				c = strip[i + 2]
				if not i%2:
					plist.append([a,c,b])
				else:
					plist.append([a,b,c])

		#Create mesh
		mesh = bpy.data.meshes.new("Mesh")
		mesh.from_pydata(vlist, [], plist)

		#Handle UV coords
		if len(uvlist):
			mesh.uv_textures.new()
			uv_layer = mesh.uv_layers.active.data
			#Cycle through each polygon
			for poly in mesh.polygons:
				for loop in poly.loop_indices:
					#Get the vertex index for current loop
					vIndex = mesh.loops[loop].vertex_index
					#Apply uv coord to vertex
					uv_layer[loop].uv = uvlist[vIndex]

		# Update Mesh
		mesh.update(calc_tessface = True)

		#Create material
		blMat = bpy.data.materials.new("Mat")
		blMat.use_vertex_color_paint = True
		blMat.transparency_method = 'Z_TRANSPARENCY'
		blMat.use_transparency = True
		blMat.use_face_texture_alpha = True
		#blMat.diffuse_ramp_blend = "MULTIPLY"

		#diffuse
		if 'diffuse' in mat:
			color = mat['diffuse'].copy()
			blMat.alpha = color.pop()
			blMat.diffuse_color = color

		#texture
		print(mat)
		if 'texId' in mat:
			texId = mat['texId']
			if self.imgList[texId] != None:
				mTex = blMat.texture_slots.add()
				mTex.texture = self.imgList[texId]

		#Append mesh to chunk model
		mesh.materials.append(blMat)
		self.meshList.append(mesh)

		return 1

	def mapIndexList(self, strip, vmap, vlist, uvlist):
		local = []

		for indice in strip:
			# Convert index to string
			key = str(indice['idx'])

			# If not in vertex map then append
			if not key in vmap:

				# Set lookup to end of list
				idx = len(vlist)
				vmap[key] = [idx]
				i = indice['idx']
				vertex = self.vertexList[i]

				# Append position to vertex list
				vlist.append(vertex)

				# Append uv to list if required
				if 'uv' in indice:
					uvlist.append(indice['uv'])

			# If no UV present, then simply use first
			elif not 'uv' in indice:
				idx = vmap[key][0]

			else:
				# Check for uv list
				found = False
				for index in vmap[key]:
					if (indice['uv'][0] == uvlist[index][0] and
						indice['uv'][1] == uvlist[index][1] ):
						found = True
						idx = index

				# Add uv to list if not found
				if not found:
					idx = len(vlist)
					vmap[key].append(idx)
					i = indice['idx']
					vertex = self.vertexList[i]

					# Append position to vertex list
					vlist.append(vertex)

					# Append uv to list if required
					if 'uv' in indice:
						uvlist.append(indice['uv'])

			#Append local index to new strip list
			local.append(idx)

		return local

	def close(self):
		self.bs.close()
		return 1

	def getMeshlist(self):
		return self.meshList
