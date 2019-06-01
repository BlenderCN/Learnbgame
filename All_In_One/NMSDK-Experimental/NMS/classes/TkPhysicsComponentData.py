# TkPhysicsComponentData struct

from .Struct import Struct
from .Empty import Empty
from .TkPhysicsData import TkPhysicsData
from .TkVolumeTriggerType import TkVolumeTriggerType


class TkPhysicsComponentData(Struct):
    def __init__(self, **kwargs):
        super(TkPhysicsComponentData, self).__init__()

        """ Contents of the struct """
        self.data['Data'] = kwargs.get('Data', TkPhysicsData())
        self.data['RagdollData'] = kwargs.get('RagdollData', Empty(0x48))
        self.data['VolumeTriggerType'] = kwargs.get('VolumeTriggerType',
                                                    TkVolumeTriggerType())
        self.SurfaceProperties = ["None", "Glass"]
        self.data['SurfaceProperties'] = kwargs.get('SurfaceProperties',
                                                    "None")
        self.data['TriggerVolume'] = kwargs.get('TriggerVolume', False)
        self.data['Climbable'] = kwargs.get('Climbable', False)
        self.data['IgnoreModelOwner'] = kwargs.get('IgnoreModelOwner', False)
        self.data['NoVehicleCollision'] = kwargs.get('NoVehicleCollision',
                                                     False)
        self.data['CameraInvisible'] = kwargs.get('CameraInvisible', False)
        self.data['EndPadding'] = Empty(0x3)
        """ End of the struct contents"""
