# TkVertexLayout struct

from .Struct import Struct
from .String import String
from .List import List


class TkVertexLayout(Struct):
    def __init__(self, **kwargs):
        super(TkVertexLayout, self).__init__()

        """ Contents of the struct """
        self.data['ElementCount'] = kwargs.get('ElementCount', 0)
        self.data['Stride'] = kwargs.get('Stride', 0)
        self.data['PlatformData'] = String(kwargs.get('PlatformData', ""), 0x8)
        self.data['VertexElements'] = kwargs.get('VertexElements', List())
        """ End of the struct contents"""
