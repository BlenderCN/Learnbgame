# GcPrimaryAxis struct

from .Struct import Struct


class GcPrimaryAxis(Struct):
    def __init__(self, **kwargs):
        super(GcPrimaryAxis, self).__init__()

        """ Contents of the struct """
        self.data['PrimaryAxis'] = kwargs.get('PrimaryAxis', "Z")
        """ End of the struct contents"""
