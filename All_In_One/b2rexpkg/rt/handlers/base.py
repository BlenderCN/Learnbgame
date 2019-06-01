"""
 Base class for agent handlers
"""

import logging

class Handler(object):
    def __init__(self, manager):
        self.out_queue = manager.out_queue
        self.manager = manager
        self.logger = logging.getLogger('simrt.rt.'+self.getName())
    def getServiceName(self):
        """
        Return the service under which you want to be registered on the manager
        """
        return None
    def getName(self):
        """
        Return the name under which this handler should be registered.
        """
        return self.__class__.__name__.replace("Handler", "")
    def onAgentConnected(self, agent):
        """
        Called once the agent is connected.
        """
        pass
    def onRegionConnect(self, region):
        """
        Called when the agent is about to enter a region
        """
        pass
    def onRegionConnected(self, region):
        """
        Called once the region is connected
        """
        pass



