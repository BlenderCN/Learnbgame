import struct
from collections import namedtuple

from ..serialization.utils import read_list_header  # noqa pylint: disable=relative-beyond-top-level
from ..NMS.LOOKUPS import DIFFUSE, MASKS, NORMAL  # noqa pylint: disable=relative-beyond-top-level


def read_material(fname):
    """ Reads the textures and types from a material file.

    Returns
    -------
    data : dict
        Mapping between the texture type (one of DIFFUSE, MASKS, NORMAL) and
        the path to the texture
    """
    data = dict()

    # Read the data directly from the mbin
    with open(fname, 'rb') as f:
        f.seek(0x60)
        # get name
        data['Name'] = struct.unpack('128s', f.read(0x80))[0].split(b'\x00')[0]
        data['Name'] = data['Name'].decode()
        # get material flags
        data['Flags'] = list()
        f.seek(0x208)
        list_offset, list_count = read_list_header(f)
        f.seek(list_offset, 1)
        for i in range(list_count):
            data['Flags'].append(struct.unpack('<I', f.read(0x4))[0])
        # get uniforms
        data['Uniforms'] = dict()
        f.seek(0x218)
        list_offset, list_count = read_list_header(f)
        f.seek(list_offset, 1)
        for i in range(list_count):
            name = struct.unpack('32s', f.read(0x20))[0].split(b'\x00')[0]
            name = name.decode()
            value = struct.unpack('<ffff', f.read(0x10))
            data['Uniforms'][name] = value
            f.seek(0x10, 1)
        # get samplers (texture paths)
        data['Samplers'] = dict()
        f.seek(0x228)
        list_offset, list_count = read_list_header(f)
        f.seek(list_offset, 1)
        for i in range(list_count):
            name = struct.unpack('32s', f.read(0x20))[0].split(b'\x00')[0]
            name = name.decode()
            Map = struct.unpack('128s', f.read(0x80))[0].split(b'\x00')[0]
            Map = Map.decode()
            data['Samplers'][name] = Map
            if i != list_count - 1:
                f.seek(0x38, 1)

    return data


def read_metadata(fname):
    """ Reads all the metadata from the gstream file.

    Returns
    -------
    data : dict (str: namedtuple)
        Mapping between the names of the meshes and their metadata
    """
    data = dict()
    with open(fname, 'rb') as f:
        # move to the start of the StreamMetaDataArray header
        f.seek(0x190)
        # find how far to jump
        list_offset, list_count = read_list_header(f)
        f.seek(list_offset, 1)
        for _ in range(list_count):
            # read the ID in and strip it to be just the string and no padding.
            string = struct.unpack('128s', f.read(0x80))[0].split(b'\x00')[0]
            string = string.decode()
            # skip the hash
            f.seek(0x8, 1)
            # read in the actual data we want
            vert_size, vert_off, idx_size, idx_off = struct.unpack(
                '<IIII',
                f.read(0x10))
            gstream_info = namedtuple('gstream_info',
                                      ['vert_size', 'vert_off',
                                       'idx_size', 'idx_off'])
            data[string] = gstream_info(vert_size, vert_off, idx_size, idx_off)
    return data


def read_gstream(fname, info):
    """ Read the requested info from the gstream file.

    Parameters
    ----------
    fname : string
        File path to the ~.GEOMETRY.DATA.MBIN.PC file.
    info : namedtuple
        namedtupled containing the vertex sizes and offset, and index sizes and
        offsets.

    Returns
    -------
    verts : bytes
        Raw vertex data.
    indexes : bytes
        Raw index data.
    """
    with open(fname, 'rb') as f:
        f.seek(info.vert_off)
        verts = f.read(info.vert_size)
        f.seek(info.idx_off)
        indexes = f.read(info.idx_size)
    return verts, indexes
