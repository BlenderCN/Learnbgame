import struct


def bytes_to_ubyte(bytes_):
    """ Read an array of bytes into a list of unsigned bytes. """
    fmt = '<' + 'B' * len(bytes_)
    data = struct.unpack(fmt, bytes_)
    return [int(n) for n in data]
