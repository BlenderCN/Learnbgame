# TkAnimNodeFrameData struct

from .Struct import Struct
from .List import List


class TkAnimNodeFrameData(Struct):
    def __init__(self, **kwargs):
        super(TkAnimNodeFrameData, self).__init__()

        """ Contents of the struct """
        self.data['Rotations'] = kwargs.get('Rotations', List())
        self.data['Translations'] = kwargs.get('Translations', List())
        self.data['Scales'] = kwargs.get('Scales', List())
        """ End of the struct contents"""

    """
    def serialize(self, output):
        # TODO: write
        pass
    """
