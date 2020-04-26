"""
Character Application settings
"""

import os

import Blender
from Blender import Registry

from ogredotscene import BoundedValueModel
from .settings import ExportSettings

#from ogredotscene import BoundedValueModel
class CharacterSettings(ExportSettings):
    """Global export settings.
    """
    def __init__(self):
        self._properties = {'translation': 'extra translation for the avatar', 
                            'rotation': 'extra rotation for the avatar', 
                            'scale': 'extra scale for the avatar',
                            # speed
                            'MovementSpeed':'base movement speed',
                            # ground offset
                            'basebone':'bone which should be adjusted to align with the ground. for ground positioning',
                            'rootbone':'avatar skeletons  hierarchy root. for ground positioning',
                            'baseoffset':'offset for ground positioning'}
        self.translation = '0 0 0'
        self.rotation = '1 0 0 0'
        self.scale = '1 1 1'
        self.MovementSpeed = ''
        self.basebone = ''
        self.rootbone = ''
        self.baseoffset = '0 0 0'
        ExportSettings.__init__(self)
        #self.load()
        return
    def getProperties(self):
        return self._properties

    def getDict(self):
        newdict = {}
        for prop in self._properties:
            newdict[prop] = getattr(self, prop)
        return newdict

    def load(self):
        """Load settings from registry, if available.
        """
        ExportSettings.load(self)
        settingsDict = Registry.GetKey('b2rex_char', True)
        if settingsDict:
            for prop in self._properties:
                setattr(self, prop, settingsDict[prop])

    def save(self):
        """Save settings to registry.
        """
        ExportSettings.save(self)
        settingsDict = {}
        for prop in self._properties:
            settingsDict[prop] = getattr(self, prop)
        Registry.SetKey('b2rex_char', settingsDict, True) 
        return

