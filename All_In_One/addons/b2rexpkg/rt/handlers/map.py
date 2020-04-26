"""
 Receive map information from coarse updates
"""

from .base import Handler

class MapHandler(Handler):
    def onRegionConnect(self, region):
        res = region.message_handler.register("CoarseLocationUpdate")
        res.subscribe(self.onCoarseLocationUpdate)

    def onCoarseLocationUpdate(self, packet):
        for i, block in enumerate(packet["Location"]):
            X = block['X']
            Y = block['Y']
            Z = block['Z']
            agent = packet["AgentData"][i]["AgentID"]

            self.out_queue.put(["CoarseLocationUpdate", str(agent), (X, Y, Z)])


