# TkModelRendererCameraData struct

from .Struct import Struct
from .Vector4f import Vector4f
from .TkCameraWanderData import TkCameraWanderData


class TkModelRendererCameraData(Struct):
    def __init__(self, **kwargs):
        super(TkModelRendererCameraData, self).__init__()

        """ Contents of the struct """
        self.data['Distance'] = kwargs.get('Distance', 1.400001)
        self.data['Offset'] = kwargs.get('Offset', Vector4f())
        self.data['Pitch'] = kwargs.get('Pitch', 1.999992)
        self.data['Rotate'] = kwargs.get('Rotate', 210)
        self.data['LightPitch'] = kwargs.get('LightPitch', 45)
        self.data['LightRotate'] = kwargs.get('LightRotate', 45)
        self.data['Wander'] = kwargs.get('Wander', TkCameraWanderData())
        """ End of the struct contents"""
