import struct


class Chunks:
    OGF_HEADER      = 0x1
    OGF4_S_DESC     = 0x12
    OGF4_CHILDREN   = 0x9
    OGF4_TEXTURE    = 0x2
    OGF4_VERTICES   = 0x3
    OGF4_INDICES    = 0x4


class rawr:
    def __init__(self, data):
        self.__offs = 0
        self.__data = data

    def unpack(self, fmt):
        s = struct.calcsize(fmt)
        self.__offs += s
        return struct.unpack_from(fmt, self.__data, self.__offs - s)

    def unpack_asciiz(self):
        zpos = self.__data.find(0, self.__offs)
        if zpos == -1:
            zpos = len(self.__data)
        return self.unpack('={}sx'.format(zpos - self.__offs))[0].decode('cp1251')


def ogfr(data):
    MASK_COMPRESSED = 0x80000000
    offs = 0
    while offs < len(data):
        i, s = struct.unpack_from('=II', data, offs)
        if (i & MASK_COMPRESSED) != 0:
            raise Exception('compressed')
        offs += 8 + s
        yield (i & ~MASK_COMPRESSED, data[offs-s:offs])


def cfrs(tupl, expected):
    if tupl[0] != expected:
        raise Exception('expected {}, but found: {}'.format(expected, tupl[0]))
    return tupl[1]
