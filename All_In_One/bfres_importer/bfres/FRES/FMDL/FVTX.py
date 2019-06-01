import logging; log = logging.getLogger(__name__)
from bfres.BinaryStruct import BinaryStruct, BinaryObject
from bfres.BinaryStruct.Padding import Padding
from bfres.BinaryStruct.StringOffset import StringOffset
from bfres.BinaryStruct.Switch import Offset32, Offset64, String
from bfres.BinaryFile import BinaryFile
from bfres.FRES.FresObject import FresObject
from bfres.FRES.Dict import Dict
from bfres.Exceptions import MalformedFileError
from .Attribute import Attribute, AttrStruct
from .Buffer import Buffer
from .Vertex import Vertex
import struct
import math


class BufferStrideStruct(BinaryStruct):
    """Vertex buffer stride info."""
    fields = (
        ('i', 'stride'),
        ('I', 'divisor'), # should be 0
        ('I', 'reserved1'),
        ('I', 'reserved2'),
    )
    size = 0x10


class BufferSizeStruct(BinaryStruct):
    """Vertex buffer size info."""
    fields = (
        ('I', 'size'),
        ('I', 'gpuAccessFlags'), # should be 5
        ('I', 'reserved1'),
        ('I', 'reserved2'),
    )
    size = 0x10


class Header(BinaryStruct):
    """FVTX header."""
    magic  = b'FVTX'
    fields = (
        ('4s',   'magic'), # 0x00
        Padding(12), # 0x04
        Offset64('vtx_attrib_array_offs'), # 0x10
        Offset64('vtx_attrib_dict_offs'), # 0x18
        Offset64('mem_pool'), # 0x20
        Offset64('unk28'), # 0x28
        Offset64('unk30'), # 0x30
        Offset64('vtx_bufsize_offs'), # 0x38 => BufferSizeStruct
        Offset64('vtx_stridesize_offs'), # 0x40 => BufferStrideStruct
        Offset64('vtx_buf_array_offs'), # 0x48
        Offset32('vtx_buf_offs'), # 0x50
        ('B',    'num_attrs'), # 0x54
        ('B',    'num_bufs'), # 0x55
        ('H',    'index'), # 0x56; Section index: index into FVTX array of this entry.
        ('I',    'num_vtxs'), # 0x58
        ('I',    'skin_weight_influence'), # 0x5C
    )
    size = 0x60


class FVTX(FresObject):
    """A vertex buffer in an FRES."""
    Header = Header

    def __init__(self, fres):
        self.fres         = fres
        self.header       = None
        self.headerOffset = None
        self.attrs        = []
        self.buffers      = []
        self.vtx_attrib_dict = None


    def __str__(self):
        return "<FVTX(@%s) at 0x%x>" %(
            '?' if self.headerOffset is None else hex(self.headerOffset),
            id(self),
        )


    def dump(self):
        """Dump to string for debug."""
        res = []
        res.append('  FVTX index %2d: %3d attrs, %3d buffers, %4d vtxs; Skin weight influence: %d' % (
            self.header['index'],
            self.header['num_attrs'],
            self.header['num_bufs'],
            self.header['num_vtxs'],
            self.header['skin_weight_influence'],
        ))
        res.append('  Mem Pool: 0x%08X' %
            self.header['mem_pool'],
        )
        res.append('  Unk28: 0x%08X 0x%08X' % (
            self.header['unk28'], self.header['unk30'],
        ))
        res.append('  Attrib Array: 0x%06X, Dict:   0x%06X' % (
            self.header['vtx_attrib_array_offs'],
            self.header['vtx_attrib_dict_offs'],
        ))
        res.append("  Attrib Dict: "+
            self.vtx_attrib_dict.dump().replace('\n', '\n  '))

        if len(self.attrs) > 0:
            res.append('  Attribute Dump:')
            res.append('    \x1B[4m#  │Idx│BufOfs│Format       │Unk04   │Attr Name\x1B[0m')
            for i, attr in enumerate(self.attrs):
                res.append('    %3d│%s' % (i, attr.dump()))

        res.append('  Buffer Array: 0x%06X, Data:   0x%06X' % (
            self.header['vtx_buf_array_offs'],
            self.header['vtx_buf_offs'],
        ))
        res.append('  BufSiz Array: 0x%06X, Stride: 0x%06X' % (
            self.header['vtx_bufsize_offs'],
            self.header['vtx_stridesize_offs'],
        ))

        if len(self.buffers) > 0:
            res.append('    \x1B[4mOffset│Size│Strd│Buffer data\x1B[0m')
            for buf in self.buffers:
                res.append('    ' + buf.dump())
        return '\n'.join(res).replace('\n', '\n  ')


    def readFromFRES(self, offset=None):
        """Read this object from given file."""
        if offset is None: offset = self.fres.file.tell()
        log.debug("Reading FVTX from 0x%06X", offset)
        self.headerOffset = offset
        self.header = self.fres.read(Header(), offset)

        try:
            self._readDicts()
            self._readBuffers()
            self._readAttrs()
            self._readVtxs()
        except struct.error:
            log.exception("Error reading FVTX")
            raise
        return self


    def _readDicts(self):
        """Read the dicts belonging to this FVTX."""
        self.vtx_attrib_dict = Dict(self.fres)
        self.vtx_attrib_dict.readFromFRES(
            self.header['vtx_attrib_dict_offs'])


    def _readBuffers(self):
        """Read the attribute data buffers."""
        #dataOffs = self.header['vtx_buf_offs'] + \
        #    self.fres.rlt.sections[1]['curOffset']
        dataOffs = self.header['vtx_buf_offs'] + \
            self.fres.bufferSection['buf_offs']
        bufSize    = self.header['vtx_bufsize_offs']
        strideSize = self.header['vtx_stridesize_offs']
        log.debug("FVTX offsets: dataOffs=0x%X bufSize=0x%X strideSize=0x%X bufferSection.size=0x%X, offs=0x%X, vtx_buf_offs=0x%X",
            dataOffs, bufSize, strideSize,
            self.fres.bufferSection['size'],
            self.fres.bufferSection['buf_offs'],
            self.header['vtx_buf_offs'])

        self.buffers = []
        file = self.fres.file
        for i in range(self.header['num_bufs']):
            #log.debug("Read buffer %d from 0x%X", i, dataOffs)
            n = i*0x10
            sizeStruct = BufferSizeStruct().readFromFile(
                self.fres, bufSize+n)
            strideStruct = BufferStrideStruct().readFromFile(
                self.fres, strideSize+n)
            size   = sizeStruct['size']
            stride = strideStruct['stride']
            if strideStruct['divisor'] != 0:
                log.warning("Buffer %d stride divisor is %d, expected 0", i, strideStruct['divisor'])

            #size   = self.fres.read('I', bufSize+n)
            #stride = self.fres.read('I', strideSize+n)
            buf    = Buffer(self.fres, size, stride, dataOffs)
            self.buffers.append(buf)
            dataOffs += buf.size


    def _readAttrs(self):
        """Read the attribute definitions."""
        self.attrs = []
        self.attrsByName = {}
        offs = self.header['vtx_attrib_array_offs']
        for i in range(self.header['num_attrs']):
            attr = Attribute(self).readFromFRES(offs)
            self.attrs.append(attr)
            self.attrsByName[attr.name] = attr
            offs += AttrStruct.size


    def _readVtxs(self):
        """Read the vertices from the buffers."""
        self.vtxs = []
        for iVtx in range(self.header['num_vtxs']):
            vtx = Vertex()
            for attr in self.attrs: # get the data for each attribute
                if attr.buf_idx >= len(self.buffers) or attr.buf_idx < 0:
                    log.error("Attribute '%s' uses buffer %d, but max index is %d",
                        attr.name, attr.buf_idx, len(self.buffers)-1)
                    raise MalformedFileError("Invalid buffer index for attribute "+attr.name)
                buf  = self.buffers[attr.buf_idx]
                offs = attr.buf_offs + (iVtx * buf.stride)
                fmt  = attr.format
                #log.debug("Read attr '%s' from buffer %d, offset 0x%X, stride 0x%X, fmt %s",
                #    attr.name, attr.buf_idx, attr.buf_offs,
                #    buf.stride, fmt['name'])

                # get the conversion function if any
                func = None
                if type(fmt) is dict:
                    func = fmt.get('func', None)
                    fmt  = fmt['fmt']

                # get the data
                try:
                    data = struct.unpack_from(fmt, buf.data, offs)
                except struct.error:
                    log.error("Attribute '%s' reading out of bounds from buffer %d (vtx %d of %d = offset 0x%X fmt '%s', max = 0x%X)",
                        attr.name, attr.buf_idx, iVtx,
                        self.header['num_vtxs'], offs, fmt,
                        len(buf.data))
                    raise MalformedFileError("Invalid buffer offset for attribute "+attr.name)
                if func: data = func(data)

                # validate
                d = data
                if type(d) not in (list, tuple): d = [d]
                for v in d:
                    if math.isinf(v) or math.isnan(v):
                        log.warning("%s value in attribute %s vtx %d (offset 0x%X buffer %d base 0x%X)",
                            str(v), attr.name, iVtx, offs,
                            attr.buf_idx, attr.buf_offs)

                vtx.setAttr(attr, data)

            self.vtxs.append(vtx)
