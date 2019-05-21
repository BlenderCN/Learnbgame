import logging; log = logging.getLogger(__name__)
from .BinaryObject import BinaryObject
import struct


class Flags(BinaryObject):
    """A set of bitflags."""
    def __init__(self, name, flags, fmt='I'):
        self.name   = name
        self._flags = flags
        self.fmt    = fmt
        self.size   = struct.calcsize(fmt)


    def readFromFile(self, file, offset=None):
        val = file.read(self.fmt, offset)
        res = {'_raw':val}
        for name, mask in self._flags.items():
            res[name] = (val & mask) == mask
        return res
