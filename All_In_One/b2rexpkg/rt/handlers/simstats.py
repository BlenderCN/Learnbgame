"""
 Receive sim stats
"""

from .base import Handler

class SimStatsHandler(Handler):
    def onRegionConnect(self, region):
        res = region.message_handler.register("SimStats")
        res.subscribe(self.onSimStats)
    def onSimStats(self, packet):
        pars = []

        for stat in packet["Stat"]:
            pars.append(stat["StatValue"])

        Region = packet["Region"][0]
        X = Region['RegionX']
        Y = Region['RegionY']
        Flags = Region['RegionFlags']
        ObjectCapacity = Region['ObjectCapacity']

        self.out_queue.put(["SimStats", X, Y, Flags, ObjectCapacity] + pars)



