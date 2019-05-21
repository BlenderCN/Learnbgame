import logging; log = logging.getLogger(__name__)
import struct
from .base import BCn, TextureFormat, unpackRGB565, clamp


class BC1(TextureFormat, BCn):
    id = 0x1A
    bytesPerPixel = 8


    def decode(self, tex):
        decode  = self.decodePixel
        bpp     = self.bytesPerPixel
        data    = tex.data
        width   = int((tex.width  + 3) / 4)
        height  = int((tex.height + 3) / 4)
        pixels  = bytearray(width * height * 64)
        swizzle = tex.swizzle.getOffset

        #log.debug("BC1: %s, %d bytes/pixel, %dx%d = %d, len = %d",
        #    tex.name,
        #    bpp, width, height, width * height * bpp,
        #    len(data))

        for y in range(height):
            for x in range(width):
                offs = swizzle(x, y)
                tile = self.decodeTile(data, offs)

                toffs = 0
                for ty in range(4):
                    for tx in range(4):
                        out = (x*4 + tx + (y * 4 + ty) * width * 4) * 4
                        pixels[out : out+4] = tile[toffs : toffs+4]
                        toffs += 4

        return pixels, self.depth


    # BC1 uses different LUT calculations than other BC formats
    def calcCLUT2(self, lut0, lut1, c0, c1):
        if c0 > c1:
            r = int((2 * lut0[0] + lut1[0]) / 3)
            g = int((2 * lut0[1] + lut1[1]) / 3)
            b = int((2 * lut0[2] + lut1[2]) / 3)
        else:
            r = (lut0[0] + lut1[0]) >> 1
            g = (lut0[1] + lut1[1]) >> 1
            b = (lut0[2] + lut1[2]) >> 1
        return r, g, b, 0xFF


    def calcCLUT3(self, lut0, lut1, c0, c1):
        if c0 > c1:
            r = int((2 * lut0[0] + lut1[0]) / 3)
            g = int((2 * lut0[1] + lut1[1]) / 3)
            b = int((2 * lut0[2] + lut1[2]) / 3)
            return r, g, b, 0xFF
        else:
            return 0, 0, 0, 0
