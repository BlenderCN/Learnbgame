"""
 Receive parcel information
"""

from .base import Handler

class ParcelHandler(Handler):
    def onRegionConnect(self, region):
        res = region.message_handler.register("ParcelOverlay")
        res.subscribe(self.onParcelOverlay)
    def onParcelOverlay(self, packet):
        # some region info
        self.logger.debug(packet)


