import logging; log = logging.getLogger(__name__)
import struct
#from BinaryFile import BinaryFile

def format(*val):
    val = val[-1] # we may or may not receive `self` argument
    if type(val) is int: return '0x%X' % val
    if type(val) is str: return '"%s"' % val
    return str(val)


class BinaryObject:
    """An object in a binary file."""

    DisplayFormat = format

    def __init__(self, name, fmt):
        self.name = name
        self.fmt  = fmt
        self.size = struct.calcsize(fmt)


    def readFromFile(self, file, offset=None):
        """Read this object from a file."""
        return file.read(self.fmt, pos=offset)
