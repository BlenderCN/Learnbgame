# TkRotationComponentData struct

from .Struct import Struct
from .Vector4f import Vector4f


class TkRotationComponentData(Struct):
    def __init__(self, **kwargs):
        super(TkRotationComponentData, self).__init__()

        """ Contents of the struct """
        self.data['Speed'] = kwargs.get('Speed', 1)
        self.data['Axis'] = kwargs.get('Axis', Vector4f(x=0, y=1, z=0, t=0))
        """ End of the struct contents"""
