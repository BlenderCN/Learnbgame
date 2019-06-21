# GcStatsEnum struct

from .Struct import Struct


class GcStatsEnum(Struct):
    def __init__(self, **kwargs):
        super(GcStatsEnum, self).__init__()

        """ Contents of the struct """
        self.data['Stat'] = kwargs.get('Stat', "None")
        """ End of the struct contents"""
