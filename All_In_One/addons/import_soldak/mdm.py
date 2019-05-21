# MDM Format

import struct
from collections import namedtuple

HEADER_FORMAT = '<' + ('i' * 10)
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

Header = namedtuple('Header', ['id', 'version', 'numSurfaces',
        'numTris', 'numVerts', 'surfaceOffset', 'trisOffset', 'vertsOffset',
        'weightsOffset', 'collapseMappingsOffset'])

def read_header(file):
    str = file.read(HEADER_SIZE)
    return Header._make(struct.unpack(HEADER_FORMAT, str))

SURFACE_FORMAT = '<' + ('i' * 6)
SURFACE_SIZE = struct.calcsize(SURFACE_FORMAT)
Surface = namedtuple('Surface', ['surfaceNumber', 'numVerts', 'numTris',
        'vertsOffset', 'trisOffset', 'collapseMappingsOffset'])

def read_surface(file):
    str = file.read(SURFACE_SIZE)
    return Surface._make(struct.unpack(SURFACE_FORMAT, str))

TRI_FORMAT = '<' + ('i' * 3)
TRI_SIZE = struct.calcsize(TRI_FORMAT)

def read_tri(file):
    str = file.read(TRI_SIZE)
    return struct.unpack(TRI_FORMAT, str)

VERT_FORMAT = '<' + ('f' * 2) + ('f' * 3) + ('f' * 4) + ('i' * 2)
VERT_SIZE = struct.calcsize(VERT_FORMAT)

Vert = namedtuple('Vert', ['u', 'v', 'normal', 'tangent', 'numBones', 'firstBone'])

def read_vert(file):
    str = file.read(VERT_SIZE)
    data = struct.unpack(VERT_FORMAT, str)
    v = Vert(data[0], data[1], (data[2], data[3], data[4]), (data[5], data[6], data[7], data[8]), data[9], data[10])
    return v

VERTBONE_FORMAT = '<i' + ('f' * 4)
VERTBONE_SIZE = struct.calcsize(VERTBONE_FORMAT)

VertBone = namedtuple('VertBone', ['boneIndex', 'vertOffset', 'boneWeight'])

def read_vertbone(file):
    str = file.read(VERTBONE_SIZE)
    data = struct.unpack(VERTBONE_FORMAT, str)
    vb = VertBone(data[0], (data[1], data[2], data[3]), data[4])
    return vb

if __name__ == '__main__':
    filename = sys.argv[1]
    with open(filename + '.mdm', 'rb') as f:
        header = read_header(f)
        print("Header: ", header)
        print("vertsOffset: {:x}".format(header.vertsOffset))

        f.seek(header.surfaceOffset)
        for surf_num in range(header.numSurfaces):
            surface = read_surface(f)
            print("Surface ", surf_num, " :", surface)

        tris = {}

        f.seek(header.trisOffset)
        for i in range(header.numTris):
            tri = read_tri(f)
            if tri in tris:
                print("Tri {} matches tri {}!!!".format(i, tris[tri]))
            tris[tri] = i
            print("Tri ", i, " :", tri)

        # Vertices ---
        f.seek(header.vertsOffset)
        for vert_num in range(header.numVerts):
            vert = read_vert(f)
            print("Vertice ", vert_num, " :", vert)

        f.seek(header.weightsOffset)
        for vb_num in range(header.numVerts):
            vb = read_vertbone(f)
            print("VertBone ", vb_num, " :", vb)
