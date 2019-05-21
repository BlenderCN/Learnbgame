import logging; log = logging.getLogger(__name__)
from bfres.BinaryStruct import BinaryStruct, BinaryObject
from bfres.BinaryStruct.StringOffset import StringOffset
from bfres.BinaryStruct.Padding import Padding
from bfres.BinaryStruct.Switch import Offset32, Offset64, String
from bfres.BinaryFile import BinaryFile
from .RLT import RLT
from bfres.Common import StringTable
from bfres.Exceptions import \
    UnsupportedFormatError, UnsupportedFileTypeError
from .Dict import Dict
from .EmbeddedFile import EmbeddedFile, Header as EmbeddedFileHeader
from .FMDL import FMDL, Header as FMDLHeader
from .BufferSection import BufferSection
from .DumpMixin import DumpMixin
import traceback
import struct

# XXX WiiU header

class SwitchHeader(BinaryStruct):
    """Switch FRES header."""
    magic = b'FRES    ' # four spaces
    fields = (
        ('8s', 'magic'),      # 0x00
        ('<2H','version'),    # 0x08
        ('H',  'byte_order'), # 0x0C; FFFE=litle, FEFF=big
        ('B',  'alignment'),  # 0x0E
        ('B',  'addr_size'),  # 0x0F; target address size, usually 0

        String('name', lenprefix=None), #0x10;  null-terminated filename
        ('H', 'flags'), # 0x14
        ('H', 'block_offset'), # 0x16

        Offset32('rlt_offset'), # 0x18; relocation table
        Offset32('file_size'),  # 0x1C; size of this file

        String('name2', fmt='Q'), # 0x20; length-prefixed filename
        # name and name2 seem to always both be the filename
        # without extension, and in fact name points to the actual
        # string following the length prefix that name2 points to.

        Offset64('fmdl_offset'),      # 0x28
        Offset64('fmdl_dict_offset'), # 0x30

        Offset64('fska_offset'),      # 0x38
        Offset64('fska_dict_offset'), # 0x40

        Offset64('fmaa_offset'),      # 0x48
        Offset64('fmaa_dict_offset'), # 0x50

        Offset64('fvis_offset'),      # 0x58
        Offset64('fvis_dict_offset'), # 0x60

        Offset64('fshu_offset'),      # 0x68
        Offset64('fshu_dict_offset'), # 0x70

        Offset64('fscn_offset'),      # 0x78
        Offset64('fscn_dict_offset'), # 0x80

        Offset64('buf_mem_pool'),       # 0x88
        Offset64('buf_section_offset'), # 0x90; BufferSection offset

        Offset64('embed_offset'),      # 0x98
        Offset64('embed_dict_offset'), # 0xA0

        Padding(8), # 0xA8; might be an unused offset?
        Offset64('str_tab_offset'), # 0xB0
        Offset32('str_tab_size'),   # 0xB8

        ('H',    'fmdl_cnt'),  # 0xBC
        ('H',    'fska_cnt'),  # 0xBE
        ('H',    'fmaa_cnt'),  # 0xC0
        ('H',    'fvis_cnt'),  # 0xC2
        ('H',    'fshu_cnt'),  # 0xC4
        ('H',    'fscn_cnt'),  # 0xC6
        ('H',    'embed_cnt'), # 0xC8
        Padding(6), # 0xCA
    )
    size = 0xD0


class FRES(DumpMixin):
    """FRES file."""

    def __init__(self, file:BinaryFile):
        self.file       = file
        self.models     = [] # fmdl
        self.animations = [] # fska
        self.buffers    = [] # buffer data
        self.embeds     = [] # embedded files

        # read magic and determine file type
        pos   = file.tell()
        magic = file.read('8s')
        file.seek(pos) # return to previous position
        if magic == b'FRES    ':
            Header = SwitchHeader()
            self.header = Header.readFromFile(file)
        elif magic[0:4] == b'FRES':
            raise UnsupportedFormatError(
                "Sorry, WiiU files aren't supported yet")
        else:
            raise UnsupportedFileTypeError(magic)

        # extract some header info.
        #log.debug("FRES header:\n%s", Header.dump(self.header))
        self.name    = self.header['name']
        self.size    = self.header['file_size']
        self.version = self.header['version']

        #self._readLogFile = open('./%s.map.csv' % self.name, 'w')

        if self.version != (3, 5):
            log.warning("Unknown FRES version 0x%04X 0x%04X",
                self.version[0], self.version[1])

        if self.header['byte_order'] == 0xFFFE:
            self.byteOrder = 'little'
            self.byteOrderFmt = '<'
        elif self.header['byte_order'] == 0xFEFF:
            self.byteOrder = 'big'
            self.byteOrderFmt = '>'
        else:
            raise ValueError("Invalid byte order 0x%04X in FRES header" %
                self.header['byte_order'])


    def decode(self):
        """Decode objects from the file."""
        self.rlt = RLT(self).readFromFRES()

        # str_tab_offset points to the first actual string, not
        # the header. (maybe it's actually the offset of some string,
        # which happens to be empty here?)
        offs = self.header['str_tab_offset'] - StringTable.Header.size
        self.strtab = StringTable().readFromFile(self, offs)

        self._readBufferSection()

        self.embeds = self._readObjects(
            EmbeddedFile, 'embed', EmbeddedFileHeader.size)

        self.models = self._readObjects(FMDL, 'fmdl',
            FMDLHeader.size)
        # XXX fska, fmaa, fvis, fshu, fscn


    def _readObjects(self, typ, name, size):
        """Read array of objects from the file."""
        offs = self.header[name + '_offset']
        cnt  = self.header[name + '_cnt']
        dofs = self.header[name + '_dict_offset']
        objs = []
        log.debug("Reading dict '%s' from 0x%X", name, dofs)
        if dofs == 0: return objs
        objDict = Dict(self).readFromFRES(dofs)
        for i in range(cnt):
            objName = objDict.root.left.name
            log.debug('Reading %s #%2d @ %06X: "%s"',
                typ.__name__, i, offs, objName)
            obj = typ(self, objName).readFromFRES(offs)
            objs.append(obj)
            offs += size
        return objs


    def _readBufferSection(self):
        """Read the BufferSection struct."""
        if self.header['buf_section_offset'] != 0:
            self.bufferSection = BufferSection().readFromFile(self.file,
                self.header['buf_section_offset'])
            log.debug("BufferSection at 0x%06X: unk=0x%X size=0x%X offs=0x%X",
                self.header['buf_section_offset'],
                self.bufferSection['unk00'],
                self.bufferSection['size'],
                self.bufferSection['buf_offs'])
        else:
            self.bufferSection = None
            log.debug("No BufferSection in this FRES")


    def _logRead(self, size, pos, count, rel):
        """Log reads to file for debug."""
        typ = '-'
        if type(size) is str:
            typ  = size
            size = struct.calcsize(size)
        elif type(size) is not int:
            typ  = type(size).__name__
            size = size.size
        size *= count
        file, line, func = '?', 0, '?'

        stack = traceback.extract_stack()
        for frame in reversed(stack):
            file, line, func = frame.filename, frame.lineno, frame.name
            file = file.split('/')
            if file[-1] == '__init__.py': file = file[0:-1]
            for i, p in enumerate(file):
                if p == 'bfres':
                    file = file[i+1:]
                    break
            file = '/'.join(file)

            ok = True
            if func in ('<lambda>', 'read', '_logRead', 'readStr', 'readHex', 'readHexWords', 'decode'):
                ok = False
            if file in (
                'Importer/Importer.py',
                'Importer/ImportOperator.py',
                'BinaryStruct',
                'BinaryStruct/BinaryObject.py',):
                ok = False
            if ok: break

        s = "%06X,%06X,%s,%d,%s,%s,%s\n" % (
            pos, size, file, line, func, typ, rel)
        self._readLogFile.write(s)


    def read(self, size:(int,str,BinaryStruct),
    pos:int=None, count:int=1,
    rel:bool=False):
        """Read data from file.

        fmt:   Number of bytes to read, or a `struct` format string,
               or a BinaryStruct.
        pos:   Position to seek to first. (optional)
        count: Number of items to read. If not 1, returns a list.

        Returns the data read.
        """
        if rel:
            log.warning("Read using rel=True: %s", traceback.extract_stack())
        if pos is None: pos = self.file.tell()
        if rel: pos += self.rlt.sections[1]['curOffset'] # XXX
        #self._logRead(size, pos, count, rel)
        return self.file.read(pos=pos, fmt=size, count=count)


    def seek(self, pos, whence=0):
        """Seek the file."""
        return self.file.seek(pos, whence)


    def tell(self):
        """Report the current position of the file."""
        return self.file.tell()


    def readStr(self, offset, fmt='<H', encoding='shift-jis'):
        """Read string (prefixed with length) from given offset."""
        size = self.read(fmt, offset)
        data = self.read(size)
        if encoding is not None: data = data.decode(encoding)
        return data


    def readHex(self, cnt, offset):
        """Read hex string for debugging."""
        data = self.read(cnt, offset)
        hx   = map(lambda b: '%02X' % b, data)
        return ' '.join(hx)


    def readHexWords(self, cnt, offset):
        data = self.read('I', offset, cnt)
        hx   = map(lambda b: '%08X' % b, data)
        return ' '.join(hx)
