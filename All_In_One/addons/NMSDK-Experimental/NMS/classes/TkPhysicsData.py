# TkPhysicsData struct

from .Struct import Struct


class TkPhysicsData(Struct):
    def __init__(self, **kwargs):
        super(TkPhysicsData, self).__init__()

        """ Contents of the struct """
        self.data['Mass'] = kwargs.get('Mass', 0.0)
        self.data['Friction'] = kwargs.get('Friction', 0.5)
        self.data['RollingFriction'] = kwargs.get('RollingFriction', 0.2)
        self.data['AngularDamping'] = kwargs.get('AngularDamping', 0.2)
        self.data['LinearDamping'] = kwargs.get('LinearDamping', 0.1)
        self.data['Gravity'] = kwargs.get('Gravity', 20.0)
        """ End of the struct contents"""
