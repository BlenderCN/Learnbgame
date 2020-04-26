import logging; log = logging.getLogger(__name__)
import struct
from .base import BCn, TextureFormat, unpackRGB565, clamp


class BC3(TextureFormat, BCn):
    id = 0x1C
    bytesPerPixel = 16


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
                offs    = swizzle(x, y)
                tile    = self.decodeTile(data, offs)
                alpha   = self.calcAlpha(data[offs : offs+2])
                alphaCh = struct.unpack('Q', alpha)[0]

                toffs = 0
                for ty in range(4):
                    for tx in range(4):
                        out = (x*4 + tx + (y * 4 + ty) * width * 4) * 4
                        pixels[out : out+3] = tile[toffs : toffs+3]
                        pixels[out+3] = \
                            alpha[(alphaCh >> (ty * 12 + tx * 3)) & 7]
                        toffs += 4

        return pixels, self.depth
