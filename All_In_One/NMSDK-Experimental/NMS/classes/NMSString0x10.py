# NMSString0x10 struct

from .Struct import Struct


class NMSString0x10(Struct):
    def __init__(self, **kwargs):
        super(NMSString0x10, self).__init__()

        """ Contents of the struct """
        self.data['Value'] = String(kwargs.get('Value', ""), 0x10)
        """ End of the struct contents"""
