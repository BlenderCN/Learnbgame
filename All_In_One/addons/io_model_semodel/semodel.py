import time
import struct

# <pep8 compliant>

LOG_READ_TIME = False
LOG_WRITE_TIME = False


def enum(**enums):
    return type('Enum', (), enums)


try:
    xrange
except NameError:
    xrange = range


SEMODEL_PRESENCE_FLAGS = enum(
    # Whether or not this model contains a bone block
    SEMODEL_PRESENCE_BONE=1 << 0,
    # Whether or not this model contains submesh blocks
    SEMODEL_PRESENCE_MESH=1 << 1,
    # Whether or not this model contains inline material blocks
    SEMODEL_PRESENCE_MATERIALS=1 << 2,

    # The file contains a custom data block
    SEMODEL_PRESENCE_CUSTOM=1 << 7,
)

SEMODEL_BONEPRESENCE_FLAGS = enum(
    # Whether or not bones contain global-space matrices
    SEMODEL_PRESENCE_GLOBAL_MATRIX=1 << 0,
    # Whether or not bones contain local-space matrices
    SEMODEL_PRESENCE_LOCAL_MATRIX=1 << 1,

    # Whether or not bones contain scales
    SEMODEL_PRESENCE_SCALES=1 << 2,
)

SEMODEL_MESHPRESENCE_FLAGS = enum(
    # Whether or not meshes contain at least 1 uv map
    SEMODEL_PRESENCE_UVSET=1 << 0,
    # Whether or not meshes contain vertex normals
    SEMODEL_PRESENCE_NORMALS=1 << 1,
    # Whether or not meshes contain vertex colors (RGBA)
    SEMODEL_PRESENCE_COLOR=1 << 2,
    # Whether or not meshes contain at least 1 weighted skin
    SEMODEL_PRESENCE_WEIGHTS=1 << 3,
)


class Info(object):
    __slots__ = ('version', 'magic')

    def __init__(self, file=None):
        self.version = 1
        self.magic = b'SEModel'
        if file is not None:
            self.load(file)

    def load(self, file):
        bytes = file.read(9)
        data = struct.unpack('=7ch', bytes)

        magic = b''
        for i in range(7):
            magic += data[i]

        version = data[7]

        assert magic == self.magic
        assert version == self.version

    def save(self, file):
        bytes = self.magic
        bytes += struct.pack('h', self.version)
        file.write(bytes)


class Header(object):
    __slots__ = (
        'dataPresenceFlags', 'bonePresenceFlags',
        'meshPresenceFlags', 'boneCount',
        'meshCount', 'matCount',
    )

    def __init__(self, file=None):
        self.dataPresenceFlags = 0x0
        self.bonePresenceFlags = 0x0
        self.meshPresenceFlags = 0x0

        self.boneCount = 0
        self.meshCount = 0
        self.matCount = 0

        if file is not None:
            self.load(file)

    def load(self, file):
        bytes = file.read(2)
        data = struct.unpack('h', bytes)

        headerSize = data[0]
        bytes = file.read(headerSize - 2)
        # = prefix tell is to ignore C struct packing rules
        data = struct.unpack('=3BIII3B', bytes)

        self.dataPresenceFlags = data[0]
        self.bonePresenceFlags = data[1]
        self.meshPresenceFlags = data[2]

        self.boneCount = data[3]
        self.meshCount = data[4]
        self.matCount = data[5]
        # reserved = data[6]
        # reserved = data[7]
        # reserved = data[8]

    def save(self, file):
        bytes = struct.pack('=3BIII3B',
                            self.dataPresenceFlags, self.bonePresenceFlags,
                            self.meshPresenceFlags, self.boneCount,
                            self.meshCount, self.matCount,
                            0, 0, 0)

        size = struct.pack('h', len(bytes) + 2)
        file.write(size)
        file.write(bytes)


class Bone_t(object):
    """
    The Bone_t class is only ever used to get the size
    and format character used by weight indices in the semodel
    """
    __slots__ = ('size', 'char')

    def __init__(self, header):
        if header.boneCount <= 0xFF:
            self.size = 1
            self.char = 'B'
        elif header.boneCount <= 0xFFFF:
            self.size = 2
            self.char = 'H'
        else:  # if header.boneCount <= 0xFFFFFFFF:
            self.size = 4
            self.char = 'I'


class Face_t(object):
    """
    The Face_t class is only ever used to get the size
    and format character used by face indices in the semodel
    """
    __slots__ = ('size', 'char')

    def __init__(self, mesh):
        if mesh.vertexCount <= 0xFF:
            self.size = 1
            self.char = 'B'
        elif mesh.vertexCount <= 0xFFFF:
            self.size = 2
            self.char = 'H'
        else:
            self.size = 4
            self.char = 'I'


class SimpleMaterialData(object):
    __slots__ = ('diffuseMap', 'normalMap', 'specularMap')

    def __init__(self, file=None):
        self.diffuseMap = ""
        self.normalMap = ""
        self.specularMap = ""

        if file is not None:
            self.load(file)

    def load(self, file):
        # Diffuse map image
        bytes = b''
        b = file.read(1)
        while not b == b'\x00':
            bytes += b
            b = file.read(1)
        self.diffuseMap = bytes.decode("utf-8")
        # Normal map image
        bytes = b''
        b = file.read(1)
        while not b == b'\x00':
            bytes += b
            b = file.read(1)
        self.normalMap = bytes.decode("utf-8")
        # Specular map image
        bytes = b''
        b = file.read(1)
        while not b == b'\x00':
            bytes += b
            b = file.read(1)
        self.specularMap = bytes.decode("utf-8")

    def save(self, file):
        # Diffuse map image
        bytes = struct.pack('%ds' % (len(self.diffuseMap) + 1),
                            self.diffuseMap.encode())
        file.write(bytes)
        # Normal map image
        bytes = struct.pack('%ds' % (len(self.normalMap) + 1),
                            self.normalMap.encode())
        file.write(bytes)
        # Specular map image
        bytes = struct.pack('%ds' % (len(self.specularMap) + 1),
                            self.specularMap.encode())
        file.write(bytes)


class Material(object):
    __slots__ = ('name', 'isSimpleMaterial', 'inputData')

    def __init__(self, file=None):
        self.name = ""
        self.isSimpleMaterial = True
        self.inputData = SimpleMaterialData()

        if file is not None:
            self.load(file)

    def load(self, file):
        bytes = b''
        b = file.read(1)
        while not b == b'\x00':
            bytes += b
            b = file.read(1)
        # Decode name
        self.name = bytes.decode("utf-8")
        # Are we a simple material
        self.isSimpleMaterial = struct.unpack("?", file.read(1))[0]

        # If simple material, decode simple payload
        if (self.isSimpleMaterial):
            self.inputData = SimpleMaterialData(file)

    def save(self, file):
        bytes = struct.pack('%dsB' % (len(self.name) + 1),
                            self.name.encode(), self.isSimpleMaterial)
        file.write(bytes)

        # Ask the input to save itself
        self.inputData.save(file)


class Bone(object):
    __slots__ = ('name', 'flags',
                 'boneParent', 'globalPosition', 'globalRotation',
                 'localPosition', 'localRotation',
                 'scale')

    def __init__(self, file=None):
        self.name = ""

        self.flags = 0x0

        self.globalPosition = (0, 0, 0)
        self.globalRotation = (0, 0, 0, 1)

        self.localPosition = (0, 0, 0)
        self.localRotation = (0, 0, 0, 1)

        self.scale = (1, 1, 1)

        if file is not None:
            self.load(file)

    def load(self, file):
        bytes = b''
        b = file.read(1)
        while not b == b'\x00':
            bytes += b
            b = file.read(1)
        self.name = bytes.decode("utf-8")

    def loadData(self, file,
                 useGlobal=False, useLocal=False, useScale=False):
        # Read the flags and boneParent for the bone
        bytes = file.read(5)
        data = struct.unpack("=Bi", bytes)
        self.flags = data[0]
        self.boneParent = data[1]

        # Read global matrices if available
        if useGlobal:
            bytes = file.read(28)
            data = struct.unpack("=7f", bytes)
            self.globalPosition = (data[0], data[1], data[2])
            self.globalRotation = (data[3], data[4], data[5], data[6])

        # Read local matrices if available
        if useLocal:
            bytes = file.read(28)
            data = struct.unpack("=7f", bytes)
            self.localPosition = (data[0], data[1], data[2])
            self.localRotation = (data[3], data[4], data[5], data[6])

        # Read scale if available
        if useScale:
            bytes = file.read(12)
            data = struct.unpack("=3f", bytes)
            self.scale = (data[0], data[1], data[2])

    def save(self, file,
             useGlobal=False, useLocal=False, useScale=False):
        bytes = struct.pack("=Bi", self.flags, self.boneParent)
        file.write(bytes)

        if useGlobal:
            bytes = struct.pack("=7f", self.globalPosition[0], self.globalPosition[1],
                                self.globalPosition[2], self.globalRotation[0],
                                self.globalRotation[1], self.globalRotation[2],
                                self.globalRotation[3])
            file.write(bytes)

        if useLocal:
            bytes = struct.pack("=7f", self.localPosition[0], self.localPosition[1],
                                self.localPosition[2], self.localRotation[0],
                                self.localRotation[1], self.localRotation[2],
                                self.localRotation[3])
            file.write(bytes)

        if useScale:
            bytes = struct.pack(
                "=3f", self.scale[0], self.scale[1], self.scale[2])
            file.write(bytes)


class Vertex(object):
    __slots__ = ('position', 'uvLayers', 'normal', 'color', 'weights')

    def __init__(self, uvSetCount=0, maxSkinInfluence=0):
        self.position = (0, 0, 0)
        self.normal = (0, 0, 0)
        self.color = (1, 1, 1, 1)

        self.uvLayers = [(0, 0)] * uvSetCount
        self.weights = [(0, 0)] * maxSkinInfluence

    @staticmethod
    def loadData(file, vertexCount, bone_t,
                 uvSetCount=0, maxSkinInfluence=0,
                 useNormals=False, useColors=False):
        # Preallocate verticies
        vertex_buffer = [None] * vertexCount

        # Positions first
        bytes = file.read(12 * vertexCount)
        data_pos = struct.unpack("=%df" % (3 * vertexCount), bytes)

        # UVLayers
        bytes = file.read((8 * uvSetCount) * vertexCount)
        data_uvs = struct.unpack(
            "=%df" % ((2 * uvSetCount) * vertexCount), bytes)

        # Normals
        if useNormals:
            bytes = file.read(12 * vertexCount)
            data_norms = struct.unpack("=%df" % (3 * vertexCount), bytes)

        # Colors
        if useColors:
            bytes = file.read(4 * vertexCount)
            data_colors = struct.unpack("=%dB" % (4 * vertexCount), bytes)

        # Weights
        bytes = file.read(((4 + bone_t.size) * maxSkinInfluence) * vertexCount)
        data_weights = struct.unpack(
            "=" + ((("%cf" % bone_t.char) * maxSkinInfluence) * vertexCount), bytes)

        for vert_idx in xrange(vertexCount):
            # Initialize vertex, assign position
            vertex_buffer[vert_idx] = Vertex(
                uvSetCount=uvSetCount, maxSkinInfluence=maxSkinInfluence)
            vertex_buffer[vert_idx].position = data_pos[vert_idx *
                                                        3:(vert_idx * 3) + 3]

            if uvSetCount > 0:
                uv_layers = data_uvs[vert_idx *
                                     (2 * uvSetCount):(vert_idx *
                                                       (2 * uvSetCount)) + 2 * uvSetCount]
                for uvi in xrange(uvSetCount):
                    vertex_buffer[vert_idx].uvLayers[uvi] = uv_layers[uvi *
                                                                      2:(uvi * 2) + 2]

            if useNormals:
                vertex_buffer[vert_idx].normal = data_norms[vert_idx *
                                                            3:(vert_idx * 3) + 3]
            if useColors:
                color = data_colors[vert_idx * 4:(vert_idx * 4) + 4]
                vertex_buffer[vert_idx].color = (
                    color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255)

            if maxSkinInfluence > 0:
                weights = data_weights[vert_idx *
                                       (2 * maxSkinInfluence):(vert_idx *
                                                               (2 * maxSkinInfluence)) + (2 * maxSkinInfluence)]
                for weight in xrange(maxSkinInfluence):
                    vertex_buffer[vert_idx].weights[weight] = weights[weight *
                                                                      2:(weight * 2) + 2]

        return vertex_buffer

    def savePosition(self, file):
        bytes = struct.pack(
            "=3f", self.position[0], self.position[1], self.position[2])
        file.write(bytes)

    def saveUVLayers(self, file, matReferenceCount):
        for _idx in xrange(matReferenceCount):
            if _idx < len(self.uvLayers):
                bytes = struct.pack(
                    "=2f", self.uvLayers[_idx][0], self.uvLayers[_idx][1])
                file.write(bytes)
            else:
                bytes = struct.pack(
                    "=2f", 0, 0)
                file.write(bytes)

    def saveNormal(self, file):
        bytes = struct.pack(
            "=3f", self.normal[0], self.normal[1], self.normal[2])
        file.write(bytes)

    def saveColor(self, file):
        bytes = struct.pack(
            "=4B", self.color[0] * 255, self.color[1] * 255, self.color[2] * 255, self.color[3] * 255)
        file.write(bytes)

    def saveWeights(self, file, maxSkinInfluence, bone_t):
        for _idx in xrange(maxSkinInfluence):
            if _idx < len(self.weights):
                bytes = struct.pack(
                    "=%cf" % bone_t.char, self.weights[_idx][0], self.weights[_idx][1])
                file.write(bytes)
            else:
                bytes = struct.pack(
                    "=%cf" % bone_t.char, 0, 0)
                file.write(bytes)


class Face(object):
    __slots__ = ('indices')

    def __init__(self, indices=(0, 1, 2)):
        self.indices = indices

    @staticmethod
    def loadData(file, faceCount, face_t):
        # Load variable length face buffer
        bytes = file.read((3 * face_t.size) * faceCount)
        data = struct.unpack("=%d%c" % ((faceCount * 3), face_t.char), bytes)

        # Create and return face buffer
        face_buffer = [None] * faceCount
        for face_idx, face_data in enumerate((data[i:i + 3] for i in xrange(0, len(data), 3))):
            face_buffer[face_idx] = Face(face_data)

        return face_buffer

    def save(self, file, face_t):
        bytes = struct.pack("=3%c" % face_t.char,
                            self.indices[0], self.indices[1], self.indices[2])
        file.write(bytes)


class Mesh(object):
    __slots__ = ('flags', 'vertexCount', 'faceCount',
                 'vertices', 'faces',
                 'materialReferences', 'matReferenceCount',
                 'maxSkinInfluence')

    def __init__(self, file=None, bone_t=None,
                 useUVs=False, useNormals=False,
                 useColors=False, useWeights=False):
        self.flags = 0x0

        self.vertexCount = 0
        self.faceCount = 0

        self.vertices = []
        self.faces = []

        self.matReferenceCount = 0
        self.maxSkinInfluence = 0

        self.materialReferences = []

        if file is not None:
            self.load(file, bone_t, useUVs, useNormals, useColors, useWeights)

    def load(self, file, bone_t,
             useUVs=False, useNormals=False,
             useColors=False, useWeights=False):
        bytes = file.read(11)
        data = struct.unpack("=3BII", bytes)
        self.flags = data[0]

        self.matReferenceCount = data[1]
        self.maxSkinInfluence = data[2]

        if not useUVs:
            self.matReferenceCount = 0
        if not useWeights:
            self.maxSkinInfluence = 0

        self.vertexCount = data[3]
        self.faceCount = data[4]

        # Expand buffers before loading
        self.materialReferences = [None] * self.matReferenceCount

        # Calculate face index
        face_t = Face_t(self)

        # Load vertex buffer
        self.vertices = Vertex.loadData(file, self.vertexCount, bone_t,
                                        self.matReferenceCount, self.maxSkinInfluence,
                                        useNormals, useColors)

        # Load face buffer
        self.faces = Face.loadData(file, self.faceCount, face_t)

        # Load material reference buffer (signed int32_t's per count)
        for mat_idx in xrange(self.matReferenceCount):
            self.materialReferences[mat_idx] = struct.unpack("i", file.read(4))[
                0]

    def save(self, file, bone_t, useUVs=False, useNormals=False, useColors=False, useWeights=False):
        # Update metadata first
        self.vertexCount = len(self.vertices)
        self.faceCount = len(self.faces)

        face_t = Face_t(self)

        for vertex in self.vertices:
            if len(vertex.uvLayers) > self.matReferenceCount:
                self.matReferenceCount = len(vertex.uvLayers)
            if len(vertex.weights) > self.maxSkinInfluence:
                self.maxSkinInfluence = len(vertex.weights)

        # Ensure we have enough references per layer, if not, default to no material
        if len(self.materialReferences) < self.matReferenceCount:
            for _idx in xrange(self.matReferenceCount - len(self.materialReferences)):
                self.materialReferences.append(-1)

        bytes = struct.pack("=3BII", self.flags, self.matReferenceCount,
                            self.maxSkinInfluence, self.vertexCount, self.faceCount)
        file.write(bytes)

        # Produce vertex buffer by data type
        for vertex in self.vertices:
            vertex.savePosition(file)

        if useUVs:
            for vertex in self.vertices:
                vertex.saveUVLayers(file, self.matReferenceCount)

        if useNormals:
            for vertex in self.vertices:
                vertex.saveNormal(file)

        if useColors:
            for vertex in self.vertices:
                vertex.saveColor(file)

        if useWeights:
            for vertex in self.vertices:
                vertex.saveWeights(file, self.maxSkinInfluence, bone_t)

        # Produce the face buffer
        for face in self.faces:
            face.save(file, face_t)

        # Produce material indices
        for matIndex in self.materialReferences:
            bytes = struct.pack("i", matIndex)
            file.write(bytes)


class Model(object):
    __slots__ = ('__info', 'info', 'header', 'bones', 'meshes', 'materials')

    def __init__(self, path=None):
        self.__info = Info()
        self.header = Header()

        self.bones = []
        self.meshes = []
        self.materials = []

        if path is not None:
            self.load(path)

    def update_metadata(self):
        header = self.header
        header.boneCount = len(self.bones)
        header.meshCount = len(self.meshes)
        header.matCount = len(self.materials)

        dataPresenceFlags = header.dataPresenceFlags
        bonePresenceFlags = header.bonePresenceFlags
        meshPresenceFlags = header.meshPresenceFlags

        if header.boneCount:
            dataPresenceFlags |= SEMODEL_PRESENCE_FLAGS.SEMODEL_PRESENCE_BONE
        if header.meshCount:
            dataPresenceFlags |= SEMODEL_PRESENCE_FLAGS.SEMODEL_PRESENCE_MESH
        if header.matCount:
            dataPresenceFlags |= SEMODEL_PRESENCE_FLAGS.SEMODEL_PRESENCE_MATERIALS

        # Check for non-default scale, local, global values
        useScales = False
        useLocals = False
        useGlobals = False

        for bone in self.bones:
            if bone.scale != (1, 1, 1):
                useScales = True
            if bone.localPosition != (0, 0, 0) or bone.localRotation != (0, 0, 0, 1):
                useLocals = True
            if bone.globalPosition != (0, 0, 0) or bone.globalRotation != (0, 0, 0, 1):
                useGlobals = True

            # Check to end early
            if useScales and useLocals and useGlobals:
                break

        if useScales:
            bonePresenceFlags |= SEMODEL_BONEPRESENCE_FLAGS.SEMODEL_PRESENCE_SCALES
        if useLocals:
            bonePresenceFlags |= SEMODEL_BONEPRESENCE_FLAGS.SEMODEL_PRESENCE_LOCAL_MATRIX
        if useGlobals:
            bonePresenceFlags |= SEMODEL_BONEPRESENCE_FLAGS.SEMODEL_PRESENCE_GLOBAL_MATRIX

        # Check for non-default properties
        useNormals = False
        useColors = False
        useUVSet = False
        useWeights = False

        for mesh in self.meshes:
            for vertex in mesh.vertices:
                if len(vertex.uvLayers):
                    useUVSet = True
                if len(vertex.weights):
                    useWeights = True
                if vertex.color != (1, 1, 1, 1):
                    useColors = True
                if vertex.normal != (0, 0, 0):
                    useNormals = True

                # Check to end early
                if useNormals and useColors and useUVSet and useWeights:
                    break

            # Check to end early
            if useNormals and useColors and useUVSet and useWeights:
                break

        if useNormals:
            meshPresenceFlags |= SEMODEL_MESHPRESENCE_FLAGS.SEMODEL_PRESENCE_NORMALS
        if useColors:
            meshPresenceFlags |= SEMODEL_MESHPRESENCE_FLAGS.SEMODEL_PRESENCE_COLOR
        if useUVSet:
            meshPresenceFlags |= SEMODEL_MESHPRESENCE_FLAGS.SEMODEL_PRESENCE_UVSET
        if useWeights:
            meshPresenceFlags |= SEMODEL_MESHPRESENCE_FLAGS.SEMODEL_PRESENCE_WEIGHTS

        # Assign header values
        header.dataPresenceFlags = dataPresenceFlags
        header.bonePresenceFlags = bonePresenceFlags
        header.meshPresenceFlags = meshPresenceFlags

    def load(self, path):
        if LOG_READ_TIME:
            time_start = time.time()
            print("Loading: '%s'" % path)

        try:
            file = open(path, "rb")
        except IOError:
            print("Could not open file for reading:\n %s" % path)
            return

        self.info = Info(file)
        self.header = Header(file)

        # Init the bone_t info
        bone_t = Bone_t(self.header)

        dataPresenceFlags = self.header.dataPresenceFlags
        bonePresenceFlags = self.header.bonePresenceFlags
        meshPresenceFlags = self.header.meshPresenceFlags

        self.bones = [None] * self.header.boneCount
        if dataPresenceFlags & SEMODEL_PRESENCE_FLAGS.SEMODEL_PRESENCE_BONE:
            useGlobal = bonePresenceFlags & SEMODEL_BONEPRESENCE_FLAGS.SEMODEL_PRESENCE_GLOBAL_MATRIX
            useLocal = bonePresenceFlags & SEMODEL_BONEPRESENCE_FLAGS.SEMODEL_PRESENCE_LOCAL_MATRIX
            useScale = bonePresenceFlags & SEMODEL_BONEPRESENCE_FLAGS.SEMODEL_PRESENCE_SCALES

            # Load bone tag names
            for i in xrange(self.header.boneCount):
                self.bones[i] = Bone(file)

            # Load bone data
            for i in xrange(self.header.boneCount):
                self.bones[i].loadData(
                    file, useGlobal, useLocal, useScale)

        self.meshes = [None] * self.header.meshCount
        if dataPresenceFlags & SEMODEL_PRESENCE_FLAGS.SEMODEL_PRESENCE_MESH:
            useUVs = meshPresenceFlags & SEMODEL_MESHPRESENCE_FLAGS.SEMODEL_PRESENCE_UVSET
            useNormals = meshPresenceFlags & SEMODEL_MESHPRESENCE_FLAGS.SEMODEL_PRESENCE_NORMALS
            useColors = meshPresenceFlags & SEMODEL_MESHPRESENCE_FLAGS.SEMODEL_PRESENCE_COLOR
            useWeights = meshPresenceFlags & SEMODEL_MESHPRESENCE_FLAGS.SEMODEL_PRESENCE_WEIGHTS

            # Load submeshes
            for i in xrange(self.header.meshCount):
                self.meshes[i] = Mesh(
                    file, bone_t, useUVs, useNormals, useColors, useWeights)

        # Load materials
        self.materials = [None] * self.header.matCount
        if dataPresenceFlags & SEMODEL_PRESENCE_FLAGS.SEMODEL_PRESENCE_MATERIALS:
            # Load material entries
            for i in xrange(self.header.matCount):
                self.materials[i] = Material(file)

        file.close()

        if LOG_READ_TIME:
            time_end = time.time()
            time_elapsed = time_end - time_start
            print("Done! - Completed in %ss" % time_elapsed)

    def save(self, filepath=""):
        if LOG_WRITE_TIME:
            time_start = time.time()
            print("Saving: '%s'" % filepath)

        try:
            file = open(filepath, "wb")
        except IOError:
            print("Could not open the file for writing:\n %s" % filepath)
            return

        # Update the header flags, based on the presence of different data types (Bones, Meshes, Materials)
        self.update_metadata()

        self.__info.save(file)
        self.header.save(file)

        for bone in self.bones:
            bytes = struct.pack(
                '%ds' % (len(bone.name) + 1), bone.name.encode())
            file.write(bytes)

        bonePresenceFlags = self.header.bonePresenceFlags
        meshPresenceFlags = self.header.meshPresenceFlags

        useGlobals = bonePresenceFlags & SEMODEL_BONEPRESENCE_FLAGS.SEMODEL_PRESENCE_GLOBAL_MATRIX
        useLocals = bonePresenceFlags & SEMODEL_BONEPRESENCE_FLAGS.SEMODEL_PRESENCE_LOCAL_MATRIX
        useScales = bonePresenceFlags & SEMODEL_BONEPRESENCE_FLAGS.SEMODEL_PRESENCE_SCALES

        useUVSet = meshPresenceFlags & SEMODEL_MESHPRESENCE_FLAGS.SEMODEL_PRESENCE_UVSET
        useNormal = meshPresenceFlags & SEMODEL_MESHPRESENCE_FLAGS.SEMODEL_PRESENCE_NORMALS
        useColor = meshPresenceFlags & SEMODEL_MESHPRESENCE_FLAGS.SEMODEL_PRESENCE_COLOR
        useWeights = meshPresenceFlags & SEMODEL_MESHPRESENCE_FLAGS.SEMODEL_PRESENCE_WEIGHTS

        bone_t = Bone_t(self.header)

        for bone in self.bones:
            bone.save(file, useGlobals, useLocals, useScales)

        for mesh in self.meshes:
            mesh.save(file, bone_t, useUVSet, useNormal, useColor, useWeights)

        for mat in self.materials:
            mat.save(file)

        file.close()

        if LOG_WRITE_TIME:
            time_end = time.time()
            time_elapsed = time_end - time_start
            print("Done! - Completed in %ss" % time_elapsed)
