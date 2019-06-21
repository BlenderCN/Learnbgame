# GcDisplayText struct

from .Struct import Struct


class GcDisplayText(Struct):
    def __init__(self, **kwargs):
        super(GcDisplayText, self).__init__()

        """ Contents of the struct """
        self.data['HUDTextDisplayType'] = kwargs.get('HUDTextDisplayType',
                                                     "Full")
        self.data['Title'] = kwargs.get('Title', "Title Text")
        self.data['Subtitle1'] = kwargs.get('Subtitle1', "Subtitle Text 1")
        self.data['Subtitle2'] = kwargs.get('Subtitle2', "Subtitle Text 2")
        """ End of the struct contents"""
