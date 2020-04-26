import logging; log = logging.getLogger(__name__)
from bfres.BinaryStruct import BinaryStruct, BinaryObject
from bfres.BinaryStruct.Padding import Padding
from bfres.BinaryStruct.StringOffset import StringOffset
from bfres.BinaryStruct.Switch import Offset32, Offset64, String
from bfres.BinaryFile import BinaryFile
from .FresObject import FresObject
import tempfile


class Header(BinaryStruct):
    """Embedded file header."""
    fields = (
        Offset64('data_offset'),
        ('I',    'size'),
        Padding(4),
    )
    size = 0x10


class EmbeddedFile(FresObject):
    """A file embedded in an FRES."""

    def __init__(self, fres, name=None):
        self.fres         = fres
        self.name         = name
        self.headerOffset = None
        self.header       = None
        self.dataOffset   = None
        self.data         = None
        self.size         = None
        self._tempFile    = None
        self._tempBinFile = None


    def __str__(self):
        return "<EmbeddedFile('%s':%s @ %s) at 0x%x>" %(
            str(self.name),
            '?' if self.size is None else hex(self.size),
            '?' if self.dataOffset is None else hex(self.dataOffset),
            id(self),
        )


    def readFromFRES(self, offset=None):
        """Read this object from FRES."""
        if offset is None: offset = self.fres.file.tell()
        self.headerOffset = offset
        self.header = self.fres.read(Header(), offset)
        self.dataOffset = self.header['data_offset']
        self.size = self.header['size']
        self.data = self.fres.read(self.size, self.dataOffset)

        return self


    def toTempFile(self) -> BinaryFile:
        """Dump to a temporary file."""
        if self._tempFile is None:
            self._tempFile = tempfile.TemporaryFile()
            self._tempFile.write(self.data)
            self._tempBinFile = BinaryFile(self._tempFile, 'w+b')
        return self._tempBinFile
