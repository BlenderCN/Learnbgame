# GcDiscoveryTypes struct

from .Struct import Struct


class GcDiscoveryTypes(Struct):
    def __init__(self, **kwargs):
        super(GcDiscoveryTypes, self).__init__()

        """ Contents of the struct """
        self.data['DiscoveryType'] = kwargs.get('DiscoveryType', "Unknown")
        """ End of the struct contents"""
