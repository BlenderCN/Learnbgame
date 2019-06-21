# TkAttachmentData struct

from .Struct import Struct
from .List import List


class TkAttachmentData(Struct):
    def __init__(self, **kwargs):
        super(TkAttachmentData, self).__init__()

        """ Contents of the struct """
        self.data['Components'] = kwargs.get('Components', List())
        self.data['LodDistances'] = kwargs.get('LodDistances',
                                               [0, 50, 80, 150, 500])
        """ End of the struct contents"""
