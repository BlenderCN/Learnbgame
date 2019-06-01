import logging; log = logging.getLogger(__name__)
from bfres.BinaryStruct import BinaryStruct, BinaryObject
from bfres.BinaryStruct.Padding import Padding
from bfres.BinaryStruct.StringOffset import StringOffset
from bfres.BinaryStruct.Switch import Offset32, Offset64, String
from bfres.BinaryFile import BinaryFile
from bfres.Common import StringTable
from enum import IntEnum
from .pixelfmt import TextureFormat
from .pixelfmt.swizzle import Swizzle, BlockLinearSwizzle


class Header(BinaryStruct):
    """BRTI object header."""
    magic  = b'BRTI'
    fields = (
        ('4s',   'magic'),
        ('I',    'length'),
        ('Q',    'length2'),
        ('B',    'flags'),
        ('B',    'dimensions'),
        ('H',    'tile_mode'),
        ('H',    'swizzle_size'),
        ('H',    'mipmap_cnt'),
        ('H',    'multisample_cnt'),
        ('H',    'reserved1A'),
        ('B',    'fmt_dtype', lambda v: BRTI.TextureDataType(v)),
        ('B',    'fmt_type',  lambda v: TextureFormat.get(v)()),
        Padding(2),
        ('I',    'access_flags'),
        ('i',    'width'),
        ('i',    'height'),
        ('i',    'depth'),
        ('i',    'array_cnt'),
        ('i',    'block_height', lambda v: 2**v),
        ('H',    'unk38'),
        ('H',    'unk3A'),
        ('i',    'unk3C'),
        ('i',    'unk40'),
        ('i',    'unk44'),
        ('i',    'unk48'),
        ('i',    'unk4C'),
        ('i',    'data_len'),
        ('i',    'alignment'),
        ('4B',   'channel_types',lambda v:tuple(map(BRTI.ChannelType,v))),
        ('i',    'tex_type'),
        String(  'name'),
        Padding(4),
        Offset64('parent_offset'),
        Offset64('ptrs_offset'),
    )


class BRTI:
    """A BRTI in a BNTX."""
    Header = Header

    class ChannelType(IntEnum):
        Zero  = 0
        One   = 1
        Red   = 2
        Green = 3
        Blue  = 4
        Alpha = 5

    class TextureType(IntEnum):
        Image1D = 0
        Image2D = 1
        Image3D = 2
        Cube    = 3
        CubeFar = 8

    class TextureDataType(IntEnum):
        UNorm  = 1
        SNorm  = 2
        UInt   = 3
        SInt   = 4
        Single = 5
        SRGB   = 6
        UHalf  = 10

    def __init__(self):
        self.file       = None
        self.mipOffsets = []


    def dump(self):
        """Dump to string for debug."""
        res = []
        res.append("BRTI Name:     '%s'" % self.name)
        res.append("Length:          0x%06X / 0x%06X" % (
            self.header['length'], self.header['length2']))
        res.append("Flags:           0x%02X" % self.header['flags'])
        res.append("Dimensions:      0x%02X" % self.header['dimensions'])
        res.append("Tile Mode:       0x%04X" % self.header['tile_mode'])
        res.append("Swiz Size:       0x%04X" % self.header['swizzle_size'])
        res.append("Mipmap Cnt:      0x%04X" % self.header['mipmap_cnt'])
        res.append("Multisample Cnt: 0x%04X" % self.header['multisample_cnt'])
        res.append("Reserved 1A:     0x%04X" % self.header['reserved1A'])
        res.append("Fmt Data Type:   %2d %s" % (
            int(self.header['fmt_dtype']),
            self.header['fmt_dtype'].name))
        res.append("Fmt Type:        %2d %s" % (
            self.header['fmt_type'].id,
            type(self.header['fmt_type']).__name__))
        res.append("Access Flags:    0x%08X" % self.header['access_flags'])
        res.append("Width x Height:  %5d/%5d" % (self.width, self.height))
        res.append("Depth:           %3d" % self.header['depth'])
        res.append("Array Cnt:       %3d" % self.header['array_cnt'])
        res.append("Block Height:    %8d" % self.header['block_height'])
        res.append("Unk38:           %04X %04X" % (
            self.header['unk38'], self.header['unk3A']))
        res.append("Unk3C:           %d, %d, %d, %d, %d" % (
            self.header['unk3C'], self.header['unk40'],
            self.header['unk44'], self.header['unk48'],
            self.header['unk4C']))
        res.append("Data Len:        0x%08X" % self.header['data_len'])
        res.append("Alignment:       0x%08X" % self.header['alignment'])
        res.append("Channel Types:   %s, %s, %s, %s" % (
            self.header['channel_types'][0].name,
            self.header['channel_types'][1].name,
            self.header['channel_types'][2].name,
            self.header['channel_types'][3].name))
        res.append("Texture Type:    0x%08X" % self.header['tex_type'])
        res.append("Parent Offs:     0x%08X" % self.header['parent_offset'])
        res.append("Ptrs Offs:       0x%08X" % self.header['ptrs_offset'])
        return '\n'.join(res).replace('\n', '\n  ')


    def readFromFile(self, file:BinaryFile, offset=0):
        """Decode objects from the file."""
        self.file          = file
        self.header        = self.Header().readFromFile(file, offset)
        self.name          = self.header['name']
        self.fmt_type      = self.header['fmt_type']
        self.fmt_dtype     = self.header['fmt_dtype']
        self.width         = self.header['width']
        self.height        = self.header['height']
        self.channel_types = self.header['channel_types']

        self.swizzle = BlockLinearSwizzle(self.width,
            self.fmt_type.bytesPerPixel,
            self.header['block_height'])
        self._readMipmaps()
        self._readData()
        self.pixels, self.depth = self.fmt_type.decode(self)
        return self


    def _readMipmaps(self):
        """Read the mipmap images."""
        for i in range(self.header['mipmap_cnt']):
            offs  = self.header['ptrs_offset'] + (i*8)
            entry = self.file.read('I', offs) #- base
            self.mipOffsets.append(entry)


    def _readData(self):
        """Read the raw image data."""
        base = self.file.read('Q', self.header['ptrs_offset'])
        self.data = self.file.read(self.header['data_len'], base)
