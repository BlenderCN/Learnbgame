# GcSubstanceAmount struct

from .Struct import Struct
from .GcRealitySubstanceCategory import GcRealitySubstanceCategory
from .GcRarity import GcRarity


class GcSubstanceAmount(Struct):
    def __init__(self, **kwargs):
        super(GcSubstanceAmount, self).__init__()

        """ Contents of the struct """
        self.data['AmountMin'] = kwargs.get('AmountMin', 0)
        self.data['AmountMax'] = kwargs.get('AmountMax', 0)
        self.data['Specific'] = kwargs.get('Specific', "")
        self.data['SpecificSecondary'] = kwargs.get('SpecificSecondary', "")
        self.data['SubstanceCategory'] = kwargs.get(
            'SubstanceCategory', GcRealitySubstanceCategory())
        self.data['Rarity'] = kwargs.get('Rarity', GcRarity())
        """ End of the struct contents"""
