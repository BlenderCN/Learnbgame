import logging; log = logging.getLogger(__name__)
from bfres.BinaryStruct import BinaryStruct
from bfres.BinaryStruct.Padding import Padding
from bfres.BinaryStruct.Switch import String
from bfres.FRES.FresObject import FresObject
from .types import attrFmts


class AttrStruct(BinaryStruct):
    """The Attribute structure in the file."""
    fields = (
        String('name'),
        ('I',  'unk04'),
        ('H',  'format'),
        Padding(2),
        ('H',  'buf_offs'),
        ('H',  'buf_idx'),
    )
    size = 0x10


class Attribute(FresObject):
    """An attribute in a FRES."""
    def __init__(self, fvtx):
        self.fvtx = fvtx


    def readFromFRES(self, offset=None):
        """Read the attribute from given FRES."""
        data = self.fvtx.fres.read(AttrStruct(), offset)
        self.name     = data['name']
        self.unk04    = data['unk04']
        self.formatID = data['format']
        self.buf_offs = data['buf_offs']
        self.buf_idx  = data['buf_idx']
        self.format   = attrFmts.get(self.formatID, None)
        if self.format is None:
            log.warning("FMDL Attribute: Unknown format 0x%04X",
                self.formatID)
        return self


    def dump(self, ind=0):
        """Dump to string for debug."""
        inds = ('  ' * ind)
        return '%s%3d│%06X│%04X %-8s│%08X│"%s"' % (
            inds,
            self.buf_idx,
            self.buf_offs,
            self.formatID,
            self.format['name'],
            self.unk04,
            self.name,
        )
