
"""
https://github.com/Benjamin-Dobell/s3tc-dxt-decompression
https://github.com/tito/libsquish/blob/master/alpha.cpp#L74
"""

from .io import unpack

DXT1 = 0
DXT3 = 1
DXT5 = 2


def pack_rgba(r, g, b, a):
    return (int(r) << 24) | (int(g) << 16) | (int(b) << 8) | int(a)


def unpack_rgba(c):
    return c >> 24, (c >> 16) & 0xff, (c >> 8) & 0xff, c & 0xff


def unpack_bgra(c):
    return (c >> 8) & 0xff, (c >> 16) & 0xff, c >> 24, c & 0xff


def decompress(dxt_type, width, height, f):
    if dxt_type == DXT1:
        block_function = decompress_block_dxt1
    elif dxt_type == DXT3:
        block_function = decompress_block_dxt3
    elif dxt_type == DXT5:
        block_function = decompress_block_dxt5
    else:
        raise ValueError('Invalid type (must be DXT1, DXT3 or DXT5')
    block_count_x = int((width + 3) / 4)
    block_count_y = int((height + 3) / 4)
    image = [0] * (width * height * 4)
    for j in range(block_count_y):
        for i in range(block_count_x):
            block_function(i * 4, j * 4, width, f, image)
    return image


def decompress_block_dxt1(x, y, width, f, image):
    color1, color2 = unpack('<2H', f)

    temp = (color1 >> 11) * 255 + 16
    r0 = (temp / 32 + temp) / 32
    temp = ((color1 & 0x07E0) >> 5) * 255 + 32
    g0 = (temp / 64 + temp) / 64
    temp = (color1 & 0x001F) * 255 + 16
    b0 = (temp / 32 + temp) / 32

    temp = (color2 >> 11) * 255 + 16
    r1 = (temp / 32 + temp) / 32
    temp = ((color2 & 0x07E0) >> 5) * 255 + 32
    g1 = (temp / 64 + temp) / 64
    temp = (color2 & 0x001F) * 255 + 16
    b1 = (temp / 32 + temp) / 32

    code = unpack('I', f)[0]

    for j in range(4):
        for i in range(4):
            color = 0
            position_code = (code >> 2 * (4 * j + i)) & 0x03

            if color1 > color2:
                if position_code == 0:
                    color = pack_rgba(r0, g0, b0, 255)
                elif position_code == 1:
                    color = pack_rgba(r1, g1, b1, 255)
                elif position_code == 2:
                    color = pack_rgba((2 * r0 + r1) / 3, (2 * g0 + g1) / 3, (2 * b0 + b1) / 3, 255)
                elif position_code == 3:
                    color = pack_rgba((r0 + 2 * r1) / 3, (g0 + 2 * g1) / 3, (b0 + 2 * b1) / 3, 255)
            else:
                if position_code == 0:
                    color = pack_rgba(r0, g0, b0, 255)
                elif position_code == 1:
                    color = pack_rgba(r1, g1, b1, 255)
                elif position_code == 2:
                    color = pack_rgba((r0 + r1) / 2, (g0 + g1) / 2, (b0 + b1) / 2, 255)
                elif position_code == 3:
                    color = pack_rgba(0, 0, 0, 255)

            if x + i < width:
                b = ((y + j) * width + (x + i)) * 4
                image[b:b+4] = unpack_rgba(color)


def dxt3_decompress_alpha(alpha):
    for a in alpha:
        lo = a & 0x0f
        hi = a & 0xf0
        yield lo | (lo << 4)
        yield hi | (hi >> 4)


def decompress_block_dxt3(x, y, width, f, image):
    # all the alpha is thrown in upfront, quantized to 4 bits
    alpha = list(dxt3_decompress_alpha(unpack('8B', f)))
    color0, color1 = unpack('2H', f)

    temp = (color0 >> 11) * 255 + 16
    r0 = (temp / 32 + temp) / 32
    temp = ((color0 & 0x07E0) >> 5) * 255 + 32
    g0 = (temp / 64 + temp) / 64
    temp = (color0 & 0x001F) * 255 + 16
    b0 = (temp / 32 + temp) / 32

    temp = (color1 >> 11) * 255 + 16
    r1 = ((temp/32 + temp)/32)
    temp = ((color1 & 0x07E0) >> 5) * 255 + 32
    g1 = ((temp/64 + temp)/64)
    temp = (color1 & 0x001F) * 255 + 16
    b1 = ((temp/32 + temp)/32)

    code = unpack('I', f)[0]

    for j in range(4):
        for i in range(4):
            final_alpha = alpha[j * 4 + i]
            color_code = (code >> 2 * (4 * j + i)) & 0x03

            if color_code == 0:
                final_color = pack_rgba(r0, g0, b0, final_alpha)
            elif color_code == 1:
                final_color = pack_rgba(r1, g1, b1, final_alpha)
            elif color_code == 2:
                final_color = pack_rgba((2 * r0 + r1) / 3, (2 * g0 + g1) / 3, (2 * b0 + b1) / 3, final_alpha)
            else:
                final_color = pack_rgba((r0 + 2 * r1) / 3, (g0 + 2 * g1) / 3, (b0 + 2 * b1) / 3, final_alpha)

            if x + i < width:
                b = ((y + j) * width + (x + i)) * 4
                image[b:b+4] = unpack_rgba(final_color)


def decompress_block_dxt5(x, y, width, f, image):
    alpha0, alpha1 = unpack('2B', f)
    bits = unpack('6B', f)
    alpha_code_1 = bits[2] | (bits[3] << 8) | (bits[4] << 16) | (bits[5] << 24)
    alpha_code_2 = bits[0] | (bits[1] << 8)
    color0, color1 = unpack('2H', f)

    temp = (color0 >> 11) * 255 + 16
    r0 = (temp / 32 + temp) / 32
    temp = ((color0 & 0x07E0) >> 5) * 255 + 32
    g0 = (temp / 64 + temp) / 64
    temp = (color0 & 0x001F) * 255 + 16
    b0 = (temp / 32 + temp) / 32

    temp = (color1 >> 11) * 255 + 16
    r1 = ((temp/32 + temp)/32)
    temp = ((color1 & 0x07E0) >> 5) * 255 + 32
    g1 = ((temp/64 + temp)/64)
    temp = (color1 & 0x001F) * 255 + 16
    b1 = ((temp/32 + temp)/32)

    code = unpack('I', f)[0]

    for j in range(4):
        for i in range(4):
            alpha_code_index = 3 * (4 * j + i)

            if alpha_code_index <= 12:
                alpha_code = (alpha_code_2 >> alpha_code_index) & 0x07
            elif alpha_code_index == 15:
                alpha_code = (alpha_code_2 >> 15) | ((alpha_code_1 << 1) & 0x06)
            else:
                alpha_code = (alpha_code_1 >> (alpha_code_index - 16)) & 0x07

            if alpha_code == 0:
                final_alpha = alpha0
            elif alpha_code == 1:
                final_alpha = alpha1
            else:
                if alpha0 > alpha1:
                    final_alpha = ((8 - alpha_code) * alpha0 + (alpha_code - 1) * alpha1) / 7
                else:
                    if alpha_code == 6:
                        final_alpha = 0
                    elif alpha_code == 7:
                        final_alpha = 255
                    else:
                        final_alpha = ((6 - alpha_code) * alpha0 + (alpha_code - 1) * alpha1) / 5

            color_code = (code >> 2 * (4 * j + i)) & 0x03

            if color_code == 0:
                final_color = pack_rgba(r0, g0, b0, final_alpha)
            elif color_code == 1:
                final_color = pack_rgba(r1, g1, b1, final_alpha)
            elif color_code == 2:
                final_color = pack_rgba((2 * r0 + r1) / 3, (2 * g0 + g1) / 3, (2 * b0 + b1) / 3, final_alpha)
            else:
                final_color = pack_rgba((r0 + 2 * r1) / 3, (g0 + 2 * g1) / 3, (b0 + 2 * b1) / 3, final_alpha)

            if x + i < width:
                k = ((y + j) * width + (x + i)) * 4
                image[k:k+4] = unpack_rgba(final_color)
