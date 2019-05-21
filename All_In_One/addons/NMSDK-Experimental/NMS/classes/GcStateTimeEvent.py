# GcStateTimeEvent struct

from .Struct import Struct


class GcStateTimeEvent(Struct):
    def __init__(self, **kwargs):
        super(GcStateTimeEvent, self).__init__()

        """ Contents of the struct """
        self.data['Seconds'] = kwargs.get('Seconds', 0)
        """ End of the struct contents"""
