# GcCameraShakeAction struct

from .Struct import Struct


class GcCameraShakeAction(Struct):
    def __init__(self, **kwargs):
        super(GcCameraShakeAction, self).__init__()

        """ Contents of the struct """
        self.data['Shake'] = kwargs.get('Shake', "")
        self.data['FalloffMin'] = kwargs.get('FalloffMin', 0)
        self.data['FalloffMax'] = kwargs.get('FalloffMax', 0)
        """ End of the struct contents"""
