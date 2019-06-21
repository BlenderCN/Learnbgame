# TkMaterialData struct

from .Struct import Struct
from .String import String


class TkMeshData(Struct):
    def __init__(self, **kwargs):
        super(TkMeshData, self).__init__()

        """ Contents of the struct """
        self.data['IdString'] = String(kwargs.get('IdString', ""), 0x80,
                                       endpadding=b'\xFE')
        self.data['Hash'] = kwargs.get('Hash', 0)
        self.data['VertexDataSize'] = kwargs.get('VertexDataSize', 0)
        self.data['IndexDataSize'] = kwargs.get('IndexDataSize', 0)
        """ End of the struct contents"""
