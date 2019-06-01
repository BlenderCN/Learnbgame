# GcNodeActivationAction struct

from .Struct import Struct


class GcNodeActivationAction(Struct):
    def __init__(self, **kwargs):
        super(GcNodeActivationAction, self).__init__()

        """ Contents of the struct """
        self.data['NodeActiveState'] = kwargs.get('NodeActiveState',
                                                  "Activate")
        self.data['Name'] = kwargs.get('Name', "")
        self.data['SceneToAdd'] = kwargs.get('SceneToAdd', "")
        self.data['IncludePhysics'] = bool(kwargs.get('IncludePhysics', False))
        self.data['NotifyNPC'] = bool(kwargs.get('NotifyNPC', False))
        self.data['UseMasterModel'] = bool(kwargs.get('UseMasterModel', False))
        self.data['RestartEmitters'] = bool(kwargs.get('RestartEmitters',
                                                       False))
        """ End of the struct contents"""
