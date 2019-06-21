class BH3Bone:
    def __init__(self):
        self.vertex_index = -1
        self.vertex_count = 0
        self.name = "bone_unnamed"
        self.rotation = [1, 0, 0, 0]
        self.position = [0, 0, 0]
        self.parent = None
        self.children = []

        self._data_size = 0
        self._total_data_size = 0

    def read(self, reader):
        self.vertex_index = reader.read_int32()
        self.vertex_count = reader.read_uint32()
        self.name = reader.read_string()
        self.rotation = reader.read_quaternion()
        self.position = reader.read_vector3()
        reader.file.seek(4, 1)

    def calc_size(self):
        self._data_size = 53 + len(self.name.encode('utf-8', 'strict'))
        self._total_data_size += self._data_size + 8

        for child in self.children:
            self._total_data_size += child.calc_size()

        return self._total_data_size

    def write(self, writer):
        writer.write_uint32(self._total_data_size)
        writer.write_uint16(6)
        writer.write_uint16(len(self.children) + 1)

        writer.write_uint32(self._data_size)
        writer.write_uint16(7)
        writer.write_uint16(0)

        writer.write_int32(self.vertex_index)
        writer.write_uint32(self.vertex_count)
        writer.write_string(self.name)
        writer.write_quaternion(self.rotation)
        writer.write_vector3(self.position)
        writer.write_float(self.rotation[1])

        for child in self.children:
            child.write(writer)
