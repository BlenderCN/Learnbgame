# GcInteractionDof struct

from .Struct import Struct


class GcInteractionDof(Struct):
    def __init__(self, **kwargs):
        super(GcInteractionDof, self).__init__()

        """ Contents of the struct """
        self.data['IsEnabled'] = kwargs.get('IsEnabled', True)
        self.data['UseGlobals'] = kwargs.get('UseGlobals', True)
        self.data['NearPlaneMin'] = kwargs.get('NearPlaneMin', 2)
        self.data['NearPlaneAdjust'] = kwargs.get('NearPlaneAdjust', 1)
        self.data['FarPlane'] = kwargs.get('FarPlane', 3)
        self.data['FarFadeDistance'] = kwargs.get('FarFadeDistance', 2)
        """ End of the struct contents"""
