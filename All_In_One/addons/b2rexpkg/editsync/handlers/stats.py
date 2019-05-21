"""
 StatsModule: Stats management.
"""

from .base import SyncModule

import bpy

simstats_labels = ["X", "Y", "Flags", "ObjectCapacity", "TimeDilation",
                   "SimFPS", "PhysicsFPS", "AgentUpdates", "Agents",
                   "ChildAgents", "TotalPrim", "ActivePrim", "FrameMS", "NetMS",
                  "PhysicsMS", "ImageMS", "OtherMS", "InPacketsPerSecond",
                   "OutPacketsPerSecond", "UnAckedBytes", "AgentMS",
                   "PendingDownloads", "PendingUploads", "ActiveScripts",
                   "ScriptLinesPerSecond"]

class StatsModule(SyncModule):
    def register(self, parent):
        """
        Register this module with the editor
        """
        parent.registerCommand('SimStats', self.processSimStats)
        self.simstats = None

    def unregister(self, parent):
        """
        Unregister this module from the editor
        """
        parent.unregisterCommand('SimStats')

    def processSimStats(self, X, Y, Flags, ObjectCapacity, *args):
        """
        SimStats arrived from the simulator.
        """
        self.simstats = [X, Y, Flags, ObjectCapacity] + list(args)

    def draw(self, layout, session, props):
        """
        Draw the stats panel into the given layout.
        """
        row = layout.row() 
        if props.show_stats:
            row.prop(props,"show_stats", icon="TRIA_DOWN", text="Stats",
                     emboss=True)
            box = layout.box()
            if session.simrt:
                if session.agent_id:
                    box.label(text="agent: "+session.agent_id+" "+session.agent_access)

            box.label(text="cmds in: %d out: %d updates: %d"%tuple(session.stats[:3]))
            box.label(text="http requests: %d ok: %d"%tuple(session.stats[3:5]))
            box.label(text="queue pending: %d last time: %d"%tuple(session.stats[5:7])+" last sec: "+str(session.second_budget))
            box.label(text="threads workers: "+str(session.stats[7]))
            box.label(text="updates cmd: %d view: %d"%tuple(session.stats[8:10]))
            if self.simstats:
                for idx, a in enumerate(self.simstats):
                    box.label(text=simstats_labels[idx]+": "+str(a))
        else:
            row.prop(props,"show_stats", icon="TRIA_RIGHT", text="Stats",
                     emboss=True)

