# GcAnimFrameEvent struct

from .Struct import Struct


class GcAnimFrameEvent(Struct):
    def __init__(self, **kwargs):
        super(GcAnimFrameEvent, self).__init__()

        """ Contents of the struct """
        self.data['Anim'] = kwargs.get('Anim', "")
        self.data['FrameStart'] = kwargs.get('FrameStart', 0)
        self.data['StartFromEnd'] = bool(kwargs.get('StartFromEnd', False))
        """ End of the struct contents"""
