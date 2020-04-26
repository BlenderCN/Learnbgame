import logging; log = logging.getLogger(__name__)
import struct
from .base import BCn, TextureFormat, unpackRGB565, clamp


class BC5(TextureFormat, BCn):
    id = 0x1E
    bytesPerPixel = 16


    def decode(self, tex):
        decode   = self.decodePixel
        bpp      = self.bytesPerPixel
        data     = tex.data
        width    = int((tex.width  + 3) / 4)
        height   = int((tex.height + 3) / 4)
        pixels   = bytearray(width * height * 64)
        swizzle  = tex.swizzle.getOffset
        is_snorm = tex.fmt_dtype.name == 'SNorm'

        for y in range(height):
            for x in range(width):
                offs    = swizzle(x, y)
                red     = self.calcAlpha(data[offs : offs+2], tex)
                redCh   = struct.unpack('Q', red)[0]
                green   = self.calcAlpha(data[offs+8 : offs+10], tex)
                greenCh = struct.unpack('Q', green)[0]

                toffs = 0
                if is_snorm:
                    for ty in range(4):
                        for tx in range(4):
                            shift = ty * 12 + tx * 3
                            out = (x*4 + tx + (y*4 + ty)*width*4)*4
                            r   = red  [(redCh   >> shift) & 7] + 0x80
                            g   = green[(greenCh >> shift) & 7] + 0x80
                            nx = (r / 255.0) * 2 - 1
                            ny = (g / 255.0) * 2 - 1
                            nz = math.sqrt(1 - (nx*nx + ny*ny))
                            pixels[out : out+4] = (
                                clamp((nz+1) * 0.5),
                                clamp((ny+1) * 0.5),
                                clamp((nx+1) * 0.5),
                                0xFF)
                            toffs += 4
                else:
                    for ty in range(4):
                        for tx in range(4):
                            shift = ty * 12 + tx * 3
                            out = (x*4 + tx + (y*4 + ty)*width*4)*4
                            r   = red  [(redCh   >> shift) & 7]
                            g   = green[(greenCh >> shift) & 7]
                            pixels[out : out+4] = (r, r, r, g)
                            toffs += 4

        return pixels, self.depth


    def calcAlpha(self, alpha, tex):
        if tex.fmt_dtype.name != 'SNorm':
            return super().calcAlpha(alpha)

        a0, a1 = alpha[0], alpha[1]
        d = (a0, a1, 0, 0, 0, 0, 0x80, 0x7F)
        alpha = bytearray(bytes(d))
        for i in range(2, 6):
            # XXX do we need to cast here?
            if a0 > a1:
                alpha[i] = int(((8-i) * a0 + (i-1) * a1) / 7)
            else:
                alpha[i] = int(((6-i) * a0 + (i-1) * a1) / 7)
        return alpha
