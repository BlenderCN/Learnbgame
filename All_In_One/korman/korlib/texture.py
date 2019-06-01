#    This file is part of Korman.
#
#    Korman is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Korman is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Korman.  If not, see <http://www.gnu.org/licenses/>.

import array
import bgl
from ..helpers import ensure_power_of_two
import math
from PyHSPlasma import plBitmap

# BGL doesn't know about this as of Blender 2.74
bgl.GL_BGRA = 0x80E1

# Some texture generation flags
TEX_DETAIL_ALPHA = 0
TEX_DETAIL_ADD = 1
TEX_DETAIL_MULTIPLY = 2

def scale_image(buf, srcW, srcH, dstW, dstH):
    """Scales an RGBA image using the algorithm from CWE's plMipmap::ScaleNicely"""
    dst, dst_idx = bytearray(dstW * dstH * 4), 0
    scaleX, scaleY = (srcW / dstW), (srcH / dstH)
    filterW, filterH = max(scaleX, 1.0), max(scaleY, 1.0)

    src_rowspan = srcW * 4
    weightsY = array.array("f", [0.0] * 16)
    weightsX = array.array("f", [0.0] * 16)

    # I hope you're in no particular hurry...
    for dstY in range(dstH):
        srcY = dstY * scaleY
        srcY_start = int(max(srcY - filterH, 0))
        srcY_end = int(min(srcY + filterH, srcH - 1))

        #weightsY = { i - srcY_start: 1.0 - abs(i - srcY) / scaleY \
        #             for i in range(srcY_start, srcY_end+1, 1) if i - srcY_start < 16 }
        for i in range(16):
            idx = i + srcY_start
            if idx > srcY_end:
                break
            weightsY[i] = 1.0 - abs(idx - srcY) / filterH

        for dstX in range(dstW):
            srcX = dstX * scaleX
            srcX_start = int(max(srcX - filterW, 0))
            srcX_end = int(min(srcX + filterW, srcW - 1))

            #weightsX = { i - srcX_start: 1.0 - abs(i - srcX) / scaleX \
            #             for i in range(srcX_start, srcX_end+1, 1) if i - srcX_start < 16 }
            for i in range(16):
                idx = i + srcX_start
                if idx > srcX_end:
                    break
                weightsX[i] = 1.0 - abs(idx - srcX) / filterW

            accum_color = [0.0, 0.0, 0.0, 0.0]
            weight_total = 0.0
            for i in range(srcY_start, srcY_end+1, 1):
                weightY_idx = i - srcY_start
                weightY = weightsY[weightY_idx] if weightY_idx < 16 else 1.0 - abs(i - srcY) / filterH
                weightY = 1.0 - abs(i - srcY) / filterH

                src_idx = (i * src_rowspan) + (srcX_start * 4)
                for j in range(srcX_start, srcX_end+1, 1):
                    weightX_idx = j - srcX_start
                    weightX = weightsX[weightX_idx] if weightX_idx < 16 else 1.0 - abs(j - srcX) / filterW
                    weight = weightY * weightX

                    if weight > 0.0:
                        # According to profiling, a list comprehension here doubles the execution time of this
                        # function. I know this function is supposed to be slow, but dayum... I've unrolled it
                        # to avoid all the extra allocations.
                        for k in range(4):
                            accum_color[k] = accum_color[k] + buf[src_idx+k] * weight
                        weight_total += weight
                    src_idx += 4

            weight_total = max(weight_total, 0.0001)
            for i in range(4):
                accum_color[i] = int(accum_color[i] * (1.0 / weight_total))
            dst[dst_idx:dst_idx+4] = accum_color
            dst_idx += 4

    return bytes(dst)


class GLTexture:
    def __init__(self, texkey=None, image=None, bgra=False, fast=False):
        assert texkey or image
        self._texkey = texkey
        if texkey is not None:
            self._blimg = texkey.image
        if image is not None:
            self._blimg = image
        self._image_inverted = fast
        self._bgra = bgra

    def __enter__(self):
        """Loads the image data using OpenGL"""

        # Set image active in OpenGL
        ownit = self._blimg.bindcode[0] == 0
        if ownit:
            if self._blimg.gl_load() != 0:
                raise RuntimeError("failed to load image")
        previous_texture = self._get_integer(bgl.GL_TEXTURE_BINDING_2D)
        changed_state = (previous_texture != self._blimg.bindcode[0])
        if changed_state:
            bgl.glBindTexture(bgl.GL_TEXTURE_2D, self._blimg.bindcode[0])

        # Grab the image data
        self._width = self._get_tex_param(bgl.GL_TEXTURE_WIDTH, 0)
        self._height = self._get_tex_param(bgl.GL_TEXTURE_HEIGHT, 0)
        size = self._width * self._height * 4
        buf = bgl.Buffer(bgl.GL_BYTE, size)
        fmt = bgl.GL_BGRA if self._bgra else bgl.GL_RGBA
        bgl.glGetTexImage(bgl.GL_TEXTURE_2D, 0, fmt, bgl.GL_UNSIGNED_BYTE, buf)

        # OpenGL returns the images upside down, so we're going to rotate it in memory.
        # ... But only if requested... :)
        if self._image_inverted:
            self._image_data = bytes(buf)
        else:
            self._image_data = self._invert_image(self._width, self._height, buf)

        # Restore previous OpenGL state
        if changed_state:
            bgl.glBindTexture(bgl.GL_TEXTURE_2D, previous_texture)
        if ownit:
            self._blimg.gl_free()
        return self

    def __exit__(self, type, value, traceback):
        del self._image_data

    @property
    def _detail_falloff(self):
        num_levels = self.num_levels
        return ((self._texkey.detail_fade_start / 100.0) * num_levels,
                (self._texkey.detail_fade_stop / 100.0) * num_levels,
                 self._texkey.detail_opacity_start / 100.0,
                 self._texkey.detail_opacity_stop / 100.0)

    def get_level_data(self, level=0, calc_alpha=False, report=None, indent=2, fast=False):
        """Gets the uncompressed pixel data for a requested mip level, optionally calculating the alpha
           channel from the image color data
        """

        # Previously, we would leave the texture bound in OpenGL and use it to do the mipmapping, using
        # old, deprecated OpenGL features. With the introduction of plCubicEnvironmap support to Korman,
        # we wind up needing to get an NPOT image from OpenGL. Unfortunately, Blender will sometimes scale
        # images to be POT _before_ loading them into OpenGL. Therefore, we now use OpenGL to grab the first
        # level, then scale down to the new level from there.
        oWidth, oHeight = self.size_npot
        eWidth = ensure_power_of_two(oWidth) >> level
        eHeight = ensure_power_of_two(oHeight) >> level

        if report is not None:
            report.msg("Level #{}: {}x{}", level, eWidth, eHeight, indent=indent)

        # Scale, if needed...
        if oWidth != eWidth or oHeight != eHeight:
            buf = scale_image(self._image_data, oWidth, oHeight, eWidth, eHeight)
        else:
            buf = self._image_data

        # Some operations, like alpha testing, don't care about the fact that OpenGL flips
        # the images in memory. Give an opportunity to bail here...
        if fast:
            return self._image_data
        else:
            buf = bytearray(self._image_data)


        if self._image_inverted:
            buf = self._invert_image(eWidth, eHeight, buf)

        # If this is a detail map, then we need to bake that per-level here.
        if self._texkey is not None and self._texkey.is_detail_map:
            detail_blend = self._texkey.detail_blend
            if detail_blend == TEX_DETAIL_ALPHA:
                self._make_detail_map_alpha(buf, level)
            elif detail_blend == TEX_DETAIL_ADD:
                self._make_detail_map_alpha(buf, level)
            elif detail_blend == TEX_DETAIL_MULTIPLY:
                self._make_detail_map_mult(buf, level)

        # Do we need to calculate the alpha component?
        if calc_alpha:
            for i in range(0, size, 4):
                buf[i+3] = int(sum(buf[i:i+3]) / 3)
        return bytes(buf)

    def _get_detail_alpha(self, level, dropoff_start, dropoff_stop, detail_max, detail_min):
        alpha = (level - dropoff_start) * (detail_min - detail_max) / (dropoff_stop - dropoff_start) + detail_max
        if detail_min < detail_max:
            return min(detail_max, max(detail_min, alpha))
        else:
            return min(detail_min, max(detail_max, alpha))

    def _get_integer(self, arg):
        buf = bgl.Buffer(bgl.GL_INT, 1)
        bgl.glGetIntegerv(arg, buf)
        return int(buf[0])

    def _get_tex_param(self, param, level=None):
        buf = bgl.Buffer(bgl.GL_INT, 1)
        if level is None:
            bgl.glGetTexParameteriv(bgl.GL_TEXTURE_2D, param, buf)
        else:
            bgl.glGetTexLevelParameteriv(bgl.GL_TEXTURE_2D, level, param, buf)
        return int(buf[0])

    @property
    def has_alpha(self):
        data = self._image_data
        for i in range(3, len(data), 4):
            if data[i] != 255:
                return True
        return False

    def _get_image_data(self):
        return (self._width, self._height, self._image_data)
    def _set_image_data(self, value):
        self._width, self._height, self._image_data = value
    image_data = property(_get_image_data, _set_image_data)

    def _invert_image(self, width, height, buf):
        size = width * height * 4
        finalBuf = bytearray(size)
        row_stride = width * 4
        for i in range(height):
            src, dst = i * row_stride, (height - (i+1)) * row_stride
            finalBuf[dst:dst+row_stride] = buf[src:src+row_stride]
        return bytes(finalBuf)

    def _make_detail_map_add(self, data, level):
        dropoff_start, dropoff_stop, detail_max, detail_min = self._detail_falloff
        alpha = self._get_detail_alpha(level, dropoff_start, dropoff_stop, detail_max, detail_min)
        for i in range(0, len(data), 4):
            data[i] = int(data[i] * alpha)
            data[i+1] = int(data[i+1] * alpha)
            data[i+2] = int(data[i+2] * alpha)

    def _make_detail_map_alpha(self, data, level):
        dropoff_start, dropoff_end, detail_max, detail_min = self._detail_falloff
        alpha = self._get_detail_alpha(level, dropoff_start, dropoff_end, detail_max, detail_min)
        for i in range(0, len(data), 4):
            data[i+3] = int(data[i+3] * alpha)

    def _make_detail_map_mult(self, data, level):
        dropoff_start, dropoff_end, detail_max, detail_min = self._detail_falloff
        alpha = self._get_detail_alpha(level, dropoff_start, dropoff_end, detail_max, detail_min)
        invert_alpha = (1.0 - alpha) * 255.0
        for i in range(0, len(data), 4):
            data[i+3] = int(invert_alpha + data[i+3] * alpha)

    @property
    def num_levels(self):
        numLevels = math.floor(math.log(max(self.size_npot), 2)) + 1

        # Major Workaround Ahoy
        # There is a bug in Cyan's level size algorithm that causes it to not allocate enough memory
        # for the color block in certain mipmaps. I personally have encountered an access violation on
        # 1x1 DXT5 mip levels -- the code only allocates an alpha block and not a color block. Paradox
        # reports that if any dimension is smaller than 4px in a mip level, OpenGL doesn't like Cyan generated
        # data. So, we're going to lop off the last two mip levels, which should be 1px and 2px as the smallest.
        # This bug is basically unfixable without crazy hacks because of the way Plasma reads in texture data.
        #     "<Deledrius> I feel like any texture at a 1x1 level is essentially academic.  I mean, JPEG/DXT
        #                  doesn't even compress that, and what is it?  Just the average color of the whole
        #                  texture in a single pixel?"
        # :)
        return max(numLevels - 2, 2)

    @property
    def size_npot(self):
        return self._width, self._height

    @property
    def size_pot(self):
        return ensure_power_of_two(self._width), ensure_power_of_two(self._height)
