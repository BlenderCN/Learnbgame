from threading import Thread, Timer
from .tools.jsonsocket import JsonSocket
from .tools import runexternal

try:
    from queue import Queue
except:
    from Queue import Queue

import os
import socket
import traceback
import time
import subprocess

import logging
logger = logging.getLogger("b2rex.proxyagent")

class ClientThread(Thread):
    def __init__ (self, parent):
        Thread.__init__(self)
        self.daemon = True
        self.parent = parent
    def run(self):
        while self.parent.alive:
            try:
                data = self.parent.socket.recv()
                if not data:
                    self.parent.disconnected()
                    self.cleanup()
                    return
                else:
                    self.parent.dataArrived(data)
            except socket.timeout:
                pass
            except socket.error as e:
                if e.errno == 9:
                    self.cleanup()
                    return
                raise e
        self.cleanup()
    def cleanup(self):
        logger.debug("exit client thread")
        self.parent = None

class ProxyFunction(object):
    def __init__(self, name, parent):
        self._name = name
        self._parent = parent
    def __call__(self, *args):
        self._parent.addCmd([self._name]+list(args))

class ProxyAgent(Thread):
    def __init__ (self, parent, server_url, login_params):
        Thread.__init__(self)
        self.server_url = server_url
        self.login_params = login_params
        self.link = parent
        self.in_queue = Queue()
        self.out_queue = Queue()
        self.connected = False
        self.socket = False
        self.queue = []
        self.cmds = []
        self.alive = False
    def dataArrived(self, data):
        self.queue.append(data)
        if not data[0] == 'SimStats':
            self.redraw()
    def __getattr__(self, name):
        return ProxyFunction(name, self)
    def addCmd(self, cmd):
        if cmd[0] == 'quit':
            self.alive = False
        self.out_queue.put(cmd)
    def getQueue(self):
        queue = list(self.queue)
        self.queue = []
        return queue

    def apply_position(self, obj_uuid, pos, rot=0):
        if rot:
            cmd = ['pos', obj_uuid, [pos[0], pos[1], pos[2]], [rot[0], rot[1],
                                                           rot[2], rot[3]]]
        else:
            cmd = ['pos', obj_uuid, [pos[0], pos[1], pos[2]], 0]
        self.addCmd(cmd)

    def apply_scale(self, obj_uuid, scale):
        cmd = ['scale', obj_uuid, [scale[0], scale[1], scale[2]]]
        self.addCmd(cmd)

    def redraw(self):
        self.link.redraw()

    def disconnected(self):
        if self.running:
            self.running = False
            self.connected = False
            self.receiver = None
            self.socket.close()
            self.socket = JsonSocket()
            # start reconnecting
            self.check_timer = Timer(0.5, self.check_connection)
            self.check_timer.start()

    def check_connection(self):
        logger.debug("check connection")
        # try connecting every 2 seconds
        if time.time() - self.starttime > 2 and not self.running:
            try:
                self.socket.connect(("localhost", 11112))
                self.receiver = ClientThread(self)
                self.running = True
                self.connected = True
                self.receiver.start()
                self.redraw()
                #logger.debug("connected!! " + self.server_url + " " + self.username)
                self.addCmd(["connect", self.server_url, self.login_params])
                return
            except socket.error as e:
                if e.errno == 111:
                    pass
                if not e.errno in [111, 103]:
                    traceback.print_exc()
                self.starttime = self.starttime + 2
                self.running = False
        # otherwise blink every 0.5 seconds
        if self.running == False and time.time() - self.blinkstart > 1:
            self.connected = not self.connected
            self.blinkstart = time.time()
            self.redraw()
        logger.debug("check connection later..")
        self.check_timer = Timer(1, self.check_connection)
        self.check_timer.start()

    def start_agent(self):
        script_path = os.path.dirname(__file__)
        tools_path = os.path.join(script_path, 'tools')
        bin_path = os.path.join(script_path, 'bin')
        libs_path = os.path.join(script_path, 'libs')
        agent_path = os.path.join(script_path, 'simrt.py')

        environ = dict(os.environ)
        if 'PYTHONPATH' in environ:
            prev_python_path = environ['PYTHONPATH'] + os.pathsep
        else:
            prev_python_path = ""

        if 'SIMRT_LIBS_PATH' in environ and os.path.exists(environ['SIMRT_LIBS_PATH']):
            # user defined libs path
            prev_python_path += environ['SIMRT_LIBS_PATH'] + os.pathsep
        elif os.path.exists(libs_path):
            # else look for included libraries under b2rexpkg/libs
            prev_python_path = libs_path + os.pathsep

        user_py_paths = []
        if 'SIMRT_TOOLS_PATH' in environ and os.path.exists(environ['SIMRT_TOOLS_PATH']):
            user_py_paths.append(environ['SIMRT_TOOLS_PATH'])
        if os.path.exists(bin_path):
            user_py_paths.append(bin_path)
        # now look for the binary
        py_path = runexternal.find_python2(user_py_paths)

        environ['PYTHONPATH'] = prev_python_path + script_path + os.pathsep + tools_path
        agent = subprocess.Popen([py_path, agent_path], env=environ)
        return agent


    def run(self):
        self.agent = self.start_agent()
        self.running = False
        self.alive = True
        self.socket = JsonSocket()
        self.receiver = None
        started = False
        self.starttime = time.time()-2
        self.blinkstart = time.time()
        self.check_timer = Timer(0.5, self.check_connection)
        self.check_timer.start()
        while self.alive:
            found = False
            # msg queue
            if self.running:
                cmd = self.out_queue.get()
                if cmd[0] == "quit":
                    try:
                        self.socket.send(cmd)
                        self.socket.close()
                    except socket.error as e:
                        if not e.errno == 32: # broken pipe
                            raise e
                    break
                try:
                    self.socket.send(cmd)
                except socket.error as e:
                    if e.errno == 32: # broken pipe
                        self.disconnected()
            else:
                time.sleep(0.4)
        # dismiss the agent
        self.agent.terminate()
        # clean up the thread
        if self.running:
            self.running = False
            self.receiver.join(0.4)
            self.socket.close()
            self.connected = False
            self.redraw()
        print("exit thread")


def run_thread(context, server_url, login_params):
    running = ProxyAgent(context, server_url, login_params)
    running.start()
    return running


