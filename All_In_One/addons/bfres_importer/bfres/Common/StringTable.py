import logging; log = logging.getLogger(__name__)
from bfres.BinaryStruct import BinaryStruct, BinaryObject
from bfres.BinaryStruct.Padding import Padding
from bfres.BinaryStruct.StringOffset import StringOffset
from bfres.BinaryStruct.Switch import Offset32, Offset64, String
from bfres.BinaryFile import BinaryFile


class Header(BinaryStruct):
    """String Table header."""
    magic  = b'_STR'
    fields = (
        ('4s', 'magic'),    Padding(4),
        ('I',  'size'),     Padding(4),
        ('I',  'num_strs'),
    )
    size = 0x14


class StringTable:
    """A string table in an FRES."""
    Header = Header

    def __init__(self):
        self.strings = {}


    def readFromFile(self, file, offset=None):
        """Read this object from the given file."""

        #log.debug("Read str table from 0x%X", offset)
        header = self.Header()
        self.header = header.readFromFile(file, offset)
        offset += header.size

        for i in range(self.header['num_strs']):
            offset += (offset & 1) # pad to u16
            length = file.read('<H',   offset)
            data   = file.read(length, offset+2)
            try:
                data = data.decode('shift-jis')
            except UnicodeDecodeError:
                log.error("Can't decode string from 0x%X as 'shift-jis': %s",
                    offset, data[0:16])
                raise
            self.strings[offset] = data
            #print('StrTab[%06X]: "%s"' % (offset, data))
            offset += length + 3 # +2 for length, 1 for null terminator

        return self
