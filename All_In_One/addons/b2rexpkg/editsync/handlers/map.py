"""
 MapModule: Provides map functionality, with information from coarse updates.
"""
from .base import SyncModule

import bpy

class MapModule(SyncModule):
    def register(self, parent):
        """
        Register this module with the editor
        """
        parent.registerCommand('CoarseLocationUpdate', self.processCoarseLocationUpdate)

    def unregister(self, parent):
        """
        Unregister this module from the editor
        """
        parent.unregisterCommand('CoarseLocationUpdate')

    def processCoarseLocationUpdate(self, agent_id, pos):
        """
        A coarse location update arrived from the sim.
        """
        #print("COARSE LOCATION UPDATE", agent_id, pos)
        pass

