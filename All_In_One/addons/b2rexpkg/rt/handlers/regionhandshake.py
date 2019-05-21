"""
 Receive region handshake
"""

from .base import Handler

class RegionHandshakeHandler(Handler):
    def onRegionConnect(self, region):
        res = region.message_handler.register("RegionHandshake")
        res.subscribe(self.onRegionHandshake)
    def onRegionHandshake(self, packet):
        regionInfo = packet["RegionInfo"][0]

        pars = {}

        for prop in ['RegionFlags', 'SimAccess', 'SimName', 'WaterHeight',
                     'BillableFactor', 'TerrainStartHeight00',
                     'IsEstateManager',
                     'TerrainStartHeight01', 'TerrainStartHeight10',
                     'TerrainStartHeight11', 'TerrainHeightRange00',
                     'TerrainHeightRange01', 'TerrainHeightRange10',
                     'TerrainHeightRange11']:
            pars[prop] = regionInfo[prop]

        for prop in ["SimOwner", 'CacheID', 'TerrainBase0', 'TerrainBase1',
                     'TerrainBase2', 'TerrainDetail0', 'TerrainDetail1',
                     'TerrainDetail2', 'TerrainDetail3']:
            pars[prop] = str(regionInfo[prop])

        pars["RegionID"] = str(packet["RegionInfo2"][0]["RegionID"])
        pars["CPUClassID"] = packet["RegionInfo3"][0]["CPUClassID"]
        pars["CPURatio"] = packet["RegionInfo3"][0]["CPURatio"]

        self.out_queue.put(["RegionHandshake", pars["RegionID"], pars])



