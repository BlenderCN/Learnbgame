import logging; log = logging.getLogger(__name__)
from bfres.BinaryStruct import BinaryStruct, BinaryObject
from bfres.BinaryStruct.Padding import Padding
from bfres.BinaryStruct.StringOffset import StringOffset
from bfres.BinaryStruct.Switch import Offset32, Offset64, String
from bfres.BinaryFile import BinaryFile
from .FresObject import FresObject


class Header(BinaryStruct):
    """Dict header."""
    fields = (
        ('4s', 'magic'), # "_DIC" or 0
        ('I',  'num_items'), # excluding root
    )
    size = 8


class Node(BinaryStruct):
    """A node in a Dict."""
    fields = (
        ('I',    'search_value'),
        ('H',    'left_idx'),
        ('H',    'right_idx'),
        String(  'name'),
        Offset32('data_offset'),
    )
    size = 16

    def readFromFile(self, file, offset):
        data = super().readFromFile(file, offset)
        self.search_value = data['search_value']
        self.left_idx     = data['left_idx']
        self.right_idx    = data['right_idx']
        self.name         = data['name']
        self.data_offset  = data['data_offset']
        self.left         = None
        self.right        = None
        return self


class Dict(FresObject):
    """A name dict in an FRES."""

    def __init__(self, fres):
        self.fres  = fres
        self.nodes = []


    def dump(self):
        """Dump to string for debug."""
        res  = [
            "  Dict, %3d items, magic = %s" % (
                len(self.nodes), self.header['magic'],
            ),
            "\x1B[4mNode│Search  │Left│Rght│DataOffs│Name\x1B[0m",
        ]
        for i, node in enumerate(self.nodes):
            res.append('%4d│%08X│%4d│%4d│%08X│"%s"' % (
                i, node.search_value, node.left_idx, node.right_idx,
                node.data_offset, node.name,
            ))
        return '\n'.join(res).replace('\n', '\n  ')


    def readFromFRES(self, offset):
        """Read this object from the FRES."""
        self.header = Header().readFromFile(self.fres.file, offset)

        #log.debug("Dict @ 0x%06X: unk00=0x%08X num_items=%d",
        #    offset,
        #    self.header['unk00'],
        #    self.header['num_items'],
        #)
        offset += Header.size

        # read nodes (+1 for root node)
        for i in range(self.header['num_items'] + 1):
            node = Node().readFromFile(self.fres.file, offset)
            self.nodes.append(node)
            #log.debug('Node %3d: S=0x%08X I=0x%04X,0x%04X D=0x%06X "%s"',
            #    i, node.search_value, node.left_idx,
            #    node.right_idx, node.data_offset, node.name,
            #)
            offset += Node.size

        # build tree
        self.root = self.nodes[0]
        for i, node in enumerate(self.nodes):
            try: node.left  = self.nodes[node.left_idx]
            except IndexError: node.left = None
            try: node.right = self.nodes[node.right_idx]
            except IndexError: node.right = None

        return self
