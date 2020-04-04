# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info= {
	"name": "Import HardReset Models",
	"author": "Mr. Wonko",
	"version": (0, 1),
	"blender": (2, 5, 9),
	"api": 39307,
	"location": "File > Import > HardReset Model (.meta)",
	"description": "Imports Hard Reset .meta/.rhm models",
	"warning": "",
	"category": "Learnbgame",
}
	
import bpy, os, struct

# helper function to read next char from file
def peek(file):
	c = file.read(1)
	if c != "":
		#file.seek(-1, 1) # 1 back (-1) from current position (1 == SEEK_CUR) - does not work for files -.-
		file.seek(file.tell() - 1) # 1 back from current position - this is more verbose anyway
	return c

# '[key] = [value]' -> '[key]', '[value]'
def toKeyValue(line):
	# split at =
	key, value = line.split("=", 1)
	if not value:
		return None, None
	# prettify, return
	return key.strip(), value

# '"string"' -> True, 'string'
def toString(s):
	s = s.strip()
	if s[:1] != '"' or s[-1:] != '"':
		return False, None
	return True, s[1:-1]

def toColor(s):
	s = s.strip()
	if s[:1] != '(' or s[-1:] != ')':
		return False, [0, 0, 0]
	s = s[1:-1]
	values = s.split(",")
	if len(values) < 3:
		return False, [0, 0, 0]
	return True, [float(values[0]), float(values[1]), float(values[2])]

# halfFloat (16 bit) read as Short to Float
# from http://forums.devshed.com/python-programming-11/converting-half-precision-floating-point-numbers-from-hexidecimal-to-decimal-576842.html
def halfToFloat(h):
    sign = int((h >> 15) & 0x00000001)
    exponent = int((h >> 10) & 0x0000001f)
    fraction = int(h & 0x000003ff)

    if exponent == 0:
       if fraction == 0:
          return int(sign << 31)
       else:
          while not (fraction & 0x00000400):
             fraction <<= 1
             exponent -= 1
          exponent += 1
          fraction &= ~0x00000400
    elif exponent == 31:
       if fraction == 0:
          return int((sign << 31) | 0x7f800000)
       else:
          return int((sign << 31) | 0x7f800000 | (fraction << 13))

    exponent = exponent + (127 -15)
    fraction = fraction << 13

    return struct.unpack("f", struct.pack("I", (sign << 31) | (exponent << 23) | fraction))[0]

UnhandledChunkKeys = []
# a chunk will translate into a mesh/object pair in Blender.
class Chunk:
	def __init__(self):
		self.message = ""
		self.startIndex = -1 # first (triangle) index belonging to this chunk - pretty much required, I guess
		self.primCount = -1 # amount of (triangle) indices belonging to this chunk - pretty much required, I guess
		self.baseIndex = 0 # indices must be offset by this much - allows for more than 2^16 vertices to be used, just not /per chunk/
		self.diffuse = "" # diffuse texture
		self.specular = "" # specular texture
		self.normal = "" # normal map texture
		self.vColor = [1, 1, 1] # vertex colour
		self.material = "" # material, for physics (esp. electricity) I guess
		# todo: add more!
	
	def loadFromMeta(self, file):
		#read lines while there are any interesting ones
		while peek(file) not in ["[", ""]: # next definition, EOF
			# read line
			line = file.readline()
			
			if line == "\n": # empty line
				continue
			line = line.strip("\n")
			# split at =
			key, value = toKeyValue(line)
			if not key:
				self.message = "line without ="
				return False
			#   use
			
			# mesh information
			if key == "StartIndex":
				self.startIndex  = int(value)
				continue
			if key == "PrimCount":
				self.primCount = int(value)
				continue
			if key == "BaseIndex":
				self.baseIndex = int(value)
				continue
			
			# material, basically
			if key == "Diffuse":
				self.diffuse = toString(value)
				continue
			if key == "Specular":
				self.specular = toString(value)
				continue
			if key == "Normal":
				self.normal = toString(value)
				continue
			if key == "vColor":
				self.material = toColor(value)
				continue
			
			# physics
			if key == "Material":
				self.material = toString(value)
				continue
			
			# bounds
			if key == "Bounds":
				# I don't need them bounds
				continue
				# todo: add more
				"""
				
				fBaseUVTile = 1.000000
				fLayerUVTile = 1.000000
				fWrapAroundTerm = 1.000000
				
				fSpecularMultiplier = 4.000000
				fSpecularPowerMultiplier = 20.000000
				fEnvMultiplier = 1.000000
				fEmissiveMultiplier = 1.000000
				"""
			
			# unhandled key?
			if key not in UnhandledChunkKeys: # only warn once
				print("Info: Unhandled Chunk Key \"%s\"" % (key))
				UnhandledChunkKeys.append(key)
				continue
		if self.startIndex == -1:
			self.message = "No StartIndex defined!"
			return False
		if self.primCount == -1:
			self.message = "No PrimCount defined!"
			return False
		return True
	
	def toBlender(self, geometry, name):
		vertexPositions = [] # not all the vertices are used...
		indices = [] # same for the indices, and they're also different since the vertices are different.
		indexMap = {} # which old vertex index maps to which new one?
		self.mesh = bpy.data.meshes.new(name)
		for triangleIndex in range(self.primCount): # need to build tuples, so I can't really iterate
			triangle = [0, 0, 0]
			# I don't want the mesh to contain unused vertices, so I need to iterate through the indices and only use those vertices.
			for vertexIndex in range(3):
				originalIndex = geometry.indices[self.startIndex + triangleIndex * 3 + vertexIndex] + self.baseIndex
				# that means I need to map the old indices (of the complete vertex list) to new ones (of this mesh's vertex list)
				# if this vertex has not yet been used...
				if originalIndex not in indexMap:
					# ... I need to add it to the list of used vertices and map its index
					indexMap[originalIndex] = len(vertexPositions)
					vertexPositions.append(geometry.vertices[originalIndex].position)
				# now it's just a matter of looking up the correct index.
				triangle[vertexIndex] = indexMap[originalIndex]
			indices.append(triangle)
		self.mesh.from_pydata(vertexPositions, [], indices) # vertices, edges, faces
		
		#UV Data
		assert(len(self.mesh.uv_textures) == 0)
		uv_texture = self.mesh.uv_textures.new() # create UV Texture - it contains UV Mapping data
		assert(len(uv_texture.data) == self.primCount) # the data should already exist, but zeroed.
		for triangleIndex in range(self.primCount):
			uv = [None, None, None]
			for vertexIndex in range(3):
				index = geometry.indices[self.startIndex + triangleIndex * 3 + vertexIndex] + self.baseIndex
				vertex = geometry.vertices[index]
				uv[vertexIndex] = vertex.uv
			uv_texture.data[triangleIndex].uv1 = uv[0]
			uv_texture.data[triangleIndex].uv2 = uv[1]
			uv_texture.data[triangleIndex].uv3 = uv[2]
		
		self.object = bpy.data.objects.new(name, self.mesh) # no data assigned to this object -> empty
		bpy.context.scene.objects.link(self.object) # add to current scene
		return True

UnhandledMeshKeys = []
# more like a group of mesh objects, though they may possibly contain only one (or none?)
class Mesh:
	def __init__(self):
		self.message = ""
		
		self.name = ""
		self.childNum = 0 # not sure what this is
		
		# how many chunks, starting from which index?
		self.numChunks = -1
		self.chunkStart = -1
	
	def loadFromMeta(self, file):
		#read lines while there are any interesting ones
		while peek(file) not in ["[", ""]: # next definition, EOF
			# read line
			line = file.readline()
			
			if line == "\n": # empty line - should not happen?
				continue
			line = line.strip("\n")
			# split at =
			key, value = toKeyValue(line)
			if not key:
				self.message = "line without ="
				return False
			#   use
			
			# use
			if key == "ChunkCount":
				self.numChunks = int(value)
				continue
			if key == "ChunkStart":
				self.chunkStart = int(value)
				continue
			if key == "Name":
				success, self.name = toString(value)
				if not success:
					self.message = "Name is no string"
					return False
				continue
			if key == "ChildNum":
				self.childNum = int(value)
				continue
			if key == "Bounds":
				# I don't need to read bounds - I just have to save 'em.
				continue
			# unhandled key?
			if key not in UnhandledMeshKeys: # only warn once
				print("Info: Unhandled Mesh Key \"%s\"" % (key))
				UnhandledMeshKeys.append(key)
				continue
		
		if self.numChunks == -1:
			self.message = "No ChunkCount defined!"
			return False
		if self.chunkStart == -1:
			self.message = "No ChunkStart defined!"
			return False
		
		return True
	
	def toBlender(self, geometry):
		""" Creates a Group (empty) and adds the children """
		self.object = bpy.data.objects.new(self.name, None) # no data assigned to this object -> empty
		bpy.context.scene.objects.link(self.object) # add to current scene
		for index, chunk in enumerate(geometry.chunks[self.chunkStart:self.chunkStart+self.numChunks]):
			if not chunk.toBlender(geometry, "%s_%d" % (self.name, index)):
				self.message = chunk.message
				return False
			chunk.object.parent = self.object
		return True

class Vertex:
	def __init__(self):
		self.position = [0, 0, 0]
		self.uv = [0, 0]
		# what are the other values saved?
	
	def loadFromRhm(self, file):
		bindata = file.read(32) # a vertex is 32 bytes long.
		if len(bindata) < 32:
			return False, "Unexpected End of File"
		data = struct.unpack("3f12x2H4x", bindata) # 3 floats (position), 12 unknown bytes, 2 unsigned? shorts (UV) and another 4 unknown/unused bytes (always 0)
		for i in range(3):
			self.position[i] = data[i]
		shortSize = pow(2, 16)
		for i in range(2):
			# negative position (offset) so I don't need to change it when I figure out the other 12 bytes (neat, huh?)
			# I normalize the value to [0.0, 1.0] - I guess that's correct?
			self.uv[i] = halfToFloat(data[-2+i])
		self.uv[1] = 1 - self.uv[1] # flip Y
		return True, ""

UnhandledGeometryKeys = []
class Geometry:
	def __init__(self):
		# error message, if any
		self.message = ""
		
		self.numVertices = -1
		self.numIndices = -1
		self.numMeshes = -1
		# I wonder why there is no NumChunks?
		
		self.meshes = []
		self.chunks = []
		
		self.vertices = []
		self.indices = () # all the indices, not grouped
	
	def loadFromMeta(self, file):
		while peek(file) not in ["[", ""]:
			line = file.readline()
			if line == "\n":
				continue
			line = line.strip("\n")
			
			# split at =
			key, value = toKeyValue(line)
			if not key:
				self.message = "line without ="
				return False
			
			#   use
			if key == "Meshes":
				self.numMeshes = int(value)
				continue
			if key == "Vertices":
				self.numVertices = int(value)
				continue
			if key == "Indices":
				self.numIndices = int(value)
				continue
			# unhandled key?
			if key not in UnhandledGeometryKeys: # only warn once
				print("Info: Unhandled Geometry Key \"%s\"" % (key))
				UnhandledGeometryKeys.append(key)
				continue
		return True
	
	def loadFromRhm(self, file):
		# read vertices
		for i in range(self.numVertices):
			v = Vertex()
			success, message = v.loadFromRhm(file)
			if not success:
				self.message = "Error reading vertex %d: %s" % (i, message)
				return False
			self.vertices.append(v)
		print("Read %d vertices" % self.numVertices)
		
		# read triangles
		bindata = file.read(2*self.numIndices)
		if len(bindata) < 2*self.numIndices:
			self.message = "Error reading indices: Unexpected end of file!"
			return False
		self.indices = struct.unpack("%dH" % self.numIndices, bindata) # 3 unsigned shorts (2 byte - only up to 65536 vertices!)
		print("Read %d indices" % self.numIndices)
		
		# read check sum
		checksumBin = file.read(4)
		if len(checksumBin) < 4:
			self.message = "Error reading checksum: Unexpected end of file!"
			return False
		checksum = struct.unpack("i", checksumBin)
		print("Checksum (?): %d" % checksum)
		
		return True
	
	def toBlender(self):
		for mesh in self.meshes:
			if not mesh.toBlender(self):
				self.message = mesh.message
				return False
		return True

unhandledBlocks = []
class HRImporter:
	def __init__(self):	
		self.message = ""
		self.geometry = None
	
	def importModel(self, filepath):
		# strip extension
		pathWithoutExtension, extension = os.path.splitext(filepath)
		# is this a .meta file?
		if extension != ".meta":
			# no! we don't like that.
			self.message = "No .meta file!"
			return False
		
		# load .meta file - header
		if not self.loadMeta(filepath):
			return False
		
		# load .rhm file - vertices/triangles
		if not self.loadRhm(pathWithoutExtension + ".rhm"):
			return False
		
		# write gathered information to blender
		if not self.toBlender():
			return False
		
		# if we got here, it can only mean one thing: Success!
		return True
	
	def loadMeta(self, filepath):
		with open(filepath, "r") as file:
			# most common error
			self.message = "Invalid/unsupported file (see console for details)"
			
			while True:
				line = file.readline()
				if line == "":
					break
				if line == "\n": # empty line - might happen?
					continue
				line = line.strip("\n")
				
				if line == "[Geometry]":
					if self.geometry:
						print("Multiple [Geometry] blocks!")
						return False
					self.geometry = Geometry()
					if not self.geometry.loadFromMeta(file):
						print("Error reading [Geometry] block:\n%s" % self.geometry.message)
						return False
					continue
				
				if line == "[Mesh]":
					mesh = Mesh()
					if not mesh.loadFromMeta(file):
						print("Error reading [Mesh] block:\n%s" % (i, mesh.message))
						return False
					self.geometry.meshes.append(mesh)
					continue
				
				if line == "[Chunk]":
					chunk = Chunk()
					if not chunk.loadFromMeta(file):
						print("Error reading [Chunk] block:\n%s" % (i, chunk.message))
						return False
					self.geometry.chunks.append(chunk)
					continue
				
				# warn about unhandled blocks - but only once.
				if line not in unhandledBlocks:
					unhandledBlocks.append(line)
					print("Warning: Unhandled block: %s" % line)
					# skip this
					while peek(file) not in ["[", ""]:
						file.readline()
					continue
			
			# check if the amount of meshes is correct
			if len(self.geometry.meshes) != self.geometry.numMeshes:
				print("Error: Number of [Mesh] blocks does not match Geometry.Meshes! (%d should be %d)" % (len(self.geometry.meshes), self.geometry.numMeshes) )
				return False
			
			return True
		self.message = "Could not open " + filepath
		return False
	
	def loadRhm(self, filepath):
		with open(filepath, "rb") as file:
			if not self.geometry.loadFromRhm(file):
				self.message = "Error reading .rhm file:\n%s" % self.geometry.message
				return False
			
			# file should be over now
			if len(file.read(1)) != 0:
				self.message = "Rhm file longer than expected!"
				return False
			
			return True
		self.message = "Could not open " + filepath
		return False
	
	def toBlender(self):
		# Before adding any meshes or armatures go into Object mode.
		if bpy.ops.object.mode_set.poll():
			bpy.ops.object.mode_set(mode='OBJECT')
		if not self.geometry.toBlender():
			self.message = self.geometry.message
			return False
		return True

from bpy.props import StringProperty, BoolProperty

#  Operator - automatically registered on creation.
class IMPORT_HR_META(bpy.types.Operator):
		'''Import Hard Reset Meta Model Operator.'''
		bl_idname = "import_scene_hardreset.meta"
		bl_label = "Import Hard Reset Model (.meta)"
		bl_description = "Imports a Hard Reset .meta/.rhm pair."
		bl_options = {'REGISTER', 'UNDO'}

		filepath = StringProperty(name="File Path", description="Filepath used for importing the Hard Reset file", maxlen=1024, default="")

		def execute(self, context):
			importer = HRImporter()
			if not importer.importModel(self.filepath):
				self.report({'ERROR'}, importer.message)
			return {'FINISHED'}

		def invoke(self, context, event):
			wm= context.window_manager
			wm.fileselect_add(self)
			return {'RUNNING_MODAL'}

# callback when menu entry is selected
def menu_callback(self, context):
	# calls the operator
	self.layout.operator(IMPORT_HR_META.bl_idname, text="Hard Reset Model (.meta)")

# called when module is registered
def register():
	bpy.utils.register_module(__name__)
	# add menu entry
	bpy.types.INFO_MT_file_import.append(menu_callback)


def unregister():
	bpy.utils.unregister_module(__name__)
	# remove menu entry
	bpy.types.INFO_MT_file_import.remove(menu_callback)

# if this is executed as a file: register it
if __name__ == "__main__":
	register()