import logging; log = logging.getLogger(__name__)
import struct
from .base import BCn, TextureFormat, unpackRGB565, clamp


class BC4(TextureFormat, BCn):
    id = 0x1D
    bytesPerPixel = 8


    def decode(self, tex):
        decode = self.decodePixel
        bpp    = self.bytesPerPixel
        data   = tex.data
        width  = int((tex.width  + 3) / 4)
        height = int((tex.height + 3) / 4)
        pixels = bytearray(width * height * 64)
        swizzle = tex.swizzle.getOffset

        for y in range(height):
            for x in range(width):
                offs  = swizzle(x, y)
                red   = self.calcAlpha(data[offs : offs+2])
                # read two extra bytes here, but we won't use them
                redCh = struct.unpack('Q', data[offs+2 : offs+10])[0]

                toffs = 0
                for ty in range(4):
                    for tx in range(4):
                        out = (x*4 + tx + (y * 4 + ty) * width * 4) * 4
                        r   = red[(redCh >> (ty * 12 + tx * 3)) & 7]
                        pixels[out : out+4] = (r, r, r, 0xFF)
                        toffs += 4

        return pixels, self.depth
