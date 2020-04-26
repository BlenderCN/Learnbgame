import bpy
import struct
import ntpath
from bpy_extras.io_utils import ImportHelper, unpack_face_list, unpack_list
from mathutils import Matrix, Quaternion, Vector


def readByte(file, endian='<'):
    return struct.unpack(endian+'b', file.read(1))[0]


def readUByte(file, endian='<'):
    return struct.unpack(endian+'B', file.read(1))[0]

    
def readShort(file, endian='<'):
    return struct.unpack(endian+'h', file.read(2))[0]


def readUShort(file, endian='<'):
    return struct.unpack(endian+'H', file.read(2))[0]

    
def readInt(file, endian='<'):
    return struct.unpack(endian+'i', file.read(4))[0]


def readUInt(file, endian='<'):
    return struct.unpack(endian+'I', file.read(4))[0]

    
def readFloat(file, endian='<'):
    return struct.unpack(endian+'f', file.read(4))[0]

    
def readBoolean(file, endian='<'):
    return struct.unpack(endian+'?', file.read(1))[0]


def expect(valueToExpect, expectedValue, errorString, file):
    if valueToExpect != expectedValue:
        raise NameError(errorString + "\t" + hex(file.tell()))

        
def UnpackNormals(packed, dim):
    return (((packed >> (dim*8)) & 255) - 127.5) / 127.5


def UnpackBoneWeights(packed):
    return packed / 255


def importGMDL(file):
    result = {'FINISHED'}

    header = Header()
    header.read(file)

    triForm = TriangleFormat()
    triForm.read(file)

    vertexForm = VertexFormat()
    vertexForm.read(file)

    # Let's create the mesh
    mesh = bpy.data.meshes.new(ntpath.basename(file.name))
    obj = bpy.data.objects.new(ntpath.basename(file.name), mesh)
    bpy.context.scene.objects.link(obj)
    bpy.context.scene.objects.active = obj

    mesh.vertices.add(vertexForm.vertexCount)
    for v in range(len(vertexForm.vertices)):
        mesh.vertices[v].co = vertexForm.vertices[v].positions

    print("Num triangles %i" % len(triForm.triangles))
    mesh.tessfaces.add(len(triForm.triangles))
    mesh.tessfaces.foreach_set("vertices_raw", unpack_face_list(triForm.triangles))

    if len(vertexForm.vertices[0].uvs) > 0:
        uvtex = mesh.tessface_uv_textures.new()
        uvtex.name = 'DefaultUV'
        for i, face in enumerate(mesh.tessfaces):
            uvtex.data[i].uv1 = vertexForm.vertices[face.vertices_raw[0]].uvs
            uvtex.data[i].uv2 = vertexForm.vertices[face.vertices_raw[1]].uvs
            uvtex.data[i].uv3 = vertexForm.vertices[face.vertices_raw[2]].uvs
            uvtex.data[i].uv4 = [0, 0]

    mesh.update()

    if len(vertexForm.vertices[0].normals) > 0:
        for v, vertex in enumerate(vertexForm.vertices):
            mesh.vertices[v].normal = vertex.normals

    file.close()
    return result


class Header:
    def __init__(self):
        self.version = None
        self.floatCount = 0
        self.randFloats = []  # ?
        self.bBox = None
        self.bRadius = 0
        self.unk1 = None

    def read(self, file):
        self.version = readInt(file)
        self.floatCount = readInt(file, '>') * 3
        self.randFloats = []
        for i in range(self.floatCount):
            self.randFloats.append(readFloat(file))
            
        self.unk1 = readInt(file)
        self.bBox = ((readFloat(file), readFloat(file), readFloat(file)),
                     (readFloat(file), readFloat(file), readFloat(file)))
        self.bRadius = readFloat(file)
        
        print(self.randFloats)
        print(self.bBox)
        print(self.bRadius)


class TriangleFormat:
    def __init__(self):
        self.indicesCount = 0
        self.triangles = []
        self.numTriGroups = 0

    def read(self, file):
        self.numTriGroups = readInt(file)
        print(self.numTriGroups)
        for i in range(self.numTriGroups):  # Always 1?
            expect(readInt(file), 4, "TF001", file)
            self.indicesCount = readInt(file)  # face count * 3
            readInt(file)
            readInt(file)
            #expect(readInt(file), 16, "TF002", file)
            #expect(readInt(file), self.indicesCount*2, "TF003", file)  # size

            for t in range(self.indicesCount//3):
                self.triangles.append([readUShort(file), readUShort(file), readUShort(file)])
                

class VertexFormat:
    def __init__(self):
        self.format = []
        self.fmtCount = 0
        self.meshCount = 0  # ?
        self.vertexCount = 0
        self.vertexPoolSize = 0
        self.vertices = []

    def read(self, file):
        self.meshCount = readInt(file)  # expect(readInt(file), 1, "VF001", file)
        self.fmtCount = readInt(file)
        print(self.fmtCount)

        for i in range(self.fmtCount):
            #expect(readShort(file), 0, "VF002", file)
            readShort(file)
            readShort(file)  # Offset
            readShort(file)  # Unk
            readShort(file)  # Unk
            self.format.append(self.vertexFormats[readInt(file)])
            
        if self.meshCount == 2:
            count = readInt(file)  # I thought this was another mesh, but it doesn't look like
            for h in range(count):
                readInt(file)
                readInt(file)
                readInt(file)
            
        expect(readInt(file), self.meshCount, "VF003", file)
        expect(readInt(file), 0, "VF004", file)
        
        self.vertexCount = readInt(file)
        print(self.vertexCount)
        self.vertexPoolSize = readInt(file)

        for v in range(self.vertexCount):
            self.vertices.append(VertexFormat.Vertex())
            for fmt in self.format:
                fmt(self.vertices[v], file)

    class Vertex:
        def __init__(self):
            self.positions = []
            self.normals = []
            self.tangents = []
            self.uvs = []
            self.boneIndices = []
            self.boneWeights = []

        def readPositions(self, file):
            self.positions.append(readFloat(file))
            self.positions.append(readFloat(file))
            self.positions.append(readFloat(file))

        def readNormals(self, file):
            packed = readInt(file)
            self.normals.append(UnpackNormals(packed, 0))
            self.normals.append(UnpackNormals(packed, 1))
            self.normals.append(UnpackNormals(packed, 2))

        def readTangents(self, file):
            self.tangents.append(readUInt(file))

        def readUVs(self, file):
            self.uvs.append(readFloat(file))
            self.uvs.append(0 - readFloat(file))

        def readBoneIndices(self, file):
            self.boneIndices.append(readUByte(file)//3)
            self.boneIndices.append(readUByte(file)//3)
            self.boneIndices.append(readUByte(file)//3)
            self.boneIndices.append(readUByte(file)//3)

        def readBoneWeights(self, file):
            self.boneWeights.append(readUByte(file)/255)
            self.boneWeights.append(readUByte(file)/255)
            self.boneWeights.append(readUByte(file)/255)
            self.boneWeights.append(readUByte(file)/255)

    vertexFormats = {0: Vertex.readPositions,
                     2: Vertex.readNormals,
                     6: Vertex.readUVs,
                     0x0E: Vertex.readBoneIndices,
                     0x0F: Vertex.readBoneWeights,
                     0x13: Vertex.readTangents}
