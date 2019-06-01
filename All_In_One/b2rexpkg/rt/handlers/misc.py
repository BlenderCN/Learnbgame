"""
 Miscelaneous functionality like localteleport or autopilot
"""

import uuid

from .base import Handler

from pyogp.lib.base.datatypes import UUID, Vector3
from pyogp.lib.base.message.message import Message, Block

class MiscHandler(Handler):
    def sendLocalTeleport(self, agent, pos):
        client = self.manager.client
        if not agent.FullID == client.agent_id:
            print("Trying to move an agent for other user")
        t_id = uuid.uuid4()
        invoice_id = UUID()
        client.teleport(region_handle=client.region.RegionHandle, 
                             position=Vector3(X=pos[0], Y=pos[1], Z=pos[2]))

    def sendAutopilot(self, agent, pos):
        packet = Message('GenericMessage',
                        Block('AgentData',
                                AgentID = client.agent_id,
                                SessionID = client.session_id,
                             TransactionID = t_id),
                        Block('MethodData',
                                Method = 'autopilot',
                                Invoice = invoice_id),
                        Block('ParamList', Parameter=data_x),
                        Block('ParamList', Parameter=data_y),
                        Block('ParamList', Parameter=data_z))
        self.manager.client.region.enqueue_message(packet)


