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
from .base import TextureFormat


class R5G6B5(TextureFormat):
    id = 0x07
    bytesPerPixel = 2

    def decodePixel(self, pixel):
        pixel = struct.unpack('H', pixel)
        r =  (pixel        & 0x1F) << 3
        g = ((pixel >>  5) & 0x3F) << 2
        b = ((pixel >> 11) & 0x1F) << 3
        a = 0xFF
        return r, g, b, a


class R8G8(TextureFormat):
    id = 0x09
    bytesPerPixel = 2

    def decodePixel(self, pixel):
        pixel = struct.unpack('H', pixel)
        r =  (pixel        & 0xFF)
        g = ((pixel >>  8) & 0xFF)
        b = ((pixel >> 11) & 0x1F) << 3
        a = 0xFF
        return r, g, b, a


class R16(TextureFormat):
    id = 0x0A
    bytesPerPixel = 2
    depth = 16

    def decodePixel(self, pixel):
        r = struct.unpack('H', pixel)
        g = 0xFFFF
        b = 0xFFFF
        a = 0xFFFF
        return r, g, b, a


class R8G8B8A8(TextureFormat):
    id = 0x0B
    bytesPerPixel = 4

    def decodePixel(self, pixel):
        return pixel


class R11G11B10(TextureFormat):
    id = 0x0F
    bytesPerPixel = 4
    depth = 16

    def decodePixel(self, pixel):
        pixel = struct.unpack('I', pixel)
        r =  ( pixel        & 0x07FF) << 5
        g =  ((pixel >> 11) & 0x07FF) << 5
        b =  ((pixel >> 22) & 0x03FF) << 6
        a =  0xFFFF
        return r, g, b, a


class R32(TextureFormat):
    id = 0x14
    bytesPerPixel = 4
    depth = 32

    def decodePixel(self, pixel):
        r =  struct.unpack('I', pixel)
        g =  0xFFFFFFFF
        b =  0xFFFFFFFF
        a =  0xFFFFFFFF
        return r, g, b, a
