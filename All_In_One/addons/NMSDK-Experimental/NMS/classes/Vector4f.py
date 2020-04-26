# Vector4f struct

from .Struct import Struct
from struct import pack


class Vector4f(Struct):
    def __init__(self, **kwargs):
        super(Vector4f, self).__init__()

        """ Contents of the struct """
        self.data['x'] = kwargs.get('x', 0.0)
        self.data['y'] = kwargs.get('y', 0.0)
        self.data['z'] = kwargs.get('z', 0.0)
        self.data['t'] = kwargs.get('t', 0.0)
        """ End of the struct contents"""

    def __bytes__(self):
        data = bytearray()
        for d in ['x', 'y', 'z', 't']:
            data.extend(pack('<f', self.data[d]))
        return bytes(data)
