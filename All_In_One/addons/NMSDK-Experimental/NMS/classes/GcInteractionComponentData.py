# GcInteractionComponentData struct

from .Struct import Struct
from .List import List
from .GcInteractionType import GcInteractionType
from .TkModelRendererData import TkModelRendererData
from .GcAlienRace import GcAlienRace
from .GcInteractionActivationCost import GcInteractionActivationCost
from .GcInteractionDof import GcInteractionDof


class GcInteractionComponentData(Struct):
    def __init__(self, **kwargs):
        super(GcInteractionComponentData, self).__init__()

        """ Contents of the struct """
        self.data['InteractionAction'] = kwargs.get(
            'InteractionAction', "PressButton")
        self.data['InteractionType'] = kwargs.get(
            'InteractionType', GcInteractionType())
        self.data['Renderer'] = kwargs.get('Renderer', TkModelRendererData())
        self.data['Race'] = kwargs.get('Race', GcAlienRace())
        self.data['AttractDistanceSq'] = kwargs.get('AttractDistanceSq', 25)
        self.data['RepeatInteraction'] = kwargs.get('RepeatInteraction', False)
        self.data['UseInteractCamera'] = kwargs.get('UseInteractCamera', True)
        self.data['BlendToCameraTime'] = kwargs.get('BlendToCameraTime', 1.5)
        self.data['BlendFromCameraTime'] = kwargs.get(
            'BlendFromCameraTime', -1)
        self.data['ActivationCost'] = kwargs.get(
            'ActivationCost', GcInteractionActivationCost())
        self.data['TriggerAction'] = kwargs.get('TriggerAction', "")
        self.data['BroadcastTriggerAction'] = kwargs.get(
            'BroadcastTriggerAction', False)
        self.data['InteractAngle'] = kwargs.get('InteractAngle', 360)
        self.data['InteractDistance'] = kwargs.get('InteractDistance', 5)
        self.data['InteractInvertFace'] = kwargs.get(
            'InteractInvertFace', False)
        self.data['SecondaryInteractionType'] = kwargs.get(
            'SecondaryInteractionType', GcInteractionType())
        self.data['SecondaryActivationCost'] = kwargs.get(
            'SecondaryActivationCost', GcInteractionActivationCost())
        self.data['EventRenderers'] = kwargs.get('EventRenderers', List())
        self.data['SecondaryCameraTransitionTime'] = kwargs.get(
            'SecondaryCameraTransitionTime', 1)
        self.data['DoInteractionsInOrder'] = kwargs.get(
            'DoInteractionsInOrder', False)
        self.data['DepthOfField'] = kwargs.get(
            'DepthOfField', GcInteractionDof())
        self.data['PuzzleMissionOverrideTable'] = kwargs.get(
            'PuzzleMissionOverrideTable', List())
        """ End of the struct contents"""
