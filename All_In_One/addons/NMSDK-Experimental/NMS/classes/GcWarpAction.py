# GcWarpAction struct

from .Struct import Struct


class GcWarpAction(Struct):
    def __init__(self, **kwargs):
        super(GcWarpAction, self).__init__()

        """ Contents of the struct """
        self.data['WarpType'] = kwargs.get('WarpType', "BlackHole")
        """ End of the struct contents"""
