"""Small example OSC client

This program sends 10 random values between 0.0 and 1.0 to the /filter address,
waiting for 1 seconds between each value.
"""
import argparse
import random
import time

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


from pythonosc import osc_message_builder
from pythonosc import udp_client




if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip", default="127.0.0.1",
      help="The ip of the OSC server")
  parser.add_argument("--port", type=int, default=5505,
      help="The port the OSC server is listening on")
  args = parser.parse_args()

  client = udp_client.SimpleUDPClient(args.ip, args.port)

  for x in range(10):
    client.send_message("/filter", random.random())
    time.sleep(1)
