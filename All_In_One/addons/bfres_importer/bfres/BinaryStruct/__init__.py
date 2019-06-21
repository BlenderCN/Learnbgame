import logging; log = logging.getLogger(__name__)
import struct
#from BinaryFile import BinaryFile
from .BinaryObject import BinaryObject


class BinaryStruct:
    """A set of data represented by a binary structure."""

    magic = None # valid values for `magic` field, if present.

    def __init__(self, *fields, size:int=None):
        """Define structure.

        fields: List of field definitions.
        size: Expected size of structure. Produces a warning message
            if actual size specified by `fields` does not match this.
        """
        # if no fields given, use those defined in the subclass.
        if len(fields) == 0: fields = self.fields

        self.fields = {}
        self.orderedFields = []

        offset = 0
        _checkSize = size
        for field in fields:
            conv = None

            if type(field) is tuple:
                # field = (type, name[, convertor])
                typ, name = field[0:2]
                if len(field) > 2: conv = field[2]
            else: # class
                typ, name = field, field.name

            assert name not in self.fields, \
                "Duplicate field name '" + name + "'"

            # determine size and make reader function
            if type(typ) is str:
                size = struct.calcsize(typ)
                func = self._makeReader(typ)
                disp = BinaryObject.DisplayFormat
            else:
                size = typ.size
                func = typ.readFromFile
                disp = typ.DisplayFormat

            field = {
                'name':   name,
                'size':   size,
                'offset': offset,
                'type':   typ,
                'read':   func,
                'conv':   conv,
                'disp':   disp,
            }
            self.fields[name] = field
            self.orderedFields.append(field)
            offset += size

        self.size = offset
        if _checkSize is not None:
            assert _checkSize == self.size, \
                "Struct size is 0x%X but should be 0x%X" % (
                    self.size, _checkSize)


    def _makeReader(self, typ):
        """Necessary because lolscope"""
        return lambda file: file.read(typ)


    def readFromFile(self, file, offset=None):
        """Read this struct from given file."""
        if offset is not None: file.seek(offset)
        offset = file.tell()

        res = {}
        for field in self.orderedFields:
            try:
                # read the field
                #log.debug("Read %s.%s from 0x%X => 0x%X",
                #    type(self).__name__, field['name'],
                #    field['offset'], offset)
                file.seek(offset)
                func = field['read']
                data = func(file)

                if type(data) is tuple and len(data) == 1:
                    data = data[0] # grumble

                if field['conv']: data = field['conv'](data)
                res[field['name']] = data
                offset += field['size']
            except Exception as ex:
                log.error("Failed reading field '%s' from offset 0x%X: %s",
                    field['name'], offset, ex)

        #log.debug("Read %s: %s", type(self).__name__, res)
        self._checkMagic(res)
        self._checkOffsets(res, file)
        self._checkPadding(res)
        return res


    def _checkMagic(self, res):
        """Verify magic value."""
        if self.magic is None: return

        magic = res.get('magic', None)
        if magic is None:
            raise RuntimeError("Struct %s has `magic` property but no `magic` field" %
                type(self).__name__)

        valid = self.magic
        if type(valid) not in (list, tuple):
            valid = (valid,)

        if magic not in valid:
            raise ValueError("%s: invalid magic %s; expected %s" % (
                type(self).__name__, str(magic), str(valid)))


    def _checkOffsets(self, res, file):
        """Check if offsets are sane."""
        from .Offset import Offset
        for field in self.orderedFields:
            typ  = field['type']
            name = field['name']
            if isinstance(typ, Offset):
                try:
                    val = int(res.get(name, None))
                    if val < 0 or val > file.size:
                        # don't warn on == file.size because some files
                        # have an offset field that's their own size
                        log.warning("%s: Offset '%s' = 0x%X but EOF = 0x%X",
                            type(self).__name__, name, val, file.size+1)
                except (TypeError, ValueError):
                    # string offsets are Offset but not numbers
                    pass


    def _checkPadding(self, res):
        """Check if padding values are as expected."""
        from .Padding import Padding
        for field in self.orderedFields:
            typ  = field['type']
            name = field['name']
            data = res.get(name, None)
            if isinstance(typ, Padding):
                expected = typ.value
                for i, byte in enumerate(data):
                    if byte != expected:
                        log.debug("%s: Padding byte at 0x%X is 0x%02X, should be 0x%02X",
                            type(self).__name__,
                            field['offset']+i, byte, expected
                        )


    def dump(self, data:dict) -> str:
        """Dump to string for debug."""
        strs = []
        longestName = 0
        longestType = 0
        for field in self.orderedFields:
            name  = field['name']
            typ   = field['type']
            if type(typ) is not str: typ = type(typ).__name__
            value = data[name]
            fmt   = field['disp']
            if type(fmt) is str:
                f = fmt
                fmt = lambda v: f % v
            strs.append((field['offset'], typ, name, fmt(value)))
            longestName = max(longestName, len(name))
            longestType = max(longestType, len(typ))

        res = []
        for offs, typ, name, val in strs:
            res.append('  [%04X %s] %s %s' % (
                offs,
                typ.ljust(longestType),
                (name+':').ljust(longestName+1),
                val,
            ))
        return '\n'.join(res)
