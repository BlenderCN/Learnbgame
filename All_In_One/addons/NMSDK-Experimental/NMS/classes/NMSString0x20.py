# NMSString0x20 struct

from .Struct import Struct
from .String import String


class NMSString0x20(Struct):
    def __init__(self, **kwargs):
        self.size = 0x20
        super(NMSString0x20, self).__init__()

        """ Contents of the struct """
        self.data['Value'] = String(kwargs.get('Value', ""), 0x20)
        """ End of the struct contents"""
