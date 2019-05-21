"""
Application settings
"""

import os

import Blender
from Blender import Registry

from ogredotscene import BoundedValueModel
from b2rexpkg.tools.passmanager import PasswordManager

#from ogredotscene import BoundedValueModel

class ExportSettings:
    """Global export settings.
    """
    properties = ['path', 'pack', 'server_url', 'username', 'export_dir']
    def __init__(self):
        self.credentials = PasswordManager("b2rex")
        self.path = os.path.dirname(Blender.Get('filename'))
        self.pack = 'pack'
        self.username = ''
        self.password = ''
        self.server_url = 'http://delirium:9000'
        self.export_dir = ''
        self.locX = BoundedValueModel(-10000.0, 10000.0, 128.0)
        self.locY = BoundedValueModel(-10000.0, 10000.0, 128.0)
        self.locZ = BoundedValueModel(-1000.0, 1000.0, 20.0)
        self.regenMaterials = True
        self.regenObjects = False
        self.regenTextures = False
        self.regenMeshes = False
        self.kbytesPerSecond = 100
        self.agent_libs_path = ""
        self.pool_workers = 5
        self.rt_budget = 20
        self.next_chat = ""
        self.tools_path = ""
        self.rt_sec_budget = 500
        self.terrainLOD = 1
        self.load()
        return

    def getLocX(self):
        """Get x offset
        """
        return self.locX.getValue()
    def getLocY(self):
        """Get y offset
        """
        return self.locY.getValue()
    def getLocZ(self):
        """Get z offset
        """
        return self.locZ.getValue()
    def load(self):
        """Load settings from registry, if available.
        """
        settingsDict = Registry.GetKey('b2rex', True)
        if settingsDict:
            for prop in ['Objects', 'Textures', 'Materials', 'Meshes']:
                keyName = 'regen' + prop
                if settingsDict.has_key(keyName):
                    setattr(self, keyName, settingsDict[keyName])
            for prop in self.properties:
                if settingsDict.has_key(prop):
                    setattr(self, prop, settingsDict[prop])
            if self.server_url and self.username:
                self.username, self.password = self.credentials.get_credentials(self.server_url, self.username)
            if settingsDict.has_key('locX'):
                try:
                    self.locX.setValue(float(settingsDict['locX']))
                except TypeError:
                    pass
            if settingsDict.has_key('locY'):
                try:
                    self.locY.setValue(float(settingsDict['locY']))
                except TypeError:
                    pass
            if settingsDict.has_key('locZ'):
                try:
                    self.locZ.setValue(float(settingsDict['locZ']))
                except TypeError:
                    pass
    def save(self):
        """Save settings to registry.
        """
        settingsDict = {}
        for prop in self.properties:
            settingsDict[prop] = getattr(self, prop)
        if self.username and self.password:
            self.credentials.set_credentials(self.server_url,
                                             self.username,
                                             self.password)
        settingsDict['locX'] = self.locX.getValue()
        settingsDict['locY'] = self.locY.getValue()
        settingsDict['locZ'] = self.locZ.getValue()
        for prop in ['Objects', 'Textures', 'Materials', 'Meshes']:
            keyName = 'regen' + prop
            settingsDict[keyName] = getattr(self, keyName)
        Registry.SetKey('b2rex', settingsDict, True) 
        return

