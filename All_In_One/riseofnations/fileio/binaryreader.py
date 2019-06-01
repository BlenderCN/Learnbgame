import struct


class BinaryReader:
    def __init__(self, binaryfile, byteorder='<'):
        """
        Wrapper around type file to read binary files
        :param binaryfile: input of type file with binary read arguments
        :param byteorder: use '<' for little-endian, and '>' for big-endian
        """
        self.file = binaryfile
        self.byteorder = byteorder

    def read_char(self):
        data = struct.unpack('c', self.file.read(1))[0]
        return data

    def read_byte(self):
        data = struct.unpack('b', self.file.read(1))[0]
        return data

    def read_ubyte(self):
        data = struct.unpack('B', self.file.read(1))[0]
        return data

    def read_bool(self):
        data = struct.unpack('?', self.file.read(1))[0]
        return data

    def read_int16(self):
        data = struct.unpack(self.byteorder + 'h', self.file.read(2))[0]
        return data

    def read_uint16(self):
        data = struct.unpack(self.byteorder + 'H', self.file.read(2))[0]
        return data

    def read_int32(self):
        data = struct.unpack(self.byteorder + 'l', self.file.read(4))[0]
        return data

    def read_uint32(self):
        data = struct.unpack(self.byteorder + 'L', self.file.read(4))[0]
        return data

    def read_int64(self):
        data = struct.unpack(self.byteorder + 'q', self.file.read(8))[0]
        return data

    def read_uint64(self):
        data = struct.unpack(self.byteorder + 'Q', self.file.read(8))[0]
        return data

    def read_float(self):
        data = struct.unpack(self.byteorder + 'f', self.file.read(4))[0]
        return data

    def read_double(self):
        data = struct.unpack(self.byteorder + 'd', self.file.read(8))[0]
        return data

    # def read_string(self):
    #     str = bytearray()
    #     byte = self.file.read(1)
    #     while byte:
    #         str += byte
    #         byte = self.file.read(1)
    #     return str.decode('utf-8', 'strict')

    def read_string(self, bytecount, encoding='utf-8', errors='strict'):
        data = self.file.read(bytecount).decode(encoding, errors)
        return data
