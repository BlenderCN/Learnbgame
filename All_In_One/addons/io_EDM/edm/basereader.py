"""
BaseReader

A very simple extended stream reader, with capability to read single or 
arrays of standard types.

It additionally has functions to read a uint-prefixed string, and a 
uint-prefixed list of some item, defined by the function passed in
"""

import struct
from collections import namedtuple

from .mathtypes import Vector, Matrix, Quaternion, sequence_to_matrix

import logging
logger = logging.getLogger(__name__)

class BaseReader(object):
  def __init__(self, filename):
    self.filename = filename
    self.stream = open(filename, "rb")
    self.version = None

  def tell(self):
    return self.stream.tell()

  def seek(self, offset, from_what=0):
    self.stream.seek(offset, from_what)

  def close(self):
    self.stream.close()

  @property
  def v8(self):
    return self.version == 8
  @property
  def v10(self):
    return self.version == 10

  def read_constant(self, data):
    filedata = self.stream.read(len(data))
    if not data == filedata:
      raise IOError("Expected constant not encountered; {} != {}".format(filedata, data))

  def read(self, length):
    return self.stream.read(length)
    
  def read_uchar(self):
    return struct.unpack("B", self.stream.read(1))[0]

  def read_uchars(self, count):
    return struct.unpack("{}B".format(count), self.stream.read(1*count))

  def read_ushort(self):
    return struct.unpack("<H", self.stream.read(2))[0]

  def read_ushorts(self, count):
    return struct.unpack("<{}H".format(count), self.stream.read(2*count))

  def read_uint(self):
    """Read an unsigned integer from the data"""
    return struct.unpack("<I", self.stream.read(4))[0]

  def read_uints(self, count):
    """Read an unsigned integer from the data"""
    return struct.unpack("<{}I".format(count), self.stream.read(4*count))

  def read_int(self):
    """Read a signed integer from the data"""
    return struct.unpack("<i", self.stream.read(4))[0]
  
  def read_ints(self, count):
    """Read a signed integer from the data"""
    return struct.unpack("<{}i".format(count), self.stream.read(4*count))

  def read_float(self):
    return struct.unpack("<f", self.stream.read(4))[0]

  def read_floats(self, count):
    return struct.unpack("<{}f".format(count), self.stream.read(4*count))
  
  def read_double(self):
    return struct.unpack("<d", self.stream.read(8))[0]  

  def read_doubles(self, count):
    return struct.unpack("<{}d".format(count), self.stream.read(8*count))

  def read_format(self, format):
    """Read a struct format from the data"""
    return struct.unpack(format, self.stream.read(struct.calcsize(format)))

  def read_string(self, lookup=True):
    """Read a length-prefixed string from the file.
    lookup: If v10, string will be read as lookup. Has no effect on v8"""

    prepos = self.stream.tell()
    if self.v10 and lookup:
      index = self.read_uint()
      assert index < len(self.strings), "Got index higher than lookup count; {} at {}".format(index, prepos)
      return self.strings[index]
    else:
      length = self.read_uint()
      assert length < 200, "Overly long string length found; {} at {}".format(length, prepos)
      try:
        data = self.stream.read(length)
        # return data.decode("UTF-8")
        return data.decode("windows-1251")
      except UnicodeDecodeError:
        print("Bad data:100 : " + repr(data[:100]))
        raise RuntimeError("Could not decode string with length {} at position {}".format(length, prepos))

  def read_list(self, reader):
    """Reads a length-prefixed list of something"""
    length = self.read_uint()
    entries = []
    for index in range(length):
      entries.append(reader(self))
    return entries

  def read_vec2f(self):
    return Vector(self.read_format("<ff"))

  def read_vec3f(self):
    return Vector(self.read_format("<fff"))

  def read_vec3d(self):
    return Vector(self.read_format("<ddd"))

  def read_matrixf(self):
    md = self.read_floats(16)
    return sequence_to_matrix(md)

  def read_matrixd(self):
    md = self.read_doubles(16)
    return sequence_to_matrix(md)

  def read_quaternion(self):
    qd = self.read_doubles(4)
    # Reorder as osg saves xyzw and we want wxyz
    return Quaternion([qd[3], qd[0], qd[1], qd[2]])

