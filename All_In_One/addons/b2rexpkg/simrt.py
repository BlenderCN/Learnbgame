# standard
import os
import sys
import logging
import time
import traceback
from collections import defaultdict
from threading import Thread

# related
import eventlet
from eventlet import api
from eventlet import Queue

simrt_path = os.path.dirname(os.path.realpath(__file__))
if __name__ == '__main__':
    sys.path.append(os.path.join(simrt_path))
sys.path.append(os.path.join(simrt_path, 'tools'))
try:
    from jsonsocket import JsonSocket
except:
    from b2rexpkg.tools.jsonsocket import JsonSocket
    from b2rexpkg import rt

# pyogp
from pyogp.lib.base.exc import LoginError
from pyogp.lib.base.datatypes import UUID

from pyogp.lib.client.agent import Agent
from pyogp.lib.client.settings import Settings

# internal rt module
from rt.handlers.chat import ChatHandler
from rt.handlers.layerdata import LayerDataHandler
from rt.handlers.parcel import ParcelHandler
from rt.handlers.object import ObjectHandler
from rt.handlers.select import SelectHandler
from rt.handlers.scripting import ScriptingHandler
from rt.handlers.inventory import InventoryHandler
from rt.handlers.rexdata import RexDataHandler
from rt.handlers.throttle import ThrottleHandler
from rt.handlers.online import OnlineHandler
from rt.handlers.bootstrap import BootstrapHandler
from rt.handlers.simstats import SimStatsHandler
from rt.handlers.assetrequest import AssetRequest
from rt.handlers.xferupload import XferUploadManager
from rt.handlers.agentmovement import AgentMovementHandler
from rt.handlers.regionhandshake import RegionHandshakeHandler
from rt.handlers.misc import MiscHandler

from rt.tools import prepare_server_name


class AgentManager(object):
    verbose = False
    def __init__(self, in_queue, out_queue):
        self._handlers = {}
        self._generichandlers = {}
        self._cmdhandlers = defaultdict(list)
        self.client = None
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.initialize_logger()

    def register_generic_handler(self, message, handler):
        """
        Register a callback for a GenericMessage method.
        """
        self._generichandlers[message] = handler

    def onGenericMessage(self, packet):
        """
        Function dealing with GenericMessages
        """
        methodname = packet["MethodData"][0]["Method"]
        if methodname in self._generichandlers:
            try:
                self._generichandlers[methodname](packet["ParamList"])
            except:
                print("error decoding "+methodname)
                traceback.print_exc()
        else:
            self.logger.debug("unrecognized generic message"+packet["MethodData"][0]["Method"])
            self.logger.debug(str(packet))

    def subscribe_region_callbacks(self, region):
        """
        Subscribe all region connected callbacks
        """
        for handler in self._handlers.values():
            handler.onRegionConnected(region)

    def subscribe_region_pre_callbacks(self, region):
        """
        Subscribe all region connect callbacks. Called just before connecting.
        """
        for handler in self._handlers.values():
            handler.onRegionConnect(region)

        res = region.message_handler.register("GenericMessage")
        res.subscribe(self.onGenericMessage)

    def add_handler(self, handler):
        """
        Add a handler object. Generally represents a given service.
        """
        self._handlers[handler.getName()] = handler
        for a in dir(handler):
            if a.startswith("process"):
                self._cmdhandlers[a[7:]].append(getattr(handler, a))
        service = handler.getName().lower()
        setattr(self, service, handler)

    def login(self, server_url, login_params):
        """ login an to a login endpoint """ 
        in_queue = self.in_queue
        out_queue = self.out_queue

        client = self.initialize_agent()

        self.uploader = XferUploadManager(self)
        self.add_handler(self.uploader)
        self.add_handler(OnlineHandler(self))
        self.add_handler(RegionHandshakeHandler(self))
        self.add_handler(SimStatsHandler(self))
        self.add_handler(AgentMovementHandler(self))
        self.add_handler(LayerDataHandler(self))
        self.add_handler(ParcelHandler(self))
        self.add_handler(ThrottleHandler(self))
        self.add_handler(RexDataHandler(self))
        self.add_handler(InventoryHandler(self))
        self.add_handler(ScriptingHandler(self))
        self.add_handler(ChatHandler(self))
        self.add_handler(SelectHandler(self))
        self.add_handler(ObjectHandler(self))
        self.add_handler(MiscHandler(self))
        self.add_handler(AssetRequest(self))

        # Now let's log it in
        #firstname, lastname = username.split(" ", 1)
        loginuri = prepare_server_name(server_url)
        regionname = 'last'


        print("LOGIN WITH", login_params)
        error = []
        def trylogin(*args, **kwargs):
            try:
                client.login(*args, **kwargs)
            except Exception as e:
                print("error connecting")
                error.append(e)

        api.spawn(trylogin, loginuri, login_params = login_params,
                  start_location = regionname, connect_region = True)

        # wait for the agent to connect to it's region
        while client.connected == False:
            if error:
                return error[0]
            api.sleep(0)

        # notify handlers of agent connection
        for handler in self._handlers.values():
            handler.onAgentConnected(client)

        # subscribe own callbacks and call handler callbacks for about to
        # connect to region
        self.subscribe_region_pre_callbacks(client.region)

        # inform our client of connection success
        out_queue.put(["connected", str(client.agent_id),
                             str(client.agent_access)])
 
        caps_sent = False
        caps = {}

        print("CONNECTING.....", client.region)
        # wait until the client is connected
        while not client.region.connected:
            # look for GetTexture and send to client as soon as possible
            if not caps_sent and "GetTexture" in client.region.capabilities:
                for cap in client.region.capabilities:
                    caps[cap] = client.region.capabilities[cap].public_url
                self.out_queue.put(["capabilities", caps])
                caps_sent = True
            api.sleep(0)
            
        print("CONNECTED.....")
        # wait until the client is connected

        # notify handlers of connection to region
        self.subscribe_region_callbacks(client.region)



        # send throttle
        self.throttle.sendThrottle()
        if not caps_sent:
            for cap in client.region.capabilities:
                caps[cap] = client.region.capabilities[cap].public_url
            self.out_queue.put(["capabilities", caps])

        # speak up the first line
        if "firstline" in login_params:
            client.say(login_params["firstline"])

        # main loop for the agent
        while client.running == True:
            cmd = in_queue.get()
            command = cmd[0]
            command = command[0].upper()+command[1:]
            if command in self._cmdhandlers:
                # we have a registered handler
                for handler in self._cmdhandlers[command]:
                    handler(*cmd[1:])
            else:
                # try a function in this class
                handler = 'process'+command
                try:
                    # look for a function called processCommandName with first
                    # letter of command capitalized, so quit, becomes processQuit
                    func = getattr(self, handler)
                except:
                    print("Cant find handler for ", handler)
                else:
                    func(*cmd[1:])
            api.sleep(0)

    def processQuit(self):
        """
        Receive Quit command from client, and ignore it for now.
        """
        self.out_queue.put(["quit"])
        self.client.logout()

    def initialize_logger(self):
        """
        Initialize application logger and logging parameters.
        """
        self.logger = logging.getLogger("b2rex.simrt")

        if self.verbose and __name__ == '__main__':
            console = logging.StreamHandler()
            console.setLevel(logging.DEBUG) # seems to be a no op, set it for the logger
            formatter = logging.Formatter('%(asctime)-30s%(name)-30s: %(levelname)-8s %(message)s')
            console.setFormatter(formatter)
            logging.getLogger('').addHandler(console)

            # setting the level for the handler above seems to be a no-op
            # it needs to be set for the logger, here the root logger
            # otherwise it is NOTSET(=0) which means to log nothing.
            logging.getLogger('').setLevel(logging.DEBUG)

    def initialize_agent(self):
        # let's disable inventory handling for this example
        settings = Settings()
        settings.ENABLE_APPEARANCE_MANAGEMENT = False
        settings.ENABLE_INVENTORY_MANAGEMENT = False
        settings.ENABLE_EQ_LOGGING = True
        settings.ENABLE_CAPS_LOGGING = False
        settings.ENABLE_REGION_EVENT_QUEUE = True
        settings.REGION_EVENT_QUEUE_POLL_INTERVAL = 5

        #First, initialize the agent
        client = Agent(settings = settings, handle_signals=False)
        self.client = client
        return client


class ProxyFunction(object):
    """
    A function that instead adds a command to be sent to the queue.
    """
    def __init__(self, name, parent):
        self._name = name
        self._parent = parent
    def __call__(self, *args):
        self._parent.addCmd([self._name]+list(args))

class GreenletsThread(Thread):
    """
    Main thread for the program. If running stand alone this will be running
    as a greenlet instead.
    """
    def __init__ (self, server_url, login_params):
        self.running = True
        self.agent = True
        self.cmd_out_queue = []
        self.cmd_in_queue = []
        self.out_queue = Queue()
        self.in_queue = Queue()
        self.server_url = server_url
        self.login_params = login_params
        Thread.__init__(self)

    def apply_position(self, obj_uuid, pos, rot=None):
        cmd = ['pos', obj_uuid, pos, rot]
        self.addCmd(cmd)

    def __getattr__(self, name):
        return ProxyFunction(name, self)

    def apply_scale(self, obj_uuid, scale):
        cmd = ['scale', obj_uuid, scale]
        self.addCmd(cmd)

    def run(self):
        agent = AgentManager(self.in_queue,
                   self.out_queue)
        error = agent.login(self.server_url, self.login_params)
        if error:
            self.out_queue.put(["error", str(error)])
            self.out_queue.put(["agentquit", str(error)])
            while self.out_queue.qsize():
                api.sleep(0.1)
        agent.logger.debug("Quitting")
        self.agent = agent
        self.running = False

    def addCmd(self, cmd):
        self.in_queue.put(cmd)

    def getQueue(self):
        out_queue = []
        while self.out_queue.qsize():
            out_queue.append(self.out_queue.get())
        return out_queue


running = False

def run_thread(context, server_url, login_params):
    """
    Call from outside the module to start up the agent thread.
    """
    global running
    running = GreenletsThread(server_url, login_params)
    running.daemon = True
    running.start()
    return running

def stop_thread():
    """
    Call from outside to stop the agent thread.
    """
    global running
    running.stop()
    running = None


# the following is to run in stand alone mode
class ClientHandler(object):
    """
    Manager that accepts a connection and initializes an agent.
    When no clients are left the agent is killed and will be respawned
    when someone comes back.
    """
    def __init__(self):
        self.current = None
        self.deferred_cmds = []
    def read_client(self, json_socket):
        global running
        while True:
            api.sleep(0)
            data = json_socket.recv()
            if not data:
                # client disconnected, bail out
                if self.current:
                    self.current.out_queue.put(["quit"])
                break
            if data[0] == 'connect':
                if not running:
                    # initial connect command
                    running = GreenletsThread(*data[1:])
                    self.current = running
                    api.spawn(running.run)
                    for cmd in self.deferred_cmds:
                        running.addCmd(cmd)
                    self.deferred_cmds = []
                    json_socket.send(["hihi"])
                else:
                    running.addCmd(["bootstrap"])
            elif self.current:
                # forward command
                self.current.addCmd(data)
            else:
                if data[0] in ["throttle"]:
                    self.deferred_cmds.append(data)
        print("exit read client")
        # exit
        self.connected = False
    def handle_client(self, json_socket):
        global running
        global run_main
        self.connected = True
        api.spawn(self.read_client, json_socket)
        if running:
            json_socket.send(["state", "connected"])
        else:
            json_socket.send(["state", "idle"])
        starttime = time.time()
        while self.connected:
            if self.current:
                cmd = self.current.out_queue.get()
                if cmd[0] == "quit":
                    print("quit on handle client")
                    break;
                else:
                    json_socket.send(cmd)
                #for cmd in self.current.queue.get():
                    #    json_socket.send(cmd)
                    #api.sleep(0)
            api.sleep(0)
        json_socket.close()
        if running:
            running.addCmd(["quit"])
            running = None
        sys.exit()
            # run_main = False
        # live..
        #raise eventlet.StopServe

run_main = True

def main():
    """
    In stand alone mode we will open a port and accept commands.
    """
    server = eventlet.listen(('0.0.0.0', 11112))
    #pool = eventlet.GreenPool(1000)
    while run_main:
         new_sock, address = server.accept()
         client_handler = ClientHandler()
         api.spawn(client_handler.handle_client, JsonSocket(new_sock))
         api.sleep(0)

if __name__=="__main__":
    main()


