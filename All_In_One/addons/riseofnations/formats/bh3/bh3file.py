from .bh3binaryreader import BH3BinaryReader
from .bh3binarywriter import BH3BinaryWriter
from .bh3bone import BH3Bone


class BH3File:
    def __init__(self):
        self.vertices = []
        self.normals = []
        self.uvs = []
        self.faces = []
        self.root_bone = None

        self._mesh_data_size = 0
        self._file_size = 0

    def read(self, filename):
        """
        Read the file at the given filename
        :param filename: The location of the file on the system
        """
        with open(filename, 'rb') as f:
            reader = BH3BinaryReader(f)
            self._read_chunk(reader)

    def _read_chunk(self, reader, parent=None):
        reader.read_uint32()  # data_size
        chunk_type = reader.read_uint16()
        num_children = reader.read_uint16()

        if chunk_type == 2:  # vertices
            num_elements = reader.read_uint32()
            for vt in range(0, num_elements):
                self.vertices.append(reader.read_vector3())
                reader.file.seek(4, 1)
        elif chunk_type == 3:  # normals
            num_elements = reader.read_uint32()
            for ni in range(0, num_elements):
                self.normals.append(reader.read_vector3())
            reader.file.seek(4 * num_elements, 1)
        elif chunk_type == 4:  # uvs
            num_elements = reader.read_uint32()
            for tv in range(0, num_elements):
                self.uvs.append(reader.read_uv())
        elif chunk_type == 5:  # faces
            num_elements = int(reader.read_uint32() / 3)
            for fa in range(0, num_elements):
                self.faces.append(reader.read_face())
        elif chunk_type == 6:
            parent = self._read_chunk(reader, parent)
            num_children -= 1
            for bc in range(0, num_children):
                self._read_chunk(reader, parent)
            self.root_bone = parent
        elif chunk_type == 7:
            bone = BH3Bone()
            bone.read(reader)
            if parent:
                bone.parent = parent
                parent.children.append(bone)
            return bone
        else:
            for c in range(0, num_children):
                self._read_chunk(reader)

    def calc_size(self):
        self._mesh_data_size = 56 + 40 * len(self.vertices) + 6 * len(self.faces)
        self._file_size = 8 + self._mesh_data_size + self.root_bone.calc_size()

    def write(self, filename):
        with open(filename, 'wb') as f:
            writer = BH3BinaryWriter(f)
            self.calc_size()

            writer.write_uint32(self._file_size)
            writer.write_uint16(0)
            writer.write_uint16(2)

            writer.write_uint32(self._mesh_data_size)
            writer.write_uint16(1)
            writer.write_uint16(4)

            writer.write_uint32(12 + len(self.vertices) * 16)
            writer.write_uint16(2)
            writer.write_uint16(0)
            writer.write_uint32(len(self.vertices))
            for vert in self.vertices:
                writer.write_vector3(vert)
                writer.write_float(1.0)

            writer.write_uint32(12 + len(self.normals) * 16)
            writer.write_uint16(3)
            writer.write_uint16(0)
            writer.write_uint32(len(self.normals))
            for norm in self.normals:
                writer.write_vector3(norm)
            for ni in range(0, len(self.normals)):
                writer.write_uint32(4294967295)

            writer.write_uint32(12 + len(self.uvs) * 8)
            writer.write_uint16(4)
            writer.write_uint16(0)
            writer.write_uint32(len(self.uvs))
            for uv in self.uvs:
                writer.write_uv(uv)

            writer.write_uint32(12 + len(self.faces) * 6)
            writer.write_uint16(5)
            writer.write_uint16(0)
            writer.write_uint32(len(self.faces) * 3)
            for face in self.faces:
                writer.write_face(face)

            self.root_bone.write(writer)
