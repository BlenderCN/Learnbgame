# TkTransformData struct

from .Struct import Struct


class TkTransformData(Struct):
    def __init__(self, **kwargs):
        super(TkTransformData, self).__init__()

        """ Contents of the struct """
        self.data['TransX'] = kwargs.get('TransX', 0)
        self.data['TransY'] = kwargs.get('TransY', 0)
        self.data['TransZ'] = kwargs.get('TransZ', 0)
        self.data['RotX'] = kwargs.get('RotX', 0)
        self.data['RotY'] = kwargs.get('RotY', 0)
        self.data['RotZ'] = kwargs.get('RotZ', 0)
        self.data['ScaleX'] = kwargs.get('ScaleX', 1)
        self.data['ScaleY'] = kwargs.get('ScaleY', 1)
        self.data['ScaleZ'] = kwargs.get('ScaleZ', 1)
        """ End of the struct contents"""
