# TkSceneNodeAttributeData struct

from .Struct import Struct
from .String import String


class TkSceneNodeAttributeData(Struct):
    def __init__(self, **kwargs):
        super(TkSceneNodeAttributeData, self).__init__()

        """ Contents of the struct """
        self.data['Name'] = String(kwargs.get('Name', ""), 0x10)
        self.data['AltID'] = String(kwargs.get('AltID', ""), 0x10)
        self.data['Value'] = String(kwargs.get('Value', ""), 0x100)
        """ End of the struct contents"""
