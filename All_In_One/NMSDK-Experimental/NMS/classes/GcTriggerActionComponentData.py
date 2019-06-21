# GcTriggerActionComponentData struct

from .Struct import Struct
from .List import List


class GcTriggerActionComponentData(Struct):
    def __init__(self, **kwargs):
        super(GcTriggerActionComponentData, self).__init__()

        """ Contents of the struct """
        self.data['HideModel'] = bool(kwargs.get('HideModel', False))
        self.data['StartInactive'] = bool(kwargs.get('StartInactive', False))
        self.data['States'] = kwargs.get('States', List())
        self.data['Persistent'] = bool(kwargs.get('Persistent', False))
        self.data['PersistentState'] = kwargs.get('PersistentState', "")
        """ End of the struct contents"""
