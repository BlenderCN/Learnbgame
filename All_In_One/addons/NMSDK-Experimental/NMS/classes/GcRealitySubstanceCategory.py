# GcRealitySubstanceCategory struct

from .Struct import Struct


class GcRealitySubstanceCategory(Struct):
    def __init__(self, **kwargs):
        super(GcRealitySubstanceCategory, self).__init__()

        """ Contents of the struct """
        self.data['SubstanceCategory'] = kwargs.get('SubstanceCategory',
                                                    "Commodity")
        """ End of the struct contents"""
