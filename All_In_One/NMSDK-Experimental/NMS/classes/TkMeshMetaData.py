# TkMaterialData struct

from .Struct import Struct
from .String import String


class TkMeshMetaData(Struct):
    def __init__(self, **kwargs):
        super(TkMeshMetaData, self).__init__()

        """ Contents of the struct """
        self.data['Name'] = String(kwargs.get('Name', ""), 0x80)
        self.data['Hash'] = kwargs.get('Hash', 0)
        self.data['VertexDataSize'] = kwargs.get('VertexDataSize', 0)
        self.data['VertexDataOffset'] = kwargs.get('VertexDataOffset', 0)
        self.data['IndexDataSize'] = kwargs.get('IndexDataSize', 0)
        self.data['IndexDataOffset'] = kwargs.get('IndexDataOffset', 0)
        """ End of the struct contents"""
