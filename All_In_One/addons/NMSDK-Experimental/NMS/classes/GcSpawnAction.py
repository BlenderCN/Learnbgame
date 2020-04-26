# GcSpawnAction struct

from .Struct import Struct


class GcSpawnAction(Struct):
    def __init__(self, **kwargs):
        super(GcSpawnAction, self).__init__()

        """ Contents of the struct """
        self.data['Event'] = kwargs.get('Event', "")
        """ End of the struct contents"""
