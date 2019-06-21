# geometry stream decompiler

from struct import pack, unpack

from .utils import pad, read_list_header, read_list_data


class TkMeshMetaData():
    def __init__(self, data=None):
        self.raw_ID = ""
        self._ID = ""
        if data is not None:
            self.read(data)

    def create(self, ID, hash, vert_size, vert_offset, index_size,
               index_offset):
        self.ID = ID
        self.hash = hash
        self.vert_size = vert_size
        self.vert_offset = vert_offset
        self.index_size = index_size
        self.index_offset = index_offset

    def read(self, data):
        self.ID = data.read(0x80)
        self.hash, self.vertex_size, _, self.index_size, _ = unpack(
            '<QIIII', data.read(0x18))

    def __bytes__(self):
        b = self.ID
        b += pack('<QIIII', self.hash, self.vert_size, self.vert_offset,
                  self.index_size, self.index_offset)
        return b

    @property
    def ID(self):
        return self._ID

    @ID.setter
    def ID(self, other):
        if isinstance(other, str):
            self._ID = pad(other, 0x80, b'\xFE', True)
            self.raw_ID = other
        else:
            self._ID = other


class TkMeshData():
    def __init__(self, data=None):
        self.raw_ID = ""
        self._ID = ""
        if data is not None:
            self.read(data)

    def create(self, ID, hash, vert_size, index_size):
        self.ID = ID
        self.hash = hash
        self.vertex_size = vert_size
        self.index_size = index_size
        self.list_data = (b'\x00'*8 + pack('<I', vert_size + index_size) +
                          b'\x01\xFE\xFE\xFE')

    def read(self, data):
        self.ID = data.read(0x80)
        self.hash, self.vertex_size, self.index_size = unpack(
            '<QII', data.read(0x10))
        self.list_data = data.read(0x10)
        # self.offset, self.count = read_list_header(data)
        # data.seek(0x10, 1)

    def __bytes__(self):
        b = self.ID
        print(self.hash, self.vertex_size, self.index_size)
        b += pack('<QII', self.hash, self.vertex_size, self.index_size)
        b += self.list_data
        return b

    @property
    def ID(self):
        return self._ID

    @ID.setter
    def ID(self, other):
        if isinstance(other, str):
            self._ID = pad(other, 0x80, b'\xFE', True)
            self.raw_ID = other
        else:
            self._ID = other


class StreamData():
    def __init__(self, fname):
        self.fname = fname
        self.metadata = []
        self.vertex_data = []       # a list of bytearrays
        self.index_data = []        # a list of bytearrays
        self.count = 0
        self.data_offsets = []

    def create(self, ids, verts, indexes):
        """
        Get the metadata an ordered dictionary with the keys as the IDs,
        and the hash as the value
        Get the index and vert data as bytearrays
        """

        self.header = (b'\xdd\xdd\xdd\xdd\xc4\x09\x00\x00'
                       b'\xff\xff\xff\xff\xff\xff\xff\xff'
                       b'\x4b\x20\x31\x90\x4a\xb7\x2c\x60'
                       b'cTkGeometryStreamData\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfe')

        i = 0
        for key, value in ids.items():
            meta = TkMeshData()
            meta.create(key, value['hash'], len(verts[i]),
                        len(indexes[i]))
            self.metadata.append(meta)
            i += 1
        self.count = i
        self.vertex_data = verts
        self.index_data = indexes

    def read(self):
        """
        Read in the geometry.data.mbin file
        This will load the file into memory and place all the data in
        variables so that they can be easily manipulated
        """
        with open(self.fname, 'rb') as f:
            # store header
            self.header = f.read(0x60)
            # read TkMeshData list header
            offset, self.count = read_list_header(f)
            # jump to start of TkMeshData
            f.seek(offset, 1)
            # read in all the metadata
            for _ in range(self.count):
                self.metadata.append(TkMeshData(f))
            # read in all the vertex and index data as bytes.
            # we will do no processing
            for m in self.metadata:
                self.vertex_data.append(f.read(m.vertex_size))
                self.index_data.append(f.read(m.index_size))

    def save(self):
        with open(self.fname, 'wb') as f:
            # keep a list of the locations that we need to overwrite the offset
            # of.
            overwrite_locs = []
            offset_locs = []
            # write the header
            f.write(self.header)
            # write the list header for the number of metadata structs
            f.write(pack('<Q', 0x10))
            f.write(pack('<I', self.count))
            f.write(pack('<I', 1))
            # write the metadata
            for m in self.metadata:
                f.write(bytes(m))
                overwrite_locs.append(f.tell() - 0x10)
            for i in range(self.count):
                offset_locs.append(f.tell())
                self.data_offsets.append(f.tell())   # record vert offset
                f.write(self.vertex_data[i])
                self.data_offsets.append(f.tell())   # record indexes offset
                f.write(self.index_data[i])
            for i in range(self.count):
                f.seek(overwrite_locs[i], 0)
                f.write(pack('<Q', offset_locs[i] - overwrite_locs[i]))

    def __add__(self, other):
        # for now will just append
        new = StreamData('COMBINED.GEOMETRY.DATA.MBIN')
        new.header = self.header        # doesn't matter which ones is used
        new.metadata = self.metadata + other.metadata
        new.vertex_data = self.vertex_data + other.vertex_data
        new.index_data = self.index_data + other.index_data
        new.count = self.count + other.count
        return new


class GeometryData():
    def __init__(self, fname):
        self.fname = fname
        self.VertexCount = 0
        self.IndexCount = 0
        self.Indices16Bit = 0
        self.CollisionIndexCount = 0
        self.JointBindings = []
        self.JointExtents = []
        self.JointMirrorPairs = []
        self.JointMirrorAxes = []
        self.SkinMatrixLayout = []
        self.MeshVertRStart = []
        self.MeshVertREnd = []
        self.BoundHullVertSt = []
        self.BoundHullVertEd = []
        self.MeshBaseSkinMat = []
        self.MeshAABBMin = []
        self.MeshAABBMax = []
        self.BoundHullVerts = []
        self.VertexLayout = b''
        self.SmallVertexLayout = b''
        self.IndexBuffer = []
        self.StreamMetaDataArray = []

    def read(self):
        """
        Read in the geometry.data.mbin file
        This will load the file into memory and place all the data in
        variables so that they can be easily manipulated
        """
        with open(self.fname, 'rb') as f:
            # store header
            self.header = f.read(0x60)
            (self.VertexCount, self.IndexCount, self.Indices16Bit,
             self.CollisionIndexCount) = unpack('<iiii', f.read(0x10))
            self.JointBindings = read_list_data(f, 0x68)
            self.JointExtents = read_list_data(f, 0x30)
            self.JointMirrorPairs = read_list_data(f, 0x4)
            self.JointMirrorAxes = read_list_data(f, 0x2C)
            self.SkinMatrixLayout = read_list_data(f, 0x4)
            self.MeshVertRStart = read_list_data(f, 0x4)
            self.MeshVertREnd = read_list_data(f, 0x4)
            self.BoundHullVertSt = read_list_data(f, 0x4)
            self.BoundHullVertEd = read_list_data(f, 0x4)
            self.MeshBaseSkinMat = read_list_data(f, 0x4)
            self.MeshAABBMin = read_list_data(f, 0x10)
            self.MeshAABBMax = read_list_data(f, 0x10)
            self.BoundHullVerts = read_list_data(f, 0x10)


if __name__ == "__main__":
    # TODO: do as tests
    c = StreamData('EGGRESOURCE.GEOMETRY.DATA.MBIN.PC')
    c.read()

    d = StreamData('test.mbin')
    d.create({'TEST1': 123456789},
             [b'THIS IS A BUNCH OF TEST DATA'],
             [b'\x01\x02\x03\x04\x01\x01\x01\x06'])
    d.save()

    d = StreamData('CRYSTAL_LARGE.GEOMETRY.DATA.MBIN.PC')
    d.read()
    e = c + d
    e.save()
