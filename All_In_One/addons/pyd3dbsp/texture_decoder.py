import struct
from io import BytesIO

# this code is straight up yoinked from Pillow
   
def _decode565(bits):
    a = ((bits >> 11) & 0x1f) << 3
    b = ((bits >> 5) & 0x3f) << 2
    c = (bits & 0x1f) << 3
    return a, b, c

def _c2a(a, b):
    return (2 * a + b) // 3


def _c2b(a, b):
    return (a + b) // 2


def _c3(a, b):
    return (2 * b + a) // 3


def decode_dxt1(byte_data, width, height):
    data = BytesIO(byte_data)
    ret = bytearray(4 * width * height)

    for y in range(0, height, 4):
        for x in range(0, width, 4):
            color0, color1, bits = struct.unpack("<HHI", data.read(8))

            r0, g0, b0 = _decode565(color0)
            r1, g1, b1 = _decode565(color1)

            # Decode this block into 4x4 pixels
            for j in range(4):
                for i in range(4):
                    # get next control op and generate a pixel
                    control = bits & 3
                    bits = bits >> 2
                    if control == 0:
                        r, g, b = r0, g0, b0
                    elif control == 1:
                        r, g, b = r1, g1, b1
                    elif control == 2:
                        if color0 > color1:
                            r, g, b = _c2a(r0, r1), _c2a(g0, g1), _c2a(b0, b1)
                        else:
                            r, g, b = _c2b(r0, r1), _c2b(g0, g1), _c2b(b0, b1)
                    elif control == 3:
                        if color0 > color1:
                            r, g, b = _c3(r0, r1), _c3(g0, g1), _c3(b0, b1)
                        else:
                            r, g, b = 0, 0, 0

                    idx = 4 * ((y + j) * width + x + i)
                    ret[idx:idx+4] = struct.pack('4B', r, g, b, 255)

    return bytes(ret)


def _dxtc_alpha(a0, a1, ac0, ac1, ai):
    if ai <= 12:
        ac = (ac0 >> ai) & 7
    elif ai == 15:
        ac = (ac0 >> 15) | ((ac1 << 1) & 6)
    else:
        ac = (ac1 >> (ai - 16)) & 7

    if ac == 0:
        alpha = a0
    elif ac == 1:
        alpha = a1
    elif a0 > a1:
        alpha = ((8 - ac) * a0 + (ac - 1) * a1) // 7
    elif ac == 6:
        alpha = 0
    elif ac == 7:
        alpha = 0xff
    else:
        alpha = ((6 - ac) * a0 + (ac - 1) * a1) // 5

    return alpha


def decode_dxt5(byte_data, width, height):
    data = BytesIO(byte_data)
    ret = bytearray(4 * width * height)

    for y in range(0, height, 4):
        for x in range(0, width, 4):
            a0, a1, ac0, ac1, c0, c1, code = struct.unpack("<2BHI2HI",
                                                        data.read(16))

            r0, g0, b0 = _decode565(c0)
            r1, g1, b1 = _decode565(c1)

            for j in range(4):
                for i in range(4):
                    ai = 3 * (4 * j + i)
                    alpha = _dxtc_alpha(a0, a1, ac0, ac1, ai)

                    cc = (code >> 2 * (4 * j + i)) & 3
                    if cc == 0:
                        r, g, b = r0, g0, b0
                    elif cc == 1:
                        r, g, b = r1, g1, b1
                    elif cc == 2:
                        r, g, b = _c2a(r0, r1), _c2a(g0, g1), _c2a(b0, b1)
                    elif cc == 3:
                        r, g, b = _c3(r0, r1), _c3(g0, g1), _c3(b0, b1)

                    idx = 4 * ((y + j) * width + x + i)
                    ret[idx:idx+4] = struct.pack('4B', r, g, b, alpha)

    return bytes(ret)
