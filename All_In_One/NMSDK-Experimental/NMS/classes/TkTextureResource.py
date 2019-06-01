# TkTextureResource struct

from .Struct import Struct


class TkTextureResource(Struct):
    def __init__(self, **kwargs):
        super(TkTextureResource, self).__init__()

        """ Contents of the struct """
        self.data['Filename'] = kwargs.get('Filename', '')
        """ End of the struct contents"""
