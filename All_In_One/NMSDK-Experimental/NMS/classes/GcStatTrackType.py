# GcStatTrackType  struct

from .Struct import Struct


class GcStatTrackType (Struct):
    def __init__(self, **kwargs):
        super(GcStatTrackType , self).__init__()

        """ Contents of the struct """
        self.data['StatTrackType'] = kwargs.get('StatTrackType', "SET")
        """ End of the struct contents"""
