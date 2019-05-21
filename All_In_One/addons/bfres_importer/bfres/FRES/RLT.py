import logging; log = logging.getLogger(__name__)
from bfres.BinaryStruct import BinaryStruct, BinaryObject
from bfres.BinaryStruct.Padding import Padding
from bfres.BinaryStruct.StringOffset import StringOffset
from bfres.BinaryStruct.Switch import Offset32, Offset64, String
from bfres.BinaryFile import BinaryFile
from .FresObject import FresObject

# https://wiki.oatmealdome.me/BFRES_(File_Format)#Relocation_Table
# BFRES always has 5 sections (some may be unused):
# 0. Pointers up to the end of the string pool.
# 1. Pointers for index buffer.
# 2. Pointers for vertex buffer.
# 3. Pointers for memory pool.
# 4. Pointers for external files.
# Relocation table is used to quickly load files; rather than
# actually parsing them, the whole file is loaded into memory,
# and this table is used to locate the structs. So the pointers
# must be correct, but mostly aren't needed to parse the file.

class Header(BinaryStruct):
    """RLT header."""
    magic  = b'_RLT'
    fields = (
        ('4s', 'magic'),
        ('I',  'curOffset'),   # offset of the RLT
        ('I',  'numSections'), # always 5
        Padding(4),
    )
    size = 0x10


class Section(BinaryStruct):
    """Section in relocation table."""
    fields = (
        Offset64('base'),
        Offset32('curOffset'),
        Offset32('size'),
        Offset32('idx'),   # entry index
        Offset32('count'), # entry count
    )
    size = 0x18


class Entry(BinaryStruct):
    """Entry in relocation section."""
    fields = (
        Offset32('curOffset'),
        ('H',    'structCount'),
        ('B',    'offsetCount'),
        ('B',    'stride'), # sometimes incorrectly called paddingCount
    )
    size = 0x08


    #def readFromFile(self, file, offset):
    #    data = super().readFromFile(file, offset)
    #    for i in range(data['structCount']):


class RLT(FresObject):
    """A relocation table in an FRES."""

    def __init__(self, fres):
        self.fres = fres


    def dump(self):
        """Dump to string for debug."""
        res = []
        res.append("  Relocation table Offset: 0x%08X" %
            self.header['curOffset'])

        res.append("  \x1B[4mSection│BaseOffs│CurOffs │Size    │EntryIdx│EntryCnt\x1B[0m")
        for i, section in enumerate(self.sections):
            res.append("  %7d│%08X│%08X│%08X│%8d|%4d" % (
                i, section['base'], section['curOffset'],
                section['size'], section['idx'], section['count']))

        res.append("  \x1B[4mEntry│CurOffs │Structs│Offsets│Padding\x1B[0m")
        for i, entry in enumerate(self.entries):
            res.append("  %5d│%08X│%7d│%7d│%4d" % (
                i, entry['curOffset'], entry['structCount'],
                entry['offsetCount'], entry['stride']))

        return '\n'.join(res).replace('\n', '\n  ')


    def readFromFRES(self, offset=None):
        """Read this object from the FRES."""
        if offset is None:
            offset = self.fres.header['rlt_offset']
        self.header = Header().readFromFile(self.fres.file, offset)
        offset += Header.size

        # read sections
        numEntries = 0
        self.sections = []
        for i in range(self.header['numSections']):
            sec = Section().readFromFile(self.fres.file, offset)
            self.sections.append(sec)
            numEntries += sec['count']
            offset += Section.size

        # read entries
        self.entries = []
        for i in range(numEntries):
            entry = Entry().readFromFile(self.fres.file, offset)
            offset += Entry.size
            self.entries.append(entry)

        return self
