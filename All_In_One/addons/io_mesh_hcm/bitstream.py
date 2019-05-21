#==============================================================
"""

Bitstream - Class Interface for working with binary files
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

import struct

class BitStream:

	PI = 3.141592

	def __init__(self, filepath):
		self.offset = 0
		self.bs = open(filepath, 'rb')
		self.bs.seek(0, 2)
		self.length = self.bs.tell()
		self.bs.seek(0, 0)

	def close(self):
		self.bs.close()
		return 1

	def seek_set(self, whence):
		self.bs.seek(whence + self.offset, 0)
		return 1

	def seek_cur(self, whence):
		self.bs.seek(whence, 1)
		return 1

	def seek_end(self, whence):
		self.bs.seek(whence, 2)
		return 1

	def reset(self):
		self.ptr = 0
		return 1

	def setOffset(self):
		self.offset = self.bs.tell()
		return 1

	def tell(self):
		return self.bs.tell()

	def readByte(self):
		bytes = struct.unpack('B', self.bs.read(1))
		return bytes[0]

	def readShort(self):
		bytes = struct.unpack('h', self.bs.read(2))
		return bytes[0]

	def readUShort(self):
		bytes = struct.unpack('H', self.bs.read(2))
		return bytes[0]

	def readInt(self):
		bytes = struct.unpack('i', self.bs.read(4))
		return bytes[0]

	def readUInt(self):
		bytes = struct.unpack('I', self.bs.read(4))
		return bytes[0]

	def readFloat(self):
		bytes = struct.unpack('f', self.bs.read(4))
		return bytes[0]

	def readVec3(self):
		#Read x,y,z vector in floats
		bytes = struct.unpack('fff', self.bs.read(12))
		return list(bytes)

	def readRot3(self):
		#Read angles as integers
		bytes = [self.readInt(),self.readInt(),self.readInt()]

		c = 360 / 0xFFFF
		r = BitStream.PI / 180

		#Convert integer to degrees
		bytes[0] *= c
		bytes[1] *= c
		bytes[2] *= c

		#Convert degrees to radians
		bytes[0] *= r
		bytes[1] *= r
		bytes[2] *= r

		return bytes

	def find(self, bytes):
		origin = self.bs.tell()

		while self.bs.tell() < (self.length - 4):

			uint = self.readUInt()
			if uint == bytes:

				return 1

		self.bs.seek(origin, 0)
		return 0

	def readIFF(self):
		bytes = self.bs.read(4)
		return str(bytes, "ASCII")

	def readStr(self, length = 0):
		string = ""

		if length == 0:

			while True:
				ch = self.readByte()
				if ch == 0:
					break
				string += chr(ch)

		else:

			string = self.bs.read(length)
			string = string.decode("ASCII").rstrip('\0')

		return string

	def readNode(self):
		node = {}
		node['flags'] = self.readUInt()
		node['model'] = self.readUInt()
		node['rot'] = self.readRot3()
		node['scl'] = self.readVec3()
		node['pos'] = self.readVec3()
		node['child'] = self.readUInt()
		node['sibling'] = self.readUInt()
		return node

	def readModel(self):
		model = {}
		model['flag'] = self.readUInt()
		model['vertex'] = self.readUInt()
		model['nbVertex'] = self.readUInt()
		model['polygon'] = self.readUInt()
		model['center'] = self.readVec3()
		model['radius'] = self.readFloat()
		return model

	def readColor(self):
		bytes = struct.unpack('BBBB', self.bs.read(4))
		bytes = [bytes[2]/255, bytes[1]/255, bytes[0]/255, bytes[3]/255]
		return bytes

	def read_specular(self):
		bytes = struct.unpack('BBBB', self.bs.read(4))
		bytes = [bytes[2], bytes[0], bytes[1], bytes[3]]
		return bytes

#==============================================================
"""
Program End
"""
#==============================================================
