# GcBeenShotEvent struct

from .Struct import Struct


class GcBeenShotEvent(Struct):
    def __init__(self, **kwargs):
        super(GcBeenShotEvent, self).__init__()

        """ Contents of the struct """
        self.data['ShotBy'] = kwargs.get('ShotBy', "Player")
        self.data['DamageThreshold'] = kwargs.get('DamageThreshold', 0)
        self.data['HealthThreshold'] = kwargs.get('HealthThreshold', 0)
        """ End of the struct contents"""
