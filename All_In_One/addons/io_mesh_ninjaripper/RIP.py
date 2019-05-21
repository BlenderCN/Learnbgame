import os
import sys
from pprint import pprint

try:
    from .ByteIO import ByteIO
    from .RIP_DATA import *
except:
    from ByteIO import ByteIO
    from RIP_DATA import *

class RIP:

    def __init__(self,filepath):
        self.reader = ByteIO(path = filepath)
        print("Impotring",os.path.basename(filepath))
        self.header = RIPHeader()

    def read(self):
        self.header.read(self.reader)

if __name__ == '__main__':
    with open('log.log', "w") as f:  # replace filepath & filename
        with f as sys.stdout:
            a = RIP(filepath=r"./test_data/MW2/Mesh_0234.rip")
            # a = RIP(filepath=r"./test_data/Mesh_0113.rip")
            a.read()
            _,uv,norm,_ = a.header.get_flat_verts()
            # for vert in uv:
            #     pprint(vert)
            # for vert in norm:
            #     pprint(vert)
            # pprint(a.header.vertexes)

