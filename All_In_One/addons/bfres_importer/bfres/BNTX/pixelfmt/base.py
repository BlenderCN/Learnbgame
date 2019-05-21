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

types = { # name => id, bytes per pixel
    'R5G6B5':    {'id':0x07, 'bpp': 2},
    'R8G8':      {'id':0x09, 'bpp': 2},
    'R16':       {'id':0x0A, 'bpp': 2},
    'R8G8B8A8':  {'id':0x0B, 'bpp': 4},
    'R11G11B10': {'id':0x0F, 'bpp': 4},
    'R32':       {'id':0x14, 'bpp': 4},
    'BC1':       {'id':0x1A, 'bpp': 8},
    'BC2':       {'id':0x1B, 'bpp':16},
    'BC3':       {'id':0x1C, 'bpp':16},
    'BC4':       {'id':0x1D, 'bpp': 8},
    'BC5':       {'id':0x1E, 'bpp':16},
    'BC6':       {'id':0x1F, 'bpp': 8}, # XXX verify bpp
    'BC7':       {'id':0x20, 'bpp': 8}, # XXX verify bpp
    'ASTC4x4':   {'id':0x2D, 'bpp':16},
    'ASTC5x4':   {'id':0x2E, 'bpp':16},
    'ASTC5x5':   {'id':0x2F, 'bpp':16},
    'ASTC6x5':   {'id':0x30, 'bpp':16},
    'ASTC6x6':   {'id':0x31, 'bpp':16},
    'ASTC8x5':   {'id':0x32, 'bpp':16},
    'ASTC8x6':   {'id':0x33, 'bpp':16},
    'ASTC8x8':   {'id':0x34, 'bpp':16},
    'ASTC10x5':  {'id':0x35, 'bpp':16},
    'ASTC10x6':  {'id':0x36, 'bpp':16},
    'ASTC10x8':  {'id':0x37, 'bpp':16},
    'ASTC10x10': {'id':0x38, 'bpp':16},
    'ASTC12x10': {'id':0x39, 'bpp':16},
    'ASTC12x12': {'id':0x3A, 'bpp':16},
}

fmts = {}

class TextureFormat:
    id = None
    bytesPerPixel = 1
    depth = 8

    @staticmethod
    def get(id):
        try:
            return fmts[id]
        except KeyError:
            log.error("Unsupported texture format 0x%02X", id)
            raise TypeError("Unsupported texure format")


    def decode(self, tex):
        pixels = []
        decode = self.decodePixel
        bpp    = self.bytesPerPixel
        data   = tex.data
        log.debug("Texture: %d bytes/pixel, %dx%d = %d, len = %d",
            bpp, tex.width, tex.height, tex.width * tex.height * bpp,
            len(data))
        for i in range(0, len(data), bpp):
            px = data[i : i+bpp]
            pixels.append(decode(px))
        return pixels, self.depth


    def decodePixel(self, pixel):
        raise TypeError("No decoder for textue format " +
            type(self).__name__)


    def __str__(self):
        return "<TextureFormat '%s' at 0x%x>" % (
            type(self).__name__, id(self))
