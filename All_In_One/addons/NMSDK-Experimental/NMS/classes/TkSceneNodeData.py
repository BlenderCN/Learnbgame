# TkSceneNodeData struct

from .Struct import Struct
from .String import String
from .TkTransformData import TkTransformData
from .List import List


class TkSceneNodeData(Struct):
    def __init__(self, **kwargs):
        super(TkSceneNodeData, self).__init__()

        """ Contents of the struct """
        self.data['Name'] = String(kwargs.get('Name', ""), 0x80)
        self.data['Type'] = String(kwargs.get('Type', 'MODEL'), 0x10)
        self.data['Transform'] = kwargs.get('Transform', TkTransformData())
        self.data['Attributes'] = kwargs.get('Attributes', List())
        self.data['Children'] = kwargs.get('Children', List())
        """ End of the struct contents"""
