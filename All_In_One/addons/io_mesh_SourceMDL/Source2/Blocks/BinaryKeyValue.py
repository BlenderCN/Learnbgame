from enum import IntEnum

try:
    from MDLIO_ByteIO import ByteIO
    from Source2.Blocks.Dummy import Dummy
    from Source2.Blocks.Header import InfoBlock
except:
    from ...MDLIO_ByteIO import ByteIO
    from .Dummy import Dummy
    from .Header import InfoBlock


class KVFlag(IntEnum):
    Nothing = 0
    Resource = 1
    DeferredResource = 2


class KVType(IntEnum):
    STRING_MULTI = 0  # STRING_MULTI doesn't have an ID
    NULL = 1
    BOOLEAN = 2
    INTEGER = 3
    FLAGGED_STRING = 4
    DOUBLE = 5
    STRING = 6
    ARRAY = 8
    OBJECT = 9


class BinaryKeyValue(Dummy):
    ENCODING = (0x46, 0x1A, 0x79, 0x95, 0xBC, 0x95, 0x6C, 0x4F, 0xA7, 0x0B, 0x05, 0xBC, 0xA1, 0xB7, 0xDF, 0xD2)
    FORMAT = (0x7C, 0x16, 0x12, 0x74, 0xE9, 0x06, 0x98, 0x46, 0xAF, 0xF2, 0xE6, 0x3E, 0xB5, 0x90, 0x37, 0xE7)
    SIG = (0x56, 0x4B, 0x56, 0x03)

    def __init__(self, block_info: InfoBlock = None):
        self.strings = []
        self.info_block = block_info
        self.kv = []
        self.flags = 0
        self.buffer = ByteIO()  # type: ByteIO

    def read(self, reader: ByteIO):
        fourcc = reader.read_bytes(4)
        assert tuple(fourcc) == self.SIG, 'Invalid KV Signature'
        encoding = reader.read_bytes(16)
        assert tuple(encoding) == self.ENCODING, 'Unrecognized KV3 Encoding'
        format = reader.read_bytes(16)
        assert tuple(format) == self.FORMAT, 'Unrecognised KV3 Format'
        self.flags = reader.read_bytes(4)
        if self.flags[3] & 0x80:
            self.buffer.write_bytes(
                reader.read_bytes(self.info_block.block_size - (reader.tell() - self.info_block.absolute_offset)))
        working = True
        while reader.tell() != reader.size() and working:
            block_mask = reader.read_uint16()
            for i in range(16):
                if block_mask & (1 << i) > 0:
                    offset_and_size = reader.read_uint16()
                    offset = ((offset_and_size & 0xFFF0) >> 4) + 1
                    size = (offset_and_size & 0x000F) + 3
                    lookup_size = offset if offset < size else size
                    entry = self.buffer.tell()
                    self.buffer.seek(entry - offset)
                    data = self.buffer.read_bytes(lookup_size)
                    self.buffer.seek(entry)
                    while size > 0:
                        self.buffer.write_bytes(data[:lookup_size if lookup_size < size else size])
                        size -= lookup_size
                else:
                    data = reader.read_int8()
                    self.buffer.write_int8(data)
                if self.buffer.size() == (self.flags[2] << 16) + (self.flags[1] << 8) + self.flags[0]:
                    working = False
                    break
        self.buffer.seek(0)
        string_count = self.buffer.read_uint32()
        for i in range(string_count):
            self.strings.append(self.buffer.read_ascii_string())
        self.parse(self.buffer, self.kv, True)
        self.buffer.close()
        del self.buffer

    def parse(self, reader: ByteIO, parent=None, in_array=False):
        name = None
        parent = parent

        if not in_array:
            string_id = reader.read_uint32()
            name = "ERROR" if string_id == -1 else self.strings[string_id]
        add = lambda v: parent.update({name: v}) if not in_array else parent.append(v)
        data_type = reader.read_int8()
        flag_info = KVFlag.Nothing
        if data_type & 0x80:
            data_type &= 0x7F
            flag_info = KVFlag(reader.read_int8())

        if data_type == KVType.NULL:
            add(None)
            return
        if data_type == KVType.BOOLEAN:
            add(reader.read_int8() > 0)
            return
        if data_type == KVType.INTEGER:
            add(reader.read_int64())
            return
        if data_type == KVType.DOUBLE:
            add(reader.read_double())
            return
        if data_type == KVType.STRING:
            string_id = reader.read_int32()
            if string_id == -1:
                add(None)
                return
            add(self.strings[string_id])
            return
        if data_type == KVType.ARRAY:
            size = reader.read_uint32()
            arr = []
            for _ in range(size):
                self.parse(reader, arr, True)
            add(arr)
            return
        if data_type == KVType.OBJECT:
            size = reader.read_uint32()
            tmp = {}
            for _ in range(size):
                self.parse(reader, tmp, False)
            add(tmp)
            if not parent:
                parent = tmp
        return parent
