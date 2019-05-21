from ...fileio.binaryreader import BinaryReader
import struct


class BH3BinaryReader(BinaryReader):
    def __init__(self, binaryfile):
        super().__init__(binaryfile, byteorder='<')

    def read_string(self):
        str_length = self.read_uint32() - 1
        data = self.file.read(str_length).decode('utf-8', 'strict')
        self.file.seek(1, 1)
        return data

    def read_vector3(self):
        data = list(struct.unpack(self.byteorder + 'fff', self.file.read(12)))
        return data

    def read_quaternion(self):
        x, y, z, w = struct.unpack(self.byteorder + 'ffff', self.file.read(16))
        return [w, x, y, z]

    def read_uv(self):
        u, v = struct.unpack(self.byteorder + 'ff', self.file.read(8))
        return [u, 1.0 - v]

    def read_face(self):
        x, y, z = struct.unpack(self.byteorder + 'HHH', self.file.read(6))
        return [z, y, x]
