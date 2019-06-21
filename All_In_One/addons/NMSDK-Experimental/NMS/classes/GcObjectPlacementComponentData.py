# GcObjectPlacementComponentData struct

from .Struct import Struct


class GcObjectPlacementComponentData(Struct):
    def __init__(self, **kwargs):
        super(GcObjectPlacementComponentData, self).__init__()

        """ Contents of the struct """
        self.data['GroupNodeName'] = kwargs.get('GroupNodeName', "_Clump")
        self.data['ActivationType'] = kwargs.get('ActivationType', "Locator")
        self.data['FractionOfNodesActive'] = kwargs.get(
            'FractionOfNodesActive', 0.5)
        self.data['MaxNodesActivated'] = kwargs.get('MaxNodesActivated', 0)
        self.data['MaxGroupsActivated'] = kwargs.get('MaxGroupsActivated', 0)
        self.data['UseRaycast'] = kwargs.get('UseRaycast', False)
        """ End of the struct contents"""
