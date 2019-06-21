# GcPlayAudioAction struct

from .Struct import Struct


class GcPlayAudioAction(Struct):
    def __init__(self, **kwargs):
        super(GcPlayAudioAction, self).__init__()

        """ Contents of the struct """
        self.data['Sound'] = kwargs.get('Sound', "")
        self.data['UseOcclusion'] = bool(kwargs.get('UseOcclusion', False))
        self.data['OcclusionRadius'] = kwargs.get('OcclusionRadius', 0)
        """ End of the struct contents"""
