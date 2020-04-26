# mpet.py - implementation of Ntreev PangYa .mpet and .pet format.
# By John Chadwick <johnwchadwick@gmail.com>
#
# Special thanks to HSReina for their universal extractor and a few pointers.
# Also, to the developers of the original paktools and mpetmqo tool.

from io import BytesIO

from .ioutil import (
    read_struct, write_struct,
    read_cstr, write_cstr
)


class Mpet:
    def __init__(self, bones=None, textures=None, meshes=None, meshid=None):
        self.bones = bones
        self.textures = textures
        self.meshes = meshes
        self.meshid = meshid

    def load(self, file):
        self.bones = []
        self.textures = []
        self.meshes = []

        while True:
            block = Block()
            block.load(file)

            # EOF
            if not block.is_valid():
                return

            # Version block
            if block.id == b'VERS':
                # Do not know what to do yet.
                # Seems to just be an integer with a version ID.
                pass

            # Textures block
            elif block.id == b'TEXT':
                count, = read_struct(block.stream, '<I')

                for i in range(count):
                    texture = Texture()
                    texture.load(block.stream)

                    self.textures.append(texture)

            # Bones block
            elif block.id == b'BONE':
                count, = read_struct(block.stream, '<B')

                for i in range(count):
                    bone = Bone()
                    bone.load(block.stream)

                    self.bones.append(bone)

            # Meshes block
            elif block.id == b'MESH':
                count, = read_struct(block.stream, '<B')

                # TODO: try to understand these values
                # are they per-mesh?

                self.meshid, u2, u3, u4, u5 = read_struct(block.stream, '<5I')

                for i in range(count):
                    mesh = Mesh()
                    mesh.load(block.stream)

                    self.meshes.append(mesh)


            # Animations block (?)
            elif block.id == b'FANM':
                pass

            # Unknown block
            else:
                print('warning: unknown block type: %r' % id)

    def save(self, file):
        # Textures block
        block = Block(b'TEXT')
        write_struct(block.stream, '<I', len(self.textures))

        for texture in self.textures:
            texture.save(block.stream)

        block.write(file)

        # Bones block
        block = Block(b'BONE')
        write_struct(block.stream, '<B', len(self.bones))

        for bone in self.bones:
            bone.save(block.stream)

        block.write(file)



class Block:
    def __init__(self, id=None):
        self.stream = BytesIO()
        self.id = id

    def is_valid(self):
        return self.id is not None

    def load(self, file):
        id = file.read(4)
        if id is None or len(id) == 0:
            id = None
            return
        size, = read_struct(file, '<I')
        data = file.read(size)

        self.id = id
        self.stream = BytesIO(data)

    def save(self, file):
        size = self.stream.tell()
        self.stream.seek(0)
        data = self.stream.read()

        file.write(self.id)
        write_struct(file, '<I', size)
        file.write(data)


class Texture:
    def __init__(self, fn=None):
        self.fn = fn

    def is_valid(self):
        return self.fn is not None

    def load(self, file):
        # looks like Ntreev left us some stack garbage
        self.fn = read_struct(file, '<44s')[0].split(b'\x00')[0]

    def save(self, file):
        write_struct(file, '<44s', self.fn)

    def __repr__(self):
        return "Texture(%s)" % (self.fn)


class Bone:
    def __init__(self, name=None, parent=None, matrix=None):
        self.name = name
        self.parent = parent
        self.matrix = matrix

    def is_valid(self):
        return self.name is not None

    def load(self, file):
        self.name = read_cstr(file)
        self.parent, = read_struct(file, '<B')
        self.matrix = read_struct(file, '<12f')

    def save(self, file):
        write_cstr(file, self.name)
        write_struct(file, '<B12f', self.parent, *self.matrix)

    def __repr__(self):
        fmt = "Bone(%s, %d, [%f" + (", %f" * 11) + "])"
        return fmt % (self.name, self.parent, *self.matrix)


class BoneWeight:
    def __init__(self, weight=None, id=None):
        self.weight = weight
        self.id = id

    def load(self, file):
        self.weight, self.id = read_struct(file, '<2B')

    def save(self, file):
        write_struct(file, '<2B', self.weight, self.id)

    def __repr__(self):
        return "BoneWeight(weight=%d, id=%d)" % self.weight, self.id


class Vertex:
    def __init__(self, x=None, y=None, z=None, w=None, bone_weights=None):
        self.x, self.y, self.z, self.w = x, y, z, w
        self.bone_weights = bone_weights

    def load(self, file):
        wsum = 0
        self.bone_weights = []

        self.x, self.y, self.z, self.w = read_struct(file, '<4f')

        # Bone weights continue until saturated.
        while wsum < 0xFF:
            weight = BoneWeight()
            weight.load(file)

            wsum += weight.weight
            self.bone_weights.append(weight)

        # Strangely, file leaves space for at least 2.
        if len(self.bone_weights) < 2:
            file.read(2)

    def save(self, file):
        write_struct(file, '<4f', self.x, self.y, self.z, self.w)

        for weight in self.bone_weights:
            weight.save(file)

        if len(self.bone_weights) < 2:
            file.write("\x00\x00")

    def __repr__(self):
        return "Vertex(%f, %f, %f)" % (self.x, self.y, self.z)


class PolygonIndex:
    def __init__(self, index=None, nx=None, ny=None, nz=None, u=None, v=None):
        self.index = index
        self.nx, self.ny, self.nz = nx, ny, nz
        self.u, self.v = u, v

    def load(self, file):
        self.index, = read_struct(file, '<I')
        self.nx, self.ny, self.nz = read_struct(file, '<3f')
        self.u, self.v = read_struct(file, '<2f')

    def save(self, file):
        write_struct(file, '<I', self.index)
        write_struct(file, '<3f', self.nx, self.ny, self.nz)
        write_struct(file, '<2f', self.u, self.v)

    def __repr__(self):
        return "PolygonIndex(index=%d)" % self.index


class Polygon:
    def __init__(self, indices=None):
        self.indices = indices

    def load(self, file):
        self.indices = []
        for i in range(3):
            index = PolygonIndex()
            index.load(file)

            self.indices.append(index)

    def save(self, file):
        for index in self.indices:
            index.save(file)


class Mesh:
    def __init__(self, vertices=None, polygons=None, texmap=None):
        self.vertices = vertices
        self.polygons = polygons
        self.texmap = texmap

    def load(self, file):
        self.vertices = []
        self.polygons = []
        self.texmap = []

        # Vertices
        num_vertices, = read_struct(file, '<I')
        print(num_vertices)
        for i in range(num_vertices):
            vertex = Vertex()
            vertex.load(file)
            print(vertex.x, vertex.y, vertex.z)

            self.vertices.append(vertex)

        # Polygons
        num_polygons, = read_struct(file, '<I')
        for i in range(num_polygons):
            polygon = Polygon()
            polygon.load(file)

            self.polygons.append(polygon)

        # Mapping of polygons to textures
        for i in range(num_polygons):
            self.texmap.append(read_struct(file, '<B')[0])

    def __repr__(self):
        return "Mesh(vertices=%s, polygons=%s)" % (
            repr(self.vertices),
            repr(self.polygons),
        )
