#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""Support for IEEE 754 half-precision binary floating-point format: binary16.

>>> [binary16(f) for f in [0.006534, -.1232]] == [b'\xb0\x1e', b'\xe2\xaf']
True
"""
from __future__ import division
import struct
from math import copysign, frexp, isinf, isnan, trunc

NEGATIVE_INFINITY = b'\x00\xfc'
POSITIVE_INFINITY = b'\x00\x7c'
POSITIVE_ZERO = b'\x00\x00'
NEGATIVE_ZERO = b'\x00\x80'
# exp=2**5-1 and significand non-zero
EXAMPLE_NAN = struct.pack('<H', (0b11111 << 10) | 1)


def binary16(f):
    """Convert Python float to IEEE 754-2008 (binary16) format.

    https://en.wikipedia.org/wiki/Half-precision_floating-point_format
    """
    if isnan(f):
        return EXAMPLE_NAN

    sign = copysign(1, f) < 0
    if isinf(f):
        return NEGATIVE_INFINITY if sign else POSITIVE_INFINITY

    #           1bit        10bits             5bits
    # f = (-1)**sign * (1 + f16 / 2**10) * 2**(e16 - 15)
    # f = (m * 2)                        * 2**(e - 1)
    m, e = frexp(f)
    assert not (isnan(m) or isinf(m))
    if e == 0 and m == 0:  # zero
        return NEGATIVE_ZERO if sign else POSITIVE_ZERO

    f16 = trunc((2 * abs(m) - 1) * 2**10)  # XXX round toward zero
    assert 0 <= f16 < 2**10
    e16 = e + 14
    if e16 <= 0:  # subnormal
        # f = (-1)**sign * fraction / 2**10 * 2**(-14)
        f16 = int(2**14 * 2**10 * abs(f) + .5)  # XXX round
        e16 = 0
    elif e16 >= 0b11111:  # infinite
        return NEGATIVE_INFINITY if sign else POSITIVE_INFINITY
    else:
        # normalized value
        assert 0b00001 <= e16 < 0b11111, (f, sign, e16, f16)
    """
    http://blogs.perl.org/users/rurban/2012/09/reading-binary-floating-point-numbers-numbers-part2.html
    sign    1 bit  15
    exp     5 bits 14-10     bias 15
    frac   10 bits 9-0

    (-1)**sign * (1 + fraction / 2**10) * 2**(exp - 15)

    +-+-----[1]+----------[0]+ # little endian
    |S| exp    |    fraction |
    +-+--------+-------------+
    |1|<---5-->|<---10bits-->|
    <--------16 bits--------->
    """
    return struct.pack('<H', (sign << 15) | (e16 << 10) | f16)


def bytes_to_half(bytes_):
    """ Read an array of bytes into a list of half's."""
    fmt = '<' + 'H' * (len(bytes_) // 2)
    data = struct.unpack(fmt, bytes_)
    return [_float_from_unsigned16(n) for n in data]


def _float_from_unsigned16(n):
    assert 0 <= n < 2**16
    sign = n >> 15
    exp = (n >> 10) & 0b011111
    fraction = n & (2**10 - 1)
    if exp == 0:
        if fraction == 0:
            return -0.0 if sign else 0.0
        else:
            return (-1)**sign * fraction / 2**10 * 2**(-14)  # subnormal
    elif exp == 0b11111:
        if fraction == 0:
            return float('-inf') if sign else float('inf')
        else:
            return float('nan')
    return (-1)**sign * (1 + fraction / 2**10) * 2**(exp - 15)


def test_wp_half_precision_examples():
    """
    https://en.wikipedia.org/wiki/Half-precision_floating-point_format#Half_precision_examples
    """
    for n, f in [
            (0b0000000000000000, 0.),
            (0b1000000000000000, -0.),
            (0b0011110000000000, 1),
            (0b0011110000000001, 1.0009765625),
            (0b1011110000000001, -1.0009765625),
            (0b1100000000000000, -2),
            (0b0100000000000000, 2),
            (0b0111101111111111, 65504.),
            (0b1111101111111111, -65504.),
            (0b0000010000000000, 6.10352e-5),
            (0b0000001111111111, 6.09756e-5),  # subnormal
            (0b0000000000000001, 5.96046e-8),  # subnormal
            (0b0111110000000000, float('infinity')),
            (0b1111110000000000, float('-infinity')),
            (0b0011010101010101, 0.333251953125)]:
        assert binary16(f) == struct.pack(
            '<H', n), (bin(n)[2:].zfill(16), f, binary16(f))


def test_float64_outside_16bit_range():
    for f16, f64 in [
            (1, 1.0000000000000002),  # ≈ the smallest number > 1
            (0, 2**(-1022 - 52)),  # min subnormal positive double
            (0, 2**(-1022) - 2**(-1022 - 52)),  # max subnormal double
            (0, 2**(-1022)),  # min normal positive double
            (float('inf'), (1 + (1 - 2**(-52))) * 2**1023),  # max double
    ]:
        assert binary16(f16) == binary16(f64)


def test_all_bits(N=16):
    for unsigned in range(2**N):
        # make sure '<h' uses 2's complement representation
        # N-bit two's complement
        signed = (unsigned - 2**N) if unsigned & (1 << (N - 1)) else unsigned
        # stored least significant byte first
        binary = struct.pack('<h', signed)
        assert binary == struct.pack('<H', unsigned), (signed, unsigned)

        f = _float_from_unsigned16(unsigned)
        got = binary16(f)
        assert got == binary or got == EXAMPLE_NAN


if __name__ == '__main__':
    print(_float_from_unsigned16(0xf785))
    """
    test_wp_half_precision_examples()
    test_float64_outside_16bit_range()
    import doctest
    doctest.testmod()
    test_all_bits()
    """
