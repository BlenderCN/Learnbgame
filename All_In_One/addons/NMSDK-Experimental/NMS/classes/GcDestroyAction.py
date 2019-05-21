# GcDestroyAction struct

from .Struct import Struct


class GcDestroyAction(Struct):
    def __init__(self, **kwargs):
        super(GcDestroyAction, self).__init__()

        """ Contents of the struct """
        self.data['DestroyAll'] = bool(kwargs.get('DestroyAll', False))
        """ End of the struct contents"""
