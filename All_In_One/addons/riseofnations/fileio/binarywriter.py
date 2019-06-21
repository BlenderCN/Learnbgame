import struct


class BinaryWriter:
    def __init__(self, binaryfile, byteorder='<'):
        """
        Wrapper around type file to write binary files
        :param binaryfile: input of type file with binary write arguments
        :param byteorder: use '<' for little-endian, and '>' for big-endian
        """
        self.file = binaryfile
        self.byteorder = byteorder

    def write_char(self, data):
        self.file.write(struct.pack('c', data))

    def write_byte(self, data):
        self.file.write(struct.pack('b', data))

    def write_ubyte(self, data):
        self.file.write(struct.pack('B', data))

    def write_bool(self, data):
        self.file.write(struct.pack('?', data))

    def write_int16(self, data):
        self.file.write(struct.pack(self.byteorder + 'h', data))

    def write_uint16(self, data):
        self.file.write(struct.pack(self.byteorder + 'H', data))

    def write_int32(self, data):
        self.file.write(struct.pack(self.byteorder + 'l', data))

    def write_uint32(self, data):
        self.file.write(struct.pack(self.byteorder + 'L', data))

    def write_int64(self, data):
        self.file.write(struct.pack(self.byteorder + 'q', data))

    def write_uint64(self, data):
        self.file.write(struct.pack(self.byteorder + 'Q', data))

    def write_float(self, data):
        self.file.write(struct.pack(self.byteorder + 'f', data))

    def write_double(self, data):
        self.file.write(struct.pack(self.byteorder + 'd', data))

    def write_string(self, data, encoding='utf-8', errors='strict'):
        self.file.write(data.encode(encoding, errors))
