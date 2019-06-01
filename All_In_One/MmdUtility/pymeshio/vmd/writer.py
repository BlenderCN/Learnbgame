# coding: utf-8
import io
import struct
from .. import common
from .. import vmd

def write(ios, motion):
    """
    """
    assert(isinstance(ios, io.IOBase))
    assert(isinstance(motion, vmd.Motion))
    writer=common.BinaryWriter(ios)

    # 30 bytes
    writer.write_bytes(b"Vocaloid Motion Data 0002", 30)
    # 20 bytes
    writer.write_bytes(b"", 20)

    # bone motions
    print(len(motion.motions))
    writer.write_uint(len(motion.motions), 4)
    for m in motion.motions:
        """
        フレームひとつ分(111 bytes)
        """
        writer.write_bytes(m.name, 15)
        writer.write_uint(m.frame, 4)
        writer.write_float(m.pos.x)
        writer.write_float(m.pos.y)
        writer.write_float(m.pos.z)
        writer.write_float(m.q.x)
        writer.write_float(m.q.y)
        writer.write_float(m.q.z)
        writer.write_float(m.q.w)
        writer.write_bytes(m.complement, 64)

    # shape motions
    writer.write_uint(len(motion.shapes), 4)
    for s in motion.shapes:
        writer.write_bytes(s.name, 15)
        writer.write_uint(s.frame, 4)
        writer.write_float(s.ratio)

    # ToDo
    writer.write_uint(0, 4)
    writer.write_uint(0, 4)

    return True

