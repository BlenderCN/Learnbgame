# TkAudioComponentData struct

from .Struct import Struct
from .List import List


class TkAudioComponentData(Struct):
    def __init__(self, **kwargs):
        super(TkAudioComponentData, self).__init__()

        """ Contents of the struct """
        self.data['Ambient'] = kwargs.get('Ambient', '')
        self.data['MaxDistance'] = kwargs.get('MaxDistance', 0)
        self.data['AnimTriggers'] = kwargs.get('AnimTriggers', List())
        """ End of the struct contents"""
