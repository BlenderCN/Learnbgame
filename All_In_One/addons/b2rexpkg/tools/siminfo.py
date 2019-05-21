"""
Class to get grid info from opensim
"""

import sys
import logging
logger = logging.getLogger('b2rex.siminfo')
if sys.version_info[0] == 2:
    import urllib2
else:
    import urllib.request as urllib2

from .restconnector import RestConnector


class GridInfo(RestConnector):
    def __init__(self):
        RestConnector.__init__(self)
        self._regions = {}

    def getGridInfo(self):
        """
        Get general grid information.
        """
        try:
            self.gridinfo = self.httpObjGet("/get_grid_info")
        except:
            self.gridinfo = {"gridname":"", "gridnick":"region", "mode":"standalone"}
        return self.gridinfo

    def getRegions(self):
        """
        Get grid regions.
        """
        xmldata = self.httpXmlGet("/admin/regions/")
        for uuid in xmldata.findall('uuid'):
            region = self.httpObjGet("/admin/regions/"+uuid.text, "region_")
            self._regions[region['id']] = region
            map_url = self._url + "/index.php?method=regionImage"+region['id'].replace('-','')
            self._regions[region['id']]['map'] = map_url
        return self._regions

    def getAsset(self, uuid):
        return self.httpObjGet("/admin/assets/"+uuid)

if __name__ == '__main__':
    base_url = "http://127.0.0.1:9000"
    gridinfo = GridInfo()
    gridinfo.connect(base_url, "caedes caedes", "XXX")
    logger.debug(gridinfo.httpXmlGet("//7a4ebc0f-cbde-4904-a0e6-ab9b5295d7e0"))
    logger.debug(gridinfo.getGridInfo()["gridnick"])
    regions = gridinfo.getRegions()
    for id in regions:
        region = regions[id]
        logger.debug((" *", region["name"], region["x"], region["y"], id))
    asset = gridinfo.getAsset("69e2f587-4bbd-4ec7-8e1f-8b03601d218e")
    logger.debug((asset["name"]))

