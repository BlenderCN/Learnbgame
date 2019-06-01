from .base import SyncModule

import bpy

class CapsModule(SyncModule):
    def register(self, parent):
        """
        Register this module with the editor
        """
        parent.registerCommand('capabilities', self.processCapabilities)

    def unregister(self, parent):
        """
        Unregister this module from the editor
        """
        parent.unregisterCommand('capabilities')

    def processCapabilities(self, caps):
        self._parent.caps = caps


