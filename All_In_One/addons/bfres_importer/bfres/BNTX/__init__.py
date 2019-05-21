import logging; log = logging.getLogger(__name__)
from bfres.BinaryStruct import BinaryStruct, BinaryObject
from bfres.BinaryStruct.Padding import Padding
from bfres.BinaryStruct.StringOffset import StringOffset
from bfres.BinaryStruct.Switch import Offset32, Offset64, String
from bfres.BinaryFile import BinaryFile
from bfres.Common import StringTable
from .NX import NX
from .BRTI import BRTI

class Header(BinaryStruct):
    """BNTX header."""
    magic  = b'BNTX'
    fields = (
        ('4s',   'magic'),
        Padding(4),
        ('I',    'data_len'),
        ('H',    'byte_order'), # FFFE or FEFF
        ('H',    'version'),
        String(  'name', lenprefix=None),
        Padding(2),
        ('H',    'strings_offs'), # relative to start of BNTX
        Offset32('reloc_offs'),
        ('I',    'file_size'),
    )
    size = 0x20


class BNTX:
    """BNTX texture pack."""
    Header = Header

    def __init__(self, file:BinaryFile):
        self.file     = file
        self.textures = []
        self.header   = self.Header().readFromFile(file)
        self.name     = self.header['name']

        if self.header['byte_order'] == 0xFFFE:
            self.byteOrder = 'little'
            self.byteOrderFmt = '<'
        elif self.header['byte_order'] == 0xFEFF:
            self.byteOrder = 'big'
            self.byteOrderFmt = '>'
        else:
            raise ValueError("Invalid byte order 0x%04X in BNTX header" %
                self.header['byte_order'])

        if self.header['version'] != 0x400C:
            log.warning("Unknown BNTX version 0x%04X",
                self.header['version'])

        #log.debug("BNTX version 0x%04X, %s endian",
        #    self.header['version'], self.byteOrder)


    def dump(self):
        """Dump to string for debug."""
        res = []
        res.append("  Name:            '%s'" % self.name)
        res.append("Version:           0x%04X, %s endian" % (
            self.header['version'], self.byteOrder))
        res.append("Data Len:          0x%06X" % self.header['data_len'])
        res.append("Str Offs:          0x%06X" % self.header['strings_offs'])
        res.append("Reloc Offs:        0x%06X" % self.header['reloc_offs'])
        res.append("File Size:         0x%06X" % self.header['file_size'])
        res.append("NX # Textures:     %3d" % self.nx['num_textures'])
        res.append("NX Info Ptrs Offs: 0x%06X" % self.nx['info_ptrs_offset'])
        res.append("NX Data Blk Offs:  0x%06X" % self.nx['data_blk_offset'])
        res.append("NX Dict Offs:      0x%06X" % self.nx['dict_offset'])
        res.append("NX Str Dict Len:   0x%06X" % self.nx['str_dict_len'])
        for tex in self.textures:
            res.append(tex.dump())
        return '\n'.join(res).replace('\n', '\n  ')


    def decode(self):
        """Decode objects from the file."""
        self.strings = StringTable().readFromFile(self.file,
            self.header['strings_offs'])

        self.nx = NX().readFromFile(self.file,
            self.Header.size)

        offs = self.nx['info_ptrs_offset']
        for i in range(self.nx['num_textures']):
            brtiOffs = self.file.read('Q', offs)
            brti = BRTI().readFromFile(self.file, brtiOffs)
            self.textures.append(brti)
            offs += 8
