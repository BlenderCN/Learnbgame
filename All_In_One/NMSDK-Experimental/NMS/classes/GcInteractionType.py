# GcInteractionType struct

from .Struct import Struct


class GcInteractionType(Struct):
    def __init__(self, **kwargs):
        super(GcInteractionType, self).__init__()

        """ Contents of the struct """
        self.data['InteractionType'] = kwargs.get('InteractionType', "NPC")
        """ End of the struct contents"""
