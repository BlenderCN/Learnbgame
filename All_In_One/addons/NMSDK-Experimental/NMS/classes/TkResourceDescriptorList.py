# TkResourceDescriptorList struct

from .Struct import Struct
from .List import List
from .String import String


class TkResourceDescriptorList(Struct):
    def __init__(self, **kwargs):
        super(TkResourceDescriptorList, self).__init__()

        """ Contents of the struct """
        self.data['TypeId'] = String(kwargs.get('TypeId', "_PROCOBJ_"), 0x10)
        self.data['Descriptors'] = kwargs.get('Descriptors', List())
        """ End of the struct contents"""
