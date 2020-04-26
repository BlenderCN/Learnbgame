# GcAISpaceshipTypes struct

from .Struct import Struct


class GcAISpaceshipTypes(Struct):
    def __init__(self, **kwargs):
        super(GcAISpaceshipTypes, self).__init__()

        """ Contents of the struct """
        self.data['ShipType'] = kwargs.get('ShipType', "None")
        """ End of the struct contents"""
