from ..bh3.bh3binaryreader import BH3BinaryReader
from ..bh3.bh3binarywriter import BH3BinaryWriter
from .bhabonetrack import BHABoneTrack


class BHAFile:
    def __init__(self):
        self.root_bone_track = None
        self._file_size = 0

    def read(self, filename):
        with open(filename, 'rb') as f:
            reader = BH3BinaryReader(f)
            self._read_chunk(reader)

    def _read_chunk(self, reader, parent=None):
        reader.file.seek(4, 1)  # data_size
        chunk_type = reader.read_uint16()
        num_children = reader.read_uint16()

        if chunk_type == 8:
            parent = self._read_chunk(reader, parent)
            num_children -= 1
            for bc in range(0, num_children):
                self._read_chunk(reader, parent)
            self.root_bone_track = parent
        elif chunk_type == 7:
            bone_track = BHABoneTrack()
            bone_track.read(reader)
            if parent:
                bone_track.parent = parent
                parent.children.append(bone_track)
            return bone_track
        else:
            for c in range(0, num_children):
                self._read_chunk(reader)

    def calc_size(self):
        self._file_size = 8 + self.root_bone_track.calc_size()

    def write(self, filename):
        with open(filename, 'wb') as f:
            writer = BH3BinaryWriter(f)
            self.calc_size()

            writer.write_uint32(self._file_size)
            writer.write_uint16(0)
            writer.write_uint16(1)

            self.root_bone_track.write(writer)

