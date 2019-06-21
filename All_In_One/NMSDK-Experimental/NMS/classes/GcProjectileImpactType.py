# GcProjectileImpactType struct

from .Struct import Struct


class GcProjectileImpactType(Struct):
    def __init__(self, **kwargs):
        super(GcProjectileImpactType, self).__init__()

        """ Contents of the struct """
        self.data['Impact'] = kwargs.get('Impact', "Default")
        """ End of the struct contents"""
