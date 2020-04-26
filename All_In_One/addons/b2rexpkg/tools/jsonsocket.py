"""
A simple socket wrapper that sends and receives json.

 s = JsonSocket()
 s.connect(('localhost', 11112))
 s.send({'foo':'bar', 'val': 2.4})

"""

import socket
import json
import struct

SEC_CODE = 666

class JsonSocket(object):
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
    def __getattr__(self, name):
        return getattr(self.sock, name)
    def __hasattr__(self, name):
        return hasattr(self.sock, name)
    def accept(self):
        sock, addr = self.sock.accept()
        return JsonSocket(sock), addr
    def send(self, data):
        msg = json.dumps(data).encode('utf-8')
        strlen = struct.pack("<ll", SEC_CODE, len(msg))
        totallen = len(msg) + 8
        totalsent = 0
        totalmsg = strlen+msg
        while totalsent < totallen:
            sent = self.sock.send(totalmsg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent += sent
    def recv(self):
        data = self.sock.recv(8)
        if len(data) < 8:
            return None
        sec_code, datalen = struct.unpack("<ll", data)
        if not sec_code == SEC_CODE:
            return None
        #raise RuntimeError("socket connection broken")
        msg = b''
        currlen = 0
        while currlen < datalen:
            msg += self.sock.recv(datalen-currlen)
            if len(msg) == currlen:
                return None
            currlen = len(msg)
        return json.loads(msg.decode('utf-8'))


