"""Small example OSC server

This program listens to several addresses, and prints some information about
received packets.
"""

#enables standalone support
if __name__ == "__main__":
    import os
    import sys
    from os.path import dirname, join
    try:
        import bpy
        mainPackage = dirname(bpy.data.filepath)
    except ModuleNotFoundError:
        from os.path import abspath
        #This line changes based on where the meta package is
        mainPackage = dirname(dirname(abspath(__file__)))  
    if not mainPackage in sys.path:
        sys.path.append(mainPackage)
        print(mainPackage + " appended to sys path")
    library = join(mainPackage, "libs")
    if not library in sys.path:
        sys.path.append(library)
        print(library + " appended to sys path")
    os.chdir(mainPackage) ###THIS IS VERY IMPORTANT AND FIXES EVERYTHING
    ######    
    #extra file-specific stuff
    extr = join(mainPackage, "extranious")
    if not extr in sys.path:
        sys.path.append(extr)
        print(extr + " appended  to sys path")
        os.chdir(extr)
#################################

#import argparse
#import os

#pid = os.getpid()
#print(pid)

from pythonosc import dispatcher
from pythonosc import osc_server

def printOutput(line):
    print(line)

def print_volume_handler(unused_addr, args, volume):
    print("[{0}] ~ {1}".format(args[0], volume))

#parser = argparse.ArgumentParser()
#parser.add_argument("--ip",
#    default="127.0.0.1", help="The ip to listen on")
#parser.add_argument("--port",
#    type=int, default=5505, help="The port to listen on")
#args = parser.parse_args()

#disp = dispatcher.Dispatcher()
disp.map("/", printOutput)

dispatcher = dispatcher.Dispatcher()
dispatcher.map("/filter", print)
#dispatcher.map("/volume", print_volume_handler, "Volume")

#server = osc_server.ThreadingOSCUDPServer(
#    (args.ip, args.port), dispatcher)
print("Serving on {}".format(server.server_address))
server.serve_forever()
