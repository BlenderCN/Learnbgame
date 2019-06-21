# GcRewardAction struct

from .Struct import Struct


class GcRewardAction(Struct):
    def __init__(self, **kwargs):
        super(GcRewardAction, self).__init__()

        """ Contents of the struct """
        self.data['Reward'] = kwargs.get('Reward', "")
        """ End of the struct contents"""
