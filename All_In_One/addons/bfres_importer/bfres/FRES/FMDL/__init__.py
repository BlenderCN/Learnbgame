import logging; log = logging.getLogger(__name__)
from bfres.BinaryStruct import BinaryStruct, BinaryObject
from bfres.BinaryStruct.Padding import Padding
from bfres.BinaryStruct.StringOffset import StringOffset
from bfres.BinaryStruct.Switch import Offset32, Offset64, String
from bfres.BinaryFile import BinaryFile
from .FMAT import FMAT
from .FVTX import FVTX
from .FSHP import FSHP
from .FSKL import FSKL
from bfres.FRES.FresObject import FresObject


class Header(BinaryStruct):
    """FMDL header."""
    # offsets in this struct are relative to the beginning of
    # the FRES file.
    # I'm assuming they're 64-bit since most are a 32-bit offset
    # followed by 4 zero bytes.
    magic  = b'FMDL'
    fields = (
        ('4s',   'magic'),
        ('I',    'size'),
        Offset64('block_offset'), # always == size?
        String(  'name', fmt='Q'),
        Offset64('str_tab_end'),

        Offset64('fskl_offset'),
        Offset64('fvtx_offset'),
        Offset64('fshp_offset'),
        Offset64('fshp_dict_offset'),
        Offset64('fmat_offset'),
        Offset64('fmat_dict_offset'),
        Offset64('udata_offset'),
        Padding(16),

        ('H',  'fvtx_count'),
        ('H',  'fshp_count'),
        ('H',  'fmat_count'),
        ('H',  'udata_count'),
        ('H',  'total_vtxs'),
        Padding(6),
    )
    size = 0x78


class FMDL(FresObject):
    """A 3D model in an FRES."""

    def __init__(self, fres, name=None):
        self.name         = name
        self.fres         = fres
        self.headerOffset = None
        self.header       = None
        self.fvtxs        = []
        self.fshps        = []
        self.fmats        = []
        self.udatas       = []
        self.totalVtxs    = None
        self.skeleton     = None


    def __str__(self):
        return "<FMDL('%s': @ %s) at 0x%x>" %(
            str(self.name),
            '?' if self.headerOffset is None else hex(self.headerOffset),
            id(self),
        )


    def dump(self):
        """Dump to string for debug."""
        res = []
        res.append('  Model "%s":'  % self.name)
        res.append('%4d FVTXs,'     % self.header['fvtx_count'])
        res.append('%4d FSHPs,'     % self.header['fshp_count'])
        res.append('%4d FMATs,'     % self.header['fmat_count'])
        res.append('%4d Udatas,'    % self.header['udata_count'])
        res.append('%4d total vtxs' % self.header['total_vtxs'])
        res = [' '.join(res)]

        for fvtx in self.fvtxs:
            res.append(fvtx.dump())

        for i, fmat in enumerate(self.fmats):
            res.append('  FMAT %d:' % i)
            res.append('  '+fmat.dump().replace('\n', '\n  '))

        self._dumpFshps(res)
        res.append('Skeleton:')
        res.append(self.skeleton.dump())
        return '\n'.join(res).replace('\n', '\n  ')


    def _dumpFshps(self, res):
        for i, fshp in enumerate(self.fshps):
            res.append('  FSHP %3d: %s' % (i, fshp.dump()))

        res.append('  \x1B[4mFSHP│LOD│Mshs│IdxB│PrimType'+
            '                     │'+
            'IdxTp│IdxCt│VisGp│Unk08   │Unk10   │Unk34   \x1B[0m')
        for i, fshp in enumerate(self.fshps):
            for j, lod in enumerate(fshp.lods):
                res.append('  %s%4d│%3d│%s\x1B[0m' % (
                    '\x1B[4m' if j == len(fshp.lods) - 1 else '',
                    i, j, lod.dump()))


    def readFromFRES(self, offset=None):
        """Read this object from FRES."""
        if offset is None: offset = self.fres.file.tell()
        self.headerOffset = offset
        self.header = self.fres.read(Header(), offset)
        self.name   = self.header['name']

        self.fmats = self._readObjects('fmat', FMAT)
        self.fvtxs = self._readObjects('fvtx', FVTX)
        self.fshps = self._readObjects('fshp', FSHP)
        self.skeleton = FSKL(self.fres).readFromFRES(
            self.header['fskl_offset'])
        # XXX udata
        return self


    def _readObjects(self, name, cls):
        """Read objects."""
        objs = []
        offs = self.header[name + '_offset']
        for i in range(self.header[name + '_count']):
            vtx = cls(self.fres).readFromFRES(offs)
            objs.append(vtx)
            offs += cls.Header.size
        return objs
