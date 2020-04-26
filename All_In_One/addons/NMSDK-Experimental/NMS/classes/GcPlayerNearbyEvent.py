# GcPlayerNearbyEvent struct

from .Struct import Struct


class GcPlayerNearbyEvent(Struct):
    def __init__(self, **kwargs):
        super(GcPlayerNearbyEvent, self).__init__()

        """ Contents of the struct """
        self.data['RequirePlayerAction'] = kwargs.get(
            'RequirePlayerAction', "None")
        self.data['Distance'] = kwargs.get('Distance', 5)
        self.data['Angle'] = kwargs.get('Angle', 360)
        self.data['Distance'] = kwargs.get('Distance', 5)
        self.data['AnglePlayerRelative'] = bool(kwargs.get(
            'AnglePlayerRelative', False))
        self.data['AngleOffset'] = kwargs.get('AngleOffset', 0)
        self.data['AngleReflected'] = bool(kwargs.get('AngleReflected', False))
        self.data['AngleMinDistance'] = kwargs.get('AngleMinDistance', 1)
        self.data['DistanceCheckType'] = kwargs.get(
            'DistanceCheckType', "Radius")
        self.data['Inverse'] = bool(kwargs.get('Inverse', False))
        """ End of the struct contents"""
