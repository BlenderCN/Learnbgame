import struct
import array
from . import s3tc
from .io import unpack

'''
https://github.com/jsj2008/lithtech/blob/master/libs/dtxmgr/dtxmgr_lib.h
'''

RESOURCE_TYPE_DTX = 0
RESOURCE_TYPE_MODEL = 1
RESOURCE_TYPE_SPRITE = 2

DTX_FULLBRITE       = (1 << 0)  # This DTX has fullbrite colors.
DTX_PREFER16BIT     = (1 << 1)  # Use 16-bit, even if in 32-bit mode.
DTX_MIPSALLOCED     = (1 << 2)  # Used to make some of the tools stuff easier..this means each TextureMipData has its texture data allocated.
DTX_SECTIONSFIXED   = (1 << 3)  # The sections count was screwed up originally.  This flag is set in all the textures from now on when the count is fixed.
DTX_NOSYSCACHE      = (1 << 6)  # tells it to not put the texture in the texture cache list.
DTX_PREFER4444      = (1 << 7)  # If in 16-bit mode, use a 4444 texture for this.
DTX_PREFER5551      = (1 << 8)  # Use 5551 if 16-bit.
DTX_32BITSYSCOPY    = (1 << 9)  # If there is a sys copy - don't convert it to device specific format (keep it 32 bit).
DTX_CUBEMAP         = (1 << 10) # Cube environment map.  +x is stored in the normal data area, -x,+y,-y,+z,-z are stored in their own sections
DTX_BUMPMAP         = (1 << 11) # Bump mapped texture, this has 8 bit U and V components for the bump normal
DTX_LUMBUMPMAP      = (1 << 12) # Bump mapped texture with luminance, this has 8 bits for luminance, U and V
DTX_FLAGSAVEMASK    = (DTX_FULLBRITE | DTX_32BITSYSCOPY | DTX_PREFER16BIT | DTX_SECTIONSFIXED | DTX_PREFER4444 | DTX_PREFER5551 | DTX_CUBEMAP | DTX_BUMPMAP | DTX_LUMBUMPMAP | DTX_NOSYSCACHE)

DTX_FLAG_NAMES = [
    (DTX_FULLBRITE, 'FULLBRITE'),
    (DTX_PREFER16BIT, 'PREFER16BIT'),
    (DTX_MIPSALLOCED, 'MIPSALLOCED'),
    (DTX_SECTIONSFIXED, 'SECTIONSFIXED'),
    (DTX_NOSYSCACHE, 'NOSYSCACHE'),
    (DTX_PREFER4444, 'PREFER4444'),
    (DTX_PREFER5551, 'PREFER5551'),
    (DTX_32BITSYSCOPY, '32BITSYSCOPY'),
    (DTX_CUBEMAP, 'CUBEMAP'),
    (DTX_BUMPMAP, 'BUMPMAP'),
    (DTX_LUMBUMPMAP, 'LUMBUMPMAP')
]

DTX_COMMANDSTRING_LENGTH = 128

BPP_8P = 0
BPP_8 = 1
BPP_16 = 2
BPP_32 = 3
BPP_S3TC_DXT1 = 4
BPP_S3TC_DXT3 = 5
BPP_S3TC_DXT5 = 6
BPP_32P = 7

bpp_names = [
    'BPP_8P',
    'BPP_8',
    'BPP_16',
    'BPP_32',
    'BPP_S3TC_DXT1',
    'BPP_S3TC_DXT3',
    'BPP_S3TC_DXT5',
    'BPP_32P'
]


class SectionHeader(object):
    def __init__(self, f):
        self.type = f.read(15)
        self.name = f.read(10)
        self.data_length = unpack('I', f)[0]    # Data length, not including SectionHeader.


class DTX(object):

    def __init__(self, path):
        with open(path, 'rb') as f:
            resource_type = unpack('I', f)[0]
            if resource_type != RESOURCE_TYPE_DTX:
                f.seek(0, 0)
            else:
                version, self.height, self.width = unpack('i2H', f)
            self.mipmap_count, self.section_count, self.flags, self.user_flags = unpack('2H2I', f)
            self.extra_data = unpack('12B', f)
            self.command_string = f.read(DTX_COMMANDSTRING_LENGTH)
            if self.bpp_identifier == BPP_8:
                # TODO: probably not right
                self.pixels = list(f.read(self.width * self.height * 4))
            elif self.bpp_identifier == BPP_8P:
                self.pixels = list(f.read(self.width * self.height * 4))
                for i in range(0, len(self.pixels), 4):
                    self.pixels[i], self.pixels[i + 2] = self.pixels[i + 2], self.pixels[i]
                    self.pixels[i + 3] = 255
            elif self.bpp_identifier == BPP_16:
                raise NotImplementedError()
            elif self.bpp_identifier == BPP_32:
                self.pixels = list(f.read(self.width * self.height * 4))
                for i in range(0, len(self.pixels), 4):
                    self.pixels[i], self.pixels[i + 2] = self.pixels[i + 2], self.pixels[i]
                    self.pixels[i + 3] = 255  # TODO: the alpha channel seems to be used for various things
            elif self.bpp_identifier == BPP_S3TC_DXT1:
                self.pixels = s3tc.decompress(s3tc.DXT1, self.width, self.height, f)
            elif self.bpp_identifier == BPP_S3TC_DXT3:
                self.pixels = s3tc.decompress(s3tc.DXT3, self.width, self.height, f)
            elif self.bpp_identifier == BPP_S3TC_DXT5:
                self.pixels = s3tc.decompress(s3tc.DXT5, self.width, self.height, f)

    @property
    def texture_group(self):
        return self.extra_data[0]

    @property
    def mipmaps_to_use(self):
        return self.extra_data[1]

    @property
    def bpp_identifier(self):
        return self.extra_data[2]

    @property
    def mipmap_offset(self):
        return self.extra_data[3]

    @property
    def mipmap_texcoord_offset(self):
        return self.extra_data[4]

    @property
    def texture_priority(self):
        return self.extra_data[5]

    @property
    def detail_texture_scale(self):
        return struct.unpack_from('>f', array.array('B', self.extra_data[6:10]))

    @property
    def detail_texture_angle(self):
        return struct.unpack_from('H', array.array('B', self.extra_data[10:]))