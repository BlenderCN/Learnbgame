# TkModelDescriptorList struct

from .Struct import Struct
from .List import List


class TkModelDescriptorList(Struct):
    def __init__(self, **kwargs):
        super(TkModelDescriptorList, self).__init__()

        """ Contents of the struct """
        self.data['List'] = kwargs.get('List', List())
        """ End of the struct contents"""
