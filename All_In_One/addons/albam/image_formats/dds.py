from ctypes import Structure, sizeof, c_int, c_char, c_byte
import os

from albam.lib.structure import DynamicStructure


class DDSHeader(Structure):

    _fields_ = (('id_magic', c_char * 4),
                ('dwSize', c_int),
                ('dwFlags', c_int),
                ('dwHeight', c_int),
                ('dwWidth', c_int),
                ('dwPitchOrLinearSize', c_int),
                ('dwDepth', c_int),
                ('dwMipMapCount', c_int),
                ('dwReserved1', c_int * 11),
                ('pixelfmt_dwSize', c_int),
                ('pixelfmt_dwFlags', c_byte * 4),
                ('pixelfmt_dwFourCC', c_char * 4),
                ('pixelfmt_dwRGBBitCount', c_int),
                ('pixelfmt_dwRBitMask', c_int),
                ('pixelfmt_dwGBitMask', c_int),
                ('pixelfmt_dwBBitMask', c_int),
                ('pixelfmt_dwABitMask', c_int),
                ('dwCaps', c_int),
                ('dwCaps2', c_int),
                ('dwCaps3', c_int),
                ('dwCaps4', c_int),
                ('dwReserved2', c_int),
                )


class DDS(DynamicStructure):
    # https://msdn.microsoft.com/en-us/library/windows/desktop/bb943982
    # https://msdn.microsoft.com/en-us/library/windows/desktop/bb943984

    DDSD_CAPS = 0x1
    DDSD_HEIGHT = 0x2
    DDSD_WIDTH = 0x4
    DDSD_PITCH = 0x8
    DDSD_PIXELFORMAT = 0x1000
    DDSD_MIPMAPCOUNT = 0x20000
    DDSD_LINEARSIZE = 0x80000
    DDSD_DEPTH = 0x800000

    DDSCAPS_COMPLEX = 0x8
    DDSCAPS_MIPMAP = 0x400000
    DDSCAPS_TEXTURE = 0x1000

    DDSCAPS2_CUBEMAP = 0x200
    DDSCAPS2_CUBEMAP_POSITIVEX = 0x400
    DDSCAPS2_CUBEMAP_NEGATIVEX = 0x800
    DDSCAPS2_CUBEMAP_POSITIVEY = 0x1000
    DDSCAPS2_CUBEMAP_NEGATIVEY = 0x2000
    DDSCAPS2_CUBEMAP_POSITIVEZ = 0x4000
    DDSCAPS2_CUBEMAP_NEGATIVEZ = 0x8000
    DDSCAPS2_VOLUME = 0x200000

    REQUIRED_FLAGS = DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PIXELFORMAT

    _fields_ = (('header', DDSHeader),
                ('data', lambda s, f: c_byte * (os.path.getsize(f) - sizeof(s.header)) if f else c_byte * len(s.data)),
                )

    # TODO: set this automatically on __init__
    def set_constants(self):
        self.header.id_magic = b'DDS '
        self.header.dwSize = 124
        self.header.dwFlags = self.REQUIRED_FLAGS

        self.header.pixelfmt_dwSize = 32

        self.header.pixelfmt_dwFlags = (c_byte * 4)(4, 0, 0, 0)

        self.header.dwCaps = self.DDSCAPS_TEXTURE

    def set_variables(self):
        self.header.dwPitchOrLinearSize = self.calculate_linear_size(self.header.dwWidth,
                                                                     self.header.dwHeight,
                                                                     self.header.pixelfmt_dwFourCC)
        if self.header.dwMipMapCount:
            self.header.dwFlags |= self.DDSD_MIPMAPCOUNT
            self.header.dwCaps |= self.DDSCAPS_MIPMAP
        if self.header.dwMipMapCount:  # TODO: add 'or cubic or mipmapped_volume'
            self.header.dwCaps |= self.DDSCAPS_COMPLEX

    @property
    def mipmap_sizes(self):
        h = self.header.dwWidth
        w = self.header.dwHeight
        fmt = self.header.pixelfmt_dwFourCC
        return [self.calculate_mipmap_size(w, h, i, fmt) for i in
                range(self.header.dwMipMapCount)]

    @staticmethod
    def get_block_size(fmt):
        if fmt in (b'DXT1', b'BC1', b'BC4'):
            return 8
        elif fmt in (b'DXT3', b'DXT5'):
            return 16
        else:
            raise RuntimeError('Unrecognized format in dds: {}'.format(fmt))

    @classmethod
    def calculate_linear_size(cls, width, height, fmt):
        block_size = cls.get_block_size(fmt)
        return ((width + 3) >> 2) * ((height + 3) >> 2) * block_size

    @staticmethod
    def calculate_mipmap_size(width, height, level, fmt):
        w = max(1, width >> level)
        h = max(1, height >> level)
        w <<= 1
        h <<= 1

        size = 0

        if w > 1:
            w >>= 1
        if h > 1:
            h >>= 1
        if fmt == 'DDS_COMPRESS_NONE':
            size += (w * h) * 16  # FIXME: get real bpp
        else:
            size += ((w + 3) // 4) * ((h + 3) // 4)
            if fmt == b'DXT1' or fmt == b'DXT4':
                size *= 8
            else:
                size *= 16

        return size

    @classmethod
    def calculate_mipmap_count(cls, width, height):
        count = 1
        size = max(width, height)
        while size > 1:
            count += 1
            size = size // 2
        return count
