# TkCameraWanderData struct

from .Struct import Struct


class TkCameraWanderData(Struct):
    def __init__(self, **kwargs):
        super(TkCameraWanderData, self).__init__()

        """ Contents of the struct """
        self.data['CamWander'] = kwargs.get('CamWander', False)
        self.data['CamWanderPhase'] = kwargs.get('CamWanderPhase', 0.003)
        self.data['CamWanderAmplitude'] = kwargs.get('CamWanderAmplitude', 0.5)
        """ End of the struct contents"""
