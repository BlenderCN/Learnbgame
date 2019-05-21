import logging; log = logging.getLogger(__name__)
import struct
from .base import BCn, TextureFormat, unpackRGB565, clamp


class BC2(TextureFormat, BCn):
    id = 0x1B
    bytesPerPixel = 16


    def decode(self, tex):
        decode  = self.decodePixel
        bpp     = self.bytesPerPixel
        data    = tex.data
        width   = int((tex.width  + 3) / 4)
        height  = int((tex.height + 3) / 4)
        pixels  = bytearray(width * height * 64)
        swizzle = tex.swizzle.getOffset

        for y in range(height):
            for x in range(width):
                offs    = swizzle(x, y)
                tile    = self.decodeTile(data, offs)
                alphaCh = struct.unpack_from('Q', data, offs)[0]

                toffs = 0
                for ty in range(4):
                    for tx in range(4):
                        alpha = (alphaCh >> (ty * 16 + tx * 4)) & 0xF
                        out = (x*4 + tx + (y * 4 + ty) * width * 4) * 4
                        pixels[out : out+3] = tile[toffs : toffs+3]
                        pixels[out+3] = alpha | (alpha << 4)
                        toffs += 4

        return pixels, self.depth
