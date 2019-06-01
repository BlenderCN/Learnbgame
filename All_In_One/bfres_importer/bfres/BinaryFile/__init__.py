import logging; log = logging.getLogger(__name__)
import struct
from bfres.BinaryStruct import BinaryStruct, BinaryObject

class BinaryFile:
    """Wrapper around files that provides binary I/O methods."""

    _seekNames = {
        'start': 0,
        'cur':   1,
        'end':   2,
    }

    _endianFmts = {
        'big':    '>',
        'little': '<',
    }

    def __init__(self, file, mode='rb', endian='little'):
        if type(file) is str: file = open(file, mode)
        self.file   = file
        self.name   = file.name
        self.endian = endian

        # get size
        pos = file.tell()
        self.size = self.seek(0, 'end')
        file.seek(pos)


    @staticmethod
    def open(path, mode='rb'):
        file = open(path, mode)
        return FileReader(file)


    @property
    def endianFmt(self):
        return self._endianFmts[self.endian]


    def seek(self, pos:int, whence:(int,str)=0) -> int:
        """Seek within the file.

        pos: Position to seek to.
        whence: Where to seek from:
            0 or 'start': Beginning of file.
            1 or 'cur':   Current position.
            2 or 'end':   Backward from end of file.

        Returns new position.
        """
        whence = self._seekNames.get(whence, whence)
        try:
            return self.file.seek(pos, whence)
        except:
            log.error("Error seeking to 0x%X from %s",
                pos, str(whence))
            raise


    def read(self, fmt:(int,str,BinaryStruct,BinaryObject)=-1,
    pos:int=None, count:int=1):
        """Read from the file.

        fmt:   Number of bytes to read, or a `struct` format string,
               or a BinaryStruct or BinaryObject,
               or a class which is a subclass of one of those two.
        pos:   Position to seek to first. (optional)
        count: Number of items to read. If not 1, returns a list.

        Returns the data read.
        """
        if pos is not None: self.seek(pos)
        pos = self.tell()
        if   count <  0: raise ValueError("Count cannot be negative")
        elif count == 0: return []

        res = []
        #log.debug("BinaryFile read fmt: %s, offset: %s", fmt, pos)

        try:
            if issubclass(fmt, BinaryObject):
                fmt = fmt("<anonymous@0x%X>" % pos)
            elif issubclass(fmt, BinaryStruct):
                fmt = fmt()
        except TypeError:
            pass # fmt is not a class

        if type(fmt) is str: # struct format string
            size = struct.calcsize(fmt)
            for i in range(count):
                offs = self.file.tell()
                try:
                    r = struct.unpack(fmt, self.file.read(size))
                except struct.error as ex:
                    log.error("Failed to unpack format '%s' from offset 0x%X (max 0x%X): %s",
                        fmt, offs, self.size, ex)
                    raise
                if len(r) == 1: r = r[0] # grumble
                res.append(r)

        elif isinstance(fmt, (BinaryStruct, BinaryObject)):
            size = getattr(fmt, 'size', 0)
            if count > 1 and not size:
                raise ValueError("Cannot read type '%s' with count >1 (class does not define a size)" %
                    type(fmt).__name__)

            for i in range(count):
                r = fmt.readFromFile(self, pos)
                res.append(r)
                if size: pos += size

        else: # size in bytes
            for i in range(count):
                res.append(self.file.read(fmt))

        if count == 1: return res[0] # grumble
        return res


    def tell(self) -> int:
        """Get current read position."""
        return self.file.tell()


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()


    def __str__(self):
        return "<BinaryFile(%s) at 0x%x>" % (self.name, id(self))
