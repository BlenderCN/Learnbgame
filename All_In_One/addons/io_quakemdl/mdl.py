# CSC 472 Term Project
# MDL Format

class MDL:
	class Vec3:
		"""A simple Vector 3 class. Holds 3 floats."""
		def __init__(self, x, y, z):
			self.x = x
			self.y = y
			self.z = z

	class Vertex:
		"""Model vertex. Contains position and Quake normal index."""
		def __init__(self, x, y, z, normalIndex):
			self.x = x
			self.y = y
			self.z = z
			self.normalIndex = normalIndex

	class Triangle:
		"""Model triangle. Contains indexes to 3 Vertices and front facing value."""
		def __init__(self, a, b, c, frontFacing):
			self.a = a
			self.b = b
			self.c = c
			self.frontFacing = frontFacing

	class Texture:
		"""Texture holder. A texture is a 8-bit color index array."""
		def __init__(self):
			self.pixels = None

		def __init__(self, pixels):
			self.pixels = pixels

	class Skin:
		"""Model skin. May be a single frame or animated."""
		def __init__(self):
			self.frameData = []
			self.frameTimes = []

		def __init__(self, frameData, frameTimes):
			self.frameData = frameData
			self.frameTimes = frameTimes

		def group(self):
			if (len(self.frameData) < 2):
				return False
			else:
				return True

	class TextureCoords:
		def __init__(self, onseam, s, t):
			self.onseam = onseam
			self.s = s
			self.t = t

	class SimpleFrame:
		def __init__(self):
			self.box_min = None #this should be a Vertex()
			self.box_max = None 
			self.name = ""
			self.vertices = []

	class Frames:
		"""A set of frames for animation purposes"""
		def __init__(self, frames, timesForFrames):
			self.frames = frames
			self.timesForFrames = timesForFrames
			self.min = frames[0].box_min
			self.max = frames[0].box_max
			for fr in frames:
				self.min.x = min(self.min.x, fr.box_min.x)
				self.min.y = min(self.min.y, fr.box_min.y)
				self.min.z = min(self.min.x, fr.box_min.z)
			for fr in frames:
				self.max.x = max(self.min.x, fr.box_max.x)
				self.max.y = max(self.min.y, fr.box_max.y)
				self.max.z = max(self.min.x, fr.box_max.z)

		def group(self):
			if (len(self.frames) < 2):
				return False
			else:
				return True


	def __init__(self):
		self.versionNumber = 6
		self.scale = self.Vec3(1, 1, 1)
		self.translation = self.Vec3(0.0, 0.0, 0.0)
		self.boundingRadius = 1.0
		self.eyePositon = self.Vec3(0.0, 0.0, 0.0)
		self.skins = []
		self.skinWidth = 0
		self.skinHeight = 0;
		self.triangles = []
		self.frames = []
		self.texCoords = []
		self.images = []



