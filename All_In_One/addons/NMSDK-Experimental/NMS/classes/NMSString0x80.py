# NMSString0x80 struct

from .Struct import Struct
from .String import String


class NMSString0x80(Struct):
    def __init__(self, **kwargs):
        self.size = 0x80
        super(NMSString0x80, self).__init__()

        """ Contents of the struct """
        self.data['Value'] = String(kwargs.get('Value', ""), 0x80)
        """ End of the struct contents"""
