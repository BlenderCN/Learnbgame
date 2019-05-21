import logging; log = logging.getLogger(__name__)
from .BinaryObject import BinaryObject
from bfres.BinaryFile import BinaryFile
import struct

class Padding(BinaryObject):
    """A series of bytes that aren't used."""
    def __init__(self, size, value=0):
        super().__init__(
            name = 'padding%d' % id(self),
            fmt  = '%ds' % size)
        self.value = value


    def readFromFile(self, file:BinaryFile, offset=None):
        """Read this object from a file."""
        if offset is None: offset = file.tell()
        data = super().readFromFile(file, offset)
        self.data = data
        #for i, byte in enumerate(data):
        #    if byte != self.value:
        #        print("Padding byte at 0x%X is 0x%02X, should be 0x%02X" % (
        #            offset+i, byte, self.value
        #        ))
        return data
