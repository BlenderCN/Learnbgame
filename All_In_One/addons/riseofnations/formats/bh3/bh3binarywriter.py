from ...fileio.binarywriter import BinaryWriter
import struct


class BH3BinaryWriter(BinaryWriter):
    def __init__(self, binaryfile):
        super().__init__(binaryfile, byteorder='<')

    def write_string(self, data):
        data = data.encode('utf-8', 'strict')
        self.file.write(struct.pack(self.byteorder + 'L', len(data) + 1))
        self.file.write(data)
        self.file.write(struct.pack('B', 0))

    def write_vector3(self, data):
        self.file.write(struct.pack(self.byteorder + 'fff', data[0], data[1], data[2]))

    def write_quaternion(self, data):
        self.file.write(struct.pack(self.byteorder + 'ffff', data[1], data[2], data[3], data[0]))

    def write_uv(self, data):
        self.file.write(struct.pack(self.byteorder + 'ff', data[0], 1.0 - data[1]))

    def write_face(self, data):
        self.file.write(struct.pack(self.byteorder + 'HHH', data[2], data[1], data[0]))
