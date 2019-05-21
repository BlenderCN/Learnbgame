# TkAnimMetadata struct

from .Struct import Struct
from .List import List
from .TkAnimNodeFrameData import TkAnimNodeFrameData


class TkAnimMetadata(Struct):
    def __init__(self, **kwargs):
        super(TkAnimMetadata, self).__init__()

        """ Contents of the struct """
        self.data['FrameCount'] = kwargs.get('FrameCount', 0)
        self.data['NodeCount'] = kwargs.get('NodeCount', 0)
        self.data['NodeData'] = kwargs.get('NodeData', List())
        self.data['AnimFrameData'] = kwargs.get('AnimFrameData', List())
        self.data['StillFrameData'] = kwargs.get('StillFrameData',
                                                 TkAnimNodeFrameData())
        """ End of the struct contents"""
