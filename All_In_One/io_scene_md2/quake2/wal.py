"""This module provides file I/O for Quake 2 WAL texture files.

Example:
    with open('arrow0.wal') as file:
        wal_file = wal.Wal.read(file)

References:
    Quake 2 Source
    - id Software
    - https://github.com/id-Software/Quake-2
"""

import struct


class Wal:
    """Class for working with Wal files

    Example:
        with open(path) as file:
            w = wal.Wal.read(file)

    Attributes:
        name: The name of the wal texture.

        width: The width of the wal texture.
            Note: This is the width at mipmap level 0.

        height: The height of the wal texture.
            Note: This is the height at mipmap level 0.

        offsets: The offsets for each of the mipmaps. This is a tuple of size
            four (this is the number of mipmap levels).

        animation_name: The name of the next wal texture in the animation
            sequence.

        flags: A bitfield of surface behaviors.

        contents:

        value:

        pixels: A bytes object of unstructured indexed color data. A
            palette must be used to obtain RGB data.

            Note: this is the pixel data for all four mip levels. The size is
            calculated using the simplified form of the geometric series where
            r = 1/4 and n = 4.

            The size of this tuple is:

            wal.width * wal.height * 85 / 64
    """

    format = '<32s6I32s3i'
    size = struct.calcsize(format)

    __slots__ = (
        'name',
        'width',
        'height',
        'offsets',
        'animation_name',
        'flags',
        'contents',
        'value',
        'pixels'
    )

    def __init__(self,
                 name,
                 width,
                 height,
                 offset_0,
                 offset_1,
                 offset_2,
                 offset_3,
                 animation_name,
                 flags,
                 contents,
                 value,
                 pixels):

        self.name = name
        self.width = width
        self.height = height
        self.offsets = offset_0, offset_1, offset_2, offset_3
        self.animation_name = animation_name
        self.flags = flags
        self.contents = contents
        self.value = value
        self.pixels = pixels

        if type(name) == bytes:
            self.name = name.split(b'\00')[0].decode('ascii')

        if type(animation_name) == bytes:
            self.animation_name = animation_name.split(b'\00')[0].decode('ascii')

    @classmethod
    def write(cls, file, wal):
        wal_data = struct.pack(cls.format,
                               wal.name.encode('ascii'),
                               wal.width,
                               wal.height,
                               *wal.offsets,
                               wal.animation_name.encode('ascii'),
                               wal.flags,
                               wal.contents,
                               wal.value)

        file.write(wal_data)
        file.write(wal.pixels)

    @classmethod
    def read(cls, file):
        wal_data = file.read(cls.size)
        wal_struct = struct.unpack(cls.format, wal_data)

        pixels_size = wal_struct[1] * wal_struct[2] * 85 // 64
        pixels = file.read(pixels_size)

        return cls(*wal_struct, pixels)
