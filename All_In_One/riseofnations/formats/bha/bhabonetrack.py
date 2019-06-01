from .bhabonetrackkey import BHABoneTrackKey


class BHABoneTrack:
    def __init__(self):
        self.keys = []
        self.parent = None
        self.children = []
        self._data_size = 0
        self._total_data_size = 0

    def read(self, reader):
        num_elements = reader.read_uint32()

        for ki in range(0, num_elements):
            bone_track_key = BHABoneTrackKey()
            bone_track_key.time_step = reader.read_float()
            bone_track_key.rotation = reader.read_quaternion()
            bone_track_key.position = reader.read_vector3()
            reader.file.seek(4, 1)
            self.keys.append(bone_track_key)

    def calc_size(self):
        self._data_size = 12 + 36 * len(self.keys)
        self._total_data_size += self._data_size + 8

        for child in self.children:
            self._total_data_size += child.calc_size()

        return self._total_data_size

    def write(self, writer):
        writer.write_uint32(self._total_data_size)
        writer.write_uint16(8)
        writer.write_uint16(len(self.children) + 1)

        writer.write_uint32(self._data_size)
        writer.write_uint16(7)
        writer.write_uint16(0)
        writer.write_uint32(len(self.keys))

        for bone_track_key in self.keys:
            writer.write_float(bone_track_key.time_step)
            writer.write_quaternion(bone_track_key.rotation)
            writer.write_vector3(bone_track_key.position)
            writer.write_float(bone_track_key.rotation[1])

        for child in self.children:
            child.write(writer)

    def add_keys(self, count):
        for ki in range(count):
            self.keys.append(BHABoneTrackKey())
