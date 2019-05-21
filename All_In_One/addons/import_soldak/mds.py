# MDS format

import os
import sys
import struct
from collections import namedtuple

HEADER_FORMAT = '<iii'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

Header = namedtuple('Header', ['id', 'x', 'numBones'])

def read_header(file):
    str = file.read(HEADER_SIZE)
    return Header._make(struct.unpack(HEADER_FORMAT, str))

BONE_FORMAT = '<ii'
BONE_SIZE = struct.calcsize(BONE_FORMAT)

Bone = namedtuple('Bone', ['joint', 'str'])

def read_bone(file):
    str = file.read(BONE_SIZE)
    return Bone._make(struct.unpack(BONE_FORMAT, str))

def read_bones(f):
    header = read_header(f)
    #print("Header: ", header)

    bone_data = []
    for _ in range(header.numBones):
        bone_data.append(read_bone(f))
        #print("Bone: ", bone_data)

    strLengths = []
    for i, bd in enumerate(bone_data[1:]):
        strLengths.append(bd.str - bone_data[i].str)
    strLengths.append(file_len - bd.str)
    #print("strLengths: ", strLengths)

    bone_data2 = []
    for i, bd in enumerate(bone_data):
        str = f.read(strLengths[i])
        bone_data2.append(Bone(bd.joint, str[:-1]))
    #print("Bone data: ", bone_data2)
    return bone_data2

if __name__ == '__main__':
    filename = sys.argv[1]
    file_len = os.stat(filename + '.mds').st_size
    with open(filename + '.mds', 'rb') as f:
        data = read_bones(f)
    print("Num bones: ", len(data), " Bones: ", data)



