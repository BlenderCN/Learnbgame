# GcEncyclopediaComponentData struct

from .Struct import Struct
from .GcDiscoveryTypes import GcDiscoveryTypes


class GcEncyclopediaComponentData(Struct):
    def __init__(self, **kwargs):
        super(GcEncyclopediaComponentData, self).__init__()

        """ Contents of the struct """
        self.data['Type'] = kwargs.get('Type', GcDiscoveryTypes())
        """ End of the struct contents"""
