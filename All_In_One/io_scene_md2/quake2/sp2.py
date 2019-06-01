"""This module provides file I/O for Quake 2 SP2 sprite files.

Example:
    with open('s_bubble.sp2') as file:
        sp2_file = sp2.Sp2.read(file)

References:
    Quake 2 Source
    - id Software
    - https://github.com/id-Software/Quake-2
"""

import struct


class SpriteFrame:
    """Class for working with sprite frames

    Attributes:
        width: Width of the frame.

        height: Height of the frame.

        origin: The offset of the frame.

        name: The name of the pcx file to use for the frame.
    """

    format = '<4i64s'
    size = struct.calcsize(format)

    __slots__ = (
        'width',
        'height',
        'origin',
        'name'
    )

    def __init__(self,
                 width,
                 height,
                 origin_x,
                 origin_y,
                 name):

        self.width = width
        self.height = height
        self.origin = origin_x, origin_y
        self.name = name

        if type(name) == bytes:
            self.name = name.split(b'\00')[0].decode('ascii')

    @classmethod
    def write(cls, file, frame):
        frame_data = struct.pack(cls.format,
                                 frame.width,
                                 frame.height,
                                 *frame.origin,
                                 frame.name.encode('ascii'))

        file.write(frame_data)

    @classmethod
    def read(cls, file):
        frame_data = file.read(cls.size)
        frame_struct = struct.unpack(cls.format, frame_data)

        return SpriteFrame(*frame_struct)


class Sp2:
    """Class for working with Sp2 files

    Example:
        with open('s_bubble.sp2') as file:
        sp2_file = sp2.Sp2.read(file)

    Attributes:
        identity: The identity of the file. Should be b'IDS2'

        version: The version of the file. Should be 2.

        number_of_frames: The number of sprite frames.

        frames: A list of SpriteFrame objects.
    """

    format = '<4s2i'
    size = struct.calcsize(format)

    __slots__ = (
        'identity',
        'version',
        'number_of_frames',
        'frames'
    )

    def __init__(self,
                 identity,
                 version,
                 number_of_frames,
                 frames):

        self.identity = identity
        self.version = version
        self.number_of_frames = number_of_frames
        self.frames = frames

    @classmethod
    def write(cls, file, sp2):
        sp2_data = struct.pack(cls.format,
                               sp2.identity,
                               sp2.version,
                               sp2.number_of_frames)

        file.write(sp2_data)

        for frame in sp2.frames:
            SpriteFrame.write(file, frame)

    @classmethod
    def read(cls, file):
        sp2_data = file.read(cls.size)
        sp2_struct = struct.unpack(cls.format, sp2_data)

        frame_count = sp2_struct[2]
        frames = [SpriteFrame.read(file) for _ in range(frame_count)]

        return Sp2(*sp2_struct, frames)
