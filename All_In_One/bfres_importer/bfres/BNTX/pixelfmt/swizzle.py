# This file is part of botwtools.
#
# botwtools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# botwtools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with botwtools.  If not, see <https://www.gnu.org/licenses/>.
import logging; log = logging.getLogger(__name__)
import struct
import math


def countLsbZeros(val):
    cnt = 0
    while ((val >> cnt) & 1) == 0: cnt += 1
    return cnt


class Swizzle:
    def __init__(self, width, bpp, blkHeight=16):
        self.width = width
        self.bpp   = bpp

    def getOffset(self, x, y):
        return (y * self.width) + x


class BlockLinearSwizzle(Swizzle):
    def __init__(self, width, bpp, blkHeight=16):
        self.bhMask    = (blkHeight * 8) - 1
        self.bhShift   = countLsbZeros(blkHeight * 8)
        self.bppShift  = countLsbZeros(bpp)
        widthGobs      = math.ceil(width * bpp / 64.0)
        self.gobStride = 512 * blkHeight * widthGobs
        self.xShift    = countLsbZeros(512 * blkHeight)

    def getOffset(self, x, y):
        x <<= self.bppShift
        return (
            ((y >> self.bhShift) * self.gobStride) +
            ((x >> 6) << self.xShift) +
            (((y & self.bhMask) >> 3) << 9) +
            (((x & 0x3F) >> 5) << 8) +
            (((y & 0x07) >> 1) << 6) +
            (((x & 0x1F) >> 4) << 5) +
            ( (y & 0x01)       << 4) +
            (  x & 0x0F)
        )
