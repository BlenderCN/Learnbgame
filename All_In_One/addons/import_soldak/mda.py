# MDA format

import os
import sys
import struct
from collections import namedtuple

HEADER_FORMAT = '<iiii' + ('i' * 3)
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

Header = namedtuple('Header', ['id', 'version', 'numFrames', 'numBones', 'offsetBonePos', 'offsetSec2', 'offsetModelPos'])

def read_header(file):
    str = file.read(HEADER_SIZE)
    return Header._make(struct.unpack(HEADER_FORMAT, str))

Pos = namedtuple('Pos', ['orientation', 'location'])
POS_FORMAT = '<' + ('f' * 7)
POS_SIZE = struct.calcsize(POS_FORMAT)

def read_pos(file):
    str = file.read(POS_SIZE)
    bp = struct.unpack(POS_FORMAT, str)
    return Pos((bp[0], bp[1], bp[2], bp[3]), (bp[4], bp[5], bp[6]))

SEC2_FORMAT = '<iii'
SEC2_SIZE = struct.calcsize(SEC2_FORMAT)

def read_sec2(file):
    str = file.read(SEC2_SIZE)
    sec2 = struct.unpack(SEC2_FORMAT, str)
    return sec2

if __name__ == '__main__':
    filename = sys.argv[1]
    file_len = os.stat(filename + '.mda').st_size
    with open(filename + '.mda', 'rb') as f:
        header = read_header(f)
        print("Header: ", header)
        print("File len: ", file_len)
        f.seek(header.offsetBonePos)
        for i in range(header.numFrames):
            print("Frame ", i, ":")
            for bone in range(header.numBones):
                pos = read_pos(f)
                print("Bone ", bone, ": ", pos)
        f.seek(header.offsetSec2)
        for i in range(header.numFrames):
            sec2 = read_sec2(f)
            print ("Frame ", i, ": ", sec2)
        f.seek(header.offsetModelPos)
        for i in range(header.numFrames):
            pos = read_pos(f)
            print("Frame: ", i, ": ", pos)

