# TkVertexElement struct

from .Struct import Struct
from .String import String
from struct import pack


class TkVertexElement(Struct):
    def __init__(self, **kwargs):
        super(TkVertexElement, self).__init__()

        """ Contents of the struct """
        self.data['SemanticID'] = kwargs.get('SemanticID', 0)
        self.data['Size'] = kwargs.get('Size', 0)
        self.data['Type'] = kwargs.get('Type', 0)
        self.data['Offset'] = kwargs.get('Offset', 0)
        self.data['Normalise'] = kwargs.get('Normalise', 0)
        self.InstancingDict = {'PerVertex': 0, 'PerModel': 1}
        self.data['Instancing'] = kwargs.get('Instancing', 0)
        self.data['PlatformData'] = String(kwargs.get('PlatformData', ""), 0x8)
        """ End of the struct contents"""

    def __bytes__(self):
        data = bytearray()
        for key in self.data:
            if key != 'PlatformData':
                if key == 'Instancing':
                    data.extend(pack('<i',
                                     self.InstancingDict[self.data[key]]))
                else:
                    data.extend(pack('<i', self.data[key]))
            else:
                data.extend(bytes(self.data['PlatformData']))
        return bytes(data)
