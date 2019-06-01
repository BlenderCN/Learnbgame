# GcPainAction struct

from .Struct import Struct


class GcPainAction(Struct):
    def __init__(self, **kwargs):
        super(GcPainAction, self).__init__()

        """ Contents of the struct """
        self.data['Damage'] = kwargs.get('Damage', "")
        self.data['Radius'] = kwargs.get('Radius', 0)
        self.data['AffectsPlayer'] = bool(kwargs.get('AffectsPlayer', True))
        """ End of the struct contents"""
