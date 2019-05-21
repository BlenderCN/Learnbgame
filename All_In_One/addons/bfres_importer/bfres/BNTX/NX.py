import logging; log = logging.getLogger(__name__)
from bfres.BinaryStruct import BinaryStruct, BinaryObject
from bfres.BinaryStruct.Padding import Padding
from bfres.BinaryStruct.Switch import Offset32, Offset64


class NX(BinaryStruct):
    """A 'NX' texture in a BNTX."""
    magic  = b'NX  '
    fields = (
        ('4s',   'magic'),
        ('I',    'num_textures'),
        Offset64('info_ptrs_offset'),
        Offset64('data_blk_offset'),
        Offset64('dict_offset'),
        ('I',    'str_dict_len'),
    )
