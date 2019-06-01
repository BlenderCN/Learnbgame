from struct import pack, unpack
from math import sqrt


def float_to_hex(num):
    """ Convert a hex value to float. """
    return hex(unpack('<I', pack('<f', num))[0])


def list_header(offset, size, end):
    """ Generate the list header.

    Parameters
    ----------
    offset : int
        Relative offset from the location the header will be placed.
    size : int
        Size in bytes of the block of information.
    end : bytes
        End 4 bytes of padding.

    Returns
    -------
    data : bytearray
        0x10 bytes of data representing the list header in memory.
    """
    data = bytearray()
    data.extend(pack('<Q', offset))
    data.extend(pack('<I', size))
    data.extend(end)
    return data


def pad(input_data, length, pad_char=b'\x00', null_terminated=False):
    """ Pads a string to the required length with the null character.

    Parameters
    ----------
    input_data : string, bytes
        Input string.
    length : int
        Required length.
    pad_char : byte
        Byte used as the padding character.
    null_terminated : bool (optional)
        Whether or not to null-terminate the string
    Returns
    -------
    data : bytes
    """
    str_len = len(input_data)
    if not isinstance(input_data, bytes):
        input_data = bytes(input_data, 'utf-8')
    if null_terminated:
        return (input_data + b'\x00' + pad_char * (length - 2 - str_len) +
                b'\x00')
    else:

        return input_data + (length - str_len) * pad_char


def to_chr(string):
    # this is a string of hex data
    out_string = ''
    for i in range(0, len(string)-1, 2):
        # bit messy but seems to be needed to get all the characters..
        out_string += bytes((int(string[i: i+2], 16),)).decode("windows-1252")
    return out_string


def quat_drop_component(arr):
    """ Determine which component of the quaternion to drop. """
    max_loc = 0
    doubled_elements = set()
    condensed_arr = set()
    for i in arr:
        if i in condensed_arr:
            doubled_elements.add(i)
        condensed_arr.add(i)

    if len(condensed_arr) == 4:
        max_loc = arr.index(max(condensed_arr))
    else:
        if 0x3FFF not in doubled_elements:
            max_loc = 0
        else:
            max_loc = arr.index(max(condensed_arr))
    return max_loc


def quat_to_hex(q):
    """ converts a quaternion to its hexadecimal representation """
    q = [int(0x3FFF * (sqrt(2) * i + 1)) for i in q]
    drop_index = quat_drop_component(q)
    del q[drop_index]
    drop_index = 3 - drop_index
    i_x = drop_index >> 1
    i_y = drop_index & 1

    q[0] = (i_x << 0xF) + q[0]
    q[1] = (i_y << 0xF) + q[1]

    return [hex(i) for i in q]


def read_list_data(data, element_size):
    return_data = []
    offset, count = read_list_header(data)
    init_loc = data.tell()
    data.seek(offset, 1)
    for _ in range(count):
        return_data.append(data.read(element_size))
    data.seek(init_loc, 0)
    return return_data


def read_list_header(data):
    """
    Takes the 0x10 byte header and returns the relative offset and
    number of entries
    """
    offset, count = unpack('<QI', data.read(0xC))
    data.seek(-0xC, 1)
    return offset, count


def serialize(x):
    """ Generic serialization function. Attempts to return the bytes
    representation of the object. """
    if type(x) == bytes:
        # in this case it is already sorted are ready to write
        return x
    elif type(x) == int:
        return pack('<i', x)
    elif type(x) == float:
        return pack('<f', x)
    else:
        # in this case just call bytes(~) on the object and hope we get
        # something useful.
        # this should work because we can give custom classes a __bytes__ class
        # method so that it returns the goods!
        return bytes(x)
