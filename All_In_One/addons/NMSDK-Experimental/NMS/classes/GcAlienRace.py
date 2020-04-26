# GcAlienRace struct

from .Struct import Struct


class GcAlienRace(Struct):
    def __init__(self, **kwargs):
        super(GcAlienRace, self).__init__()

        """ Contents of the struct """
        self.data['AlienRace'] = kwargs.get('AlienRace', "Warriors")
        """ End of the struct contents"""
