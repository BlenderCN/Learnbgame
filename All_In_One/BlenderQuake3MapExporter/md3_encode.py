__author__ = ["Mr. Wonko","Xembie","PhaethonH","Bob Holcomb","Damien McGinnes","Robert (Tr3B) Beckebans"]
__url__ = ["http://xreal.sourceforge.net","http://www.katsbits.com"]
import math,struct
MAX_QPATH = 64

MD3_IDENT = "IDP3"
MD3_VERSION = 15
MD3_MAX_TAGS = 16
MD3_MAX_SURFACES = 32
MD3_MAX_FRAMES = 1024
MD3_MAX_SHADERS = 256
MD3_MAX_VERTICES = 4096
MD3_MAX_TRIANGLES = 8192
MD3_XYZ_SCALE = 64.0

class md3Vert:
	xyz = []
	normal = 0
	binaryFormat = "<3hH"
	
	def __init__(self):
		self.xyz = [0.0, 0.0, 0.0]
		self.normal = 0
		
	def GetSize(self):
		return struct.calcsize(self.binaryFormat)
	
	# copied from PhaethonH <phaethon@linux.ucla.edu> md3.py
	def Decode(self, latlng):
		lat = (latlng >> 8) & 0xFF;
		lng = (latlng) & 0xFF;
		lat *= math.pi / 128;
		lng *= math.pi / 128;
		x = math.cos(lat) * math.sin(lng)
		y = math.sin(lat) * math.sin(lng)
		z =                 math.cos(lng)
		retval = [ x, y, z ]
		return retval
	
	# copied from PhaethonH <phaethon@linux.ucla.edu> md3.py
	def Encode(self, normal):
		x = normal[0]
		y = normal[1]
		z = normal[2]
		# normalize
		l = math.sqrt((x*x) + (y*y) + (z*z))
		if l == 0:
			return 0
		x = x/l
		y = y/l
		z = z/l
		
		if (x == 0.0) & (y == 0.0) :
			if z > 0.0:
				return 0
			else:
				return (128 << 8)
		
		lng = math.acos(z) * 255 / (2 * math.pi)
		lat = math.atan2(y, x) * 255 / (2 * math.pi)
		retval = ((int(lat) & 0xFF) << 8) | (int(lng) & 0xFF)
		return retval
		
	def Save(self, file):
		tmpData = [0] * 4
		tmpData[0] = int(self.xyz[0] * MD3_XYZ_SCALE)
		tmpData[1] = int(self.xyz[1] * MD3_XYZ_SCALE)
		tmpData[2] = int(self.xyz[2] * MD3_XYZ_SCALE)
		tmpData[3] = self.normal
		data = struct.pack(self.binaryFormat, tmpData[0], tmpData[1], tmpData[2], tmpData[3])
		file.write(data)
		
class md3TexCoord:
	u = 0.0
	v = 0.0

	binaryFormat = "<2f"

	def __init__(self):
		self.u = 0.0
		self.v = 0.0
		
	def GetSize(self):
		return struct.calcsize(self.binaryFormat)

	def Save(self, file):
		tmpData = [0] * 2
		tmpData[0] = self.u
		tmpData[1] = 1.0 - self.v
		data = struct.pack(self.binaryFormat, tmpData[0], tmpData[1])
		file.write(data)

class md3Triangle:
	indexes = []

	binaryFormat = "<3i"

	def __init__(self):
		self.indexes = [ 0, 0, 0 ]
		
	def GetSize(self):
		return struct.calcsize(self.binaryFormat)

	def Save(self, file):
		tmpData = [0] * 3
		tmpData[0] = self.indexes[0]
		tmpData[1] = self.indexes[2] # reverse
		tmpData[2] = self.indexes[1] # reverse
		data = struct.pack(self.binaryFormat,tmpData[0], tmpData[1], tmpData[2])
		file.write(data)

class md3Shader:
	name = ""
	index = 0
	
	binaryFormat = "<%dsi" % MAX_QPATH

	def __init__(self):
		self.name = ""
		self.index = 0
		
	def GetSize(self):
		return struct.calcsize(self.binaryFormat)

	def Save(self, file):
		tmpData = [0] * 2
		tmpData[0] = self.name
		tmpData[1] = self.index
		data = struct.pack(self.binaryFormat, tmpData[0].encode('utf-8'), tmpData[1])
		file.write(data)

class md3Surface:
	ident = ""
	name = ""
	flags = 0
	numFrames = 0
	numShaders = 0
	numVerts = 0
	numTriangles = 0
	ofsTriangles = 0
	ofsShaders = 0
	ofsUV = 0
	ofsVerts = 0
	ofsEnd = 0
	shaders = []
	triangles = []
	uv = []
	verts = []
	
	binaryFormat = "<4s%ds10i" % MAX_QPATH  # 1 int, name, then 10 ints
	
	def __init__(self):
		self.ident = ""
		self.name = ""
		self.flags = 0
		self.numFrames = 0
		self.numShaders = 0
		self.numVerts = 0
		self.numTriangles = 0
		self.ofsTriangles = 0
		self.ofsShaders = 0
		self.ofsUV = 0
		self.ofsVerts = 0
		self.ofsEnd
		self.shaders = []
		self.triangles = []
		self.uv = []
		self.verts = []
		
	def GetSize(self):
		sz = struct.calcsize(self.binaryFormat)
		self.ofsShaders = sz
		for s in self.shaders:
			sz += s.GetSize()
		self.ofsTriangles = sz
		for t in self.triangles:
			sz += t.GetSize()
		self.ofsUV = sz
		for u in self.uv:
			sz += u.GetSize()
		self.ofsVerts = sz
		for v in self.verts:
			sz += v.GetSize()
		self.ofsEnd = sz
		return self.ofsEnd
	
	def Save(self, file):
		self.GetSize()
		tmpData = [0] * 12
		tmpData[0] = self.ident
		tmpData[1] = self.name
		tmpData[2] = self.flags
		tmpData[3] = self.numFrames
		tmpData[4] = self.numShaders
		tmpData[5] = self.numVerts
		tmpData[6] = self.numTriangles
		tmpData[7] = self.ofsTriangles
		tmpData[8] = self.ofsShaders
		tmpData[9] = self.ofsUV
		tmpData[10] = self.ofsVerts
		tmpData[11] = self.ofsEnd
		data = struct.pack(self.binaryFormat, tmpData[0].encode('utf-8'),tmpData[1].encode('utf-8'),tmpData[2],tmpData[3],tmpData[4],tmpData[5],tmpData[6],tmpData[7],tmpData[8],tmpData[9],tmpData[10],tmpData[11])
		file.write(data)

		# save the shader coordinates
		for s in self.shaders:
			s.Save(file)

		# write the tri data
		for t in self.triangles:
			t.Save(file)

		# save the uv info
		for u in self.uv:
			u.Save(file)

		# save the verts
		for v in self.verts:
			v.Save(file)

class md3Tag:
	name = ""
	origin = []
	axis = []
	
	binaryFormat="<%ds3f9f" % MAX_QPATH
	
	def __init__(self):
		self.name = ""
		self.origin = [0, 0, 0]
		self.axis = [0, 0, 0, 0, 0, 0, 0, 0, 0]
		
	def GetSize(self):
		return struct.calcsize(self.binaryFormat)
		
	def Save(self, file):
		tmpData = [0] * 13
		tmpData[0] = self.name
		tmpData[1] = float(self.origin[0])
		tmpData[2] = float(self.origin[1])
		tmpData[3] = float(self.origin[2])
		tmpData[4] = float(self.axis[0])
		tmpData[5] = float(self.axis[1])
		tmpData[6] = float(self.axis[2])
		tmpData[7] = float(self.axis[3])
		tmpData[8] = float(self.axis[4])
		tmpData[9] = float(self.axis[5])
		tmpData[10] = float(self.axis[6])
		tmpData[11] = float(self.axis[7])
		tmpData[12] = float(self.axis[8])
		data = struct.pack(self.binaryFormat, tmpData[0].encode('utf-8'),tmpData[1],tmpData[2],tmpData[3],tmpData[4],tmpData[5],tmpData[6], tmpData[7], tmpData[8], tmpData[9], tmpData[10], tmpData[11], tmpData[12])
		file.write(data)
	
class md3Frame:
	mins = 0
	maxs = 0
	localOrigin = 0
	radius = 0.0
	name = ""
	
	binaryFormat="<3f3f3ff16s"
	
	def __init__(self):
		self.mins = [32767, 32767, 32767]
		self.maxs = [-32768, -32768, -32768]
		self.localOrigin = [0, 0, 0]
		self.radius = 0.0
		self.name = ""
		
	def GetSize(self):
		return struct.calcsize(self.binaryFormat)

	def Save(self, file):
		tmpData = [0] * 11
		tmpData[0] = self.mins[0]
		tmpData[1] = self.mins[1]
		tmpData[2] = self.mins[2]
		tmpData[3] = self.maxs[0]
		tmpData[4] = self.maxs[1]
		tmpData[5] = self.maxs[2]
		tmpData[6] = self.localOrigin[0]
		tmpData[7] = self.localOrigin[1]
		tmpData[8] = self.localOrigin[2]
		tmpData[9] = self.radius
		tmpData[10] = self.name
		data = struct.pack(self.binaryFormat, tmpData[0],tmpData[1],tmpData[2],tmpData[3],tmpData[4],tmpData[5],tmpData[6],tmpData[7], tmpData[8], tmpData[9], tmpData[10].encode('utf-8'))
		file.write(data)

class md3Object:
	# header structure
	ident = ""			# this is used to identify the file (must be IDP3)
	version = 0			# the version number of the file (Must be 15)
	name = ""
	flags = 0
	numFrames = 0
	numTags = 0
	numSurfaces = 0
	numSkins = 0
	ofsFrames = 0
	ofsTags = 0
	ofsSurfaces = 0
	ofsEnd = 0
	frames = []
	tags = []
	surfaces = []

	binaryFormat="<4si%ds9i" % MAX_QPATH  # little-endian (<), 4 bytes, 1 ints, 64 bytes, 9 ints

	def __init__(self):
		self.ident = 0
		self.version = 0
		self.name = ""
		self.flags = 0
		self.numFrames = 0
		self.numTags = 0
		self.numSurfaces = 0
		self.numSkins = 0
		self.ofsFrames = 0
		self.ofsTags = 0
		self.ofsSurfaces = 0
		self.ofsEnd = 0
		self.frames = []
		self.tags = []
		self.surfaces = []

	def GetSize(self):
        # frames start after header
		self.ofsFrames = struct.calcsize(self.binaryFormat)
        # tags start after frames
		self.ofsTags = self.ofsFrames
		for f in self.frames:
			self.ofsTags += f.GetSize()
        # surfaces start after tags
		self.ofsSurfaces = self.ofsTags
		for t in self.tags:
			self.ofsSurfaces += t.GetSize()
        # end starts after surfaces
		self.ofsEnd = self.ofsSurfaces
		for s in self.surfaces:
			self.ofsEnd += s.GetSize()
		return self.ofsEnd
		
	def Save(self, file):
		self.GetSize()
		tmpData = [0] * 12
		tmpData[0] = self.ident # 4 bytes
		tmpData[1] = self.version # 1 int
		tmpData[2] = self.name # 64 bytes
		tmpData[3] = self.flags # 9 ints
		tmpData[4] = self.numFrames
		tmpData[5] = self.numTags
		tmpData[6] = self.numSurfaces
        # always 0
		tmpData[7] = self.numSkins
        # calculated in self.GetSize()
		tmpData[8] = self.ofsFrames
		tmpData[9] = self.ofsTags
		tmpData[10] = self.ofsSurfaces
		tmpData[11] = self.ofsEnd

		data = struct.pack(self.binaryFormat, tmpData[0].encode('utf-8'),tmpData[1],tmpData[2].encode('utf-8'),tmpData[3],tmpData[4],tmpData[5],tmpData[6],tmpData[7], tmpData[8], tmpData[9], tmpData[10], tmpData[11])
		file.write(data)

		for f in self.frames:
			f.Save(file)
			
		for t in self.tags:
			t.Save(file)
			
		for s in self.surfaces:
			s.Save(file)
