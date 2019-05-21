# GcCustomInventoryComponentData struct

from .Struct import Struct
from .List import List


class GcCustomInventoryComponentData(Struct):
    def __init__(self, **kwargs):
        super(GcCustomInventoryComponentData, self).__init__()

        """ Contents of the struct """
        self.data['Size'] = kwargs.get('Size', '')
        self.data['DesiredTechs'] = kwargs.get('DesiredTechs', List())
        self.data['Cool'] = kwargs.get('Cool', False)
        """ End of the struct contents"""
