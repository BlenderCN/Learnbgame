"""
 RegionHandshakeModule: Process RegionHandshake commands.
"""

from .base import SyncModule

import bpy

from b2rexpkg.tools.simtypes import RegionFlags

class RegionHandshakeModule(SyncModule):
    flags = 0
    name = ''
    access = 0
    def register(self, parent):
        """
        Register this module with the editor
        """
        parent.registerCommand('RegionHandshake', self.processRegionHandshake)

    def unregister(self, parent):
        """
        Unregister this module from the editor
        """
        parent.unregisterCommand('RegionHandshake')

    def getPanelName(self):
        """
        Return the name under which this handlers panel should be registered.
        """
        return self.name

    def processRegionHandshake(self, regionID, pars):
        """
        RegionHandshake arrived from the simulator.
        """
        print("REGION HANDSHAKE", pars)
        self.flags = pars['RegionFlags']
        self.name = pars['SimName']
        self.access = pars['SimAccess']
        self.pars = pars

    def draw(self, layout, session, props):
        if not session.RegionHandshake.name or not self.expand(layout):
            return
        if session.RegionHandshake.name:
            row = layout.box()
            access_labels = {0:'unknown', 13:'PG', 21:'Mature', 42: 'Adult'}
            row.label(text='Current Region: '+ session.RegionHandshake.name)
            access_level = session.RegionHandshake.access
            row.label(text='Access Level: '+ access_labels[access_level])
            for flag in dir(RegionFlags):
                val = getattr(RegionFlags, flag)
                if isinstance(val, int):
                    symbol = '-'
                    if val & session.RegionHandshake.flags:
                        symbol = '+'
                        row.label(text=symbol+" "+flag)

