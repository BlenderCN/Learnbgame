# GcPlayAnimAction struct

from .Struct import Struct


class GcPlayAnimAction(Struct):
    def __init__(self, **kwargs):
        super(GcPlayAnimAction, self).__init__()

        """ Contents of the struct """
        self.data['Anim'] = kwargs.get('Anim', "")
        """ End of the struct contents"""
