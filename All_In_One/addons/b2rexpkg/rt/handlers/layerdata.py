"""
 Receive and send terrain layer data
"""

import base64
import struct
from array import array

from pyogp.lib.base.message.message import Message, Block

try:
    from simtypes import LayerTypes
except:
    from b2rexpkg.tools.simtypes import LayerTypes

from .base import Handler

class LayerDataHandler(Handler):
    def onRegionConnect(self, region):
        res = region.message_handler.register("LayerData")
        res.subscribe(self.onLayerData)

    def processLayerData(self, x, y, b64data):
        bindata = base64.urlsafe_b64decode(b64data.encode('ascii'))
        packet = Message('LayerData',
                        Block('LayerID',
                                Type = LayerTypes.LayerLand),
                        Block('LayerData',
                              Data=array('c', bindata)))
        self.manager.client.region.enqueue_message(packet)

    def onLayerData(self, packet):
        data = packet["LayerData"][0]["Data"]
        layerType = struct.unpack("<B", data[3])[0]
        if layerType == LayerTypes.LayerLand or True:
            b64data = base64.urlsafe_b64encode(data).decode('ascii')
            self.out_queue.put(["LayerData", layerType, b64data])


