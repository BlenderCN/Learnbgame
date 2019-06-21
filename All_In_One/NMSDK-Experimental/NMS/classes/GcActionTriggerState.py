# GcActionTriggerState struct

from .Struct import Struct
from .List import List


class GcActionTriggerState(Struct):
    def __init__(self, **kwargs):
        super(GcActionTriggerState, self).__init__()

        """ Contents of the struct """
        self.data['StateID'] = kwargs.get('StateID', "")
        self.data['Triggers'] = kwargs.get('Triggers', List())
        """ End of the struct contents"""
