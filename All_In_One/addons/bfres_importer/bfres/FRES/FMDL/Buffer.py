import logging; log = logging.getLogger(__name__)
from bfres.BinaryStruct import BinaryStruct, BinaryObject
from bfres.BinaryStruct.Padding import Padding
from bfres.BinaryStruct.StringOffset import StringOffset
from bfres.BinaryStruct.Switch import Offset32, Offset64, String
from bfres.BinaryFile import BinaryFile
from bfres.Exceptions import MalformedFileError


class Buffer:
    """A buffer of data that can be read in various formats."""

    def __init__(self, file, size, stride, offset):
        self.file   = file
        self.size   = size
        self.stride = stride
        self.offset = offset
        log.debug("Reading buffer (size 0x%X stride 0x%X) from 0x%X",
            size, stride, offset)
        self.data   = file.read(size, offset)
        if len(self.data) < size:
            log.error("Buffer size is 0x%X but only read 0x%X",
                size, len(self.data))
            raise MalformedFileError("Buffer data out of bounds")

        fmts = {
              'int8': 'b',
             'uint8': 'B',
             'int16': 'h',
            'uint16': 'H',
            ' int32': 'i',
            'uint32': 'I',
            ' int64': 'q',
            'uint64': 'Q',
            #'half':   'e',
            'float':  'f',
            'double': 'd',
            'char':   'c',
        }
        for name, fmt in fmts.items():
            try:
                view = memoryview(self.data).cast(fmt)
                setattr(self, name, view)
            except TypeError:
                # this just means we can't interpret the buffer as
                # eg int64 because its size isn't a multiple of
                # that type's size.
                pass


    def dump(self):
        """Dump to string for debug."""
        data = []
        try:
            for i in range(4):
                for j in range(4):
                    b = self.data[(i*4)+j]
                    data.append('%02X ' % b)
                data.append(' ')
        except IndexError:
            pass

        return ("%06X│%04X│%04X│%s" % (
            self.offset, self.size, self.stride, ''.join(data)))
