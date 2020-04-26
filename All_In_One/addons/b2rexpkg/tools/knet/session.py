"""
Maintain a session to a kristalli server
"""

# Echo client program
import os
import socket
import struct
from collections import defaultdict
from .ksocket import KristalliSocket
from .template import MessageTemplateParser

class KristalliSession(object):
    """
    Object managing a session with a kristalli server
    """
    def __init__(self, name):
        self.name = name.encode('utf-8')
        self._callbacks = defaultdict(list)
        self._socket = KristalliSocket()
        self.templates = MessageTemplateParser()

    def subscribe(self, msg_id, cb):
        """
        Subscribe a callback for given msg_id
        """
        if isinstance(msg_id, str):
            msg_id = self.templates.get_msg_id(msg_id)
        self._callbacks[msg_id].append(cb)

    def connect(self, host, port):
        """
        Connect to the given host and post
        """
        self._socket.connect((host, port))
        self.login(host, port)

    def login(self, host, port):
        """
        Send a login message to the given host and port
        """
        login_data = """<login>
                            <address value="%s" />
                            <port value="%s" />
                            <protocol value="tcp" />
                            <username value="%s" />
                            <password value="" />
                        </login>
                    """ %(host, port, self.name)
        self._socket.send(100, struct.pack('<H', len(login_data))+login_data)

    def loop(self):
        """
        Loop over the connection and trigger registered callbacks as
        messages arrive
        """
        s = self._socket
        t = self.templates
        while True:
            data = s.recv()
            if data == '':
                break
            msgId, data = data
            if msgId == 1:
                val = data.get_u8()
                #print(" - Ping request", val)
                s.send(2, data._data)
            elif msgId in t.templates:
                msg = t.parse(msgId, data)
                if msgId in self._callbacks:
                    for cb in self._callbacks[msgId]:
                        cb(msg)
                        # print(msg)
            else:
                if not os.path.exists("/tmp/"+str(msgId)+".txt"):
                    f = open("/tmp/"+str(msgId)+".txt", "w")
                    f.write(data._data)
                    f.close()
                print('Received unknown', msgId, len(data._data))
        s.close()

if __name__ == "__main__":
    k = KristalliSession("caedes")
    k.templates.add_file('/home/caedes/SVN/REALXTEND/tundra/TundraLogicModule/TundraMessages.xml')
    k.connect('localhost', 2345)
    k.loop()

