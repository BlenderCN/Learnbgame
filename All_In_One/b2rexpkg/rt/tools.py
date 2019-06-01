from hashlib import md5
import socket
import urlparse

from pyogp.lib.base.helpers import Helpers
from pyogp.lib.base.datatypes import UUID, Vector3, Quaternion

def v3_to_list(v3):
    return [v3.X, v3.Y, v3.Z]
def q_to_list(q):
    return [q.X, q.Y, q.Z, q.W]
def b_to_s(b):
    return b.decode('utf-8')
def uuid_to_s(b):
    return str(b)
def unpack_q(data, offset):
    min = -1.0
    max = 1.0
    q = Quaternion(X=Helpers.packed_u16_to_float(data, offset,
                                                     min, max),
                        Y=Helpers.packed_u16_to_float(data, offset+2,
                                                     min, max),
                        Z=Helpers.packed_u16_to_float(data, offset+4,
                                                     min, max),
                        W=Helpers.packed_u16_to_float(data, offset+6,
                                                     min, max))
    return q

def unpack_v3(data, offset, min, max):
    vector3 = Vector3(X=Helpers.packed_u16_to_float(data, offset,
                                                     min, max),
                        Y=Helpers.packed_u16_to_float(data, offset+2,
                                                     min, max),
                        Z=Helpers.packed_u16_to_float(data, offset+4,
                                                     min, max))
    return vector3

def uuid_combine(uuid_one, uuid_two):
    return UUID(bytes=md5(uuid_one.uuid.bytes+uuid_two.uuid.bytes).digest())



def prepare_server_name(server_url):
    parsed_url = urlparse.urlparse(server_url)
    split_netloc = parsed_url.netloc.split(":")
    if len(split_netloc) == 2:
        server_name, port = split_netloc
    else:
        server_name = parsed_url.netloc
        port = None
    try:
        # reconstruct the url with the ip to avoid problems
        res_server_name = socket.gethostbyname(server_name)
        if res_server_name == '::1': # :-P
            res_server_name = '127.0.0.1'
            #if res_server_name in ['127.0.01', '::1']:
        if len(server_name.split(".")) == 1:
            server_name = res_server_name
    except:
        pass
    if port:
        server_name = server_name + ":" + port
    else:
        server_name = server_name + '/xml-rpc.php'
    server_url = parsed_url.scheme + '://' + server_name
    return server_url

