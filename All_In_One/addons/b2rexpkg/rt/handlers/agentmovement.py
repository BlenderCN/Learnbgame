"""
 Implements agent movement operations.
"""

from .base import Handler

class AgentMovementHandler(Handler):
    def onRegionConnect(self, region):
        """
        Agent connected to region
        """
        res = region.message_handler.register("AgentMovementComplete")
        res.subscribe(self.onAgentMovementComplete)

    def processSetFlags(self, flags):
        """
        Set agent movement flags directly
        """
        agent = self.manager.client
        agent.control_flags = flags

    def processStop(self):
        """
        Stop all movement
        """
        agent = self.manager.client
        agent.stop()

    def onAgentMovementComplete(self, packet):
        """
        AgentMovementComplete received from sim
        """
        # some region info
        AgentData = packet['AgentData'][0]
        Data = packet['Data'][0]
        pos = Data['Position']
        lookat = Data['LookAt']
        agent_id = str(AgentData['AgentID'])
        lookat = [lookat.X, lookat.Y, lookat.Z]
        pos = [pos.X, pos.Y, pos.Z]
        self.out_queue.put(["AgentMovementComplete", agent_id, pos, lookat])

    # unused:
    def processWalk(self, walk = False):
        """
        Walk on/off
        """
        agent = self.manager.client
        agent.walk(walk)

    def processWalkBackwards(self, walk = False):
        """
        Walk backwards on/off
        """
        agent = self.manager.client
        agent.walk_backwards(walk)

    def processBodyRotation(self, body_rotation):
        """
        Set body rotation by a quaternion
        """
        agent = self.manager.client
        agent.body_rotation(body_rotation)

    def processFly(self, flying):
        """
        Set flying flag
        """
        agent = self.manager.client
        agent.fly(flying)

    def processMoveUp(self, flying):
        """
        Move up on/off
        """
        agent = self.manager.client
        agent.move_up(flying)

    def processMoveDown(self, flying):
        """
        Move down on/off
        """
        agent = self.manager.client
        agent.move_down(flying)


