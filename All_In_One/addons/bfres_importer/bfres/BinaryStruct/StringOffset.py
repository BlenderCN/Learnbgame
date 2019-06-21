import logging; log = logging.getLogger(__name__)
from .Offset import Offset
from .BinaryObject import BinaryObject
from bfres.BinaryFile import BinaryFile
import struct


class StringOffset(Offset):
    """An offset of a string in a binary file."""

    def __init__(self, name, fmt='I', maxlen=None, encoding=None,
    lenprefix=None):
        """Create StringOffset.

        name:      Field name.
        fmt:       Offset format. If None, this struct represents a
            string; otherwise, it represents the offset of a string.
        maxlen:    Maximum string length.
        encoding:  String encoding.
        lenprefix: Format of length field ahead of string.
            None for null-terminated string.
        """
        # XXX fmt=None doesn't work
        super().__init__(name, fmt)
        self.maxlen    = maxlen
        self.encoding  = encoding
        self.lenprefix = lenprefix

        if lenprefix is None: self.lensize = None
        else: self.lensize = struct.calcsize(lenprefix)


    def DisplayFormat(self, val):
        """Format value for display."""
        return '"%s"' % str(val)


    def readFromFile(self, file:BinaryFile, offset=None):
        """Read this object from a file."""
        if self.fmt is not None:
            # get the offset
            offset = super().readFromFile(file, offset)

        # get the string
        if offset is not None: file.seek(offset)
        if self.lenprefix is not None:
            s = self._readWithLengthPrefix(file)
        else:
            s = self._readNullTerminated(file)

        # decode the string
        try:
            if self.encoding is not None: s = s.decode(self.encoding)
        except UnicodeDecodeError:
            log.error("Can't decode string from 0x%X as '%s': %s",
                offset, self.encoding, s[0:15])
            raise

        return s


    def _readWithLengthPrefix(self, file:BinaryFile) -> (str,bytes):
        """Read length-prefixed string from file."""
        length = struct.unpack_from(self.lenprefix,
            file.read(self.lensize))[0]
        return file.read(length)


    def _readNullTerminated(self, file:BinaryFile) -> (str,bytes):
        """Read null-terminated string from file."""
        # XXX faster method?
        s = []
        while self.maxlen == None or len(s) < self.maxlen:
            b = file.read(1)
            if b == b'\0': break
            else: s.append(b)
        return b''.join(s)
