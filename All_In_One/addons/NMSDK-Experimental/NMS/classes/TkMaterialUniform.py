# TkMaterialUniform struct

from .Struct import Struct
from .String import String
from .Vector4f import Vector4f
from .List import List


class TkMaterialUniform(Struct):
    def __init__(self, **kwargs):
        super(TkMaterialUniform, self).__init__()

        """ Contents of the struct """
        self.data['Name'] = String(kwargs.get('Name', None), 0x20)
        self.data['Values'] = kwargs.get('Values', Vector4f())
        self.data['ExtendedValues'] = kwargs.get('ExtendedValues', List())
        """ End of the struct contents"""
