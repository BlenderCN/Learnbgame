import logging; log = logging.getLogger(__name__)
from .BinaryObject import BinaryObject
import struct

SIZEOF_FLOAT  = 4
SIZEOF_DOUBLE = 8


class Vector(BinaryObject):
    """A mathematical vector."""
    def __init__(self, name):
        self.name = name
        self.size = struct.calcsize(self.fmt) * self.count


    def readFromFile(self, file, offset=None):
        return file.read(self.fmt, offset, count=self.count)


class Vec3f(Vector):
    count = 3
    fmt   = 'f'

class Vec4f(Vector):
    count = 4
    fmt   = 'f'
