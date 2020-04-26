from enum import IntEnum
from typing import List

from .ValveFileSystem.byte_io import ByteIO


class VTF_FLAGS:
    POINTSAMPLE = 0x00000001,
    TRILINEAR = 0x00000002,
    CLAMPS = 0x00000004,
    CLAMPT = 0x00000008,
    ANISOTROPIC = 0x00000010,
    HINT_DXT5 = 0x00000020,
    SRGB = 0x00000040,
    DEPRECATED_NOCOMPRESS = 0x00000040,
    NORMAL = 0x00000080,
    NOMIP = 0x00000100,
    NOLOD = 0x00000200,
    MINMIP = 0x00000400,
    PROCEDURAL = 0x00000800,
    ONEBITALPHA = 0x00001000,
    EIGHTBITALPHA = 0x00002000,
    ENVMAP = 0x00004000,
    RENDERTARGET = 0x00008000,
    DEPTHRENDERTARGET = 0x00010000,
    NODEBUGOVERRIDE = 0x00020000,
    SINGLECOPY = 0x00040000,
    UNUSED0 = 0x00080000,
    DEPRECATED_ONEOVERMIPLEVELINALPHA = 0x00080000,
    UNUSED1 = 0x00100000,
    DEPRECATED_PREMULTCOLORBYONEOVERMIPLEVEL = 0x00100000,
    UNUSED2 = 0x00200000,
    DEPRECATED_NORMALTODUDV = 0x00200000,
    UNUSED3 = 0x00400000,
    DEPRECATED_ALPHATESTMIPGENERATION = 0x00400000,
    NODEPTHBUFFER = 0x00800000,
    UNUSED4 = 0x01000000,
    DEPRECATED_NICEFILTERED = 0x01000000,
    CLAMPU = 0x02000000,
    VERTEXTEXTURE = 0x04000000,
    SSBUMP = 0x08000000,
    UNUSED5 = 0x10000000,
    DEPRECATED_UNFILTERABLE_OK = 0x10000000,
    BORDER = 0x20000000,
    DEPRECATED_SPECVAR_RED = 0x40000000,
    DEPRECATED_SPECVAR_ALPHA = 0x80000000,
    LAST = 0x20000000,
    @staticmethod
    def get_flags(value):
        flags = []
        vars_ = {var: VTF_FLAGS.__dict__[var] for var in vars(
            VTF_FLAGS) if not var.startswith('_') and var.isupper()}
        for var, int_ in vars_.items():
            if (value & int_[0]) > 0:
                flags.append(var)
        return flags


class VTF_FORMATS(IntEnum):
    RGBA8888 = 0
    ABGR8888 = 1
    RGB888 = 2
    BGR888 = 3
    RGB565 = 4
    I8 = 5
    IA88 = 6
    P8 = 7
    A8 = 8
    RGB888_BLUESCREEN = 9
    BGR888_BLUESCREEN = 10
    ARGB8888 = 11
    BGRA8888 = 12
    DXT1 = 13
    DXT3 = 14
    DXT5 = 15
    BGRX8888 = 16
    BGR565 = 17
    BGRX5551 = 18
    BGRA4444 = 19
    DXT1_ONEBITALPHA = 20
    BGRA5551 = 21
    UV88 = 22
    UVWQ8888 = 23
    RGBA16161616F = 24
    RGBA16161616 = 25
    UVLX8888 = 26
    R32F = 27
    RGB323232F = 28
    RGBA32323232F = 29
    NV_DST16 = 30
    NV_DST24 = 31
    NV_INTZ = 32
    NV_RAWZ = 33
    ATI_DST16 = 34
    ATI_DST24 = 35
    NV_NULL = 36
    ATI2N = 37


class VTF_HEADER:
    def __init__(self):
        self.signature = []  # type: List[str]*4
        self.version = []  # type: List[int]*2
        self.header_size = 0
        self.width = 0
        self.height = 0
        self.flags = 0
        self.frames = 0
        self.first_frame = 0
        self.padding0 = []  # type: List[int]*4
        self.reflectivity = []  # type: List[int]*3
        self.padding1 = []  # type: List[int]*4
        self.bumpmap_scale = 0.0
        self.mipmap_count = 0
        self.high_res_image_format = 0
        self.low_res_image_format = 0
        self.low_res_image_width = 0
        self.low_res_image_height = 0
        self.depth = 1
        self.padding2 = []  # type: List[int]*3
        self.numResources = 0

    def __repr__(self):
        return "<VTF v{0[0]}.{0[1]} size:{1}x{2} format:{3}>".format(
            self.version, self.width, self.height, VTF_FORMATS(self.high_res_image_format).name)

    def read(self, reader: ByteIO):
        self.signature = reader.read_fourcc()
        self.version = [reader.read_uint32(), reader.read_uint32()]
        self.header_size = reader.read_uint32()
        self.width = reader.read_uint16()
        self.height = reader.read_uint16()
        self.flags = reader.read_uint32()
        self.frames = reader.read_uint16()
        self.first_frame = reader.read_uint16()
        self.padding0 = reader.read_bytes(4)
        self.reflectivity = [reader.read_float() for _ in range(3)]
        self.padding1 = reader.read_bytes(4)
        self.bumpmap_scale = reader.read_float()
        self.high_res_image_format = reader.read_uint32()
        self.mipmap_count = reader.read_uint8()
        self.low_res_image_format = reader.read_uint32()
        self.low_res_image_width = reader.read_uint8()
        self.low_res_image_height = reader.read_uint8()
        self.depth = reader.read_uint16()
        self.padding2 = reader.read_bytes(3)
        self.numResources = reader.read_uint32()
