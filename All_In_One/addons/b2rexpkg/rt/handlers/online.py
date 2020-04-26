"""
 Receive status updates from other avatars
"""

from .base import Handler

class OnlineHandler(Handler):
    def onOnlineNotification(self, packet):
        self.out_queue.put(["OnlineNotification",
                            str(packet["AgentBlock"][0]["AgentID"])])

    def onOfflineNotification(self, packet):
        self.out_queue.put(["OfflineNotification",
                            str(packet["AgentBlock"][0]["AgentID"])])

    def onRegionConnect(self, region):
        res = region.message_handler.register("OnlineNotification")
        res.subscribe(self.onOnlineNotification)
        res = region.message_handler.register("OfflineNotification")
        res.subscribe(self.onOfflineNotification)


    def getName(self):
        return self.__class__.__name__



