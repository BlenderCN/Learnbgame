import logging; log = logging.getLogger(__name__)
from bfres.BinaryStruct import BinaryStruct, BinaryObject
from bfres.BinaryStruct.Padding import Padding
from bfres.BinaryStruct.StringOffset import StringOffset
from bfres.BinaryStruct.Switch import Offset32, Offset64, String
from bfres.BinaryFile import BinaryFile
from bfres.FRES.FresObject import FresObject
from bfres.FRES.Dict import Dict
from bfres.Exceptions import MalformedFileError
import struct


primTypes = {
    # where did these come from?
    # id: (min, incr, name)
    #0x01: (1, 1, 'points'),
    #0x02: (2, 2, 'lines'),
    #0x03: (2, 1, 'line_strip'),
    #0x04: (3, 3, 'triangles'),
    #0x05: (3, 1, 'triangle_fan'),
    #0x06: (3, 1, 'triangle_strip'),
    #0x0A: (4, 4, 'lines_adjacency'),
    #0x0B: (4, 1, 'line_strip_adjacency'),
    #0x0C: (6, 1, 'triangles_adjacency'),
    #0x0D: (6, 6, 'triangle_strip_adjacency'),
    #0x11: (3, 3, 'rects'),
    #0x12: (2, 1, 'line_loop'),
    #0x13: (4, 4, 'quads'),
    #0x14: (4, 2, 'quad_strip'),
    #0x82: (2, 2, 'tesselate_lines'),
    #0x83: (2, 1, 'tesselate_line_strip'),
    #0x84: (3, 3, 'tesselate_triangles'),
    #0x86: (3, 1, 'tesselate_triangle_strip'),
    #0x93: (4, 4, 'tesselate_quads'),
    #0x94: (4, 2, 'tesselate_quad_strip'),

    # according to Jasper...
    # id: (min, incr, name)
    0x00: (1, 1, 'point_list'),
    0x01: (2, 2, 'line_list'),
    0x02: (2, 1, 'line_strip'),
    0x03: (3, 3, 'triangle_list'),
}
idxFormats = {
    0x00: '<I', # I/H are backward from gx2Enum.h???
    0x01: '<H',
    0x02: '<I',
    0x04: '>I',
    0x09: '>H',
}


class Header(BinaryStruct):
    """LOD header."""
    fields = (
        Offset64('submesh_array_offs'), # 0x00
        Offset64('unk08'), # 0x08
        Offset64('unk10'), # 0x10
        Offset64('idx_buf_offs'), # 0x18 -> buffer size in bytes
        ('I',    'face_offs'),    # 0x20; offset into index buffer
        ('I',    'prim_fmt'),     # 0x24; how to draw the faces
        ('I',    'idx_type'),     # 0x28; data type of index buffer entries
        ('I',    'idx_cnt'),      # 0x2C; total number of indices
        ('H',    'visibility_group'), # 0x30
        ('H',    'submesh_cnt'), # 0x32
        ('I',    'unk34'),       # 0x34
    )
    size = 0x38


class LOD(FresObject):
    """A level-of-detail model in an FRES."""
    Header = Header

    def __init__(self, fres):
        self.fres         = fres
        self.header       = None
        self.headerOffset = None


    def __str__(self):
        return "<FSHP(@%s) at 0x%x>" %(
            '?' if self.headerOffset is None else hex(self.headerOffset),
            id(self),
        )


    def dump(self):
        """Dump to string for debug."""
        res = []
        #res.append("Submeshes: %d" % len(self.submeshes))
        #res.append("IdxBuf:    0x%04X bytes" % len(self.idx_buf))
        #res.append("PrimFmt:   0x%04X (%s)" % (
        #    self.prim_fmt_id, self.prim_fmt))
        #res.append("IdxType:   0x%02X (%s)" % (
        #    self.header['idx_type'], self.idx_fmt,
        #))
        #res.append("IdxCnt:    %d" % self.header['idx_cnt'])
        #res.append("VisGrp:    %d" % self.header['visibility_group'])
        #res.append("Unknown:   0x%08X 0x%08X 0x%08X" % (
        #    self.header['unk08'],
        #    self.header['unk10'],
        #    self.header['unk34'],
        #))
        #return '\n'.join(res).replace('\n', '\n    ')

        return "%4d│%04X│%04X %-24s│%02X %s│%5d│%5d│%08X│%08X│%08X" %(
            len(self.submeshes),
            len(self.idx_buf),
            self.prim_fmt_id, self.prim_fmt,
            self.header['idx_type'], self.idx_fmt,
            self.header['idx_cnt'],
            self.header['visibility_group'],
            self.header['unk08'], self.header['unk10'],
            self.header['unk34'],
        )


    def readFromFRES(self, offset=None):
        """Read this object from given file."""
        if offset is None: offset = self.fres.file.tell()
        log.debug("Reading LOD  from 0x%06X", offset)
        self.headerOffset = offset
        self.header = self.fres.read(Header(), offset)

        # decode primitive and index formats
        self.prim_fmt_id = self.header['prim_fmt']
        try:
            self.prim_min, self.prim_size, self.prim_fmt = \
                primTypes[self.header['prim_fmt']]
        except KeyError:
            raise MalformedFileError("Unknown primitive format 0x%X" %
                self.header['prim_fmt'])

        try:
            self.idx_fmt = idxFormats[self.header['idx_type']]
        except KeyError:
            raise MalformedFileError("Unknown index type 0x%X" %
                self.header['idx_type'])

        self._readIdxBuf()
        self._readSubmeshes()

        return self


    def _readIdxBuf(self):
        """Read the index buffer."""
        base  = self.fres.bufferSection['buf_offs']
        self.idx_buf = self.fres.read(self.idx_fmt,
            pos   = self.header['face_offs'] + base,
            count = self.header['idx_cnt'])

        for i in range(self.header['idx_cnt']):
            self.idx_buf[i] += self.header['visibility_group']


    def _readSubmeshes(self):
        """Read the submeshes."""
        self.submeshes = []
        base = self.header['submesh_array_offs']
        # XXX is this right, adding 1 here?
        for i in range(self.header['submesh_cnt']+1):
            offs, cnt = self.fres.read('2I', base + (i*8))
            idxs = self.idx_buf[offs:offs+cnt] # XXX offs / size?
            self.submeshes.append({
                'offset': offs,
                'count':  cnt,
                'idxs':   idxs,
            })
            #log.debug("FVTX submesh %d: offset=0x%06X count=0x%04X idxs=%s",
            #    i, offs, cnt, idxs)
