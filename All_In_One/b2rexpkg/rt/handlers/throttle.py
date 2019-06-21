"""
 Send throttle parameters to sim
"""

import struct

from pyogp.lib.base.message.message import Message, Block

from .base import Handler

class ThrottleHandler(Handler):
    bps = 100 * 1024  # bytes per second
    _counter = 0
    def processThrottle(self, bps):
        if not bps == self.bps:
            self.bps = bps
            client = self.manager.client
            if client and client.connected and client.region.connected:
                self.sendThrottle(bps)

    def sendThrottle(self, bps=None):
        if not bps:
            bps = self.bps
        client = self.manager.client
        bps = bps*8 # we use bytes per second :)
        data = b''
        data += struct.pack('<f', bps*0.1) # resend
        data += struct.pack('<f', bps*0.1) # land
        data += struct.pack('<f', bps*0.2) # wind
        data += struct.pack('<f', bps*0.2) # cloud
        data += struct.pack('<f', bps*0.25) # task
        data += struct.pack('<f', bps*0.26) # texture
        data += struct.pack('<f', bps*0.25) # asset
        self._counter += 1
        packet = Message('AgentThrottle',
                        Block('AgentData',
                                AgentID = client.agent_id,
                                SessionID = client.session_id,
                             CircuitCode = client.region.circuit_code),
                        Block('Throttle',
                              GenCounter=self._counter,
                              Throttles=data))
        client.region.enqueue_message(packet)


