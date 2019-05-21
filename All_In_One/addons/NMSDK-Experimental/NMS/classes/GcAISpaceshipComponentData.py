# GcAISpaceshipComponentData struct

from .Struct import Struct
from .TkTextureResource import TkTextureResource
from .GcPrimaryAxis import GcPrimaryAxis
from .GcSpaceshipClasses import GcSpaceshipClasses
from .GcAISpaceshipTypes import GcAISpaceshipTypes


class GcAISpaceshipComponentData(Struct):
    def __init__(self, **kwargs):
        super(GcAISpaceshipComponentData, self).__init__()

        """ Contents of the struct """
        self.data['Type'] = kwargs.get('Type', GcAISpaceshipTypes())
        self.data['Class'] = kwargs.get('Class', GcSpaceshipClasses())
        self.data['Axis'] = kwargs.get('Axis', GcPrimaryAxis())
        self.data['Hangar'] = kwargs.get('Hangar', TkTextureResource())
        self.data['IsSpaceAnomaly'] = kwargs.get('IsSpaceAnomaly', False)
        """ End of the struct contents"""
