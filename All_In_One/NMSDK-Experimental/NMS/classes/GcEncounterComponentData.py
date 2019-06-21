# GcEncounterComponentData struct

from .Struct import Struct


class GcEncounterComponentData(Struct):
    def __init__(self, **kwargs):
        super(GcEncounterComponentData, self).__init__()

        """ Contents of the struct """
        self.data['EncounterType'] = kwargs.get('EncounterType',
                                                "FactoryGuards")
        """ End of the struct contents"""
