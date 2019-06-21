import bpy
import struct
import ntpath
from bpy_extras.io_utils import ImportHelper, unpack_face_list, unpack_list

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


def importGMSH(file):
    result = {'FINISHED'}

    model = Header()
    model.read(file)

    for me in model.meshes:
        mesh = bpy.data.meshes.new(ntpath.basename(file.name))
        obj = bpy.data.objects.new(ntpath.basename(file.name), mesh)
        bpy.context.scene.objects.link(obj)
        bpy.context.scene.objects.active = obj

        mesh.vertices.add(me.numVertices)
        mesh.vertices.foreach_set("co", unpack_list(me.positions))

        mesh.tessfaces.add(me.numTriangles)
        mesh.tessfaces.foreach_set("vertices_raw", unpack_face_list(me.triangles))

        uvtex = mesh.tessface_uv_textures.new()
        uvtex.name = 'DefaultUV'
        if len(me.UVs) > 0:
            for v, face in enumerate(mesh.tessfaces):
                uvtex.data[v].uv1 = me.UVs[face.vertices_raw[0]]
                uvtex.data[v].uv2 = me.UVs[face.vertices_raw[1]]
                uvtex.data[v].uv3 = me.UVs[face.vertices_raw[2]]
                uvtex.data[v].uv4 = [0, 0]

        mesh.update()

        if len(me.normals) > 0:
            mesh.vertices.foreach_set("normal", unpack_list(me.normals))

    file.close()

    return result


class Header:
    def __init__(self):
        self.blockCount = 0
        self.meshes = []
        self.positions = []
        self.normals = []
        self.UVs = []
        self.tangents = []
        self.triangles = []
        self.numVertices = 0
        self.numTriangles = 0

    def read(self, file):
        expect(readInt(file, '>'), 1, "H001", file)
        expect(readInt(file, '>'), 1, "H001", file)
        readInt(file)
        self.blockCount = readUShort(file, '>')

        for i in range(self.blockCount):
            print(hex(file.tell()))
            itemType = readShort(file)
            print(str(type))
            readInt(file)
            itemCt = readUShort(file, '>')
            itemSz = readUShort(file, '>')

            if itemType == 1:
                self.numVertices = itemCt
                for p in range(itemCt):
                    self.positions.append([readFloat(file), readFloat(file), readFloat(file)])

            elif itemType == 2:
                for n in range(itemCt):
                    packedNm = readInt(file)
                    self.normals.append([UnpackNormals(packedNm, 0),
                                         UnpackNormals(packedNm, 1),
                                         UnpackNormals(packedNm, 2)])

            elif itemType == 3:
                for t in range(itemCt):
                    packedTg = readInt(file)  # TODO ?

            elif itemType == 8:
                for u in range(itemCt):
                    self.UVs.append([readFloat(file), 0 - readFloat(file)])

            elif itemType == 21:
                # readInt(file) ?
                # type = readShort(file)
                # print(str(type))
                # readInt(file)
                # itemCt = readUShort(file, '>')
                # itemSz = readUShort(file, '>')
                self.numTriangles = itemCt//3
                for x in range(self.numTriangles):
                    self.triangles.append([readUShort(file), readUShort(file), readUShort(file)])
