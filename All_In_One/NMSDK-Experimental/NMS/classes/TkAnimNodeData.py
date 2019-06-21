# TkAnimNodeData struct

from .Struct import Struct
from .String import String


class TkAnimNodeData(Struct):
    def __init__(self, **kwargs):
        super(TkAnimNodeData, self).__init__()

        """ Contents of the struct """
        self.data['Node'] = String(kwargs.get('Node', ""), 0x10)
        # String(chr(0xFE)*4, 4))
        self.data['CanCompress'] = kwargs.get('CanCompress', False)
        self.data['RotIndex'] = kwargs.get('RotIndex', 0)
        self.data['TransIndex'] = kwargs.get('TransIndex', 0)
        self.data['ScaleIndex'] = kwargs.get('ScaleIndex', 0)
        """ End of the struct contents"""
