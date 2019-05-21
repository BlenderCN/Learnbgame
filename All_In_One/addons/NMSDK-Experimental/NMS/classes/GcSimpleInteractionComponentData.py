# GcSimpleInteractionComponentData struct

from .Struct import Struct
from .GcInteractionActivationCost import GcInteractionActivationCost
from .GcSizeIndicator import GcSizeIndicator
from .GcStatsEnum import GcStatsEnum
from .GcRarity import GcRarity
from .GcDiscoveryTypes import GcDiscoveryTypes
from .List import List


class GcSimpleInteractionComponentData(Struct):
    def __init__(self, **kwargs):
        super(GcSimpleInteractionComponentData, self).__init__()

        """ Contents of the struct """
        self.data['SimpleInteractionType'] = kwargs.get(
            'SimpleInteractionType', "Interact")
        self.data['InteractDistance'] = kwargs.get('InteractDistance', 0)
        self.data['Id'] = kwargs.get('Id', '')
        self.data['Rarity'] = kwargs.get('Rarity', GcRarity())
        self.data['SizeIndicator'] = kwargs.get(
            'SizeIndicator', GcSizeIndicator())
        self.data['TriggerAction'] = kwargs.get('TriggerAction', '')
        self.data['BroadcastTriggerAction'] = kwargs.get(
            'BroadcastTriggerAction', False)
        self.data['Delay'] = kwargs.get('Delay', 0)
        self.data['InteractIsCrime'] = kwargs.get('InteractIsCrime', False)
        self.data['InteractCrimeLevel'] = kwargs.get('InteractCrimeLevel', 0)
        self.data['ActivationCost'] = kwargs.get(
            'ActivationCost', GcInteractionActivationCost())
        self.data['StatToTrack'] = kwargs.get('StatToTrack', GcStatsEnum())
        self.data['Name'] = kwargs.get('Name', '')
        self.data['TerminalMessage'] = kwargs.get('TerminalMessage', '')
        self.data['ScanType'] = kwargs.get('ScanType', '')
        self.data['ScanData'] = kwargs.get('ScanData', '')
        self.data['ScanIcon'] = kwargs.get('ScanIcon', GcDiscoveryTypes())
        self.data['BaseBuildingTriggerActions'] = kwargs.get(
            'BaseBuildingTriggerActions', List())
        """ End of the struct contents"""
