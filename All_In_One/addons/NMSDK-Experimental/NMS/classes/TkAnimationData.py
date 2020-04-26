# TkAnimationData struct

from .Struct import Struct
from .List import List


class TkAnimationData(Struct):
    def __init__(self, **kwargs):
        super(TkAnimationData, self).__init__()

        """ Contents of the struct """
        self.data['Anim'] = kwargs.get('Anim', '')
        self.data['Filename'] = kwargs.get('Filename', '')
        self.data['AnimType'] = kwargs.get('AnimType', 'Loop')
        self.data['FrameStart'] = kwargs.get('FrameStart', 0)
        self.data['FrameEnd'] = kwargs.get('FrameEnd', 0)
        self.data['StartNode'] = kwargs.get('StartNode', '')
        self.data['ExtraStartNodes'] = kwargs.get('ExtraStartNodes', List())
        self.data['Priority'] = kwargs.get('Priority', 0)
        self.data['LoopOffsetMin'] = kwargs.get('LoopOffsetMin', 0)
        self.data['LoopOffsetMax'] = kwargs.get('LoopOffsetMax', 0)
        self.data['ControlDelay'] = kwargs.get('ControlDelay', 0)
        self.data['ControlSpeed'] = kwargs.get('ControlSpeed', 1)
        self.data['ControlActionFrame'] = kwargs.get('ControlActionFrame', -1)
        self.data['ControlCreatureSize'] = kwargs.get('ControlCreatureSize',
                                                      'AllSizes')
        self.data['FlagsAdditive'] = kwargs.get('FlagsAdditive', 'False')
        self.data['FlagsMirrored'] = kwargs.get('FlagsMirrored', 'False')
        self.data['FlagsActive'] = kwargs.get('FlagsActive', 'True')
        """ End of the struct contents"""
